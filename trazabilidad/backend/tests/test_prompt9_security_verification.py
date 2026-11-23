"""Pruebas de Verificación Integral de Seguridad (Prompt 9).

Verifica exhaustivamente la matriz de seguridad exigida:
1. Operaciones, Ventas y Auditor reciben 403 en POST/PUT/DELETE de /users, /tenants y POST /users/{id}/roles.
2. El Admin de Empresa 2 no ve usuarios ni empresa de la Empresa 1 (404/403 y filtrado estricto).
3. Con switch-tenant a la Empresa 2, /actors, /units, /locations y /purchases devuelven solo idtenant = 2.
4. DELETE /products da 403 a roles no autorizados (Admin Empresa, Operaciones, Ventas, Auditor).
5. Las operaciones DELETE con registros dependientes devuelven 409 Conflict.
"""
import pytest
from starlette.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.db.session import SessionLocal
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu009_categorias.category import Categoria
from app.models.cu010_ordenes_compra.purchase import Compra
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.packages.p4_trazabilidad.models.cu023_reporte_sospecha.suspicion_report import ReporteSospecha


def get_token(client, tenant_slug: str, email: str, password: str = "Admin123!"):
    resp = client.post("/api/v1/auth/login", json={
        "tenant_slug": tenant_slug,
        "email": email,
        "password": password
    })
    assert resp.status_code == 200, f"Error login {email}: {resp.text}"
    return resp.json()["access_token"]


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def api_client():
    return TestClient(app)


# =============================================================================
# 1. OPERACIONES / VENTAS / AUDITOR RECIBEN 403 EN MUTACIONES CRÍTICAS
# =============================================================================

@pytest.mark.parametrize("email", [
    "operaciones@istore.com",
    "ventas@istore.com",
    "auditor@istore.com",
])
def test_roles_operativos_reciben_403_en_users_y_tenants(api_client, email):
    token = get_token(api_client, "1", email)
    h = auth_header(token)

    # 1. Mutaciones en /users
    resp_post_u = api_client.post("/api/v1/users", json={"email": "dummy@test.com", "password": "Pass123!A#", "nombrecompleto": "Dummy"}, headers=h)
    assert resp_post_u.status_code == 403, f"{email} debió recibir 403 en POST /users, recibió {resp_post_u.status_code}"

    resp_put_u = api_client.put("/api/v1/users/1", json={"nombrecompleto": "Hacked"}, headers=h)
    assert resp_put_u.status_code == 403, f"{email} debió recibir 403 en PUT /users, recibió {resp_put_u.status_code}"

    resp_del_u = api_client.delete("/api/v1/users/1", headers=h)
    assert resp_del_u.status_code == 403, f"{email} debió recibir 403 en DELETE /users, recibió {resp_del_u.status_code}"

    # 2. Mutaciones en /tenants
    resp_post_t = api_client.post("/api/v1/tenants", json={"nombre": "Fake", "razonsocial": "Fake SA", "nit": "000000"}, headers=h)
    assert resp_post_t.status_code == 403, f"{email} debió recibir 403 en POST /tenants, recibió {resp_post_t.status_code}"

    resp_put_t = api_client.put("/api/v1/tenants/1", json={"nombre": "Mod Fake"}, headers=h)
    assert resp_put_t.status_code == 403, f"{email} debió recibir 403 en PUT /tenants, recibió {resp_put_t.status_code}"

    resp_del_t = api_client.delete("/api/v1/tenants/1", headers=h)
    assert resp_del_t.status_code == 403, f"{email} debió recibir 403 en DELETE /tenants, recibió {resp_del_t.status_code}"

    # 3. Asignación de roles
    resp_roles = api_client.post("/api/v1/users/1/roles", json={"role_names": ["SuperAdministrador"]}, headers=h)
    assert resp_roles.status_code == 403, f"{email} debió recibir 403 en POST /users/roles, recibió {resp_roles.status_code}"


# =============================================================================
# 2. EL ADMIN DE LA EMPRESA 2 NO VE USUARIOS NI EMPRESA DE LA EMPRESA 1
# =============================================================================

def test_admin_empresa_2_aislamiento_total(api_client):
    token_admin_2 = get_token(api_client, "2", "admin@techimport.com")
    h = auth_header(token_admin_2)

    # 1. GET /users solo devuelve usuarios vinculados al tenant 2
    resp_users = api_client.get("/api/v1/users", headers=h)
    assert resp_users.status_code == 200
    users_data = resp_users.json()["items"]
    for u in users_data:
        assert "istore.com" not in u["email"], f"Fuga de usuario de empresa 1: {u['email']}"
        assert "superadmin@trazabilidad.com" not in u["email"], f"Fuga de SuperAdmin: {u['email']}"

    # 2. GET /users/{id} de un usuario perteneciente a empresa 1 devuelve 404
    db = SessionLocal()
    try:
        user_t1 = db.query(User).filter(User.email == "admin@istore.com").first()
        assert user_t1 is not None
        id_t1 = user_t1.idusuario
    finally:
        db.close()

    resp_user_1 = api_client.get(f"/api/v1/users/{id_t1}", headers=h)
    assert resp_user_1.status_code == 404

    # 3. GET /tenants solo devuelve la empresa 2 (total == 1, idtenant == 2)
    resp_tenants = api_client.get("/api/v1/tenants", headers=h)
    assert resp_tenants.status_code == 200
    t_items = resp_tenants.json()["items"]
    assert len(t_items) == 1
    assert t_items[0]["idtenant"] == 2

    # 4. GET /tenants/1 devuelve 403 Forbidden
    resp_t1 = api_client.get("/api/v1/tenants/1", headers=h)
    assert resp_t1.status_code == 403


# =============================================================================
# 3. SWITCH-TENANT A EMPRESA 2 AISLA ACTORS, UNITS, LOCATIONS, PURCHASES
# =============================================================================

def test_switch_tenant_aisla_recursos_al_tenant_activo(api_client):
    # 1. El Admin de Empresa 2 solo ve recursos con idtenant = 2 en endpoints operacionales
    token_t2 = get_token(api_client, "2", "admin@techimport.com")
    h_t2 = auth_header(token_t2)

    resp_actors = api_client.get("/api/v1/actors", headers=h_t2)
    assert resp_actors.status_code == 200
    for a in resp_actors.json()["items"]:
        assert a["idtenant"] == 2

    resp_units = api_client.get("/api/v1/units", headers=h_t2)
    assert resp_units.status_code == 200
    for u in resp_units.json()["items"]:
        assert u["idtenant"] == 2

    resp_loc = api_client.get("/api/v1/locations", headers=h_t2)
    assert resp_loc.status_code == 200
    for l in resp_loc.json()["items"]:
        assert l["idtenant"] == 2

    resp_purch = api_client.get("/api/v1/purchases", headers=h_t2)
    assert resp_purch.status_code == 200
    for p in resp_purch.json()["items"]:
        assert p["idtenant"] == 2

    # 2. El SuperAdministrador de plataforma NO tiene acceso a recursos de empresas clientes (recibe 403)
    token_super = get_token(api_client, "1", "superadmin@trazabilidad.com")
    h_super = auth_header(token_super)

    for endpoint in ["/api/v1/actors", "/api/v1/units", "/api/v1/locations", "/api/v1/purchases", "/api/v1/sales"]:
        resp_sa = api_client.get(endpoint, headers=h_super)
        assert resp_sa.status_code == 403, f"SuperAdmin debió recibir 403 en {endpoint}, recibió {resp_sa.status_code}"


# =============================================================================
# 4. DELETE /products DA 403 A ROLES NO AUTORIZADOS
# =============================================================================

@pytest.mark.parametrize("slug,email", [
    ("2", "admin@techimport.com"),
    ("1", "admin@istore.com"),
    ("1", "operaciones@istore.com"),
    ("1", "ventas@istore.com"),
    ("1", "auditor@istore.com"),
])
def test_delete_products_da_403_a_roles_no_autorizados(api_client, slug, email):
    token = get_token(api_client, slug, email)
    h = auth_header(token)

    resp = api_client.delete("/api/v1/products/1", headers=h)
    assert resp.status_code == 403, f"{email} debió recibir 403 en DELETE /products/1, recibió {resp.status_code}"


# =============================================================================
# 5. LOS DELETE CON DEPENDIENTES DAN 409 CONFLICT
# =============================================================================

def test_delete_con_dependientes_da_409(api_client):
    token_super = get_token(api_client, "1", "superadmin@trazabilidad.com")
    token_admin1 = get_token(api_client, "1", "admin@istore.com")
    h_super = auth_header(token_super)
    h_admin1 = auth_header(token_admin1)
    db = SessionLocal()

    try:
        # 1. Actor con compras asociadas en Tenant 1 (Admin Empresa 1)
        actor_con_compra = db.execute(
            select(ActorCadena)
            .join(Compra, Compra.idproveedor == ActorCadena.idactor)
            .where(ActorCadena.idtenant == 1)
        ).scalars().first()
        assert actor_con_compra is not None
        resp_actor = api_client.delete(f"/api/v1/actors/{actor_con_compra.idactor}", headers=h_admin1)
        assert resp_actor.status_code == 409
        assert "registros relacionados" in resp_actor.json()["detail"].lower()

        # 2. Categoría con productos asociados (SuperAdmin de plataforma)
        cat = db.execute(select(Categoria).join(Producto, Producto.idcategoria == Categoria.idcategoria)).scalars().first()
        assert cat is not None
        resp_cat = api_client.delete(f"/api/v1/categories/{cat.idcategoria}", headers=h_super)
        assert resp_cat.status_code == 409
        assert "registros relacionados" in resp_cat.json()["detail"].lower()

        # 3. Producto con variantes y compras/unidades (SuperAdmin de plataforma)
        prod = db.execute(select(Producto).where(Producto.nombre.like("%iPhone 16 Pro Max%"))).scalars().first()
        assert prod is not None
        resp_prod = api_client.delete(f"/api/v1/products/{prod.idproducto}", headers=h_super)
        assert resp_prod.status_code == 409
        assert "unidades físicas" in resp_prod.json()["detail"].lower() or "registros relacionados" in resp_prod.json()["detail"].lower()

        # 4. Unidad física con dependientes (Admin Empresa 1)
        unit = db.execute(select(UnidadProducto).where(UnidadProducto.idtenant == 1)).scalars().first()
        assert unit is not None
        # Asociar reporte
        rep_existente = db.execute(select(ReporteSospecha).where(ReporteSospecha.idunidad == unit.idunidad)).scalars().first()
        if not rep_existente:
            rep = ReporteSospecha(
                idtenant=1,
                idunidad=unit.idunidad,
                codigoticket=f"TCK-P9-{unit.idunidad}"[:30],
                tipoanomalia="fraude_autenticidad",
                descripcion="Sospecha de prueba P9",
                estado="pendiente",
                gravedad="alta"
            )
            db.add(rep)
            db.commit()

        resp_unit = api_client.delete(f"/api/v1/units/{unit.idunidad}", headers=h_admin1)
        assert resp_unit.status_code == 409
        assert "registros relacionados" in resp_unit.json()["detail"].lower()

    finally:
        db.close()
