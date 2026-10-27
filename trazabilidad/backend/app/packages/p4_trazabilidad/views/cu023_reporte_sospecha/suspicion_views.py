from typing import Optional
from pydantic import BaseModel, Field


# Esquemas para el reporte público de sospecha de falsificación (CU-023)
class ReportarSospechaRequest(BaseModel):
    uuidpublico: Optional[str] = Field(
        None, max_length=100, description="UUID público leído del código QR de la unidad"
    )
    numeroserie: Optional[str] = Field(
        None, max_length=100, description="Número de serie de la unidad (alternativo al UUID)"
    )
    motivo: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Motivo breve de la sospecha (ej. producto_falso, empaque_alterado, serial_duplicado)",
    )
    descripcion: Optional[str] = Field(
        None, max_length=2000, description="Detalle de la irregularidad observada"
    )
    evidencia: Optional[str] = Field(
        None, max_length=500, description="URL o referencia de la evidencia (foto, factura, etc.)"
    )
    nombrereportante: Optional[str] = Field(None, max_length=100)
    contactoreportante: Optional[str] = Field(None, max_length=150)


class ReporteSospechaResponse(BaseModel):
    idalerta: int
    referencia: str
    tipoalerta: str
    estado: str
    mensaje: str
