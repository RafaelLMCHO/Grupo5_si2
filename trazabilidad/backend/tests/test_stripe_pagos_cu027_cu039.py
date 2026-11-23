"""Stripe Checkout de pago único: CU-027 (ventas) y CU-037/CU-039 (facturas)."""
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import hmac
import json
import time
import uuid

import pytest

from app.core.config import settings
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.packages.p5_comercial.models.cu025_ventas.venta import Venta
from app.packages.p5_comercial.models.cu027_pagos.pago import Pago
from app.packages.p5_comercial.models.cu027_pagos.stripe_event import StripeEvent
from app.packages.p8_suscripciones.models.cu036_planes.subscription_models import Plan, Suscripcion
from app.packages.p8_suscripciones.models.cu039_facturacion.factura import Cobro, Factura
from app.services.payments import stripe_gateway

WEBHOOK_SECRET = "whsec_test"


def _firmar(payload: bytes, secreto: str = WEBHOOK_SECRET) -> str:
    timestamp = int(time.time())
    firma = hmac.new(
        secreto.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={firma}"


def _evento(tipo: str, objeto: dict, eventoid: str | None = None) -> dict:
    return {
        "id": eventoid or f"evt_{uuid.uuid4().hex}",
        "object": "event",
        "type": tipo,
        "data": {"object": objeto},
    }


def _enviar_webhook(client, evento: dict, firma: str | None = None):
    payload = json.dumps(evento).encode()
    headers = {"Content-Type": "application/json"}
    headers["Stripe-Signature"] = firma if firma is not None else _firmar(payload)
    return client.post("/api/v1/payments/webhook", content=payload, headers=headers)


@pytest.fixture(autouse=True)
def _stripe_config(monkeypatch):
    """Configuración y llamadas a Stripe deterministas, sin red."""
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_demo")
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", WEBHOOK_SECRET)
    contador = {"sesiones": 0, "reembolsos": 0}

    def crear_sesion(**kwargs):
        contador["sesiones"] += 1
        sid = f"cs_test_{contador['sesiones']}_{uuid.uuid4().hex[:8]}"
        return {
            "id": sid,
            "url": f"https://checkout.stripe.com/c/pay/{sid}",
            "estado": "open",
            "expira_en": int(time.time()) + 1800,
        }

    def consultar_sesion(session_id):
        return {
            "id": session_id, "estado": "complete",
            "payment_status": "paid", "url": None,
            "payment_intent": "pi_test_123",
        }

    def reembolsar(**kwargs):
        contador["reembolsos"] += 1
        return {"id": "re_test_123", "estado": "succeeded"}

    monkeypatch.setattr(stripe_gateway, "create_checkout_session", crear_sesion)
    monkeypatch.setattr(stripe_gateway, "retrieve_checkout_session", consultar_sesion)
    monkeypatch.setattr(stripe_gateway, "create_refund", reembolsar)
    return contador


def _venta(db_session, tenant, total="200.00"):
    suf = uuid.uuid4().hex[:8]
    cliente = ActorCadena(
        idtenant=tenant.idtenant,
        nombre=f"Cliente Stripe {suf}",
        email=f"stripe{suf}@test.com",
        tipoactor="CONSUMIDOR",
    )
    db_session.add(cliente)
    db_session.flush()
    venta = Venta(
        idtenant=tenant.idtenant, idcliente=cliente.idactor,
        total=Decimal(total), estado="pendiente",
    )
    db_session.add(venta)
    db_session.commit()
    return venta


def _factura_con_suscripcion(db_session, tenant):
    suf = uuid.uuid4().hex[:8]
    plan = Plan(
        codigo=f"stripe-plan-{suf}", nombre=f"Plan Stripe {suf}",
        preciomensual=Decimal("50.00"), precioanual=Decimal("500.00"),
        moneda="USD", activo=True, diastrial=0,
    )
    db_session.add(plan)
    db_session.flush()
    ahora = datetime.utcnow()
    sus = Suscripcion(
        idtenant=tenant.idtenant, idplan=plan.idplan, estado="trial",
        fechainicio=ahora, fechafin=ahora + timedelta(days=10),
    )
    db_session.add(sus)
    db_session.flush()
    factura = Factura(
        idtenant=tenant.idtenant, idsuscripcion=sus.idsuscripcion,
        numero=f"FAC-STRIPE-{suf}", fechaemision=ahora,
        fechavencimiento=ahora + timedelta(days=15),
        monto=Decimal("50.00"), moneda="USD", estado="pendiente",
    )
    db_session.add(factura)
    db_session.commit()
    return factura, sus


def test_checkout_venta_webhook_confirma_y_es_idempotente(
    client, db_session, setup_test_data, auth_headers
):
    tenant = setup_test_data["tenant1"]
    venta = _venta(db_session, tenant)

    respuesta = client.post(
        "/api/v1/payments/checkout",
        json={"idventa": venta.idventa},
        headers=auth_headers,
    )
    assert respuesta.status_code == 200, respuesta.text
    data = respuesta.json()
    assert data["checkout_url"].startswith("https://checkout.stripe.com/")

    db_session.expire_all()
    pago = db_session.get(Pago, data["idpago"])
    assert pago.proveedor == "stripe"
    assert pago.estado == "pendiente"
    assert pago.idtransaccion == data["checkout_id"]

    evento = _evento("checkout.session.completed", {
        "id": data["checkout_id"],
        "payment_intent": "pi_test_123",
        "metadata": {
            "kind": "venta", "tenant_id": str(tenant.idtenant),
            "id": str(venta.idventa),
        },
    })
    webhook = _enviar_webhook(client, evento)
    assert webhook.status_code == 200, webhook.text
    assert webhook.json()["duplicado"] is False

    db_session.expire_all()
    pago = db_session.get(Pago, data["idpago"])
    assert pago.estado == "completado"
    assert pago.paymentintentid == "pi_test_123"
    assert str(db_session.get(Venta, venta.idventa).estado) == "pagada"

    repetido = _enviar_webhook(client, evento)
    assert repetido.status_code == 200, repetido.text
    assert repetido.json()["duplicado"] is True
    assert db_session.query(StripeEvent).filter(StripeEvent.eventoid == evento["id"]).count() == 1


def test_checkout_venta_rechaza_otro_tenant(client, db_session, setup_test_data, auth_headers):
    venta = _venta(db_session, setup_test_data["tenant2"])
    respuesta = client.post(
        "/api/v1/payments/checkout",
        json={"idventa": venta.idventa},
        headers=auth_headers,
    )
    assert respuesta.status_code == 404


def test_webhook_rechaza_firma_invalida(client):
    evento = _evento("checkout.session.completed", {"id": "cs_test_x"})
    respuesta = _enviar_webhook(client, evento, firma="t=1,v1=invalida")
    assert respuesta.status_code == 400


def test_estado_y_reembolso_stripe(client, db_session, setup_test_data, auth_headers, _stripe_config):
    tenant = setup_test_data["tenant1"]
    venta = _venta(db_session, tenant)
    checkout = client.post(
        "/api/v1/payments/checkout", json={"idventa": venta.idventa}, headers=auth_headers
    ).json()
    _enviar_webhook(client, _evento("checkout.session.completed", {
        "id": checkout["checkout_id"], "payment_intent": "pi_test_123",
        "metadata": {
            "kind": "venta", "tenant_id": str(tenant.idtenant), "id": str(venta.idventa),
        },
    }))

    estado = client.get(
        f"/api/v1/payments/{checkout['idpago']}/checkout", headers=auth_headers
    )
    assert estado.status_code == 200, estado.text
    assert estado.json()["pago_pasarela"] == "pi_test_123"

    reembolso = client.post(
        f"/api/v1/payments/{checkout['idpago']}/refund", headers=auth_headers
    )
    assert reembolso.status_code == 200, reembolso.text
    db_session.expire_all()
    assert db_session.get(Pago, checkout["idpago"]).estado == "reembolsado"
    assert _stripe_config["reembolsos"] == 1


def test_checkout_factura_activar_suscripcion(client, db_session, setup_test_data, auth_headers):
    tenant = setup_test_data["tenant1"]
    factura, sus = _factura_con_suscripcion(db_session, tenant)

    respuesta = client.post(
        f"/api/v1/invoices/{factura.idfactura}/checkout", headers=auth_headers
    )
    assert respuesta.status_code == 200, respuesta.text
    data = respuesta.json()
    assert data["checkout_url"].startswith("https://checkout.stripe.com/")

    db_session.expire_all()
    cobro = db_session.get(Cobro, data["idcobro"])
    assert cobro.proveedor == "stripe"
    assert cobro.estado == "pendiente"

    webhook = _enviar_webhook(client, _evento("checkout.session.completed", {
        "id": data["checkout_id"], "payment_intent": "pi_factura_123",
        "metadata": {
            "kind": "factura", "tenant_id": str(tenant.idtenant),
            "id": str(factura.idfactura),
        },
    }))
    assert webhook.status_code == 200, webhook.text

    db_session.expire_all()
    assert db_session.get(Cobro, data["idcobro"]).estado == "completado"
    assert db_session.get(Factura, factura.idfactura).estado == "pagada"
    assert db_session.get(Suscripcion, sus.idsuscripcion).estado == "activa"
