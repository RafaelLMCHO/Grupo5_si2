"""Eventos de Stripe ya procesados (idempotencia del webhook, ADR-013)."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StripeEvent(Base):
    __tablename__ = "stripeevento"

    idevento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # ID del evento en Stripe (evt_...). Único para que un reenvío sea no-op.
    eventoid: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    tenant_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    referencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    procesadoen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
