"""Tests de Control de Errores de Integridad Referencial - 409 Conflict (Prompt 6).

Verifica que las operaciones DELETE devuelvan HTTP 409 Conflict en lugar de 500
cuando existan registros relacionados (llaves foráneas):
1. DELETE /actors/{id} con compras o unidades asociadas -> 409 Conflict.
2. DELETE /units/{id} con códigos QR asociados -> 409 Conflict.
3. DELETE /categories/{id} con productos asociados -> 409 Conflict.
4. DELETE /locations/{id} con unidades asociadas -> 409 Conflict.
"""
import time
import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cu001_tenants.tenant import Tenant
from app.models.cu002_usuarios.user import User
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.models.cu003_roles_permisos.role import Role
from app.models.cu003_roles_permisos.usuario_tenant_rol import UsuarioTenantRol
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu009_categorias.category import Categoria
from app.models.cu010_ordenes_compra.purchase import Compra
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu016_codigos_qr.qr_code import CodigoQR
from app.packages.p4_trazabilidad.models.cu023_reporte_sospecha.suspicion_report import ReporteSospecha
from app.core.security import hash_password


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def integrity_setup(client, db_session: Session):
    """Configuración para pruebas de integridad referencial con credenciales de SuperAdmin."""
    rol_super = db_session.execute(select(Role).where(Role.nombrerol == "SuperAdministrador")).scalars().first()
    if not rol_super:
        rol_super = Role(nombrerol="SuperAdministrador", descripcion="Super Admin")
        db_session.add(rol_super)
        db_session.flush()

    t = db_session.execute(select(Tenant).where(Tenant.nit == "NIT-INT-409")).scalars().first()
    if not t:
        t = Tenant(nombre="Integrity Tenant", razonsocial="Integrity SA", nit="NIT-INT-409", email="int409@test.com", activo=True)
        db_session.add(t)
        db_session.flush()

    u = db_session.execute(select(User).where(User.email == "admin@int409.com")).scalars().first()
    if not u:
        u = User(nombrecompleto="Admin Integrity", email="admin@int409.com", contrasenahash=hash_password("Pass123!"), activo=True)
        db_session.add(u)
        db_session.flush()
    else:
        u.contrasenahash = hash_password("Pass123!")
        u.activo = True

    ut = db_session.execute(select(UsuarioTenant).where(
        UsuarioTenant.idusuario == u.idusuario,
        UsuarioTenant.idtenant == t.idtenant
    )).scalars().first()
    if not ut:
        ut = UsuarioTenant(idusuario=u.idusuario, idtenant=t.idtenant)
        db_session.add(ut)
        db_session.flush()

    for r_name in ["SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones"]:
        r_obj = db_session.execute(select(Role).where(Role.nombrerol == r_name)).scalars().first()
        if not r_obj:
            r_obj = Role(nombrerol=r_name, descripcion=r_name)
            db_session.add(r_obj)
            db_session.flush()
        utr = db_session.execute(select(UsuarioTenantRol).where(
            UsuarioTenantRol.idusuariotenant == ut.idusuariotenant,
            UsuarioTenantRol.idrol == r_obj.idrol
        )).scalars().first()
        if not utr:
            db_session.add(UsuarioTenantRol(idusuariotenant=ut.idusuariotenant, idrol=r_obj.idrol))

    db_session.commit()

    login_res = client.post("/api/v1/auth/login", json={
        "tenant_slug": "integrity-tenant",
        "email": "admin@int409.com",
        "password": "Pass123!"
    })
    assert login_res.status_code == 200, f"Error login: {login_res.text}"
    token = login_res.json()["access_token"]

    return {
        "tenant": t,
        "token": token
    }


def test_delete_actor_con_dependientes_retorna_409(client, db_session, integrity_setup):
    """DELETE /actors/{id} debe devolver 409 Conflict si tiene compras o dependientes."""
    unique_suffix = int(time.time() * 1000)
    t = integrity_setup["tenant"]

    actor = ActorCadena(
        idtenant=t.idtenant,
        nombre=f"Proveedor Dep {unique_suffix}",
        tipoactor="PROVEEDOR_EEUU",
        email=f"proveedor_{unique_suffix}@dep.com"
    )
    db_session.add(actor)
    db_session.commit()

    # Crear una compra que dependa del actor como proveedor (FK NOT NULL)
    compra = Compra(
        idtenant=t.idtenant,
        idproveedor=actor.idactor,
        numeroorden=f"ORD-ACTOR-{unique_suffix}",
        fechacompra=date.today(),
        totalusd=Decimal("500.00"),
        estado="pendiente"
    )
    db_session.add(compra)
    db_session.commit()

    # Intentar eliminar el actor con dependientes
    resp = client.delete(f"/api/v1/actors/{actor.idactor}", headers=_auth_header(integrity_setup["token"]))
    assert resp.status_code == 409
    assert "registros relacionados" in resp.json()["detail"].lower()


def test_delete_unit_con_dependientes_retorna_409(client, db_session, integrity_setup):
    """DELETE /units/{id} debe devolver 409 Conflict si tiene códigos QR o dependientes."""
    unique_suffix = int(time.time() * 1000)
    t = integrity_setup["tenant"]

    cat = db_session.execute(select(Categoria)).scalars().first()
    if not cat:
        cat = Categoria(nombrecategoria="Cat Unit Test", descripcion="Cat")
        db_session.add(cat)
        db_session.commit()

    prod = Producto(nombre=f"Prod Unit {unique_suffix}", modelo="MOD-U409", idcategoria=cat.idcategoria)
    db_session.add(prod)
    db_session.commit()

    var = VarianteProducto(idproducto=prod.idproducto, sku=f"SKU-U409-{unique_suffix}", preciousd=799.0)
    db_session.add(var)
    db_session.commit()

    unit = UnidadProducto(
        idtenant=t.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-DEP-{unique_suffix}",
        estado="disponible"
    )
    db_session.add(unit)
    db_session.commit()

    # Reporte de sospecha dependiente de la unidad (FK NOT NULL y sin CASCADE)
    rep = ReporteSospecha(
        idtenant=t.idtenant,
        idunidad=unit.idunidad,
        codigoticket=f"TCK-{unique_suffix}"[:30],
        tipoanomalia="fraude_autenticidad",
        descripcion="Unidad reportada como sospechosa",
        estado="pendiente",
        gravedad="alta"
    )
    db_session.add(rep)
    db_session.commit()

    # Intentar eliminar la unidad con reporte dependiente
    resp = client.delete(f"/api/v1/units/{unit.idunidad}", headers=_auth_header(integrity_setup["token"]))
    assert resp.status_code == 409
    assert "registros relacionados" in resp.json()["detail"].lower()


def test_delete_category_con_dependientes_retorna_409(client, db_session, integrity_setup):
    """DELETE /categories/{id} debe devolver 409 Conflict si tiene productos asociados."""
    unique_suffix = int(time.time() * 1000)

    cat = Categoria(
        nombrecategoria=f"Categoria Dep {unique_suffix}",
        descripcion="Categoría con productos asociados"
    )
    db_session.add(cat)
    db_session.commit()

    # Producto dependiente de la categoría (FK NOT NULL)
    prod = Producto(
        nombre=f"iPhone Cat {unique_suffix}",
        modelo="MOD-CAT409",
        idcategoria=cat.idcategoria
    )
    db_session.add(prod)
    db_session.commit()

    # Intentar eliminar la categoría con productos
    resp = client.delete(f"/api/v1/categories/{cat.idcategoria}", headers=_auth_header(integrity_setup["token"]))
    assert resp.status_code == 409
    assert "registros relacionados" in resp.json()["detail"].lower()


def test_delete_location_con_dependientes_retorna_409(client, db_session, integrity_setup):
    """DELETE /locations/{id} debe devolver 409 Conflict si tiene unidades en custodia."""
    unique_suffix = int(time.time() * 1000)
    t = integrity_setup["tenant"]

    loc = Ubicacion(
        idtenant=t.idtenant,
        nombre=f"Almacén Central {unique_suffix}",
        tipo="almacen"
    )
    db_session.add(loc)
    db_session.commit()

    cat = db_session.execute(select(Categoria)).scalars().first()
    prod = Producto(nombre=f"Prod Loc {unique_suffix}", modelo="MOD-L409", idcategoria=cat.idcategoria)
    db_session.add(prod)
    db_session.commit()

    var = VarianteProducto(idproducto=prod.idproducto, sku=f"SKU-L409-{unique_suffix}", preciousd=999.0)
    db_session.add(var)
    db_session.commit()

    # Unidad ubicada en esta ubicación
    unit = UnidadProducto(
        idtenant=t.idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-LOCDEP-{unique_suffix}",
        idubicacionactual=loc.idubicacion,
        estado="disponible"
    )
    db_session.add(unit)
    db_session.commit()

    # Intentar eliminar la ubicación con unidades vinculadas
    resp = client.delete(f"/api/v1/locations/{loc.idubicacion}", headers=_auth_header(integrity_setup["token"]))
    assert resp.status_code == 409
    assert "registros relacionados" in resp.json()["detail"].lower()
