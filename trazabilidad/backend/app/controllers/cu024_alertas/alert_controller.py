from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.session import get_db
from app.models.cu021_eventos_transporte.transport_event import (
    Alerta,
    EventoTrazabilidad,
    TIPO_ALERTA_ENUM,
    GRAVEDAD_ALERTA_ENUM,
    ESTADO_ALERTA_ENUM,
)
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu002_usuarios.user import User
from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import (
    get_bolivia_now,
    get_client_ip,
    get_idusuariotenant,
    require_roles,
    resolve_tenant_id,
)
from app.views.cu024_alertas.alert_views import (
    AlertaResponse,
    AlertaListResponse,
    AlertaSummaryResponse,
    CreateAlertaRequest,
    UpdateAlertaEstadoRequest,
)

router = APIRouter(prefix="/alerts", tags=["Alertas e Incidencias (CU-024)"])

# Roles autorizados a visualizar, clasificar y resolver alertas.
ROLES_ALERTAS = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")

requires_alertas = require_roles(*ROLES_ALERTAS)

_TIPOS_VALIDOS = set(TIPO_ALERTA_ENUM.enums)
_GRAVEDADES_VALIDAS = set(GRAVEDAD_ALERTA_ENUM.enums)
_ESTADOS_VALIDOS = set(ESTADO_ALERTA_ENUM.enums)


class AlertaController:

    @staticmethod
    def _to_response(db: Session, alerta: Alerta) -> AlertaResponse:
        numeroserie = None
        uuidpublico = None
        if alerta.idunidad:
            row = db.execute(
                select(UnidadProducto.numeroserie, UnidadProducto.uuidpublico).where(
                    UnidadProducto.idunidad == alerta.idunidad
                )
            ).first()
            if row:
                numeroserie, uuidpublico = row

        resolutor = None
        if alerta.idusuarioresolutor:
            resolutor = db.execute(
                select(User.nombrecompleto).where(
                    User.idusuario == alerta.idusuarioresolutor
                )
            ).scalar_one_or_none()

        return AlertaResponse(
            idalerta=alerta.idalerta,
            idtenant=alerta.idtenant,
            idunidad=alerta.idunidad,
            idevento=alerta.idevento,
            tipoalerta=str(alerta.tipoalerta),
            descripcion=alerta.descripcion,
            gravedad=str(alerta.gravedad),
            fechadeteccion=alerta.fechadeteccion,
            fecharesolucion=alerta.fecharesolucion,
            estado=str(alerta.estado),
            idusuarioresolutor=alerta.idusuarioresolutor,
            numeroserie=numeroserie,
            uuidpublico=uuidpublico,
            usuarioresolutor_nombre=resolutor,
        )

    @staticmethod
    def _registrar_bitacora(
        db: Session, user: User, tenant_id: int, accion: str, identidad: int, ip: str
    ) -> None:
        idut = get_idusuariotenant(db, user)
        db.add(
            Bitacora(
                idusuariotenant=idut,
                accion=accion,
                entidad="Alerta",
                identidad=identidad,
                ip=ip,
                fechahora=get_bolivia_now(),
            )
        )

    @staticmethod
    def list_alerts(
        db: Session,
        user: User,
        estado: Optional[str] = None,
        tipoalerta: Optional[str] = None,
        gravedad: Optional[str] = None,
        idunidad: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> AlertaListResponse:
        tenant_id = resolve_tenant_id(db, user)

        query = select(Alerta).where(Alerta.idtenant == tenant_id)
        if estado:
            if estado not in _ESTADOS_VALIDOS:
                raise HTTPException(status_code=400, detail=f"Estado inválido: {estado}.")
            query = query.where(Alerta.estado == estado)
        if tipoalerta:
            if tipoalerta not in _TIPOS_VALIDOS:
                raise HTTPException(status_code=400, detail=f"Tipo de alerta inválido: {tipoalerta}.")
            query = query.where(Alerta.tipoalerta == tipoalerta)
        if gravedad:
            if gravedad not in _GRAVEDADES_VALIDAS:
                raise HTTPException(status_code=400, detail=f"Gravedad inválida: {gravedad}.")
            query = query.where(Alerta.gravedad == gravedad)
        if idunidad:
            query = query.where(Alerta.idunidad == idunidad)

        total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

        # Orden cronológico inverso (lo más reciente primero).
        query = (
            query.order_by(Alerta.fechadeteccion.desc())
            .offset(skip)
            .limit(limit)
        )
        alertas = db.execute(query).scalars().all()

        return AlertaListResponse(
            total=total,
            items=[AlertaController._to_response(db, a) for a in alertas],
        )

    @staticmethod
    def summary(db: Session, user: User) -> AlertaSummaryResponse:
        tenant_id = resolve_tenant_id(db, user)

        rows = db.execute(
            select(Alerta.estado, Alerta.gravedad, Alerta.tipoalerta, func.count())
            .where(Alerta.idtenant == tenant_id)
            .group_by(Alerta.estado, Alerta.gravedad, Alerta.tipoalerta)
        ).all()

        por_estado = {e: 0 for e in _ESTADOS_VALIDOS}
        por_gravedad = {g: 0 for g in _GRAVEDADES_VALIDAS}
        por_tipo = {t: 0 for t in _TIPOS_VALIDOS}
        total = 0
        criticas = 0
        for estado, gravedad, tipo, count in rows:
            total += count
            por_estado[str(estado)] = por_estado.get(str(estado), 0) + count
            por_gravedad[str(gravedad)] = por_gravedad.get(str(gravedad), 0) + count
            por_tipo[str(tipo)] = por_tipo.get(str(tipo), 0) + count
            if str(gravedad) == "critica":
                criticas += count

        return AlertaSummaryResponse(
            total=total,
            pendientes=por_estado.get("pendiente", 0),
            en_proceso=por_estado.get("en_proceso", 0),
            resueltas=por_estado.get("resuelta", 0),
            criticas=criticas,
            por_estado=por_estado,
            por_gravedad=por_gravedad,
            por_tipo=por_tipo,
        )

    @staticmethod
    def get_alert(db: Session, user: User, idalerta: int) -> AlertaResponse:
        tenant_id = resolve_tenant_id(db, user)
        alerta = db.execute(
            select(Alerta).where(
                Alerta.idalerta == idalerta, Alerta.idtenant == tenant_id
            )
        ).scalar_one_or_none()
        if not alerta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alerta con ID {idalerta} no encontrada.",
            )
        return AlertaController._to_response(db, alerta)

    @staticmethod
    def create_alert(
        db: Session,
        user: User,
        request: Request,
        body: CreateAlertaRequest,
    ) -> AlertaResponse:
        tenant_id = resolve_tenant_id(db, user)

        if body.tipoalerta not in _TIPOS_VALIDOS:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de alerta inválido. Valores permitidos: {sorted(_TIPOS_VALIDOS)}.",
            )
        if body.gravedad not in _GRAVEDADES_VALIDAS:
            raise HTTPException(
                status_code=400,
                detail=f"Gravedad inválida. Valores permitidos: {sorted(_GRAVEDADES_VALIDAS)}.",
            )

        if body.idunidad:
            unidad = db.execute(
                select(UnidadProducto).where(
                    UnidadProducto.idunidad == body.idunidad,
                    UnidadProducto.idtenant == tenant_id,
                )
            ).scalar_one_or_none()
            if not unidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"La unidad con ID {body.idunidad} no existe en su empresa.",
                )

        if body.idevento:
            evento = db.execute(
                select(EventoTrazabilidad).where(
                    EventoTrazabilidad.idevento == body.idevento,
                    EventoTrazabilidad.idtenant == tenant_id,
                )
            ).scalar_one_or_none()
            if not evento:
                raise HTTPException(
                    status_code=400,
                    detail=f"El evento con ID {body.idevento} no existe en su empresa.",
                )

        hora = get_bolivia_now()
        alerta = Alerta(
            idtenant=tenant_id,
            idunidad=body.idunidad,
            idevento=body.idevento,
            tipoalerta=body.tipoalerta,
            descripcion=body.descripcion,
            gravedad=body.gravedad,
            fechadeteccion=hora,
            estado="pendiente",
        )
        db.add(alerta)
        db.flush()

        AlertaController._registrar_bitacora(
            db, user, tenant_id, "CREAR_ALERTA", alerta.idalerta, get_client_ip(request)
        )
        db.commit()
        db.refresh(alerta)
        return AlertaController._to_response(db, alerta)

    @staticmethod
    def update_estado(
        db: Session,
        user: User,
        request: Request,
        idalerta: int,
        body: UpdateAlertaEstadoRequest,
    ) -> AlertaResponse:
        tenant_id = resolve_tenant_id(db, user)

        if body.estado not in _ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=400,
                detail=f"Estado inválido. Valores permitidos: {sorted(_ESTADOS_VALIDOS)}.",
            )

        alerta = db.execute(
            select(Alerta).where(
                Alerta.idalerta == idalerta, Alerta.idtenant == tenant_id
            )
        ).scalar_one_or_none()
        if not alerta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alerta con ID {idalerta} no encontrada.",
            )

        estado_anterior = str(alerta.estado)
        alerta.estado = body.estado

        if body.estado == "resuelta":
            alerta.fecharesolucion = get_bolivia_now()
            alerta.idusuarioresolutor = user.idusuario
        else:
            alerta.fecharesolucion = None
            alerta.idusuarioresolutor = None

        if body.comentario and body.comentario.strip():
            alerta.descripcion = f"{alerta.descripcion}\n[clasificación] {body.comentario.strip()}"

        AlertaController._registrar_bitacora(
            db,
            user,
            tenant_id,
            f"CLASIFICAR_ALERTA_{body.estado.upper()}",
            alerta.idalerta,
            get_client_ip(request),
        )
        db.commit()
        db.refresh(alerta)
        return AlertaController._to_response(db, alerta)


# Endpoints API REST

@router.get("", response_model=AlertaListResponse)
def list_alerts_route(
    estado: Optional[str] = Query(None, description="Filtrar por estado (pendiente, en_proceso, resuelta)"),
    tipoalerta: Optional[str] = Query(None, description="Filtrar por tipo de alerta"),
    gravedad: Optional[str] = Query(None, description="Filtrar por gravedad (baja, media, alta, critica)"),
    idunidad: Optional[int] = Query(None, description="Filtrar por unidad afectada"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_alertas),
):
    """Listar alertas e incidencias de la empresa (CU-024)."""
    return AlertaController.list_alerts(
        db, current_user, estado, tipoalerta, gravedad, idunidad, skip, limit
    )


@router.get("/summary", response_model=AlertaSummaryResponse)
def summary_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_alertas),
):
    """Resumen de alertas por estado, gravedad y tipo (CU-024)."""
    return AlertaController.summary(db, current_user)


@router.get("/{idalerta}", response_model=AlertaResponse)
def get_alert_route(
    idalerta: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_alertas),
):
    """Detalle de una alerta (CU-024)."""
    return AlertaController.get_alert(db, current_user, idalerta)


@router.post("", response_model=AlertaResponse, status_code=status.HTTP_201_CREATED)
def create_alert_route(
    body: CreateAlertaRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_alertas),
):
    """Registrar manualmente una incidencia (CU-024)."""
    return AlertaController.create_alert(db, current_user, request, body)


@router.patch("/{idalerta}/estado", response_model=AlertaResponse)
def update_estado_route(
    idalerta: int,
    body: UpdateAlertaEstadoRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_alertas),
):
    """Clasificar o resolver una alerta (CU-024)."""
    return AlertaController.update_estado(db, current_user, request, idalerta, body)
