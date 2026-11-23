from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.db.session import get_db
from app.packages.p1_seguridad.models.cu001_tenants.tenant import Tenant
from app.packages.p1_seguridad.models.cu002_usuarios.user import User
from app.packages.p1_seguridad.controllers.cu004_autenticacion.auth_controller import get_current_user
from app.packages.p1_seguridad.views.cu001_tenants.tenant_views import (
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse
)

router = APIRouter(prefix="/tenants", tags=["Gestión de Empresas (CU-001)"])


def _require_superadmin_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    from app.controllers.shared import require_roles
    checker = require_roles("SuperAdministrador")
    return checker(db=db, current_user=current_user)


class TenantController:
    @staticmethod
    def list_tenants(
        db: Session,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
        only_active: bool = False
    ) -> TenantListResponse:
        query = select(Tenant)

        if only_active:
            query = query.where(Tenant.activo == True)

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            query = query.where(
                or_(
                    func.lower(Tenant.nombre).like(term),
                    func.lower(Tenant.razonsocial).like(term),
                    func.lower(Tenant.nit).like(term),
                    func.lower(Tenant.email).like(term)
                )
            )

        # Contar total
        count_stmt = select(func.count()).select_from(query.subquery())
        total = db.execute(count_stmt).scalar_one()

        # Ejecutar consulta paginada
        query = query.order_by(Tenant.idtenant.asc()).offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return TenantListResponse(
            total=total,
            items=[TenantResponse.model_validate(t) for t in items]
        )

    @staticmethod
    def create_tenant(db: Session, data: TenantCreate) -> TenantResponse:
        # Validar unicidad del NIT
        stmt_nit = select(Tenant).where(Tenant.nit == data.nit.strip())
        existing = db.execute(stmt_nit).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una empresa registrada con el NIT '{data.nit}'."
            )

        tenant = Tenant(
            nombre=data.nombre.strip(),
            razonsocial=data.razonsocial.strip(),
            nit=data.nit.strip(),
            email=data.email.strip().lower(),
            telefono=data.telefono.strip() if data.telefono else None,
            activo=data.activo if data.activo is not None else True
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        # Asignar suscripción (trial o el plan solicitado)
        try:
            from app.packages.p8_suscripciones.controllers.cu037_suscripciones.subscription_controller import SubscriptionService
            from app.packages.p8_suscripciones.models.cu036_planes.subscription_models import Plan
            if data.idplan and data.idplan > 0:
                plan_obj = db.execute(select(Plan).where(Plan.idplan == data.idplan)).scalar_one_or_none()
                if plan_obj:
                    from datetime import timedelta
                    inicio = func.now()
                    fin = func.now() + timedelta(days=plan_obj.diastrial or 30)
                    from app.packages.p8_suscripciones.models.cu036_planes.subscription_models import Suscripcion
                    sub = Suscripcion(
                        idtenant=tenant.idtenant,
                        idplan=plan_obj.idplan,
                        estado="trial" if (plan_obj.diastrial and plan_obj.diastrial > 0) else "activa",
                        fechainicio=inicio,
                        fechafin=fin,
                        renovacionautomatica=False,
                    )
                    db.add(sub)
                    db.commit()
                else:
                    SubscriptionService.asignar_trial_por_defecto(db, tenant.idtenant)
                    db.commit()
            else:
                SubscriptionService.asignar_trial_por_defecto(db, tenant.idtenant)
                db.commit()
        except Exception as e:
            db.rollback()

        # Si se proporcionó contraseña (registro público desde Login), crear el usuario Administrador
        if data.password and data.password.strip():
            try:
                from app.core.security import hash_password
                from app.packages.p1_seguridad.models.cu002_usuarios.user import User
                from app.packages.p1_seguridad.models.cu002_usuarios.usuario_tenant import UsuarioTenant
                from app.packages.p1_seguridad.models.cu003_roles_permisos.role import Role
                from app.packages.p1_seguridad.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol

                email_clean = data.email.strip().lower()
                existing_user = db.execute(
                    select(User).where(func.lower(User.email) == email_clean)
                ).scalar_one_or_none()

                if not existing_user:
                    user = User(
                        nombrecompleto=data.nombre.strip() + " Admin",
                        email=email_clean,
                        contrasenahash=hash_password(data.password.strip()),
                        activo=True
                    )
                    db.add(user)
                    db.flush()
                else:
                    user = existing_user

                # Vincular usuario al tenant
                link = UsuarioTenant(idusuario=user.idusuario, idtenant=tenant.idtenant)
                db.add(link)
                db.flush()

                # Asignar rol AdministradorEmpresa
                rol_admin = db.execute(
                    select(Role).where(Role.nombrerol == "AdministradorEmpresa")
                ).scalars().first()
                if rol_admin:
                    db.add(UsuarioTenantRol(idusuariotenant=link.idusuariotenant, idrol=rol_admin.idrol))

                db.commit()
            except Exception as ex:
                db.rollback()

        return TenantResponse.model_validate(tenant)

    @staticmethod
    def get_tenant(db: Session, idtenant: int) -> TenantResponse:
        stmt = select(Tenant).where(Tenant.idtenant == idtenant)
        tenant = db.execute(stmt).scalar_one_or_none()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa con ID {idtenant} no encontrada."
            )
        return TenantResponse.model_validate(tenant)

    @staticmethod
    def update_tenant(db: Session, idtenant: int, data: TenantUpdate) -> TenantResponse:
        stmt = select(Tenant).where(Tenant.idtenant == idtenant)
        tenant = db.execute(stmt).scalar_one_or_none()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa con ID {idtenant} no encontrada."
            )

        if data.nit and data.nit.strip() != tenant.nit:
            stmt_nit = select(Tenant).where(
                Tenant.nit == data.nit.strip(),
                Tenant.idtenant != idtenant
            )
            if db.execute(stmt_nit).scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otra empresa registrada con el NIT '{data.nit}'."
                )
            tenant.nit = data.nit.strip()

        if data.nombre is not None:
            tenant.nombre = data.nombre.strip()
        if data.razonsocial is not None:
            tenant.razonsocial = data.razonsocial.strip()
        if data.email is not None:
            tenant.email = data.email.strip().lower()
        if data.telefono is not None:
            tenant.telefono = data.telefono.strip() if data.telefono else None
        if data.activo is not None:
            tenant.activo = data.activo

        db.commit()
        db.refresh(tenant)
        return TenantResponse.model_validate(tenant)

    @staticmethod
    def delete_tenant(db: Session, idtenant: int) -> TenantResponse:
        stmt = select(Tenant).where(Tenant.idtenant == idtenant)
        tenant = db.execute(stmt).scalar_one_or_none()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empresa con ID {idtenant} no encontrada."
            )

        tenant.activo = False
        db.commit()
        db.refresh(tenant)
        return TenantResponse.model_validate(tenant)


# Endpoints (Rutas HTTP)
@router.get("", response_model=TenantListResponse)
def get_tenants(
    search: Optional[str] = Query(None, description="Buscador por nombre, razón social o NIT"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    only_active: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar empresas registradas (CU-001).
    - SuperAdministrador: listado completo con paginación y búsqueda.
    - Demás roles: únicamente su empresa activa.
    """
    from app.controllers.shared import _es_superadmin, resolve_tenant_id

    if _es_superadmin(db, current_user):
        return TenantController.list_tenants(db, search, skip, limit, only_active)

    active_id = resolve_tenant_id(db, current_user)
    stmt = select(Tenant).where(Tenant.idtenant == active_id)
    tenant = db.execute(stmt).scalar_one_or_none()
    if not tenant or (only_active and not tenant.activo):
        return TenantListResponse(total=0, items=[])

    if search and search.strip():
        term = search.strip().lower()
        matches = (
            term in (tenant.nombre or "").lower()
            or term in (tenant.razonsocial or "").lower()
            or term in (tenant.nit or "").lower()
            or term in (tenant.email or "").lower()
        )
        if not matches:
            return TenantListResponse(total=0, items=[])

    return TenantListResponse(
        total=1,
        items=[TenantResponse.model_validate(tenant)]
    )


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_require_superadmin_role)]
)
def create_tenant(
    data: TenantCreate,
    db: Session = Depends(get_db),
):
    """Registrar una nueva empresa (CU-001) - Solo SuperAdministrador."""
    return TenantController.create_tenant(db, data)


@router.get("/{idtenant}", response_model=TenantResponse)
def get_tenant_by_id(
    idtenant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener los detalles de una empresa específica por su ID (CU-001).
    - SuperAdministrador: puede consultar cualquier empresa.
    - Demás roles: únicamente su empresa activa.
    """
    from app.controllers.shared import _es_superadmin, resolve_tenant_id

    if not _es_superadmin(db, current_user):
        active_id = resolve_tenant_id(db, current_user)
        if idtenant != active_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para consultar información de otra empresa."
            )
    return TenantController.get_tenant(db, idtenant)


@router.put(
    "/{idtenant}",
    response_model=TenantResponse,
    dependencies=[Depends(_require_superadmin_role)]
)
def update_tenant(
    idtenant: int,
    data: TenantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar datos de una empresa existente (CU-001) - Solo SuperAdministrador."""
    return TenantController.update_tenant(db, idtenant, data)


@router.delete(
    "/{idtenant}",
    response_model=TenantResponse,
    dependencies=[Depends(_require_superadmin_role)]
)
def delete_tenant(
    idtenant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Desactivación lógica de una empresa (CU-001) - Solo SuperAdministrador."""
    return TenantController.delete_tenant(db, idtenant)
