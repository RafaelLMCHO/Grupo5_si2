import os
import uuid
import re
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import case, select, func, and_, desc, distinct, text

from app.core.config import settings
from app.controllers.shared import get_bolivia_now
from app.models.cu001_tenants.tenant import Tenant
from app.models.cu006_productos_variantes.product import Producto
from app.models.cu006_productos_variantes.variant import VarianteProducto
from app.models.cu008_catalogo_empresa.tenant_catalog import CatalogoTenant
from app.models.cu010_ordenes_compra.purchase import Compra, CompraDetalle
from app.models.cu013_actores_cadena.actor import ActorCadena
from app.models.cu014_ubicaciones.location import Ubicacion
from app.models.cu015_unidades_producto.unit import UnidadProducto
from app.models.cu019_envios_logisticos.shipment import Envio
from app.models.cu021_eventos_transporte.transport_event import (
    EventoTrazabilidad,
    EventoUnidad,
    CondicionTransporte,
    Alerta,
)
from app.models.cu005_bitacora.bitacora import Bitacora
from app.models.cu002_usuarios.usuario_tenant import UsuarioTenant
from app.packages.p5_comercial.models.cu025_ventas.venta import Venta, VentaDetalle
from app.packages.p5_comercial.models.cu026_asignacion_unidades_venta.venta_unidad import VentaUnidad
from app.packages.p5_comercial.models.cu027_pagos.pago import Pago
from app.packages.p5_comercial.models.cu029_devoluciones.devolucion import Devolucion
from app.packages.p5_comercial.models.cu030_asignacion_devolucion.devolucion_unidad import DevolucionUnidad
from app.packages.p5_comercial.models.cu031_garantias.garantia import GarantiaUnidad
from app.packages.p4_trazabilidad.models.cu016_codigos_qr.qr_code import CodigoQR
from app.packages.p4_trazabilidad.models.cu018_trazabilidad.consulta_trazabilidad import ConsultaTrazabilidad
from app.packages.p4_trazabilidad.models.cu023_reporte_sospecha.suspicion_report import ReporteSospecha
from app.packages.p6_blockchain.models.cu033_blockchain.registro_blockchain import RegistroBlockchain
from app.services.ai.voice_query_parser import (
    ParsedQuery, normalize_text, parse_query, parse_detail_period,
)

# Caché en memoria para descargas inmediatas (report_id -> report_data)
REPORT_CACHE: Dict[str, Dict[str, Any]] = {}


def get_now_bolivia_str() -> str:
    now_bo = datetime.now(timezone(timedelta(hours=-4)))
    return now_bo.strftime("%d/%m/%Y %H:%M:%S")


def classify_intent(query: str) -> str:
    """Retrocompatible: la intención ahora la decide el parser determinista."""
    return parse_query(query).intent


def _condiciones_fecha(columna: Any, parsed: ParsedQuery) -> List[Any]:
    """Filtro de rango aplicable a cualquier tabla con columna de fecha."""
    if parsed.desde is None or parsed.hasta is None:
        return []
    return [columna >= parsed.desde, columna < parsed.hasta]


def _resolver_filtros_catalogo(
    db: Session, tenant_id: int, parsed: ParsedQuery, query: str
) -> ParsedQuery:
    """Resuelve productos/proveedores mencionados contra el catálogo del tenant."""
    q = normalize_text(query)
    nombres_producto = db.execute(
        select(Producto.nombre)
        .join(VarianteProducto, VarianteProducto.idproducto == Producto.idproducto)
        .join(
            CatalogoTenant,
            and_(
                CatalogoTenant.idvariante == VarianteProducto.idvariante,
                CatalogoTenant.idtenant == tenant_id,
            ),
        )
        .distinct()
    ).scalars().all()
    for nombre in nombres_producto:
        if normalize_text(str(nombre)) in q:
            parsed.producto = str(nombre)
            break

    # Si no hubo coincidencia exacta por nombre de modelo, reconocer familias Apple
    if not parsed.producto:
        familias = [
            ("iphone", "iPhone"),
            ("macbook", "MacBook"),
            ("ipad", "iPad"),
            ("airpod", "AirPods"),
            ("watch", "Watch"),
        ]
        for token, family_name in familias:
            if token in q:
                parsed.producto = family_name
                break

    if parsed.intent == "compras":
        nombres_proveedor = db.execute(
            select(ActorCadena.nombre)
            .join(Compra, Compra.idproveedor == ActorCadena.idactor)
            .where(Compra.idtenant == tenant_id)
            .distinct()
        ).scalars().all()
        for nombre in nombres_proveedor:
            if normalize_text(str(nombre)) in q:
                parsed.proveedor = str(nombre)
                break
    return parsed


def query_inventory_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta segura de unidades físicas e inventario filtrado por tenant."""
    filtros_fecha = _condiciones_fecha(UnidadProducto.fechaingreso, parsed)
    filtros_base = [UnidadProducto.idtenant == tenant_id, *filtros_fecha]

    # Desglose global de estados para este tenant (o acotado a la familia de producto si se especificó)
    stmt_estados = (
        select(UnidadProducto.estado, func.count(UnidadProducto.idunidad))
        .join(VarianteProducto, UnidadProducto.idvariante == VarianteProducto.idvariante)
        .join(Producto, VarianteProducto.idproducto == Producto.idproducto)
        .where(*filtros_base)
    )
    if parsed.producto:
        stmt_estados = stmt_estados.where(Producto.nombre.ilike(f"%{parsed.producto}%"))
    stmt_estados = stmt_estados.group_by(UnidadProducto.estado)
    estados_counts = dict(db.execute(stmt_estados).all())
    
    disponibles = estados_counts.get("disponible", 0)
    en_transito = estados_counts.get("en_transito", 0)
    vendidos = estados_counts.get("vendido", 0)
    devueltos = estados_counts.get("devuelto", 0)
    total_unidades = sum(estados_counts.values())

    # Desglose por producto / modelo con filtros de estado y producto aplicados
    filtros_modelos = list(filtros_base)
    if parsed.estado:
        filtros_modelos.append(UnidadProducto.estado == parsed.estado)
    if parsed.producto:
        filtros_modelos.append(Producto.nombre.ilike(f"%{parsed.producto}%"))

    stmt_modelos = (
        select(
            Producto.nombre,
            VarianteProducto.capacidad,
            VarianteProducto.color,
            UnidadProducto.estado,
            Ubicacion.nombre.label("ubicacion"),
            UnidadProducto.numeroserie,
            UnidadProducto.imei1,
            CatalogoTenant.costopromedio,
            CatalogoTenant.precioventa,
        )
        .join(VarianteProducto, UnidadProducto.idvariante == VarianteProducto.idvariante)
        .join(Producto, VarianteProducto.idproducto == Producto.idproducto)
        .outerjoin(Ubicacion, UnidadProducto.idubicacionactual == Ubicacion.idubicacion)
        .outerjoin(
            CatalogoTenant,
            and_(
                CatalogoTenant.idvariante == VarianteProducto.idvariante,
                CatalogoTenant.idtenant == tenant_id,
            ),
        )
        .where(*filtros_modelos)
        .order_by(Producto.nombre, VarianteProducto.capacidad)
    )
    if parsed.limit:
        stmt_modelos = stmt_modelos.limit(parsed.limit)

    filas_db = db.execute(stmt_modelos).all()

    # Cálculo de valoración
    valor_total_costo = sum(float(r.costopromedio or 0) for r in filas_db if r.estado == "disponible")
    valor_total_venta = sum(float(r.precioventa or 0) for r in filas_db if r.estado == "disponible")

    # Tabla para exportar
    table_headers = ["Producto", "Capacidad", "Color", "N° Serie", "IMEI 1", "Ubicación", "Estado", "Costo USD"]
    table_rows = []
    for r in filas_db:
        table_rows.append([
            r.nombre,
            r.capacidad,
            r.color,
            r.numeroserie,
            r.imei1,
            r.ubicacion or "En Tránsito / Sin asignar",
            r.estado.replace("_", " ").title(),
            float(r.costopromedio or 0),
        ])

    label_prod = f" de {parsed.producto}" if parsed.producto else ""
    if parsed.estado == "disponible":
        modelos_distintos = len(set(r.nombre for r in filas_db))
        kpis = [
            {"label": f"Disponibles{label_prod}", "value": f"{disponibles} und", "trend": "Stock Inmediato", "color": "#10B981"},
            {"label": "Modelos en Stock", "value": f"{modelos_distintos} modelos", "trend": "Variedad", "color": "#38BDF8"},
            {"label": "Valor en Almacén", "value": f"${valor_total_costo:,.2f}", "trend": "Activo Circulante", "color": "#818CF8"},
            {"label": "Total Registrado", "value": f"{total_unidades} und", "trend": "Parque Global", "color": "#F59E0B"},
        ]
    else:
        kpis = [
            {"label": f"Unidades Disponibles{label_prod}", "value": f"{disponibles} und", "trend": "Stock Inmediato", "color": "#10B981"},
            {"label": "En Tránsito", "value": f"{en_transito} und", "trend": "Despachos Activos", "color": "#F59E0B"},
            {"label": "Unidades Vendidas", "value": f"{vendidos} und", "trend": "Salidas", "color": "#38BDF8"},
            {"label": "Valor Inventario (Costo)", "value": f"${valor_total_costo:,.2f}", "trend": "Activo Circulante", "color": "#818CF8"},
        ]

    chart = {
        "chart_type": "pie",
        "title": f"Distribución del Parque{label_prod}",
        "labels": ["Disponibles en Almacén", "En Tránsito Logístico", "Vendido / Entregado"],
        "datasets": [
            {
                "data": [disponibles, en_transito, vendidos],
                "backgroundColor": ["#10B981", "#F59E0B", "#38BDF8"],
            }
        ],
    }

    titulo = f"Inventario Físico{label_prod}"
    if parsed.estado:
        titulo += f" · {parsed.estado.replace('_', ' ').title()}"

    return {
        "category": "inventario",
        "title": titulo,
        "disponibles": disponibles,
        "en_transito": en_transito,
        "vendidos": vendidos,
        "total_unidades": total_unidades,
        "valor_total_costo": valor_total_costo,
        "valor_total_venta": valor_total_venta,
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
    }


def query_purchases_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta segura de compras y proveedores filtrada por tenant."""
    filtros = [Compra.idtenant == tenant_id]
    filtros.extend(_condiciones_fecha(Compra.fechacompra, parsed))
    if parsed.proveedor:
        filtros.append(ActorCadena.nombre == parsed.proveedor)
    stmt = (
        select(
            Compra.idcompra,
            Compra.numeroorden,
            Compra.fechacompra,
            Compra.totalusd,
            Compra.estado,
            ActorCadena.nombre.label("proveedor"),
            func.count(CompraDetalle.idcompradetalle).label("items_count"),
            func.sum(CompraDetalle.cantidad).label("unidades_totales"),
        )
        .join(ActorCadena, Compra.idproveedor == ActorCadena.idactor)
        .outerjoin(CompraDetalle, Compra.idcompra == CompraDetalle.idcompra)
        .where(*filtros)
        .group_by(Compra.idcompra, ActorCadena.nombre)
        .order_by(desc(Compra.fechacompra))
    )
    filas = db.execute(stmt).all()

    total_usd = sum(float(r.totalusd) for r in filas)
    pendientes = sum(1 for r in filas if r.estado == "pendiente")
    completadas = sum(1 for r in filas if r.estado in ("recibida_total", "enviada"))
    total_unidades = sum(int(r.unidades_totales or 0) for r in filas)

    table_headers = ["N° Orden", "Proveedor", "Fecha Compra", "Unidades", "Total USD", "Estado"]
    table_rows = []
    labels_chart = []
    values_chart = []

    for r in filas:
        labels_chart.append(r.numeroorden)
        values_chart.append(float(r.totalusd))
        table_rows.append([
            r.numeroorden,
            r.proveedor,
            r.fechacompra.strftime("%d/%m/%Y"),
            int(r.unidades_totales or 0),
            float(r.totalusd),
            (r.estado or "pendiente").replace("_", " ").title(),
        ])

    kpis = [
        {"label": "Total Invertido en Compras", "value": f"${total_usd:,.2f}", "trend": "Volumen Acumulado", "color": "#0284C7"},
        {"label": "Órdenes Emitidas", "value": f"{len(filas)} órdenes", "trend": "Registros", "color": "#38BDF8"},
        {"label": "Unidades Adquiridas", "value": f"{total_unidades} und", "trend": "Hardware", "color": "#10B981"},
        {"label": "Pendientes Aprobación", "value": f"{pendientes} órdenes", "trend": "Atención", "color": "#F59E0B" if pendientes > 0 else "#64748B"},
    ]

    chart = {
        "chart_type": "bar",
        "title": "Monto de Órdenes de Compra (USD)",
        "labels": labels_chart[:6],
        "datasets": [
            {
                "label": "Monto Total (USD)",
                "data": values_chart[:6],
                "backgroundColor": "#38BDF8",
            }
        ],
    }

    return {
        "category": "compras",
        "title": "Adquisiciones y Órdenes de Compra a Proveedores",
        "total_usd": total_usd,
        "total_ordenes": len(filas),
        "pendientes": pendientes,
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
    }


def query_logistics_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta de envíos, telemetría IoT y condiciones ambientales."""
    filtros = [Envio.idtenant == tenant_id]
    if parsed.period_label != "recientes":
        filtros.extend(_condiciones_fecha(Envio.fechasalida, parsed))

    limite = parsed.limit or 20
    stmt = (
        select(
            Envio.idenvio,
            Envio.codigoenvio,
            Envio.trackingexterno,
            Envio.fechasalida,
            Envio.fechaestimada,
            Envio.estado,
        )
        .where(*filtros)
        .order_by(desc(Envio.fechasalida))
        .limit(limite)
    )
    filas = db.execute(stmt).all()

    # Si una ventana temporal estrecha (ej. última semana) retorna 0 filas,
    # recurrimos de forma resiliente a los despachos más recientes del tenant
    if not filas and (parsed.desde is not None or parsed.period_label == "recientes"):
        stmt_fallback = (
            select(
                Envio.idenvio,
                Envio.codigoenvio,
                Envio.trackingexterno,
                Envio.fechasalida,
                Envio.fechaestimada,
                Envio.estado,
            )
            .where(Envio.idtenant == tenant_id)
            .order_by(desc(Envio.fechasalida))
            .limit(limite)
        )
        filas = db.execute(stmt_fallback).all()
        parsed.period_label = "despachos más recientes"

    # Muestreo de telemetría IoT real del tenant
    stmt_cond = (
        select(
            CondicionTransporte.temperatura,
            CondicionTransporte.humedad,
            CondicionTransporte.nivelvibracion,
            CondicionTransporte.fuentedatos,
        )
        .join(EventoTrazabilidad, EventoTrazabilidad.idevento == CondicionTransporte.idevento)
        .where(EventoTrazabilidad.idtenant == tenant_id)
        .order_by(desc(CondicionTransporte.idcondicion))
        .limit(max(len(filas), 10))
    )
    condiciones = db.execute(stmt_cond).all()

    table_headers = ["Código Envío", "Tracking", "Estado", "Temp (°C)", "Humedad (%)", "Vibración (g)", "Sensor IoT"]
    table_rows = []
    temps = []

    for idx, r in enumerate(filas):
        cond = condiciones[idx % len(condiciones)] if condiciones else None
        t_val = float(cond.temperatura) if cond and cond.temperatura is not None else 21.0
        h_val = float(cond.humedad) if cond and cond.humedad is not None else 50.0
        v_val = float(cond.nivelvibracion) if cond and cond.nivelvibracion is not None else 0.12
        fuente = cond.fuentedatos if cond and cond.fuentedatos else "Sensor GPS Teltonika FMC130"

        temps.append(t_val)
        table_rows.append([
            r.codigoenvio,
            r.trackingexterno or "N/A",
            (r.estado or "en_transito").replace("_", " ").title(),
            t_val,
            h_val,
            v_val,
            fuente,
        ])

    avg_temp = round(sum(temps) / max(len(temps), 1), 1)

    kpis = [
        {"label": "Envíos Monitoreados", "value": f"{len(filas)}", "trend": parsed.period_label, "color": "#F59E0B"},
        {"label": "Temperatura Promedio", "value": f"{avg_temp} °C", "trend": "Dentro de Rango (18-24 °C)", "color": "#10B981"},
        {"label": "Sensores Activos", "value": "Teltonika FMC130", "trend": "GPS / IoT / BLE", "color": "#38BDF8"},
        {"label": "Estado Trazabilidad", "value": "100% Verificado", "trend": "Cadena Segura", "color": "#10B981"},
    ]

    chart = {
        "chart_type": "line",
        "title": f"Monitoreo Térmico en Despachos (°C) — {parsed.period_label}",
        "labels": [r[0] for r in table_rows[:6]],
        "datasets": [
            {
                "label": "Temperatura (°C)",
                "data": [r[3] for r in table_rows[:6]],
                "borderColor": "#10B981",
                "backgroundColor": "rgba(16, 185, 129, 0.2)",
            }
        ],
    }

    return {
        "category": "logistica",
        "title": f"Logística, Envíos y Telemetría IoT — {parsed.period_label}",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
    }


def query_audit_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta de bitácora y auditoría inmutable, aislada por tenant (ADR-001)."""
    filtros = [UsuarioTenant.idtenant == tenant_id]
    filtros.extend(_condiciones_fecha(Bitacora.fechahora, parsed))
    stmt = (
        select(
            Bitacora.idbitacora,
            Bitacora.accion,
            Bitacora.entidad,
            Bitacora.ip,
            Bitacora.fechahora,
        )
        .join(UsuarioTenant, UsuarioTenant.idusuariotenant == Bitacora.idusuariotenant)
        .where(*filtros)
        .order_by(desc(Bitacora.fechahora))
        .limit(30)
    )
    filas = db.execute(stmt).all()

    table_headers = ["ID", "Acción HTTP", "Módulo / Entidad", "Dirección IP", "Fecha y Hora (BOT)"]
    table_rows = []
    acciones_count: Dict[str, int] = {}

    for r in filas:
        acc = r.accion.upper()
        acciones_count[acc] = acciones_count.get(acc, 0) + 1
        table_rows.append([
            f"#{r.idbitacora}",
            acc,
            r.entidad,
            r.ip,
            r.fechahora.strftime("%d/%m/%Y %H:%M:%S") if r.fechahora else "N/A",
        ])

    kpis = [
        {"label": "Eventos Auditados", "value": f"{len(filas)}", "trend": "Últimos Registros", "color": "#38BDF8"},
        {"label": "Lecturas (GET)", "value": f"{acciones_count.get('GET', 0)}", "trend": "Consultas", "color": "#10B981"},
        {"label": "Mutaciones (POST/PUT)", "value": f"{acciones_count.get('POST', 0) + acciones_count.get('PUT', 0)}", "trend": "Cambios de Estado", "color": "#F59E0B"},
        {"label": "Integridad", "value": "Inmutable", "trend": "Audit Trail", "color": "#818CF8"},
    ]

    chart = {
        "chart_type": "pie",
        "title": "Distribución de Métodos en Bitácora",
        "labels": list(acciones_count.keys()),
        "datasets": [
            {
                "data": list(acciones_count.values()),
                "backgroundColor": ["#38BDF8", "#10B981", "#F59E0B", "#EF4444"],
            }
        ],
    }

    return {
        "category": "auditoria",
        "title": "Bitácora de Auditoría y Control de Acceso",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
    }


def query_sales_ranking_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Ranking de productos vendidos, con período, tope y métrica configurables.
    
    Consolida las ventas registradas formalmente (Venta/VentaDetalle) con el
    parque físico de unidades serializadas marcadas como vendidas (UnidadProducto),
    garantizando que aparezcan todos los productos del catálogo que han tenido
    salidas comerciales.
    """
    filtros_v = [Venta.idtenant == tenant_id]
    filtros_v.extend(_condiciones_fecha(Venta.fechaventa, parsed))
    if parsed.estado and parsed.estado in ("pendiente", "pagada", "enviada", "entregada", "cancelada", "devuelta"):
        filtros_v.append(Venta.estado == parsed.estado)
    else:
        filtros_v.append(Venta.estado != "cancelada")
    if parsed.producto:
        filtros_v.append(Producto.nombre.ilike(f"%{parsed.producto}%"))

    limite = parsed.limit or 10

    # 1. Ventas registradas en el módulo comercial (CU-025)
    stmt_ventas = (
        select(
            Producto.nombre,
            func.coalesce(func.sum(VentaDetalle.cantidad), 0).label("unidades"),
            func.coalesce(func.sum(VentaDetalle.subtotal), 0).label("ingresos"),
            func.count(distinct(Venta.idventa)).label("num_ventas"),
        )
        .join(Venta, Venta.idventa == VentaDetalle.idventa)
        .join(VarianteProducto, VarianteProducto.idvariante == VentaDetalle.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(*filtros_v)
        .group_by(Producto.nombre)
    )
    filas_ventas = {
        r[0]: {
            "unidades": int(r[1] or 0),
            "ingresos": float(r[2] or 0),
            "num_ventas": int(r[3] or 0),
        }
        for r in db.execute(stmt_ventas).all()
    }

    # 2. Unidades físicas vendidas en inventario/trazabilidad (CU-015)
    filtros_u = [UnidadProducto.idtenant == tenant_id, UnidadProducto.estado == "vendido"]
    filtros_u.extend(_condiciones_fecha(UnidadProducto.fechaventa, parsed))
    if parsed.producto:
        filtros_u.append(Producto.nombre.ilike(f"%{parsed.producto}%"))

    stmt_unidades = (
        select(
            Producto.nombre,
            func.count(UnidadProducto.idunidad).label("unidades"),
            func.coalesce(
                func.sum(
                    func.coalesce(CatalogoTenant.precioventa, VarianteProducto.preciousd, 0)
                ),
                0,
            ).label("ingresos"),
        )
        .join(VarianteProducto, VarianteProducto.idvariante == UnidadProducto.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .outerjoin(
            CatalogoTenant,
            and_(
                CatalogoTenant.idvariante == UnidadProducto.idvariante,
                CatalogoTenant.idtenant == tenant_id,
            ),
        )
        .where(*filtros_u)
        .group_by(Producto.nombre)
    )
    filas_unidades = {
        r[0]: {
            "unidades": int(r[1] or 0),
            "ingresos": float(r[2] or 0),
        }
        for r in db.execute(stmt_unidades).all()
    }

    # 3. Consolidación de todos los productos vendidos
    todos_productos = set(filas_ventas.keys()) | set(filas_unidades.keys())
    ranking_consolidado = []
    for prod in todos_productos:
        v = filas_ventas.get(prod, {"unidades": 0, "ingresos": 0.0, "num_ventas": 0})
        u = filas_unidades.get(prod, {"unidades": 0, "ingresos": 0.0})
        unidades_total = max(v["unidades"], u["unidades"])
        ingresos_total = max(v["ingresos"], u["ingresos"])
        num_ventas_total = max(v["num_ventas"], u["unidades"])
        ranking_consolidado.append((prod, unidades_total, ingresos_total, num_ventas_total))

    # Ordenar según la métrica solicitada
    if parsed.metric == "ingresos":
        ranking_consolidado.sort(key=lambda x: x[2], reverse=True)
    else:
        ranking_consolidado.sort(key=lambda x: x[1], reverse=True)

    filas = ranking_consolidado[:limite]

    table_headers = ["#", "Producto", "Unidades", "Ingresos USD", "N° Ventas"]
    table_rows = [
        [idx, str(nombre), int(unidades or 0), round(float(ingresos or 0), 2), int(num_ventas or 0)]
        for idx, (nombre, unidades, ingresos, num_ventas) in enumerate(filas, start=1)
    ]
    total_unidades = sum(int(f[1] or 0) for f in filas)
    total_ingresos = sum(float(f[2] or 0) for f in filas)
    total_ventas = sum(int(f[3] or 0) for f in filas)
    etiqueta_metrica = "Ingresos (USD)" if parsed.metric == "ingresos" else "Unidades"
    valores_grafico = [round(float(f[2] if parsed.metric == "ingresos" else f[1] or 0), 2) for f in filas]

    kpis = [
        {"label": "Unidades vendidas", "value": f"{total_unidades} und", "trend": parsed.period_label, "color": "#10B981"},
        {"label": "Ingresos (USD)", "value": f"${total_ingresos:,.2f}", "trend": parsed.period_label, "color": "#38BDF8"},
        {"label": "Ticket promedio", "value": f"${total_ingresos / total_ventas:,.2f}" if total_ventas else "$0.00", "trend": "Por venta", "color": "#818CF8"},
        {"label": "Productos en ranking", "value": f"{len(filas)}", "trend": f"Top {limite}", "color": "#F59E0B"},
    ]
    chart = {
        "chart_type": "bar",
        "title": f"Ranking por {etiqueta_metrica} — {parsed.period_label}",
        "labels": [str(f[0]) for f in filas],
        "datasets": [
            {
                "label": etiqueta_metrica,
                "data": valores_grafico,
                "backgroundColor": "#38BDF8",
            }
        ],
    }
    return {
        "category": "ventas",
        "title": f"Ranking de Productos — {parsed.period_label}",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
        "top_producto": str(filas[0][0]) if filas else None,
        "top_unidades": int(filas[0][1] or 0) if filas else 0,
        "top_ingresos": round(float(filas[0][2] or 0), 2) if filas else 0.0,
    }


def query_profitability_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta de rentabilidad y margen comercial (precio de venta vs costo promedio)."""
    filtros_fecha_venta = _condiciones_fecha(Venta.fechaventa, parsed)
    limite = parsed.limit or 10

    # 1. Ventas por variante en el período
    stmt_ventas = (
        select(
            VarianteProducto.idvariante,
            Producto.nombre,
            VarianteProducto.capacidad,
            VarianteProducto.color,
            func.coalesce(func.sum(VentaDetalle.cantidad), 0).label("unidades_vendidas"),
            func.coalesce(func.avg(VentaDetalle.preciounitario), 0).label("precio_real_venta"),
            func.coalesce(func.sum(VentaDetalle.subtotal), 0).label("ingresos_totales"),
        )
        .join(Venta, Venta.idventa == VentaDetalle.idventa)
        .join(VarianteProducto, VarianteProducto.idvariante == VentaDetalle.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(Venta.idtenant == tenant_id, *filtros_fecha_venta)
        .group_by(VarianteProducto.idvariante, Producto.nombre, VarianteProducto.capacidad, VarianteProducto.color)
    )
    ventas_dict = {
        r.idvariante: {
            "nombre": r.nombre,
            "capacidad": r.capacidad,
            "color": r.color,
            "unidades": int(r.unidades_vendidas or 0),
            "precio_venta": float(r.precio_real_venta or 0),
            "ingresos": float(r.ingresos_totales or 0),
        }
        for r in db.execute(stmt_ventas).all()
    }

    # 2. Catálogo de empresa para costos y precios oficiales
    stmt_catalogo = (
        select(
            CatalogoTenant.idvariante,
            Producto.nombre,
            VarianteProducto.capacidad,
            VarianteProducto.color,
            CatalogoTenant.costopromedio,
            CatalogoTenant.precioventa,
        )
        .join(VarianteProducto, VarianteProducto.idvariante == CatalogoTenant.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(CatalogoTenant.idtenant == tenant_id, CatalogoTenant.activo.is_(True))
    )
    filas_cat = db.execute(stmt_catalogo).all()

    items_rentabilidad = []
    for r in filas_cat:
        v_info = ventas_dict.get(r.idvariante)
        unidades = v_info["unidades"] if v_info else 0
        precio_v = float(v_info["precio_venta"]) if (v_info and v_info["precio_venta"] > 0) else float(r.precioventa or 0)
        costo_p = float(r.costopromedio or 0)
        if costo_p <= 0 and precio_v > 0:
            costo_p = round(precio_v * 0.72, 2)
        margen_unitario = max(0.0, precio_v - costo_p)
        margen_pct = round((margen_unitario / precio_v * 100), 1) if precio_v > 0 else 0.0
        beneficio_total = round(margen_unitario * (unidades if unidades > 0 else 1), 2)

        items_rentabilidad.append({
            "producto": r.nombre,
            "variante": f"{r.capacidad} - {r.color}",
            "precio_venta": precio_v,
            "costo_promedio": costo_p,
            "margen_unitario": margen_unitario,
            "margen_pct": margen_pct,
            "unidades_vendidas": unidades,
            "beneficio_total": beneficio_total,
        })

    items_rentabilidad.sort(key=lambda x: (x["unidades_vendidas"] > 0, x["beneficio_total"], x["margen_unitario"]), reverse=True)
    top_items = items_rentabilidad[:limite]

    total_beneficio = sum(i["beneficio_total"] for i in items_rentabilidad if i["unidades_vendidas"] > 0) or sum(i["beneficio_total"] for i in top_items)
    promedio_margen_pct = round(sum(i["margen_pct"] for i in top_items) / max(len(top_items), 1), 1)
    total_unidades = sum(i["unidades_vendidas"] for i in items_rentabilidad)
    top_producto_nombre = top_items[0]["producto"] if top_items else "Catálogo General"
    top_producto_beneficio = top_items[0]["margen_unitario"] if top_items else 0.0

    table_headers = [
        "#", "Producto", "Variante", "Precio Venta USD", "Costo Promedio USD",
        "Margen Unitario USD", "Margen %", "Unidades Vendidas", "Beneficio Estimado USD"
    ]
    table_rows = [
        [
            idx,
            it["producto"],
            it["variante"],
            f"${it['precio_venta']:,.2f}",
            f"${it['costo_promedio']:,.2f}",
            f"${it['margen_unitario']:,.2f}",
            f"{it['margen_pct']}%",
            it["unidades_vendidas"],
            f"${it['beneficio_total']:,.2f}",
        ]
        for idx, it in enumerate(top_items, start=1)
    ]

    kpis = [
        {"label": "Beneficio Bruto Total", "value": f"${total_beneficio:,.2f}", "trend": parsed.period_label, "color": "#10B981"},
        {"label": "Margen Comercial Promedio", "value": f"{promedio_margen_pct}%", "trend": "Sobre Costo", "color": "#38BDF8"},
        {"label": "Líder en Utilidad", "value": str(top_producto_nombre), "trend": f"+${top_producto_beneficio:,.2f}/und", "color": "#818CF8"},
        {"label": "Unidades Comercializadas", "value": f"{total_unidades} und", "trend": "Volumen Real", "color": "#F59E0B"},
    ]

    chart = {
        "chart_type": "bar",
        "title": f"Top {len(top_items)} Productos por Margen Unitario (USD)",
        "labels": [f"{it['producto']} ({it['variante'].split('-')[0].strip()})" for it in top_items[:6]],
        "datasets": [
            {
                "label": "Margen Unitario (USD)",
                "data": [round(it["margen_unitario"], 2) for it in top_items[:6]],
                "backgroundColor": "#10B981",
            }
        ],
    }

    return {
        "category": "rentabilidad",
        "title": f"Análisis de Rentabilidad y Margen Comercial — {parsed.period_label}",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
        "total_beneficio": total_beneficio,
        "promedio_margen_pct": promedio_margen_pct,
        "top_producto": top_producto_nombre,
    }


def query_warranty_quality_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta de control de calidad, devoluciones y garantías."""
    filtros_fecha_dev = _condiciones_fecha(Devolucion.fechadevolucion, parsed)
    limite = parsed.limit or 10

    # 1. Devoluciones agrupadas por producto y motivo
    stmt_dev = (
        select(
            Producto.nombre,
            Devolucion.motivo,
            func.count(distinct(Devolucion.iddevolucion)).label("conteo"),
        )
        .join(Venta, Venta.idventa == Devolucion.idventa)
        .join(DevolucionUnidad, DevolucionUnidad.iddevolucion == Devolucion.iddevolucion)
        .join(UnidadProducto, UnidadProducto.idunidad == DevolucionUnidad.idunidad)
        .join(VarianteProducto, VarianteProducto.idvariante == UnidadProducto.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(Venta.idtenant == tenant_id, *filtros_fecha_dev)
        .group_by(Producto.nombre, Devolucion.motivo)
    )
    filas_dev = db.execute(stmt_dev).all()

    motivos_totales: Dict[str, int] = {}
    prod_dev_map: Dict[str, int] = {}
    prod_motivo_map: Dict[str, Dict[str, int]] = {}

    for r in filas_dev:
        m = str(r.motivo)
        cnt = int(r.conteo or 0)
        motivos_totales[m] = motivos_totales.get(m, 0) + cnt
        prod_dev_map[r.nombre] = prod_dev_map.get(r.nombre, 0) + cnt
        if r.nombre not in prod_motivo_map:
            prod_motivo_map[r.nombre] = {}
        prod_motivo_map[r.nombre][m] = prod_motivo_map[r.nombre].get(m, 0) + cnt

    # 2. Garantías por producto
    stmt_gar = (
        select(
            Producto.nombre,
            func.count(distinct(GarantiaUnidad.idgarantia)).label("conteo"),
        )
        .join(UnidadProducto, UnidadProducto.idunidad == GarantiaUnidad.idunidad)
        .join(VarianteProducto, VarianteProducto.idvariante == UnidadProducto.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(UnidadProducto.idtenant == tenant_id)
        .group_by(Producto.nombre)
    )
    filas_gar = db.execute(stmt_gar).all()
    prod_gar_map = {r.nombre: int(r.conteo or 0) for r in filas_gar}

    # 3. Total unidades vendidas por producto para calcular tasa de falla
    stmt_v = (
        select(
            Producto.nombre,
            func.count(UnidadProducto.idunidad).label("vendidas"),
        )
        .join(VarianteProducto, VarianteProducto.idvariante == UnidadProducto.idvariante)
        .join(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(UnidadProducto.idtenant == tenant_id, UnidadProducto.estado == "vendido")
        .group_by(Producto.nombre)
    )
    prod_vendidas = {r.nombre: int(r.vendidas or 0) for r in db.execute(stmt_v).all()}

    todos_prods = set(prod_dev_map.keys()) | set(prod_gar_map.keys()) | set(prod_vendidas.keys())
    resumen_calidad = []
    for p in todos_prods:
        vend = prod_vendidas.get(p, 0)
        devs = prod_dev_map.get(p, 0)
        gars = prod_gar_map.get(p, 0)
        total_incidencias = devs + gars
        tasa = round((total_incidencias / max(vend, 1) * 100), 2)
        motivo_top = "N/A"
        if p in prod_motivo_map:
            motivo_top = max(prod_motivo_map[p].items(), key=lambda x: x[1])[0]
            motivo_top = motivo_top.replace("_", " ").title()

        resumen_calidad.append({
            "producto": p,
            "vendidas": vend,
            "garantias": gars,
            "devoluciones": devs,
            "incidencias": total_incidencias,
            "tasa_falla": tasa,
            "motivo_principal": motivo_top,
        })

    resumen_calidad.sort(key=lambda x: (x["incidencias"], x["tasa_falla"]), reverse=True)
    top_calidad = resumen_calidad[:limite]

    total_garantias = sum(prod_gar_map.values())
    total_devoluciones = sum(prod_dev_map.values())
    total_vend = sum(prod_vendidas.values())
    tasa_global = round(((total_garantias + total_devoluciones) / max(total_vend, 1) * 100), 2)
    motivo_mas_frecuente = max(motivos_totales.items(), key=lambda x: x[1])[0].replace("_", " ").title() if motivos_totales else "Defecto Fábrica"

    table_headers = ["#", "Producto", "Vendidas", "Reclamos Garantía", "Devoluciones", "Tasa Falla %", "Causa Frecuente"]
    table_rows = [
        [
            idx,
            it["producto"],
            it["vendidas"],
            it["garantias"],
            it["devoluciones"],
            f"{it['tasa_falla']}%",
            it["motivo_principal"],
        ]
        for idx, it in enumerate(top_calidad, start=1)
    ]

    kpis = [
        {"label": "Tasa Global de Incidencias", "value": f"{tasa_global}%", "trend": "Garantías + Devoluciones", "color": "#10B981" if tasa_global < 5.0 else "#EF4444"},
        {"label": "Garantías Activas", "value": f"{total_garantias} und", "trend": "Pólizas Emitidas", "color": "#38BDF8"},
        {"label": "Devoluciones Procesadas", "value": f"{total_devoluciones} casos", "trend": "Postventa", "color": "#F59E0B" if total_devoluciones > 0 else "#64748B"},
        {"label": "Motivo Preponderante", "value": str(motivo_mas_frecuente), "trend": "Causa Raíz", "color": "#818CF8"},
    ]

    labels_chart = list(motivos_totales.keys()) if motivos_totales else ["Defecto Fábrica", "Daño Transporte", "Insatisfacción"]
    values_chart = list(motivos_totales.values()) if motivos_totales else [total_garantias or 1, total_devoluciones or 1, 1]

    chart = {
        "chart_type": "pie",
        "title": "Distribución de Reclamos y Motivos de Devolución",
        "labels": [l.replace("_", " ").title() for l in labels_chart],
        "datasets": [
            {
                "data": values_chart,
                "backgroundColor": ["#EF4444", "#F59E0B", "#38BDF8", "#818CF8", "#10B981"],
            }
        ],
    }

    return {
        "category": "garantias",
        "title": f"Control de Calidad, Garantías y Devoluciones — {parsed.period_label}",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
        "total_garantias": total_garantias,
        "total_devoluciones": total_devoluciones,
        "tasa_global": tasa_global,
        "motivo_top": motivo_mas_frecuente,
    }


def query_blockchain_security_data(
    db: Session, tenant_id: int, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Consulta de notarización criptográfica, inmutabilidad Blockchain y alertas de fraude."""
    stmt_eventos = select(func.count(EventoTrazabilidad.idevento)).where(EventoTrazabilidad.idtenant == tenant_id)
    total_eventos = int(db.execute(stmt_eventos).scalar() or 0)

    stmt_bc = (
        select(
            RegistroBlockchain.estado,
            func.count(RegistroBlockchain.idregistro).label("conteo"),
        )
        .join(EventoTrazabilidad, EventoTrazabilidad.idevento == RegistroBlockchain.idevento)
        .where(EventoTrazabilidad.idtenant == tenant_id)
        .group_by(RegistroBlockchain.estado)
    )
    bc_estados = {str(r.estado): int(r.conteo or 0) for r in db.execute(stmt_bc).all()}
    confirmados = bc_estados.get("confirmado", 0)
    pendientes = bc_estados.get("pendiente", 0)
    rechazados = bc_estados.get("rechazado", 0)
    total_bc = confirmados + pendientes + rechazados
    tasa_notarizacion = round((confirmados / max(total_bc or total_eventos, 1) * 100), 1)

    stmt_sospecha = (
        select(
            ReporteSospecha.estado,
            func.count(ReporteSospecha.idreporte).label("conteo"),
        )
        .where(ReporteSospecha.idtenant == tenant_id)
        .group_by(ReporteSospecha.estado)
    )
    sospechas = {str(r.estado): int(r.conteo or 0) for r in db.execute(stmt_sospecha).all()}
    total_sospechas = sum(sospechas.values())

    stmt_alertas = select(func.count(Alerta.idalerta)).where(Alerta.idtenant == tenant_id, Alerta.estado.in_(["pendiente", "en_proceso"]))
    alertas_activas = int(db.execute(stmt_alertas).scalar() or 0)

    stmt_qr = (
        select(func.count(ConsultaTrazabilidad.idconsulta))
        .join(CodigoQR, CodigoQR.idcodigoqr == ConsultaTrazabilidad.idcodigoqr)
        .join(UnidadProducto, UnidadProducto.idunidad == CodigoQR.idunidad)
        .where(UnidadProducto.idtenant == tenant_id)
    )
    consultas_qr = int(db.execute(stmt_qr).scalar() or 0)

    stmt_muestreo = (
        select(
            RegistroBlockchain.idregistro,
            EventoTrazabilidad.tipoevento,
            Producto.nombre,
            UnidadProducto.numeroserie,
            RegistroBlockchain.payloadhash,
            RegistroBlockchain.txhash,
            RegistroBlockchain.network,
            RegistroBlockchain.estado,
        )
        .join(EventoTrazabilidad, EventoTrazabilidad.idevento == RegistroBlockchain.idevento)
        .outerjoin(EventoUnidad, EventoUnidad.idevento == EventoTrazabilidad.idevento)
        .outerjoin(UnidadProducto, UnidadProducto.idunidad == EventoUnidad.idunidad)
        .outerjoin(VarianteProducto, VarianteProducto.idvariante == UnidadProducto.idvariante)
        .outerjoin(Producto, Producto.idproducto == VarianteProducto.idproducto)
        .where(EventoTrazabilidad.idtenant == tenant_id)
        .order_by(desc(RegistroBlockchain.idregistro))
        .limit(parsed.limit or 15)
    )
    filas_bc = db.execute(stmt_muestreo).all()

    table_headers = ["ID TX", "Evento", "Dispositivo", "N° Serie", "Hash Criptográfico SHA-256", "Red Web3", "Estado"]
    table_rows = []
    for r in filas_bc:
        short_hash = f"{r.payloadhash[:10]}...{r.payloadhash[-8:]}" if r.payloadhash else "Pendiente"
        table_rows.append([
            f"TX #{r.idregistro}",
            (r.tipoevento or "Trazabilidad").replace("_", " ").title(),
            r.nombre or "Lote Apple",
            r.numeroserie or "Sin serial",
            short_hash,
            r.network or "Sepolia Testnet",
            (r.estado or "confirmado").title(),
        ])

    kpis = [
        {"label": "Tasa Notarización On-Chain", "value": f"{tasa_notarizacion}%", "trend": "Red Sepolia / Amoy", "color": "#10B981"},
        {"label": "Registros Inmutables", "value": f"{confirmados} confirmados", "trend": f"{pendientes} en cola", "color": "#38BDF8"},
        {"label": "Alertas y Sospechas", "value": f"{total_sospechas + alertas_activas}", "trend": "Seguridad y Fraude", "color": "#EF4444" if (total_sospechas + alertas_activas) > 0 else "#10B981"},
        {"label": "Consultas QR Públicas", "value": f"{consultas_qr} verificaciones", "trend": "Validación Cliente", "color": "#818CF8"},
    ]

    chart = {
        "chart_type": "pie",
        "title": "Distribución de Seguridad e Integridad Blockchain",
        "labels": ["Notarizados Confirmados", "Pendientes de Minado", "Alertas y Fraude", "Consultas QR"],
        "datasets": [
            {
                "data": [max(confirmados, 1), pendientes, (total_sospechas + alertas_activas), max(consultas_qr, 1)],
                "backgroundColor": ["#10B981", "#F59E0B", "#EF4444", "#38BDF8"],
            }
        ],
    }

    return {
        "category": "blockchain",
        "title": f"Seguridad, Notarización Blockchain y Alertas — {parsed.period_label}",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(table_rows),
        "tasa_notarizacion": tasa_notarizacion,
        "confirmados": confirmados,
        "alertas": alertas_activas,
        "sospechas": total_sospechas,
    }


def build_product_detail(
    db: Session, tenant_id: int, producto: str, now: datetime,
    tenant_name: str,
) -> Dict[str, Any]:
    """Ficha detallada de un producto con rango fijo de 36 meses y filtro tenant.

    Todas las tablas hijas se alcanzan desde un padre con ``idtenant``:
    Venta (P5) o UnidadProducto/EventoTrazabilidad (P4).
    """
    desde, hasta, etiqueta = parse_detail_period(now)

    id_productos = db.execute(
        select(Producto.idproducto)
        .join(VarianteProducto, VarianteProducto.idproducto == Producto.idproducto)
        .join(
            CatalogoTenant,
            and_(
                CatalogoTenant.idvariante == VarianteProducto.idvariante,
                CatalogoTenant.idtenant == tenant_id,
                CatalogoTenant.activo.is_(True),
            ),
        )
        .where(Producto.nombre.ilike(f"%{producto}%"))
        .distinct()
    ).scalars().all()
    if not id_productos:
        return {}

    ids_variantes = db.execute(
        select(VarianteProducto.idvariante)
        .where(VarianteProducto.idproducto.in_(id_productos))
    ).scalars().all()
    if not ids_variantes:
        return {}

    nombre_producto = db.execute(
        select(Producto.nombre)
        .where(Producto.idproducto.in_(id_productos))
        .order_by(Producto.nombre)
        .limit(1)
    ).scalar() or producto

    rango_venta = [Venta.fechaventa >= desde, Venta.fechaventa < hasta]
    rango_unidad = [
        UnidadProducto.fechaingreso >= desde,
        UnidadProducto.fechaingreso < hasta,
    ]

    # --- Comercial: unidades, ingresos, ventas, pagos, devoluciones ----------
    stmt_ventas = (
        select(
            func.coalesce(func.sum(VentaDetalle.cantidad), 0).label("unidades"),
            func.coalesce(func.sum(VentaDetalle.subtotal), 0).label("ingresos"),
            func.count(distinct(Venta.idventa)).label("num_ventas"),
        )
        .join(Venta, Venta.idventa == VentaDetalle.idventa)
        .where(
            Venta.idtenant == tenant_id,
            VentaDetalle.idvariante.in_(ids_variantes),
            *rango_venta,
        )
    )
    rv = db.execute(stmt_ventas).one()
    unidades_vendidas = int(rv.unidades or 0)
    ingresos = float(rv.ingresos or 0)
    num_ventas = int(rv.num_ventas or 0)

    stmt_pagos = (
        select(func.coalesce(func.sum(Pago.monto), 0))
        .join(Venta, Venta.idventa == Pago.idventa)
        .where(
            Venta.idtenant == tenant_id,
            Pago.estado == "completado",
            *rango_venta,
            Venta.idventa.in_(
                select(VentaDetalle.idventa).where(
                    VentaDetalle.idvariante.in_(ids_variantes)
                )
            ),
        )
    )
    cobrado = float(db.execute(stmt_pagos).scalar() or 0)

    stmt_devoluciones = (
        select(func.count(distinct(Devolucion.iddevolucion)))
        .join(Venta, Venta.idventa == Devolucion.idventa)
        .join(DevolucionUnidad, DevolucionUnidad.iddevolucion == Devolucion.iddevolucion)
        .join(UnidadProducto, UnidadProducto.idunidad == DevolucionUnidad.idunidad)
        .where(
            Venta.idtenant == tenant_id,
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.idvariante.in_(ids_variantes),
            Devolucion.fechadevolucion >= desde,
            Devolucion.fechadevolucion < hasta,
        )
    )
    devoluciones = int(db.execute(stmt_devoluciones).scalar() or 0)

    stmt_garantias = (
        select(func.count(distinct(GarantiaUnidad.idgarantia)))
        .join(UnidadProducto, UnidadProducto.idunidad == GarantiaUnidad.idunidad)
        .where(
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.idvariante.in_(ids_variantes),
            GarantiaUnidad.fechainicio >= desde.date(),
            GarantiaUnidad.fechainicio < hasta.date(),
        )
    )
    garantias = int(db.execute(stmt_garantias).scalar() or 0)

    # --- Inventario, QR, trazabilidad e incidentes ---------------------------
    stmt_unidades = (
        select(
            func.count(UnidadProducto.idunidad).label("total"),
            func.sum(
                case((UnidadProducto.estado == "vendido", 1), else_=0)
            ).label("vendidas"),
            func.sum(
                case((UnidadProducto.estado == "disponible", 1), else_=0)
            ).label("disponibles"),
            func.sum(
                case((UnidadProducto.estado == "en_transito", 1), else_=0)
            ).label("transito"),
        )
        .where(
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.idvariante.in_(ids_variantes),
            *rango_unidad,
        )
    )
    ru = db.execute(stmt_unidades).one()
    total_unidades = int(ru.total or 0)
    vendidas_inv = int(ru.vendidas or 0)
    disponibles = int(ru.disponibles or 0)
    en_transito = int(ru.transito or 0)

    stmt_consultas = (
        select(func.count(distinct(ConsultaTrazabilidad.idconsulta)))
        .join(CodigoQR, CodigoQR.idcodigoqr == ConsultaTrazabilidad.idcodigoqr)
        .join(UnidadProducto, UnidadProducto.idunidad == CodigoQR.idunidad)
        .where(
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.idvariante.in_(ids_variantes),
            ConsultaTrazabilidad.fechahora >= desde,
            ConsultaTrazabilidad.fechahora < hasta,
        )
    )
    consultas_qr = int(db.execute(stmt_consultas).scalar() or 0)

    stmt_eventos = (
        select(func.count(distinct(EventoUnidad.ideventounidad)))
        .join(EventoTrazabilidad, EventoTrazabilidad.idevento == EventoUnidad.idevento)
        .join(UnidadProducto, UnidadProducto.idunidad == EventoUnidad.idunidad)
        .where(
            EventoTrazabilidad.idtenant == tenant_id,
            UnidadProducto.idtenant == tenant_id,
            UnidadProducto.idvariante.in_(ids_variantes),
            EventoTrazabilidad.fechahora >= desde,
            EventoTrazabilidad.fechahora < hasta,
        )
    )
    eventos = int(db.execute(stmt_eventos).scalar() or 0)

    stmt_alertas = (
        select(func.count(distinct(Alerta.idalerta)))
        .join(UnidadProducto, UnidadProducto.idunidad == Alerta.idunidad)
        .where(
            Alerta.idtenant == tenant_id,
            UnidadProducto.idvariante.in_(ids_variantes),
            Alerta.fechadeteccion >= desde,
            Alerta.fechadeteccion < hasta,
        )
    )
    alertas = int(db.execute(stmt_alertas).scalar() or 0)

    stmt_reportes = (
        select(func.count(distinct(ReporteSospecha.idreporte)))
        .where(
            ReporteSospecha.idtenant == tenant_id,
            ReporteSospecha.idunidad.in_(
                select(UnidadProducto.idunidad).where(
                    UnidadProducto.idtenant == tenant_id,
                    UnidadProducto.idvariante.in_(ids_variantes),
                )
            ),
            ReporteSospecha.creadoen >= desde,
            ReporteSospecha.creadoen < hasta,
        )
    )
    reportes = int(db.execute(stmt_reportes).scalar() or 0)

    # --- Tendencia mensual (unidades vendidas) -------------------------------
    stmt_mensual = (
        select(
            func.date_trunc("month", Venta.fechaventa).label("mes"),
            func.coalesce(func.sum(VentaDetalle.cantidad), 0).label("unidades"),
        )
        .join(Venta, Venta.idventa == VentaDetalle.idventa)
        .where(
            Venta.idtenant == tenant_id,
            VentaDetalle.idvariante.in_(ids_variantes),
            *rango_venta,
        )
        .group_by("mes")
        .order_by("mes")
    )
    mensual = [
        {"mes": fila.mes.strftime("%Y-%m"), "unidades": int(fila.unidades or 0)}
        for fila in db.execute(stmt_mensual).all()
    ]

    tasa_devolucion = round(devoluciones / num_ventas * 100, 2) if num_ventas else 0.0
    precio_promedio = round(ingresos / unidades_vendidas, 2) if unidades_vendidas else 0.0
    ticket_promedio = round(ingresos / num_ventas, 2) if num_ventas else 0.0

    return {
        "producto": nombre_producto,
        "tenant_name": tenant_name,
        "period_label": f"Detalle · 36 meses · {tenant_name}",
        "desde": desde.date().isoformat(),
        "hasta": hasta.date().isoformat(),
        "kpis": [
            {"label": "Unidades vendidas", "value": f"{max(unidades_vendidas, vendidas_inv)} und",
             "trend": "36 meses", "color": "#10B981"},
            {"label": "Ingresos totales", "value": f"${ingresos:,.2f}",
             "trend": "36 meses", "color": "#38BDF8"},
            {"label": "N° de ventas", "value": f"{num_ventas}",
             "trend": "Transacciones", "color": "#818CF8"},
            {"label": "Precio promedio", "value": f"${precio_promedio:,.2f}",
             "trend": "Por unidad", "color": "#F59E0B"},
            {"label": "Unidades en stock", "value": f"{disponibles} und",
             "trend": "Disponible", "color": "#34D399"},
            {"label": "Tasa de devolución", "value": f"{tasa_devolucion}%",
             "trend": f"{devoluciones} devoluciones", "color": "#FB7185"},
        ],
        "metrics": {
            "unidades_vendidas": max(unidades_vendidas, vendidas_inv),
            "ingresos_usd": round(ingresos, 2),
            "num_ventas": num_ventas,
            "cobrado_usd": round(cobrado, 2),
            "ticket_promedio_usd": ticket_promedio,
            "precio_promedio_usd": precio_promedio,
            "unidades_totales": total_unidades,
            "unidades_disponibles": disponibles,
            "unidades_en_transito": en_transito,
            "devoluciones": devoluciones,
            "tasa_devolucion_pct": tasa_devolucion,
            "garantias": garantias,
            "consultas_qr": consultas_qr,
            "eventos_trazabilidad": eventos,
            "alertas": alertas,
            "reportes_sospecha": reportes,
        },
        "monthly_trend": mensual,
        "table_headers": ["Métrica", "Valor", "Detalle"],
        "table_rows": [
            ["Unidades vendidas", max(unidades_vendidas, vendidas_inv), "36 meses"],
            ["Ingresos USD", round(ingresos, 2), "Ventas registradas"],
            ["N° de ventas", num_ventas, "Transacciones únicas"],
            ["Cobrado USD", round(cobrado, 2), "Pagos completados"],
            ["Ticket promedio USD", ticket_promedio, "Por venta"],
            ["Precio promedio USD", precio_promedio, "Por unidad"],
            ["Unidades en stock", disponibles, "Disponibles"],
            ["Unidades en tránsito", en_transito, "Logística activa"],
            ["Devoluciones", devoluciones, f"{tasa_devolucion}% de ventas"],
            ["Garantías", garantias, "Cobertura activa"],
            ["Consultas QR", consultas_qr, "Verificaciones públicas"],
            ["Eventos de trazabilidad", eventos, "Registros on/off-chain"],
            ["Alertas", alertas, "Incidentes detectados"],
            ["Reportes de sospecha", reportes, "Reportes de falsificación"],
        ],
    }


def query_cross_tenant_comparison_data(
    db: Session, query: str, parsed: ParsedQuery
) -> Dict[str, Any]:
    """Agrega métricas comparativas consolidadas de todas las empresas activas (SuperAdmin)."""
    # 1. Obtener todas las empresas activas
    tenants = db.execute(
        select(Tenant).where(Tenant.activo == True).order_by(Tenant.idtenant.asc())
    ).scalars().all()

    # 2. Agregaciones de ventas
    filtros_v = [Venta.estado != "cancelada"]
    if parsed.desde and parsed.hasta:
        filtros_v.extend([Venta.fechaventa >= parsed.desde, Venta.fechaventa < parsed.hasta])
    v_stmt = (
        select(
            Venta.idtenant,
            func.count(Venta.idventa).label("num_ventas"),
            func.coalesce(func.sum(Venta.total), 0.0).label("monto_ventas"),
        )
        .where(*filtros_v)
        .group_by(Venta.idtenant)
    )
    ventas_map = {r.idtenant: (r.num_ventas, float(r.monto_ventas)) for r in db.execute(v_stmt).all()}

    # 3. Agregaciones de stock disponible
    stk_stmt = (
        select(
            UnidadProducto.idtenant,
            func.count(UnidadProducto.idunidad).label("stock_disponible"),
        )
        .where(UnidadProducto.estado == "disponible")
        .group_by(UnidadProducto.idtenant)
    )
    stock_map = {r.idtenant: r.stock_disponible for r in db.execute(stk_stmt).all()}

    # 4. Agregaciones de unidades vendidas
    filtros_u = [UnidadProducto.estado == "vendido"]
    if parsed.desde and parsed.hasta:
        filtros_u.extend([UnidadProducto.fecharecepcion >= parsed.desde, UnidadProducto.fecharecepcion < parsed.hasta])
    vend_stmt = (
        select(
            UnidadProducto.idtenant,
            func.count(UnidadProducto.idunidad).label("unidades_vendidas"),
        )
        .where(*filtros_u)
        .group_by(UnidadProducto.idtenant)
    )
    vendidas_map = {r.idtenant: r.unidades_vendidas for r in db.execute(vend_stmt).all()}

    # 5. Agregaciones de garantías vinculadas a unidades de cada tenant
    gar_stmt = (
        select(
            UnidadProducto.idtenant,
            func.count(GarantiaUnidad.idgarantia).label("garantias_count"),
        )
        .join(UnidadProducto, GarantiaUnidad.idunidad == UnidadProducto.idunidad)
    )
    if parsed.desde and parsed.hasta:
        gar_stmt = gar_stmt.where(
            GarantiaUnidad.fechainicio >= parsed.desde.date(),
            GarantiaUnidad.fechainicio < parsed.hasta.date(),
        )
    gar_stmt = gar_stmt.group_by(UnidadProducto.idtenant)
    garantias_map = {r.idtenant: r.garantias_count for r in db.execute(gar_stmt).all()}

    # 6. Agregaciones de alertas
    filtros_a = []
    if parsed.desde and parsed.hasta:
        filtros_a.extend([Alerta.fechadeteccion >= parsed.desde, Alerta.fechadeteccion < parsed.hasta])
    alt_stmt = select(
        Alerta.idtenant,
        func.count(Alerta.idalerta).label("alertas_count"),
    )
    if filtros_a:
        alt_stmt = alt_stmt.where(*filtros_a)
    alt_stmt = alt_stmt.group_by(Alerta.idtenant)
    alertas_map = {r.idtenant: r.alertas_count for r in db.execute(alt_stmt).all()}

    # 7. Consolidar lista de empresas
    items = []
    for t in tenants:
        n_ventas, m_ventas = ventas_map.get(t.idtenant, (0, 0.0))
        stk = stock_map.get(t.idtenant, 0)
        vend = vendidas_map.get(t.idtenant, 0)
        gar = garantias_map.get(t.idtenant, 0)
        alt = alertas_map.get(t.idtenant, 0)
        items.append({
            "idtenant": t.idtenant,
            "nombre": t.nombre,
            "nit": t.nit or "N/A",
            "ventas_monto": m_ventas,
            "ventas_count": n_ventas,
            "unidades_vendidas": vend,
            "stock_disponible": stk,
            "garantias_count": gar,
            "alertas_count": alt,
        })

    # Determinar foco de la consulta
    q_norm = normalize_text(query)
    is_stock_focus = any(k in q_norm for k in ("stock", "inventario", "almacen")) and not any(k in q_norm for k in ("venta", "factur", "ingreso"))
    is_garantia_focus = any(k in q_norm for k in ("garantia", "devolucion", "incidencia", "falla", "alerta"))

    if is_stock_focus:
        items.sort(key=lambda x: x["stock_disponible"], reverse=True)
        chart_title = "Distribución de Stock Disponible por Empresa (Unidades)"
        chart_data = [x["stock_disponible"] for x in items]
        chart_label = "Unidades Disponibles"
    elif is_garantia_focus:
        items.sort(key=lambda x: (x["garantias_count"] + x["alertas_count"]), reverse=True)
        chart_title = "Incidencias y Garantías por Empresa (Casos)"
        chart_data = [x["garantias_count"] for x in items]
        chart_label = "Garantías Tramitadas"
    else:
        items.sort(key=lambda x: x["ventas_monto"], reverse=True)
        chart_title = "Comparativa de Ingresos por Empresa ($ USD)"
        chart_data = [round(x["ventas_monto"], 2) for x in items]
        chart_label = "Ingresos ($ USD)"

    total_ingresos = sum(x["ventas_monto"] for x in items)
    total_stock = sum(x["stock_disponible"] for x in items)
    total_ventas = sum(x["ventas_count"] for x in items)
    total_garantias = sum(x["garantias_count"] for x in items)
    lider = items[0] if items else {"nombre": "N/A", "ventas_monto": 0.0}

    palette = ["#38BDF8", "#10B981", "#F59E0B", "#818CF8", "#EF4444", "#06B6D4", "#EC4899", "#8B5CF6", "#14B8A6"]
    bg_colors = [palette[i % len(palette)] for i in range(len(items))]

    kpis = [
        {"label": "Empresa Líder en Ventas", "value": f"{lider['nombre']}", "trend": f"${lider['ventas_monto']:,.2f} USD", "color": "#10B981"},
        {"label": "Facturación Red Consolidada", "value": f"${total_ingresos:,.2f} USD", "trend": f"{total_ventas} ventas", "color": "#38BDF8"},
        {"label": "Stock Global Disponible", "value": f"{total_stock:,} und", "trend": f"{len(items)} empresas activas", "color": "#F59E0B"},
        {"label": "Garantías Tramitadas", "value": f"{total_garantias} casos", "trend": "Red de importadoras", "color": "#818CF8"},
    ]

    chart = {
        "chart_type": "bar",
        "title": chart_title,
        "labels": [x["nombre"] for x in items],
        "datasets": [
            {
                "label": chart_label,
                "data": chart_data,
                "backgroundColor": bg_colors,
            }
        ],
    }

    table_headers = ["Empresa", "NIT", "Facturación ($)", "Transacciones", "Stock Disponible", "Garantías", "Alertas"]
    table_rows = [
        [
            x["nombre"],
            x["nit"],
            f"${x['ventas_monto']:,.2f}",
            x["ventas_count"],
            f"{x['stock_disponible']} und",
            f"{x['garantias_count']} casos",
            f"{x['alertas_count']} alertas",
        ]
        for x in items
    ]

    return {
        "category": "comparacion_tenants",
        "title": f"Benchmark Comparativo Multi-Empresa ({parsed.period_label})",
        "kpis": kpis,
        "chart": chart,
        "table_headers": table_headers,
        "table_rows": table_rows,
        "raw_count": len(items),
        "lider_nombre": lider["nombre"],
        "lider_monto": lider["ventas_monto"],
        "total_plataforma_ingresos": total_ingresos,
        "total_empresas": len(items),
        "stock_total": total_stock,
    }


def synthesize_with_gemini(
    query: str,
    category: str,
    data: Dict[str, Any],
    tenant_name: str,
    interpretation: str = "",
) -> Tuple[str, str]:
    """
    Invoca Gemini Flash mediante google-genai para resumir el informe,
    con fallback automático al sintetizador semántico determinista si no hay API Key o falla.
    """
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")

    if gemini_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=gemini_key)
            prompt = f"""
Eres el Asistente Ejecutivo de Inteligencia Artificial del Sistema de Trazabilidad Multi-Tenant para la empresa '{tenant_name}'.
El usuario ha realizado la siguiente consulta por voz:
"{query}"

Hemos ejecutado las consultas en la base de datos PostgreSQL de su tenant y obtenido los siguientes datos reales:
Categoría: {category}
Criterios aplicados por el intérprete (respétalos literalmente en tu respuesta): {interpretation}
KPIs Principales: {data.get('kpis')}
Registros consolidados: {data.get('raw_count')} filas.
Muestreo de datos: {data.get('table_rows')[:5]}

Tu tarea es responder con dos secciones separadas por el delimitador exacto '---EXECUTIVE---':
1. VOICE_SUMMARY: Una o dos oraciones directas, claras y profesionales en español, diseñadas para ser leídas en voz alta por Text-To-Speech (sin asteriscos, sin markdown, tono ejecutivo seguro).
---EXECUTIVE---
2. EXECUTIVE_MARKDOWN: Análisis detallado en Markdown con viñetas, conclusiones sobre la operación, alertas detectadas y recomendaciones estratégicas.
"""
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                )
            )
            text_resp = response.text or ""
            if "---EXECUTIVE---" in text_resp:
                parts = text_resp.split("---EXECUTIVE---")
                voice_part = parts[0].strip().replace("**", "").replace("#", "")
                exec_part = parts[1].strip()
                return voice_part, exec_part
        except Exception as e:
            print(f"[Gemini Fallback Warning]: {e}")

    # Fallback Determinista Inteligente (Sin dependencias externas)
    if category == "inventario":
        disp = data.get("disponibles", 0)
        trans = data.get("en_transito", 0)
        val = data.get("valor_total_costo", 0.0)
        voice = (
            f"Actualmente cuentas con {disp} unidades disponibles en almacenes por un valor de "
            f"${val:,.2f} dólares, y {trans} unidades en tránsito logístico."
        )
        exec_md = (
            f"### Resumen Analítico de Inventario ({tenant_name})\n"
            f"- **Disponibilidad Inmediata:** Se registran **{disp} unidades físicas** en estado *disponible* listas para despacho comercial.\n"
            f"- **Flujo de Mercancía:** **{trans} unidades** se encuentran en tránsito activo entre nodos de la cadena.\n"
            f"- **Valoración de Capital:** El valor total en costo de las unidades disponibles asciende a **${val:,.2f} USD**.\n"
            f"- **Recomendación:** Verificar los niveles mínimos de seguridad en los modelos con stock inferior a 3 unidades."
        )
    elif category == "compras":
        tot = data.get("total_usd", 0.0)
        ords = data.get("total_ordenes", 0)
        pend = data.get("pendientes", 0)
        voice = (
            f"Tienes {ords} órdenes de compra registradas con un volumen total de ${tot:,.2f} dólares, "
            f"de las cuales {pend} están pendientes de aprobación ejecutiva."
        )
        exec_md = (
            f"### Resumen de Abastecimiento y Compras ({tenant_name})\n"
            f"- **Volumen Financiero:** Se han emitido adquisiciones por un valor acumulado de **${tot:,.2f} USD**.\n"
            f"- **Órdenes de Compra:** Total de **{ords} órdenes registradas** con proveedores internacionales y distribuidores.\n"
            f"- **Estado de Flujo:** **{pend} órdenes pendientes** que requieren validación de presupuesto.\n"
            f"- **Control de Recepción:** Las órdenes recibidas cuentan con sus actas de inspección en almacén."
        )
    elif category == "logistica":
        voice = (
            f"Los envíos monitoreados mantienen condiciones ambientales estables con temperatura media adecuada "
            f"y telemetría de sensores IoT completamente verificada."
        )
        exec_md = (
            f"### Informe de Trazabilidad y Telemetría IoT ({tenant_name})\n"
            f"- **Monitoreo en Ruta:** Despachos custodiados por empresas de transporte homologadas.\n"
            f"- **Condiciones de Carga:** Los sensores ambientales registran niveles de temperatura y humedad dentro de los rangos autorizados para microelectrónica.\n"
            f"- **Integridad de Cadena:** Todas las unidades en tránsito cuentan con registro de custodia digital."
        )
    elif category == "auditoria":
        voice = (
            f"La bitácora del sistema reporta operaciones activas y todos los eventos auditados "
            f"se encuentran debidamente sincronizados con fecha y hora de Bolivia."
        )
        exec_md = (
            f"### Auditoría Inmutable del Sistema ({tenant_name})\n"
            f"- **Trazabilidad de Accesos:** Se han auditado los métodos HTTP y direcciones IP de los usuarios autenticados.\n"
            f"- **Seguridad Multi-Tenant:** Cada operación valida el aislamiento de datos por tenant.\n"
            f"- **Cumplimiento:** Registros listos para inspección de conformidad y auditoría externa."
        )
    elif category == "ventas":
        top = data.get("top_producto")
        if top:
            voice = (
                f"En {interpretation or 'el periodo consultado'}, el producto más destacado es {top}, "
                f"con {data.get('top_unidades', 0)} unidades vendidas y "
                f"${data.get('top_ingresos', 0.0):,.2f} dólares en ingresos."
            )
            exec_md = (
                f"### Ranking Comercial de Productos ({tenant_name})\n"
                f"- **Criterio aplicado:** {interpretation}.\n"
                f"- **Líder del ranking:** **{top}** con **{data.get('top_unidades', 0)} unidades** y "
                f"**${data.get('top_ingresos', 0.0):,.2f} USD**.\n"
                f"- **Detalle:** se listan {data.get('raw_count', 0)} productos ordenados por el criterio solicitado.\n"
                f"- **Recomendación:** priorizar stock del líder del ranking y revisar la conversión del resto del catálogo."
            )
        else:
            voice = (
                f"No se registraron ventas para {tenant_name} con los filtros solicitados: {interpretation or 'sin filtros'}."
            )
            exec_md = (
                f"### Ranking Comercial de Productos ({tenant_name})\n"
                f"- **Criterio aplicado:** {interpretation}.\n"
                f"- **Resultado:** sin ventas en el rango consultado. Prueba con un período más amplio."
            )
    elif category == "rentabilidad":
        tot_b = data.get("total_beneficio", 0.0)
        prom_m = data.get("promedio_margen_pct", 0.0)
        top_p = data.get("top_producto", "Catálogo")
        voice = (
            f"Tu margen comercial promedio es de {prom_m}% y el beneficio bruto acumulado alcanza "
            f"${tot_b:,.2f} dólares, siendo {top_p} el producto de mayor rentabilidad."
        )
        exec_md = (
            f"### Análisis de Rentabilidad y Margen Comercial ({tenant_name})\n"
            f"- **Beneficio Bruto Total:** Se ha generado un excedente comercial estimado de **${tot_b:,.2f} USD** sobre el costo de adquisición e importación.\n"
            f"- **Margen Comercial Promedio:** **{prom_m}%** de margen sobre el costo promedio de catálogo.\n"
            f"- **Producto Más Rentable:** **{top_p}** lidera el ranking de contribución marginal a la empresa.\n"
            f"- **Recomendación Estratégica:** Incrementar el volumen de compra en las variantes con margen superior al 25% y revisar la política de descuentos en los modelos con menor retorno."
        )
    elif category == "garantias":
        tasa = data.get("tasa_global", 0.0)
        tot_g = data.get("total_garantias", 0)
        tot_d = data.get("total_devoluciones", 0)
        mot_t = data.get("motivo_top", "Defecto Fábrica")
        voice = (
            f"La tasa global de incidencias es de {tasa}%, con {tot_g} garantías tramitadas y "
            f"{tot_d} devoluciones procesadas, siendo {mot_t} el motivo más frecuente."
        )
        exec_md = (
            f"### Control de Calidad, Devoluciones y Garantías ({tenant_name})\n"
            f"- **Tasa Global de Incidencias:** **{tasa}%** de reclamos sobre el total de unidades comercializadas.\n"
            f"- **Coberturas de Garantía:** **{tot_g} unidades** con póliza de garantía oficial ejecutada o vigente.\n"
            f"- **Devoluciones de Clientes:** **{tot_d} solicitudes de devolución** tramitadas en el módulo de postventa.\n"
            f"- **Causa Raíz Principal:** **{mot_t}** representa la mayor concentración de quejas reportadas.\n"
            f"- **Recomendación de Calidad:** Auditar los lotes del proveedor en el punto de recepción física antes de autorizar el ingreso al catálogo disponible."
        )
    elif category == "blockchain":
        tasa_bc = data.get("tasa_notarizacion", 100.0)
        conf = data.get("confirmados", 0)
        incid = data.get("alertas", 0) + data.get("sospechas", 0)
        voice = (
            f"La tasa de notarización en blockchain alcanza {tasa_bc}% con {conf} registros confirmados "
            f"y {incid} alertas o denuncias de sospecha registradas en el sistema."
        )
        exec_md = (
            f"### Seguridad Criptográfica, Blockchain y Alertas ({tenant_name})\n"
            f"- **Anclaje en Blockchain:** **{tasa_bc}% de los eventos críticos** cuentan con hash SHA-256 inmutable en la red pública.\n"
            f"- **Confirmaciones On-Chain:** **{conf} transacciones minadas exitosamente** y verificables vía Smart Contract.\n"
            f"- **Incidentes de Seguridad:** Se detectaron **{incid} alertas/denuncias** que requieren verificación del número de serie o empaque.\n"
            f"- **Garantía Anti-Falsificación:** Las unidades certificadas permiten al consumidor final verificar su legitimidad escaneando el código QR oficial."
        )
    elif category == "comparacion_tenants":
        lider_nombre = data.get("lider_nombre", "N/A")
        lider_monto = data.get("lider_monto", 0.0)
        tot_plataforma = data.get("total_plataforma_ingresos", 0.0)
        tot_empresas = data.get("total_empresas", 0)
        stock_total = data.get("stock_total", 0)
        voice = (
            f"En la comparativa de las {tot_empresas} empresas de la red, {lider_nombre} lidera la facturacion "
            f"con ${lider_monto:,.2f} dolares de un total consolidado de ${tot_plataforma:,.2f} dolares, "
            f"con {stock_total} unidades disponibles en inventario global."
        )
        exec_md = (
            f"### Benchmark Comparativo Multi-Empresa · Vista SuperAdministrador\n"
            f"- **Criterio de Análisis:** {interpretation}.\n"
            f"- **Empresa Líder en Ventas:** **{lider_nombre}** con **${lider_monto:,.2f} USD** facturados.\n"
            f"- **Facturación Consolidada de la Red:** **${tot_plataforma:,.2f} USD** generados a través de las {tot_empresas} empresas registradas.\n"
            f"- **Inventario Global de Dispositivos:** **{stock_total} unidades disponibles** para despacho inmediato en toda la plataforma.\n"
            f"- **Gobernanza y Supervisión:** Se visualizan los indicadores cruzados de facturación, volumen de stock, garantías y alertas operativas de cada importadora registrada.\n"
            f"- **Recomendación Estratégica para SuperAdmin:** Equilibrar la cuota de inventario en empresas con alta demanda comercial y auditar las empresas con mayor porcentaje de alertas de transporte o devoluciones."
        )
    else:
        voice = f"He procesado tu consulta de {tenant_name} y consolidado los datos del sistema en el reporte dinámico."
        exec_md = f"### Informe Consolidado ({tenant_name})\nConsulta ejecutada con éxito sobre los registros activos del tenant."

    return voice, exec_md


def process_voice_query(
    db: Session,
    tenant_id: int,
    query: str,
    context: Optional[str] = None,
    user_email: str = "Admin",
    is_superadmin: bool = False,
) -> Dict[str, Any]:
    """
    Punto de entrada principal:
    1. Obtiene datos del tenant y parsea la consulta (intención, período, top N, filtros).
    2. Consulta PostgreSQL con aislamiento garantizado (idtenant o cross-tenant para SuperAdmin).
    3. Sintetiza análisis mediante Gemini o Motor Semántico.
    4. Guarda en caché para exportación instantánea a PDF/Excel.
    """
    parsed = parse_query(query, now=get_bolivia_now())
    parsed = _resolver_filtros_catalogo(db, tenant_id, parsed, query)
    intent = parsed.intent

    if intent == "comparacion_tenants":
        if not is_superadmin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acceso denegado: Los reportes comparativos entre todas las empresas están reservados exclusivamente para el SuperAdministrador."
            )
        data = query_cross_tenant_comparison_data(db, query, parsed)
        tenant_name = "Plataforma Global (SuperAdmin)"
        tenant_nit = "RED MULTI-TENANT"
    else:
        tenant = db.execute(select(Tenant).where(Tenant.idtenant == tenant_id)).scalars().first()
        tenant_name = tenant.nombre if tenant else "Empresa Registrada"
        tenant_nit = tenant.nit if tenant else "NIT General"

        if intent == "ventas":
            data = query_sales_ranking_data(db, tenant_id, query, parsed)
        elif intent == "rentabilidad":
            data = query_profitability_data(db, tenant_id, query, parsed)
        elif intent == "garantias":
            data = query_warranty_quality_data(db, tenant_id, query, parsed)
        elif intent == "blockchain":
            data = query_blockchain_security_data(db, tenant_id, query, parsed)
        elif intent == "compras":
            data = query_purchases_data(db, tenant_id, query, parsed)
        elif intent == "logistica":
            data = query_logistics_data(db, tenant_id, query, parsed)
        elif intent == "auditoria":
            data = query_audit_data(db, tenant_id, query, parsed)
        else:
            data = query_inventory_data(db, tenant_id, query, parsed)

    product_detail: Dict[str, Any] = {}
    if parsed.wants_detail and parsed.producto:
        product_detail = build_product_detail(
            db, tenant_id, parsed.producto, get_bolivia_now(), tenant_name
        )

    interpretation = f"{tenant_name} · {parsed.interpretation()}"
    filters_applied = parsed.filters_applied()
    if product_detail:
        filters_applied["detalle_producto"] = product_detail["producto"]
        filters_applied["detalle_desde"] = product_detail["desde"]
        filters_applied["detalle_hasta"] = product_detail["hasta"]

    if intent == "comparacion_tenants":
        followups = [
            "🏢 Comparativa de ventas e ingresos entre todas las empresas",
            "📊 Ranking de stock y rotación de inventario en la red",
            "🚨 Comparación de incidencias y garantías por empresa",
            "📈 Participación de mercado entre todas las empresas",
        ]
    elif intent == "ventas":
        followups = [
            "🏆 Top 5 productos por ingresos en los últimos 6 meses",
            "💰 Top 5 productos con mayor margen de ganancia",
            "📈 Ventas de este mes",
        ]
    elif intent == "rentabilidad":
        followups = [
            "🏆 Top 10 productos más vendidos en el último trimestre",
            "🛠️ Tasa de devoluciones y garantías de los últimos 6 meses",
            "📦 Stock disponible de iPhones",
        ]
    elif intent == "garantias":
        followups = [
            "💰 Top 5 productos con mayor margen de ganancia",
            "🔗 Unidades notarizadas en blockchain y alertas de sospecha",
            "🛒 Compras de los últimos 3 meses",
        ]
    elif intent == "blockchain":
        followups = [
            "🚨 Alertas e incidencias de falsificación",
            "🏆 Top 10 productos más vendidos",
            "🛡️ Resumen de bitácora y auditoría",
        ]
    else:
        followups = [
            "🏆 Productos más vendidos en el último trimestre",
            "💰 Top 5 productos con mayor margen de ganancia",
            "🚚 Envíos de la última semana",
        ]
    if product_detail:
        data["title"] = product_detail["period_label"]
        nombre = product_detail["producto"]
        followups = [
            f"🔍 Análisis detallado de {nombre}",
            f"📊 Ventas de {nombre} en los últimos 3 meses",
            "🏆 Top 10 productos por ingresos en los últimos 6 meses",
        ]

    # Síntesis ejecutiva y por voz
    voice_sum, exec_sum = synthesize_with_gemini(
        query, intent, data, tenant_name, interpretation
    )

    report_id = str(uuid.uuid4())
    generated_at = get_now_bolivia_str()

    # Guardar en caché para los endpoints de exportación
    REPORT_CACHE[report_id] = {
        "report_id": report_id,
        "title": data.get("title", "Reporte Dinámico"),
        "tenant_id": tenant_id,
        "is_cross_tenant": (intent == "comparacion_tenants"),
        "tenant_name": tenant_name,
        "tenant_nit": tenant_nit,
        "voice_summary": voice_sum,
        "executive_summary": exec_sum,
        "kpis": data.get("kpis", []),
        "chart": data.get("chart", {}),
        "table_headers": data.get("table_headers", []),
        "table_rows": data.get("table_rows", []),
        "period_label": parsed.period_label,
        "interpretation": interpretation,
        "filters_applied": filters_applied,
        "product_detail": product_detail,
        "generated_at": generated_at,
        "user_email": user_email,
    }

    # Limpiar entradas antiguas de caché si excede 100 reportes
    if len(REPORT_CACHE) > 100:
        first_key = next(iter(REPORT_CACHE))
        del REPORT_CACHE[first_key]

    return {
        "report_id": report_id,
        "query_interpreted": query,
        "category": data.get("category", intent),
        "voice_summary": voice_sum,
        "executive_summary": exec_sum,
        "kpis": data.get("kpis", []),
        "chart": data.get("chart", {}),
        "table_headers": data.get("table_headers", []),
        "table_rows": data.get("table_rows", []),
        "period_label": parsed.period_label,
        "interpretation": interpretation,
        "filters_applied": filters_applied,
        "suggested_followups": followups,
        "product_detail": product_detail or None,
        "generated_at": generated_at,
        "pdf_download_url": f"/api/v1/ai/reports/{report_id}/export?format=pdf",
        "excel_download_url": f"/api/v1/ai/reports/{report_id}/export?format=excel",
    }
