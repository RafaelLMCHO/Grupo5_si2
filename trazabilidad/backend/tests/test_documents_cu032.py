"""CU-032 — Adjuntar Documentos a Unidades.

Cubre la carga/asociación de documentos a una unidad, el listado, la consulta,
la verificación de integridad por hash, la eliminación y el aislamiento por tenant.
"""

import hashlib
import time
import uuid as uuid_lib

from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu009_categorias.category import Categoria
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu032_documentos_unidad.documento_unidad import DocumentoUnidad


def login(client, tenant_slug, email, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"tenant_slug": tenant_slug, "email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _crear_unidad(db_session, tenant):
    suffix = int(time.time() * 1000)
    cat = Categoria(nombrecategoria=f"Cat DOC {suffix}")
    db_session.add(cat)
    db_session.flush()
    prod = Producto(
        idcategoria=cat.idcategoria, nombre=f"Producto DOC {suffix}", modelo="M-DOC", paisorigen="EEUU"
    )
    db_session.add(prod)
    db_session.flush()
    var = VarianteProducto(idproducto=prod.idproducto, sku=f"SKU-DOC-{suffix}", color="Plateado", capacidad="128GB")
    db_session.add(var)
    db_session.flush()
    unidad = UnidadProducto(
        idtenant=tenant.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-DOC-{suffix}",
        uuidpublico=str(uuid_lib.uuid4()),
        estado="disponible",
    )
    db_session.add(unidad)
    db_session.commit()
    return unidad


def test_adjuntar_documento_calcula_hash(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    resp = client.post(
        f"/api/v1/documents/units/{unidad.idunidad}",
        json={
            "nombre": "Factura de compra",
            "urlarchivo": "https://storage.local/facturas/f-1.pdf",
            "tipodocumento": "factura_compra",
            "contenido": "contenido-de-la-factura",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["tipodocumento"] == "factura_compra"
    assert data["numeroserie"] == unidad.numeroserie
    assert data["hasharchivo"] == hashlib.sha256(b"contenido-de-la-factura").hexdigest()
    assert data["fechaemision"] is not None


def test_adjuntar_documento_tipo_invalido(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    resp = client.post(
        f"/api/v1/documents/units/{unidad.idunidad}",
        json={
            "nombre": "Doc raro",
            "urlarchivo": "https://storage.local/x",
            "tipodocumento": "no_existe",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_adjuntar_documento_unidad_ajena(client, db_session, setup_test_data, auth_headers):
    t2 = setup_test_data["tenant2"]
    unidad_ajena = _crear_unidad(db_session, t2)

    resp = client.post(
        f"/api/v1/documents/units/{unidad_ajena.idunidad}",
        json={
            "nombre": "Doc cross-tenant",
            "urlarchivo": "https://storage.local/x",
            "tipodocumento": "informe_tecnico",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_fecha_vencimiento_invalida(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    resp = client.post(
        f"/api/v1/documents/units/{unidad.idunidad}",
        json={
            "nombre": "Garantía",
            "urlarchivo": "https://storage.local/g.pdf",
            "tipodocumento": "comprobante_garantia",
            "fechaemision": "2026-05-01",
            "fechavencimiento": "2026-01-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_listar_y_obtener_documentos(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    client.post(
        f"/api/v1/documents/units/{unidad.idunidad}",
        json={
            "nombre": "Certificado importación",
            "urlarchivo": "https://storage.local/ci.pdf",
            "tipodocumento": "certificado_importacion",
        },
        headers=auth_headers,
    )

    listado = client.get(f"/api/v1/documents/units/{unidad.idunidad}", headers=auth_headers)
    assert listado.status_code == 200, listado.text
    assert listado.json()["total"] == 1
    iddocumento = listado.json()["items"][0]["iddocumento"]

    detalle = client.get(f"/api/v1/documents/{iddocumento}", headers=auth_headers)
    assert detalle.status_code == 200
    assert detalle.json()["iddocumento"] == iddocumento

    # Listado global con filtro por tipo.
    filtrado = client.get(
        f"/api/v1/documents?tipodocumento=certificado_importacion", headers=auth_headers
    )
    assert filtrado.status_code == 200
    assert filtrado.json()["total"] == 1


def test_verificar_integridad_documento(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    creado = client.post(
        f"/api/v1/documents/units/{unidad.idunidad}",
        json={
            "nombre": "Informe",
            "urlarchivo": "https://storage.local/i.pdf",
            "tipodocumento": "informe_tecnico",
            "contenido": "informe-original",
        },
        headers=auth_headers,
    ).json()
    iddocumento = creado["iddocumento"]

    ok = client.post(
        f"/api/v1/documents/{iddocumento}/verify",
        json={"contenido": "informe-original"},
        headers=auth_headers,
    )
    assert ok.status_code == 200
    assert ok.json()["coincide"] is True

    alterado = client.post(
        f"/api/v1/documents/{iddocumento}/verify",
        json={"contenido": "informe-alterado"},
        headers=auth_headers,
    )
    assert alterado.status_code == 200
    assert alterado.json()["coincide"] is False


def test_eliminar_documento(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    creado = client.post(
        f"/api/v1/documents/units/{unidad.idunidad}",
        json={
            "nombre": "Temporal",
            "urlarchivo": "https://storage.local/t.pdf",
            "tipodocumento": "informe_tecnico",
        },
        headers=auth_headers,
    ).json()
    iddocumento = creado["iddocumento"]

    borrado = client.delete(f"/api/v1/documents/{iddocumento}", headers=auth_headers)
    assert borrado.status_code == 204

    assert client.get(f"/api/v1/documents/{iddocumento}", headers=auth_headers).status_code == 404


def test_documento_otro_tenant_devuelve_404(client, db_session, setup_test_data, auth_headers):
    from datetime import date

    t2 = setup_test_data["tenant2"]
    unidad = _crear_unidad(db_session, t2)

    documento = DocumentoUnidad(
        idunidad=unidad.idunidad,
        nombre="Ajeno",
        urlarchivo="https://storage.local/a.pdf",
        hasharchivo="f" * 64,
        fechaemision=date(2026, 1, 1),
        tipodocumento="informe_tecnico",
    )
    db_session.add(documento)
    db_session.commit()

    # user1 (empresa activa tenant1) no puede ver el documento de tenant2
    ajeno = client.get(f"/api/v1/documents/{documento.iddocumento}", headers=auth_headers)
    assert ajeno.status_code == 404


def test_documentos_sin_token(client, setup_test_data):
    resp = client.get("/api/v1/documents")
    assert resp.status_code in (401, 403)
