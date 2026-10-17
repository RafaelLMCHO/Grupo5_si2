from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.cu021_eventos_transporte.transport_event import Alerta
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu005_bitacora.notification import Notificacion
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.controllers.shared import get_bolivia_now
from app.views.cu023_reporte_sospecha.suspicion_views import (
    ReportarSospechaRequest,
    ReporteSospechaResponse,
)

router = APIRouter(prefix="/reports", tags=["Reporte de Sospecha (CU-023)"])

_ROLES_NOTIFICABLES = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")


class SuspicionController:

    @staticmethod
    def _resolver_unidad(
        db: Session, body: ReportarSospechaRequest
    ) -> UnidadProducto:
        if body.uuidpublico:
            unidad = db.execute(
                select(UnidadProducto).where(
                    UnidadProducto.uuidpublico == body.uuidpublico.strip()
                )
            ).scalar_one_or_none()
            if unidad:
                return unidad

        if body.numeroserie:
            unidad = db.execute(
                select(UnidadProducto).where(
                    UnidadProducto.numeroserie == body.numeroserie.strip()
                )
            ).scalar_one_or_none()
            if unidad:
                return unidad

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se pudo identificar la unidad reportada. Verifique el código QR o el número de serie.",
        )

    @staticmethod
    def _notificar_incidencia(db: Session, alerta: Alerta) -> None:
        """Notifica a los responsables de la empresa (best-effort, no rompe el reporte)."""
        try:
            stmt = (
                select(UsuarioTenant.idusuariotenant)
                .join(
                    UsuarioTenantRol,
                    UsuarioTenantRol.idusuariotenant == UsuarioTenant.idusuariotenant,
                )
                .join(Role, Role.idrol == UsuarioTenantRol.idrol)
                .where(
                    UsuarioTenant.idtenant == alerta.idtenant,
                    Role.nombrerol.in_(_ROLES_NOTIFICABLES),
                )
                .distinct()
            )
            iduts = db.execute(stmt).scalars().all()
            for idut in iduts:
                db.add(
                    Notificacion(
                        idusuariotenant=idut,
                        titulo="Reporte de sospecha de falsificación",
                        contenido=(
                            f"Se recibió un reporte ciudadano de posible falsificación "
                            f"(alerta #{alerta.idalerta}). Requiere revisión."
                        ),
                        enlaceaccion=f"/alerts/{alerta.idalerta}",
                    )
                )
            db.flush()
        except Exception:  # pragma: no cover - la notificación nunca debe romper el reporte
            db.rollback()

    @staticmethod
    def report_suspicion(
        db: Session, body: ReportarSospechaRequest
    ) -> ReporteSospechaResponse:
        if not (body.uuidpublico or body.numeroserie):
            raise HTTPException(
                status_code=400,
                detail="Debe indicar el UUID público o el número de serie de la unidad.",
            )

        unidad = SuspicionController._resolver_unidad(db, body)

        partes = [f"Reporte de sospecha: {body.motivo.strip()}."]
        if body.descripcion and body.descripcion.strip():
            partes.append(f"Descripción: {body.descripcion.strip()}")
        if body.evidencia and body.evidencia.strip():
            partes.append(f"Evidencia: {body.evidencia.strip()}")
        if body.nombrereportante and body.nombrereportante.strip():
            partes.append(f"Reportante: {body.nombrereportante.strip()}")
        if body.contactoreportante and body.contactoreportante.strip():
            partes.append(f"Contacto: {body.contactoreportante.strip()}")
        partes.append(f"Unidad: {unidad.numeroserie} (UUID {unidad.uuidpublico}).")

        alerta = Alerta(
            idtenant=unidad.idtenant,
            idunidad=unidad.idunidad,
            tipoalerta="fraude_autenticidad",
            descripcion="\n".join(partes),
            gravedad="alta",
            fechadeteccion=get_bolivia_now(),
            estado="pendiente",
        )
        db.add(alerta)
        db.flush()

        SuspicionController._notificar_incidencia(db, alerta)

        db.commit()
        db.refresh(alerta)

        return ReporteSospechaResponse(
            idalerta=alerta.idalerta,
            referencia=f"REP-{alerta.idalerta:06d}",
            tipoalerta=str(alerta.tipoalerta),
            estado=str(alerta.estado),
            mensaje="Reporte registrado. El equipo de operaciones revisará la incidencia.",
        )


@router.post("/suspicion", response_model=ReporteSospechaResponse, status_code=status.HTTP_201_CREATED)
def report_suspicion_route(
    body: ReportarSospechaRequest,
    db: Session = Depends(get_db),
):
    """Reporte público de sospecha de falsificación (sin autenticación). CU-023."""
    return SuspicionController.report_suspicion(db, body)
