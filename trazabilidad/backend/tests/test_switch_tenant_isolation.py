import time
import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cu001_tenants.tenant import Tenant
from app.models.cu009_categorias.category import Categoria
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu008_catalogo_empresa.tenant_catalog import CatalogoTenant
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto


def _switch_to_tenant(client, auth_headers, target_tenant_id: int):
    resp = client.post(f"/api/v1/auth/switch-tenant/{target_tenant_id}", headers=auth_headers)
    assert resp.status_code == 200, f"Error en switch-tenant: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_switch_tenant_isolation_actors_units_locations(client, auth_headers, setup_test_data, db_session: Session):
    """Con token de switch-tenant a Empresa 2, GET /actors, /locations y /units devuelven solo idtenant = 2."""
    t1 = setup_test_data["tenant1"]
    t2 = setup_test_data["tenant2"]
    suffix = int(time.time() * 1000)

    # 1. Crear datos en Empresa 1
    actor1 = ActorCadena(idtenant=t1.idtenant, nombre=f"Actor T1 {suffix}", tipoactor="PROVEEDOR_EEUU")
    loc1 = Ubicacion(idtenant=t1.idtenant, nombre=f"Loc T1 {suffix}", tipo="almacen")
    cat = Categoria(nombrecategoria=f"Cat {suffix}")
    db_session.add_all([actor1, loc1, cat])
    db_session.flush()

    prod = Producto(nombre=f"Prod {suffix}", modelo=f"M-{suffix}", idcategoria=cat.idcategoria)
    db_session.add(prod)
    db_session.flush()

    var = VarianteProducto(idproducto=prod.idproducto, capacidad="128GB", color="Negro", sku=f"SKU-{suffix}", preciousd=100)
    db_session.add(var)
    db_session.flush()

    unit1 = UnidadProducto(
        idtenant=t1.idtenant, idvariante=var.idvariante, idrecepciondetalle=1,
        numeroserie=f"SN-T1-{suffix}", uuidpublico=str(uuid.uuid4()), estado="disponible"
    )
    # 2. Crear datos en Empresa 2
    actor2 = ActorCadena(idtenant=t2.idtenant, nombre=f"Actor T2 {suffix}", tipoactor="IMPORTADOR")
    loc2 = Ubicacion(idtenant=t2.idtenant, nombre=f"Loc T2 {suffix}", tipo="punto_venta")
    unit2 = UnidadProducto(
        idtenant=t2.idtenant, idvariante=var.idvariante, idrecepciondetalle=1,
        numeroserie=f"SN-T2-{suffix}", uuidpublico=str(uuid.uuid4()), estado="disponible"
    )
    db_session.add_all([unit1, actor2, loc2, unit2])
    db_session.commit()

    # 3. SuperAdmin cambia de contexto a Empresa 2
    headers_t2 = _switch_to_tenant(client, auth_headers, t2.idtenant)

    # 4. Verificar GET /actors
    resp_actors = client.get("/api/v1/actors", headers=headers_t2)
    assert resp_actors.status_code == 200
    actors_items = resp_actors.json()["items"]
    assert len(actors_items) >= 1
    for item in actors_items:
        assert item["idtenant"] == t2.idtenant, f"Actor ajeno detectado en Empresa 2: {item}"

    # 5. Verificar GET /locations
    resp_locs = client.get("/api/v1/locations", headers=headers_t2)
    assert resp_locs.status_code == 200
    locs_items = resp_locs.json()["items"]
    assert len(locs_items) >= 1
    for item in locs_items:
        assert item["idtenant"] == t2.idtenant, f"Ubicación ajena detectada en Empresa 2: {item}"

    # 6. Verificar GET /units
    resp_units = client.get("/api/v1/units", headers=headers_t2)
    assert resp_units.status_code == 200
    units_items = resp_units.json()["items"]
    assert len(units_items) >= 1
    for item in units_items:
        assert item["idtenant"] == t2.idtenant, f"Unidad ajena detectada en Empresa 2: {item}"


def test_create_unit_rejects_foreign_actor_and_location(client, auth_headers, setup_test_data, db_session: Session):
    """Al registrar una unidad en Empresa 2, rechaza actores o ubicaciones de Empresa 1 con 422."""
    t1 = setup_test_data["tenant1"]
    t2 = setup_test_data["tenant2"]
    suffix = int(time.time() * 1000)

    # Actor y ubicación en Empresa 1
    actor_t1 = ActorCadena(idtenant=t1.idtenant, nombre=f"Actor T1 {suffix}", tipoactor="PROVEEDOR_EEUU")
    loc_t1 = Ubicacion(idtenant=t1.idtenant, nombre=f"Loc T1 {suffix}", tipo="almacen")
    cat = Categoria(nombrecategoria=f"Cat Unit {suffix}")
    db_session.add_all([actor_t1, loc_t1, cat])
    db_session.flush()

    prod = Producto(nombre=f"Prod Unit {suffix}", modelo=f"MU-{suffix}", idcategoria=cat.idcategoria)
    db_session.add(prod)
    db_session.flush()

    var = VarianteProducto(idproducto=prod.idproducto, capacidad="256GB", color="Blanco", sku=f"SKU-U-{suffix}", preciousd=200)
    db_session.add(var)
    db_session.flush()

    # Actor y ubicación legítimos en Empresa 2
    actor_t2 = ActorCadena(idtenant=t2.idtenant, nombre=f"Actor T2 {suffix}", tipoactor="IMPORTADOR")
    loc_t2 = Ubicacion(idtenant=t2.idtenant, nombre=f"Loc T2 {suffix}", tipo="punto_venta")
    db_session.add_all([actor_t2, loc_t2])
    db_session.commit()

    # Cambiar contexto a Empresa 2
    headers_t2 = _switch_to_tenant(client, auth_headers, t2.idtenant)

    # Intento 1: usar actor de Empresa 1 en Empresa 2 -> 422
    payload_bad_actor = {
        "idvariante": var.idvariante,
        "numeroserie": f"SN-FAIL-A-{suffix}",
        "idcustodioactual": actor_t1.idactor,
        "idubicacionactual": loc_t2.idubicacion,
    }
    resp1 = client.post("/api/v1/units", json=payload_bad_actor, headers=headers_t2)
    assert resp1.status_code == 422, f"Debe rechazar actor de otra empresa: {resp1.status_code} {resp1.text}"

    # Intento 2: usar ubicación de Empresa 1 en Empresa 2 -> 422
    payload_bad_loc = {
        "idvariante": var.idvariante,
        "numeroserie": f"SN-FAIL-L-{suffix}",
        "idcustodioactual": actor_t2.idactor,
        "idubicacionactual": loc_t1.idubicacion,
    }
    resp2 = client.post("/api/v1/units", json=payload_bad_loc, headers=headers_t2)
    assert resp2.status_code == 422, f"Debe rechazar ubicación de otra empresa: {resp2.status_code} {resp2.text}"

    # Intento 3: datos legítimos de Empresa 2 -> 201
    payload_ok = {
        "idvariante": var.idvariante,
        "numeroserie": f"SN-SUCCESS-{suffix}",
        "idcustodioactual": actor_t2.idactor,
        "idubicacionactual": loc_t2.idubicacion,
    }
    resp3 = client.post("/api/v1/units", json=payload_ok, headers=headers_t2)
    assert resp3.status_code == 201
    assert resp3.json()["idtenant"] == t2.idtenant


def test_create_unit_rejects_foreign_variant(client, auth_headers, setup_test_data, db_session: Session):
    """Al registrar una unidad en Empresa 2, rechaza variantes que pertenezcan a Empresa 1 (422)."""
    t1 = setup_test_data["tenant1"]
    t2 = setup_test_data["tenant2"]
    suffix = int(time.time() * 1000)

    cat = Categoria(nombrecategoria=f"Cat Var {suffix}")
    db_session.add(cat)
    db_session.flush()

    prod = Producto(nombre=f"Prod Var {suffix}", modelo=f"MV-{suffix}", idcategoria=cat.idcategoria)
    db_session.add(prod)
    db_session.flush()

    var_t1 = VarianteProducto(idproducto=prod.idproducto, capacidad="512GB", color="Oro", sku=f"SKU-T1-{suffix}", preciousd=500)
    db_session.add(var_t1)
    db_session.flush()

    # Asociar variante exclusivamente a Empresa 1 en CatalogoTenant
    ct1 = CatalogoTenant(idtenant=t1.idtenant, idvariante=var_t1.idvariante, precioventa=600)
    db_session.add(ct1)
    db_session.commit()

    # Cambiar contexto a Empresa 2
    headers_t2 = _switch_to_tenant(client, auth_headers, t2.idtenant)

    # Intento de registrar unidad con la variante de Empresa 1 -> 422
    payload = {
        "idvariante": var_t1.idvariante,
        "numeroserie": f"SN-VAR-FAIL-{suffix}",
    }
    resp = client.post("/api/v1/units", json=payload, headers=headers_t2)
    assert resp.status_code == 422
    assert "otra empresa" in resp.json()["detail"].lower()
