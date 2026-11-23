"""CU-027 - Gestión de pagos de ventas."""
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import (
    get_bolivia_now, get_client_ip, get_idusuariotenant, require_roles, resolve_tenant_id,
)
from app.db.session import get_db
from app.models.cu002_usuarios.user import User
from app.models.cu005_bitacora.bitacora import Bitacora
from app.packages.p5_comercial.models.cu025_ventas.venta import Venta
from app.packages.p5_comercial.models.cu027_pagos.pago import Pago, METODO_PAGO_ENUM, ESTADO_PAGO_ENUM
from app.packages.p5_comercial.views.cu027_pagos.payment_views import (
    CreatePagoRequest, UpdatePagoEstadoRequest, PagoResponse, PagoListResponse,
    CheckoutVentaRequest, CheckoutResponse, CheckoutStatusResponse, WebhookResponse,
)
from app.services.payments import stripe_gateway
from app.services.payments.stripe_gateway import StripeGatewayError, StripeNotConfiguredError
from app.services.payments.stripe_webhook import procesar_evento

router = APIRouter(prefix="/payments", tags=["Pagos de Ventas (CU-027)"])

ROLES_PAGOS = ("SuperAdministrador", "AdministradorEmpresa", "GestorVentasPostventa")
requires_pagos = require_roles(*ROLES_PAGOS)
_METODOS = set(METODO_PAGO_ENUM.enums)
_ESTADOS = set(ESTADO_PAGO_ENUM.enums)


class PaymentController:

    @staticmethod
    def _query_tenant(db: Session, tenant_id: int):
        return select(Pago).join(Venta, Venta.idventa == Pago.idventa).where(Venta.idtenant == tenant_id)

    @staticmethod
    def _get_pago(db: Session, tenant_id: int, idpago: int) -> Pago:
        pago = db.execute(
            PaymentController._query_tenant(db, tenant_id).where(Pago.idpago == idpago)
        ).scalar_one_or_none()
        if not pago:
            raise HTTPException(status_code=404, detail=f"Pago {idpago} no encontrado.")
        return pago

    @staticmethod
    def _to_response(db: Session, pago: Pago) -> PagoResponse:
        venta_estado = db.execute(
            select(Venta.estado).where(Venta.idventa == pago.idventa)
        ).scalar_one_or_none()
        return PagoResponse(
            idpago=pago.idpago,
            idventa=pago.idventa,
            metodopago=str(pago.metodopago),
            monto=pago.monto,
            fechapago=pago.fechapago,
            estado=str(pago.estado),
            venta_estado=str(venta_estado) if venta_estado else None,
        )

    @staticmethod
    def _bitacora(db: Session, user: User, tenant_id: int, accion: str, identidad: int, ip: str) -> None:
        db.add(Bitacora(
            idusuariotenant=get_idusuariotenant(db, user),
            accion=accion, entidad="Pago", identidad=identidad,
            ip=ip, fechahora=get_bolivia_now(),
        ))

    @staticmethod
    def list_pagos(db: Session, user: User, estado: Optional[str], idventa: Optional[int],
                   skip: int, limit: int) -> PagoListResponse:
        tenant_id = resolve_tenant_id(db, user)
        query = PaymentController._query_tenant(db, tenant_id)
        if estado:
            if estado not in _ESTADOS:
                raise HTTPException(status_code=400, detail=f"Estado inválido: {estado}.")
            query = query.where(Pago.estado == estado)
        if idventa:
            query = query.where(Pago.idventa == idventa)
        total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()
        pagos = db.execute(
            query.order_by(Pago.fechapago.desc()).offset(skip).limit(limit)
        ).scalars().all()
        return PagoListResponse(
            total=total, items=[PaymentController._to_response(db, p) for p in pagos]
        )

    @staticmethod
    def create_pago(db: Session, user: User, request: Request, body: CreatePagoRequest) -> PagoResponse:
        tenant_id = resolve_tenant_id(db, user)
        if body.metodopago not in _METODOS:
            raise HTTPException(
                status_code=400,
                detail=f"Método de pago inválido. Permitidos: {sorted(_METODOS)}.",
            )
        if body.estado not in _ESTADOS:
            raise HTTPException(status_code=400, detail=f"Estado inválido: {body.estado}.")
        venta = db.execute(
            select(Venta).where(Venta.idventa == body.idventa, Venta.idtenant == tenant_id)
        ).scalar_one_or_none()
        if not venta:
            raise HTTPException(status_code=404, detail="La venta no existe en su empresa.")
        if str(venta.estado) in ("cancelada", "devuelta"):
            raise HTTPException(status_code=409, detail="No se pueden registrar pagos de una venta cancelada.")

        pago = Pago(
            idventa=body.idventa, metodopago=body.metodopago,
            monto=body.monto, fechapago=get_bolivia_now(), estado=body.estado,
        )
        db.add(pago)
        db.flush()
        PaymentController._sync_venta_estado(db, venta)
        PaymentController._bitacora(
            db, user, tenant_id, "REGISTRAR_PAGO", pago.idpago, get_client_ip(request)
        )
        db.commit()
        db.refresh(pago)
        return PaymentController._to_response(db, pago)

    @staticmethod
    def _sync_venta_estado(db: Session, venta: Venta) -> None:
        pagado = db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(
                Pago.idventa == venta.idventa, Pago.estado == "completado"
            )
        ).scalar() or Decimal("0")
        if Decimal(str(pagado)) >= Decimal(str(venta.total)):
            venta.estado = "pagada"

    @staticmethod
    def _saldo_pendiente(db: Session, venta: Venta) -> Decimal:
        cobrado = db.execute(
            select(func.coalesce(func.sum(Pago.monto), 0)).where(
                Pago.idventa == venta.idventa, Pago.estado == "completado"
            )
        ).scalar() or Decimal("0")
        return max(Decimal("0"), Decimal(str(venta.total)) - Decimal(str(cobrado)))

    @staticmethod
    def checkout_venta(db: Session, user: User, request: Request,
                       body: CheckoutVentaRequest) -> CheckoutResponse:
        """Crea un Checkout Session de Stripe y su Pago pendiente (CU-027)."""
        tenant_id = resolve_tenant_id(db, user)
        venta = db.execute(
            select(Venta).where(Venta.idventa == body.idventa, Venta.idtenant == tenant_id)
        ).scalar_one_or_none()
        if not venta:
            raise HTTPException(status_code=404, detail="La venta no existe en su empresa.")
        if str(venta.estado) in ("cancelada", "devuelta"):
            raise HTTPException(status_code=409, detail="No se puede cobrar una venta cancelada.")
        saldo = PaymentController._saldo_pendiente(db, venta)
        if saldo <= 0:
            raise HTTPException(status_code=409, detail="La venta ya está cancelada.")

        metadata = {
            "kind": "venta", "tenant_id": tenant_id,
            "id": venta.idventa, "ref": f"venta-{venta.idventa}",
        }
        try:
            sesion = stripe_gateway.create_checkout_session(
                monto=saldo, moneda="usd", descripcion=f"Venta #{venta.idventa}",
                metadata=metadata,
            )
        except StripeNotConfiguredError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except StripeGatewayError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        pago = Pago(
            idventa=venta.idventa, metodopago="tarjeta_credito", monto=saldo,
            fechapago=get_bolivia_now(), estado="pendiente", proveedor="stripe",
            idtransaccion=sesion.get("id"), estadopasarela=sesion.get("estado"),
        )
        db.add(pago)
        db.flush()
        PaymentController._bitacora(
            db, user, tenant_id, "CHECKOUT_STRIPE_VENTA", pago.idpago, get_client_ip(request)
        )
        db.commit()
        db.refresh(pago)
        return CheckoutResponse(
            idpago=pago.idpago, idventa=venta.idventa,
            checkout_id=str(sesion.get("id") or ""),
            checkout_url=str(sesion.get("url") or ""),
            estado=pago.estado, monto=pago.monto, expira_en=sesion.get("expira_en"),
        )

    @staticmethod
    def estado_checkout(db: Session, user: User, idpago: int) -> CheckoutStatusResponse:
        tenant_id = resolve_tenant_id(db, user)
        pago = PaymentController._get_pago(db, tenant_id, idpago)
        if pago.proveedor != "stripe" or not pago.idtransaccion:
            raise HTTPException(status_code=400, detail="El pago no fue creado con Stripe.")
        try:
            sesion = stripe_gateway.retrieve_checkout_session(pago.idtransaccion)
        except StripeNotConfiguredError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except StripeGatewayError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        return CheckoutStatusResponse(
            idpago=pago.idpago, estado=pago.estado, proveedor=pago.proveedor,
            checkout_id=pago.idtransaccion, estado_pasarela=sesion.get("estado"),
            pago_pasarela=sesion.get("payment_intent"), pago_confirmado=sesion.get("payment_status"),
        )

    @staticmethod
    def reembolsar(db: Session, user: User, request: Request, idpago: int) -> PagoResponse:
        tenant_id = resolve_tenant_id(db, user)
        pago = PaymentController._get_pago(db, tenant_id, idpago)
        if pago.proveedor != "stripe":
            raise HTTPException(status_code=400, detail="El pago no fue creado con Stripe.")
        if pago.estado != "completado":
            raise HTTPException(status_code=409, detail="Sólo se pueden reembolsar pagos completados.")
        try:
            stripe_gateway.create_refund(
                payment_intent_id=pago.paymentintentid,
                metadata={
                    "kind": "venta", "tenant_id": tenant_id,
                    "pago_id": pago.idpago, "id": pago.idventa,
                },
            )
        except StripeNotConfiguredError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except StripeGatewayError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        pago.estado = "reembolsado"
        pago.estadopasarela = "refunded"
        db.flush()
        venta = db.execute(
            select(Venta).where(Venta.idventa == pago.idventa)
        ).scalars().first()
        if venta:
            PaymentController._sync_venta_estado(db, venta)
        PaymentController._bitacora(
            db, user, tenant_id, "REEMBOLSO_STRIPE_VENTA", pago.idpago, get_client_ip(request)
        )
        db.commit()
        db.refresh(pago)
        return PaymentController._to_response(db, pago)

    @staticmethod
    def update_estado(db: Session, user: User, request: Request,
                      idpago: int, estado: str) -> PagoResponse:
        tenant_id = resolve_tenant_id(db, user)
        if estado not in _ESTADOS:
            raise HTTPException(status_code=400, detail=f"Estado inválido: {estado}.")
        pago = PaymentController._get_pago(db, tenant_id, idpago)
        pago.estado = estado
        venta = db.execute(
            select(Venta).where(Venta.idventa == pago.idventa)
        ).scalar_one_or_none()
        if venta:
            PaymentController._sync_venta_estado(db, venta)
        PaymentController._bitacora(
            db, user, tenant_id, f"CAMBIAR_ESTADO_PAGO_{estado.upper()}",
            idpago, get_client_ip(request),
        )
        db.commit()
        db.refresh(pago)
        return PaymentController._to_response(db, pago)


@router.get("", response_model=PagoListResponse)
def list_pagos_route(
    estado: Optional[str] = Query(None),
    idventa: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    return PaymentController.list_pagos(db, current_user, estado, idventa, skip, limit)


@router.get("/{idpago}", response_model=PagoResponse)
def get_pago_route(
    idpago: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    tenant_id = resolve_tenant_id(db, current_user)
    return PaymentController._to_response(db, PaymentController._get_pago(db, tenant_id, idpago))


@router.post("", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def create_pago_route(
    body: CreatePagoRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    return PaymentController.create_pago(db, current_user, request, body)


@router.patch("/{idpago}/estado", response_model=PagoResponse)
def update_estado_route(
    idpago: int,
    body: UpdatePagoEstadoRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    return PaymentController.update_estado(db, current_user, request, idpago, body.estado)


# ── Stripe Checkout (ADR-013) ──────────────────────────────────────────────

@router.post("/checkout", response_model=CheckoutResponse,
             summary="Crear Checkout de Stripe para una venta")
def crear_checkout_venta_route(
    body: CheckoutVentaRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    return PaymentController.checkout_venta(db, current_user, request, body)


@router.get("/{idpago}/checkout", response_model=CheckoutStatusResponse,
            summary="Consultar estado del Checkout de Stripe")
def estado_checkout_venta_route(
    idpago: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    return PaymentController.estado_checkout(db, current_user, idpago)


@router.post("/{idpago}/refund", response_model=PagoResponse,
             summary="Reembolsar un pago de Stripe")
def reembolsar_pago_route(
    idpago: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_pagos),
):
    return PaymentController.reembolsar(db, current_user, request, idpago)


@router.post("/webhook", response_model=WebhookResponse,
             summary="Webhook de Stripe (firma verificada, sin JWT)")
async def stripe_webhook_route(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.body()
    firma = request.headers.get("stripe-signature", "")
    try:
        evento = stripe_gateway.verify_webhook(payload, firma)
    except StripeGatewayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        return procesar_evento(db, evento)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
