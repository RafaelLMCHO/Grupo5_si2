from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class CreateTraceabilityEventRequest(BaseModel):
    """T038 - Alta de un evento de trazabilidad genérico (no ligado a un envío)."""

    tipoevento: str = Field(
        ...,
        description="Tipo de hito (fabricacion, exportacion, recepcion_almacen, venta, ...)",
    )
    idubicacion: int = Field(..., description="Ubicación física del evento")
    idactororigen: Optional[int] = Field(None, description="Actor que entrega/despacha")
    idactordestino: Optional[int] = Field(None, description="Actor que recibe/custodia")
    descripcion: Optional[str] = Field(None, max_length=500)
    unidadIds: List[int] = Field(default_factory=list, description="Unidades involucradas")
    fechahora: Optional[datetime] = Field(None, description="Fecha del hecho (por defecto ahora)")
    anchor: bool = Field(True, description="Anclar el evento en Blockchain al crearlo")


class RegistroBlockchainResponse(BaseModel):
    idregistro: int
    idevento: int
    payloadhash: str
    txhash: Optional[str] = None
    blocknumber: Optional[int] = None
    network: Optional[str] = None
    chainid: Optional[str] = None
    contractaddress: Optional[str] = None
    fechaenvio: Optional[datetime] = None
    fechaconfirmacion: Optional[datetime] = None
    estado: Optional[str] = None
    numeroconfirmaciones: Optional[int] = None
    mensajeerror: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TraceabilityEventDetailResponse(BaseModel):
    """T043 - Evento con su asociación a actor, ubicación, fecha y transacción."""

    idevento: int
    idtenant: int
    tipoevento: str
    fechahora: Optional[datetime] = None
    idactororigen: Optional[int] = None
    actor_origen_nombre: Optional[str] = None
    idactordestino: Optional[int] = None
    actor_destino_nombre: Optional[str] = None
    idubicacion: int
    ubicacion_nombre: Optional[str] = None
    idusuarioresponsable: int
    usuario_nombre: Optional[str] = None
    descripcion: Optional[str] = None
    payloadhash: Optional[str] = None
    estadoverificacion: Optional[str] = None
    unidades: List[str] = Field(default_factory=list)
    registro_blockchain: Optional[RegistroBlockchainResponse] = None


class VerifyEventResponse(BaseModel):
    idevento: int
    payloadhash: str
    registro_estado: Optional[str] = None
    txhash: Optional[str] = None
    en_blockchain: bool = False
    coincide: bool = False
    verificado: bool = False
    onchain_payloadhash: Optional[str] = None
    detalle: Optional[str] = None
