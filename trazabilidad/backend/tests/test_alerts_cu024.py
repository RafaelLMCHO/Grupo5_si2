"""CU-024 — Gestionar Alertas e Incidencias.

Cubre el listado, resumen, creación manual, clasificación/resolución y el
aislamiento multi-tenant sobre la tabla `alerta`.
"""

import time
import uuid as uuid_lib

from sqlalchemy import select

from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu009_categorias.category import Categoria
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu021_eventos_transporte.transport_event import Alerta


def login(client, tenant_slug, email, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"tenant_slug": tenant_slug, "email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _crear_unidad(db_session, tenant):
    suffix = int(time.time() * 1000)
    cat = Categoria(nombrecategoria=f"Cat AL {suffix}")
    db_session.add(cat)
    db_session.flush()
    prod = Producto(
        idcategoria=cat.idcategoria, nombre=f"Producto AL {suffix}", modelo="M-AL", paisorigen="EEUU"
    )
    db_session.add(prod)
    db_session.flush()
    var = VarianteProducto(idproducto=prod.idproducto, sku=f"SKU-AL-{suffix}", color="Negro", capacidad="64GB")
    db_session.add(var)
    db_session.flush()
    unidad = UnidadProducto(
        idtenant=tenant.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-AL-{suffix}",
        uuidpublico=str(uuid_lib.uuid4()),
        estado="disponible",
    )
    db_session.add(unidad)
    db_session.commit()
    return unidad


def _crear_alerta_directa(db_session, tenant, unidad=None, estado="pendiente", gravedad="media"):
    alerta = Alerta(
        idtenant=tenant.idtenant,
        idunidad=unidad.idunidad if unidad else None,
        tipoalerta="temperatura",
        descripcion="Alerta de prueba",
        gravedad=gravedad,
        estado=estado,
    )
    db_session.add(alerta)
    db_session.commit()
    return alerta


def test_crear_alertas_cu024(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    resp = client.post(
        "/api/v1/alerts",
        json={
            "tipoalerta": "vibracion",
            "descripcion": "Impacto detectado durante el traslado",
            "gravedad": "alta",
            "idunidad": unidad.idunidad,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["tipoalerta"] == "vibracion"
    assert data["gravedad"] == "alta"
    assert data["estado"] == "pendiente"
    assert data["numeroserie"] == unidad.numeroserie
    assert data["fecharesolucion"] is None


def test_crear_alerta_tipo_invalido(client, db_session, setup_test_data, auth_headers):
    resp = client.post(
        "/api/v1/alerts",
        json={"tipoalerta": "no_existe", "descripcion": "descripcion valida", "gravedad": "media"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_crear_alerta_unidad_otro_tenant(client, db_session, setup_test_data, auth_headers):
    t2 = setup_test_data["tenant2"]
    unidad_ajena = _crear_unidad(db_session, t2)

    resp = client.post(
        "/api/v1/alerts",
        json={
            "tipoalerta": "inconsistencia_cadena",
            "descripcion": "Intento cross-tenant",
            "gravedad": "media",
            "idunidad": unidad_ajena.idunidad,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_listar_alertas_con_filtros(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    _crear_alerta_directa(db_session, t1, estado="pendiente", gravedad="critica")
    _crear_alerta_directa(db_session, t1, estado="resuelta", gravedad="baja")

    resp = client.get("/api/v1/alerts", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    pend = client.get("/api/v1/alerts?estado=pendiente", headers=auth_headers).json()
    assert pend["total"] == 1
    assert pend["items"][0]["estado"] == "pendiente"

    crit = client.get("/api/v1/alerts?gravedad=critica", headers=auth_headers).json()
    assert crit["total"] == 1
    assert crit["items"][0]["gravedad"] == "critica"


def test_resumen_alertas(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    _crear_alerta_directa(db_session, t1, estado="pendiente", gravedad="critica")
    _crear_alerta_directa(db_session, t1, estado="pendiente", gravedad="media")
    _crear_alerta_directa(db_session, t1, estado="resuelta", gravedad="baja")

    resp = client.get("/api/v1/alerts/summary", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total"] == 3
    assert data["pendientes"] == 2
    assert data["resueltas"] == 1
    assert data["criticas"] == 1


def test_resolver_alerta(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    alerta = _crear_alerta_directa(db_session, t1, estado="pendiente")

    resp = client.patch(
        f"/api/v1/alerts/{alerta.idalerta}/estado",
        json={"estado": "resuelta", "comentario": "Verificado y descartado"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["estado"] == "resuelta"
    assert data["fecharesolucion"] is not None
    assert data["idusuarioresolutor"] == setup_test_data["user1"].idusuario
    assert "Verificado y descartado" in data["descripcion"]


def test_estado_invalido(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    alerta = _crear_alerta_directa(db_session, t1)

    resp = client.patch(
        f"/api/v1/alerts/{alerta.idalerta}/estado",
        json={"estado": "cerrada"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_alerta_otro_tenant_devuelve_404(client, db_session, setup_test_data, auth_headers):
    t2 = setup_test_data["tenant2"]
    alerta = _crear_alerta_directa(db_session, t2)

    # user1 (SuperAdministrador con empresa activa = tenant1) no ve la alerta de tenant2
    ajeno = client.get(f"/api/v1/alerts/{alerta.idalerta}", headers=auth_headers)
    assert ajeno.status_code == 404


def test_alertas_sin_token(client, setup_test_data):
    resp = client.get("/api/v1/alerts")
    assert resp.status_code in (401, 403)


def test_alertas_sin_rol(client, setup_test_data):
    # Login sin asignar rol: no puede gestionar alertas -> 403.
    headers = login(client, "empresa-test-1", "user1@test.com", "MiClave@123")
    resp = client.get("/api/v1/alerts", headers=headers)
    assert resp.status_code == 403
