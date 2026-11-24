# Relevo Operativo de Agentes (Handoff Latest)

> **Documento:** Pase de Posta Inmediato entre Sesiones de Agentes de IA  
> **Ubicación:** `docs/ai/HANDOFF_LATEST.md`  
> **Fecha / Sesión:** 2026-11-23  
> **Sprint Activo:** Sprint 5 (Seguridad, Hardening, Auditoría y Robusteza Multi-Tenant)  
> **Estado Técnico:** **Despliegue Completo en la Nube: Backend en Railway `sprint#4` (`https://sprint4-production.up.railway.app`) | Frontend Web en Vercel (`https://frontend-sepia-seven-97.vercel.app`) | Base de Datos en Supabase Cloud con 38,386 filas | Mobile apuntado a Railway | Repositorio https://github.com/RafaelLMCHO/Grupo5_si2.git sincronizado**

---

## 0. Sesión actual (2026-11-23): Despliegue de Frontend Web en Vercel

**Petición del Usuario:** Subir el frontend web a Vercel.

### 1. Despliegue en Producción
* **Comando:** `vercel --prod --yes` ejecutado exitosamente.
* **URL Canónica de Producción:** **`https://frontend-sepia-seven-97.vercel.app`**
* **Deployment URL:** `https://frontend-hbvjomrpq-sistemas26.vercel.app`
* **Verificación:** Código HTTP 200 y bundle compilado `main.js` verificado apuntando a `https://sprint4-production.up.railway.app/api/v1`.

## 0. Sesión actual (2026-11-23): Despliegue en Railway (Proyecto Independiente `sprint#4`) y Conexión Supabase Cloud

**Petición del Usuario:** Subir todo a Railway en un proyecto nuevo llamado `sprint#4` (Opción A: preservando intacto el proyecto `si2_parcial2`).

### 1. Infraestructura Desplegada en Railway
1. **Nuevo Proyecto Aislado:**
   * **Nombre:** `sprint#4` (ID: `4889a3c5-4ac9-49f3-bd7e-f75ce14bf66c`).
   * **Entorno:** `production` (ID: `4c059e0c-bbf5-4125-a4e4-b86a74ef0aa9`).
   * **Servicio:** `sprint#4` (ID: `0e7c902a-f148-4bf5-8172-786260fdedad`).
   * **Dominio Público Oficial:** `https://sprint4-production.up.railway.app`
2. **Configuración de Variables de Entorno en Railway:**
   * `DATABASE_URL`: `postgresql+psycopg://postgres.vwonuktrcpnyoknrzrfs:Rafael2026Trazabilidad!@aws-0-us-west-2.pooler.supabase.com:5432/postgres` (Utilizando el Supabase Session Pooler compatible con IPv4/IPv6 en AWS us-west-2).
   * `SUPABASE_URL`: `https://vwonuktrcpnyoknrzrfs.supabase.co`
   * `BLOCKCHAIN_ENABLED`: `false`
   * `PORT`: `8000`
   * `CORS_ORIGINS`: `*`
   * `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`.
3. **Validaciones en Producción (100% Exitosas):**
   * **Healthcheck:** `GET https://sprint4-production.up.railway.app/health` -> `{"status":"ok","app":"Sistema de Trazabilidad","db":"connected"}`.
   * **Autenticación Multi-Tenant:** `POST /api/v1/auth/login` con credenciales reales (`admin@istore.com`, `demo`) generando JWT bearer token.
   * **Consultas de Datos:** `GET /api/v1/units` retornando unidades reales desde Supabase.
   * **Inteligencia Artificial por Voz:** `POST /api/v1/ai/voice-report` generando reportes ejecutivos dinámicos, KPIs, gráficos y enlaces de descarga oficial.
4. **Clientes Actualizados con la Nueva URL:**
   * `trazabilidad/frontend/src/environments/environment.prod.ts` -> `https://sprint4-production.up.railway.app/api/v1`
   * `trazabilidad/mobile/lib/core/api_config.dart` -> `https://sprint4-production.up.railway.app/api/v1`

---

## 0. Sesión actual (2026-11-23): Migración Integral de Base de Datos y Poblado en Supabase Cloud

**Petición:** Subir la base de datos completa con todos sus datos poblados a Supabase Cloud.

### 1. Proceso de Migración Ejecutado
1. **Exportación limpia (`supabase_dump_completo.sql` - 7.4 MB):**
   * Generado con `pg_dump` mediante flags `--no-owner --no-acl` para evitar colisiones de permisos en el entorno gestionado de Supabase.
2. **Carga y Verificación en Supabase (`db.vwonuktrcpnyoknrzrfs.supabase.co`):**
   * Conexión directa y ejecución con `psql` completando DDL, tipos enum, 53 tablas en `public`, índices, secuencias (`setval`) y claves foráneas.
   * **Auditoría de datos en la nube (38,386 registros cargados exitosamente):**
     * `tenant`: 9 empresas (SuperAdmin + 8 empresas comerciales).
     * `usuario`: 35 usuarios.
     * `producto`: 61 productos Apple.
     * `varianteproducto`: 73 variantes.
     * `catalogotenant`: 175 productos en catálogo.
     * `unidadproducto`: 7,697 unidades con serial e IMEI.
     * `codigoqr`: 5,996 códigos QR generados.
     * `compra` / `compradetalle`: 310 órdenes y 966 líneas.
     * `recepcioncompra`: 296 recepciones.
     * `envio` / `condiciontransporte`: 306 despachos y 3,074 lecturas IoT.
     * `venta` / `ventadetalle`: 3,051 ventas y 3,059 detalles.
     * `pago` / `factura`: 3,061 pagos y 288 facturas.
     * `bitacora`: 4,010 eventos de auditoría inmutable.
     * `alerta`: 2,803 incidencias y alertas operativas.
     * `registroblockchain`: 3,061 registros notarizados on-chain con hashes SHA-256.
     * `suscripcion`: 10 planes activos.
3. **Reconexión del Backend:**
   * Actualizado `DATABASE_URL` y `SUPABASE_URL` en `trazabilidad/backend/.env`.
   * Reiniciado FastAPI (`http://127.0.0.1:8000`), respondiendo `/health` con `db: connected` y probando exitosamente autenticación JWT y reportes IA de voz contra Supabase.

## 0. Sesión actual (2026-11-23): Auditoría Integral de la App Móvil y Regla de Visibilidad en AndroidManifest

**Petición:** Análisis de conectividad de la aplicación móvil Flutter y adición de la regla de visibilidad de paquete en AndroidManifest.xml.

### 1. Hallazgos y Corrección
* **Auditoría:** Se verificó la alineación al 100% de los 27 endpoints en `ApiConfig` contra los controladores de FastAPI, la navegación en `DashboardView`, y la visualización de gráficos nativos con `fl_chart`.
* **Corrección Android 11+:** Se añadió el `<intent>` con `android.speech.RecognitionService` en el bloque `<queries>` de `trazabilidad/mobile/android/app/src/main/AndroidManifest.xml` para evitar que las políticas de *Package Visibility* bloqueen el reconocimiento de voz nativo en Android 11+.

## 0. Sesión actual (2026-11-23): Gráficos Dinámicos y Diagnóstico del Error 'network' en Reconocimiento de Voz

**Petición:** Diagnóstico del error `⚠️ Error en reconocimiento de voz: network` mostrado en el asistente de voz y verificación de gráficos.

### 1. Diagnóstico del Error `network` en Web Speech API
* **Naturaleza del Error:** El error no proviene del backend FastAPI ni de la base de datos PostgreSQL, ni depende del tenant autenticado.
* **Causa Raíz:** Ocurre en el navegador del cliente mediante la Web Speech API (`SpeechRecognition`). En navegadores basados en Chromium (Chrome, Brave, Edge), el navegador intenta enviar el stream de audio del micrófono a los servidores en la nube de Google (`speech.googleapis.com`). Si el usuario utiliza **Brave Browser** (que bloquea llamadas a Google por defecto en sus escudos de privacidad), si no hay conexión externa a internet o si un bloqueador de rastreo/adblocker bloquea el endpoint de Google, la API del navegador emite el evento `onerror: { error: 'network' }`.
* **Solución y UX:**
  1. La aplicación dispone de fallback completo por teclado: cualquier consulta puede escribirse en el input o ejecutarse con las píldoras de sugerencias rápidas.
  2. En Brave Browser: habilitar `brave://settings/privacy` -> *"Usar servicios de Google para reconocimiento de voz"*.
  3. En Google Chrome/Edge: verificar permisos de micrófono y acceso a internet.

### 2. Estado de la Suite de Pruebas y Exportación Excel
* Corregida firma de `generate_excel_bytes` en `report_generator.py` para soportar parámetros gráficos kwargs.
* **Suite de pruebas:** **252 tests verdes (100% pasando)**.
* Servidores FastAPI (:8000) y Angular (:4200) activos y operativos.

---

## 0. Sesión actual (2026-11-23): Resolución Integral de Consultas del Asistente por Voz en Todos los Tenants

**Petición:** Diagnosticar y corregir por qué no estaban funcionando la mayoría de las consultas en el asistente de informes dinámicos por voz en los tenants.

### 1. Diagnóstico de Causas Raíz
1. **Error Enum SQL en Consultas de Ventas (`Top 10 productos más vendidos`):**
   * El parser determinista mapeaba `"vendidos"` a `estado="vendido"`.
   * En `query_sales_ranking_data`, se aplicaba `Venta.estado == parsed.estado`.
   * En PostgreSQL, `Venta.estado` utiliza el enum `estado_venta_enum` (`pendiente`, `pagada`, `enviada`, `entregada`, `cancelada`, `devuelta`). El valor `'vendido'` pertenece a `UnidadProducto.estado` (`estado_unidad_enum`), no a `Venta`.
   * Esto provocaba una excepción `InvalidTextRepresentation: la sintaxis de entrada no es válida para el enum estado_venta_enum: «vendido»` y un error 500 no capturado que abortaba la transacción en la sesión de base de datos.
2. **Ventana Temporal Estricta en Envíos Logísticos (`Envíos de la última semana`):**
   * Los registros históricos del seed tenían fechas de despacho hasta mediados de noviembre de 2026. Al consultar por los últimos 7 días respecto al día actual, la consulta SQL retornaba 0 filas.
3. **Falta de Reconocimiento de Familias de Productos y Filtro de Inventario:**
   * La resolución de catálogo buscaba substrings exactos del nombre del modelo (`iPhone 15 Pro Max`). Consultas como *"Stock disponible de iPhones"* no coincidían exactamente con ningún modelo individual y retornaban todo el inventario sin filtrar.
   * `query_inventory_data` no aplicaba `parsed.estado` ni `parsed.producto` en el listado de unidades.
4. **Brecha de Sembrado en Inquilinos Registrados Posteriormente (Tenants 7166, 7167, 7168):**
   * Las empresas `Apple Bolivia SRL` (7166), `Sucursal Santa Cruz` (7167) y `RafaelStore` (7168) fueron creadas sin actores de cadena, sin catálogo de precios ni ubicaciones logísticas, y `seed_historical_6m.py` tenía un filtro excluyente `Tenant.idtenant <= 5`. Por tanto, al cambiar a estas empresas, cualquier consulta devolvía 0 registros.

### 2. Soluciones Implementadas
1. **Blindaje en Parser (`voice_query_parser.py`) y Motor SQL (`voice_query_engine.py`):**
   * En `parse_query`: se evita asignar `estado = "vendido"` cuando la intención es comercial (`ventas`, `rentabilidad`, `garantias`), ya que describe la acción comercial y no el sub-estado de una orden de venta.
   * En `query_sales_ranking_data`: se valida que `parsed.estado` pertenezca estrictamente a los valores válidos de `estado_venta_enum`. Por defecto, se excluyen únicamente las ventas `cancelada`.
   * En `_resolver_filtros_catalogo`: se añadió detección automática de familias Apple (`iPhone`, `MacBook`, `iPad`, `AirPods`, `Watch`).
   * En `query_inventory_data`: se aplican filtros `UnidadProducto.estado == parsed.estado` y `Producto.nombre.ilike(f"%{parsed.producto}%")` tanto al desglose como a la tabla y los KPIs.
   * En `query_logistics_data`: si un rango temporal estrecho retorna 0 envíos, se aplica un fallback automático a los despachos y telemetría IoT más recientes del tenant.
2. **Onboarding y Sembrado Completo de 36 Meses para Todos los Tenants:**
   * En `seed.py`: se agregaron los tenants 7166, 7167 y 7168 a `TENANTS_DATA`, inicializando sus catálogos con precios y márgenes, actores de cadena y almacenes en Santa Cruz.
   * En `seed_historical_6m.py`: se cambió el filtro a `Tenant.nit != "000000000"`, abarcando todas las empresas comerciales.
   * Ejecutado `seed_historical_36m.py`: +21,684 registros insertados con éxito en la base de datos local para los 8 tenants comerciales.
3. **Frontend (`dashboard.controller.ts`):**
   * Prompt rápido actualizado a: `'🚚 Envíos recientes y telemetría IoT'`.
4. **Verificación:**
   * Las 9 consultas fueron ejecutadas y verificadas contra la base de datos real en los 8 tenants comerciales, confirmando 100% de respuestas exitosas y datos enriquecidos.
   * Suite de pruebas `pytest tests/`: **251 passed (100% verde)**.
   * Cero commits ni pushes a Git.

---

## 0. Sesión actual (2026-11-23): Implementación de las 3 Consultas de Mayor Impacto en el Asistente IA (CU-022)

**Petición:** Implementar para todas las empresas (multi-tenant) las 3 consultas de inteligencia estratégica más recomendadas:
1. Rentabilidad y Margen Comercial (precio de venta vs. costo promedio).
2. Control de Calidad, Devoluciones y Garantías (tasa de incidencias por modelo).
3. Seguridad Criptográfica, Blockchain y Alertas de Sospecha (inmutabilidad on-chain y fraudes).

### 1. Implementación Realizada
1. **Parser de Lenguaje Natural (`voice_query_parser.py`):**
   * Agregadas 3 nuevas intenciones deterministas con soporte multi-período: `rentabilidad`, `garantias` y `blockchain`.
   * Frases clave: margen de ganancia, más rentable, margen comercial, tasa de devoluciones, garantías, reclamos, notarizadas en blockchain, alertas de sospecha, falsificación.
   * `interpretation()` actualizado para reflejar criterios de rentabilidad, calidad y seguridad criptográfica.
2. **Motores de Consulta en Backend (`voice_query_engine.py`):**
   * `query_profitability_data`: cruza catálogo de empresa (`CatalogoTenant`) y ventas (`VentaDetalle`) calculando margen unitario en USD, margen porcentual y beneficio bruto estimado. Devuelve KPIs ejecutivos, bar chart y tabla analítica.
   * `query_warranty_quality_data`: analiza reclamos de garantía (`GarantiaUnidad`), devoluciones procesadas (`Devolucion`, `DevolucionUnidad`) y unidades vendidas, determinando la tasa global de falla (%) y el motivo preponderante (defecto de fábrica, daño en transporte, insatisfacción).
   * `query_blockchain_security_data`: consolida eventos de trazabilidad, transacciones confirmadas on-chain en Ethereum/Polygon (`RegistroBlockchain`), reportes de sospecha (`ReporteSospecha`), alertas activas (`Alerta`) y consultas de autenticidad QR (`ConsultaTrazabilidad`).
3. **Síntesis Ejecutiva y Fallbacks Semánticos:**
   * Ampliado `synthesize_with_gemini` para generar resúmenes por voz y diagnósticos estratégicos en Markdown para `rentabilidad`, `garantias` y `blockchain`.
   * Integrados chips de preguntas de seguimiento recomendadas (`followups`) según la intención activa.
4. **Actualización de Frontend (`dashboard.controller.ts`):**
   * Agregados los nuevos prompts rápidos con un solo clic a `quickPrompts`:
     * `💰 Top 5 productos con mayor margen de ganancia`
     * `🛠️ Tasa de devoluciones y garantías de los últimos 6 meses`
     * `🔗 Unidades notarizadas en blockchain y alertas de sospecha`
5. **Pruebas Automatizadas:**
   * Creado `tests/test_ai_voice_new_queries.py`: 6 tests unitarios y de integración API verificando parser, KPIs, gráficos, tablas y exportaciones para las 3 consultas.
   * Suite completa: **251 passed (100% verde)**.
   * Cero commits ni pushes a Git.

---

## 0. Sesión actual (2026-11-23): Segregación Estricta del SuperAdministrador en Frontend (Plano de Control SaaS)

**Petición:** Retirar del frontend del `SuperAdministrador` todos los casos de uso y accesos a los que no debe tener permiso (módulos operacionales de empresas clientes: catálogo de empresa, actores, ubicaciones, unidades, compras, recepciones, QR, transporte, trazabilidad interna, certificados de unidad, documentos, alertas, ventas, postventa y reportes de empresa), así como el selector de empresa en la barra de navegación.

### 1. Implementación Realizada en Frontend
1. **Protección Estricta en Rutas (`role.guard.ts`):**
   * Eliminado el bypass incondicional `if (roles.includes('SuperAdministrador')) return true;`.
   * Ahora evalúa con precisión quirúrgica si el rol del usuario está explícitamente contenido en `allowedRoles`.
2. **Depuración de Rutas Operacionales (`app.routes.ts`):**
   * Removido `'SuperAdministrador'` de los guards de las 15 rutas operacionales de empresas clientes (`/tenant-catalog`, `/actors`, `/locations`, `/units`, `/purchases`, `/receptions`, `/qr-codes`, `/shipments`, `/alerts`, `/documents`, `/certificates`, `/traceability`, `/sales`, `/post-sales`, `/reports`).
   * El SuperAdministrador solo tiene acceso a las rutas del Plano de Control SaaS (`/tenants`, `/users`, `/roles`, `/subscription-plans`, `/subscriptions`, `/bitacora`, `/categories`, `/products`, `/certifications`, `/quotas`, `/billing`).
3. **Control de Acceso Dinámico a la Barra de Navegación (`dashboard.controller.ts`):**
   * En `canAccess(module: string)`, si el rol es `SuperAdministrador`, retorna `true` estrictamente para los módulos de `saasControlPlaneModules`:
     `['tenants', 'users', 'roles', 'subscription-plans', 'subscriptions', 'bitacora', 'categories', 'products', 'certifications', 'quotas', 'billing']`.
   * Cualquier módulo operacional de inquilino retorna `false`, ocultándolo por completo de la barra de navegación.
4. **Eliminación del Selector de Cambio de Empresa (`dashboard.view.html`):**
   * Eliminado el dropdown `<select>` de cambio de contexto de empresa (`switch-tenant`) que permitía al SuperAdmin saltar entre inquilinos. Ahora muestra únicamente el badge informativo de su tenant (`Plataforma SaaS`).
   * El panel de analítica operacional (`<app-analytics-panel>`) queda oculto al SuperAdmin dado que `canAccess('reports')` es `false`.
5. **Ajuste en `auth.service.ts`:**
   * En `hasAnyRole`, eliminado el retorno forzado `true` para `SuperAdministrador`, previniendo falsos positivos de roles en cualquier componente consumidor.
6. **Compilación y Verificación:**
   * `ng build`: **Generación de bundle exitosa (0 errores)**.
   * `pytest`: **245 tests verdes (100% passed)**.
   * Cero commits ni pushes a Git.

---

## 0. Sesión actual (2026-11-23): Segregación Estricta del SuperAdministrador al Plano de Control SaaS (ADR-016)

**Petición:** El `SuperAdministrador` no debe tener acceso a operaciones operacionales de ninguna empresa cliente (compras, recepciones, actores, ubicaciones, unidades, QR, envíos, ventas, pagos, devoluciones, garantías, reportes privados). Debe limitarse exclusivamente a los casos de uso del **Plano de Control** de la plataforma SaaS (tenants, usuarios globales, roles, catálogo global Apple, certificaciones, bitácora SaaS, planes, suscripciones y nodo blockchain).

### 1. Implementación Realizada
1. **Separación de Identidades e Inquilino de Plataforma:**
   * Creado `platform_tenant` (`nit="000000000"`, `nombre="Plataforma SaaS Global"`).
   * `superadmin@trazabilidad.com` (`Admin123!`) vinculado exclusivamente al tenant de plataforma con rol único `SuperAdministrador`.
   * `admin@istore.com` (`Admin123!`) administrador exclusivo de Empresa 1 (`idtenant = 1`).
   * Eliminados todos los vínculos `UsuarioTenant` previos del superadmin a empresas clientes 1..5.
2. **Control de Acceso en `shared.py` (`require_roles`):**
   * El SuperAdministrador solo pasa la barrera de seguridad si `"SuperAdministrador"` está explícitamente en la lista de roles permitidos del endpoint.
   * Si no lo está, lanza inmediatamente `403 Forbidden` con detalle: *"El SuperAdministrador de plataforma no tiene acceso a operaciones comerciales/logísticas de empresas clientes."*
3. **Limpieza de Controladores Operacionales:**
   * Removido el rol `SuperAdministrador` de todos los controladores de compras, recepciones, actores, ubicaciones, unidades físicas, códigos QR, envíos logísticos, eventos de transporte, alertas, ventas, pagos, devoluciones, garantías, documentos de unidad y reportes internos de empresa.
   * Protegidos los métodos `GET` de consulta de dichos controladores para que exijan roles de empresa (`requires_...`), denegando la lectura de datos privados al SuperAdmin.
4. **Blindaje de Autenticación (`auth_controller.py`):**
   * La asociación a `platform_tenant` opera exclusivamente para `superadmin@trazabilidad.com` o slugs de plataforma (`system`, `platform`, `saas`).
   * En `switch_tenant`, se asignan roles de administración de empresa (`AdministradorEmpresa`, `GestorOperaciones`) para operaciones legítimas de auditoría entre empresas autorizadas.
5. **Verificación de Pruebas Automatizadas:**
   * `tests/test_prompt9_security_verification.py`: **11 passed (100% verde)** verificando el rechazo con 403 al SuperAdmin en `/actors`, `/units`, `/locations`, `/purchases` y `/sales`.
   * Suite completa: **245 passed, 0 failed** en 135.07s.

---

---

## 0. Sesión actual (2026-11-23): Refinamiento Arquitectónico de Cuentas Multi-Tenant (Opción A)

**Petición:** Desacoplar la cuenta del SuperAdministrador de la cuenta del Administrador de la Empresa 1 para eliminar la colisión de identidades y lograr un modelo 100% simétrico y profesional.
* **1. Separación de Cuentas y Dominios Corporativos:**
  * **SuperAdministrador Global:** `superadmin@trazabilidad.com` (Plataforma SaaS, acceso irrestricto y bypass global en todos los tenants).
  * **Empresa 1 (*iStore Bolivia S.A.*, Tenant 1):**
    * Administrador: `admin@istore.com` (Rol `AdministradorEmpresa` aislado al Tenant 1).
    * Usuarios operativos: `operaciones@istore.com`, `ventas@istore.com`, `auditor@istore.com`.
  * **Empresas 2 a 5:** Se mantienen con sus dominios corporativos (`@techimport.com`, `@andinadigital.com`, etc.).
* **2. Actualización de Seeding:**
  * Modificado `backend/seed.py` para crear explícitamente a `superadmin@trazabilidad.com` como operador SaaS global, asignar `admin@istore.com` como administrador de Empresa 1 y limpiar roles sobrantes de cuentas previas.
* **3. Actualización de Pruebas:**
  * En `tests/test_prompt9_security_verification.py`, parametrización actualizada con `admin@istore.com` y los roles operativos de `@istore.com`.
  * Validación de que `admin@techimport.com` (Tenant 2) no ve ni a `istore.com` ni a `superadmin@trazabilidad.com`.
* **4. Verificación de Suite:**
  * `pytest -q`: **245 passed, 0 failed** en 143.56s (100% verde).
* **5. Documentación y README:**
  * `README.md` actualizado con la nueva tabla canónica de credenciales de prueba.

---

## 0. Sesión actual (2026-11-23): Prompt 9 - Verificación Final de Seguridad Integral con Usuarios Demo (Sprint 5)

**Petición:** Ejecutar una verificación exhaustiva de seguridad integral con los usuarios del README (`admin`, `operaciones`, `ventas` y `auditor` de la empresa 1, y `admin` de la empresa 2, contraseña `Admin123!`), probando los 5 escenarios clave de hardening implementados en Sprint 5 sin tocar Git.

### 1. Escenarios Evaluados y Resultados
* **A) Restricción de Roles Operativos:**
  * Usuarios con roles `GestorOperaciones`, `GestorVentasPostventa` y `Auditor` (de Empresa 1) reciben `403 Forbidden` al intentar ejecutar mutaciones (`POST`, `PUT`, `DELETE`) sobre `/users` y `/tenants`, así como al intentar asignar roles (`POST /users/{id}/roles`).
  * Estado: **OK (PASSED)**.
* **B) Aislamiento Estricto de Administrador de Empresa 2:**
  * El usuario `admin@techimport.com` (tenant 2) no puede visualizar ni listar la empresa 1 (`GET /tenants/1` -> `404 Not Found`; `GET /tenants` devuelve solo su empresa).
  * No visualiza usuarios de la empresa 1 ni a SuperAdministradores en `GET /users` (devuelve exclusivamente los usuarios pertenecientes al tenant 2).
  * Estado: **OK (PASSED)**.
* **C) Aislamiento en Switch-Tenant:**
  * Al autenticarse como admin con tenant activo 2 (o realizar switch-tenant a la empresa 2), las consultas a `/actors`, `/units`, `/locations` y `/purchases` devuelven estrictamente recursos con `idtenant = 2`.
  * Estado: **OK (PASSED)**.
* **D) Protección de Catálogo Maestro (`DELETE /products`):**
  * Roles no autorizados (`AdministradorEmpresa` de tenant 2, `GestorOperaciones`, `GestorVentasPostventa` y `Auditor`) reciben `403 Forbidden` al intentar invocar `DELETE /products/{id}`. Solo el `SuperAdministrador` tiene privilegios de eliminación del catálogo global.
  * Estado: **OK (PASSED)**.
* **E) Integridad Referencial con Respuesta 409:**
  * Intentos de eliminación de entidades con registros dependientes (ej. unidad con reporte de sospecha vinculado) responden `409 Conflict` con mensaje explicativo, evitando errores `500` por violaciones de clave foránea.
  * Estado: **OK (PASSED)**.

### 2. Archivos Modificados / Creados
* `backend/app/packages/p1_seguridad/controllers/cu002_usuarios/user_controller.py`: corrección de imports de `Role` y `UsuarioTenantRol` para el filtrado de SuperAdministradores en listados de usuarios.
* `backend/tests/test_prompt9_security_verification.py`: suite automatizada con 10 tests que comprueban los 5 escenarios anteriores con las credenciales demo.

### 3. Resultados de Pruebas
* `pytest tests/test_prompt9_security_verification.py -vv`: **10 passed, 0 failed** en 4.15s.
* Suite completa: `pytest -q`: **244 passed, 0 failed** en 139.76s (0 regresiones).

---

## 0. Sesión actual (2026-11-23): Prompt 8 - Configuración, Migraciones Alembic en BD vacía, Depuración de Bitácora y Fixtures (CU-005 / CU-036 / CU-037)

**Petición:** Implementar el Prompt 8 del backlog de hardening (Sprint 5) sin tocar Git ni pushear a repositorios remotos.
* **1. Dependencia en `requirements.txt`:** Se añadió `python-multipart==0.0.20` con versión fija para garantizar arranque y soporte de formularios.
* **2. Corrección de Migración Alembic `f1a2b3c4d5e6`:**
  * Se añadió en `f1a2b3c4d5e6_tablas_sprint4_facturacion_cuotas.py` la inspección y creación previa de las tablas `plan` y `suscripcion` (junto con el enum `estado_suscripcion_enum`) si no existen, resolviendo la llave foránea `idsuscripcion` de la tabla `factura`.
  * Verificado contra una base de datos PostgreSQL vacía (`test_empty_migration_db`): `alembic upgrade head` finaliza al 100% exitosamente sin errores.
* **3. Fixtures automáticos para planes y suscripciones:**
  * Se integró la invocación automática e idempotente de `seed_plans_and_subscriptions()` en los fixtures `setup_test_data` (`conftest.py`) y `ensure_seed_plans_subscriptions` (`test_subscriptions_cu036_cu037.py`), desacoplando las pruebas de la ejecución manual previa del seed.
* **4. Optimización de Auditoría en `Bitacora` (`CU-005`):**
  * Se configuró el middleware de auditoría en `app/main.py` para ignorar peticiones `GET` convencionales (evitando saturación de la base de datos).
  * Se auditan exclusivamente operaciones de mutación (`POST`, `PUT`, `PATCH`, `DELETE`) y accesos críticos de seguridad (`/auth/me`, `/auth/switch-tenant`, `/backup/tenants`, `/bitacora/export`).
* **5. Decisión de Arquitectura:** Registrado **ADR-015** en `docs/DECISION_LOG.md`.
* **6. Pruebas:** Creado `tests/test_prompt8_config_migrations_audit.py` (4 tests nuevos). Suite global verificada: **234 passed, 0 failed, 0 errors**.

---

## 0-bis. Sesión anterior (2026-11-23): Prompt 7 - Login sin límite de intentos (429 y Bitácora) y ofuscación segura de errores 500 (CU-004 / CU-005)

**Petición:** Implementar el Prompt 7 del backlog de hardening (Sprint 5) sin tocar Git ni pushear a repositorios remotos.
* **A) Mitigación de fuerza bruta en `POST /auth/login`:**
  * Implementación de `LoginRateLimiter` en memoria con `threading.Lock` para control atómico concurrente y cero latencia de I/O de red.
  * Límite estricto: máximo 5 intentos fallidos consecutivos por combinación `(email, IP)`. Al 5to fallo, se activa bloqueo temporal de 15 minutos (`locked_until`).
  * El 6to intento responde inmediatamente `HTTP 429 Too Many Requests` con mensaje `"Demasiados intentos fallidos. Cuenta temporalmente bloqueada por 15 minutos."`.
  * Todo intento durante el periodo de bloqueo (incluso con credenciales válidas) es denegado con 429.
  * Login exitoso reinicia el contador de intentos fallidos a 0.
  * Persistencia en auditoría: al activarse el bloqueo se registra en la tabla `Bitacora` (`CU-005`) con `accion="BLOQUEO_LOGIN"`, `entidad="Autenticacion"`, IP y hora oficial de Bolivia (BOT, UTC-4).
* **B) Ofuscación de errores no controlados (500) en `app/main.py`:**
  * El manejador global `@app.exception_handler(Exception)` registra el detalle técnico y stack trace únicamente en los logs del servidor (`logger.error`).
  * Al cliente HTTP se responde únicamente un JSON estandarizado y seguro: `{"detail": "Error interno del servidor"}` con status 500, eliminando `error_detail`, `error_type` y `trace`.
* **C) Decisión de Arquitectura:**
  * Documentada en [`docs/DECISION_LOG.md`](file:///c:/Users/rafae/OneDrive/Escritorio/universidad/si2/p_semestral/Grupo-5-/docs/DECISION_LOG.md) como **ADR-014**.
* **D) Suite de pruebas en `tests/test_auth_rate_limit_and_500.py`:**
  * 4 pruebas pasando al 100%: 5 fallos devuelven 401 y el 6to 429; login exitoso reinicia contador; bloqueo registrado en Bitácora; y error 500 forzado sin filtración de `error_detail` ni `error_type`.
* **Suite global verificada:** **230 passed, 0 failed, 0 errors**.

---

## 0-bis. Sesión anterior (2026-11-23): Prompt 6 - Control de errores de integridad referencial 409 en eliminaciones (DELETE)

**Petición:** Implementar el Prompt 6 del backlog de hardening (Sprint 5) sin tocar Git ni pushear a repositorios remotos.
* En operaciones `DELETE` de entidades clave (`/actors/{id}`, `/units/{id}`, `/categories/{id}`, `/locations/{id}`, `/tenant-catalog/{id}`, `/documents/{id}`): capturar `sqlalchemy.exc.IntegrityError`, ejecutar `db.rollback()` y responder `HTTPException(409)` con mensaje claro `"No se puede eliminar: tiene registros relacionados."`.
* Prevenir errores 500 no controlados ante violaciones de llaves foráneas en base de datos.
* Suite de pruebas en `tests/test_integrity_409.py` (4 tests verdes al 100%):
  1. `test_delete_actor_con_dependientes_retorna_409`: intento de borrado de actor con compras asociadas -> 409 Conflict.
  2. `test_delete_unit_con_dependientes_retorna_409`: intento de borrado de unidad con reporte de sospecha vinculado -> 409 Conflict.
  3. `test_delete_category_con_dependientes_retorna_409`: intento de borrado de categoría con productos vinculados -> 409 Conflict.
  4. `test_delete_location_con_dependientes_retorna_409`: intento de borrado de ubicación con unidades asociadas -> 409 Conflict.
* Suite global verificada: **226 passed, 0 failed, 0 errors**.

### Archivos modificados
* `backend/app/packages/p3_actores/controllers/cu013_actores_cadena/actor_controller.py`: captura `IntegrityError` con rollback y retorno 409 en `delete_actor`.
* `backend/app/packages/p4_trazabilidad/controllers/cu015_unidades_producto/unit_controller.py`: captura `IntegrityError` con rollback y retorno 409 en `delete_unit`.
* `backend/app/packages/p2_catalogo/controllers/cu009_categorias/category_controller.py`: captura `IntegrityError` con rollback y retorno 409 en `delete_category`.
* `backend/app/packages/p3_actores/controllers/cu014_ubicaciones/location_controller.py`: captura `IntegrityError` con rollback y retorno 409 en `delete_location`.
* `backend/app/packages/p2_catalogo/controllers/cu008_catalogo_empresa/tenant_catalog_controller.py`: captura `IntegrityError` con rollback y retorno 409 en `delete_catalog_item`.
* `backend/app/packages/p5_comercial/controllers/cu032_documentos_unidad/document_controller.py`: captura `IntegrityError` con rollback y retorno 409 en `delete_document`.
* `backend/tests/test_integrity_409.py`: 4 tests de validación 409.

---

## 0-bis. Sesión anterior (2026-11-22): Prompt 5 - Control de roles y protección referencial 409 en `/products` (CU-006 / CU-007)

**Petición:** Implementar el Prompt 5 del backlog de hardening (Sprint 5) sin tocar Git (`no lo actualices en el git`).
* Protección RBAC en mutaciones del catálogo maestro (`POST /products`, `PUT /products/{id}`, `DELETE /products/{id}`, `POST /products/{id}/variants`, `PUT /variants/{id}`, `DELETE /variants/{id}`): reservado exclusivamente para `SuperAdministrador`. Roles operativos (`GestorOperaciones`, `GestorVentasPostventa`, etc.) y administradores de empresa (`AdministradorEmpresa` de cualquier tenant) reciben `403 Forbidden`.
* Integridad referencial con retorno `409 Conflict`:
  * Al intentar eliminar un producto con unidades físicas o compras asociadas, responde `409 Conflict` con mensaje claro explicativo.
  * Al intentar eliminar una variante con unidades físicas o compras asociadas, responde `409 Conflict`.
  * Al intentar eliminar una certificación asignada a productos del catálogo, responde `409 Conflict`.
* Suite de pruebas en `tests/test_products_security.py` (7 tests verdes al 100%).

### Archivos modificados
* `backend/app/packages/p2_catalogo/controllers/cu006_productos_variantes/product_controller.py`:
  * `ROLES_GESTION_PRODUCTO = ("SuperAdministrador",)` (solo SuperAdministrador gestiona el catálogo global).
  * `delete_product`: valida previamente si existen unidades físicas (`UnidadProducto`) o compras (`CompraDetalle`) vinculadas a través de sus variantes y retorna `409 Conflict`. Captura además `IntegrityError` con rollback y retorno `409`.
  * `delete_variant`: valida unidades físicas y compras vinculadas retornando `409 Conflict`, con captura de `IntegrityError`.
* `backend/app/packages/p2_catalogo/controllers/cu007_certificaciones/certification_controller.py`:
  * `delete_certification`: valida si la certificación está asignada a productos (`ProductoCertificacion`) y retorna `409 Conflict`, con captura de `IntegrityError`.
* `backend/tests/test_products_security.py`:
  * 7 tests cubriendo: 403 a GestorOperaciones y Admin de otra empresa en DELETE/POST/PUT, 200 a SuperAdmin en producto limpio, 409 en producto con unidades, 409 en producto con compras, 409 en variante con unidades, 409 en certificación asignada.

---

## 0-bis. Sesión actual (2026-11-22): Prompt 4 - Aislamiento de cambio de empresa (Switch-Tenant) en Actores, Ubicaciones, Unidades y QR

**Petición:** Implementar el Prompt 4 del backlog de hardening (Sprint 5) sin tocar Git (`no lo actualices en el git`).
* Reemplazo de `get_user_tenant_id` por `resolve_tenant_id` en controladores para respetar el `tenant_id` activo en el token JWT.
* Validación estricta multi-tenant al crear/editar unidades: custodio, ubicación y variante deben pertenecer al tenant activo (o responder 422/403).
* Sincronización del selector de empresa en el dashboard web de Angular.
* Suite de pruebas en `tests/test_switch_tenant_isolation.py` (3 tests verdes al 100%).

---

## 0-ter. Sesión actual (2026-11-22): Prompt 3 - Control de roles y aislamiento multi-tenant en `/users` (CU-002)

**Petición:** Implementar el Prompt 3 del backlog de hardening (Sprint 5) sin tocar Git (`no lo actualices en el git`).
* Protección RBAC en mutaciones (`POST`, `PUT`, `DELETE /users`): solo `SuperAdministrador` y `AdministradorEmpresa`. Roles operativos y auditores reciben `403 Forbidden`.
* Protección RBAC en lecturas (`GET /users`, `GET /users/{id}`): solo `SuperAdministrador`, `AdministradorEmpresa` y `Auditor`.
* Aislamiento multi-tenant: salvo `SuperAdministrador`, un usuario solo puede listar, ver, editar o eliminar usuarios con vínculo `UsuarioTenant` en su empresa activa. Consultas fuera de su empresa responden `404 Not Found`.
* Auto-protección: un usuario no puede eliminarse ni desactivarse a sí mismo (`400 Bad Request`).
* Jerarquía administrativa: un `AdministradorEmpresa` no puede editar ni eliminar a un `SuperAdministrador` (`403 Forbidden`).
* Pruebas en `tests/test_users.py`: 10 pruebas pasando al 100%.

### Backend implementado
* **Controlador modificado:** `app/packages/p1_seguridad/controllers/cu002_usuarios/user_controller.py`:
  * Dependencias diferidas `_require_admin_or_superadmin` y `_require_gestion_or_auditor` para evitar importaciones circulares.
  * `list_users`: filtrado forzoso por `active_tenant_id` para roles distintos de `SuperAdministrador`.
  * `create_user`: vinculación obligatoria a la empresa activa del administrador solicitante.
  * `get_user`: verificación de pertenencia multi-tenant; retorno `404` ante usuarios de otra empresa.
  * `update_user`: validación de auto-desactivación (`400`), aislamiento multi-tenant (`404`) y protección a SuperAdmin (`403`).
  * `delete_user`: validación de auto-eliminación (`400`), aislamiento multi-tenant (`404`) y protección a SuperAdmin (`403`).

### Pruebas de verificación
* `tests/test_users.py` (10 pruebas):
  1. `test_list_users_authenticated`: 200 OK.
  2. `test_create_user_success`: 201 Created.
  3. `test_create_user_duplicate_email`: 400 Bad Request.
  4. `test_get_user_by_id`: 200 OK.
  5. `test_update_user`: 200 OK.
  6. `test_delete_user_soft`: 200 OK.
  7. `test_roles_no_autorizados_no_pueden_mutar_usuarios`: Ventas, Operaciones y Auditor reciben 403 en POST/PUT/DELETE.
  8. `test_admin_otra_empresa_recibe_404_en_usuarios_ajenos`: Admin T2 recibe 404 al consultar, editar o eliminar usuario de T1.
  9. `test_usuario_no_puede_eliminarse_ni_desactivarse_a_si_mismo`: DELETE o PUT activo=False sobre sí mismo retorna 400.
  10. `test_admin_empresa_no_puede_editar_ni_eliminar_superadmin`: Admin T1 recibe 403 al intentar editar o eliminar SuperAdmin.
* **Suite de seguridad consolidada:** `pytest tests/test_users.py tests/test_tenants.py tests/test_rbac.py tests/test_roles.py -v` -> **29 PASSED, 0 FAILED**.
* **Nota estricta:** NO se ha realizado commit ni push a Git.

---

## 0-bis. Sesión actual (2026-11-22): Prompt 2 - Endpoints `/tenants` sin control de roles (CU-001)

**Petición:** Implementar el Prompt 2 del backlog de hardening (Sprint 5) sin tocar Git (`no lo actualices en el git`).
* Mutaciones de empresas (`POST /tenants`, `PUT /tenants/{id}`, `DELETE /tenants/{id}`) reservadas exclusivamente para `SuperAdministrador`.
* Listado general (`GET /tenants`): `SuperAdministrador` lista todas las empresas; para otros roles devuelve únicamente su empresa activa (lista de 1 elemento) para preservar compatibilidad con combos de la UI sin filtrar datos ni NITs de competidores.
* Detalle (`GET /tenants/{id}`): `SuperAdministrador` accede a cualquiera; otros roles solo acceden si `idtenant == active_id`, denegando acceso ajeno con `403 Forbidden`.
* Frontend Angular: ruta `/tenants` protegida con `roleGuard(['SuperAdministrador'])` y menú `🏢 Empresas` en el dashboard visible únicamente para `SuperAdministrador`.
* Pruebas en `tests/test_tenants.py`: 9 pruebas (6 de SuperAdmin + 3 de seguridad RBAC multi-tenant) pasando al 100%.

### Backend implementado
* **Controlador modificado:** `app/packages/p1_seguridad/controllers/cu001_tenants/tenant_controller.py`:
  * Dependencia diferida `_require_superadmin_role` para prevenir ciclos de importación circular con `app.controllers.__init__`.
  * `POST /tenants`, `PUT /tenants/{idtenant}` y `DELETE /tenants/{idtenant}` decorados con `dependencies=[Depends(_require_superadmin_role)]`.
  * `GET /tenants`: evalúa `_es_superadmin(db, current_user)`. Si no lo es, filtra la consulta exclusivamente al `active_id = resolve_tenant_id(db, current_user)`, retornando `total=1` y solo su empresa.
  * `GET /tenants/{idtenant}`: valida pertenencia de la empresa para roles no superadmin (`403 Forbidden`).

### Frontend Web adaptado
* `frontend/src/app/app.routes.ts`: guarda de ruta `roleGuard(['SuperAdministrador'])` en `/tenants`.
* `frontend/src/app/controllers/pages/dashboard.controller.ts`: `canAccess('tenants')` retorna `true` exclusivamente para `SuperAdministrador`.
* `npm run build` verificado exitosamente (0 errores).

### Pruebas de verificación
* `tests/test_tenants.py`:
  1. `test_list_tenants_superadmin`: 200 OK, total >= 2 empresas.
  2. `test_create_tenant_superadmin_success`: 201 Created.
  3. `test_create_tenant_duplicate_nit`: 400 Bad Request.
  4. `test_get_tenant_by_id_superadmin`: 200 OK.
  5. `test_update_tenant_superadmin`: 200 OK.
  6. `test_delete_tenant_soft_superadmin`: 200 OK.
  7. `test_roles_no_autorizados_no_pueden_mutar_tenants`: Auditor, GestorVentas, GestorOperaciones y AdministradorEmpresa reciben 403 en POST/PUT/DELETE.
  8. `test_admin_empresa2_no_puede_ver_tenant1`: Admin T2 recibe 403 en `GET /tenants/1` y 200 en `GET /tenants/2`.
  9. `test_usuario_no_superadmin_solo_lista_su_empresa_activa`: Usuario T2 solo recibe su empresa en `GET /tenants` (`total == 1`).
* **Suite de seguridad combinada:** `pytest tests/test_tenants.py tests/test_rbac.py tests/test_roles.py tests/test_users.py -v` -> **25 PASSED, 0 FAILED**.
* **Nota estricta:** NO se ha realizado commit ni push a Git.

---

## 0-bis. Sesión actual (2026-11-22): Prompt 1 - Hardening RBAC y Prevención de Escalada de Privilegios (CU-003)

**Petición:** Implementar el Prompt 1 del backlog de hardening (Sprint 5) sin tocar Git (`no lo actualices en el git`).
* Protección contra escalada de privilegios en asignación de roles (`POST /users/{idusuario}/roles`).
* Bloqueo para que `AdministradorEmpresa` no pueda auto-adjudicarse o asignar el rol `SuperAdministrador`.
* Validación multi-tenant: `AdministradorEmpresa` no puede alterar roles de usuarios de otro tenant ni consultar roles fuera de su empresa.
* Protección de endpoints de lectura de roles (`GET /roles`, `GET /permissions`, `GET /roles/{idrol}/permissions`, `GET /users/{idusuario}/roles`) exigiendo roles autorizados (`SuperAdministrador`, `AdministradorEmpresa`, `Auditor`).

### Backend implementado
* **Controlador modificado:** `app/packages/p1_seguridad/controllers/cu003_roles_permisos/role_controller.py`:
  * Inyección de `_requires_asignacion_roles = require_roles("SuperAdministrador", "AdministradorEmpresa")` en `POST /users/{idusuario}/roles`.
  * Verificación en `assign_user_roles`:
    * Si el solicitante es `AdministradorEmpresa` e intenta asignar el rol `SuperAdministrador`, se rechaza con `403 Forbidden` ("Un Administrador de Empresa no tiene privilegios para asignar el rol SuperAdministrador").
    * Validación multi-tenant: si el usuario destino pertenece a otro tenant, se rechaza con `403 Forbidden`.
  * Inyección de `_requires_lectura_roles = require_roles("SuperAdministrador", "AdministradorEmpresa", "Auditor")` en:
    * `GET /roles`
    * `GET /permissions`
    * `GET /roles/{idrol}/permissions`
    * `GET /users/{idusuario}/roles`
  * Verificación multi-tenant en `get_user_roles`: usuarios no superadministradores no pueden consultar los roles de usuarios de otra empresa (`403 Forbidden`).

### Pruebas de verificación
* **Nuevo suite:** `backend/tests/test_rbac.py` con 5 casos de prueba:
  1. `test_gestor_operaciones_no_puede_asignar_roles`: Retorna `403 Forbidden`.
  2. `test_admin_empresa_no_puede_asignar_superadministrador`: Retorna `403 Forbidden`.
  3. `test_admin_empresa_no_puede_modificar_usuario_otra_empresa`: Retorna `403 Forbidden`.
  4. `test_superadministrador_asigna_roles_exitosamente`: Retorna `200 OK` y asigna roles correctamente.
  5. `test_endpoints_lectura_roles_protegidos`: Bloquea anónimos/gestores (`403`), permite admins/auditores (`200`), y bloquea lectura cruzada entre tenants (`403`).
* **Actualización en tests existentes:** `backend/tests/test_roles.py` adaptado para usar la fixture `auth_headers` (usuario con rol autorizado `SuperAdministrador`), verificando que los 5 tests de roles continúen en verde tras la introducción de RBAC.
* **Resultado de pruebas:** `pytest tests/test_roles.py tests/test_users.py tests/test_rbac.py -v` -> **16 PASSED, 0 FAILED**.
* **Suite global total:** **214 PASSED (0 fallos)**.

### Archivos modificados / creados
* Modificado: `backend/app/packages/p1_seguridad/controllers/cu003_roles_permisos/role_controller.py`
* Modificado: `backend/tests/test_roles.py`
* Creado: `backend/tests/test_rbac.py`
* Documentación: `docs/ai/HANDOFF_LATEST.md`, `docs/ai/CURRENT_STATE.md`, `docs/ai/NEXT_STEPS.md`
* **Nota estricta:** NO se ha realizado commit ni push a Git.

---

## 0-bis. Sesión anterior (2026-11-22): Stripe Checkout de pago único (ADR-013)

**Petición:** integrar una pasarela de pago para cobros únicos en ventas (P5) y facturación SaaS (P8), con webhook firmado, reembolso y cero regresiones. Alcance confirmado: primero pago único; suscripciones recurrentes y QR de cobro quedan para después (CU-041/CU-042). El QR actual (CU-016) es de trazabilidad y no se tocó.

### Backend implementado
* **Capa compartida nueva:** `app/services/payments/stripe_gateway.py` (Checkout Session `mode=payment`, consulta de sesión, reembolso y verificación de `Stripe-Signature`) y `app/services/payments/stripe_webhook.py` (despacho idempotente). `stripe==11.5.0` añadido a `requirements.txt`; ya estaba instalado.
* **Contratos aditivos** (prefijos `/api/v1` y endpoints manuales intactos): `POST /payments/checkout`, `GET /payments/{idpago}/checkout`, `POST /payments/{idpago}/refund`, `POST /invoices/{idfactura}/checkout` y `POST /payments/webhook` (único para ventas y facturas, sin JWT).
* **Metadata firmada** `kind=venta|factura`, `tenant_id`, `id`, `ref`: el webhook valida la firma con `STRIPE_WEBHOOK_SECRET`, resuelve el tenant del metadata y vuelve a verificar `Venta.idtenant` / `Factura.idtenant`. Firma inválida → 400; sin credenciales → 503; error de Stripe → 502.
* **Idempotencia:** modelo/tabla nueva `StripeEvent` → `stripeevento`, `eventoid` único; reenvío = `duplicado=true`, sin efectos. Se atienden `checkout.session.completed`, `checkout.session.expired`, `payment_intent.payment_failed` y `charge.refunded`.
* **Columnas aditivas** (`pago` y `cobro`): `proveedor` (default `manual`), `idtransaccion`, `paymentintentid`, `estadopasarela`. Migración Alembic `c7d8e9f0a1b2` aplicada (`alembic current` en head). Los pagos/cobros manuales siguen igual.
* **Efectos de negocio:** confirmación de venta reutiliza `_sync_venta_estado()` y escribe Bitácora (CU-005); pago de factura reutiliza `_saldo()`, marca factura `pagada` y activa/renueva la `Suscripcion`; reembolso usa el `PaymentIntent`.
* **Configuración:** nuevos `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`, `STRIPE_WEBHOOK_TOLERANCE_SECONDS` en `app/core/config.py` y placeholders en `.env.example`. La llave del usuario está en `.env` local y **no se versionó**. Falta el `whsec_...` del webhook.

### Verificación
* `tests/test_stripe_pagos_cu027_cu039.py` (5 pruebas): checkout propio, venta ajena 404, firma inválida 400, webhook duplicado sin efecto, estado + reembolso y checkout de factura que activa suscripción. Suite completa: **209 passed, 0 failed, 0 errors**. `npm run build` OK (sólo warnings de presupuesto CSS preexistentes); `flutter analyze` → **No issues found**.

### Archivos nuevos / modificados
`trazabilidad/backend/app/core/config.py`, `.env.example`, `requirements.txt`, `app/models/__init__.py`, `app/packages/p5_comercial/{models/cu027_pagos/{pago.py,stripe_event.py},views/cu027_pagos/payment_views.py,controllers/cu027_pagos/payment_controller.py}`, `app/packages/p8_suscripciones/{models/cu039_facturacion/factura.py,views/cu039_facturacion/billing_views.py,controllers/cu039_facturacion/billing_controller.py}`, `app/services/payments/{__init__.py,stripe_gateway.py,stripe_webhook.py}`, `alembic/versions/c7d8e9f0a1b2_stripe_pago_unico_cu027_cu039.py`, `tests/test_stripe_pagos_cu027_cu039.py`, `docs/{DECISION_LOG.md,USE_CASES_MAP.md,ai/*.md}`.

---

## 0-bis. Sesión anterior (2026-11-22): Poblado completo del `top 10` por período

**Petición:** «falta poblar porque cuando top 10 unidades vendidas en el último trimestre solo me muestra 6, es decir no muestras las últimas 4» y «ejecútalo, debe estar bien poblado todo».

### Diagnóstico
* No era paginación: `query_sales_ranking_data()` hace `ranking_consolidado[:limite]`, es decir `top 10` es un **tope**, no un mínimo. En `2026-09 → 2026-12` solo había **6 productos con señal**: 3 del bloque `HIST` y 3 del seed canónico. El catálogo tiene 21–37 variantes por tenant, pero el seed histórico vendía únicamente sobre las 3 primeras.

### Cambio implementado (ADR-012)
* `seed_historical_6m.py` (reutilizado por el envoltorio 36m) incorpora un bloque idempotente **`HSALE`** con claves naturales propias que no colisionan con `HIST`.
* `seleccionar_variantes_top10()` elige una variante activa por **producto distinto**, excluye los 3 productos base, descarta nombres `Producto Tenant %` y ordena por nombre real. Máximo 10 por tenant (7 en tenants 2–5, que tienen 10 productos activos → 10 con señal en total).
* Por producto/mes de los 36 meses: unidad vendida + QR + consulta, venta + detalle + asignación + pago, evento + condición + anclaje blockchain, alerta y garantía; unidad disponible, devolución y documento cada 6 meses; reporte de sospecha con evidencia cada 3 meses. Un cliente distinto por producto evita colisiones en la clave de `Venta` (`idcliente`, `fechaventa`) y mantiene `total = sum(detalles)`.
* Devoluciones adicionales para las unidades vendidas de los 3 productos `HIST` (meses `mes % 6 == 0`) con motivo válido del enum (`daño_transporte`).
* Regeneración con `--reset-history` + ejecución real. **Manifest final: 41.838 IDs**. `--dry-run` posterior: **0 filas nuevas** (idempotente).

### Verificación
* `top 10 ... último trimestre` → **10 filas en los 5 tenants**, con nombres reales (`iPhone 15`, `iPhone 16 Pro`, `AirPods Pro`, `Galaxy S24`, `Smartwatch Fit 2`, `iPhone 15 Pro`, `iPhone 16`, `iPhone 15 Pro Max`, `Cargador Apple 20W USB-C`, `iPhone 16 Pro Max`).
* Las **50 fichas** (`product_detail`, rango fijo 36 meses) tienen **todas sus métricas > 0**; ninguna devolución, garantía, ingreso o consulta QR en cero.
* `tests/test_ai_voice_query_customization.py` ampliado a **13 pruebas** (selector del seed y ranking lleno). Suite completa: **204 passed, 0 failed, 0 errors**. `npm run build` OK (solo warnings de presupuesto CSS preexistentes). `flutter analyze` → **No issues found**.

### Archivos modificados
`trazabilidad/backend/seed_historical_6m.py`, `trazabilidad/backend/seed_historical_36m.manifest.json`, `trazabilidad/backend/tests/test_ai_voice_query_customization.py`, `docs/{DECISION_LOG.md,ai/CURRENT_STATE.md,ai/HANDOFF_LATEST.md,ai/NEXT_STEPS.md}`.

---

## 0-ter. Sesión anterior (2026-11-21): Análisis detallado por producto dentro del asistente

**Petición:** que el asistente muestre un análisis detallado por producto (unidades, ingresos, N° ventas y más métricas que salían a 0), con datos reales, siempre sobre un rango amplio de 36 meses, para los 5 tenants demo. Alcance aprobado: detalle dentro del asistente, seed idempotente re-ejecutable y cero regresiones.

### Backend (P4/CU-022, respuesta aditiva)
* `ParsedQuery.wants_detail` y `_DETALLE` en `voice_query_parser.py` reconocen «analisis detallado / detalle de / ficha de / desglose de / perfil de…». `parse_detail_period(now)` fija **36 meses** (`2023-12 → 2026-11`) con hora Bolivia, aunque la consulta pida otro período. El productor se resuelve con `_resolver_filtros_catalogo()` contra `CatalogoTenant`, sin duplicar lógica.
* `build_product_detail()` en `voice_query_engine.py` consulta por tenant y variantes del producto: unidades, ingresos, N° ventas, cobrado, ticket y precio promedio, stock/disponibles/en tránsito, devoluciones y tasa, garantías, consultas QR, eventos, alertas, reportes de sospecha y tendencia mensual. Todas las tablas hijas se filtran desde un padre con `idtenant` (`Venta`, `UnidadProducto`, `EventoTrazabilidad`, `Alerta`, `ReporteSospecha`).
* `POST /api/v1/ai/voice-report` devuelve **`product_detail`** (opcional) con insignia `Detalle · 36 meses · <empresa>`; `filters_applied` añade `analisis_detallado`, `detalle_producto`, `detalle_desde` y `detalle_hasta`. La consulta principal conserva su período original y los followups pasan a incluir «Análisis detallado de …».
* `REPORT_CACHE` incluye el detalle; `GET /api/v1/ai/reports/{id}/export` lo pasa a `report_generator.py`, que añade la hoja **«Detalle Producto»** en Excel y una sección de ficha en PDF.

### Seed histórico (idempotente y re-ejecutable)
* `seed_historical_6m.py` (reutilizado por el envoltorio 36m) ahora genera: una **garantía por unidad vendida**, un **reporte de sospecha por unidad** en meses `mes % 3 == 0` (tickets `-Uxx`, sin chocar con el ticket histórico) y una **unidad en tránsito por variante activa** cada 6 meses. Las claves naturales siguen siendo deterministas (`numeroserie`, `codigoticket`, `idunidad`), por lo que re-ejecutar es no-op.
* `--dry-run` validado (+2.340 y luego +726 filas, rollback limpio). Ejecución real completada: **20.401 IDs** en `seed_historical_36m.manifest.json`; la segunda ejecución reporta **0 filas nuevas**.
* Verificado en tenant 1, producto «iPhone 15»: 80 unidades vendidas, $34.164 ingresos, 36 ventas, 72 garantías, 48 reportes, 146 consultas QR, 37 alertas y 48 unidades en tránsito. **Ninguna métrica de la ficha queda en 0.**

### Web Angular y Móvil Flutter
* Modelos aditivos `product_detail` en `ai-report.model.ts` y `ProductDetailModel` en `ai_report_model.dart`.
* Dashboard web: tarjeta «DETALLE · 36 MESES» con KPIs, rango y chips de tendencia mensual, además de chips de seguimiento dentro del resultado. Asistente móvil: `_buildProductDetailCard()` con el mismo contenido y chips reutilizando los followups existentes.

### Verificación
* `tests/test_ai_voice_query_customization.py` ampliado a **11 pruebas** (añade parser de detalle, métricas reales, rango 36m aunque la consulta pida 1 mes, invisibilidad de producto ajeno y exportación con ficha).
* **Suite completa: 202 passed, 0 failed, 0 errors**. `npm run build` OK (solo warnings de presupuesto CSS preexistentes). `flutter analyze` → **No issues found**. ADR-011 registrado.

### Archivos nuevos / modificados
`app/services/ai/{voice_query_parser.py,voice_query_engine.py,report_generator.py}`, `app/packages/p4_trazabilidad/{views/cu022_ia/ai_schemas.py,controllers/cu022_ia/ai_report_controller.py}`, `tests/test_ai_voice_query_customization.py`, `seed_historical_6m.py`, `seed_historical_36m.manifest.json`, `frontend/src/app/{models/ai-report.model.ts,views/pages/dashboard.view.html}`, `mobile/lib/{models/ai_report_model.dart,views/widgets/voice_assistant_sheet.dart}`, `docs/{DECISION_LOG.md,ai/*.md}`.

---

## 0-quater. Sesión anterior (2026-11-20): Asistente de Informes Dinámicos por Voz personalizable

**Petición:** mejorar el asistente para entender consultas ricas por empresa, p. ej. «¿Cuáles fueron los 10 productos más vendidos en el último trimestre o 3 meses?», con chips sugeridos y una insignia visible de la interpretación aplicada en web y móvil. Alcance aprobado: motor + chips + badge, endurecimiento multi-tenant y ventas/fechas en todos los intentos.

### Backend (P4/CU-022, extensiones aditivas)
* **Nuevo parser determinista** `app/services/ai/voice_query_parser.py`: `ParsedQuery` extrae `intent` (`ventas`, `compras`, `logistica`, `auditoria`, `inventario`), rango temporal, `limit`, `metric`, `estado`, `producto` y `proveedor`. Normaliza acentos, calcula fechas con `get_bolivia_now()` (BOT) y **no añade dependencias**. Períodos: hoy/ayer, 7 días, mes, trimestre (3 meses), semestre (6 meses), año, «últimos N meses/días» y año explícito; sin período = todo el historial (comportamiento previo intacto).
* `top N` acepta `top 10`, `los 10 productos`, `primeros 5` y números en palabras; **`top 999` se acota a 50**. Métrica `unidades` por defecto; `ingresos` con `ingresos/facturación/monto/rentables`.
* **Nuevo ranking P5** `query_sales_ranking_data()`: `Venta → VentaDetalle → VarianteProducto → Producto`, filtrado por `Venta.idtenant`, rango de fechas, estado y producto; orden por unidades o ingresos y límite `top N` (default 10). KPIs, gráfico de barras y tabla con `#`, producto, unidades, ingresos USD y número de ventas.
* **Fechas en todos los intentos**: compras (`fechacompra`), logística (`fechasalida`), inventario (`fechaingreso`) y auditoría (`fechahora`). El intérprete resuelve productos/proveedores mencionados contra el **catálogo del tenant**.
* **Corrección de aislamiento (ADR-001/005):** `query_audit_data()` ahora hace join con `UsuarioTenant` y filtra por tenant (antes filtraba globalmente); `/ai/voice-report` usa `resolve_tenant_id(db, current_user)` en lugar del fallback `idtenant=1`.
* **Exportación endurecida:** `REPORT_CACHE` guarda `tenant_id`; `GET /api/v1/ai/reports/{id}/export` exige JWT y devuelve **404** si la empresa activa no coincide con la del snapshot (incluso SuperAdmin debe cambiar de empresa con `/auth/switch-tenant`). Se corrigió además un bug preexistente: nombre de archivo PDF con acentos rompía la cabecera HTTP; ahora se normaliza a ASCII.
* **Respuesta aditiva** (sin romper clientes): `period_label`, `interpretation` («Empresa · Top N por métrica · período · filtros»), `filters_applied` y `suggested_followups`. El prompt de Gemini recibe la interpretación literal; el fallback determinista para `ventas` nombra el producto líder, unidades e ingresos. La interpretación también aparece en el PDF/Excel mediante `period_label`/`interpretation` opcionales en `report_generator.py`.

### Web Angular y Móvil Flutter
* `quickPrompts` / `_quickPrompts` con 6 chips (top 10, top 5 por ingresos, compras, envíos, stock, auditoría). Badge «Consulta interpretada» con la interpretación y chips de seguimiento; en móvil, `ActionChip` llama al `submitQuery` existente.
* Modelos actualizados de forma opcional/retrocompatible: `ai-report.model.ts` y `ai_report_model.dart` (`periodLabel`, `interpretation`, `filtersApplied`, `suggestedFollowups`).

### Verificación
* `tests/test_ai_voice_query_customization.py` (7 pruebas): parser trimestre/top 10, ingresos + estado + 6 meses, tope 999→50 e historial, ranking ordenado, aislamiento de ranking por ingresos, bitácora por tenant y descarga ajena 404.
* **Suite completa: 198 passed, 0 failed, 0 errors** (191 + 7). `npm run build` OK (solo warnings de presupuesto CSS preexistentes). `flutter analyze` → **No issues found**. ADR-010 registrado.

### Archivos nuevos / modificados
`app/services/ai/voice_query_parser.py` (nuevo), `app/services/ai/voice_query_engine.py`, `app/services/ai/report_generator.py`, `app/packages/p4_trazabilidad/controllers/cu022_ia/ai_report_controller.py`, `app/packages/p4_trazabilidad/views/cu022_ia/ai_schemas.py`, `tests/test_ai_voice_query_customization.py` (nuevo), `frontend/src/app/{models/ai-report.model.ts,controllers/pages/dashboard.controller.ts,views/pages/dashboard.view.html}`, `mobile/lib/{models/ai_report_model.dart,views/widgets/voice_assistant_sheet.dart}`, `docs/{DECISION_LOG.md,ai/*.md}`.

---

## 0-quinquies. Sesión inmediatamente anterior (2026-11-20): Panel Integral por tenant con 36 meses

**Petición:** «en el dashboard de cada tenant me pide lo siguiente: tiene que dar todos los reportes consultas totalmente. Debe tener datos estadisticos de 3 años. Diseña esto para hacerlo bien por favor.»

### Backend (P7 / CU-035, extensión sin romper contratos)
* **Nuevo endpoint** `GET /api/v1/reports/analytics?meses=36&idtenant=2` — agregado analítico por tenant, `1 ≤ meses ≤ 36` (default 36), RBAC `requires_reportes` (5 roles), `Depends(resolve_analytics_tenant)` con bypass SuperAdmin (ADR-001/005) y Bitácora del middleware.
* **11 series mensuales** con los 36 puntos siempre presentes (`0` en meses sin datos, nunca omitidos): unidades, ventas, ingresos, pagos, eventos, eventos anclados, alertas, consultas QR, facturado, cobrado y reportes generados.
* **10 KPIs** con variación vs. 12 meses anteriores y base textual; 10 distribuciones, ranking de productos/eventos y bloques comercial, alertas, logística, facturación, actividad y suscripción.
* Archivos nuevos: `app/packages/p7_reportes/controllers/cu035_reportes/report_analytics_service.py`, `app/packages/p7_reportes/views/cu035_reportes/report_analytics_views.py`; endpoint en `report_controller.py`. **No se modificaron** `/reports/summary`, `/reports/traceability`, `/reports/pdf` ni `/dashboard`.
* Tests nuevos: `tests/test_dashboard_integral_36m.py` (3 pruebas: 36 puntos/secciones, rango+rol+400, aislamiento+bypass 404). Suite: **191 passed**.

### Histórico real de 36 meses (BD local `Blockchain`)
* `seed_historical_36m.py` (envoltorio de `seed_historical_6m.py` con `MESES=36` y manifest propio, sin duplicar 800 líneas).
* El manifest 36m se siembra desde el 6m, por lo que `--reset-history` cubre **17.335 IDs** (2.894 + 14.441 nuevas filas).
* Rango generado: **`2023-12` → `2026-11`** (36 meses). Verificado tenant 2: 513 unidades, 142 ventas, 202.137,00 USD, 36/36 meses con datos.
* `--dry-run` tras la carga → **0 filas nuevas** (idempotente).

### Web Angular
* `models/analytics.model.ts`, `controllers/services/analytics.service.ts`, `controllers/pages/analytics-panel.controller.ts`, `views/pages/analytics-panel.view.{html,css}`.
* Panel único de **8 pestañas** (Resumen, Tendencias 36 meses, Trazabilidad, Comercial, Alertas, Logística, Facturación, Actividad) integrado en `/dashboard` y reutilizado en `/reports`.
* Gráfico SVG inline sin librería nueva; franja de cadencia de 36 celdas; superficies planas, `tabular-nums`, tabs con scroll horizontal en móvil.
* Correcciones de QA visual: `formatoFecha` respeta `YYYY-MM` sin desplazamiento de zona horaria; `.dashboard-nav` apilado ≤768 px para eliminar overflow horizontal a 390 px (verificado 390=390).

### Móvil Flutter
* `models/analytics_model.dart`, `controllers/analytics_service.dart`, `controllers/analytics_controller.dart`, `views/analytics_view.dart`, getter `reportsAnalytics` en `api_config.dart`.
* Tarjeta «Panel Integral (CU-035)» en `dashboard_view.dart` con 3 KPIs y acceso a la pantalla, oculta para `Consumidor`; `user_model.dart` acepta `roles`.
* `flutter analyze` → **No issues found**.

### ADR
* **ADR-009**: agregado analítico P7 + manifest 36 meses (ver `docs/DECISION_LOG.md`).

---

## 1. ¿Qué se completó en la sesión anterior (2026-11-19)?

1. **Paquete P8 (ADR-008):**
   * Creado físicamente `app/packages/p8_suscripciones/` y registrado como **8º router** en `app/main.py`.
   * CU-036 y CU-037 migrados desde P1, conservando shims retrocompatibles (incluido el import usado por `tests/test_subscriptions_cu036_cu037.py`).
   * ADR-006 parcialmente supersedido y corregido: el control de límites duros corresponde a **CU-038**, no a CU-040.
   * Migración Alembic aplicada: tablas `usoplan`, `factura`, `facturadetalle`, `cobro` y unicidades en `ventaunidad`, `devolucionunidad`, `garantiaunidad` (`f1a2b3c4d5e6`).

2. **Backend Sprint 4 (P5, P7, P8 y CU-005):**
   * **CU-025/026/027/028/029/030/031:** ventas, asignación de unidades, pagos, historial del consumidor, devoluciones y garantías under `/api/v1/sales`, `/payments`, `/consumer`, `/returns`, `/warranties`.
   * **CU-035:** `/reports/summary`, `/reports/traceability`, `/reports/pdf` y `/dashboard`.
   * **CU-038:** `/quotas` y `/quotas/consume` con límite duro y respuesta `429`.
   * **CU-039:** `/invoices`, `/invoices/{id}/charges` y `/billing/history`.
   * **CU-040:** `/billing/notifications` y `/billing/notifications/process`.
   * **CU-005:** cerrada la brecha de push con `POST /api/v1/notifications/push` y `PushGateway` (in-app + proveedores FCM/APNs registrables).
   * **Aislamiento CU-040 reforzado:** `POST /billing/notifications/process` ahora inyecta `resolve_tenant_id` y filtra suscripciones/facturas por empresa (ADR-001); el modo global queda reservado al scheduler que invoca `BillingNotifier.procesar_programadas` sin `idtenant`. Nuevo test `test_procesar_notificaciones_aisla_tenant`.
   * Seams creados: `UnitAvailabilityService`, `SalesNotarizationService` (best-effort), `PushGateway`.
   * Correcciones: `to_char` para la serie temporal de reportes (psycopg 3) y normalización `Decimal` a 2 decimales en el saldo de facturación.

3. **Pruebas:**
   * `tests/test_sprint4_comercial_cu025_a_cu031.py` → 11 pruebas (200/201, 403, aislamiento multi-tenant).
   * `tests/test_sprint4_reportes_y_suscripciones.py` → 7 pruebas (reportes/PDF/dashboard, cuotas 429, facturación y cobros, factura ajena 404, notificaciones y push, aislamiento de notificaciones por tenant).
   * Suite completa: **188 passed, 0 failed, 0 errors**.

4. **Frontend Web (Angular 21):**
   * Servicios: `sales.service.ts`, `after-sales.service.ts`, `reporting.service.ts`, `quotas.service.ts`, `billing.service.ts`.
   * Modelos: `models/sprint4.model.ts`.
   * Pantallas: `/sales` (CU-025/026/027/028), `/post-sales` (CU-029/030/031), `/reports` (CU-035), `/quotas` (CU-038), `/billing` (CU-039/040 + push CU-005), todas con `authGuard` + `roleGuard` y enlaces en el dashboard.
   * `npm run build` exitoso; se amplió el presupuesto inicial de 1 MB a 2 MB en `angular.json` por el crecimiento del bundle.

5. **Aplicación Móvil (Flutter):**
   * CU-028: modelo, servicio, controlador y vista `consumer_history_view.dart` con acceso a trazabilidad y certificado por unidad.
   * CU-040: modelo, servicio, controlador y vista `billing_notifications_view.dart`.
   * Getters `consumerHistory` y `billingNotifications` en `api_config.dart`; dos tarjetas nuevas en `dashboard_view.dart`.
   * `flutter analyze` → **No issues found**.

6. **Poblado histórico de 6 meses (BD local `Blockchain`):**
   * Creado `trazabilidad/backend/seed_historical_6m.py`: **2.894 filas nuevas** para los 5 tenants en `2026-06` → `2026-11`.
   * Distribución: 360 unidades con QR y consulta, 120 eventos con condición/anclaje blockchain simulado, 120 ventas/pagos, 30 facturas/cobros, 90 alertas, 10 reportes de sospecha, 30 bitácoras y 30 notificaciones.
   * Re-ejecución verificada: `--dry-run` posterior reportó **0 filas nuevas** (idempotente por clave natural).
   * Manifest `seed_historical_6m.manifest.json` permite `--reset-history` sin afectar datos del seed canónico.
   * Suite completa tras la carga: **188 passed, 0 failed, 0 errors**.

---

## 2. Archivos Afectados / Creados (resumen)

* `trazabilidad/backend/app/main.py`
* `trazabilidad/backend/app/packages/p5_comercial/**` (CU-025 a CU-031)
* `trazabilidad/backend/app/packages/p7_reportes/**` (CU-035)
* `trazabilidad/backend/app/packages/p8_suscripciones/**` (CU-036 a CU-040)
* `trazabilidad/backend/app/packages/p1_seguridad/controllers/cu005_bitacora/bitacora_controller.py`
* `trazabilidad/backend/app/services/{unit_availability,sales_notarization,push_gateway}.py`
* `trazabilidad/backend/alembic/versions/f1a2b3c4d5e6_tablas_sprint4_facturacion_cuotas.py`
* `trazabilidad/backend/tests/test_sprint4_comercial_cu025_a_cu031.py`
* `trazabilidad/backend/tests/test_sprint4_reportes_y_suscripciones.py`
* `trazabilidad/backend/seed_historical_6m.py` (nuevo)
* `trazabilidad/backend/seed_historical_6m.manifest.json` (generado)
* `trazabilidad/frontend/src/app/app.routes.ts`
* `trazabilidad/frontend/src/app/models/sprint4.model.ts`
* `trazabilidad/frontend/src/app/controllers/services/{sales,after-sales,reporting,quotas,billing}.service.ts`
* `trazabilidad/frontend/src/app/controllers/pages/{sales,after-sales,reporting,quotas,billing}-*.controller.ts`
* `trazabilidad/frontend/src/app/views/pages/{sales,after-sales,reporting,quotas,billing}-*.view.html`
* `trazabilidad/frontend/src/app/views/pages/sales-management.view.css` (estilo compartido Sprint 4)
* `trazabilidad/frontend/angular.json`
* `trazabilidad/mobile/lib/core/api_config.dart`
* `trazabilidad/mobile/lib/controllers/{consumer_history,billing_notification}_{service,controller}.dart`
* `trazabilidad/mobile/lib/models/{consumer_history,billing_notification}_model.dart`
* `trazabilidad/mobile/lib/views/{consumer_history,billing_notifications}_view.dart`
* `trazabilidad/mobile/lib/views/dashboard_view.dart`
* `docs/DECISION_LOG.md` (ADR-006 corregido + ADR-008)
* `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_PHASES.md`
* `docs/ai/{CURRENT_STATE,HANDOFF_LATEST,NEXT_STEPS}.md`

---

## 3. Verificación y Credenciales de Prueba

* Backend: `cd trazabilidad/backend && python -m pytest tests/ -q` → **191 passed, 0 failed, 0 errors**.
* Web: `cd trazabilidad/frontend && npm run build` → OK (1,04 MB / 195,64 kB transfer; solo warnings de presupuesto CSS preexistentes).
* Móvil: `cd trazabilidad/mobile && flutter analyze` → No issues found.
* QA visual (browser-automation, 1440 y 390): 8 pestañas, 2 paths SVG y 36 celdas de cadencia en Tendencias, sin overflow horizontal (390=390).

### Smoke test real (servidor local + credenciales entregadas)
* Login `empresa-demo / admin@trazabilidad.com / Admin123!` → OK, roles `SuperAdministrador, AdministradorEmpresa`.
* 200 OK: `/sales`, `/payments`, `/returns`, `/warranties`, `/reports/summary`, `/reports/traceability`, `/dashboard`, `/quotas`, `/invoices`, `/billing/history`, `/billing/notifications`.
* `/reports/pdf` → 200, `application/pdf`, 2039 bytes (contenido `%PDF-1.3`).
* `/consumer/history` → 200 con datos demo creados (venta `idventa=45`, `idcliente=1839`, `total=1200.00`, 1 unidad). Sin `?idcliente` devuelve 404 si el correo del administrador no tiene perfil de consumidor; usar el cliente demo indicado.

### Verificación del historico (BD local)
* `python seed_historical_6m.py --dry-run` → 2.894 filas nuevas; segunda ejecución → 0 nuevas.
* Series `/api/v1/reports/traceability` → 6 puntos (`2026-06` … `2026-11`) para el tenant demo.
* `/api/v1/reports/summary` → 158 unidades, ingresos 35.364,00 USD; `/reports/pdf` → 200 `application/pdf`.
* Conteos por tenant: 72 unidades y 24 eventos vinculados en cada empresa (1…5).

### Credenciales demo (verificadas contra la BD actual)
| Uso | `tenant_slug` | Email | Password | Rol |
| :--- | :--- | :--- | :--- | :--- |
| Revisar **todos** los CUs (recomendado) | `empresa-demo` (o `1`) | `admin@trazabilidad.com` | `Admin123!` | SuperAdministrador |
| Admin de empresa (otro tenant) | `2` | `admin@techimport.com` | `Admin123!` | AdministradorEmpresa |
| Otros tenants | `3`, `4`, `5` | `admin@andinadigital.com`, `admin@electrosur.com`, `admin@cochawireless.com` | `Admin123!` | AdministradorEmpresa |

> El `tenant_slug` también acepta el ID numérico, el NIT o el slug del nombre de la empresa.  
> Los usuarios operativos del seed (`operaciones@…`, `ventas@…`, `auditor@…`) **no están presentes en la BD actual**; si se requieren para probar RBAC específico, ejecutar `python seed.py`. Las cuentas admin anteriores tienen acceso a todos los endpoints Sprint 4 (SuperAdmin por bypass ADR-005; AdminEmpresa por roles explícitos).

---

## 4. Servidores

* Backend FastAPI: `http://localhost:8000` (`/docs`).
* Frontend Angular: `http://localhost:4200` (`npm start`).
* Móvil Flutter: `flutter run` (configurar URL del servidor en la pantalla de login; hosts soportados en `ApiConfig`).

---

## 5. Despliegue y datos en la nube (pendiente)

El historico se cargo **solo en la BD local `Blockchain`**. Subir el codigo a Git/Railway **no traslada los datos**: la BD de Railway es otra instancia y el `Dockerfile` no ejecuta seeds en el arranque.

Cuando se tenga acceso al entorno remoto, ejecutar en Railway Shell (con `DATABASE_URL` de produccion inyectado):

```bash
python seed.py                     # solo si la BD remota no tiene tenants/catalogo base
python seed_historical_36m.py --dry-run
python seed_historical_36m.py
```

El script es determinista, por lo que genera los mismos 36 meses (`2023-12` → `2026-11`) en cualquier BD que tenga el seed base, incluido el bloque `HSALE` (manifest final local: **41.838 IDs**). El frontend en Vercel consume la API desplegada y no requiere cambios. No usar `--reset-history` en la primera ejecucion remota; sólo se usó en local para regenerar el historial con el nuevo orden de productos (`HSALE`).

> Nota: persiste un 403 preexistente en `GET /api/v1/planes?solo_activos=true` que el dashboard llama al iniciar (controlador P8 no modificado en esta sesión). No afecta al Panel Integral ni a la navegación.
