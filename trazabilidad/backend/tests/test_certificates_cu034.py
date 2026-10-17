"""CU-034 — Consultar Registros Blockchain y Certificados.

Cubre el consolidado de registros blockchain + certificaciones + documentos de
una unidad, la generación del certificado digital y la consulta pública (lectura)
por UUID.
"""

import time
import uuid as uuid_lib
from datetime import datetime

from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu007_certificaciones.certification import Certificacion, ProductoCertificacion
from app.models.cu009_categorias.category import Categoria
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu021_eventos_transporte.transport_event import EventoTrazabilidad, EventoUnidad
from app.models.cu033_blockchain.registro_blockchain import RegistroBlockchain


def login(client, tenant_slug, email, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"tenant_slug": tenant_slug, "email": email, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _crear_unidad_con_datos(db_session, tenant, user):
    suffix = int(time.time() * 1000)
    cat = Categoria(nombrecategoria=f"Cat CERT {suffix}")
    db_session.add(cat)
    db_session.flush()
    prod = Producto(
        idcategoria=cat.idcategoria, nombre=f"iPhone {suffix}", modelo="15 Pro", paisorigen="EEUU"
    )
    db_session.add(prod)
    db_session.flush()
    var = VarianteProducto(
        idproducto=prod.idproducto, sku=f"SKU-CERT-{suffix}", color="Titanio", capacidad="256GB"
    )
    db_session.add(var)
    db_session.flush()

    certificacion = Certificacion(
        nombre=f"Homologación {suffix}", entidademisora="Apple Inc.", descripcion="Certificado técnico"
    )
    db_session.add(certificacion)
    db_session.flush()
    db_session.add(
        ProductoCertificacion(
            idproducto=prod.idproducto, idcertificacion=certificacion.idcertificacion
        )
    )

    ubicacion = Ubicacion(idtenant=tenant.idtenant, nombre=f"Almacen {suffix}", tipo="almacen")
    db_session.add(ubicacion)
    db_session.flush()

    unidad = UnidadProducto(
        idtenant=tenant.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-CERT-{suffix}",
        uuidpublico=str(uuid_lib.uuid4()),
        estado="disponible",
    )
    db_session.add(unidad)
    db_session.flush()

    evento = EventoTrazabilidad(
        idtenant=tenant.idtenant,
        tipoevento="fabricacion",
        fechahora=datetime(2026, 1, 10, 12, 0, 0),
        idubicacion=ubicacion.idubicacion,
        idusuarioresponsable=user.idusuario,
        descripcion="Fabricación en origen",
        estadoverificacion="verificado",
    )
    db_session.add(evento)
    db_session.flush()
    evento.payloadhash = "a" * 64
    db_session.add(EventoUnidad(idevento=evento.idevento, idunidad=unidad.idunidad))

    db_session.add(
        RegistroBlockchain(
            idevento=evento.idevento,
            payloadhash="a" * 64,
            txhash="0x" + "b" * 64,
            blocknumber=123456,
            network="sepolia",
            chainid="11155111",
            contractaddress="0x" + "c" * 40,
            estado="confirmado",
            numeroconfirmaciones=1,
        )
    )
    db_session.commit()
    return unidad


def test_consultar_certificado_unidad(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad_con_datos(db_session, t1, setup_test_data["user1"])

    resp = client.get(f"/api/v1/certificates/units/{unidad.idunidad}", headers=auth_headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["numeroserie"] == unidad.numeroserie
    assert data["autenticidad"] == "verificado"
    assert data["total_eventos"] == 1
    assert data["registros_confirmados"] == 1
    assert len(data["eventos"]) == 1
    assert data["eventos"][0]["en_blockchain"] is True
    assert len(data["certificaciones"]) == 1
    assert data["certificaciones"][0]["nombre"].startswith("Homologación")


def test_generar_certificado_digital(client, db_session, setup_test_data, auth_headers):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad_con_datos(db_session, t1, setup_test_data["user1"])

    resp = client.get(
        f"/api/v1/certificates/units/{unidad.idunidad}/digital", headers=auth_headers
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["codigocertificado"].startswith(f"CERT-{unidad.numeroserie}-")
    assert len(data["hashcertificado"]) == 64
    assert data["total_eventos"] == 1
    assert data["eventos_verificados"] == 1
    assert data["emitido_por"]


def test_certificado_publico_por_uuid(client, db_session, setup_test_data):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad_con_datos(db_session, t1, setup_test_data["user1"])

    resp = client.get(f"/api/v1/certificates/public/{unidad.uuidpublico}")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["uuidpublico"] == unidad.uuidpublico
    assert data["producto"].startswith("iPhone")


def test_certificado_publico_uuid_inexistente(client, setup_test_data):
    resp = client.get("/api/v1/certificates/public/no-existe-uuid")
    assert resp.status_code == 404


def test_certificado_unidad_ajena(client, db_session, setup_test_data, auth_headers):
    t2 = setup_test_data["tenant2"]
    unidad = _crear_unidad_con_datos(db_session, t2, setup_test_data["user2"])

    resp = client.get(f"/api/v1/certificates/units/{unidad.idunidad}", headers=auth_headers)
    assert resp.status_code == 404


def test_certificado_sin_token(client, setup_test_data):
    resp = client.get("/api/v1/certificates/units/1")
    assert resp.status_code in (401, 403)


def test_certificado_sin_rol(client, db_session, setup_test_data):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad_con_datos(db_session, t1, setup_test_data["user1"])

    headers = login(client, "empresa-test-1", "user1@test.com", "MiClave@123")
    resp = client.get(f"/api/v1/certificates/units/{unidad.idunidad}", headers=headers)
    assert resp.status_code == 403
