"""CU-033 - Registrar Evento en Blockchain y consultar registros.

Cubre:
- T038: API REST de registro de eventos de trazabilidad.
- T042: Integración con el Smart Contract vía Web3.
- T043: Asociación del evento con actor, ubicación, fecha y transacción.
- T044: Persistencia de hashes/identificadores en `registroblockchain`.
- T045: Consulta y validación de registros Blockchain.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.controllers.shared import (
    get_bolivia_now,
    get_client_ip,
    get_idusuariotenant,
    require_roles,
    resolve_tenant_id,
)
from app.db.session import get_db
from app.models.cu002_usuarios.user import User
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu021_eventos_transporte.transport_event import (
    TIPO_EVENTO_ENUM,
    EventoTrazabilidad,
    EventoUnidad,
)
from app.models.cu033_blockchain.registro_blockchain import RegistroBlockchain
from app.services.blockchain.registry_service import blockchain_registry
from app.views.cu033_blockchain.blockchain_views import (
    CreateTraceabilityEventRequest,
    RegistroBlockchainResponse,
    TraceabilityEventDetailResponse,
    VerifyEventResponse,
)

router = APIRouter(prefix="/blockchain", tags=["Registro en Blockchain (CU-033)"])

ROLES_BLOCKCHAIN = ("SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones")
requires_blockchain = require_roles(*ROLES_BLOCKCHAIN)


def _actor_nombre(actor: ActorCadena) -> str:
    return actor.nombre or actor.razonsocial or f"Actor #{actor.idactor}"


class BlockchainController:

    # ── Helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def _get_evento(db: Session, idtenant: int, idevento: int) -> EventoTrazabilidad:
        event = db.execute(
            select(EventoTrazabilidad).where(
                EventoTrazabilidad.idevento == idevento,
                EventoTrazabilidad.idtenant == idtenant,
            )
        ).scalar_one_or_none()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evento de trazabilidad {idevento} no encontrado.",
            )
        return event

    @staticmethod
    def _registrar_bitacora(
        db: Session, current_user: User, tenant_id: int, accion: str, identidad: int, ip: str
    ) -> None:
        idut = get_idusuariotenant(db, current_user)
        db.add(
            Bitacora(
                idusuariotenant=idut,
                accion=accion,
                entidad="RegistroBlockchain",
                identidad=identidad,
                ip=ip,
                fechahora=get_bolivia_now(),
            )
        )

    @staticmethod
    def _serialize_detail(
        db: Session, event: EventoTrazabilidad
    ) -> TraceabilityEventDetailResponse:
        ubic = db.execute(
            select(Ubicacion).where(Ubicacion.idubicacion == event.idubicacion)
        ).scalar_one_or_none()
        usuario = db.execute(
            select(User.nombrecompleto).where(User.idusuario == event.idusuarioresponsable)
        ).scalar_one_or_none()

        actor_orig = None
        if event.idactororigen:
            a = db.execute(
                select(ActorCadena).where(ActorCadena.idactor == event.idactororigen)
            ).scalar_one_or_none()
            actor_orig = _actor_nombre(a) if a else None

        actor_dest = None
        if event.idactordestino:
            a = db.execute(
                select(ActorCadena).where(ActorCadena.idactor == event.idactordestino)
            ).scalar_one_or_none()
            actor_dest = _actor_nombre(a) if a else None

        created = db.execute(
            select(UnidadProducto.numeroserie)
            .join(EventoUnidad, EventoUnidad.idunidad == UnidadProducto.idunidad)
            .where(EventoUnidad.idevento == event.idevento)
        ).scalars().all()

        registro = blockchain_registry.get_registro(db, event.idevento)

        return TraceabilityEventDetailResponse(
            idevento=event.idevento,
            idtenant=event.idtenant,
            tipoevento=str(event.tipoevento),
            fechahora=event.fechahora,
            idactororigen=event.idactororigen,
            actor_origen_nombre=actor_orig,
            idactordestino=event.idactordestino,
            actor_destino_nombre=actor_dest,
            idubicacion=event.idubicacion,
            ubicacion_nombre=ubic.nombre if ubic else None,
            idusuarioresponsable=event.idusuarioresponsable,
            usuario_nombre=usuario,
            descripcion=event.descripcion,
            payloadhash=event.payloadhash,
            estadoverificacion=str(event.estadoverificacion) if event.estadoverificacion else None,
            unidades=list(created),
            registro_blockchain=(
                RegistroBlockchainResponse.model_validate(registro) if registro else None
            ),
        )

    # ── Casos de uso ───────────────────────────────────────────────────────
    @staticmethod
    def create_event(
        db: Session, current_user: User, request: Request, body: CreateTraceabilityEventRequest
    ) -> TraceabilityEventDetailResponse:
        tenant_id = resolve_tenant_id(db, current_user)

        if body.tipoevento not in TIPO_EVENTO_ENUM.enums:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Tipo de evento inválido: '{body.tipoevento}'. "
                    f"Valores permitidos: {', '.join(TIPO_EVENTO_ENUM.enums)}."
                ),
            )

        ubic = db.execute(
            select(Ubicacion).where(
                Ubicacion.idubicacion == body.idubicacion, Ubicacion.idtenant == tenant_id
            )
        ).scalar_one_or_none()
        if not ubic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La ubicación {body.idubicacion} no existe en la empresa.",
            )

        for actor_id in (body.idactororigen, body.idactordestino):
            if actor_id is not None:
                actor = db.execute(
                    select(ActorCadena).where(
                        ActorCadena.idactor == actor_id, ActorCadena.idtenant == tenant_id
                    )
                ).scalar_one_or_none()
                if not actor:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El actor {actor_id} no existe en la empresa.",
                    )

        unidades = []
        if body.unidadIds:
            unidades = db.execute(
                select(UnidadProducto).where(
                    UnidadProducto.idunidad.in_(body.unidadIds),
                    UnidadProducto.idtenant == tenant_id,
                )
            ).scalars().all()
            if len(unidades) != len(set(body.unidadIds)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Una o más unidades no existen en la empresa.",
                )

        hora = body.fechahora or get_bolivia_now()
        evento = EventoTrazabilidad(
            idtenant=tenant_id,
            tipoevento=body.tipoevento,
            fechahora=hora,
            idactororigen=body.idactororigen,
            idactordestino=body.idactordestino,
            idubicacion=body.idubicacion,
            idusuarioresponsable=current_user.idusuario,
            descripcion=body.descripcion,
            estadoverificacion="pendiente",
        )
        db.add(evento)
        db.flush()

        evento.payloadhash = blockchain_registry.compute_payload_hash(evento)

        for unidad in unidades:
            db.add(EventoUnidad(idevento=evento.idevento, idunidad=unidad.idunidad))

        if body.anchor:
            blockchain_registry.anchor_event(db, evento, commit=False)

        BlockchainController._registrar_bitacora(
            db, current_user, tenant_id, "REGISTRAR_EVENTO_BLOCKCHAIN",
            evento.idevento, get_client_ip(request),
        )

        db.commit()
        db.refresh(evento)
        return BlockchainController._serialize_detail(db, evento)

    @staticmethod
    def anchor_event(
        db: Session, current_user: User, request: Request, idevento: int, force: bool = False
    ) -> RegistroBlockchainResponse:
        tenant_id = resolve_tenant_id(db, current_user)
        evento = BlockchainController._get_evento(db, tenant_id, idevento)

        if not evento.payloadhash:
            evento.payloadhash = blockchain_registry.compute_payload_hash(evento)

        registro = blockchain_registry.anchor_event(db, evento, commit=False, force=force)
        BlockchainController._registrar_bitacora(
            db, current_user, tenant_id, "ANCLAR_EVENTO_BLOCKCHAIN",
            evento.idevento, get_client_ip(request),
        )
        db.commit()
        db.refresh(registro)
        return RegistroBlockchainResponse.model_validate(registro)

    @staticmethod
    def get_event(db: Session, current_user: User, idevento: int) -> TraceabilityEventDetailResponse:
        tenant_id = resolve_tenant_id(db, current_user)
        evento = BlockchainController._get_evento(db, tenant_id, idevento)
        return BlockchainController._serialize_detail(db, evento)

    @staticmethod
    def verify_event(db: Session, current_user: User, idevento: int) -> VerifyEventResponse:
        tenant_id = resolve_tenant_id(db, current_user)
        evento = BlockchainController._get_evento(db, tenant_id, idevento)
        if not evento.payloadhash:
            evento.payloadhash = blockchain_registry.compute_payload_hash(evento)
            db.commit()
            db.refresh(evento)
        return VerifyEventResponse(**blockchain_registry.verify_event(db, evento))

    @staticmethod
    def list_registry(db: Session, current_user: User) -> List[RegistroBlockchainResponse]:
        tenant_id = resolve_tenant_id(db, current_user)
        registros = blockchain_registry.list_registros(db, tenant_id)
        return [RegistroBlockchainResponse.model_validate(r) for r in registros]

    @staticmethod
    def status() -> dict:
        return blockchain_registry.status()


# ── Rutas FastAPI ─────────────────────────────────────────────────────────
@router.post("/events", response_model=TraceabilityEventDetailResponse)
def create_event_route(
    body: CreateTraceabilityEventRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_blockchain),
):
    """T038 - Registrar un evento de trazabilidad (y anclarlo en Blockchain)."""
    return BlockchainController.create_event(db, current_user, request, body)


@router.post("/events/{idevento}/anchor", response_model=RegistroBlockchainResponse)
def anchor_event_route(
    idevento: int,
    request: Request,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(requires_blockchain),
):
    """T042/T044 - Anclar (o reintentar el anclaje de) un evento existente."""
    return BlockchainController.anchor_event(db, current_user, request, idevento, force)


@router.get("/events/{idevento}", response_model=TraceabilityEventDetailResponse)
def get_event_route(
    idevento: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """T043 - Evento con actor, ubicación, fecha y transacción asociada."""
    return BlockchainController.get_event(db, current_user, idevento)


@router.get("/events/{idevento}/verify", response_model=VerifyEventResponse)
def verify_event_route(
    idevento: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """T045 - Verificar el hash local contra el registro anclado on-chain."""
    return BlockchainController.verify_event(db, current_user, idevento)


@router.get("/registry", response_model=List[RegistroBlockchainResponse])
def list_registry_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """T045 - Listar los registros Blockchain de la empresa activa."""
    return BlockchainController.list_registry(db, current_user)


@router.get("/status")
def status_route(current_user: User = Depends(get_current_user)):
    """T045 - Estado de la conexión a la red y del contrato desplegado."""
    return BlockchainController.status()
