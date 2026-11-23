from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    validate_password_strength,
    create_access_token,
    decode_access_token,
    generate_secure_raw_token,
    hash_token
)
from app.db.session import get_db
from app.packages.p1_seguridad.models.cu001_tenants.tenant import Tenant
from app.packages.p1_seguridad.models.cu002_usuarios.user import User
from app.packages.p1_seguridad.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.packages.p1_seguridad.models.cu003_roles_permisos.role import Role
from app.packages.p1_seguridad.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.packages.p1_seguridad.models.cu004_autenticacion.password_reset_token import PasswordResetToken
from app.packages.p1_seguridad.models.cu004_autenticacion.refresh_token import RefreshToken
from app.core.mail_service import MailService
from app.packages.p1_seguridad.views.cu004_autenticacion.auth_views import (
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse
)
from app.packages.p1_seguridad.views.cu002_usuarios.user_views import UserResponse
from app.packages.p1_seguridad.views.cu001_tenants.tenant_views import TenantResponse
import threading
from dataclasses import dataclass
from typing import Dict, Tuple

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

@dataclass
class LoginAttemptState:
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None


class LoginRateLimiter:
    """Controlador en memoria de intentos de login fallidos y bloqueo temporal por IP + Email.
    
    Elección técnica: Almacenamiento en memoria con threading.Lock para latencia mínima
    y cero dependencias de I/O o migraciones adicionales de base de datos.
    """
    def __init__(self, max_attempts: int = MAX_LOGIN_ATTEMPTS, lockout_minutes: int = LOCKOUT_MINUTES):
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes
        self._lock = threading.Lock()
        self._attempts: Dict[Tuple[str, str], LoginAttemptState] = {}

    def _key(self, email: str, ip: str) -> Tuple[str, str]:
        return (email.strip().lower(), ip.strip())

    def check_rate_limit(self, email: str, ip: str) -> Tuple[bool, Optional[int]]:
        """Verifica si la tupla (email, ip) se encuentra temporalmente bloqueada."""
        key = self._key(email, ip)
        now = datetime.now(timezone.utc)
        with self._lock:
            state = self._attempts.get(key)
            if not state:
                return False, None
            if state.locked_until:
                if now < state.locked_until:
                    remaining = int((state.locked_until - now).total_seconds())
                    return True, max(1, remaining)
                else:
                    # El bloqueo expiró, limpiar estado
                    del self._attempts[key]
                    return False, None
            return False, None

    def record_failure(self, email: str, ip: str) -> Tuple[bool, int]:
        """Registra un intento fallido. Bloquea si alcanza el límite de intentos."""
        key = self._key(email, ip)
        now = datetime.now(timezone.utc)
        with self._lock:
            state = self._attempts.get(key)
            if not state:
                state = LoginAttemptState(failed_attempts=1)
                self._attempts[key] = state
            else:
                if state.locked_until and now >= state.locked_until:
                    state.failed_attempts = 1
                    state.locked_until = None
                else:
                    state.failed_attempts += 1

            if state.failed_attempts >= self.max_attempts:
                state.locked_until = now + timedelta(minutes=self.lockout_minutes)
                return True, state.failed_attempts
            return False, state.failed_attempts

    def record_success(self, email: str, ip: str) -> None:
        """Limpia los intentos fallidos tras un inicio de sesión exitoso."""
        key = self._key(email, ip)
        with self._lock:
            self._attempts.pop(key, None)

    def reset(self, email: Optional[str] = None, ip: Optional[str] = None) -> None:
        """Reinicia los contadores (útil para pruebas y tareas administrativas)."""
        with self._lock:
            if email is not None and ip is not None:
                self._attempts.pop(self._key(email, ip), None)
            else:
                self._attempts.clear()


login_rate_limiter = LoginRateLimiter(max_attempts=MAX_LOGIN_ATTEMPTS, lockout_minutes=LOCKOUT_MINUTES)


def _registrar_bloqueo_bitacora(db: Session, email: str, ip: str) -> None:
    """Registrar evento de bloqueo por fuerza bruta en la Bitácora (CU-005)."""
    try:
        from app.packages.p1_seguridad.models.cu005_bitacora.bitacora import Bitacora
        from app.packages.p1_seguridad.models.cu002_usuarios.user import User
        from app.packages.p1_seguridad.models.cu002_usuarios.usuario_tenant import UsuarioTenant

        email_clean = email.strip().lower()
        stmt_u = select(User).where(func.lower(User.email) == email_clean)
        user = db.execute(stmt_u).scalar_one_or_none()

        idut = None
        idusuario = None
        if user:
            idusuario = user.idusuario
            stmt_ut = select(UsuarioTenant.idusuariotenant).where(UsuarioTenant.idusuario == user.idusuario)
            idut = db.execute(stmt_ut).scalars().first()

        if not idut:
            stmt_first = select(UsuarioTenant.idusuariotenant).limit(1)
            idut = db.execute(stmt_first).scalar()

        if idut:
            # Hora oficial de Bolivia (BOT = UTC-4)
            hora_bolivia = datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)
            bitacora_entry = Bitacora(
                idusuariotenant=idut,
                accion="BLOQUEO_LOGIN",
                entidad="Autenticacion",
                identidad=idusuario,
                ip=ip,
                fechahora=hora_bolivia
            )
            db.add(bitacora_entry)
            db.commit()
    except Exception as e:
        db.rollback()
        import logging
        logging.getLogger(__name__).warning(f"[Bitacora Bloqueo Error]: {e}")


security_scheme = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Autenticación Multi-Tenant"])


class AuthController:
    @staticmethod
    def _find_tenant(db: Session, tenant_slug: str) -> Optional[Tenant]:
        clean_slug = tenant_slug.strip().lower()
        
        # 0. Coincidencia por alias demo predeterminado o plataforma
        if clean_slug in ("system", "platform", "plataforma", "0", "saas"):
            stmt_plat = select(Tenant).where(Tenant.nit == "000000000")
            plat = db.execute(stmt_plat).scalar_one_or_none()
            if plat:
                return plat

        if clean_slug in ("empresa-demo", "demo", "default"):
            stmt_first = select(Tenant).where(Tenant.activo != False).order_by(Tenant.idtenant)
            first_tenant = db.execute(stmt_first).scalars().first()
            if first_tenant:
                return first_tenant

        # 1. Coincidencia directa por ID si es numérico
        if clean_slug.isdigit():
            stmt = select(Tenant).where(Tenant.idtenant == int(clean_slug))
            tenant = db.execute(stmt).scalar_one_or_none()
            if tenant:
                return tenant

        # 2. Coincidencia por NIT
        stmt = select(Tenant).where(func.lower(Tenant.nit) == clean_slug)
        tenant = db.execute(stmt).scalar_one_or_none()
        if tenant:
            return tenant

        # 3. Coincidencia por nombre exacto o formato slug
        stmt_all = select(Tenant).where(Tenant.activo != False)
        all_tenants = db.execute(stmt_all).scalars().all()
        for t in all_tenants:
            # normalización a slug: "Importadora Bolivia S.A." -> "importadora-bolivia-s.a."
            t_name_slug = t.nombre.strip().lower().replace(" ", "-")
            t_name_simple = t.nombre.strip().lower()
            if clean_slug in (t_name_slug, t_name_simple, t.nombre.lower()):
                return t
        
        # Retornar None si ninguna empresa coincide
        return None

    @staticmethod
    def authenticate_user(
        db: Session, tenant_slug: str, email: str, password: str
    ) -> Tuple[str, str, User, Tenant]:
        """Autenticar usuario por empresa, correo y contraseña."""
        tenant = AuthController._find_tenant(db, tenant_slug)
        if not tenant or tenant.activo == False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empresa o credenciales inválidas."
            )

        email_clean = email.strip().lower()
        stmt_user = select(User).where(
            func.lower(User.email) == email_clean,
            User.activo != False
        )
        user = db.execute(stmt_user).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empresa o credenciales inválidas."
            )

        # Si el usuario es el SuperAdministrador global de plataforma (o inicia sesión vía slug de plataforma)
        clean_slug = tenant_slug.strip().lower()
        is_platform_superadmin = (user.email == "superadmin@trazabilidad.com") or (clean_slug in ("system", "platform", "plataforma", "0", "saas"))

        if is_platform_superadmin:
            stmt_plat = select(Tenant).where(Tenant.nit == "000000000")
            plat = db.execute(stmt_plat).scalar_one_or_none()
            if plat:
                tenant = plat
            stmt_link = select(UsuarioTenant).where(
                UsuarioTenant.idusuario == user.idusuario,
                UsuarioTenant.idtenant == tenant.idtenant
            )
            link = db.execute(stmt_link).scalar_one_or_none()
            if not link:
                link = UsuarioTenant(idusuario=user.idusuario, idtenant=tenant.idtenant)
                db.add(link)
                db.commit()
        else:
            # Verificar vinculación con la empresa en la tabla usuariotenant
            stmt_link = select(UsuarioTenant).where(
                UsuarioTenant.idusuario == user.idusuario,
                UsuarioTenant.idtenant == tenant.idtenant
            )
            link = db.execute(stmt_link).scalar_one_or_none()
            if not link:
                # Si no existe el vínculo, crearlo para garantizar el acceso multiempresa
                link = UsuarioTenant(idusuario=user.idusuario, idtenant=tenant.idtenant)
                db.add(link)
                db.commit()

        if not verify_password(password, user.contrasenahash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empresa o credenciales inválidas."
            )

        access_token_payload = {
            "sub": str(user.idusuario),
            "tenant_id": str(tenant.idtenant),
            "email": user.email
        }
        access_token = create_access_token(access_token_payload)

        raw_refresh_token = generate_secure_raw_token()
        refresh_token_hash = hash_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        db_refresh_token = RefreshToken(
            idtenant=tenant.idtenant,
            idusuario=user.idusuario,
            tokenhash=refresh_token_hash,
            expiraen=expires_at,
            revocado=False
        )
        db.add(db_refresh_token)
        db.commit()

        user.tenant = TenantResponse.model_validate(tenant)
        stmt_roles = (
            select(Role.nombrerol)
            .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
            .where(UsuarioTenantRol.idusuariotenant == link.idusuariotenant)
        )
        user_roles = list(db.execute(stmt_roles).scalars().all())

        stmt_super = (
            select(Role.nombrerol)
            .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
            .join(UsuarioTenant, UsuarioTenant.idusuariotenant == UsuarioTenantRol.idusuariotenant)
            .where(
                UsuarioTenant.idusuario == user.idusuario,
                Role.nombrerol == "SuperAdministrador"
            )
        )
        if db.execute(stmt_super).scalars().first():
            if "SuperAdministrador" not in user_roles:
                user_roles.append("SuperAdministrador")

        user.roles = user_roles
        return access_token, raw_refresh_token, user, tenant

    @staticmethod
    def refresh_access_token(db: Session, raw_refresh_token: str) -> Tuple[str, User]:
        """Refrescar token de acceso JWT usando un token de refresco válido."""
        token_hash_val = hash_token(raw_refresh_token)
        stmt = select(RefreshToken).where(
            RefreshToken.tokenhash == token_hash_val,
            RefreshToken.revocado == False
        )
        refresh_token_obj = db.execute(stmt).scalar_one_or_none()

        if not refresh_token_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido o revocado."
            )

        now = datetime.now(timezone.utc)
        if refresh_token_obj.expiraen < now:
            refresh_token_obj.revocado = True
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco expirado."
            )

        stmt_user = select(User).where(
            User.idusuario == refresh_token_obj.idusuario,
            User.activo != False
        )
        user = db.execute(stmt_user).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o empresa inactivos."
            )

        tenant = None
        if refresh_token_obj.idtenant:
            stmt_t = select(Tenant).where(Tenant.idtenant == refresh_token_obj.idtenant)
            tenant = db.execute(stmt_t).scalar_one_or_none()
        if tenant:
            user.tenant = TenantResponse.model_validate(tenant)

        access_token_payload = {
            "sub": str(user.idusuario),
            "tenant_id": str(tenant.idtenant if tenant else 1),
            "email": user.email
        }
        access_token = create_access_token(access_token_payload)
        return access_token, user

    @staticmethod
    def logout(db: Session, raw_refresh_token: Optional[str]) -> None:
        """Revocar token de refresco al cerrar sesión."""
        if not raw_refresh_token:
            return
        token_hash_val = hash_token(raw_refresh_token)
        stmt = select(RefreshToken).where(RefreshToken.tokenhash == token_hash_val)
        refresh_token_obj = db.execute(stmt).scalar_one_or_none()
        if refresh_token_obj:
            refresh_token_obj.revocado = True
            db.commit()

    @staticmethod
    async def request_password_reset(
        db: Session,
        tenant_slug: str,
        email: str,
        background_tasks: Optional[BackgroundTasks] = None,
        frontend_origin: Optional[str] = None
    ) -> str:
        """Generar token de recuperación y enviar correo de forma asíncrona."""
        generic_message = (
            "Si la cuenta existe, recibirás un correo con las instrucciones "
            "para restablecer tu contraseña."
        )

        email_clean = email.strip().lower()

        tenant = AuthController._find_tenant(db, tenant_slug)
        if not tenant:
            return generic_message

        stmt_user = select(User).where(
            func.lower(User.email) == email_clean,
            User.activo != False
        )
        user = db.execute(stmt_user).scalar_one_or_none()
        if not user:
            return generic_message

        raw_token = generate_secure_raw_token()
        token_hash_val = hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
        )

        db_token = PasswordResetToken(
            idtenant=tenant.idtenant,
            idusuario=user.idusuario,
            tokenhash=token_hash_val,
            expiraen=expires_at
        )
        db.add(db_token)
        db.commit()

        if background_tasks:
            background_tasks.add_task(
                MailService.send_reset_password_email,
                email=user.email,
                first_name=user.nombrecompleto,
                tenant_name=tenant.nombre,
                raw_token=raw_token,
                frontend_origin=frontend_origin
            )
        else:
            await MailService.send_reset_password_email(
                email=user.email,
                first_name=user.nombrecompleto,
                tenant_name=tenant.nombre,
                raw_token=raw_token,
                frontend_origin=frontend_origin
            )

        return generic_message

    @staticmethod
    def reset_password(
        db: Session, token: str, new_password: str, confirm_password: str
    ) -> str:
        """Restablecer contraseña usando el token de recuperación."""
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las contraseñas no coinciden."
            )

        is_valid, msg = validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

        token_hash_val = hash_token(token)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.tokenhash == token_hash_val,
            PasswordResetToken.usadoen.is_(None)
        )
        reset_token = db.execute(stmt).scalar_one_or_none()
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de recuperación es inválido o ya ha sido utilizado."
            )

        now = datetime.now(timezone.utc)
        if reset_token.expiraen < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El token de recuperación ha expirado."
            )

        stmt_user = select(User).where(User.idusuario == reset_token.idusuario)
        user = db.execute(stmt_user).scalar_one_or_none()
        if not user or user.activo == False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no encontrado o inactivo."
            )

        user.contrasenahash = hash_password(new_password)
        reset_token.usadoen = now

        stmt_refreshes = select(RefreshToken).where(
            RefreshToken.idusuario == user.idusuario,
            RefreshToken.revocado == False
        )
        refresh_tokens = db.execute(stmt_refreshes).scalars().all()
        for rt in refresh_tokens:
            rt.revocado = True

        db.commit()
        return "Contraseña restablecida correctamente."

    @staticmethod
    def get_current_user_from_token(db: Session, token: str) -> User:
        """Validar token de acceso JWT y retornar el usuario autenticado activo."""
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de acceso inválido o expirado.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        user_id_str: Optional[str] = payload.get("sub")
        tenant_id_str: Optional[str] = payload.get("tenant_id")
        if not user_id_str or not tenant_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Payload de token incompleto.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        try:
            user_id = int(user_id_str)
            tenant_id = int(tenant_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identificadores inválidos en token.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        stmt = select(User).where(
            User.idusuario == user_id,
            User.activo != False
        )
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o empresa inactivos o no encontrados.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        stmt_t = select(Tenant).where(Tenant.idtenant == tenant_id)
        tenant = db.execute(stmt_t).scalar_one_or_none()
        if tenant:
            user.tenant = TenantResponse.model_validate(tenant)

        stmt_roles = (
            select(Role.nombrerol)
            .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
            .join(UsuarioTenant, UsuarioTenant.idusuariotenant == UsuarioTenantRol.idusuariotenant)
            .where(
                UsuarioTenant.idusuario == user.idusuario,
                UsuarioTenant.idtenant == tenant_id
            )
        )
        user_roles = list(db.execute(stmt_roles).scalars().all())

        stmt_super = (
            select(Role.nombrerol)
            .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
            .join(UsuarioTenant, UsuarioTenant.idusuariotenant == UsuarioTenantRol.idusuariotenant)
            .where(
                UsuarioTenant.idusuario == user.idusuario,
                Role.nombrerol == "SuperAdministrador"
            )
        )
        if db.execute(stmt_super).scalars().first():
            if "SuperAdministrador" not in user_roles:
                user_roles.append("SuperAdministrador")

        user.roles = user_roles

        return user

    @staticmethod
    def switch_tenant(db: Session, target_tenant_id: int, current_user: User) -> Tuple[str, Tenant]:
        """Cambiar el contexto de empresa activa para el usuario."""
        stmt_t = select(Tenant).where(Tenant.idtenant == target_tenant_id, Tenant.activo != False)
        tenant = db.execute(stmt_t).scalar_one_or_none()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La empresa con ID {target_tenant_id} no existe o está inactiva."
            )

        # Validar pertenencia: el usuario debe estar vinculado a la empresa destino
        # (el SuperAdministrador puede cambiar a cualquier empresa).
        stmt_link = select(UsuarioTenant).where(
            UsuarioTenant.idusuario == current_user.idusuario,
            UsuarioTenant.idtenant == tenant.idtenant
        )
        link = db.execute(stmt_link).scalar_one_or_none()
        user_roles = getattr(current_user, "roles", []) or []
        if not link and "SuperAdministrador" not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para operar sobre esa empresa."
            )

        # Crear nuevo token de acceso con el idtenant solicitado
        access_token_payload = {
            "sub": str(current_user.idusuario),
            "tenant_id": str(tenant.idtenant),
            "email": current_user.email
        }
        access_token = create_access_token(access_token_payload)

        # Vincular SuperAdministrador a la empresa si no estuviera vinculado,
        # asignando roles operativos dentro del nuevo vinculo para permitir gestion.
        if not link:
            link = UsuarioTenant(idusuario=current_user.idusuario, idtenant=tenant.idtenant)
            db.add(link)
            db.flush()
            for r_name in ["SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones"]:
                rol_obj = db.execute(
                    select(Role).where(Role.nombrerol == r_name)
                ).scalars().first()
                if rol_obj:
                    db.add(UsuarioTenantRol(idusuariotenant=link.idusuariotenant, idrol=rol_obj.idrol))
            db.commit()

        current_user.tenant = TenantResponse.model_validate(tenant)
        return access_token, tenant


# Dependencias
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependencia para inyectar el usuario autenticado actual."""
    return AuthController.get_current_user_from_token(db, credentials.credentials)


# Endpoints del Controlador (Rutas HTTP)
@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    """Autenticar usuario y retornar token de acceso JWT y cookie de refresco HttpOnly."""
    client_ip = (
        request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "127.0.0.1")
    )
    email_clean = credentials.email.strip().lower()

    # 1. Verificar si la IP + Email se encuentra temporalmente bloqueada por intentos fallidos
    is_locked, remaining_seconds = login_rate_limiter.check_rate_limit(email_clean, client_ip)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Cuenta temporalmente bloqueada por 15 minutos."
        )

    try:
        access_token, raw_refresh_token, user, tenant = AuthController.authenticate_user(
            db, credentials.tenant_slug, credentials.email, credentials.password
        )
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            is_now_locked, attempts = login_rate_limiter.record_failure(email_clean, client_ip)
            if is_now_locked:
                _registrar_bloqueo_bitacora(db, email_clean, client_ip)
        raise exc

    # 2. Si la autenticación fue exitosa, reiniciar contador de intentos fallidos
    login_rate_limiter.record_success(email_clean, client_ip)

    # 3. Registrar evento real en Bitácora con Hora de Bolivia (BOT, UTC-4)
    try:
        from app.packages.p1_seguridad.models.cu005_bitacora.bitacora import Bitacora
        ut_stmt = select(UsuarioTenant.idusuariotenant).where(
            UsuarioTenant.idusuario == user.idusuario,
            UsuarioTenant.idtenant == tenant.idtenant
        )
        idut = db.execute(ut_stmt).scalar()
        if not idut:
            ut_stmt2 = select(UsuarioTenant.idusuariotenant).where(
                UsuarioTenant.idusuario == user.idusuario
            )
            idut = db.execute(ut_stmt2).scalar()

        if idut:
            hora_bolivia = datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)
            db.add(Bitacora(
                idusuariotenant=idut,
                accion="LOGIN",
                entidad="Autenticacion",
                identidad=user.idusuario,
                ip=client_ip,
                fechahora=hora_bolivia
            ))
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Bitacora Login Audit Error]: {e}")

    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    )

    user_resp = UserResponse(
        idusuario=user.idusuario,
        nombrecompleto=user.nombrecompleto,
        email=user.email,
        activo=user.activo,
        fecharegistro=user.fecharegistro,
        tenant=TenantResponse.model_validate(tenant),
        roles=getattr(user, "roles", [])
    )

    return TokenResponse(access_token=access_token, user=user_resp)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Refrescar token de acceso JWT usando la cookie HttpOnly."""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cookie de refresco no proporcionada."
        )

    new_access_token, user = AuthController.refresh_access_token(db, refresh_token)
    user_resp = UserResponse.model_validate(user)
    return TokenResponse(access_token=new_access_token, user=user_resp)


@router.post("/logout", response_model=MessageResponse)
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Revocar token de refresco y limpiar cookie HttpOnly."""
    AuthController.logout(db, refresh_token)
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
    return MessageResponse(message="Sesión cerrada correctamente.")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Retornar datos del usuario autenticado actual."""
    return UserResponse(
        idusuario=current_user.idusuario,
        nombrecompleto=current_user.nombrecompleto,
        email=current_user.email,
        activo=current_user.activo,
        fecharegistro=current_user.fecharegistro,
        tenant=getattr(current_user, "tenant", None),
        roles=getattr(current_user, "roles", [])
    )


@router.post("/switch-tenant/{idtenant}", response_model=TokenResponse)
def switch_tenant(
    idtenant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cambiar contexto de empresa activa para el usuario (CU-001)."""
    access_token, tenant = AuthController.switch_tenant(db, idtenant, current_user)
    stmt_roles = (
        select(Role.nombrerol)
        .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
        .join(UsuarioTenant, UsuarioTenant.idusuariotenant == UsuarioTenantRol.idusuariotenant)
        .where(
            UsuarioTenant.idusuario == current_user.idusuario,
            UsuarioTenant.idtenant == idtenant
        )
    )
    user_roles = list(db.execute(stmt_roles).scalars().all())

    stmt_super = (
        select(Role.nombrerol)
        .join(UsuarioTenantRol, UsuarioTenantRol.idrol == Role.idrol)
        .join(UsuarioTenant, UsuarioTenant.idusuariotenant == UsuarioTenantRol.idusuariotenant)
        .where(
            UsuarioTenant.idusuario == current_user.idusuario,
            Role.nombrerol == "SuperAdministrador"
        )
    )
    if db.execute(stmt_super).scalars().first():
        if "SuperAdministrador" not in user_roles:
            user_roles.append("SuperAdministrador")

    user_resp = UserResponse(
        idusuario=current_user.idusuario,
        nombrecompleto=current_user.nombrecompleto,
        email=current_user.email,
        activo=current_user.activo,
        fecharegistro=current_user.fecharegistro,
        tenant=TenantResponse.model_validate(tenant),
        roles=user_roles
    )
    return TokenResponse(access_token=access_token, user=user_resp)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    forgot_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """Solicitar enlace de recuperación de contraseña por correo."""
    origin = request.headers.get("origin") or request.headers.get("referer")
    msg = await AuthController.request_password_reset(
        db,
        forgot_data.tenant_slug,
        forgot_data.email,
        background_tasks=background_tasks,
        frontend_origin=origin
    )
    return MessageResponse(message=msg)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Restablecer contraseña de usuario usando un token válido."""
    msg = AuthController.reset_password(
        db, reset_data.token, reset_data.new_password, reset_data.confirm_password
    )
    return MessageResponse(message=msg)
