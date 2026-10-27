from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.views.cu033_blockchain.blockchain_views import RegistroBlockchainResponse


# Esquemas de la consulta de registros Blockchain y certificados (CU-034)

class EventoCertificado(BaseModel):
    idevento: int
    tipoevento: str
    fechahora: Optional[datetime] = None
    descripcion: Optional[str] = None
    payloadhash: Optional[str] = None
    estadoverificacion: Optional[str] = None
    registro_blockchain: Optional[RegistroBlockchainResponse] = None
    en_blockchain: bool = False
    verificado: bool = False


class CertificacionUnidad(BaseModel):
    idcertificacion: int
    nombre: str
    entidademisora: Optional[str] = None
    descripcion: Optional[str] = None
    fechaobtencion: Optional[date] = None


class DocumentoCertificado(BaseModel):
    iddocumento: int
    nombre: str
    tipodocumento: str
    urlarchivo: str
    hasharchivo: str
    fechaemision: date
    fechavencimiento: Optional[date] = None


class UnitCertificateResponse(BaseModel):
    """Consolidado de registros Blockchain + certificaciones + documentos de la unidad."""

    idunidad: int
    numeroserie: str
    uuidpublico: str
    producto: Optional[str] = None
    modelo: Optional[str] = None
    sku: Optional[str] = None
    color: Optional[str] = None
    capacidad: Optional[str] = None
    autenticidad: str = Field(..., description="verificado | registrado | sin_datos")
    total_eventos: int = 0
    eventos: List[EventoCertificado] = Field(default_factory=list)
    certificaciones: List[CertificacionUnidad] = Field(default_factory=list)
    documentos: List[DocumentoCertificado] = Field(default_factory=list)
    registros_blockchain: int = 0
    registros_confirmados: int = 0


class DigitalCertificateResponse(BaseModel):
    """Certificado digital de trazabilidad generado a partir de los registros."""

    idunidad: int
    numeroserie: str
    uuidpublico: str
    producto: Optional[str] = None
    sku: Optional[str] = None
    codigocertificado: str
    fechageneracion: datetime
    hashcertificado: str
    autenticidad: str
    total_eventos: int
    eventos_verificados: int
    documentos: int
    certificaciones: List[str] = Field(default_factory=list)
    emitido_por: Optional[str] = None
    mensaje: str
