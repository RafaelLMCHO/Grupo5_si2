// ============================================================================
// Diagrama de Clases (Modelo Físico y Relacional) para Enterprise Architect — JScript
// Sistema de Trazabilidad Multi-Tenant con Blockchain (Grupo 5 - Sistemas de Información II)
//
// CARACTERÍSTICAS UML 2.5+:
//   - 53 Entidades: 43 tablas físicas + 10 especializaciones de actores y roles.
//   - 12 «association class»: Tablas asociativas que resuelven relaciones M:N y detalles con atributos propios.
//   - 14 Relaciones de COMPOSICIÓN («Aggregation» fuerte, rombo negro en el Todo, sin flechas).
//   - 10 Relaciones de HERENCIA / GENERALIZACIÓN («Generalization», triángulo cerrado en el Padre).
//   - 49 Asociaciones estándar con cardinalidades explícitas y líneas simples sin flechas.
//   - Geometría compacta (170 x 115 px) en grilla de 6 columnas para legibilidad óptima.
// ============================================================================

var Repo = (typeof Repository != "undefined") ? Repository : null;
if (Repo == null) {
    var eaApp = new ActiveXObject("EA.App");
    Repo = eaApp.Repository;
}

function Log(msg) {
    try { Session.Output("[Trazabilidad-EA] " + msg); } catch (e) { WScript.Echo(msg); }
}

// ---------------------------------------------------------------------------
// Mapeo de tipos SQL a tipos nativos de Enterprise Architect
// ---------------------------------------------------------------------------
function eaType(sqlType) {
    var t = (sqlType + "").toLowerCase();
    if (t.indexOf("uuid") >= 0) return "Guid";
    if (t.indexOf("boolean") >= 0) return "Boolean";
    if (t.indexOf("bigint") >= 0) return "Long";
    if (t.indexOf("integer") >= 0 || t.indexOf("serial") >= 0 || t.indexOf("int") >= 0) return "Integer";
    if (t.indexOf("numeric") >= 0 || t.indexOf("decimal") >= 0 || t.indexOf("money") >= 0) return "Currency";
    if (t.indexOf("timestamp") >= 0 || t.indexOf("datetime") >= 0 || t.indexOf("date") >= 0) return "Date";
    if (t.indexOf("json") >= 0) return "String";
    if (t.indexOf("text") >= 0 || t.indexOf("character") >= 0 || t.indexOf("char") >= 0 || t.indexOf("varchar") >= 0) return "String";
    return "String";
}

// ---------------------------------------------------------------------------
// 1. RELACIONES: [Origen, Destino, Verbo, CardOrigen, CardDestino, TipoRelacion]
// TipoRelacion:
//   - "Composition":    Composición UML (Rombo negro en Origen, Parte en Destino, sin flechas)
//   - "Generalization": Herencia UML (Origen = Subclase, Destino = Superclase)
//   - "Association":    Asociación estándar UML (Línea simple sin flechas)
// ---------------------------------------------------------------------------
var RELACIONES = [
    // === COMPOSICIONES FUERTES (Todo -> Parte, Rombo Negro) ===
    ["tenant",                        "tenant_backup",        "posee_backups",         "1", "0..*", "Composition"],
    ["tenant",                        "tenant_backup_schedule","programa_backups",      "1", "0..*", "Composition"],
    ["producto",                      "varianteproducto",     "compone_variantes",     "1", "1..*", "Composition"],
    ["compra",                        "compradetalle",        "compone_items",         "1", "1..*", "Composition"],
    ["recepcioncompra",               "recepciondetalle",     "compone_recepcion",     "1", "1..*", "Composition"],
    ["venta",                         "ventadetalle",         "compone_items_venta",   "1", "1..*", "Composition"],
    ["devolucion",                    "devolucionunidad",     "incluye_unidades_dev",  "1", "1..*", "Composition"],
    ["eventotrazabilidad",            "condiciontransporte",  "registra_telemetria",   "1", "0..1", "Composition"],
    ["eventotrazabilidad",            "registroblockchain",   "notariza_blockchain",  "1", "0..1", "Composition"],
    ["unidadproducto",                "codigoqr",             "genera_qr_publico",     "1", "1",    "Composition"],
    ["unidadproducto",                "documentounidad",      "adjunta_documentos",    "1", "0..*", "Composition"],
    ["unidadproducto",                "garantiaunidad",       "posee_garantia",        "1", "0..*", "Composition"],
    ["usuario",                       "tokenrecuperacion",    "solicita_recuperacion", "1", "0..*", "Composition"],
    ["usuario",                       "tokenrefresco",        "mantiene_sesiones",     "1", "0..*", "Composition"],

    // === HERENCIA / GENERALIZACIÓN (Subclase -> Superclase, Triángulo Cerrado) ===
    // --- Especializaciones de Usuario ---
    ["SuperAdministrador",            "usuario",              "",                      "",  "",     "Generalization"],
    ["AdministradorEmpresa",          "usuario",              "",                      "",  "",     "Generalization"],
    ["GestorOperaciones",             "usuario",              "",                      "",  "",     "Generalization"],
    ["AuditorCadena",                 "usuario",              "",                      "",  "",     "Generalization"],
    // --- Especializaciones de Actor de la Cadena ---
    ["ProveedorEEUU",                 "actorcadena",          "",                      "",  "",     "Generalization"],
    ["TransportistaInternacional",    "actorcadena",          "",                      "",  "",     "Generalization"],
    ["AduanaNacional",                "actorcadena",          "",                      "",  "",     "Generalization"],
    ["ImportadorMayorista",           "actorcadena",          "",                      "",  "",     "Generalization"],
    ["TiendaMinorista",               "actorcadena",          "",                      "",  "",     "Generalization"],
    ["ConsumidorFinal",               "actorcadena",          "",                      "",  "",     "Generalization"],

    // === ASOCIACIONES CON CLASES ASOCIADAS (Resolución de relaciones M:N y Detalles) ===
    ["usuariotenant",                 "usuario",              "pertenece_a_usuario",   "0..*", "1", "Association"],
    ["usuariotenant",                 "tenant",               "asociado_a_tenant",     "0..*", "1", "Association"],
    ["usuariotenantrol",              "usuariotenant",        "asigna_a_membresia",    "0..*", "1", "Association"],
    ["usuariotenantrol",              "rol",                  "concede_rol",           "0..*", "1", "Association"],
    ["rolpermiso",                    "rol",                  "contiene_rol",          "0..*", "1", "Association"],
    ["rolpermiso",                    "permiso",              "otorga_permiso",        "0..*", "1", "Association"],
    ["productocertificacion",         "producto",             "certifica_producto",    "0..*", "1", "Association"],
    ["productocertificacion",         "certificacion",        "valida_normativa",      "0..*", "1", "Association"],
    ["catalogotenant",                "tenant",               "catalogo_de_tenant",    "0..*", "1", "Association"],
    ["catalogotenant",                "varianteproducto",     "fija_precio_variante",  "0..*", "1", "Association"],
    ["enviounidad",                   "envio",                "agrupada_en_envio",     "0..*", "1", "Association"],
    ["enviounidad",                   "unidadproducto",       "incluye_unidad_fisica", "0..*", "1", "Association"],
    ["eventounidad",                  "eventotrazabilidad",   "afecta_en_evento",      "0..*", "1", "Association"],
    ["eventounidad",                  "unidadproducto",       "trazabilidad_de_unidad","0..*", "1", "Association"],
    ["ventaunidad",                   "ventadetalle",         "despacha_item",         "0..*", "1", "Association"],
    ["ventaunidad",                   "unidadproducto",       "entrega_unidad_serial", "0..*", "1", "Association"],
    ["devolucionunidad",              "devolucion",           "reingresa_por_devolucion","0..*","1","Association"],
    ["devolucionunidad",              "unidadproducto",       "reingresa_unidad",      "0..*", "1", "Association"],
    ["compradetalle",                 "varianteproducto",     "ordena_variante",       "0..*", "1", "Association"],
    ["recepciondetalle",              "varianteproducto",     "recibe_variante",       "0..*", "1", "Association"],
    ["ventadetalle",                  "varianteproducto",     "vende_variante",        "0..*", "1", "Association"],

    // === ASOCIACIONES REGULARES DEL SISTEMA ===
    // --- Núcleo Multi-Tenant y Auditoría (p0, p1) ---
    ["actorcadena",                   "tenant",               "opera_en_tenant",       "0..*", "1", "Association"],
    ["ubicacion",                     "tenant",               "instalacion_de_tenant", "0..*", "1", "Association"],
    ["ubicacion",                     "actorcadena",          "pertenece_a_actor",     "0..*", "1", "Association"],
    ["tokenrecuperacion",             "tenant",               "pertenece_a_tenant",    "0..*", "0..1","Association"],
    ["tokenrefresco",                 "tenant",               "pertenece_a_tenant",    "0..*", "0..1","Association"],
    ["bitacora",                      "usuariotenant",        "audita_operacion",      "0..*", "1", "Association"],
    ["notificacion",                  "usuariotenant",        "notifica_a_miembro",    "0..*", "1", "Association"],
    ["tenant_backup",                 "usuario",              "creado_por_usuario",    "0..*", "1", "Association"],
    ["tenant_backup_schedule",        "usuario",              "programado_por_usuario","0..*", "1", "Association"],

    // --- Catálogo y Clasificación (p2) ---
    ["producto",                      "categoria",            "clasificado_en",        "0..*", "1", "Association"],

    // --- Inventario Físico y Trazabilidad Individual (p4) ---
    ["unidadproducto",                "tenant",               "inventariada_en_tenant","0..*", "1", "Association"],
    ["unidadproducto",                "varianteproducto",     "es_instancia_de",       "0..*", "1", "Association"],
    ["unidadproducto",                "recepciondetalle",     "ingresa_por_recepcion", "0..*", "0..1","Association"],
    ["unidadproducto",                "actorcadena",          "custodiado_por",        "0..*", "0..1","Association"],
    ["unidadproducto",                "ubicacion",            "almacenado_en",         "0..*", "0..1","Association"],
    ["consultatrazabilidad",          "codigoqr",             "escanea_qr",            "0..*", "1", "Association"],

    // --- Cadena Logística y Compras (p5, p6) ---
    ["compra",                        "tenant",               "emitida_por_tenant",    "0..*", "1", "Association"],
    ["compra",                        "actorcadena",          "proveedor_internacional","0..*","1", "Association"],
    ["recepcioncompra",               "compra",               "recibe_orden_compra",   "0..*", "1", "Association"],
    ["recepcioncompra",               "ubicacion",            "recibida_en_almacen",   "0..*", "1", "Association"],
    ["envio",                         "tenant",               "envio_de_tenant",       "0..*", "1", "Association"],
    ["envio",                         "actorcadena",          "origen_despacho",       "0..*", "1", "Association"],
    ["envio",                         "actorcadena",          "destino_recepcion",     "0..*", "1", "Association"],
    ["envio",                         "actorcadena",          "transportado_por",      "0..*", "0..1","Association"],

    // --- Eventos de Trazabilidad, Telemetría y Alertas (p6, p7) ---
    ["eventotrazabilidad",            "tenant",               "ocurre_en_tenant",      "0..*", "1", "Association"],
    ["eventotrazabilidad",            "actorcadena",          "actor_origen_custodia", "0..*", "0..1","Association"],
    ["eventotrazabilidad",            "actorcadena",          "actor_destino_custodia","0..*", "0..1","Association"],
    ["eventotrazabilidad",            "ubicacion",            "ocurre_en_ubicacion",   "0..*", "1", "Association"],
    ["eventotrazabilidad",            "usuario",              "operado_por_usuario",   "0..*", "1", "Association"],
    ["alerta",                        "tenant",               "alerta_de_tenant",      "0..*", "1", "Association"],
    ["alerta",                        "unidadproducto",       "afecta_unidad",         "0..*", "0..1","Association"],
    ["alerta",                        "eventotrazabilidad",   "originada_en_evento",   "0..*", "0..1","Association"],
    ["alerta",                        "usuario",              "resuelta_por_usuario",  "0..*", "0..1","Association"],

    // --- Ventas y Postventa (p8) ---
    ["venta",                         "tenant",               "venta_de_tenant",       "0..*", "1", "Association"],
    ["venta",                         "actorcadena",          "comprador_cliente",     "0..*", "1", "Association"],
    ["pago",                          "venta",                "pago_de_venta",         "0..*", "1", "Association"],
    ["devolucion",                    "venta",                "reclamo_de_venta",      "0..*", "1", "Association"]
];

// ---------------------------------------------------------------------------
// 2. TABLAS Y CLASES: [nombre, [ [columna, tipoSQL, estereotipo] ], estereotipo_clase]
// Total: 53 entidades (43 físicas + 10 roles y actores especializados)
// ---------------------------------------------------------------------------
var TABLAS = [
    // --- PAQUETE P0: PLATAFORMA MULTI-TENANT, USUARIOS Y RBAC ---
    ["tenant", [
        ["idtenant", "SERIAL", "PK"], ["nombre", "VARCHAR(100)", null], ["razonsocial", "VARCHAR(100)", null], ["nit", "VARCHAR(50)", null], ["email", "VARCHAR(100)", null], ["telefono", "VARCHAR(20)", null], ["activo", "BOOLEAN", null], ["configuracion", "JSONB", null], ["fechacreacion", "TIMESTAMP", null]
    ], "table"],
    ["usuario", [
        ["idusuario", "SERIAL", "PK"], ["nombrecompleto", "VARCHAR(100)", null], ["email", "VARCHAR(100)", null], ["contrasenahash", "VARCHAR(255)", null], ["fecharegistro", "TIMESTAMP", null], ["activo", "BOOLEAN", null]
    ], "table"],
    ["usuariotenant", [
        ["idusuariotenant", "SERIAL", "PK"], ["idusuario", "INTEGER", "FK"], ["idtenant", "INTEGER", "FK"], ["fechaasociacion", "TIMESTAMP", null], ["activo", "BOOLEAN", null]
    ], "association class"],
    ["rol", [
        ["idrol", "SERIAL", "PK"], ["nombrerol", "VARCHAR(50)", null], ["descripcion", "VARCHAR(200)", null]
    ], "table"],
    ["permiso", [
        ["idpermiso", "SERIAL", "PK"], ["nombrepermiso", "VARCHAR(100)", null], ["descripcion", "VARCHAR(200)", null], ["modulo", "VARCHAR(50)", null]
    ], "table"],
    ["rolpermiso", [
        ["idrolpermiso", "SERIAL", "PK"], ["idrol", "INTEGER", "FK"], ["idpermiso", "INTEGER", "FK"]
    ], "association class"],
    ["usuariotenantrol", [
        ["idusuariotenantrol", "SERIAL", "PK"], ["idusuariotenant", "INTEGER", "FK"], ["idrol", "INTEGER", "FK"], ["fechaasignacion", "TIMESTAMP", null]
    ], "association class"],
    ["tokenrecuperacion", [
        ["idtoken", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idusuario", "INTEGER", "FK"], ["tokenhash", "VARCHAR(255)", null], ["expiraen", "TIMESTAMP", null], ["usadoen", "TIMESTAMP", null], ["fechacreacion", "TIMESTAMP", null]
    ], "table"],
    ["tokenrefresco", [
        ["idtoken", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idusuario", "INTEGER", "FK"], ["tokenhash", "VARCHAR(255)", null], ["expiraen", "TIMESTAMP", null], ["revocado", "BOOLEAN", null], ["fechacreacion", "TIMESTAMP", null]
    ], "table"],
    // --- ESPECIALIZACIONES DE ROLES (HERENCIA DE USUARIO) ---
    ["SuperAdministrador", [
        ["permisos_globales", "String", null], ["audita_tenants", "Boolean", null]
    ], "role"],
    ["AdministradorEmpresa", [
        ["gestion_tenant", "Boolean", null], ["politicas_seguridad", "String", null]
    ], "role"],
    ["GestorOperaciones", [
        ["gestion_logistica", "Boolean", null], ["supervisa_almacen", "Boolean", null]
    ], "role"],
    ["AuditorCadena", [
        ["audita_blockchain", "Boolean", null], ["certificacion_iso", "String", null]
    ], "role"],
    // --- PAQUETE P1: BACKUPS Y CONTINUIDAD OPERATIVA ---
    ["tenant_backup", [
        ["idbackup", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idusuario_creador", "INTEGER", "FK"], ["nombre_archivo", "VARCHAR(255)", null], ["cloud_storage", "VARCHAR(50)", null], ["cloud_path", "VARCHAR(500)", null], ["peso_bytes", "BIGINT", null], ["checksum_sha256", "VARCHAR(64)", null], ["estado", "VARCHAR(30)", null], ["mensaje_error", "TEXT", null], ["total_registros", "INTEGER", null], ["fechacreacion", "TIMESTAMP", null]
    ], "table"],
    ["tenant_backup_schedule", [
        ["idschedule", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idusuario_creador", "INTEGER", "FK"], ["fecha_hora_programada", "TIMESTAMP", null], ["frecuencia", "VARCHAR(20)", null], ["activo", "BOOLEAN", null], ["estado", "VARCHAR(20)", null], ["ultimo_ejecutado", "TIMESTAMP", null], ["proxima_ejecucion", "TIMESTAMP", null], ["mensaje_resultado", "TEXT", null], ["fechacreacion", "TIMESTAMP", null]
    ], "table"],
    ["bitacora", [
        ["idbitacora", "SERIAL", "PK"], ["idusuariotenant", "INTEGER", "FK"], ["accion", "VARCHAR(100)", null], ["modulo", "VARCHAR(50)", null], ["ip", "VARCHAR(45)", null], ["detalles", "JSONB", null], ["fechahora", "TIMESTAMP", null]
    ], "table"],
    ["notificacion", [
        ["idnotificacion", "SERIAL", "PK"], ["idusuariotenant", "INTEGER", "FK"], ["titulo", "VARCHAR(150)", null], ["contenido", "TEXT", null], ["leida", "BOOLEAN", null], ["fechaenvio", "TIMESTAMP", null], ["enlaceaccion", "VARCHAR(255)", null]
    ], "table"],
    // --- PAQUETE P2: CATÁLOGO DE HARDWARE Y CERTIFICACIONES ---
    ["categoria", [
        ["idcategoria", "SERIAL", "PK"], ["nombrecategoria", "VARCHAR(100)", null], ["descripcion", "TEXT", null]
    ], "table"],
    ["producto", [
        ["idproducto", "SERIAL", "PK"], ["idcategoria", "INTEGER", "FK"], ["nombre", "VARCHAR(100)", null], ["modelo", "VARCHAR(50)", null], ["paisorigen", "VARCHAR(50)", null], ["descripcion", "TEXT", null], ["imagenurl", "VARCHAR(255)", null], ["fechacreacion", "TIMESTAMP", null], ["activo", "BOOLEAN", null]
    ], "table"],
    ["varianteproducto", [
        ["idvariante", "SERIAL", "PK"], ["idproducto", "INTEGER", "FK"], ["capacidad", "VARCHAR(50)", null], ["color", "VARCHAR(50)", null], ["sku", "VARCHAR(50)", null], ["preciousd", "NUMERIC(10,2)", null]
    ], "table"],
    ["certificacion", [
        ["idcertificacion", "SERIAL", "PK"], ["nombre", "VARCHAR(100)", null], ["entidademisora", "VARCHAR(100)", null], ["descripcion", "TEXT", null], ["logourl", "VARCHAR(255)", null]
    ], "table"],
    ["productocertificacion", [
        ["idproductocertificacion", "SERIAL", "PK"], ["idproducto", "INTEGER", "FK"], ["idcertificacion", "INTEGER", "FK"], ["fechacertificacion", "DATE", null], ["fechavencimiento", "DATE", null], ["numerocertificado", "VARCHAR(100)", null]
    ], "association class"],
    ["catalogotenant", [
        ["idcatalogotenant", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idvariante", "INTEGER", "FK"], ["skuinterno", "VARCHAR(50)", null], ["precioventa", "NUMERIC(10,2)", null], ["costopromedio", "NUMERIC(10,2)", null], ["activo", "BOOLEAN", null]
    ], "association class"],
    // --- PAQUETE P3: CADENA DE SUMINISTRO Y UBICACIONES ---
    ["actorcadena", [
        ["idactor", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["nombre", "VARCHAR(100)", null], ["razonsocial", "VARCHAR(100)", null], ["nit", "VARCHAR(50)", null], ["email", "VARCHAR(100)", null], ["telefono", "VARCHAR(50)", null], ["tipoactor", "tipo_actor_enum", "enum"]
    ], "table"],
    ["ubicacion", [
        ["idubicacion", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idactor", "INTEGER", "FK"], ["nombre", "VARCHAR(100)", null], ["direccion", "TEXT", null], ["ciudad", "VARCHAR(50)", null], ["pais", "VARCHAR(50)", null], ["tipoubicacion", "tipo_ubicacion_enum", "enum"], ["coordenadaslatitud", "NUMERIC(10,8)", null], ["coordenadaslongitud", "NUMERIC(11,8)", null]
    ], "table"],
    // --- ESPECIALIZACIONES DE ACTORES (HERENCIA DE ACTOR CADENA) ---
    ["ProveedorEEUU", [
        ["codigo_distribuidor_apple", "String", null], ["pais_sede", "String", null]
    ], "role"],
    ["TransportistaInternacional", [
        ["licencia_transporte_imo_iata", "String", null], ["flota_monitoreada_iot", "Boolean", null]
    ], "role"],
    ["AduanaNacional", [
        ["codigo_recinto_aduanero", "String", null], ["jurisdiccion", "String", null]
    ], "role"],
    ["ImportadorMayorista", [
        ["registro_importador_aduana", "String", null], ["capacidad_almacen_m3", "Numeric", null]
    ], "role"],
    ["TiendaMinorista", [
        ["codigo_sucursal_retail", "String", null], ["punto_pos_autorizado", "Boolean", null]
    ], "role"],
    ["ConsumidorFinal", [
        ["registro_garantia_activada", "Boolean", null], ["app_movil_instalada", "Boolean", null]
    ], "role"],
    // --- PAQUETE P4: INVENTARIO SERIALIZADO, QR Y DOCUMENTACIÓN TÉCNICA ---
    ["unidadproducto", [
        ["idunidad", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idvariante", "INTEGER", "FK"], ["idrecepciondetalle", "INTEGER", "FK"], ["numeroserie", "VARCHAR(100)", null], ["imei1", "VARCHAR(50)", null], ["imei2", "VARCHAR(50)", null], ["eid", "VARCHAR(50)", null], ["uuidpublico", "VARCHAR(100)", null], ["idcustodioactual", "INTEGER", "FK"], ["idubicacionactual", "INTEGER", "FK"], ["estado", "estado_unidad_enum", "enum"], ["fechaingreso", "TIMESTAMP", null], ["fechaventa", "TIMESTAMP", null]
    ], "table"],
    ["codigoqr", [
        ["idcodigoqr", "SERIAL", "PK"], ["idunidad", "INTEGER", "FK"], ["tokenpublico", "VARCHAR(100)", null], ["url", "VARCHAR(255)", null], ["fechageneracion", "TIMESTAMP", null], ["activo", "BOOLEAN", null]
    ], "table"],
    ["consultatrazabilidad", [
        ["idconsulta", "SERIAL", "PK"], ["idcodigoqr", "INTEGER", "FK"], ["fechahora", "TIMESTAMP", null], ["ip", "VARCHAR(45)", null], ["paisaproximado", "VARCHAR(50)", null], ["useragent", "TEXT", null]
    ], "table"],
    ["documentounidad", [
        ["iddocumento", "SERIAL", "PK"], ["idunidad", "INTEGER", "FK"], ["nombre", "VARCHAR(100)", null], ["urlarchivo", "VARCHAR(255)", null], ["hasharchivo", "VARCHAR(255)", null], ["fechaemision", "DATE", null], ["fechavencimiento", "DATE", null], ["tipodocumento", "tipo_documento_enum", "enum"]
    ], "table"],
    ["garantiaunidad", [
        ["idgarantia", "SERIAL", "PK"], ["idunidad", "INTEGER", "FK"], ["fechainicio", "DATE", null], ["fechafin", "DATE", null], ["proveedor", "VARCHAR(100)", null], ["condiciones", "TEXT", null]
    ], "table"],
    // --- PAQUETE P5: COMPRAS INTERNACIONALES Y RECEPCIÓN EN ALMACÉN ---
    ["compra", [
        ["idcompra", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idproveedor", "INTEGER", "FK"], ["numeroorden", "VARCHAR(50)", null], ["fechacompra", "DATE", null], ["totalusd", "NUMERIC(10,2)", null], ["estado", "estado_compra_enum", "enum"]
    ], "table"],
    ["compradetalle", [
        ["idcompradetalle", "SERIAL", "PK"], ["idcompra", "INTEGER", "FK"], ["idvariante", "INTEGER", "FK"], ["cantidad", "INTEGER", null], ["costounitariousd", "NUMERIC(10,2)", null], ["subtotalusd", "NUMERIC(10,2)", null]
    ], "association class"],
    ["recepcioncompra", [
        ["idrecepcion", "SERIAL", "PK"], ["idcompra", "INTEGER", "FK"], ["idubicacion", "INTEGER", "FK"], ["fecharecepcion", "TIMESTAMP", null], ["numerodocumento", "VARCHAR(50)", null], ["estado", "estado_recepcion_enum", "enum"]
    ], "table"],
    ["recepciondetalle", [
        ["idrecepciondetalle", "SERIAL", "PK"], ["idrecepcion", "INTEGER", "FK"], ["idvariante", "INTEGER", "FK"], ["cantidadesperada", "INTEGER", null], ["cantidadrecibida", "INTEGER", null]
    ], "association class"],
    // --- PAQUETE P6: ENVÍOS LOGÍSTICOS, TELEMETRÍA IOT Y ALERTAS ---
    ["envio", [
        ["idenvio", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idactororigen", "INTEGER", "FK"], ["idactordestino", "INTEGER", "FK"], ["idtransportista", "INTEGER", "FK"], ["codigoenvio", "VARCHAR(50)", null], ["fechasalida", "TIMESTAMP", null], ["fechaestimada", "TIMESTAMP", null], ["fechaentrega", "TIMESTAMP", null], ["estado", "estado_envio_enum", "enum"], ["trackingexterno", "VARCHAR(100)", null]
    ], "table"],
    ["enviounidad", [
        ["idenviounidad", "SERIAL", "PK"], ["idenvio", "INTEGER", "FK"], ["idunidad", "INTEGER", "FK"]
    ], "association class"],
    ["condiciontransporte", [
        ["idcondicion", "SERIAL", "PK"], ["idevento", "INTEGER", "FK"], ["temperatura", "NUMERIC(5,2)", null], ["humedad", "NUMERIC(5,2)", null], ["presion", "NUMERIC(7,2)", null], ["nivelvibracion", "NUMERIC(5,2)", null], ["timestampregistro", "TIMESTAMP", null], ["fuentedatos", "VARCHAR(50)", null]
    ], "table"],
    ["alerta", [
        ["idalerta", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idunidad", "INTEGER", "FK"], ["idevento", "INTEGER", "FK"], ["tipoalerta", "tipo_alerta_enum", "enum"], ["descripcion", "TEXT", null], ["gravedad", "gravedad_alerta_enum", "enum"], ["fechadeteccion", "TIMESTAMP", null], ["fecharesolucion", "TIMESTAMP", null], ["estado", "estado_alerta_enum", "enum"], ["idusuarioresolutor", "INTEGER", "FK"]
    ], "table"],
    // --- PAQUETE P7: TRAZABILIDAD Y NOTARIZACIÓN BLOCKCHAIN ---
    ["eventotrazabilidad", [
        ["idevento", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["tipoevento", "tipo_evento_enum", "enum"], ["fechahora", "TIMESTAMP", null], ["idactororigen", "INTEGER", "FK"], ["idactordestino", "INTEGER", "FK"], ["idubicacion", "INTEGER", "FK"], ["idusuarioresponsable", "INTEGER", "FK"], ["descripcion", "TEXT", null], ["payloadhash", "VARCHAR(255)", null], ["estadoverificacion", "estado_verificacion_enum", "enum"]
    ], "table"],
    ["eventounidad", [
        ["ideventounidad", "SERIAL", "PK"], ["idevento", "INTEGER", "FK"], ["idunidad", "INTEGER", "FK"]
    ], "association class"],
    ["registroblockchain", [
        ["idregistro", "SERIAL", "PK"], ["idevento", "INTEGER", "FK"], ["payloadhash", "VARCHAR(255)", null], ["txhash", "VARCHAR(255)", null], ["blocknumber", "BIGINT", null], ["network", "VARCHAR(50)", null], ["chainid", "VARCHAR(50)", null], ["contractaddress", "VARCHAR(100)", null], ["fechaenvio", "TIMESTAMP", null], ["fechaconfirmacion", "TIMESTAMP", null], ["estado", "estado_confirmacion_enum", "enum"], ["numeroconfirmaciones", "INTEGER", null], ["mensajeerror", "TEXT", null]
    ], "table"],
    // --- PAQUETE P8: VENTAS COMERCIALES, PAGOS Y DEVOLUCIONES (RMA) ---
    ["venta", [
        ["idventa", "SERIAL", "PK"], ["idtenant", "INTEGER", "FK"], ["idcliente", "INTEGER", "FK"], ["fechaventa", "TIMESTAMP", null], ["total", "NUMERIC(10,2)", null], ["estado", "estado_venta_enum", "enum"]
    ], "table"],
    ["ventadetalle", [
        ["idventadetalle", "SERIAL", "PK"], ["idventa", "INTEGER", "FK"], ["idvariante", "INTEGER", "FK"], ["cantidad", "INTEGER", null], ["preciounitario", "NUMERIC(10,2)", null], ["subtotal", "NUMERIC(10,2)", null]
    ], "association class"],
    ["ventaunidad", [
        ["idventaunidad", "SERIAL", "PK"], ["idventadetalle", "INTEGER", "FK"], ["idunidad", "INTEGER", "FK"]
    ], "association class"],
    ["pago", [
        ["idpago", "SERIAL", "PK"], ["idventa", "INTEGER", "FK"], ["metodopago", "metodo_pago_enum", "enum"], ["monto", "NUMERIC(10,2)", null], ["fechapago", "TIMESTAMP", null], ["estado", "estado_pago_enum", "enum"]
    ], "table"],
    ["devolucion", [
        ["iddevolucion", "SERIAL", "PK"], ["idventa", "INTEGER", "FK"], ["fechadevolucion", "TIMESTAMP", null], ["motivo", "motivo_devolucion_enum", "enum"], ["descripcion", "TEXT", null], ["estado", "estado_devolucion_enum", "enum"]
    ], "table"],
    ["devolucionunidad", [
        ["iddevolucionunidad", "SERIAL", "PK"], ["iddevolucion", "INTEGER", "FK"], ["idunidad", "INTEGER", "FK"]
    ], "association class"]
];

// ============================================================================
// FUNCIÓN PRINCIPAL DE EJECUCIÓN
// ============================================================================
function Main() {
    Log("Iniciando creación de Modelo UML de Clases y Datos (Trazabilidad Blockchain Grupo 5)...");

    var packageDestino = Repo.GetTreeSelectedPackage();
    if (packageDestino == null) {
        if (Repo.Models.Count > 0) {
            packageDestino = Repo.Models.GetAt(0);
        } else {
            Session.Prompt("Error: No se encontró ningún modelo ni paquete seleccionado en Enterprise Architect.", 0);
            return;
        }
    }

    // Crear paquete contenedor
    var model = packageDestino.Packages.AddNew("Modelo de Clases y Datos — Trazabilidad Blockchain", "");
    model.Update();

    var elementos = {};
    var total = TABLAS.length;

    Log("Creando " + total + " entidades estereotipadas («table», «association class», «role»)...");

    // 1) Crear cada entidad con su estereotipo y atributos
    for (var i = 0; i < total; i++) {
        var tabla = TABLAS[i][0];
        var campos = TABLAS[i][1];
        var estereoClase = (TABLAS[i].length > 2 && TABLAS[i][2] != null) ? TABLAS[i][2] : "table";

        var cls = model.Elements.AddNew(tabla, "Class");
        cls.Stereotype = estereoClase;
        cls.Update();

        for (var j = 0; j < campos.length; j++) {
            var campo = campos[j][0];
            var tipo  = campos[j][1];
            var est   = campos[j][2];
            var a = cls.Attributes.AddNew(campo, eaType(tipo));
            if (est != null) a.Stereotype = est;
            a.Update();
        }
        cls.Update();
        elementos[tabla] = cls;
    }

    Log("Creando " + RELACIONES.length + " relaciones (Composiciones, Herencias y Asociaciones)...");

    // 2) Crear relaciones tipadas (Composición, Generalización, Asociación)
    var creadas = 0;
    var nComp = 0, nGen = 0, nAssoc = 0;

    for (var r = 0; r < RELACIONES.length; r++) {
        var rel = RELACIONES[r];
        var origen  = rel[0];
        var destino = rel[1];
        var verbo   = rel[2];
        var cardOrigen  = rel[3];
        var cardDestino = rel[4];
        var tipoRel = (rel.length > 5 && rel[5] != null) ? rel[5] : "Association";

        if (elementos[origen] == null || elementos[destino] == null) {
            Log("Aviso: No se pudo relacionar " + origen + " con " + destino + " (entidad no encontrada).");
            continue;
        }

        if (tipoRel == "Generalization") {
            // HERENCIA: Origen = Subclase, Destino = Superclase. Flecha triangular cerrada en Destino.
            var conn = elementos[origen].Connectors.AddNew("", "Generalization");
            conn.ClientID    = elementos[origen].ElementID;
            conn.SupplierID  = elementos[destino].ElementID;
            conn.Direction   = "Source -> Destination";
            conn.Update();
            creadas++;
            nGen++;
        } else if (tipoRel == "Composition") {
            // COMPOSICIÓN: Origen = Todo (Rombo Negro), Destino = Parte. Línea sólida sin flechas.
            var conn = elementos[origen].Connectors.AddNew(verbo, "Aggregation");
            conn.ClientID    = elementos[origen].ElementID;
            conn.SupplierID  = elementos[destino].ElementID;
            conn.Subtype     = "Strong";
            conn.ClientEnd.Aggregation = 2; // 2 = Composite (Rombo negro en Origen)
            conn.ClientEnd.Cardinality = cardOrigen;
            conn.SupplierEnd.Cardinality = cardDestino;
            conn.Direction   = "Unspecified";
            conn.Update();
            creadas++;
            nComp++;
        } else {
            // ASOCIACIÓN ESTÁNDAR: Línea simple sin flechas con cardinalidades.
            var conn = elementos[origen].Connectors.AddNew(verbo, "Association");
            conn.ClientID    = elementos[origen].ElementID;
            conn.SupplierID  = elementos[destino].ElementID;
            conn.ClientEnd.Cardinality  = cardOrigen;
            conn.SupplierEnd.Cardinality = cardDestino;
            conn.Direction   = "Unspecified";
            conn.Update();
            creadas++;
            nAssoc++;
        }
    }

    Log("Creando diagrama y posicionando elementos en grilla compacta...");

    // 3) Crear el diagrama y distribuir las entidades
    var diagram = model.Diagrams.AddNew("Diagrama de Clases BD — Trazabilidad Blockchain", "Logical");
    diagram.Update();

    // Distribución compacta en matriz de 6 columnas
    var cols = 6;
    var ancho = 170;
    var alto = 115;
    var gapX = 85;
    var gapY = 75;
    var x0 = 40;
    var y0 = 40;

    for (var k = 0; k < total; k++) {
        var nombre = TABLAS[k][0];
        var obj = elementos[nombre];
        if (obj == null) continue;

        var fila = Math.floor(k / cols);
        var col = k % cols;
        var left   = x0 + col * (ancho + gapX);
        var top    = y0 + fila * (alto + gapY);

        var dObj = diagram.DiagramObjects.AddNew("l=" + left + ";r=" + (left + ancho) + ";t=" + top + ";b=" + (top + alto) + ";", "");
        dObj.ElementID = obj.ElementID;
        dObj.Update();
    }

    diagram.Update();
    Repo.RefreshModelView(diagram.DiagramID);
    Repo.OpenDiagram(diagram.DiagramID);

    Log("¡Éxito! Generado con " + total + " entidades (" + nComp + " Composiciones, " + nGen + " Herencias, " + nAssoc + " Asociaciones).");
    try {
        Session.Prompt("¡Diagrama de Clases UML actualizado exitosamente!\n" +
                       "- Total entidades: " + total + " (incluye 12 «association class» y 10 «role»)\n" +
                       "- Composiciones (Rombo negro): " + nComp + "\n" +
                       "- Herencias (Generalización): " + nGen + "\n" +
                       "- Asociaciones simples: " + nAssoc, 0);
    } catch(e) {}
}

Main();
// ============================================================================
// FIN DEL SCRIPT
// ============================================================================
