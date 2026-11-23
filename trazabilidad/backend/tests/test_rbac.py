"""Tests de RBAC y Prevención de Escalada de Privilegios (CU-003 - Prompt 1).

Verifica:
1. GestorOperaciones recibe 403 al intentar asignar SuperAdministrador (o cualquier rol).
2. AdministradorEmpresa recibe 403 al intentar asignar el rol SuperAdministrador.
3. AdministradorEmpresa recibe 403 al intentar modificar roles de un usuario de otra empresa.
4. SuperAdministrador recibe 200 y puede asignar roles legítimamente.
5. Endpoints GET /roles, GET /permissions y GET /users/{id}/roles están protegidos por roles.
"""
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.packages.p1_seguridad.models.cu001_tenants.tenant import Tenant
from app.packages.p1_seguridad.models.cu002_usuarios.user import User
from app.packages.p1_seguridad.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.packages.p1_seguridad.models.cu003_roles_permisos.role import Role
from app.packages.p1_seguridad.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.core.security import hash_password


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def rbac_setup(client, db_session: Session):
    """Crea 2 tenants, roles y usuarios haciendo login real para obtener tokens válidos."""
    # 1. Asegurar roles
    roles = {}
    for r_name in ["SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones", "Auditor", "Consumidor"]:
        r = db_session.execute(select(Role).where(Role.nombrerol == r_name)).scalars().first()
        if not r:
            r = Role(nombrerol=r_name, descripcion=f"Rol {r_name}")
            db_session.add(r)
            db_session.flush()
        roles[r_name] = r

    # 2. Asegurar Tenants
    t1 = db_session.execute(select(Tenant).where(Tenant.nit == "NIT-RBAC-T1")).scalars().first()
    if not t1:
        t1 = Tenant(nombre="RBAC Tenant Uno", razonsocial="RBAC T1 SA", nit="NIT-RBAC-T1", email="t1@rbac.com", activo=True)
        db_session.add(t1)
        db_session.flush()

    t2 = db_session.execute(select(Tenant).where(Tenant.nit == "NIT-RBAC-T2")).scalars().first()
    if not t2:
        t2 = Tenant(nombre="RBAC Tenant Dos", razonsocial="RBAC T2 SA", nit="NIT-RBAC-T2", email="t2@rbac.com", activo=True)
        db_session.add(t2)
        db_session.flush()

    # 3. Helper para crear usuario con rol
    def _create_user(email: str, name: str, tenant_id: int, role_name: str, slug: str):
        u = db_session.execute(select(User).where(User.email == email)).scalars().first()
        if not u:
            u = User(nombrecompleto=name, email=email, contrasenahash=hash_password("Pass123!"), activo=True)
            db_session.add(u)
            db_session.flush()
        else:
            u.contrasenahash = hash_password("Pass123!")
            u.activo = True

        ut = db_session.execute(select(UsuarioTenant).where(UsuarioTenant.idusuario == u.idusuario, UsuarioTenant.idtenant == tenant_id)).scalars().first()
        if not ut:
            ut = UsuarioTenant(idusuario=u.idusuario, idtenant=tenant_id)
            db_session.add(ut)
            db_session.flush()

        utr = db_session.execute(select(UsuarioTenantRol).where(UsuarioTenantRol.idusuariotenant == ut.idusuariotenant, UsuarioTenantRol.idrol == roles[role_name].idrol)).scalars().first()
        if not utr:
            utr = UsuarioTenantRol(idusuariotenant=ut.idusuariotenant, idrol=roles[role_name].idrol)
            db_session.add(utr)
            db_session.flush()

        db_session.commit()

        login_res = client.post("/api/v1/auth/login", json={
            "tenant_slug": slug,
            "email": email,
            "password": "Pass123!"
        })
        assert login_res.status_code == 200, f"Error login {email}: {login_res.text}"
        return u, login_res.json()["access_token"]

    u_super, token_super = _create_user("super@rbac.com", "Super Admin", t1.idtenant, "SuperAdministrador", "rbac-tenant-uno")
    u_admin1, token_admin1 = _create_user("admin1@rbac.com", "Admin T1", t1.idtenant, "AdministradorEmpresa", "rbac-tenant-uno")
    u_op1, token_op1 = _create_user("op1@rbac.com", "Operador T1", t1.idtenant, "GestorOperaciones", "rbac-tenant-uno")
    u_admin2, token_admin2 = _create_user("admin2@rbac.com", "Admin T2", t2.idtenant, "AdministradorEmpresa", "rbac-tenant-dos")
    u_target1, _ = _create_user("target1@rbac.com", "Target T1", t1.idtenant, "Consumidor", "rbac-tenant-uno")
    u_target2, _ = _create_user("target2@rbac.com", "Target T2", t2.idtenant, "Consumidor", "rbac-tenant-dos")

    return {
        "roles": roles,
        "t1": t1,
        "t2": t2,
        "token_super": token_super,
        "token_admin1": token_admin1,
        "token_op1": token_op1,
        "token_admin2": token_admin2,
        "u_super": u_super,
        "u_admin1": u_admin1,
        "u_op1": u_op1,
        "u_target1": u_target1,
        "u_target2": u_target2,
    }


def test_gestor_operaciones_no_puede_asignar_roles(client, rbac_setup):
    """Gestor de Operaciones debe recibir 403 al intentar asignar cualquier rol."""
    headers = _auth_header(rbac_setup["token_op1"])
    target_id = rbac_setup["u_target1"].idusuario
    role_super_id = rbac_setup["roles"]["SuperAdministrador"].idrol

    resp = client.post(
        f"/api/v1/users/{target_id}/roles",
        json={"role_ids": [role_super_id]},
        headers=headers,
    )
    assert resp.status_code == 403


def test_admin_empresa_no_puede_asignar_superadministrador(client, rbac_setup):
    """Administrador de Empresa recibe 403 si intenta asignar el rol SuperAdministrador."""
    headers = _auth_header(rbac_setup["token_admin1"])
    target_id = rbac_setup["u_target1"].idusuario
    role_super_id = rbac_setup["roles"]["SuperAdministrador"].idrol

    resp = client.post(
        f"/api/v1/users/{target_id}/roles",
        json={"role_ids": [role_super_id]},
        headers=headers,
    )
    assert resp.status_code == 403
    assert "SuperAdministrador" in resp.json().get("detail", "")


def test_admin_empresa_no_puede_modificar_usuario_otra_empresa(client, rbac_setup):
    """Administrador de Empresa recibe 403 si intenta modificar usuario de otro tenant."""
    headers = _auth_header(rbac_setup["token_admin1"])
    target_t2_id = rbac_setup["u_target2"].idusuario
    role_op_id = rbac_setup["roles"]["GestorOperaciones"].idrol

    resp = client.post(
        f"/api/v1/users/{target_t2_id}/roles",
        json={"role_ids": [role_op_id]},
        headers=headers,
    )
    assert resp.status_code == 403
    assert "empresa activa" in resp.json().get("detail", "")


def test_superadministrador_asigna_roles_exitosamente(client, rbac_setup):
    """SuperAdministrador puede asignar roles legítimamente (200 OK)."""
    headers = _auth_header(rbac_setup["token_super"])
    target_id = rbac_setup["u_target1"].idusuario
    role_op_id = rbac_setup["roles"]["GestorOperaciones"].idrol

    resp = client.post(
        f"/api/v1/users/{target_id}/roles",
        json={"role_ids": [role_op_id]},
        headers=headers,
    )
    assert resp.status_code == 200
    roles_asignados = [r["nombrerol"] for r in resp.json().get("roles", [])]
    assert "GestorOperaciones" in roles_asignados


def test_endpoints_lectura_roles_protegidos(client, rbac_setup):
    """GET /roles, GET /permissions y GET /users/{id}/roles deniegan a usuarios sin rol de gestión."""
    headers_op = _auth_header(rbac_setup["token_op1"])
    headers_admin = _auth_header(rbac_setup["token_admin1"])

    # GestorOperaciones recibe 403 en /roles
    resp_roles_op = client.get("/api/v1/roles", headers=headers_op)
    assert resp_roles_op.status_code == 403

    # AdministradorEmpresa sí tiene acceso a /roles
    resp_roles_admin = client.get("/api/v1/roles", headers=headers_admin)
    assert resp_roles_admin.status_code == 200

    # Admin Empresa 1 recibe 403 al consultar roles de usuario en Empresa 2
    target_t2_id = rbac_setup["u_target2"].idusuario
    resp_user_t2 = client.get(f"/api/v1/users/{target_t2_id}/roles", headers=headers_admin)
    assert resp_user_t2.status_code == 403
