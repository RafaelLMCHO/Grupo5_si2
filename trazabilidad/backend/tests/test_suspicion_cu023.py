"""CU-023 — Reportar Sospecha de Falsificación (endpoint público).

Un consumidor (o visitante anónimo) reporta una unidad sospechosa; el sistema
crea una Alerta de tipo `fraude_autenticidad` para la empresa propietaria y
notifica a sus responsables operativos.
"""

import time
import uuid as uuid_lib

from sqlalchemy import select

from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.models.cu005_bitacora.notification import Notificacion
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu009_categorias.category import Categoria
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.models.cu021_eventos_transporte.transport_event import Alerta


def _crear_unidad(db_session, tenant, con_qr=True):
    suffix = int(time.time() * 1000)
    cat = Categoria(nombrecategoria=f"Cat RP {suffix}")
    db_session.add(cat)
    db_session.flush()
    prod = Producto(
        idcategoria=cat.idcategoria, nombre=f"Producto RP {suffix}", modelo="M-RP", paisorigen="EEUU"
    )
    db_session.add(prod)
    db_session.flush()
    var = VarianteProducto(idproducto=prod.idproducto, sku=f"SKU-RP-{suffix}", color="Negro", capacidad="128GB")
    db_session.add(var)
    db_session.flush()
    uuid_publico = str(uuid_lib.uuid4())
    unidad = UnidadProducto(
        idtenant=tenant.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-RP-{suffix}",
        uuidpublico=uuid_publico,
        estado="disponible",
    )
    db_session.add(unidad)
    db_session.flush()
    if con_qr:
        db_session.add(
            CodigoQR(
                idunidad=unidad.idunidad,
                tokenpublico=f"tok-rp-{suffix}",
                url=f"https://example.com/trace/{uuid_publico}",
                activo=True,
            )
        )
    db_session.commit()
    return unidad


def test_reportar_sospecha_crea_alerta(client, db_session, setup_test_data):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1)

    resp = client.post(
        "/api/v1/reports/suspicion",
        json={
            "uuidpublico": unidad.uuidpublico,
            "motivo": "producto_falso",
            "descripcion": "El empaque no coincide con el original",
            "evidencia": "https://example.com/foto.jpg",
            "nombrereportante": "Juan Perez",
            "contactoreportante": "juan@example.com",
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["tipoalerta"] == "fraude_autenticidad"
    assert data["estado"] == "pendiente"
    assert data["referencia"].startswith("REP-")

    alerta = db_session.execute(
        select(Alerta).where(Alerta.idalerta == data["idalerta"])
    ).scalar_one()
    assert alerta.idtenant == t1.idtenant
    assert alerta.idunidad == unidad.idunidad
    assert alerta.gravedad == "alta"
    assert "producto_falso" in alerta.descripcion


def test_reportar_sospecha_por_numeroserie(client, db_session, setup_test_data):
    t1 = setup_test_data["tenant1"]
    unidad = _crear_unidad(db_session, t1, con_qr=False)

    resp = client.post(
        "/api/v1/reports/suspicion",
        json={"numeroserie": unidad.numeroserie, "motivo": "serial_duplicado"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["estado"] == "pendiente"


def test_reportar_unidad_no_encontrada(client, db_session, setup_test_data):
    resp = client.post(
        "/api/v1/reports/suspicion",
        json={"uuidpublico": "uuid-inexistente", "motivo": "producto_falso"},
    )
    assert resp.status_code == 404


def test_reportar_sin_identificador(client, setup_test_data):
    resp = client.post(
        "/api/v1/reports/suspicion",
        json={"motivo": "producto_falso"},
    )
    assert resp.status_code == 400


def test_reportar_notifica_responsables(client, db_session, setup_test_data):
    t1 = setup_test_data["tenant1"]
    u1 = setup_test_data["user1"]
    unidad = _crear_unidad(db_session, t1)

    rol = db_session.execute(
        select(Role).where(Role.nombrerol == "AdministradorEmpresa")
    ).scalar_one_or_none()
    if not rol:
        rol = Role(nombrerol="AdministradorEmpresa", descripcion="Admin empresa (test)")
        db_session.add(rol)
        db_session.flush()

    from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant

    idut = db_session.execute(
        select(UsuarioTenant.idusuariotenant).where(
            UsuarioTenant.idusuario == u1.idusuario,
            UsuarioTenant.idtenant == t1.idtenant,
        )
    ).scalar_one()
    db_session.add(UsuarioTenantRol(idusuariotenant=idut, idrol=rol.idrol))
    db_session.commit()

    resp = client.post(
        "/api/v1/reports/suspicion",
        json={"uuidpublico": unidad.uuidpublico, "motivo": "producto_falso"},
    )
    assert resp.status_code == 201, resp.text

    notifs = db_session.execute(
        select(Notificacion).where(Notificacion.idusuariotenant == idut)
    ).scalars().all()
    assert len(notifs) == 1
    assert "falsificación" in notifs[0].titulo.lower()
