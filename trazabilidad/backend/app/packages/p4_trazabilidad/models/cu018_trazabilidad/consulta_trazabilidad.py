from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConsultaTrazabilidad(Base):
    """CU-018 - Registro de cada escaneo/consulta público de un código QR (1:N)."""

    __tablename__ = "consultatrazabilidad"

    idconsulta: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idcodigoqr: Mapped[int] = mapped_column(
        Integer, ForeignKey("codigoqr.idcodigoqr"), nullable=False
    )
    fechahora: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    paisaproximado: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    useragent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    codigoqr = relationship("CodigoQR")
