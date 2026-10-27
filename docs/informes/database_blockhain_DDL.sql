-- =============================================================================
-- SISTEMA DE TRAZABILIDAD MULTI-TENANT CON BLOCKCHAIN PARA IMPORTACIÓN DE HARDWARE
-- Proyecto: Grupo 5 - Sistemas de Información II
-- Archivo: database_blockhain_DDL.sql
-- Motor: PostgreSQL 15+ / Supabase
-- Total de Tablas: 43
--
-- Estructura del script:
--  1. Tipos Enumerados (ENUMs de dominio)
--  2. Definición DDL de Tablas (Columnas, Tipos y Llaves Primarias)
--     - Cada tabla incluye su comment de -- Nombre y -- Breve descripción
--  3. Declaración Externa de Relaciones (Claves Foráneas / Constraints)
--  4. Índices de Rendimiento y Búsqueda
-- =============================================================================

-- =============================================================================
-- SECCIÓN 1: TIPOS ENUMERADOS (DOMINIO DEL SISTEMA)
-- =============================================================================

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_actor_enum') THEN
        CREATE TYPE tipo_actor_enum AS ENUM (
            'PROVEEDOR_EEUU',
            'TRANSPORTISTA_INTERNACIONAL',
            'ADUANA',
            'IMPORTADOR',
            'DISTRIBUIDOR',
            'TIENDA',
            'CONSUMIDOR'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_ubicacion_enum') THEN
        CREATE TYPE tipo_ubicacion_enum AS ENUM (
            'ALMACEN',
            'TIENDA',
            'PUERTO',
            'AEROPUERTO',
            'ADUANA',
            'OFICINA',
            'OTRO'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_unidad_enum') THEN
        CREATE TYPE estado_unidad_enum AS ENUM (
            'disponible',
            'vendido',
            'en_transito',
            'devuelto',
            'retirado'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_documento_enum') THEN
        CREATE TYPE tipo_documento_enum AS ENUM (
            'factura_compra',
            'certificado_importacion',
            'comprobante_garantia',
            'certificado_autenticidad',
            'declaracion_aduanera',
            'poliza_seguro',
            'informe_tecnico',
            'otro'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_evento_enum') THEN
        CREATE TYPE tipo_evento_enum AS ENUM (
            'fabricacion',
            'control_calidad_apple',
            'empaque',
            'despacho_origen',
            'exportacion',
            'embarque',
            'transporte_maritimo',
            'transporte_aereo',
            'transito',
            'llegada_puerto',
            'llegada_aduana',
            'despacho_aduanero',
            'inspeccion_aduanera',
            'liberacion_aduanera',
            'transporte_terrestre',
            'recepcion_almacen',
            'almacenamiento',
            'despacho_tienda',
            'recepcion_tienda',
            'venta',
            'venta_consumidor',
            'cambio_custodia',
            'inspeccion_calidad',
            'alerta_anomalia',
            'devolucion',
            'retiro'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_verificacion_enum') THEN
        CREATE TYPE estado_verificacion_enum AS ENUM (
            'pendiente',
            'verificado',
            'fallido'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_alerta_enum') THEN
        CREATE TYPE tipo_alerta_enum AS ENUM (
            'temperatura',
            'humedad',
            'vibracion',
            'presion',
            'ruta_no_autorizada',
            'retraso_aduanero',
            'vencimiento_garantia',
            'fraude_autenticidad',
            'violacion_sello',
            'inconsistencia_cadena'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gravedad_alerta_enum') THEN
        CREATE TYPE gravedad_alerta_enum AS ENUM (
            'baja',
            'media',
            'alta',
            'critica'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_alerta_enum') THEN
        CREATE TYPE estado_alerta_enum AS ENUM (
            'pendiente',
            'en_proceso',
            'resuelta'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_compra_enum') THEN
        CREATE TYPE estado_compra_enum AS ENUM (
            'pendiente',
            'enviada',
            'recibida_parcial',
            'recibida_total',
            'cancelada'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_recepcion_enum') THEN
        CREATE TYPE estado_recepcion_enum AS ENUM (
            'pendiente',
            'parcial',
            'en_proceso',
            'completa',
            'completada',
            'con_discrepancias',
            'rechazada'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_envio_enum') THEN
        CREATE TYPE estado_envio_enum AS ENUM (
            'preparacion',
            'en_transito',
            'aduanas',
            'entregado',
            'retrasado',
            'cancelado'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_confirmacion_enum') THEN
        CREATE TYPE estado_confirmacion_enum AS ENUM (
            'pendiente',
            'confirmado',
            'rechazado'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_venta_enum') THEN
        CREATE TYPE estado_venta_enum AS ENUM (
            'pendiente',
            'pagada',
            'completada',
            'enviada',
            'entregada',
            'cancelada',
            'devuelta'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'metodo_pago_enum') THEN
        CREATE TYPE metodo_pago_enum AS ENUM (
            'efectivo',
            'tarjeta_credito',
            'tarjeta_debito',
            'transferencia',
            'qr_codigo',
            'criptomoneda'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_pago_enum') THEN
        CREATE TYPE estado_pago_enum AS ENUM (
            'pendiente',
            'completado',
            'fallido',
            'rechazado',
            'reembolsado'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'motivo_devolucion_enum') THEN
        CREATE TYPE motivo_devolucion_enum AS ENUM (
            'defecto_fabrica',
            'defecto_fabricacion',
            'dano_transporte',
            'producto_incorrecto',
            'insatisfaccion_cliente',
            'insatisfaccion',
            'garantia',
            'otro'
        );
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_devolucion_enum') THEN
        CREATE TYPE estado_devolucion_enum AS ENUM (
            'solicitada',
            'aprobada',
            'rechazada',
            'en_proceso',
            'procesada',
            'completada'
        );
    END IF;
END $$;


-- =============================================================================
-- SECCIÓN 2: DEFINICIÓN DE TABLAS (DDL)
-- =============================================================================

-- =============================================================================
-- Nombre: tenant
-- Breve descripción: Entidad raíz multi-tenant. Representa empresas importadoras, distribuidoras y cadenas comerciales con aislamiento lógico de datos.
-- =============================================================================
CREATE TABLE tenant (
    idtenant SERIAL NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    razonsocial VARCHAR(100) NOT NULL,
    nit VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE,
    configuracion JSONB,
    fechacreacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_tenant PRIMARY KEY (idtenant)
);

-- =============================================================================
-- Nombre: usuario
-- Breve descripción: Usuarios globales del sistema (administradores, operadores, auditores) con autenticación centralizada por credenciales seguras.
-- =============================================================================
CREATE TABLE usuario (
    idusuario SERIAL NOT NULL,
    nombrecompleto VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    contrasenahash VARCHAR(255) NOT NULL,
    fecharegistro TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT pk_usuario PRIMARY KEY (idusuario),
    CONSTRAINT uq_usuario_email UNIQUE (email)
);

-- =============================================================================
-- Nombre: usuariotenant
-- Breve descripción: Clase asociación entre Usuario y Tenant. Gestiona la pertenencia, vínculo contractual y estado de un usuario dentro de cada organización.
-- =============================================================================
CREATE TABLE usuariotenant (
    idusuariotenant SERIAL NOT NULL,
    idusuario INTEGER NOT NULL,
    idtenant INTEGER NOT NULL,
    fechaasociacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT pk_usuariotenant PRIMARY KEY (idusuariotenant),
    CONSTRAINT uq_usuariotenant_usuario_tenant UNIQUE (idusuario, idtenant)
);

-- =============================================================================
-- Nombre: rol
-- Breve descripción: Catálogo de roles de seguridad (SuperAdmin, Administrador de Empresa, Gestor de Operaciones, Auditor, etc.) para el esquema RBAC.
-- =============================================================================
CREATE TABLE rol (
    idrol SERIAL NOT NULL,
    nombrerol VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200),
    CONSTRAINT pk_rol PRIMARY KEY (idrol)
);

-- =============================================================================
-- Nombre: permiso
-- Breve descripción: Catálogo de permisos atómicos y privilegios funcionales organizados por módulos de la plataforma.
-- =============================================================================
CREATE TABLE permiso (
    idpermiso SERIAL NOT NULL,
    nombrepermiso VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200),
    modulo VARCHAR(50),
    CONSTRAINT pk_permiso PRIMARY KEY (idpermiso)
);

-- =============================================================================
-- Nombre: rolpermiso
-- Breve descripción: Clase asociación entre Rol y Permiso (N:M). Configura la matriz de privilegios y facultades de cada rol.
-- =============================================================================
CREATE TABLE rolpermiso (
    idrolpermiso SERIAL NOT NULL,
    idrol INTEGER NOT NULL,
    idpermiso INTEGER NOT NULL,
    CONSTRAINT pk_rolpermiso PRIMARY KEY (idrolpermiso),
    CONSTRAINT uq_rolpermiso_rol_permiso UNIQUE (idrol, idpermiso)
);

-- =============================================================================
-- Nombre: usuariotenantrol
-- Breve descripción: Clase asociación ternaria que vincula la membresía de un Usuario en un Tenant con uno o más Roles asignados para esa empresa.
-- =============================================================================
CREATE TABLE usuariotenantrol (
    idusuariotenantrol SERIAL NOT NULL,
    idusuariotenant INTEGER NOT NULL,
    idrol INTEGER NOT NULL,
    fechaasignacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_usuariotenantrol PRIMARY KEY (idusuariotenantrol),
    CONSTRAINT uq_usuariotenantrol UNIQUE (idusuariotenant, idrol)
);

-- =============================================================================
-- Nombre: tokenrecuperacion
-- Breve descripción: Tokens de restablecimiento de contraseña de un solo uso con ciclo de vida acotado y hash de seguridad.
-- =============================================================================
CREATE TABLE tokenrecuperacion (
    idtoken SERIAL NOT NULL,
    idtenant INTEGER,
    idusuario INTEGER NOT NULL,
    tokenhash VARCHAR(255) NOT NULL,
    expiraen TIMESTAMP WITH TIME ZONE NOT NULL,
    usadoen TIMESTAMP WITH TIME ZONE,
    fechacreacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk_tokenrecuperacion PRIMARY KEY (idtoken)
);

-- =============================================================================
-- Nombre: tokenrefresco
-- Breve descripción: Almacén de refresh tokens JWT de sesión activa por usuario y tenant con soporte de revocación y rotación.
-- =============================================================================
CREATE TABLE tokenrefresco (
    idtoken SERIAL NOT NULL,
    idtenant INTEGER,
    idusuario INTEGER NOT NULL,
    tokenhash VARCHAR(255) NOT NULL,
    expiraen TIMESTAMP WITH TIME ZONE NOT NULL,
    revocado BOOLEAN DEFAULT FALSE NOT NULL,
    fechacreacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT pk_tokenrefresco PRIMARY KEY (idtoken),
    CONSTRAINT uq_tokenrefresco_hash UNIQUE (tokenhash)
);

-- =============================================================================
-- Nombre: tenant_backup
-- Breve descripción: Registro histórico de copias de seguridad generadas por tenant, con metadatos de almacenamiento cloud y hash SHA-256.
-- =============================================================================
CREATE TABLE tenant_backup (
    idbackup SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idusuario_creador INTEGER NOT NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    cloud_storage VARCHAR(50) DEFAULT 'supabase' NOT NULL,
    cloud_path VARCHAR(500) NOT NULL,
    peso_bytes BIGINT DEFAULT 0 NOT NULL,
    checksum_sha256 VARCHAR(64),
    estado VARCHAR(30) DEFAULT 'PENDIENTE' NOT NULL,
    mensaje_error TEXT,
    total_registros INTEGER DEFAULT 0 NOT NULL,
    fechacreacion TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT pk_tenant_backup PRIMARY KEY (idbackup)
);

-- =============================================================================
-- Nombre: tenant_backup_schedule
-- Breve descripción: Configuración de tareas programadas y frecuencias de ejecución para copias de seguridad automáticas por tenant.
-- =============================================================================
CREATE TABLE tenant_backup_schedule (
    idschedule SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idusuario_creador INTEGER NOT NULL,
    fecha_hora_programada TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    frecuencia VARCHAR(20) NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    estado VARCHAR(20) DEFAULT 'PROGRAMADO' NOT NULL,
    ultimo_ejecutado TIMESTAMP WITHOUT TIME ZONE,
    proxima_ejecucion TIMESTAMP WITHOUT TIME ZONE,
    mensaje_resultado TEXT,
    fechacreacion TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    CONSTRAINT pk_tenant_backup_schedule PRIMARY KEY (idschedule)
);

-- =============================================================================
-- Nombre: bitacora
-- Breve descripción: Registro de auditoría inmutable de eventos del sistema, trazando acciones de usuario, IP, módulo y detalles técnicos.
-- =============================================================================
CREATE TABLE bitacora (
    idbitacora SERIAL NOT NULL,
    idusuariotenant INTEGER NOT NULL,
    accion VARCHAR(100) NOT NULL,
    modulo VARCHAR(50) NOT NULL,
    ip VARCHAR(45),
    detalles JSONB,
    fechahora TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_bitacora PRIMARY KEY (idbitacora)
);

-- =============================================================================
-- Nombre: notificacion
-- Breve descripción: Bandeja de notificaciones operativas dirigidas a usuarios de un tenant (alertas, órdenes, recepciones y envíos).
-- =============================================================================
CREATE TABLE notificacion (
    idnotificacion SERIAL NOT NULL,
    idusuariotenant INTEGER NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fechaenvio TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    enlaceaccion VARCHAR(255),
    CONSTRAINT pk_notificacion PRIMARY KEY (idnotificacion)
);

-- =============================================================================
-- Nombre: categoria
-- Breve descripción: Categorías jerárquicas del catálogo maestro de productos de hardware (ej. Smartphones, Portátiles, Wearables).
-- =============================================================================
CREATE TABLE categoria (
    idcategoria SERIAL NOT NULL,
    nombrecategoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    CONSTRAINT pk_categoria PRIMARY KEY (idcategoria)
);

-- =============================================================================
-- Nombre: producto
-- Breve descripción: Ficha maestra de producto en el catálogo general (marca, modelo general, país de procedencia y descripción técnica).
-- =============================================================================
CREATE TABLE producto (
    idproducto SERIAL NOT NULL,
    idcategoria INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    modelo VARCHAR(50),
    paisorigen VARCHAR(50),
    descripcion TEXT,
    imagenurl VARCHAR(255),
    fechacreacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    CONSTRAINT pk_producto PRIMARY KEY (idproducto)
);

-- =============================================================================
-- Nombre: varianteproducto
-- Breve descripción: Variantes físicas y comerciales de un producto base discriminadas por SKU maestro, color, capacidad y precio base en USD.
-- =============================================================================
CREATE TABLE varianteproducto (
    idvariante SERIAL NOT NULL,
    idproducto INTEGER NOT NULL,
    capacidad VARCHAR(50),
    color VARCHAR(50),
    sku VARCHAR(50) NOT NULL,
    preciousd NUMERIC(10,2) NOT NULL,
    CONSTRAINT pk_varianteproducto PRIMARY KEY (idvariante),
    CONSTRAINT uq_varianteproducto_sku UNIQUE (sku)
);

-- =============================================================================
-- Nombre: certificacion
-- Breve descripción: Catálogo de estándares y certificaciones técnicas internacionales homologadas para dispositivos electrónicos (FCC, CE, RoHS, etc.).
-- =============================================================================
CREATE TABLE certificacion (
    idcertificacion SERIAL NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    entidademisora VARCHAR(100),
    descripcion TEXT,
    logourl VARCHAR(255),
    CONSTRAINT pk_certificacion PRIMARY KEY (idcertificacion)
);

-- =============================================================================
-- Nombre: productocertificacion
-- Breve descripción: Clase asociación entre Producto y Certificación (N:M). Registra los sellos de conformidad técnica y números de certificado por producto.
-- =============================================================================
CREATE TABLE productocertificacion (
    idproductocertificacion SERIAL NOT NULL,
    idproducto INTEGER NOT NULL,
    idcertificacion INTEGER NOT NULL,
    fechacertificacion DATE,
    fechavencimiento DATE,
    numerocertificado VARCHAR(100),
    CONSTRAINT pk_productocertificacion PRIMARY KEY (idproductocertificacion),
    CONSTRAINT uq_productocertificacion UNIQUE (idproducto, idcertificacion)
);

-- =============================================================================
-- Nombre: catalogotenant
-- Breve descripción: Clase asociación entre Tenant y VarianteProducto. Permite a cada empresa definir sus precios locales de venta, costos y SKUs internos.
-- =============================================================================
CREATE TABLE catalogotenant (
    idcatalogotenant SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idvariante INTEGER NOT NULL,
    skuinterno VARCHAR(50),
    precioventa NUMERIC(10,2) NOT NULL,
    costopromedio NUMERIC(10,2),
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    CONSTRAINT pk_catalogotenant PRIMARY KEY (idcatalogotenant),
    CONSTRAINT uq_catalogotenant UNIQUE (idtenant, idvariante)
);

-- =============================================================================
-- Nombre: actorcadena
-- Breve descripción: Actores organizacionales e intermedios de la cadena de suministro (proveedores EEUU, transportistas, aduanas, importadores, tiendas).
-- =============================================================================
CREATE TABLE actorcadena (
    idactor SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    razonsocial VARCHAR(100),
    nit VARCHAR(50),
    email VARCHAR(100),
    telefono VARCHAR(50),
    tipoactor tipo_actor_enum NOT NULL,
    CONSTRAINT pk_actorcadena PRIMARY KEY (idactor)
);

-- =============================================================================
-- Nombre: ubicacion
-- Breve descripción: Instalaciones físicas o logísticas (almacenes centrales, depósitos aduaneros, tiendas minoristas) asociadas a un actor y tenant.
-- =============================================================================
CREATE TABLE ubicacion (
    idubicacion SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idactor INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT,
    ciudad VARCHAR(50),
    pais VARCHAR(50),
    tipoubicacion tipo_ubicacion_enum NOT NULL,
    coordenadaslatitud NUMERIC(10,8),
    coordenadaslongitud NUMERIC(11,8),
    CONSTRAINT pk_ubicacion PRIMARY KEY (idubicacion)
);

-- =============================================================================
-- Nombre: unidadproducto
-- Breve descripción: Registro serializado individual de cada pieza física de hardware con Número de Serie, IMEI 1/2, EID, estado y UUID público.
-- =============================================================================
CREATE TABLE unidadproducto (
    idunidad SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idvariante INTEGER NOT NULL,
    idrecepciondetalle INTEGER,
    numeroserie VARCHAR(100) NOT NULL,
    imei1 VARCHAR(50),
    imei2 VARCHAR(50),
    eid VARCHAR(50),
    uuidpublico VARCHAR(100) NOT NULL,
    idcustodioactual INTEGER,
    idubicacionactual INTEGER,
    estado estado_unidad_enum DEFAULT 'disponible',
    fechaingreso TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    fechaventa TIMESTAMP WITHOUT TIME ZONE,
    CONSTRAINT pk_unidadproducto PRIMARY KEY (idunidad),
    CONSTRAINT uq_unidadproducto_numeroserie UNIQUE (numeroserie),
    CONSTRAINT uq_unidadproducto_uuidpublico UNIQUE (uuidpublico)
);

-- =============================================================================
-- Nombre: codigoqr
-- Breve descripción: Código QR y token público generado de forma unívoca para cada unidad física para consultas de autenticidad y trazabilidad.
-- =============================================================================
CREATE TABLE codigoqr (
    idcodigoqr SERIAL NOT NULL,
    idunidad INTEGER NOT NULL,
    tokenpublico VARCHAR(100) NOT NULL,
    url VARCHAR(255),
    fechageneracion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT pk_codigoqr PRIMARY KEY (idcodigoqr),
    CONSTRAINT uq_codigoqr_idunidad UNIQUE (idunidad),
    CONSTRAINT uq_codigoqr_tokenpublico UNIQUE (tokenpublico)
);

-- =============================================================================
-- Nombre: consultatrazabilidad
-- Breve descripción: Registro de auditoría y telemetría de cada escaneo del código QR realizado por consumidores o inspectores (IP, país, user agent).
-- =============================================================================
CREATE TABLE consultatrazabilidad (
    idconsulta SERIAL NOT NULL,
    idcodigoqr INTEGER NOT NULL,
    fechahora TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip VARCHAR(45),
    paisaproximado VARCHAR(50),
    useragent TEXT,
    CONSTRAINT pk_consultatrazabilidad PRIMARY KEY (idconsulta)
);

-- =============================================================================
-- Nombre: documentounidad
-- Breve descripción: Expediente documental digital asociado a una unidad física (facturas comerciales, DUA de aduana, certificados de autenticidad).
-- =============================================================================
CREATE TABLE documentounidad (
    iddocumento SERIAL NOT NULL,
    idunidad INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    urlarchivo VARCHAR(255) NOT NULL,
    hasharchivo VARCHAR(255) NOT NULL,
    fechaemision DATE NOT NULL,
    fechavencimiento DATE,
    tipodocumento tipo_documento_enum NOT NULL,
    CONSTRAINT pk_documentounidad PRIMARY KEY (iddocumento)
);

-- =============================================================================
-- Nombre: compra
-- Breve descripción: Órdenes de compra internacionales emitidas a proveedores de hardware en origen (EEUU).
-- =============================================================================
CREATE TABLE compra (
    idcompra SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idproveedor INTEGER NOT NULL,
    numeroorden VARCHAR(50) NOT NULL,
    fechacompra DATE NOT NULL,
    totalusd NUMERIC(10,2) NOT NULL,
    estado estado_compra_enum DEFAULT 'pendiente',
    CONSTRAINT pk_compra PRIMARY KEY (idcompra),
    CONSTRAINT uq_compra_numeroorden UNIQUE (numeroorden)
);

-- =============================================================================
-- Nombre: compradetalle
-- Breve descripción: Detalle de líneas de producto asociadas a una orden de compra (variante adquirida, cantidad solicitada, costo y subtotal).
-- =============================================================================
CREATE TABLE compradetalle (
    idcompradetalle SERIAL NOT NULL,
    idcompra INTEGER NOT NULL,
    idvariante INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    costounitariousd NUMERIC(10,2) NOT NULL,
    subtotalusd NUMERIC(10,2) NOT NULL,
    CONSTRAINT pk_compradetalle PRIMARY KEY (idcompradetalle),
    CONSTRAINT compradetalle_cantidad_check CHECK (cantidad > 0)
);

-- =============================================================================
-- Nombre: recepcioncompra
-- Breve descripción: Registro de recepción física de mercancía en instalaciones de la empresa contra una orden de compra internacional.
-- =============================================================================
CREATE TABLE recepcioncompra (
    idrecepcion SERIAL NOT NULL,
    idcompra INTEGER NOT NULL,
    idubicacion INTEGER NOT NULL,
    fecharecepcion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    numerodocumento VARCHAR(50) NOT NULL,
    estado estado_recepcion_enum DEFAULT 'pendiente',
    CONSTRAINT pk_recepcioncompra PRIMARY KEY (idrecepcion)
);

-- =============================================================================
-- Nombre: recepciondetalle
-- Breve descripción: Líneas de detalle de recepción de mercancía, cotejando cantidades pactadas frente a unidades efectivamente recibidas.
-- =============================================================================
CREATE TABLE recepciondetalle (
    idrecepciondetalle SERIAL NOT NULL,
    idrecepcion INTEGER NOT NULL,
    idvariante INTEGER NOT NULL,
    cantidadesperada INTEGER NOT NULL,
    cantidadrecibida INTEGER NOT NULL,
    CONSTRAINT pk_recepciondetalle PRIMARY KEY (idrecepciondetalle),
    CONSTRAINT chk_cantidades CHECK (cantidadrecibida <= cantidadesperada),
    CONSTRAINT recepciondetalle_cantidadesperada_check CHECK (cantidadesperada > 0),
    CONSTRAINT recepciondetalle_cantidadrecibida_check CHECK (cantidadrecibida >= 0)
);

-- =============================================================================
-- Nombre: envio
-- Breve descripción: Despachos y traslados logísticos internacionales y nacionales entre actores de la cadena con seguimiento de tracking.
-- =============================================================================
CREATE TABLE envio (
    idenvio SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idactororigen INTEGER NOT NULL,
    idactordestino INTEGER NOT NULL,
    idtransportista INTEGER,
    codigoenvio VARCHAR(50) NOT NULL,
    fechasalida TIMESTAMP WITHOUT TIME ZONE,
    fechaestimada TIMESTAMP WITHOUT TIME ZONE,
    fechaentrega TIMESTAMP WITHOUT TIME ZONE,
    estado estado_envio_enum DEFAULT 'preparacion',
    trackingexterno VARCHAR(100),
    CONSTRAINT pk_envio PRIMARY KEY (idenvio),
    CONSTRAINT uq_envio_codigoenvio UNIQUE (codigoenvio)
);

-- =============================================================================
-- Nombre: enviounidad
-- Breve descripción: Clase asociación entre Envio y UnidadProducto (N:M). Asigna piezas físicas serializadas a un embarque o transporte logístico.
-- =============================================================================
CREATE TABLE enviounidad (
    idenviounidad SERIAL NOT NULL,
    idenvio INTEGER NOT NULL,
    idunidad INTEGER NOT NULL,
    CONSTRAINT pk_enviounidad PRIMARY KEY (idenviounidad),
    CONSTRAINT uq_enviounidad UNIQUE (idenvio, idunidad)
);

-- =============================================================================
-- Nombre: eventotrazabilidad
-- Breve descripción: Hitos de auditoría y custodia en la cadena logística (embarque, aduana, tránsito, entrega) con hash criptográfico del payload.
-- =============================================================================
CREATE TABLE eventotrazabilidad (
    idevento SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    tipoevento tipo_evento_enum NOT NULL,
    fechahora TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    idactororigen INTEGER,
    idactordestino INTEGER,
    idubicacion INTEGER NOT NULL,
    idusuarioresponsable INTEGER NOT NULL,
    descripcion TEXT,
    payloadhash VARCHAR(255),
    estadoverificacion estado_verificacion_enum DEFAULT 'pendiente',
    CONSTRAINT pk_eventotrazabilidad PRIMARY KEY (idevento)
);

-- =============================================================================
-- Nombre: eventounidad
-- Breve descripción: Clase asociación entre EventoTrazabilidad y UnidadProducto (N:M). Vincula el evento de custodia con las unidades físicas que participaron en él.
-- =============================================================================
CREATE TABLE eventounidad (
    ideventounidad SERIAL NOT NULL,
    idevento INTEGER NOT NULL,
    idunidad INTEGER NOT NULL,
    CONSTRAINT pk_eventounidad PRIMARY KEY (ideventounidad),
    CONSTRAINT uq_eventounidad UNIQUE (idevento, idunidad)
);

-- =============================================================================
-- Nombre: condiciontransporte
-- Breve descripción: Lecturas telemétricas de sensores IoT (temperatura, humedad, vibración, presión) registradas durante un evento de transporte.
-- =============================================================================
CREATE TABLE condiciontransporte (
    idcondicion SERIAL NOT NULL,
    idevento INTEGER NOT NULL,
    temperatura NUMERIC(5,2),
    humedad NUMERIC(5,2),
    presion NUMERIC(7,2),
    nivelvibracion NUMERIC(5,2),
    timestampregistro TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fuentedatos VARCHAR(50),
    CONSTRAINT pk_condiciontransporte PRIMARY KEY (idcondicion)
);

-- =============================================================================
-- Nombre: alerta
-- Breve descripción: Registro de anomalías e infracciones a parámetros de transporte o seguridad física (temperatura excesiva, golpes, retrasos aduaneros).
-- =============================================================================
CREATE TABLE alerta (
    idalerta SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idunidad INTEGER,
    idevento INTEGER,
    tipoalerta tipo_alerta_enum NOT NULL,
    descripcion TEXT NOT NULL,
    gravedad gravedad_alerta_enum NOT NULL,
    fechadeteccion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecharesolucion TIMESTAMP WITHOUT TIME ZONE,
    estado estado_alerta_enum DEFAULT 'pendiente',
    idusuarioresolutor INTEGER,
    CONSTRAINT pk_alerta PRIMARY KEY (idalerta)
);

-- =============================================================================
-- Nombre: registroblockchain
-- Breve descripción: Notarización inmutable de eventos de trazabilidad en blockchain (Polygon/Ethereum), almacenando txHash, bloque, contrato y confirmaciones.
-- =============================================================================
CREATE TABLE registroblockchain (
    idregistro SERIAL NOT NULL,
    idevento INTEGER NOT NULL,
    payloadhash VARCHAR(255) NOT NULL,
    txhash VARCHAR(255),
    blocknumber BIGINT,
    network VARCHAR(50),
    chainid VARCHAR(50),
    contractaddress VARCHAR(100),
    fechaenvio TIMESTAMP WITHOUT TIME ZONE,
    fechaconfirmacion TIMESTAMP WITHOUT TIME ZONE,
    estado estado_confirmacion_enum DEFAULT 'pendiente',
    numeroconfirmaciones INTEGER DEFAULT 0,
    mensajeerror TEXT,
    CONSTRAINT pk_registroblockchain PRIMARY KEY (idregistro),
    CONSTRAINT uq_registroblockchain_idevento UNIQUE (idevento)
);

-- =============================================================================
-- Nombre: venta
-- Breve descripción: Registro de ventas comerciales de hardware a clientes finales o distribuidores autorizados por cada tenant.
-- =============================================================================
CREATE TABLE venta (
    idventa SERIAL NOT NULL,
    idtenant INTEGER NOT NULL,
    idcliente INTEGER NOT NULL,
    fechaventa TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL,
    estado estado_venta_enum DEFAULT 'pendiente',
    CONSTRAINT pk_venta PRIMARY KEY (idventa)
);

-- =============================================================================
-- Nombre: ventadetalle
-- Breve descripción: Detalle de ítems de una transacción de venta (variante comercializada, unidades facturadas, precio unitario y subtotal).
-- =============================================================================
CREATE TABLE ventadetalle (
    idventadetalle SERIAL NOT NULL,
    idventa INTEGER NOT NULL,
    idvariante INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    preciounitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    CONSTRAINT pk_ventadetalle PRIMARY KEY (idventadetalle),
    CONSTRAINT ventadetalle_cantidad_check CHECK (cantidad > 0)
);

-- =============================================================================
-- Nombre: ventaunidad
-- Breve descripción: Clase asociación entre VentaDetalle y UnidadProducto. Vincula individualmente el número de serie de cada unidad física despachada en la venta.
-- =============================================================================
CREATE TABLE ventaunidad (
    idventaunidad SERIAL NOT NULL,
    idventadetalle INTEGER NOT NULL,
    idunidad INTEGER NOT NULL,
    CONSTRAINT pk_ventaunidad PRIMARY KEY (idventaunidad),
    CONSTRAINT uq_ventaunidad UNIQUE (idventadetalle, idunidad)
);

-- =============================================================================
-- Nombre: pago
-- Breve descripción: Transacciones y comprobantes de pago asociados a una venta comercial (monto, fecha, medio de pago y estado de conciliación).
-- =============================================================================
CREATE TABLE pago (
    idpago SERIAL NOT NULL,
    idventa INTEGER NOT NULL,
    metodopago metodo_pago_enum NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    fechapago TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    estado estado_pago_enum DEFAULT 'pendiente',
    CONSTRAINT pk_pago PRIMARY KEY (idpago)
);

-- =============================================================================
-- Nombre: devolucion
-- Breve descripción: Solicitudes de devolución física y gestión de RMA / garantía de clientes vinculadas a una venta previa.
-- =============================================================================
CREATE TABLE devolucion (
    iddevolucion SERIAL NOT NULL,
    idventa INTEGER NOT NULL,
    fechadevolucion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    motivo motivo_devolucion_enum NOT NULL,
    descripcion TEXT,
    estado estado_devolucion_enum DEFAULT 'solicitada',
    CONSTRAINT pk_devolucion PRIMARY KEY (iddevolucion)
);

-- =============================================================================
-- Nombre: devolucionunidad
-- Breve descripción: Clase asociación entre Devolucion y UnidadProducto. Identifica las piezas físicas serializadas devueltas a inventario o enviadas a servicio técnico.
-- =============================================================================
CREATE TABLE devolucionunidad (
    iddevolucionunidad SERIAL NOT NULL,
    iddevolucion INTEGER NOT NULL,
    idunidad INTEGER NOT NULL,
    CONSTRAINT pk_devolucionunidad PRIMARY KEY (iddevolucionunidad),
    CONSTRAINT uq_devolucionunidad UNIQUE (iddevolucion, idunidad)
);

-- =============================================================================
-- Nombre: garantiaunidad
-- Breve descripción: Términos, proveedor y cobertura temporal de garantía oficial del fabricante o distribuidor para una unidad física específica.
-- =============================================================================
CREATE TABLE garantiaunidad (
    idgarantia SERIAL NOT NULL,
    idunidad INTEGER NOT NULL,
    fechainicio DATE NOT NULL,
    fechafin DATE NOT NULL,
    proveedor VARCHAR(100),
    condiciones TEXT,
    CONSTRAINT pk_garantiaunidad PRIMARY KEY (idgarantia),
    CONSTRAINT chk_fechas_garantia CHECK (fechafin >= fechainicio)
);


-- =============================================================================
-- SECCIÓN 3: RELACIONES Y CLAVES FORÁNEAS (DECLARADAS FUERA DE LAS TABLAS)
-- =============================================================================

-- Relaciones de la tabla: usuariotenant
ALTER TABLE usuariotenant
    ADD CONSTRAINT fk_usuariotenant_usuario
    FOREIGN KEY (idusuario) REFERENCES usuario(idusuario) ON DELETE CASCADE;

ALTER TABLE usuariotenant
    ADD CONSTRAINT fk_usuariotenant_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

-- Relaciones de la tabla: rolpermiso
ALTER TABLE rolpermiso
    ADD CONSTRAINT fk_rolpermiso_rol
    FOREIGN KEY (idrol) REFERENCES rol(idrol) ON DELETE CASCADE;

ALTER TABLE rolpermiso
    ADD CONSTRAINT fk_rolpermiso_permiso
    FOREIGN KEY (idpermiso) REFERENCES permiso(idpermiso) ON DELETE CASCADE;

-- Relaciones de la tabla: usuariotenantrol
ALTER TABLE usuariotenantrol
    ADD CONSTRAINT fk_usuariotenantrol_usuariotenant
    FOREIGN KEY (idusuariotenant) REFERENCES usuariotenant(idusuariotenant) ON DELETE CASCADE;

ALTER TABLE usuariotenantrol
    ADD CONSTRAINT fk_usuariotenantrol_rol
    FOREIGN KEY (idrol) REFERENCES rol(idrol) ON DELETE CASCADE;

-- Relaciones de la tabla: tokenrecuperacion
ALTER TABLE tokenrecuperacion
    ADD CONSTRAINT fk_tokenrecuperacion_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE tokenrecuperacion
    ADD CONSTRAINT fk_tokenrecuperacion_usuario
    FOREIGN KEY (idusuario) REFERENCES usuario(idusuario) ON DELETE CASCADE;

-- Relaciones de la tabla: tokenrefresco
ALTER TABLE tokenrefresco
    ADD CONSTRAINT fk_tokenrefresco_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE tokenrefresco
    ADD CONSTRAINT fk_tokenrefresco_usuario
    FOREIGN KEY (idusuario) REFERENCES usuario(idusuario) ON DELETE CASCADE;

-- Relaciones de la tabla: tenant_backup
ALTER TABLE tenant_backup
    ADD CONSTRAINT fk_tenant_backup_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE tenant_backup
    ADD CONSTRAINT fk_tenant_backup_usuario
    FOREIGN KEY (idusuario_creador) REFERENCES usuario(idusuario) ON DELETE CASCADE;

-- Relaciones de la tabla: tenant_backup_schedule
ALTER TABLE tenant_backup_schedule
    ADD CONSTRAINT fk_tenant_backup_schedule_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE tenant_backup_schedule
    ADD CONSTRAINT fk_tenant_backup_schedule_usuario
    FOREIGN KEY (idusuario_creador) REFERENCES usuario(idusuario) ON DELETE CASCADE;

-- Relaciones de la tabla: bitacora
ALTER TABLE bitacora
    ADD CONSTRAINT fk_bitacora_usuariotenant
    FOREIGN KEY (idusuariotenant) REFERENCES usuariotenant(idusuariotenant) ON DELETE CASCADE;

-- Relaciones de la tabla: notificacion
ALTER TABLE notificacion
    ADD CONSTRAINT fk_notificacion_usuariotenant
    FOREIGN KEY (idusuariotenant) REFERENCES usuariotenant(idusuariotenant) ON DELETE CASCADE;

-- Relaciones de la tabla: producto
ALTER TABLE producto
    ADD CONSTRAINT fk_producto_categoria
    FOREIGN KEY (idcategoria) REFERENCES categoria(idcategoria) ON DELETE RESTRICT;

-- Relaciones de la tabla: varianteproducto
ALTER TABLE varianteproducto
    ADD CONSTRAINT fk_varianteproducto_producto
    FOREIGN KEY (idproducto) REFERENCES producto(idproducto) ON DELETE CASCADE;

-- Relaciones de la tabla: productocertificacion
ALTER TABLE productocertificacion
    ADD CONSTRAINT fk_productocertificacion_producto
    FOREIGN KEY (idproducto) REFERENCES producto(idproducto) ON DELETE CASCADE;

ALTER TABLE productocertificacion
    ADD CONSTRAINT fk_productocertificacion_certificacion
    FOREIGN KEY (idcertificacion) REFERENCES certificacion(idcertificacion) ON DELETE RESTRICT;

-- Relaciones de la tabla: catalogotenant
ALTER TABLE catalogotenant
    ADD CONSTRAINT fk_catalogotenant_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE catalogotenant
    ADD CONSTRAINT fk_catalogotenant_variante
    FOREIGN KEY (idvariante) REFERENCES varianteproducto(idvariante) ON DELETE RESTRICT;

-- Relaciones de la tabla: actorcadena
ALTER TABLE actorcadena
    ADD CONSTRAINT fk_actorcadena_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

-- Relaciones de la tabla: ubicacion
ALTER TABLE ubicacion
    ADD CONSTRAINT fk_ubicacion_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE ubicacion
    ADD CONSTRAINT fk_ubicacion_actor
    FOREIGN KEY (idactor) REFERENCES actorcadena(idactor) ON DELETE CASCADE;

-- Relaciones de la tabla: unidadproducto
ALTER TABLE unidadproducto
    ADD CONSTRAINT fk_unidadproducto_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE unidadproducto
    ADD CONSTRAINT fk_unidadproducto_variante
    FOREIGN KEY (idvariante) REFERENCES varianteproducto(idvariante) ON DELETE RESTRICT;

ALTER TABLE unidadproducto
    ADD CONSTRAINT fk_unidadproducto_recepciondetalle
    FOREIGN KEY (idrecepciondetalle) REFERENCES recepciondetalle(idrecepciondetalle) ON DELETE SET NULL;

ALTER TABLE unidadproducto
    ADD CONSTRAINT fk_unidadproducto_custodio
    FOREIGN KEY (idcustodioactual) REFERENCES actorcadena(idactor) ON DELETE SET NULL;

ALTER TABLE unidadproducto
    ADD CONSTRAINT fk_unidadproducto_ubicacion
    FOREIGN KEY (idubicacionactual) REFERENCES ubicacion(idubicacion) ON DELETE SET NULL;

-- Relaciones de la tabla: codigoqr
ALTER TABLE codigoqr
    ADD CONSTRAINT fk_codigoqr_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;

-- Relaciones de la tabla: consultatrazabilidad
ALTER TABLE consultatrazabilidad
    ADD CONSTRAINT fk_consultatrazabilidad_codigoqr
    FOREIGN KEY (idcodigoqr) REFERENCES codigoqr(idcodigoqr) ON DELETE CASCADE;

-- Relaciones de la tabla: documentounidad
ALTER TABLE documentounidad
    ADD CONSTRAINT fk_documentounidad_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;

-- Relaciones de la tabla: compra
ALTER TABLE compra
    ADD CONSTRAINT fk_compra_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE compra
    ADD CONSTRAINT fk_compra_proveedor
    FOREIGN KEY (idproveedor) REFERENCES actorcadena(idactor) ON DELETE RESTRICT;

-- Relaciones de la tabla: compradetalle
ALTER TABLE compradetalle
    ADD CONSTRAINT fk_compradetalle_compra
    FOREIGN KEY (idcompra) REFERENCES compra(idcompra) ON DELETE CASCADE;

ALTER TABLE compradetalle
    ADD CONSTRAINT fk_compradetalle_variante
    FOREIGN KEY (idvariante) REFERENCES varianteproducto(idvariante) ON DELETE RESTRICT;

-- Relaciones de la tabla: recepcioncompra
ALTER TABLE recepcioncompra
    ADD CONSTRAINT fk_recepcioncompra_compra
    FOREIGN KEY (idcompra) REFERENCES compra(idcompra) ON DELETE RESTRICT;

ALTER TABLE recepcioncompra
    ADD CONSTRAINT fk_recepcioncompra_ubicacion
    FOREIGN KEY (idubicacion) REFERENCES ubicacion(idubicacion) ON DELETE RESTRICT;

-- Relaciones de la tabla: recepciondetalle
ALTER TABLE recepciondetalle
    ADD CONSTRAINT fk_recepciondetalle_recepcion
    FOREIGN KEY (idrecepcion) REFERENCES recepcioncompra(idrecepcion) ON DELETE CASCADE;

ALTER TABLE recepciondetalle
    ADD CONSTRAINT fk_recepciondetalle_variante
    FOREIGN KEY (idvariante) REFERENCES varianteproducto(idvariante) ON DELETE RESTRICT;

-- Relaciones de la tabla: envio
ALTER TABLE envio
    ADD CONSTRAINT fk_envio_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE envio
    ADD CONSTRAINT fk_envio_actororigen
    FOREIGN KEY (idactororigen) REFERENCES actorcadena(idactor) ON DELETE RESTRICT;

ALTER TABLE envio
    ADD CONSTRAINT fk_envio_actordestino
    FOREIGN KEY (idactordestino) REFERENCES actorcadena(idactor) ON DELETE RESTRICT;

ALTER TABLE envio
    ADD CONSTRAINT fk_envio_transportista
    FOREIGN KEY (idtransportista) REFERENCES actorcadena(idactor) ON DELETE SET NULL;

-- Relaciones de la tabla: enviounidad
ALTER TABLE enviounidad
    ADD CONSTRAINT fk_enviounidad_envio
    FOREIGN KEY (idenvio) REFERENCES envio(idenvio) ON DELETE CASCADE;

ALTER TABLE enviounidad
    ADD CONSTRAINT fk_enviounidad_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;

-- Relaciones de la tabla: eventotrazabilidad
ALTER TABLE eventotrazabilidad
    ADD CONSTRAINT fk_eventotrazabilidad_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE eventotrazabilidad
    ADD CONSTRAINT fk_eventotrazabilidad_actororigen
    FOREIGN KEY (idactororigen) REFERENCES actorcadena(idactor) ON DELETE SET NULL;

ALTER TABLE eventotrazabilidad
    ADD CONSTRAINT fk_eventotrazabilidad_actordestino
    FOREIGN KEY (idactordestino) REFERENCES actorcadena(idactor) ON DELETE SET NULL;

ALTER TABLE eventotrazabilidad
    ADD CONSTRAINT fk_eventotrazabilidad_ubicacion
    FOREIGN KEY (idubicacion) REFERENCES ubicacion(idubicacion) ON DELETE RESTRICT;

ALTER TABLE eventotrazabilidad
    ADD CONSTRAINT fk_eventotrazabilidad_usuarioresponsable
    FOREIGN KEY (idusuarioresponsable) REFERENCES usuario(idusuario) ON DELETE RESTRICT;

-- Relaciones de la tabla: eventounidad
ALTER TABLE eventounidad
    ADD CONSTRAINT fk_eventounidad_evento
    FOREIGN KEY (idevento) REFERENCES eventotrazabilidad(idevento) ON DELETE CASCADE;

ALTER TABLE eventounidad
    ADD CONSTRAINT fk_eventounidad_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;

-- Relaciones de la tabla: condiciontransporte
ALTER TABLE condiciontransporte
    ADD CONSTRAINT fk_condiciontransporte_evento
    FOREIGN KEY (idevento) REFERENCES eventotrazabilidad(idevento) ON DELETE CASCADE;

-- Relaciones de la tabla: alerta
ALTER TABLE alerta
    ADD CONSTRAINT fk_alerta_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE alerta
    ADD CONSTRAINT fk_alerta_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE SET NULL;

ALTER TABLE alerta
    ADD CONSTRAINT fk_alerta_evento
    FOREIGN KEY (idevento) REFERENCES eventotrazabilidad(idevento) ON DELETE SET NULL;

ALTER TABLE alerta
    ADD CONSTRAINT fk_alerta_usuarioresolutor
    FOREIGN KEY (idusuarioresolutor) REFERENCES usuario(idusuario) ON DELETE SET NULL;

-- Relaciones de la tabla: registroblockchain
ALTER TABLE registroblockchain
    ADD CONSTRAINT fk_registroblockchain_evento
    FOREIGN KEY (idevento) REFERENCES eventotrazabilidad(idevento) ON DELETE CASCADE;

-- Relaciones de la tabla: venta
ALTER TABLE venta
    ADD CONSTRAINT fk_venta_tenant
    FOREIGN KEY (idtenant) REFERENCES tenant(idtenant) ON DELETE CASCADE;

ALTER TABLE venta
    ADD CONSTRAINT fk_venta_cliente
    FOREIGN KEY (idcliente) REFERENCES actorcadena(idactor) ON DELETE RESTRICT;

-- Relaciones de la tabla: ventadetalle
ALTER TABLE ventadetalle
    ADD CONSTRAINT fk_ventadetalle_venta
    FOREIGN KEY (idventa) REFERENCES venta(idventa) ON DELETE CASCADE;

ALTER TABLE ventadetalle
    ADD CONSTRAINT fk_ventadetalle_variante
    FOREIGN KEY (idvariante) REFERENCES varianteproducto(idvariante) ON DELETE RESTRICT;

-- Relaciones de la tabla: ventaunidad
ALTER TABLE ventaunidad
    ADD CONSTRAINT fk_ventaunidad_ventadetalle
    FOREIGN KEY (idventadetalle) REFERENCES ventadetalle(idventadetalle) ON DELETE CASCADE;

ALTER TABLE ventaunidad
    ADD CONSTRAINT fk_ventaunidad_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;

-- Relaciones de la tabla: pago
ALTER TABLE pago
    ADD CONSTRAINT fk_pago_venta
    FOREIGN KEY (idventa) REFERENCES venta(idventa) ON DELETE CASCADE;

-- Relaciones de la tabla: devolucion
ALTER TABLE devolucion
    ADD CONSTRAINT fk_devolucion_venta
    FOREIGN KEY (idventa) REFERENCES venta(idventa) ON DELETE CASCADE;

-- Relaciones de la tabla: devolucionunidad
ALTER TABLE devolucionunidad
    ADD CONSTRAINT fk_devolucionunidad_devolucion
    FOREIGN KEY (iddevolucion) REFERENCES devolucion(iddevolucion) ON DELETE CASCADE;

ALTER TABLE devolucionunidad
    ADD CONSTRAINT fk_devolucionunidad_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;

-- Relaciones de la tabla: garantiaunidad
ALTER TABLE garantiaunidad
    ADD CONSTRAINT fk_garantiaunidad_unidad
    FOREIGN KEY (idunidad) REFERENCES unidadproducto(idunidad) ON DELETE CASCADE;


-- =============================================================================
-- SECCIÓN 4: ÍNDICES DE RENDIMIENTO Y BÚSQUEDA OPERATIVA
-- =============================================================================

CREATE INDEX ix_usuario_email ON usuario(email);
CREATE INDEX ix_usuariotenant_usuario ON usuariotenant(idusuario);
CREATE INDEX ix_usuariotenant_tenant ON usuariotenant(idtenant);
CREATE INDEX ix_tokenrecuperacion_tokenhash ON tokenrecuperacion(tokenhash);
CREATE INDEX ix_tokenrefresco_tokenhash ON tokenrefresco(tokenhash);
CREATE INDEX ix_producto_categoria ON producto(idcategoria);
CREATE INDEX ix_varianteproducto_sku ON varianteproducto(sku);
CREATE INDEX ix_catalogotenant_tenant ON catalogotenant(idtenant);
CREATE INDEX ix_actorcadena_tenant ON actorcadena(idtenant);
CREATE INDEX ix_ubicacion_tenant ON ubicacion(idtenant);
CREATE INDEX ix_unidadproducto_serial ON unidadproducto(numeroserie);
CREATE INDEX ix_unidadproducto_uuid ON unidadproducto(uuidpublico);
CREATE INDEX ix_unidadproducto_tenant ON unidadproducto(idtenant);
CREATE INDEX ix_codigoqr_tokenpublico ON codigoqr(tokenpublico);
CREATE INDEX ix_consultatrazabilidad_qr ON consultatrazabilidad(idcodigoqr);
CREATE INDEX ix_envio_codigo ON envio(codigoenvio);
CREATE INDEX ix_envio_tenant ON envio(idtenant);
CREATE INDEX ix_eventotrazabilidad_tenant ON eventotrazabilidad(idtenant);
CREATE INDEX ix_eventotrazabilidad_fecha ON eventotrazabilidad(fechahora);
CREATE INDEX ix_registroblockchain_txhash ON registroblockchain(txhash);
CREATE INDEX ix_registroblockchain_payloadhash ON registroblockchain(payloadhash);
CREATE INDEX ix_alerta_tenant ON alerta(idtenant);
CREATE INDEX ix_alerta_estado ON alerta(estado);
CREATE INDEX ix_venta_tenant ON venta(idtenant);
CREATE INDEX ix_devolucion_venta ON devolucion(idventa);

-- =============================================================================
-- FIN DEL SCRIPT database_blockhain_DDL.sql
-- =============================================================================
