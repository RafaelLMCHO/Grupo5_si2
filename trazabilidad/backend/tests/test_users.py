import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.core.security import hash_password


def _crear_usuario_con_rol(client, db_session: Session, email: str, rol_nombre: str, tenant: Tenant, password: str = "MiClave@123"):
    rol = db_session.execute(select(Role).where(Role.nombrerol == rol_nombre)).scalars().first()
    if not rol:
        rol = Role(nombrerol=rol_nombre, descripcion=f"Rol {rol_nombre}")
        db_session.add(rol)
        db_session.flush()

    user = db_session.execute(select(User).where(User.email == email)).scalars().first()
    if not user:
        user = User(
            nombrecompleto=f"Usuario {rol_nombre}",
            email=email,
            contrasenahash=hash_password(password),
            activo=True
        )
        db_session.add(user)
        db_session.flush()

    ut = db_session.execute(
        select(UsuarioTenant).where(
            UsuarioTenant.idusuario == user.idusuario,
            UsuarioTenant.idtenant == tenant.idtenant
        )
    ).scalars().first()
    if not ut:
        ut = UsuarioTenant(idusuario=user.idusuario, idtenant=tenant.idtenant)
        db_session.add(ut)
        db_session.flush()

    utr = db_session.execute(
        select(UsuarioTenantRol).where(
            UsuarioTenantRol.idusuariotenant == ut.idusuariotenant,
            UsuarioTenantRol.idrol == rol.idrol
        )
    ).scalars().first()
    if not utr:
        utr = UsuarioTenantRol(idusuariotenant=ut.idusuariotenant, idrol=rol.idrol)
        db_session.add(utr)
        db_session.commit()

    slug = tenant.nombre.lower().replace(" ", "-")
    resp = client.post(
        "/api/v1/auth/login",
        json={"tenant_slug": slug, "email": email, "password": password}
    )
    assert resp.status_code == 200, f"Error login {email}: {resp.text}"
    token = resp.json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------
# Pruebas Base de Usuarios (SuperAdministrador)
# --------------------------------------------------------------------------
def test_list_users_authenticated(client, auth_headers):
    response = client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 1


def test_create_user_success(client, auth_headers):
    payload = {
        "nombrecompleto": "Nuevo Operador",
        "email": "operador_nuevo@test.com",
        "contrasena": "ClaveSegura@123",
        "activo": True
    }
    response = client.post("/api/v1/users", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombrecompleto"] == "Nuevo Operador"
    assert data["email"] == "operador_nuevo@test.com"
    assert data["idusuario"] is not None


def test_create_user_duplicate_email(client, auth_headers):
    payload = {
        "nombrecompleto": "Usuario Repetido",
        "email": "user1@test.com",
        "contrasena": "ClaveSegura@123"
    }
    response = client.post("/api/v1/users", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "correo" in response.json()["detail"]


def test_get_user_by_id(client, auth_headers, setup_test_data):
    u1 = setup_test_data["user1"]
    response = client.get(f"/api/v1/users/{u1.idusuario}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == u1.email


def test_update_user(client, auth_headers, setup_test_data):
    u2 = setup_test_data["user2"]
    payload = {"nombrecompleto": "Usuario Dos Actualizado"}
    response = client.put(f"/api/v1/users/{u2.idusuario}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["nombrecompleto"] == "Usuario Dos Actualizado"


def test_delete_user_soft(client, auth_headers, setup_test_data):
    u2 = setup_test_data["user2"]
    response = client.delete(f"/api/v1/users/{u2.idusuario}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["activo"] is False


# --------------------------------------------------------------------------
# Pruebas de Seguridad RBAC y Aislamiento Multi-Tenant (Prompt 3)
# --------------------------------------------------------------------------
def test_roles_no_autorizados_no_pueden_mutar_usuarios(client, db_session, setup_test_data):
    """Ventas, Operaciones y Auditor reciben 403 en POST, PUT y DELETE /users."""
    t1 = setup_test_data["tenant1"]
    u1 = setup_test_data["user1"]
    roles_prohibidos = [
        ("Auditor", "auditor_u@test.com"),
        ("GestorVentasPostventa", "ventas_u@test.com"),
        ("GestorOperaciones", "ops_u@test.com"),
    ]

    create_payload = {
        "nombrecompleto": "User Ilegal",
        "email": "ilegal_user@test.com",
        "contrasena": "Clave123!Valida",
    }
    update_payload = {"nombrecompleto": "Intento Modificar"}

    for rol_nombre, email in roles_prohibidos:
        _, headers = _crear_usuario_con_rol(client, db_session, email, rol_nombre, t1)

        # POST /users -> 403
        resp_post = client.post("/api/v1/users", json=create_payload, headers=headers)
        assert resp_post.status_code == 403, f"{rol_nombre} no debe poder crear usuarios: {resp_post.status_code}"

        # PUT /users/{id} -> 403
        resp_put = client.put(f"/api/v1/users/{u1.idusuario}", json=update_payload, headers=headers)
        assert resp_put.status_code == 403, f"{rol_nombre} no debe poder editar usuarios: {resp_put.status_code}"

        # DELETE /users/{id} -> 403
        resp_del = client.delete(f"/api/v1/users/{u1.idusuario}", headers=headers)
        assert resp_del.status_code == 403, f"{rol_nombre} no debe poder eliminar usuarios: {resp_del.status_code}"


def test_admin_otra_empresa_recibe_404_en_usuarios_ajenos(client, db_session, setup_test_data):
    """Admin de empresa 2 recibe 404 al intentar ver, editar o eliminar usuario de empresa 1."""
    t1 = setup_test_data["tenant1"]
    t2 = setup_test_data["tenant2"]
    u1 = setup_test_data["user1"]

    _, headers_admin_t2 = _crear_usuario_con_rol(
        client, db_session, "admin_t2_users@test.com", "AdministradorEmpresa", t2
    )

    # GET /users/{u1.idusuario} -> 404
    resp_get = client.get(f"/api/v1/users/{u1.idusuario}", headers=headers_admin_t2)
    assert resp_get.status_code == 404, f"Admin T2 no debe ver usuario de T1: {resp_get.status_code}"

    # PUT /users/{u1.idusuario} -> 404
    resp_put = client.put(f"/api/v1/users/{u1.idusuario}", json={"nombrecompleto": "Hacked"}, headers=headers_admin_t2)
    assert resp_put.status_code == 404

    # DELETE /users/{u1.idusuario} -> 404
    resp_del = client.delete(f"/api/v1/users/{u1.idusuario}", headers=headers_admin_t2)
    assert resp_del.status_code == 404


def test_usuario_no_puede_eliminarse_ni_desactivarse_a_si_mismo(client, db_session, setup_test_data):
    """Un usuario no puede eliminarse ni desactivarse a sí mismo (400 Bad Request)."""
    t1 = setup_test_data["tenant1"]
    admin_user, headers_admin = _crear_usuario_con_rol(
        client, db_session, "admin_self@test.com", "AdministradorEmpresa", t1
    )

    # Intento de DELETE de sí mismo -> 400
    resp_del = client.delete(f"/api/v1/users/{admin_user.idusuario}", headers=headers_admin)
    assert resp_del.status_code == 400
    assert "no puede eliminarse" in resp_del.json()["detail"]

    # Intento de desactivarse a sí mismo vía PUT -> 400
    resp_put = client.put(f"/api/v1/users/{admin_user.idusuario}", json={"activo": False}, headers=headers_admin)
    assert resp_put.status_code == 400
    assert "no puede desactivarse" in resp_put.json()["detail"]


def test_admin_empresa_no_puede_editar_ni_eliminar_superadmin(client, db_session, setup_test_data):
    """Un AdministradorEmpresa no puede editar ni eliminar a un SuperAdministrador (403 Forbidden)."""
    t1 = setup_test_data["tenant1"]
    u1_super = setup_test_data["user1"]

    # Asegurar que u1 sea SuperAdministrador en t1
    rol_super = db_session.execute(select(Role).where(Role.nombrerol == "SuperAdministrador")).scalars().first()
    ut1 = db_session.execute(select(UsuarioTenant).where(UsuarioTenant.idusuario == u1_super.idusuario, UsuarioTenant.idtenant == t1.idtenant)).scalar_one()
    ya_rol = db_session.execute(select(UsuarioTenantRol).where(UsuarioTenantRol.idusuariotenant == ut1.idusuariotenant, UsuarioTenantRol.idrol == rol_super.idrol)).first()
    if not ya_rol:
        db_session.add(UsuarioTenantRol(idusuariotenant=ut1.idusuariotenant, idrol=rol_super.idrol))
        db_session.commit()

    # Crear Admin en el mismo tenant 1
    admin_local, headers_admin = _crear_usuario_con_rol(
        client, db_session, "admin_local_t1@test.com", "AdministradorEmpresa", t1
    )

    # Intento de editar al SuperAdmin -> 403
    resp_put = client.put(f"/api/v1/users/{u1_super.idusuario}", json={"nombrecompleto": "SuperAdmin Modificado"}, headers=headers_admin)
    assert resp_put.status_code == 403
    assert "no tiene privilegios para modificar a un SuperAdministrador" in resp_put.json()["detail"]

    # Intento de eliminar al SuperAdmin -> 403
    resp_del = client.delete(f"/api/v1/users/{u1_super.idusuario}", headers=headers_admin)
    assert resp_del.status_code == 403
    assert "no tiene privilegios para eliminar a un SuperAdministrador" in resp_del.json()["detail"]
