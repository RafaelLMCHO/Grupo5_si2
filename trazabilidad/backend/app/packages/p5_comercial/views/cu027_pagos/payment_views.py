from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class CreatePagoRequest(BaseModel):
    idventa: int
    metodopago: str = Field(..., description="efectivo, tarjeta_credito, tarjeta_debito, transferencia o criptomoneda")
    monto: Decimal = Field(..., gt=0)
    estado: str = Field("pendiente", description="pendiente, completado, rechazado o reembolsado")


class UpdatePagoEstadoRequest(BaseModel):
    estado: str


class PagoResponse(BaseModel):
    idpago: int
    idventa: int
    metodopago: str
    monto: Decimal
    fechapago: datetime
    estado: str
    venta_estado: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PagoListResponse(BaseModel):
    total: int
    items: List[PagoResponse]


class CheckoutVentaRequest(BaseModel):
    idventa: int = Field(..., gt=0)


class CheckoutResponse(BaseModel):
    """Respuesta aditiva de Checkout (Stripe). No altera PagoResponse."""

    idpago: int
    idventa: int
    checkout_id: str
    checkout_url: str
    estado: str
    monto: Decimal
    expira_en: int | None = None


class CheckoutStatusResponse(BaseModel):
    idpago: int
    estado: str
    proveedor: str
    checkout_id: str | None = None
    estado_pasarela: str | None = None
    pago_pasarela: str | None = None
    pago_confirmado: str | None = None


class WebhookResponse(BaseModel):
    recibido: bool = True
    duplicado: bool = False
    tipo: str | None = None
    referencia: str | None = None
