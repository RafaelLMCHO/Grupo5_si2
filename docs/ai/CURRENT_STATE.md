# Estado Actual del Sistema (Current State)

> **Documento:** Snapshot Técnico y Contexto Operativo para Agentes de IA  
> **Ubicación:** `docs/ai/CURRENT_STATE.md`  
> **Última Actualización:** 2026-10-27 (Sprint 2 Auditado / Inicio de Sprint 3)  
> **Branch Principal:** `main` (o rama de desarrollo activa)  

---

## 1. Resumen Ejecutivo de la Base de Código

* **Estado de la Suite de Pruebas:** **120 PASSED | 0 FAILED | 0 ERRORS** (100% verde).
* **Base de Datos de Pruebas:** PostgreSQL 15+ en base de datos dedicada `blacktest`.
* **Sprints Completados y Auditados:**
  * **Sprint 0:** Arquitectura, Multi-Tenant, Usuarios, Roles y Permisos (CU-001, CU-002, CU-003).
  * **Sprint 1:** Autenticación JWT, Catálogo de Productos Apple, Categorías, Certificaciones, Actores de Cadena y Ubicaciones (CU-004, CU-006 a CU-009, CU-013, CU-014).
  * **Sprint 2:** Órdenes de Compra, Flujo de Aprobación, Recepción de Mercancía, Registro de Unidades (Serial/IMEI/EID), Códigos QR, Envíos Logísticos y Condiciones de Transporte (CU-010 a CU-012, CU-015, CU-016, CU-019 a CU-021).
* **Sprint Activo / En Foco:** **Sprint 3 (Trazabilidad Digital, Blockchain y Autenticidad)**.

---

## 2. Mapa de Cobertura de Casos de Uso (Backend)

| CU | Nombre del Caso de Uso | Paquete | Controlador en `app/controllers/` | Estado |
| :--- | :--- | :---: | :--- | :---: |
| **CU-001** | Gestionar Tenants | P1 | `cu001_tenants/tenant_controller.py` | Implementado / Probado |
| **CU-002** | Gestionar Usuarios | P1 | `cu002_usuarios/user_controller.py` | Implementado / Probado |
| **CU-003** | Roles y Permisos (RBAC) | P1 | `cu003_roles_permisos/role_controller.py` | Implementado / Probado |
| **CU-004** | Autenticación y Refresh JWT | P1 | `cu004_autenticacion/auth_controller.py` | Implementado / Probado |
| **CU-005** | Bitácora y Auditoría | P1 | `cu005_bitacora/bitacora_controller.py` | Implementado (Middleware) |
| **CU-006** | Productos y Variantes Apple | P2 | `cu006_productos_variantes/product_controller.py` | Implementado / Probado |
| **CU-007** | Certificaciones Técnicas | P2 | `cu007_certificaciones/certification_controller.py` | Implementado / Probado |
| **CU-008** | Catálogo por Empresa | P2 | `cu008_catalogo_empresa/tenant_catalog_controller.py` | Implementado / Probado |
| **CU-009** | Categorías de Producto | P2 | `cu009_categorias/category_controller.py` | Implementado / Probado |
| **CU-010** | Órdenes de Compra | P2 | `cu010_ordenes_compra/purchase_controller.py` | Implementado / Probado |
| **CU-011** | Aprobación/Rechazo Compra | P2 | `cu011_compras/purchase_approval_controller.py` | Implementado / Probado |
| **CU-012** | Recepciones de Mercancía | P2 | `cu012_recepciones/reception_controller.py` | Implementado / Probado |
| **CU-013** | Actores de la Cadena | P3 | `cu013_actores_cadena/actor_controller.py` | Implementado / Probado |
| **CU-014** | Ubicaciones Físicas | P3 | `cu014_ubicaciones/location_controller.py` | Implementado / Probado |
| **CU-015** | Unidades (Serial/IMEI/EID) | P4 | `cu015_unidades_producto/unit_controller.py` | Implementado / Probado |
| **CU-016** | Códigos QR y Trazabilidad Pública | P4 | `cu016_codigos_qr/qr_controller.py` | Implementado / Probado |
| **CU-019** | Envíos Logísticos | P4 | `cu019_envios_logisticos/shipment_controller.py` | Implementado / Probado |
| **CU-020** | Asignación Unidades a Envío | P4 | `cu020_asignacion_unidades_envio/shipment_unit_controller.py` | Implementado / Probado |
| **CU-021** | Eventos y Condiciones de Transporte | P4 | `cu021_eventos_transporte/transport_event_controller.py` | Implementado / Probado |
| **CU-022** | Análisis IA de Trazabilidad | P4 | `cu022_ia/ai_report_controller.py` | Prototipo inicial |
| **CU-023** | Reporte de Sospecha Falsificación | P4 | `cu023_reporte_sospecha/suspicion_controller.py` | Implementado |
| **CU-024** | Alertas e Incidencias | P4 | `cu024_alertas/alert_controller.py` | Implementado |
| **CU-032** | Documentos Adjuntos a Unidades | P5 | `cu032_documentos_unidad/document_controller.py` | Implementado |
| **CU-033** | Controlador Blockchain | P6 | `cu033_blockchain/blockchain_controller.py` | Estructurado / Por conectar |
| **CU-034** | Certificados Digitales | P6 | `cu034_certificados/certificate_controller.py` | Estructurado |

---

## 3. Estado de la Infraestructura y Configuración

1. **Variables de Entorno Clave (`.env`):**
   * `DATABASE_URL`: Conexión PostgreSQL (ej. `postgresql://usuario:pass@localhost:5432/blacktest`).
   * `JWT_SECRET` / `JWT_ALGORITHM`: Firma simétrica HS256 para tokens de sesión.
   * `BLOCKCHAIN_PROVIDER_URL`: Endpoint RPC para Ethereum Sepolia/Amoy (Infura / Alchemy).
   * `SMART_CONTRACT_ADDRESS`: Dirección del contrato compilado de trazabilidad.
2. **Seguridad y RBAC:**
   * Validado en Sprint 2: todo endpoint de mutación (`POST`, `PUT`, `DELETE`) exige `require_roles(...)`.
   * El `Super Administrador` posee bypass total en `resolve_tenant_id` y en `require_roles`.
3. **Mantenibilidad Arquitectónica Pendiente:**
   * Actualmente `main.py` registra 26 routers individuales directamente.
   * Se requiere agrupar en 7 fachadas (`app/routers/p1_seguridad.py` a `p7_reportes.py`) para modularizar el backend sin romper rutas ni contratos.
