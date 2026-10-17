"""CU-018 (registro de consultas públicas) y CU-033 (registro en Blockchain).

Los tests corren con BLOCKCHAIN_ENABLED=False (modo degradado): los eventos se
persisten y se calcula su hash, pero el anclaje queda en estado 'pendiente'.
"""

import time
import uuid as uuid_lib

from sqlalchemy import select

from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu009_categorias.category import Categoria
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.models.cu018_trazabilidad.consulta_trazabilidad import ConsultaTrazabilidad
from app.models.cu033_blockchain.registro_blockchain import RegistroBlockchain


def login(client, tenant_slug, email, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"tenant_slug": tenant_slug, "email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _crear_unidad(db_session, setup_test_data, con_qr=True):
    t1 = setup_test_data["tenant1"]
    u1 = setup_test_data["user1"]
    suffix = int(time.time() * 1000)

    cat = Categoria(nombrecategoria=f"Cat BC {suffix}")
    db_session.add(cat)
    db_session.flush()

    prod = Producto(
        idcategoria=cat.idcategoria,
        nombre=f"Producto BC {suffix}",
        modelo="MOD-BC",
        paisorigen="EEUU",
    )
    db_session.add(prod)
    db_session.flush()

    var = VarianteProducto(
        idproducto=prod.idproducto, sku=f"SKU-BC-{suffix}", color="Negro", capacidad="128GB"
    )
    db_session.add(var)
    db_session.flush()

    uuid_publico = str(uuid_lib.uuid4())
    unidad = UnidadProducto(
        idtenant=t1.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-BC-{suffix}",
        uuidpublico=uuid_publico,
        estado="disponible",
    )
    db_session.add(unidad)
    db_session.flush()

    if con_qr:
        db_session.add(
            CodigoQR(
                idunidad=unidad.idunidad,
                tokenpublico=f"tok-{suffix}",
                url=f"https://example.com/trace/{uuid_publico}",
                activo=True,
            )
        )

    ubic = Ubicacion(
        idtenant=t1.idtenant, nombre=f"Almacen BC {suffix}", tipo="almacen", pais="Bolivia"
    )
    db_session.add(ubic)
    db_session.commit()
    return {"unidad": unidad, "ubicacion": ubic, "usuario": u1, "tenant": t1}


# ---------------------------------------------------------------------------
# CU-018 — registro de cada consulta pública del QR
# ---------------------------------------------------------------------------


def test_trace_publico_registra_consulta(client, db_session, setup_test_data):
    ctx = _crear_unidad(db_session, setup_test_data, con_qr=True)

    resp = client.get(f"/api/v1/trace/{ctx['unidad'].uuidpublico}")
    assert resp.status_code == 200, resp.text

    consultas = db_session.execute(
        select(ConsultaTrazabilidad).where(
            ConsultaTrazabilidad.idcodigoqr
            == select(CodigoQR.idcodigoqr)
            .where(CodigoQR.idunidad == ctx["unidad"].idunidad)
            .scalar_subquery()
        )
    ).scalars().all()
    assert len(consultas) == 1
    assert consultas[0].ip is not None


# ---------------------------------------------------------------------------
# CU-033 — registrar evento y anclarlo (modo degradado)
# ---------------------------------------------------------------------------


def test_crear_evento_anclado_modo_degradado(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    body = {
        "tipoevento": "fabricacion",
        "idubicacion": ctx["ubicacion"].idubicacion,
        "descripcion": "Alta en planta",
        "unidadIds": [ctx["unidad"].idunidad],
        "anchor": True,
    }
    resp = client.post("/api/v1/blockchain/events", json=body, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["tipoevento"] == "fabricacion"
    assert data["ubicacion_nombre"] == ctx["ubicacion"].nombre
    assert len(data["payloadhash"]) == 64
    assert data["unidades"] == [ctx["unidad"].numeroserie]

    registro = data["registro_blockchain"]
    assert registro is not None
    assert registro["estado"] == "pendiente"
    assert registro["payloadhash"] == data["payloadhash"]
    assert registro["mensajeerror"]

    idevento = data["idevento"]

    r = db_session.execute(
        select(RegistroBlockchain).where(RegistroBlockchain.idevento == idevento)
    ).scalar_one()
    assert r.estado == "pendiente"


def test_crear_evento_sin_anclar(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    body = {
        "tipoevento": "recepcion_almacen",
        "idubicacion": ctx["ubicacion"].idubicacion,
        "anchor": False,
    }
    resp = client.post("/api/v1/blockchain/events", json=body, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["registro_blockchain"] is None
    assert len(data["payloadhash"]) == 64


def test_crear_evento_ubicacion_invalida(client, db_session, setup_test_data, auth_headers):
    _crear_unidad(db_session, setup_test_data)

    resp = client.post(
        "/api/v1/blockchain/events",
        json={"tipoevento": "fabricacion", "idubicacion": 999999, "anchor": False},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_crear_evento_tipo_invalido(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    resp = client.post(
        "/api/v1/blockchain/events",
        json={"tipoevento": "no_existe", "idubicacion": ctx["ubicacion"].idubicacion},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_get_evento_detalle(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    created = client.post(
        "/api/v1/blockchain/events",
        json={
            "tipoevento": "exportacion",
            "idubicacion": ctx["ubicacion"].idubicacion,
            "anchor": True,
        },
        headers=auth_headers,
    ).json()

    resp = client.get(f"/api/v1/blockchain/events/{created['idevento']}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["idevento"] == created["idevento"]
    assert data["usuario_nombre"] == "Usuario Uno"
    assert data["registro_blockchain"]["estado"] == "pendiente"


def test_verify_evento_modo_degradado(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    created = client.post(
        "/api/v1/blockchain/events",
        json={
            "tipoevento": "venta",
            "idubicacion": ctx["ubicacion"].idubicacion,
            "anchor": True,
        },
        headers=auth_headers,
    ).json()

    resp = client.get(
        f"/api/v1/blockchain/events/{created['idevento']}/verify", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["coincide"] is True
    assert data["en_blockchain"] is False
    assert data["verificado"] is False


def test_anchor_evento_existente(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    created = client.post(
        "/api/v1/blockchain/events",
        json={
            "tipoevento": "transporte_terrestre",
            "idubicacion": ctx["ubicacion"].idubicacion,
            "anchor": False,
        },
        headers=auth_headers,
    ).json()

    resp = client.post(
        f"/api/v1/blockchain/events/{created['idevento']}/anchor",
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["estado"] == "pendiente"


def test_listar_registry_y_status(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    client.post(
        "/api/v1/blockchain/events",
        json={
            "tipoevento": "fabricacion",
            "idubicacion": ctx["ubicacion"].idubicacion,
            "anchor": True,
        },
        headers=auth_headers,
    )

    resp = client.get("/api/v1/blockchain/registry", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    assert len(resp.json()) >= 1

    status_resp = client.get("/api/v1/blockchain/status", headers=auth_headers)
    assert status_resp.status_code == 200, status_resp.text
    assert status_resp.json()["ready"] is False


def test_evento_otro_tenant_devuelve_404(client, db_session, setup_test_data, auth_headers):
    ctx = _crear_unidad(db_session, setup_test_data)

    created = client.post(
        "/api/v1/blockchain/events",
        json={
            "tipoevento": "fabricacion",
            "idubicacion": ctx["ubicacion"].idubicacion,
            "anchor": False,
        },
        headers=auth_headers,
    ).json()

    headers2 = login(client, "empresa-test-2", "user2@test.com", "OtroPassword@456")
    resp = client.get(
        f"/api/v1/blockchain/events/{created['idevento']}", headers=headers2
    )
    assert resp.status_code == 404


def test_crear_evento_sin_token(client, setup_test_data):
    resp = client.post("/api/v1/blockchain/events", json={"tipoevento": "x", "idubicacion": 1})
    assert resp.status_code in (401, 403)
