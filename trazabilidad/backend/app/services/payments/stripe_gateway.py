"""Adapter de Stripe Checkout para pagos únicos (CU-027, CU-037, CU-039).

No expone llaves ni objetos de Stripe a los controladores: sólo diccionarios
planos. Las credenciales se leen de ``settings`` y nunca se versionan.
"""
from decimal import Decimal
from time import time
from typing import Any, Dict, Optional

import stripe

from app.core.config import settings


class StripeNotConfiguredError(RuntimeError):
    """La pasarela no tiene credenciales configuradas."""


class StripeGatewayError(RuntimeError):
    """Fallo al comunicarse con Stripe o al verificar un webhook."""


def _api_key() -> str:
    key = (settings.STRIPE_SECRET_KEY or "").strip()
    if not key:
        raise StripeNotConfiguredError(
            "Stripe no está configurado. Defina STRIPE_SECRET_KEY en el entorno."
        )
    return key


def _webhook_secret() -> str:
    secret = (settings.STRIPE_WEBHOOK_SECRET or "").strip()
    if not secret:
        raise StripeNotConfiguredError(
            "Stripe no está configurado. Defina STRIPE_WEBHOOK_SECRET en el entorno."
        )
    return secret


def _centavos(monto: Decimal) -> int:
    total = (Decimal(str(monto)) * 100).quantize(Decimal("1"))
    if total <= 0:
        raise StripeGatewayError("El monto del cobro debe ser mayor a cero.")
    return int(total)


def _stripe_error(exc: Exception) -> StripeGatewayError:
    mensaje = getattr(exc, "user_message", None) or getattr(exc, "message", None)
    return StripeGatewayError(f"Error de Stripe: {mensaje or type(exc).__name__}")


def create_checkout_session(
    *,
    monto: Decimal,
    moneda: str,
    descripcion: str,
    metadata: Dict[str, Any],
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Crea una Checkout Session de pago único y devuelve sus datos públicos."""
    datos: Dict[str, Any] = {
        "metadata": {str(k): str(v) for k, v in (metadata or {}).items()},
        "payment_intent_data": {
            "metadata": {str(k): str(v) for k, v in (metadata or {}).items()}
        },
    }
    if metadata and metadata.get("ref"):
        datos["client_reference_id"] = str(metadata["ref"])
    try:
        session = stripe.checkout.Session.create(
            api_key=_api_key(),
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": (moneda or "usd").lower(),
                    "product_data": {"name": descripcion[:120]},
                    "unit_amount": _centavos(monto),
                },
                "quantity": 1,
            }],
            success_url=success_url or settings.STRIPE_SUCCESS_URL,
            cancel_url=cancel_url or settings.STRIPE_CANCEL_URL,
            # Stripe exige al menos 30 min; 60 min evita rechazos por desfase de reloj.
            expires_at=int(time()) + 3600,
            **datos,
        )
    except StripeNotConfiguredError:
        raise
    except Exception as exc:  # stripe.error.StripeError y errores de red
        raise _stripe_error(exc) from exc

    return {
        "id": session.get("id"),
        "url": session.get("url"),
        "expira_en": session.get("expires_at"),
        "estado": session.get("status"),
    }


def retrieve_checkout_session(session_id: str) -> Dict[str, Any]:
    try:
        session = stripe.checkout.Session.retrieve(session_id, api_key=_api_key())
    except StripeNotConfiguredError:
        raise
    except Exception as exc:
        raise _stripe_error(exc) from exc
    return {
        "id": session.get("id"),
        "estado": session.get("status"),
        "payment_status": session.get("payment_status"),
        "url": session.get("url"),
        "payment_intent": session.get("payment_intent"),
    }


def create_refund(*, payment_intent_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    if not payment_intent_id:
        raise StripeGatewayError(
            "El pago aún no tiene PaymentIntent confirmado; no se puede reembolsar."
        )
    try:
        reembolso = stripe.Refund.create(
            api_key=_api_key(),
            payment_intent=payment_intent_id,
            reason="requested_by_customer",
            metadata={str(k): str(v) for k, v in (metadata or {}).items()},
        )
    except StripeNotConfiguredError:
        raise
    except Exception as exc:
        raise _stripe_error(exc) from exc
    return {"id": reembolso.get("id"), "estado": reembolso.get("status")}


def verify_webhook(payload: bytes, signature_header: str) -> Dict[str, Any]:
    """Verifica la firma y devuelve el evento de Stripe como dict."""
    if not signature_header:
        raise StripeGatewayError("Falta la cabecera Stripe-Signature.")
    try:
        evento = stripe.Webhook.construct_event(
            payload,
            signature_header,
            _webhook_secret(),
            tolerance=settings.STRIPE_WEBHOOK_TOLERANCE_SECONDS,
        )
    except StripeNotConfiguredError:
        raise
    except Exception as exc:
        raise StripeGatewayError("Firma de webhook inválida.") from exc
    return dict(evento)
