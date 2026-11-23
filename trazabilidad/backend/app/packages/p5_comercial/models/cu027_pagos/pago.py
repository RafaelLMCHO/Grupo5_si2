from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

METODO_PAGO_ENUM = Enum(
    'efectivo',
    'tarjeta_credito',
    'tarjeta_debito',
    'transferencia',
    'criptomoneda',
    name='metodo_pago_enum',
    create_type=False,
)

ESTADO_PAGO_ENUM = Enum(
    'pendiente',
    'completado',
    'rechazado',
    'reembolsado',
    name='estado_pago_enum',
    create_type=False,
)


class Pago(Base):
    __tablename__ = "pago"

    idpago: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idventa: Mapped[int] = mapped_column(Integer, ForeignKey("venta.idventa"), nullable=False, index=True)
    metodopago: Mapped[str] = mapped_column(METODO_PAGO_ENUM, nullable=False)
    monto: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fechapago: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    estado: Mapped[str] = mapped_column(ESTADO_PAGO_ENUM, default="pendiente")
    # Campos aditivos de pasarela (ADR-013). Los pagos manuales conservan
    # proveedor='manual' y dejan las referencias de Stripe en NULL.
    proveedor: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    idtransaccion: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    paymentintentid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estadopasarela: Mapped[str | None] = mapped_column(String(40), nullable=True)

    venta = relationship("Venta")
