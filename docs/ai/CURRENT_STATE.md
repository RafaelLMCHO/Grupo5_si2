# Estado Actual del Sistema (Current State)

> **Documento:** Snapshot Técnico y Contexto Operativo para Agentes de IA  
> **Ubicación:** `docs/ai/CURRENT_STATE.md`  
> **Última Actualización:** 2026-11-24 (Implementación y Despliegue de Prioridad 0: Seguridad, Aislamiento Multi-Tenant y RBAC; 32 tests de seguridad y aislamiento 100% verdes contra Supabase; Frontend en Vercel [`https://grupo5-trazabilidad.vercel.app`]; Backend en Railway [`https://sprint4-production.up.railway.app`])  
> **Branch Principal:** `Rafael` (Repositorio `https://github.com/RafaelLMCHO/Grupo5_si2.git`)

---

## 1. Resumen Ejecutivo de la Base de Código

* **Estado de la Suite de Pruebas:** **32 PASSED | 0 FAILED | 0 ERRORS** verificados específicamente en los módulos de seguridad, usuarios, roles, RBAC y documentos contra Supabase Cloud (`test_audit.py`, `test_users.py`, `test_roles.py`, `test_rbac.py`, `test_documents_cu032.py`).
* **Base de Datos:** PostgreSQL en Supabase Cloud (`aws-0-us-west-2.pooler.supabase.com`) con 38,386 filas migradas y operando en Railway `sprint#4`.
* **Empaquetado Modular (ADR-003 + ADR-008):**
  * **P1** `app/packages/p1_seguridad/` — CU-001 a CU-005 (Filtro multi-tenant estricto en `/bitacora` y `/notifications`, columnas Usuario y Empresa; Aislamiento estricto en `/users` y `/roles`, exclusión de usuarios de otros tenants y SuperAdmin para administradores locales, prevención de escalada de privilegios y protección de filas sensibles).
  * **P2** `app/packages/p2_catalogo/` — CU-006 a CU-012.
  * **P3** `app/packages/p3_actores/` — CU-013, CU-014.
  * **P4** `app/packages/p4_trazabilidad/` — CU-015 a CU-024 (Rol `Auditor` con lectura de solo consulta habilitada en `/units`, `/qr/units` y `/shipments`).
  * **P5** `app/packages/p5_comercial/` — CU-025 a CU-032 (`/documents` protegido: mutación reservada a `SuperAdministrador`, `AdministradorEmpresa` y `GestorOperaciones`; `Auditor` y `GestorVentasPostventa` con solo lectura).
  * **P6** `app/packages/p6_blockchain/` — CU-033, CU-034.
  * **P7** `app/packages/p7_reportes/` — CU-035.
  * **P8** `app/packages/p8_suscripciones/` — CU-036 a CU-040.
* **Consolidación en `main.py`:** exactamente **8 inclusiones canónicas** de paquete con prefijo `/api/v1` (~174 rutas registradas).
* **Sprints Completados:** S0, S1, S2, S3 y S4 (backend + web + móvil de los CUs del sprint).
* **UI Web (Angular 21):** compila con `npm run build` (styles y plantillas sin errores).
* **UI Móvil (Flutter):** `flutter analyze` → **No issues found**.

---

## 2. Mapa de Cobertura de Casos de Uso (Backend)

| CU | Nombre del Caso de Uso | Paquete | Contrato principal | Estado |
| :--- | :--- | :---: | :--- | :---: |
| **CU-001 a CU-004** | Tenants, Usuarios, RBAC, Autenticación | P1 | `/tenants`, `/users`, `/roles`, `/auth` | Implementado / Probado |
| **CU-005** | Bitácora, notificaciones y push | P1 | `/bitacora`, `/notifications`, `/notifications/push` | Implementado / Probado |
| **CU-006 a CU-012** | Catálogo, compras y recepciones | P2 | `/products`, `/purchases`, `/receptions` | Implementado / Probado |
| **CU-013, CU-014** | Actores y ubicaciones | P3 | `/actors`, `/locations` | Implementado / Probado |
| **CU-015 a CU-024** | Unidades, QR, envíos, eventos, IA, sospechas y alertas (CU-022: ranking ventas/períodos/top N, ficha detallada 36m y Comparativa Multi-Empresa para SuperAdmin en Web) | P4 | `/units`, `/qr`, `/shipments`, `/alerts`, `/ai/voice-report`, `/ai/reports/{id}/export` | Implementado / Probado |
| **CU-025, CU-026** | Ventas y asignación de unidades | P5 | `/sales`, `/sales/{id}/units` | Implementado / Probado |
| **CU-027** | Pagos de venta (Checkout Stripe, estado y reembolso) | P5 | `/payments`, `/payments/checkout`, `/payments/{id}/checkout`, `/payments/{id}/refund`, `/payments/webhook` | Implementado / Probado |
| **CU-028** | Historial del consumidor | P5 | `/consumer/history` | Implementado / Probado (Web + Móvil) |
| **CU-029, CU-030** | Devoluciones y sus unidades | P5 | `/returns` | Implementado / Probado |
| **CU-031** | Garantías | P5 | `/warranties` | Implementado / Probado |
| **CU-032** | Documentos de unidad | P5 | `/documents` | Implementado |
| **CU-033, CU-034** | Blockchain y certificados | P6 | `/blockchain`, `/certificates` | Implementado |
| **CU-035** | Reportes, dashboard y Panel Integral 36 meses | P7 | `/reports/summary`, `/reports/traceability`, `/reports/pdf`, `/dashboard`, `/reports/analytics` | Implementado / Probado (Web + Móvil) |
| **CU-036, CU-037** | Planes y suscripciones | P8 | `/planes`, `/suscripciones` | Implementado / Probado |
| **CU-038** | Cuotas del plan | P8 | `/quotas`, `/quotas/consume` | Implementado / Probado |
| **CU-039** | Facturación y cobros (Checkout Stripe + activación de suscripción) | P8 | `/invoices`, `/invoices/{id}/checkout`, `/billing/history` | Implementado / Probado |
| **CU-040** | Notificaciones de facturación | P8 | `/billing/notifications`, `/billing/notifications/process` | Implementado / Probado (Web + Móvil) |

---

## 3. Estado de la Infraestructura y Configuración

1. **Variables de Entorno Clave (`.env`):**
   * `DATABASE_URL`: PostgreSQL (ej. `postgresql+psycopg://postgres:rafa@localhost:5432/Blockchain`).
   * `JWT_SECRET` / `JWT_ALGORITHM`: firma HS256 para tokens de sesión.
   * `BLOCKCHAIN_PROVIDER_URL`, `SMART_CONTRACT_ADDRESS`: RPC y contrato de notarización.
   * `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`, `STRIPE_WEBHOOK_TOLERANCE_SECONDS`: pasarela de pago único (ADR-013). LLaves reales sólo en `.env`; placeholders en `.env.example`. Falta el `whsec_...` definitivo.
2. **Seguridad y RBAC:**
   * Todo endpoint sensible usa `require_roles(...)`, con bypass de `SuperAdministrador` según ADR-005.
   * Todo endpoint de lectura/mutación aplica `resolve_tenant_id` (o filtra por unidad/venta del tenant en tablas hijas), incluido `POST /billing/notifications/process` (CU-040, corregido en el cierre de Sprint 4).
3. **Servicios transversales nuevos:**
   * `UnitAvailabilityService`: valida disponibilidad de unidades antes de asignarlas a ventas/devoluciones.
   * `SalesNotarizationService`: notarización best-effort de ventas (si falla Blockchain, la venta no se revierte).
   * `PushGateway`: notificaciones in-app con proveedores externos registrables (FCM/APNs).
    * `StripeGateway` + `stripe_webhook.procesar_evento`: Checkout de pago único, verificación de firma, reembolso e idempotencia por `stripeevento` (ADR-013). Los eventos `checkout.session.completed` confirman venta o factura; la factura pagada activa la suscripción y todo se audita en Bitácora.
4. **Servicio transversal del asistente (ADR-010, ADR-011):** `VoiceQueryParser` es determinista y no añade dependencias; calcula períodos en hora Bolivia y el fallback de Gemini funciona sin API key. `POST /ai/voice-report` es aditivo (`period_label`, `interpretation`, `filters_applied`, `suggested_followups`) y, cuando se detecta un producto o la frase «analisis detallado/ficha de…», añade `product_detail` con rango fijo de 36 meses y métricas filtradas por tenant. La exportación desde `REPORT_CACHE` exige JWT y valida el `tenant_id` activo (404 si no coincide), con nombre de archivo ASCII; PDF/Excel incluyen la sección de ficha.
5. **Mantenibilidad:**
   * `app/main.py` registra exclusivamente las 8 fachadas de paquete.
   * Los contratos REST históricos y los imports previos se preservan mediante shims.

---

## 4. Datos históricos de demostración (3 años / 36 meses)

* Script activo: `trazabilidad/backend/seed_historical_36m.py` (envoltorio de `seed_historical_6m.py`, `MESES=36`) con `--dry-run`, `--reset-history` y manifest `seed_historical_36m.manifest.json` (**41.838 IDs**; siembra los IDs del manifest 6m).
* Periodos generados: **`2023-12` a `2026-11`** (36 meses, relativos a `get_bolivia_now()`), para los tenants 1 a 5.
* Volumen total cargado: **41.838 filas** en el manifest (histórico `HIST` + bloque suplementario `HSALE`). El bloque `HSALE` añade señal comercial a hasta 10 productos reales distintos por tenant en los 36 meses: 4.566 unidades (vendidas/disponibles), 3.420 QR + consultas, 1.980 ventas/detalles/pagos/eventos con condición y anclaje, 1.800 alertas, 2.340 garantías, 1.140 reportes de sospecha con evidencia, 450 devoluciones (incluye los 3 productos base) y 750 documentos. Por tenant hay 10 productos con ventas en el último trimestre y 36/36 meses con datos.
* Idempotencia demostrada: tras la carga, `--dry-run` y una segunda ejecución real insertan **0 filas**. `--reset-history` + re-ejecución regeneran el historial completo sin tocar datos operacionales.
* **Verificación del asistente (2026-11-22):** `top 10 productos mas vendidos en el ultimo trimestre` devuelve **10 filas en los 5 tenants** (`2026-09 → 2026-12`) con nombres reales (iPhone, AirPods, Galaxy, Smartwatch, Cargador). Las 50 fichas resultantes (`product_detail`, 36 meses) tienen **todas sus métricas > 0**; ninguna queda en cero. ADR-012.
* `/api/v1/reports/analytics?meses=36` devuelve 11 series con 36 puntos cada una; 36/36 meses con datos reales. `/api/v1/reports/traceability` sigue devolviendo sus 6 puntos originales (contrato intacto).
* Los datos estan **solo en la BD local**; para la nube (Railway) hay que ejecutar `seed_historical_36m.py` alli (ver `HANDOFF_LATEST.md`, sección 5).
