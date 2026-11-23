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
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------
# Pruebas de SuperAdministrador (CU-001)
# --------------------------------------------------------------------------
def test_list_tenants_superadmin(client, auth_headers):
    response = client.get("/api/v1/tenants", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert data["total"] >= 2


def test_create_tenant_superadmin_success(client, auth_headers):
    payload = {
        "nombre": "Nueva Empresa Corp",
        "razonsocial": "Nueva Empresa Corp S.R.L.",
        "nit": "999888777",
        "email": "contacto@nuevaempresa.com",
        "telefono": "78912345",
        "activo": True
    }
    response = client.post("/api/v1/tenants", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nueva Empresa Corp"
    assert data["nit"] == "999888777"
    assert data["idtenant"] is not None


def test_create_tenant_duplicate_nit(client, auth_headers):
    payload = {
        "nombre": "Empresa Duplicada",
        "razonsocial": "Empresa Duplicada S.A.",
        "nit": "1111111",
        "email": "dup@empresa.com"
    }
    response = client.post("/api/v1/tenants", json=payload, headers=auth_headers)
    assert response.status_code == 400
    assert "NIT" in response.json()["detail"]


def test_get_tenant_by_id_superadmin(client, auth_headers, setup_test_data):
    t1 = setup_test_data["tenant1"]
    response = client.get(f"/api/v1/tenants/{t1.idtenant}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == t1.nombre


def test_update_tenant_superadmin(client, auth_headers, setup_test_data):
    t1 = setup_test_data["tenant1"]
    payload = {"nombre": "Empresa Test 1 Modificada", "telefono": "77700000"}
    response = client.put(f"/api/v1/tenants/{t1.idtenant}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Empresa Test 1 Modificada"
    assert response.json()["telefono"] == "77700000"


def test_delete_tenant_soft_superadmin(client, auth_headers, setup_test_data):
    t2 = setup_test_data["tenant2"]
    response = client.delete(f"/api/v1/tenants/{t2.idtenant}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["activo"] is False


# --------------------------------------------------------------------------
# Pruebas de Seguridad RBAC y Aislamiento Multi-Tenant (Prompt 2)
# --------------------------------------------------------------------------
def test_roles_no_autorizados_no_pueden_mutar_tenants(client, db_session, setup_test_data):
    """Auditor, GestorVentas, GestorOperaciones y AdministradorEmpresa reciben 403 en POST/PUT/DELETE /tenants."""
    t1 = setup_test_data["tenant1"]
    roles_prohibidos = [
        ("Auditor", "auditor_tenant@test.com"),
        ("GestorVentasPostventa", "ventas_tenant@test.com"),
        ("GestorOperaciones", "ops_tenant@test.com"),
        ("AdministradorEmpresa", "admin_tenant@test.com"),
    ]

    create_payload = {
        "nombre": "Empresa Ilegal",
        "razonsocial": "Empresa Ilegal S.A.",
        "nit": "999000111",
        "email": "ilegal@test.com",
    }
    update_payload = {"nombre": "Nombre Modificado"}

    for rol_nombre, email in roles_prohibidos:
        headers = _crear_usuario_con_rol(client, db_session, email, rol_nombre, t1)

        # POST /tenants -> 403
        resp_post = client.post("/api/v1/tenants", json=create_payload, headers=headers)
        assert resp_post.status_code == 403, f"{rol_nombre} no debe poder crear empresas: {resp_post.status_code}"

        # PUT /tenants/{id} -> 403
        resp_put = client.put(f"/api/v1/tenants/{t1.idtenant}", json=update_payload, headers=headers)
        assert resp_put.status_code == 403, f"{rol_nombre} no debe poder editar empresas: {resp_put.status_code}"

        # DELETE /tenants/{id} -> 403
        resp_del = client.delete(f"/api/v1/tenants/{t1.idtenant}", headers=headers)
        assert resp_del.status_code == 403, f"{rol_nombre} no debe poder desactivar empresas: {resp_del.status_code}"


def test_admin_empresa2_no_puede_ver_tenant1(client, db_session, setup_test_data):
    """El admin de la empresa 2 no puede consultar /tenants/1 (debe responder 403)."""
    t1 = setup_test_data["tenant1"]
    t2 = setup_test_data["tenant2"]

    headers_admin_t2 = _crear_usuario_con_rol(
        client, db_session, "admin_t2@test.com", "AdministradorEmpresa", t2
    )

    # Intento de consultar tenant 1 -> 403 Forbidden
    resp_t1 = client.get(f"/api/v1/tenants/{t1.idtenant}", headers=headers_admin_t2)
    assert resp_t1.status_code == 403, f"Admin T2 no debe poder consultar T1: {resp_t1.status_code}"
    assert "No tiene permisos para consultar información de otra empresa" in resp_t1.json()["detail"]

    # Consulta de su propio tenant 2 -> 200 OK
    resp_t2 = client.get(f"/api/v1/tenants/{t2.idtenant}", headers=headers_admin_t2)
    assert resp_t2.status_code == 200
    assert resp_t2.json()["idtenant"] == t2.idtenant


def test_usuario_no_superadmin_solo_lista_su_empresa_activa(client, db_session, setup_test_data):
    """GET /tenants para un usuario no superadmin devuelve únicamente su empresa activa."""
    t2 = setup_test_data["tenant2"]

    headers_admin_t2 = _crear_usuario_con_rol(
        client, db_session, "admin_t2_list@test.com", "AdministradorEmpresa", t2
    )

    resp = client.get("/api/v1/tenants", headers=headers_admin_t2)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["idtenant"] == t2.idtenant
    assert data["items"][0]["nombre"] == t2.nombre
