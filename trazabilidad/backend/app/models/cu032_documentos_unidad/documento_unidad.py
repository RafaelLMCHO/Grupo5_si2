from typing import Optional
from datetime import date
from sqlalchemy import String, Integer, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

TIPO_DOCUMENTO_ENUM = Enum(
    'factura_compra',
    'certificado_importacion',
    'comprobante_garantia',
    'certificado_autenticidad',
    'informe_tecnico',
    name='tipo_documento_enum',
    create_type=False
)


class DocumentoUnidad(Base):
    """CU-032 - Documento adjunto a una unidad (factura, certificado, etc.).

    El archivo se almacena fuera de la blockchain (URL); se guarda el hash de su
    contenido para poder verificar su integridad posteriormente.
    """

    __tablename__ = "documentounidad"

    iddocumento: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idunidad: Mapped[int] = mapped_column(
        Integer, ForeignKey("unidadproducto.idunidad"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    urlarchivo: Mapped[str] = mapped_column(String(255), nullable=False)
    hasharchivo: Mapped[str] = mapped_column(String(255), nullable=False)
    fechaemision: Mapped[date] = mapped_column(Date, nullable=False)
    fechavencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    tipodocumento: Mapped[str] = mapped_column(TIPO_DOCUMENTO_ENUM, nullable=False)

    unidad = relationship("UnidadProducto")
