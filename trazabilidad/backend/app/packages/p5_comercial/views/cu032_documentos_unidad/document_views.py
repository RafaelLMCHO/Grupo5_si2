from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


# Esquemas de la carga y asociación de documentos a unidades (CU-032)

class DocumentoResponse(BaseModel):
    iddocumento: int
    idunidad: int
    nombre: str
    urlarchivo: str
    hasharchivo: str
    fechaemision: date
    fechavencimiento: Optional[date] = None
    tipodocumento: str

    # Enriquecimiento para la UI (opcionales)
    numeroserie: Optional[str] = None
    uuidpublico: Optional[str] = None
    vencido: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentoListResponse(BaseModel):
    total: int
    items: List[DocumentoResponse]


class CreateDocumentoRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    urlarchivo: str = Field(..., min_length=3, max_length=255, description="URL del archivo almacenado")
    tipodocumento: str = Field(
        ...,
        description="factura_compra, certificado_importacion, comprobante_garantia, "
                    "certificado_autenticidad o informe_tecnico",
    )
    fechaemision: Optional[date] = Field(None, description="Por defecto, la fecha actual")
    fechavencimiento: Optional[date] = Field(None, description="Fecha de vencimiento (si aplica)")
    hasharchivo: Optional[str] = Field(
        None, max_length=255, description="Hash SHA-256 provisto por el cliente (opcional)"
    )
    contenido: Optional[str] = Field(
        None,
        max_length=100000,
        description="Contenido textual del documento; si se envía se calcula su hash SHA-256",
    )


class VerifyDocumentoRequest(BaseModel):
    hasharchivo: Optional[str] = Field(None, description="Hash a comparar con el almacenado")
    contenido: Optional[str] = Field(
        None, max_length=100000, description="Contenido textual; se calcula su hash SHA-256"
    )


class VerifyDocumentoResponse(BaseModel):
    iddocumento: int
    hasharchivo: str
    hashcalculado: str
    coincide: bool
    mensaje: str
