# Próximos Pasos Operativos (Next Steps - Agentes de IA)

> **Documento:** Checklist Táctico y Cola de Trabajo Inmediata para Agentes  
> **Ubicación:** `docs/ai/NEXT_STEPS.md`  
> **Metodología:** SCRUM · **Sprint Activo:** **Sprint 5 (Hardening, Seguridad y Robusteza Multi-Tenant)**  
> **Estado de Base de Código:** Sprints 0-4 implementados + **Sprint 5 (Prompts 1 al 9 + Segregación SuperAdmin ADR-016 + 3 Consultas Estratégicas de Voz CU-022) 100% COMPLETADO** · **251 tests verdes (0 fallos)** · FastAPI (:8000) y Angular (:4200) levantados en localhost · Angular build OK · Flutter analyze OK

---

## 1. Contexto Operativo Inmediato

Se ha completado en su totalidad la implementación y verificación de **Sprint 5**:
* **Prompt 1 (CU-003 - Hardening RBAC y Prevención de Escalada de Privilegios):** roles de gestión protegidos, prevención de escalada a SuperAdmin y verificación multi-tenant.
* **Prompt 2 (CU-001 - /tenants sin control de roles):** mutaciones restringidas a `SuperAdministrador`, `GET /tenants` filtrado a empresa activa para otros roles, `GET /tenants/{id}` protegido contra fuga entre empresas, y menú frontend limitado a `SuperAdministrador`.
* **Prompt 3 (CU-002 - /users sin control de roles y fuga entre empresas):** mutaciones restringidas a `SuperAdministrador` y `AdministradorEmpresa`, lecturas con Auditor, aislamiento multi-tenant con `404`, auto-protección (`400`) y protección a SuperAdmin (`403`).
* **Prompt 4 (CU-013, CU-014, CU-015, CU-016 - Aislamiento en cambio de empresa):** reemplazo de `get_user_tenant_id` por `resolve_tenant_id` en actores, ubicaciones, unidades y QR; validación de pertenencia 422 en unidades; combo frontend sincronizado.
* **Prompt 5 (CU-006, CU-007 - DELETE /products y /variants con guard y 409):** `ROLES_GESTION_PRODUCTO` reservado a `SuperAdministrador` (403 para GestorOperaciones y Admin de empresa), verificación de dependencias (unidades y compras) con respuesta `409 Conflict`, y verificación de certificaciones con retorno `409`.
* **Prompt 6 (Actores, Unidades, Categorías, Ubicaciones - Control de errores de integridad referencial 409):** captura de `IntegrityError` con rollback y retorno 409 en DELETE de actores, unidades, categorías, ubicaciones, catálogo de empresa y documentos de unidad.
* **Prompt 7 (Autenticación y Manejo de Errores - Rate Limiting en Login 429 y Ofuscación 500):** límite de 5 intentos fallidos consecutivos por combinación (email, IP) con bloqueo temporal de 15 minutos (429 Too Many Requests); registro del bloqueo en la tabla Bitácora (`CU-005`); reseteo de contador en login exitoso; y ofuscación de respuestas 500 para evitar fugas de información interna.
* **Prompt 8 (Configuración y Migraciones):** inclusión de `python-multipart==0.0.20` en `requirements.txt`; corrección en migración `f1a2b3c4d5e6` creando `plan` y `suscripcion` si no existen (verificado en base de datos vacía); fixtures automáticos e idempotentes para tests de suscripciones; y depuración del middleware de `Bitacora` para registrar únicamente operaciones de mutación (POST, PUT, PATCH, DELETE) y accesos críticos.
* **Prompt 9 (Verificación Integral de Seguridad con Usuarios Demo):** validación exhaustiva con las cuentas demo (`admin`, `operaciones`, `ventas`, `auditor` de Empresa 1 y `admin` de Empresa 2, contraseña `Admin123!`), verificando restricciones 403 en roles operativos, aislamiento total de Empresa 2, aislamiento multi-tenant con switch-tenant, protección 403 en catálogo y 409 en dependencias vinculadas.
* **Pruebas:** 61 pruebas específicas de seguridad y hardening en verde (`test_prompt9_security_verification.py`, `test_prompt8_config_migrations_audit.py`, `test_auth_rate_limit_and_500.py`, `test_integrity_409.py`, `test_products_security.py`, `test_switch_tenant_isolation.py`, `test_users.py`, `test_tenants.py`, `test_rbac.py`, `test_roles.py`) y suite global con **244 tests verdes (0 fallos)**.
* **Regla estricta aplicada:** NO se ha hecho commit ni push a Git.

### Resumen del Sprint 5:
- [x] **Prompt 1:** RBAC y jerarquía de roles (CU-003).
- [x] **Prompt 2:** Hardening y aislamiento en Tenants (CU-001).
- [x] **Prompt 3:** Hardening y aislamiento en Usuarios (CU-002).
- [x] **Prompt 4:** Aislamiento dinámico en Switch-Tenant (CU-013..CU-016).
- [x] **Prompt 5:** Protección de Catálogo y variantes (CU-006, CU-007).
- [x] **Prompt 6:** Integridad 409 en DELETE con dependientes.
- [x] **Prompt 7:** Rate limiting de Login 429 y ofuscación de errores 500.
- [x] **Prompt 8:** Dependencias, migraciones en BD limpia y depuración de Bitácora.
- [x] **Prompt 9:** Verificación integral de seguridad con usuarios demo (10 tests específicos + 244 tests globales).

* **P5 (CU-025 a CU-031):** ventas, asignación de unidades, pagos, historial del consumidor, devoluciones y garantías.
* **P7 (CU-035):** reportes, trazabilidad consolidada, PDF y dashboard.
* **P8 (CU-036 a CU-040):** planes/suscripciones migrados, cuotas con límite duro, facturación/cobros y notificaciones de facturación.
* **CU-005:** push implementado y conectado con la UI web.
* **Web:** 5 rutas nuevas (`/sales`, `/post-sales`, `/reports`, `/quotas`, `/billing`) con guardas RBAC y enlaces en el dashboard.
* **Móvil:** historial del consumidor y notificaciones de facturación integrados en el dashboard.

No quedan CUs pendientes del listado Sprint 4. Se agregó el **Panel Integral por tenant con 36 meses** (extensión de CU-035): `GET /reports/analytics`, panel de 8 pestañas en web y móvil, e histórico real `2023-12 → 2026-11`. También se personalizó el **Asistente de Informes Dinámicos por Voz** (CU-022): parser determinista con períodos/top N/métrica/filtros, ranking de ventas por tenant, chips sugeridos y badge de interpretación en web y móvil (ADR-010). Finalmente se añadió la **ficha detallada por producto** dentro del asistente (ADR-011): `product_detail` con rango fijo de 36 meses, métricas reales y exportación en PDF/Excel, con seed suplementario idempotente para los 5 tenants. La cola siguiente es de **verificación y cierre**, no de implementación funcional.

---

## 2. Checklist de Cierre (en orden)

- [x] Backend P5/P7/P8 y push CU-005 implementados.
- [x] Tests Sprint 4 creados y suite global en verde (188 → 191 con el Panel Integral).
- [x] Panel Integral 36 meses: endpoint `/reports/analytics`, 3 tests nuevos, series completas, panel web/móvil y seed 36m (17.335 filas, idempotente).
- [x] QA visual del panel a 1440 y 390 px: 8 pestañas, SVG + 36 celdas, sin overflow horizontal; corregido `formatoFecha` y nav responsive.
- [x] Migración Alembic aplicada y `alembic current` en head.
- [x] Angular: rutas, servicios, modelos, vistas y dashboard actualizados; `npm run build` OK.
- [x] Flutter: modelos, servicios, controladores, vistas y dashboard actualizados; `flutter analyze` OK.
- [x] ADR-008 redactado, ADR-006 corregido y documentación de 7→8 paquetes actualizada.
- [x] Aislamiento multi-tenant de `POST /billing/notifications/process` (CU-040) corregido y cubierto por test.
- [x] Asistente de informes (CU-022, ADR-010): parser + ranking ventas + fechas en todos los intentos + auditoría por tenant + 404 en exportación ajena; 7 tests nuevos (suite 198), chips y badge en web/móvil; build y analyze OK.
- [x] Ficha detallada de producto (CU-022, ADR-011): `product_detail` aditivo con 36 meses fijos, métricas filtradas por tenant, tarjeta web/móvil y sección PDF/Excel; seed suplementario idempotente (20.401 IDs, 0 filas en re-ejecución); 4 tests nuevos (suite 202); build y analyze OK.
- [x] Poblado completo del `top 10` (CU-022, ADR-012): bloque `HSALE` con hasta 10 productos reales distintos por tenant × 36 meses, devoluciones para los productos base, manifest 41.838 IDs, `--dry-run` con 0 filas nuevas, 10/10 filas en los 5 tenants y 50/50 fichas sin métricas en cero; 2 tests nuevos (suite 204); build y analyze OK.
- [x] **Stripe pago único (CU-027/CU-039, ADR-013):** gateway compartido, `POST /payments/checkout`, `GET /payments/{idpago}/checkout`, `POST /payments/{idpago}/refund`, `POST /invoices/{idfactura}/checkout` y webhook firmado/idempotente `POST /payments/webhook`; columnas aditivas en `pago`/`cobro` + tabla `stripeevento` (migración `c7d8e9f0a1b2` aplicada); activación de suscripción y Bitácora; 5 tests nuevos (suite **209**); build y analyze OK. Falta configurar `STRIPE_WEBHOOK_SECRET` real en `.env`.
- [x] Smoke test de endpoints con las credenciales demo (todos 200; `/reports/pdf` devuelve PDF; `/consumer/history` con `idcliente=1839`).
- [x] Poblado historico de 6 meses (`2026-06`→`2026-11`) en la BD local: 2.894 filas, idempotente, serie de 6 puntos en `/reports/traceability` y suite en verde (188).
- [ ] **Pendiente (sin acceso):** ejecutar `python seed_historical_36m.py` en Railway Shell con el `DATABASE_URL` de produccion (previamente `python seed.py` si la BD remota esta vacia). Los datos locales NO se suben con `git push`.
- [ ] **Verificación manual end-to-end con las credenciales demo** de `docs/ai/HANDOFF_LATEST.md`:
  * `/sales` → crear venta, asignar unidades, registrar pago y cambiar estados.
  * `/post-sales` → crear devolución, asignar unidades y registrar garantía.
  * `/reports` → resumen, trazabilidad, dashboard y descarga PDF.
  * `/quotas` → consultar y consumir hasta exceder (429).
  * `/billing` → crear factura, registrar cobro, procesar vencimientos y enviar push.
  * Móvil → tarjetas “Mis Compras (CU-028)” y “Notificaciones de Facturación (CU-040)”.
- [ ] Opcional: ajustar el presupuesto de `anyComponentStyle` en `angular.json` para eliminar warnings preexistentes de CSS.
- [x] Roles en `UserModel` de Flutter registrados: la tarjeta del Panel Integral se oculta a `Consumidor`.
- [ ] Opcional: corregir el 403 preexistente de `GET /planes?solo_activos=true` que el dashboard solicita al iniciar (parámetro no reconocido por `_requires_lectura_planes`).

---

## 3. Notas para el siguiente agente

* **No alterar** los prefijos `/api/v1/...` existentes; Angular y Flutter dependen de ellos.
* **Multi-tenant:** las tablas hijas (`pago`, `devolucionunidad`, `garantiaunidad`, `ventaunidad`, etc.) no tienen `idtenant`; filtrar siempre por join a `venta.idtenant` o `unidadproducto.idtenant`.
* **Notarización de ventas:** es best-effort; un fallo de Blockchain no debe revertir la venta.
* **ADR-006** queda parcialmente supersedido por **ADR-008**; no reintroducir planes/suscripciones en P1.
* Si se crean nuevos tests, ejecutar `cd trazabilidad/backend && python -m pytest tests/ -q` y mantener **≥209 passed, 0 failed, 0 errors**.
* Asistente (ADR-010, ADR-011, ADR-012): no alterar los campos nuevos de `VoiceReportResponse` (`period_label`, `interpretation`, `filters_applied`, `suggested_followups`, `product_detail`); son aditivos y los clientes móvil/web ya los consumen de forma opcional. El `top N` se acota a 50 y sin período se mantiene "todo el historico". La ficha detallada ignora el período de la consulta y usa siempre 36 meses; el producto se resuelve contra `CatalogoTenant` del tenant activo. `/ai/reports/{id}/export` exige JWT y valida empresa activa: el SuperAdmin debe cambiar de tenant antes de descargar un informe ajeno.
* `/reports/analytics` es el único agregado nuevo: no modificar los contratos existentes de P7. El rango `meses` está limitado a `1..36`; los 36 puntos se rellenan con `0` en meses sin datos (nunca se omiten).
* **Stripe (ADR-013):** no versionar llaves (`sk_test_...` y `whsec_...` sólo en `.env`); los endpoints de checkout son aditivos y los manuales quedan como fallback. El webhook **no lleva JWT**: confía en la firma y en el metadata `kind/tenant_id/id`, y vuelve a validar el padre por tenant. Un evento repetido es no-op por `stripeevento.eventoid`. Sin `STRIPE_WEBHOOK_SECRET` real, el webhook local devuelve 400/503. Para probar en local: `stripe listen --forward-to localhost:8000/api/v1/payments/webhook` y copiar el `whsec_` resultante. Pendiente para otra entrega: suscripciones recurrentes y QR de cobro (CU-041/CU-042); el QR de CU-016 es de trazabilidad.
