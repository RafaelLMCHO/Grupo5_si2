from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ESTADO_CONFIRMACION_ENUM = Enum(
    'pendiente',
    'confirmado',
    'rechazado',
    name='estado_confirmacion_enum',
    create_type=False
)


class RegistroBlockchain(Base):
    """T044 - Anclaje de un EventoTrazabilidad en la red Blockchain (1:1)."""

    __tablename__ = "registroblockchain"

    idregistro: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idevento: Mapped[int] = mapped_column(
        Integer, ForeignKey("eventotrazabilidad.idevento"), nullable=False
    )
    payloadhash: Mapped[str] = mapped_column(String(255), nullable=False)
    txhash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    blocknumber: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    network: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    chainid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    contractaddress: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fechaenvio: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fechaconfirmacion: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado: Mapped[Optional[str]] = mapped_column(
        ESTADO_CONFIRMACION_ENUM, default="pendiente"
    )
    numeroconfirmaciones: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    mensajeerror: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    evento = relationship("EventoTrazabilidad")
