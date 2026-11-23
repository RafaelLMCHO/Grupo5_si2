"""Despachador del webhook de Stripe para ventas y facturas (ADR-013).

El webhook no trae JWT: el tenant se toma del metadata firmado por nosotros y
siempre se valida contra la tabla padre. Un evento repetido es no-op.
"""
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers.shared import get_bolivia_now
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu005_bitacora.bitacora import Bitacora
from app.packages.p5_comercial.models.cu027_pagos.pago import Pago
from app.packages.p5_comercial.models.cu027_pagos.stripe_event import StripeEvent
from app.packages.p5_comercial.models.cu025_ventas.venta import Venta
from app.packages.p8_suscripciones.models.cu039_facturacion.factura import Cobro, Factura


def _entero(valor: Any) -> Optional[int]:
    try:
        return int(valor) if valor not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _metadata(obj: Dict[str, Any]) -> Dict[str, Any]:
    datos = obj.get("metadata") or {}
    return dict(datos) if hasattr(datos, "get") else {}


def _bitacora(
    db: Session, tenant_id: Optional[int], accion: str, entidad: str, identidad: Optional[int]
) -> None:
    """Audita con el primer usuario del tenant; sin usuario, sólo queda StripeEvent."""
    if not tenant_id:
        return
    idut = db.execute(
        select(UsuarioTenant.idusuariotenant)
        .where(UsuarioTenant.idtenant == tenant_id)
        .order_by(UsuarioTenant.idusuariotenant)
        .limit(1)
    ).scalar_one_or_none()
    if idut is None:
        return
    db.add(Bitacora(
        idusuariotenant=idut,
        accion=accion[:50],
        entidad=entidad[:50],
        identidad=identidad,
        ip="stripe-webhook",
        fechahora=get_bolivia_now(),
    ))


def _pago_por_sesion(db: Session, session_id: str) -> Optional[Pago]:
    if not session_id:
        return None
    return db.execute(
        select(Pago).where(Pago.idtransaccion == session_id)
    ).scalars().first()


def _cobro_por_sesion(db: Session, session_id: str) -> Optional[Cobro]:
    if not session_id:
        return None
    return db.execute(
        select(Cobro).where(Cobro.idtransaccion == session_id)
    ).scalars().first()


def _validar_venta(db: Session, pago: Pago, meta: Dict[str, Any]) -> bool:
    venta = db.execute(
        select(Venta).where(Venta.idventa == pago.idventa)
    ).scalars().first()
    return bool(
        venta
        and _entero(meta.get("tenant_id")) == venta.idtenant
        and _entero(meta.get("id")) == pago.idventa
    )


def _validar_factura(db: Session, cobro: Cobro, meta: Dict[str, Any]) -> bool:
    factura = db.execute(
        select(Factura).where(Factura.idfactura == cobro.idfactura)
    ).scalars().first()
    return bool(
        factura
        and _entero(meta.get("tenant_id")) == factura.idtenant
        and _entero(meta.get("id")) == cobro.idfactura
    )


def _confirmar_venta(db: Session, pago: Pago, payment_intent: Optional[str]) -> None:
    from app.packages.p5_comercial.controllers.cu027_pagos.payment_controller import (
        PaymentController,
    )

    pago.estado = "completado"
    pago.fechapago = pago.fechapago or get_bolivia_now()
    pago.estadopasarela = "complete"
    if payment_intent:
        pago.paymentintentid = payment_intent
    db.flush()  # autoflush=False: el UPDATE debe verse antes de la agregación
    venta = db.execute(select(Venta).where(Venta.idventa == pago.idventa)).scalars().first()
    if venta:
        PaymentController._sync_venta_estado(db, venta)
    _bitacora(db, venta.idtenant if venta else None, "STRIPE_PAGO_CONFIRMADO", "Pago", pago.idpago)


def _confirmar_factura(db: Session, cobro: Cobro, payment_intent: Optional[str]) -> None:
    from app.packages.p8_suscripciones.controllers.cu039_facturacion.billing_controller import (
        BillingController,
    )

    BillingController.confirmar_cobro_stripe(db, cobro, payment_intent)


def _rechazar(db: Session, pago: Optional[Pago], cobro: Optional[Cobro]) -> None:
    if pago is not None and pago.estado == "pendiente":
        pago.estado = "rechazado"
        pago.estadopasarela = "expired"
    if cobro is not None and cobro.estado == "pendiente":
        cobro.estado = "rechazado"
        cobro.estadopasarela = "expired"


def procesar_evento(db: Session, evento: Dict[str, Any]) -> Dict[str, Any]:
    """Idempotente: devuelve ``duplicado=True`` si el evento ya se aplicó."""
    eventoid = evento.get("id")
    if not eventoid:
        raise ValueError("El evento de Stripe no tiene id.")
    existe = db.execute(
        select(StripeEvent).where(StripeEvent.eventoid == str(eventoid))
    ).scalar_one_or_none()
    if existe:
        return {
            "recibido": True,
            "duplicado": True,
            "tipo": existe.tipo,
            "referencia": existe.referencia,
        }

    tipo = str(evento.get("type") or "")
    obj = (evento.get("data") or {}).get("object") or {}
    obj = dict(obj) if hasattr(obj, "get") else {}
    meta = _metadata(obj)
    tenant_id = _entero(meta.get("tenant_id"))
    referencia: Optional[str] = None
    pago: Optional[Pago] = None
    cobro: Optional[Cobro] = None

    if tipo in ("checkout.session.completed", "checkout.session.expired"):
        session_id = obj.get("id")
        pago = _pago_por_sesion(db, session_id)
        cobro = _cobro_por_sesion(db, session_id)
        kind = meta.get("kind")
        if kind == "venta" and pago and _validar_venta(db, pago, meta):
            referencia = f"venta:{pago.idpago}"
            if tipo == "checkout.session.completed":
                _confirmar_venta(db, pago, obj.get("payment_intent"))
            else:
                _rechazar(db, pago, None)
        elif kind == "factura" and cobro and _validar_factura(db, cobro, meta):
            referencia = f"factura:{cobro.idcobro}"
            if tipo == "checkout.session.completed":
                _confirmar_factura(db, cobro, obj.get("payment_intent"))
            else:
                _rechazar(db, None, cobro)
    elif tipo in ("payment_intent.payment_failed", "charge.refunded"):
        pago_id = _entero(meta.get("pago_id"))
        cobro_id = _entero(meta.get("cobro_id"))
        if pago_id:
            pago = db.execute(select(Pago).where(Pago.idpago == pago_id)).scalars().first()
            if pago and _validar_venta(db, pago, meta):
                referencia = f"venta:{pago.idpago}"
                if tipo == "charge.refunded":
                    pago.estado = "reembolsado"
                    pago.estadopasarela = "refunded"
                    db.flush()
                    from app.packages.p5_comercial.controllers.cu027_pagos.payment_controller import (
                        PaymentController,
                    )

                    venta = db.execute(
                        select(Venta).where(Venta.idventa == pago.idventa)
                    ).scalars().first()
                    if venta:
                        PaymentController._sync_venta_estado(db, venta)
                else:
                    _rechazar(db, pago, None)
        elif cobro_id:
            cobro = db.execute(select(Cobro).where(Cobro.idcobro == cobro_id)).scalars().first()
            if cobro and _validar_factura(db, cobro, meta):
                referencia = f"factura:{cobro.idcobro}"
                if tipo == "charge.refunded":
                    cobro.estado = "reembolsado"
                    cobro.estadopasarela = "refunded"
                else:
                    _rechazar(db, None, cobro)

    db.add(StripeEvent(
        eventoid=str(eventoid),
        tipo=tipo,
        tenant_id=tenant_id,
        referencia=referencia,
        procesadoen=get_bolivia_now(),
    ))
    db.commit()
    return {"recibido": True, "duplicado": False, "tipo": tipo, "referencia": referencia}
