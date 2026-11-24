from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.db.session import get_db
from app.packages.p1_seguridad.models.cu005_bitacora.bitacora import Bitacora
from app.packages.p1_seguridad.models.cu005_bitacora.notification import Notificacion
from app.packages.p1_seguridad.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.packages.p1_seguridad.models.cu002_usuarios.user import User
from app.controllers.shared import require_roles, resolve_tenant_id
from app.packages.p1_seguridad.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.packages.p1_seguridad.views.cu005_bitacora.bitacora_views import (
    BitacoraResponse,
    BitacoraListResponse,
    NotificacionResponse,
    NotificacionListResponse,
    EnviarNotificacionRequest,
    EnviarNotificacionResponse,
)
from app.services.push_gateway import push_gateway


router = APIRouter(tags=["Bitácora de Auditoría y Notificaciones (CU-005)"])


class BitacoraController:
    # 1. Consultar registros de bitácora con filtros (acción, entidad, tenant) y paginación
    @staticmethod
    def list_bitacora(
        db: Session,
        current_user: User,
        accion: Optional[str] = None,
        entidad: Optional[str] = None,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> BitacoraListResponse:
        from app.controllers.shared import _es_superadmin, resolve_tenant_id
        from app.packages.p1_seguridad.models.cu001_tenants.tenant import Tenant

        is_super = _es_superadmin(db, current_user)
        query = (
            select(
                Bitacora,
                User.email.label("usuario_email"),
                User.nombrecompleto.label("usuario_nombre"),
                Tenant.nombre.label("empresa_nombre"),
                UsuarioTenant.idtenant.label("idtenant")
            )
            .outerjoin(UsuarioTenant, Bitacora.idusuariotenant == UsuarioTenant.idusuariotenant)
            .outerjoin(User, UsuarioTenant.idusuario == User.idusuario)
            .outerjoin(Tenant, UsuarioTenant.idtenant == Tenant.idtenant)
        )

        if is_super:
            if tenant_id and tenant_id != -1:
                query = query.where(UsuarioTenant.idtenant == tenant_id)
        else:
            active_tenant_id = resolve_tenant_id(db, current_user)
            # Aislamiento multi-tenant estricto: solo eventos del tenant activo
            query = query.where(UsuarioTenant.idtenant == active_tenant_id)

        if accion and accion.strip():
            query = query.where(func.lower(Bitacora.accion) == accion.strip().lower())
        if entidad and entidad.strip():
            query = query.where(func.lower(Bitacora.entidad) == entidad.strip().lower())

        # Total para paginación
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        # Orden cronológico inverso (lo más reciente primero)
        query = query.order_by(Bitacora.fechahora.desc()).offset(skip).limit(limit)
        rows = db.execute(query).all()

        items = []
        for row in rows:
            b = row.Bitacora
            items.append(
                BitacoraResponse(
                    idbitacora=b.idbitacora,
                    idusuariotenant=b.idusuariotenant,
                    accion=b.accion,
                    entidad=b.entidad,
                    identidad=b.identidad,
                    ip=b.ip,
                    fechahora=b.fechahora,
                    usuario_email=row.usuario_email,
                    usuario_nombre=row.usuario_nombre,
                    empresa_nombre=row.empresa_nombre,
                    idtenant=row.idtenant,
                )
            )

        return BitacoraListResponse(total=total, items=items)

    # 2. Listar notificaciones del usuario actual
    @staticmethod
    def list_notifications(
        db: Session,
        current_user: User,
        only_unread: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> NotificacionListResponse:
        from app.controllers.shared import _es_superadmin, resolve_tenant_id

        is_super = _es_superadmin(db, current_user)
        if is_super:
            stmt_uts = select(UsuarioTenant.idusuariotenant).where(
                UsuarioTenant.idusuario == current_user.idusuario
            )
        else:
            active_tenant_id = resolve_tenant_id(db, current_user)
            stmt_uts = select(UsuarioTenant.idusuariotenant).where(
                UsuarioTenant.idusuario == current_user.idusuario,
                UsuarioTenant.idtenant == active_tenant_id
            )
        iduts = list(db.execute(stmt_uts).scalars().all())

        query = select(Notificacion)
        if iduts:
            query = query.where(Notificacion.idusuariotenant.in_(iduts))
        else:
            query = query.where(False)

        if only_unread:
            query = query.where(Notificacion.leida == False)

        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        # Cantidad de notificaciones pendientes
        unread_stmt = select(func.count()).where(Notificacion.leida == False)
        if iduts:
            unread_stmt = unread_stmt.where(Notificacion.idusuariotenant.in_(iduts))
        else:
            unread_stmt = unread_stmt.where(False)
        unread_count = db.execute(unread_stmt).scalar_one()

        query = query.order_by(Notificacion.fechaenvio.desc()).offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return NotificacionListResponse(
            total=total,
            unread_count=unread_count,
            items=[NotificacionResponse.model_validate(n) for n in items]
        )

    # 3. Marcar notificación como leída
    @staticmethod
    def mark_notification_read(
        db: Session,
        idnotificacion: int,
        current_user: User
    ) -> NotificacionResponse:
        # Resolver el vínculo UsuarioTenant del solicitante para validar propiedad.
        stmt_ut = select(UsuarioTenant.idusuariotenant).where(
            UsuarioTenant.idusuario == current_user.idusuario
        )
        idut = db.execute(stmt_ut).scalar()

        stmt = select(Notificacion).where(Notificacion.idnotificacion == idnotificacion)
        notif = db.execute(stmt).scalar_one_or_none()

        # 404 tanto si no existe como si pertenece a otro usuario: no filtrar datos.
        if not notif or (idut is not None and notif.idusuariotenant != idut):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notificación con ID {idnotificacion} no encontrada."
            )

        notif.leida = True
        notif.fechalectura = datetime.utcnow()
        db.commit()
        db.refresh(notif)

        return NotificacionResponse.model_validate(notif)


AuditController = BitacoraController


# Endpoints API REST

@router.get("/bitacora", response_model=BitacoraListResponse)
def get_bitacora(
    accion: Optional[str] = Query(None, description="Filtrar por tipo de acción (ej. INSERT, UPDATE, DELETE, LOGIN)"),
    entidad: Optional[str] = Query(None, description="Filtrar por entidad (ej. Venta, Usuario, EventoTrazabilidad)"),
    tenant_id: Optional[int] = Query(None, description="Filtrar por empresa/tenant (solo SuperAdministrador)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultar bitácora de auditoría con aislamiento multi-tenant estricto."""
    return BitacoraController.list_bitacora(db, current_user, accion, entidad, tenant_id, skip, limit)


@router.get("/notifications", response_model=NotificacionListResponse)
def get_notifications(
    only_unread: bool = Query(False, description="Filtrar solo notificaciones no leídas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consultar notificaciones del usuario."""
    return BitacoraController.list_notifications(db, current_user, only_unread, skip, limit)


@router.patch("/notifications/{idnotificacion}/read", response_model=NotificacionResponse)
def mark_notification_read(
    idnotificacion: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Marcar notificación como leída."""
    return BitacoraController.mark_notification_read(db, idnotificacion, current_user)


@router.post(
    "/notifications/push",
    response_model=EnviarNotificacionResponse,
    dependencies=[Depends(require_roles("SuperAdministrador", "AdministradorEmpresa"))],
)
def enviar_notificacion_push(
    body: EnviarNotificacionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cierra la brecha de push de CU-005: emite notificaciones a todos los
    usuarios activos del tenant y delega el envío externo al PushGateway.
    """
    tenant_id = resolve_tenant_id(db, current_user)
    destinatarios = push_gateway.notify_tenant(
        db, tenant_id, body.titulo, body.contenido, body.enlaceaccion
    )
    db.commit()
    return EnviarNotificacionResponse(
        destinatarios=destinatarios,
        titulo=body.titulo,
        contenido=body.contenido,
        enlaceaccion=body.enlaceaccion,
    )

