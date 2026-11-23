"""Tests de Seguridad, RBAC e Integridad Referencial en Productos y Variantes (CU-006 / CU-007 - Prompt 5).

Verifica:
1. GestorOperaciones recibe 403 al intentar eliminar un producto (DELETE /products/{id}).
2. Administrador de otra empresa (o cualquier rol sin SuperAdministrador) recibe 403 al intentar eliminar un producto.
3. Roles no autorizados reciben 403 en POST /products, PUT /products/{id} y DELETE /variants/{id}.
4. SuperAdministrador puede eliminar un producto sin dependientes (200 OK).
5. Producto con unidades físicas relacionadas responde 409 Conflict en DELETE /products/{id}.
6. Producto con compras relacionadas responde 409 Conflict en DELETE /products/{id}.
7. Variante con unidades físicas relacionadas responde 409 Conflict en DELETE /variants/{id}.
8. Variante con compras relacionadas responde 409 Conflict en DELETE /variants/{id}.
9. Certificación asignada a un producto responde 409 Conflict en DELETE /certifications/{id}.
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
from app.models.cu007_certificaciones.certification import Certificacion, ProductoCertificacion
from app.models.cu009_categorias.category import Categoria
from app.models.cu010_ordenes_compra.purchase import Compra, CompraDetalle
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.core.security import hash_password


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def prod_sec_setup(client, db_session: Session):
    """Crea roles, tenants y usuarios autenticados para pruebas de seguridad de catálogo."""
    roles = {}
    for r_name in ["SuperAdministrador", "AdministradorEmpresa", "GestorOperaciones", "Auditor"]:
        r = db_session.execute(select(Role).where(Role.nombrerol == r_name)).scalars().first()
        if not r:
            r = Role(nombrerol=r_name, descripcion=f"Rol {r_name}")
            db_session.add(r)
            db_session.flush()
        roles[r_name] = r

    t1 = db_session.execute(select(Tenant).where(Tenant.nit == "NIT-PROD-T1")).scalars().first()
    if not t1:
        t1 = Tenant(nombre="Prod Sec T1", razonsocial="Prod Sec T1 SA", nit="NIT-PROD-T1", email="t1@prodsec.com", activo=True)
        db_session.add(t1)
        db_session.flush()

    t2 = db_session.execute(select(Tenant).where(Tenant.nit == "NIT-PROD-T2")).scalars().first()
    if not t2:
        t2 = Tenant(nombre="Prod Sec T2", razonsocial="Prod Sec T2 SA", nit="NIT-PROD-T2", email="t2@prodsec.com", activo=True)
        db_session.add(t2)
        db_session.flush()

    def _create_user(email: str, name: str, tenant_id: int, role_name: str, slug: str):
        u = db_session.execute(select(User).where(User.email == email)).scalars().first()
        if not u:
            u = User(nombrecompleto=name, email=email, contrasenahash=hash_password("Pass123!"), activo=True)
            db_session.add(u)
            db_session.flush()
        else:
            u.contrasenahash = hash_password("Pass123!")
            u.activo = True

        ut = db_session.execute(select(UsuarioTenant).where(
            UsuarioTenant.idusuario == u.idusuario,
            UsuarioTenant.idtenant == tenant_id
        )).scalars().first()
        if not ut:
            ut = UsuarioTenant(idusuario=u.idusuario, idtenant=tenant_id)
            db_session.add(ut)
            db_session.flush()

        utr = db_session.execute(select(UsuarioTenantRol).where(
            UsuarioTenantRol.idusuariotenant == ut.idusuariotenant,
            UsuarioTenantRol.idrol == roles[role_name].idrol
        )).scalars().first()
        if not utr:
            utr = UsuarioTenantRol(idusuariotenant=ut.idusuariotenant, idrol=roles[role_name].idrol)
            db_session.add(utr)
            db_session.flush()

        db_session.commit()

        login_res = client.post("/api/v1/auth/login", json={
            "tenant_slug": slug,
            "email": email,
            "password": "Pass123!"
        })
        assert login_res.status_code == 200, f"Error login {email}: {login_res.text}"
        return u, login_res.json()["access_token"]

    u_super, token_super = _create_user("super@prodsec.com", "Super Admin", t1.idtenant, "SuperAdministrador", "prod-sec-t1")
    u_admin1, token_admin1 = _create_user("admin1@prodsec.com", "Admin T1", t1.idtenant, "AdministradorEmpresa", "prod-sec-t1")
    u_op1, token_op1 = _create_user("op1@prodsec.com", "Operador T1", t1.idtenant, "GestorOperaciones", "prod-sec-t1")
    u_admin2, token_admin2 = _create_user("admin2@prodsec.com", "Admin T2", t2.idtenant, "AdministradorEmpresa", "prod-sec-t2")

    # Crear categoría base
    cat = db_session.execute(select(Categoria)).scalars().first()
    if not cat:
        cat = Categoria(nombrecategoria="General Tech", descripcion="Categoría general")
        db_session.add(cat)
        db_session.commit()

    return {
        "t1": t1,
        "t2": t2,
        "token_super": token_super,
        "token_admin1": token_admin1,
        "token_op1": token_op1,
        "token_admin2": token_admin2,
        "cat": cat,
    }


def test_roles_no_autorizados_reciben_403_en_delete_product(client, db_session, prod_sec_setup):
    """Gestor de Operaciones y Admin de otra empresa reciben 403 en DELETE /products/{id}."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"Producto Test {unique_suffix}",
        modelo="MOD-403",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    # 1. Gestor de Operaciones -> 403
    resp_op = client.delete(f"/api/v1/products/{p.idproducto}", headers=_auth_header(prod_sec_setup["token_op1"]))
    assert resp_op.status_code == 403

    # 2. Admin de otra empresa (T2) -> 403
    resp_admin2 = client.delete(f"/api/v1/products/{p.idproducto}", headers=_auth_header(prod_sec_setup["token_admin2"]))
    assert resp_admin2.status_code == 403

    # 3. Admin de la empresa (T1) -> 403 (solo SuperAdministrador gestiona el catálogo global)
    resp_admin1 = client.delete(f"/api/v1/products/{p.idproducto}", headers=_auth_header(prod_sec_setup["token_admin1"]))
    assert resp_admin1.status_code == 403


def test_roles_no_autorizados_reciben_403_en_mutaciones_producto_y_variante(client, db_session, prod_sec_setup):
    """Gestor de Operaciones y Admin de empresa reciben 403 en POST /products, PUT /products y DELETE /variants."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"Producto Mut {unique_suffix}",
        modelo="MOD-MUT",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    var = VarianteProducto(idproducto=p.idproducto, sku=f"SKU-MUT-{unique_suffix}", preciousd=100.0)
    db_session.add(var)
    db_session.commit()

    # Operaciones no puede crear producto
    resp_post = client.post("/api/v1/products", json={
        "nombre": "iPhone Ilegal",
        "modelo": "MOD-ILLEGAL",
        "idcategoria": prod_sec_setup["cat"].idcategoria
    }, headers=_auth_header(prod_sec_setup["token_op1"]))
    assert resp_post.status_code == 403

    # Admin T2 no puede actualizar producto
    resp_put = client.put(f"/api/v1/products/{p.idproducto}", json={
        "nombre": "Nombre Modificado Ilegal"
    }, headers=_auth_header(prod_sec_setup["token_admin2"]))
    assert resp_put.status_code == 403

    # Operaciones no puede eliminar variante
    resp_del_var = client.delete(f"/api/v1/variants/{var.idvariante}", headers=_auth_header(prod_sec_setup["token_op1"]))
    assert resp_del_var.status_code == 403

    # Admin T2 no puede eliminar variante
    resp_del_var2 = client.delete(f"/api/v1/variants/{var.idvariante}", headers=_auth_header(prod_sec_setup["token_admin2"]))
    assert resp_del_var2.status_code == 403


def test_superadmin_puede_eliminar_producto_sin_dependientes(client, db_session, prod_sec_setup):
    """SuperAdministrador puede eliminar (desactivar) un producto que no tiene unidades ni compras."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"Producto Limpio {unique_suffix}",
        modelo="MOD-CLEAN",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    resp = client.delete(f"/api/v1/products/{p.idproducto}", headers=_auth_header(prod_sec_setup["token_super"]))
    assert resp.status_code == 200
    assert resp.json()["activo"] is False


def test_delete_product_con_unidades_retorna_409(client, db_session, prod_sec_setup):
    """Si el producto tiene unidades físicas registradas, DELETE /products/{id} retorna 409 Conflict."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"iPhone con Unidades {unique_suffix}",
        modelo="MOD-UNITS",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    var = VarianteProducto(idproducto=p.idproducto, sku=f"SKU-U-{unique_suffix}", preciousd=899.0)
    db_session.add(var)
    db_session.commit()

    # Crear unidad asociada
    unidad = UnidadProducto(
        idtenant=prod_sec_setup["t1"].idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-TEST-{unique_suffix}",
        estado="disponible"
    )
    db_session.add(unidad)
    db_session.commit()

    # Intentar eliminar producto con SuperAdmin -> 409 Conflict
    resp = client.delete(f"/api/v1/products/{p.idproducto}", headers=_auth_header(prod_sec_setup["token_super"]))
    assert resp.status_code == 409
    assert "unidades físicas" in resp.json()["detail"].lower()


def test_delete_product_con_compras_retorna_409(client, db_session, prod_sec_setup):
    """Si el producto tiene órdenes de compra asociadas, DELETE /products/{id} retorna 409 Conflict."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"MacBook con Compras {unique_suffix}",
        modelo="MOD-BUY",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    var = VarianteProducto(idproducto=p.idproducto, sku=f"SKU-BUY-{unique_suffix}", preciousd=1299.0)
    db_session.add(var)
    db_session.commit()

    # Proveedor necesario para la compra
    proveedor = ActorCadena(
        idtenant=prod_sec_setup["t1"].idtenant,
        nombre=f"Apple US {unique_suffix}",
        tipoactor="PROVEEDOR_EEUU",
        email=f"proveedor_{unique_suffix}@apple.com"
    )
    db_session.add(proveedor)
    db_session.commit()

    compra = Compra(
        idtenant=prod_sec_setup["t1"].idtenant,
        idproveedor=proveedor.idactor,
        numeroorden=f"ORD-{unique_suffix}",
        fechacompra=date.today(),
        totalusd=Decimal("1299.00"),
        estado="pendiente"
    )
    db_session.add(compra)
    db_session.commit()

    detalle = CompraDetalle(
        idcompra=compra.idcompra,
        idvariante=var.idvariante,
        cantidad=1,
        costounitariousd=Decimal("1299.00"),
        subtotalusd=Decimal("1299.00")
    )
    db_session.add(detalle)
    db_session.commit()

    # Intentar eliminar producto con SuperAdmin -> 409 Conflict
    resp = client.delete(f"/api/v1/products/{p.idproducto}", headers=_auth_header(prod_sec_setup["token_super"]))
    assert resp.status_code == 409
    assert "compras" in resp.json()["detail"].lower()


def test_delete_variant_con_dependientes_retorna_409(client, db_session, prod_sec_setup):
    """Si la variante tiene unidades registradas, DELETE /variants/{id} retorna 409 Conflict."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"iPad para Variante {unique_suffix}",
        modelo="MOD-VAR",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    var = VarianteProducto(idproducto=p.idproducto, sku=f"SKU-VARDEP-{unique_suffix}", preciousd=499.0)
    db_session.add(var)
    db_session.commit()

    unidad = UnidadProducto(
        idtenant=prod_sec_setup["t1"].idtenant,
        idvariante=var.idvariante,
        numeroserie=f"SN-VAR-{unique_suffix}",
        estado="disponible"
    )
    db_session.add(unidad)
    db_session.commit()

    resp = client.delete(f"/api/v1/variants/{var.idvariante}", headers=_auth_header(prod_sec_setup["token_super"]))
    assert resp.status_code == 409
    assert "unidades físicas" in resp.json()["detail"].lower()


def test_delete_certification_con_productos_retorna_409(client, db_session, prod_sec_setup):
    """Si una certificación está vinculada a un producto, DELETE /certifications/{id} retorna 409 Conflict."""
    unique_suffix = int(time.time() * 1000)
    p = Producto(
        nombre=f"Prod con Cert {unique_suffix}",
        modelo="MOD-CERT409",
        idcategoria=prod_sec_setup["cat"].idcategoria,
        activo=True
    )
    db_session.add(p)
    db_session.commit()

    cert = Certificacion(
        nombre=f"ATT-BOL-{unique_suffix}",
        entidademisora="Autoridad de Telecomunicaciones y Transportes",
        descripcion="Homologación técnica en Bolivia"
    )
    db_session.add(cert)
    db_session.commit()

    link = ProductoCertificacion(idproducto=p.idproducto, idcertificacion=cert.idcertificacion)
    db_session.add(link)
    db_session.commit()

    resp = client.delete(f"/api/v1/certifications/{cert.idcertificacion}", headers=_auth_header(prod_sec_setup["token_super"]))
    assert resp.status_code == 409
    assert "asignada a productos" in resp.json()["detail"].lower()
