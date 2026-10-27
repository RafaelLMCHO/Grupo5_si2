from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, ConfigDict, Field


# Esquemas de respuesta JSON para la gestión de alertas e incidencias (CU-024)
class AlertaResponse(BaseModel):
    idalerta: int
    idtenant: int
    idunidad: Optional[int] = None
    idevento: Optional[int] = None
    tipoalerta: str
    descripcion: str
    gravedad: str
    fechadeteccion: datetime
    fecharesolucion: Optional[datetime] = None
    estado: str
    idusuarioresolutor: Optional[int] = None

    # Enriquecimiento para la UI (opcionales)
    numeroserie: Optional[str] = None
    uuidpublico: Optional[str] = None
    usuarioresolutor_nombre: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlertaListResponse(BaseModel):
    total: int
    items: List[AlertaResponse]


class AlertaSummaryResponse(BaseModel):
    total: int
    pendientes: int
    en_proceso: int
    resueltas: int
    criticas: int
    por_estado: Dict[str, int]
    por_gravedad: Dict[str, int]
    por_tipo: Dict[str, int]


class CreateAlertaRequest(BaseModel):
    tipoalerta: str = Field(
        ...,
        description="Tipo de incidencia (temperatura, vibracion, retraso_aduanero, "
                    "fraude_autenticidad, inconsistencia_cadena, etc.)",
    )
    descripcion: str = Field(..., min_length=5, max_length=1000)
    gravedad: str = Field("media", description="baja, media, alta o critica")
    idunidad: Optional[int] = Field(None, description="Unidad afectada (opcional)")
    idevento: Optional[int] = Field(None, description="Evento que originó la alerta (opcional)")


class UpdateAlertaEstadoRequest(BaseModel):
    estado: str = Field(..., description="Nuevo estado: pendiente, en_proceso o resuelta")
    comentario: Optional[str] = Field(
        None, max_length=500, description="Nota de clasificación o resolución"
    )
