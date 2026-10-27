# Resumen del proyecto: Plataforma Web y Aplicación Móvil para la Trazabilidad de Dispositivos Apple mediante Tecnología Blockchain, desde el Origen hasta el Consumidor Final

**Equipo:** Grupo 5 · **Metodología:** SCRUM por Sprints (Sprint 0 al 4) con seguimiento en Jira

---

## 0. Ficha rápida

**Objetivo general:** desarrollar una plataforma web y aplicación móvil para la trazabilidad de dispositivos Apple importados (iPhone, MacBook, iPad y accesorios) mediante blockchain, desde la compra en EE.UU. hasta el consumidor final en Bolivia.

**Idea central:** cada unidad física se identifica de forma individual (número de serie, IMEI o EID) y recibe un código QR/NFC único. Sus eventos críticos (compra, despacho aduanero, movimientos, venta) se registran de forma inmutable en blockchain, y el consumidor puede consultar el historial completo y verificar la autenticidad.

**Arquitectura:** multi-tenant (varias empresas importadoras operan aisladas sobre la misma plataforma).

**Tecnologías**

| Componente | Tecnología |
| :--- | :--- |
| Backend / API REST | FastAPI (Python) |
| Frontend web | Angular (TypeScript) |
| App móvil | Flutter (Dart) |
| Base de datos | PostgreSQL |
| Blockchain | Ethereum (testnet Sepolia/Amoy), contratos en Solidity, integración con Web3.py |
| Nube | Google Cloud Platform, contenedores Docker |
| Control de versiones y gestión | Git/GitHub, Jira |

**Actores del sistema**

| Actor | Acceso | Descripción |
| :--- | :--- | :--- |
| Super Administrador | Con cuenta | Control total de la plataforma; único que crea y elimina empresas. |
| Administrador de Empresa | Con cuenta | Responsable de una empresa (tenant): catálogo, usuarios, aprobación de compras. |
| Gestor de Operaciones | Con cuenta | Abastecimiento, inventario, logística y trazabilidad de unidades. |
| Gestor de Ventas y Postventa | Con cuenta | Ventas, devoluciones, garantías y documentos. |
| Consumidor Registrado | Con cuenta | Consulta historial de trazabilidad, garantías, compras, favoritos. |
| Auditor / Inspector Externo | Con cuenta | Solo lectura: verifica cumplimiento normativo e integridad de la cadena. |
| Proveedor EE.UU., Transportista Internacional, Aduana | Sin cuenta | Participantes externos referenciados en los eventos. |
| Visitante Anónimo | Sin cuenta | Escanea un QR y consulta el historial público. |

**Alcance acotado:** el sistema expone la trazabilidad por API REST, **no** gestiona carrito ni pagos; las ventas se registran como eventos referenciales.

---

## 1. Resumen de los módulos (8)

| # | Módulo | Resumen | Funcionalidades principales |
| :--- | :--- | :--- | :--- |
| 5.1.1 | **Seguridad y multi-tenant** | Controla el acceso y administra las empresas, garantizando que cada usuario vea solo lo de su rol y empresa. | Login con JWT; recuperación de contraseña por correo; gestión de usuarios y roles; gestión de empresas; aislamiento de datos; bitácora de accesos y actividades. |
| 5.1.2 | **Catálogo y certificaciones** | Administra los productos Apple de cada empresa y las certificaciones que respaldan su autenticidad. | Productos y variantes; categorías; certificaciones (FCC, CE, RoHS, Energy Star, garantía); consulta pública del catálogo. |
| 5.1.3 | **Abastecimiento e importación** | Gestiona la compra a proveedores de EE.UU. y la recepción tras el despacho aduanero. | Órdenes de compra; aprobación/rechazo; recepción en almacén; estado de órdenes. |
| 5.1.4 | **Actores y ubicaciones** | Representa a los participantes externos y los lugares físicos sin que necesiten cuenta. | Proveedores, transportistas, aduanas; almacenes, puertos, oficinas aduaneras; asociación a eventos. |
| 5.1.5 | **Inventario y trazabilidad (núcleo)** | Identifica cada unidad y construye su historial completo. | Unidades por serial/IMEI/EID; QR/NFC; escaneo móvil; envíos y movimientos; condiciones de transporte (temperatura, humedad, vibración); incidencias; historial con mapa; verificación de autenticidad; reporte de sospecha; API REST con API key para e-commerce externo. |
| 5.1.6 | **Ventas** | Registra la venta como un evento más de la cadena, sin procesar pagos. | Evento de venta; asignación de unidad (serial/IMEI) a la venta; estado referencial; historial de ventas. |
| 5.1.7 | **Postventa** | Gestiona la relación con el consumidor tras la venta. | Devoluciones; garantías por serial; documentos adjuntos; consulta del consumidor; favoritos y notificaciones. |
| 5.1.8 | **Blockchain (registro inmutable)** | Registra de forma inmutable los eventos críticos. | Registro en blockchain con hash y timestamp; estado "pendiente" hasta confirmación; verificación de integridad; certificados digitales PDF; reportes e indicadores. |

---

## 2. Casos de uso: descripción breve y actor (35)

| ID | Caso de uso | Descripción breve | Actor(es) |
| :--- | :--- | :--- | :--- |
| CU-001 | Gestionar Empresas (Tenants) | Crear, configurar, suspender y eliminar empresas, con datos aislados entre sí. | Super Administrador |
| CU-002 | Gestionar Usuarios del Sistema | Crear, editar y desactivar cuentas de usuario dentro de una empresa. | Administrador de Empresa, Super Administrador |
| CU-003 | Asignar Roles y Permisos a Usuario | Asignar roles y permisos a los usuarios de la empresa. | Administrador de Empresa |
| CU-004 | Autenticar y Recuperar Contraseña | Iniciar/cerrar sesión con JWT y restablecer contraseña por correo. | Todos los usuarios con cuenta |
| CU-005 | Consultar Bitácora y Gestionar Notificaciones | Consultar la bitácora de auditoría y gestionar notificaciones. | Super Administrador, Auditor (bitácora); usuarios con cuenta (notificaciones) |
| CU-006 | Gestionar Productos y Variantes | Registrar, editar y desactivar productos y sus variantes (capacidad, color, SKU, precio). | Administrador de Empresa |
| CU-007 | Gestionar Certificaciones Técnicas | Crear certificaciones y asociarlas a productos. | Administrador de Empresa |
| CU-008 | Gestionar Catálogo por Empresa | Definir qué variantes vende cada empresa, con SKU interno, precio y costo. | Administrador de Empresa |
| CU-009 | Gestionar Categorías de Productos | Crear, editar y organizar categorías (smartphones, laptops, tablets, accesorios). | Super Administrador, Administrador de Empresa |
| CU-010 | Gestionar Órdenes de Compra | Registrar y consultar órdenes de compra a proveedores de EE.UU. con su detalle. | Gestor de Operaciones |
| CU-011 | Aprobar / Rechazar Compra | Aprobar o rechazar (con motivo) órdenes pendientes. | Administrador de Empresa |
| CU-012 | Gestionar Recepciones de Mercancía | Registrar la recepción física en Bolivia y actualizar existencias. | Gestor de Operaciones |
| CU-013 | Gestionar Actores de la Cadena | Administrar proveedores, transportistas, aduanas y demás actores. | Administrador de Empresa |
| CU-014 | Gestionar Ubicaciones Físicas | Administrar almacenes, puertos, aduanas y tiendas con georreferenciación. | Administrador de Empresa |
| CU-015 | Gestionar Unidades de Producto (Serial/IMEI) | Registrar cada dispositivo con serial, IMEI/EID, estado, custodio y ubicación. | Gestor de Operaciones |
| CU-016 | Generar y Descargar Código QR | Generar un QR único por unidad y permitir su descarga/impresión. | Gestor de Operaciones |
| CU-017 | Escanear Código QR | Leer el QR/NFC con la cámara para consultar el historial o registrar eventos. | Gestor de Operaciones, Consumidor Registrado, Visitante Anónimo |
| CU-018 | Registrar Consulta de Trazabilidad | Registrar automáticamente cada escaneo (fecha, IP, país aproximado). | Sistema (automático) |
| CU-019 | Gestionar Envíos Logísticos | Crear envíos entre ubicaciones y gestionar su ciclo de estados. | Gestor de Operaciones |
| CU-020 | Asignar / Desasignar Unidades a Envío | Asignar unidades específicas a un envío o retirarlas. | Gestor de Operaciones |
| CU-021 | Registrar Eventos y Condiciones de Transporte | Registrar hitos y condiciones (temperatura, humedad, vibración) de un envío. | Gestor de Operaciones |
| CU-022 | Consultar Historial y Verificar Autenticidad | Ver el historial cronológico de una unidad y confirmar que es original. | Consumidor Registrado, Visitante Anónimo, Auditor |
| CU-023 | Reportar Sospecha de Falsificación | Denunciar una unidad sospechosa con evidencia. | Consumidor Registrado, Visitante Anónimo |
| CU-024 | Gestionar Alertas e Incidencias | Visualizar, clasificar y resolver alertas generadas por el sistema. | Gestor de Operaciones, Administrador de Empresa |
| CU-025 | Gestionar Ventas | Registrar la venta de unidades al consumidor final. | Gestor de Ventas y Postventa |
| CU-026 | Asignar Unidades Físicas a Venta | Asociar cada serial/IMEI vendido a su línea de venta. | Gestor de Ventas y Postventa |
| CU-027 | Gestionar Pagos | Registrar el estado del pago de una venta (referencial, sin pasarela). | Gestor de Ventas y Postventa, Super Administrador |
| CU-028 | Consultar Historial de Compras del Consumidor | Ver compras, unidades adquiridas, favoritos y preferencias. | Consumidor Registrado |
| CU-029 | Gestionar Devoluciones | Registrar devoluciones con motivo y estado. | Gestor de Ventas y Postventa |
| CU-030 | Asignar Unidades a Devolución | Vincular las unidades concretas devueltas. | Gestor de Ventas y Postventa |
| CU-031 | Gestionar Garantías por Unidad | Registrar y consultar vigencia y condiciones de garantía por serial. | Gestor de Ventas y Postventa (consulta: Consumidor Registrado) |
| CU-032 | Adjuntar Documentos a Unidades | Adjuntar facturas, certificados y comprobantes, con hash de integridad. | Gestor de Ventas y Postventa |
| CU-033 | Registrar Evento en Blockchain | Enviar eventos críticos a la red con hash y timestamp. | Sistema (backend + smart contract) |
| CU-034 | Consultar Registros Blockchain y Certificados | Verificar integridad y ver/descargar certificados digitales en PDF. | Auditor, Super Administrador, Consumidor Registrado |
| CU-035 | Gestionar Reportes y Dashboards | Indicadores de importación, incidencias, ventas y cumplimiento, con filtros y exportación. | Administrador de Empresa, Super Administrador |

> Nota: el actor de CU-002, CU-005, CU-009, CU-011, CU-024, CU-027 y CU-031 se tomó de las tablas de funciones y paquetes del documento. En CU-027 el equipo definió además el nombre "Registrar Estado de Pago (referencial)".

---

## 3. Casos de uso por Sprint (prioridad, plataforma, actor, paquete)

Cada CU se ubica en el Sprint donde se desarrolla según el Product Backlog (sección "Casos de uso cubiertos").

### Sprint 0: Arquitectura, empresas, usuarios y roles
**Objetivo:** definir arquitectura y modelo de datos, configurar Backend/Web/Móvil/PostgreSQL e implementar empresas, usuarios y roles.

| ID | Caso de uso | Prioridad | Web | Móvil | Actor | Paquete |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| CU-001 | Gestionar Empresas (Tenants) | Alta | ✓ | — | Super Administrador | P1 |
| CU-002 | Gestionar Usuarios del Sistema | Alta | ✓ | — | Administrador de Empresa | P1 |
| CU-003 | Asignar Roles y Permisos a Usuario | Alta | ✓ | — | Administrador de Empresa | P1 |

### Sprint 1: Autenticación y gestión de productos
**Objetivo:** completar la seguridad de acceso y desarrollar productos, variantes, categorías, certificaciones, catálogo, actores y ubicaciones.

| ID | Caso de uso | Prioridad | Web | Móvil | Actor | Paquete |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| CU-004 | Autenticar y Recuperar Contraseña | Alta | ✓ | ✓ | Todos los usuarios con cuenta | P1 |
| CU-006 | Gestionar Productos y Variantes | Alta | ✓ | — | Administrador de Empresa | P2 |
| CU-007 | Gestionar Certificaciones Técnicas | Media | ✓ | — | Administrador de Empresa | P2 |
| CU-008 | Gestionar Catálogo por Empresa | Alta | ✓ | — | Administrador de Empresa | P2 |
| CU-009 | Gestionar Categorías de Productos | Media | ✓ | — | Super Administrador, Administrador de Empresa | P2 |
| CU-013 | Gestionar Actores de la Cadena | Media | ✓ | — | Administrador de Empresa | P3 |
| CU-014 | Gestionar Ubicaciones Físicas | Media | ✓ | — | Administrador de Empresa | P3 |

### Sprint 2: Compras, unidades y logística
**Objetivo:** seguimiento físico de unidades, compras y recepción, identificadores y QR, y procesos logísticos.

| ID | Caso de uso | Prioridad | Web | Móvil | Actor | Paquete |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| CU-010 | Gestionar Órdenes de Compra | Alta | ✓ | — | Gestor de Operaciones | P2 |
| CU-011 | Aprobar / Rechazar Compra | Alta | ✓ | — | Administrador de Empresa | P2 |
| CU-012 | Gestionar Recepciones de Mercancía | Alta | ✓ | — | Gestor de Operaciones | P2 |
| CU-015 | Gestionar Unidades de Producto (Serial/IMEI) | Alta | ✓ | — | Gestor de Operaciones | P4 |
| CU-016 | Generar y Descargar Código QR | Alta | ✓ | — | Gestor de Operaciones | P4 |
| CU-019 | Gestionar Envíos Logísticos | Alta | ✓ | — | Gestor de Operaciones | P4 |
| CU-020 | Asignar / Desasignar Unidades a Envío | Alta | ✓ | — | Gestor de Operaciones | P4 |
| CU-021 | Registrar Eventos y Condiciones de Transporte | Alta | ✓ | ✓ | Gestor de Operaciones | P4 |

### Sprint 3: Trazabilidad, blockchain y autenticidad
**Objetivo:** trazabilidad digital de unidades e integración con blockchain: historial, verificación de autenticidad, escaneo QR y evidencias.

| ID | Caso de uso | Prioridad | Web | Móvil | Actor | Paquete |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| CU-017 | Escanear Código QR | Alta | — | ✓ | Gestor de Operaciones, Consumidor Registrado, Visitante Anónimo | P4 |
| CU-018 | Registrar Consulta de Trazabilidad | Alta | ✓ (backend) | ✓ (backend) | Sistema (automático) | P4 |
| CU-022 | Consultar Historial y Verificar Autenticidad | Alta | ✓ | ✓ | Consumidor Registrado, Visitante Anónimo, Auditor | P4 |
| CU-023 | Reportar Sospecha de Falsificación | Media | — | ✓ | Consumidor Registrado, Visitante Anónimo | P4 |
| CU-032 | Adjuntar Documentos a Unidades | Media | ✓ | — | Gestor de Ventas y Postventa | P5 |
| CU-033 | Registrar Evento en Blockchain | Alta | ✓ (backend) | — | Sistema (backend + smart contract) | P6 |
| CU-034 | Consultar Registros Blockchain y Certificados | Alta | ✓ | ✓ (lectura) | Auditor, Super Administrador, Consumidor Registrado | P6 |

### Sprint 4: Ventas, consumidor, devoluciones y reportes
**Objetivo:** funcionalidades comerciales y de posventa: ventas, pagos, devoluciones, garantías, notificaciones, preferencias y reportes.

| ID | Caso de uso | Prioridad | Web | Móvil | Actor | Paquete |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| CU-005 | Consultar Bitácora y Gestionar Notificaciones | Media | ✓ | ✓ | Super Administrador, Auditor | P1 |
| CU-024 | Gestionar Alertas e Incidencias | Alta | ✓ | ✓ | Gestor de Operaciones, Administrador de Empresa | P4 |
| CU-025 | Gestionar Ventas | Alta | ✓ | — | Gestor de Ventas y Postventa | P5 |
| CU-026 | Asignar Unidades Físicas a Venta | Alta | ✓ | — | Gestor de Ventas y Postventa | P5 |
| CU-027 | Gestionar Pagos | Media | ✓ | — | Gestor de Ventas y Postventa, Super Administrador | P5 |
| CU-028 | Consultar Historial de Compras del Consumidor | Media | ✓ | ✓ | Consumidor Registrado | P5 |
| CU-029 | Gestionar Devoluciones | Alta | ✓ | — | Gestor de Ventas y Postventa | P5 |
| CU-030 | Asignar Unidades a Devolución | Alta | ✓ | — | Gestor de Ventas y Postventa | P5 |
| CU-031 | Gestionar Garantías por Unidad | Alta | ✓ | — | Gestor de Ventas y Postventa | P5 |
| CU-035 | Gestionar Reportes y Dashboards | Alta | ✓ | — | Administrador de Empresa, Super Administrador | P7 |

**Resumen:** 35 CU en total; 3 + 7 + 8 + 7 + 10 por sprint (S0 a S4). Prioridad Alta: 25, Media: 10.

> **Diferencias internas del documento** (la tabla 3.9 "Lista de casos de uso" y los sprints del Product Backlog no coinciden en 4 CU): CU-005 figura en Sprint 3 en la lista pero en Sprint 4 en el backlog; CU-024 en Sprint 3 vs. Sprint 4; CU-015 en Sprint 1 vs. Sprint 2; CU-032 en Sprint 2 vs. Sprint 3. Aquí se usó el backlog por sprint.

---

## 4. Paquetes de casos de uso (7)

| Paquete | Módulo(s) | Casos de uso | Cant. | Actores principales |
| :--- | :--- | :--- | :---: | :--- |
| **P1. Seguridad y Multi-Tenant** | 5.1.1 | CU-001, 002, 003, 004, 005 | 5 | Super Administrador, Administrador de Empresa, todos los usuarios con cuenta |
| **P2. Catálogo y Abastecimiento** | 5.1.2, 5.1.3 | CU-006, 007, 008, 009, 010, 011, 012 | 7 | Administrador de Empresa, Gestor de Operaciones |
| **P3. Actores y Ubicaciones** | 5.1.4 | CU-013, 014 | 2 | Administrador de Empresa |
| **P4. Inventario y Trazabilidad (Núcleo)** | 5.1.5 | CU-015 a CU-024 | 10 | Gestor de Operaciones, Consumidor Registrado, Visitante Anónimo, Auditor |
| **P5. Comercialización (Ventas y Postventa)** | 5.1.6, 5.1.7 | CU-025 a CU-032 | 8 | Gestor de Ventas y Postventa, Consumidor Registrado, Super Administrador (en CU-027) |
| **P6. Blockchain y Certificados** | 5.1.8 | CU-033, 034 | 2 | Sistema (Smart Contract), Auditor, Super Administrador, Consumidor Registrado |
| **P7. Reportes y Administración** | Transversal | CU-035 | 1 | Administrador de Empresa, Super Administrador |

---

## 5. Product Backlog: lista completa de tareas por Sprint (T001–T061)

Total: **61 tareas, 271 horas estimadas** (S0: 57 h · S1: 51 h · S2: 53 h · S3: 55 h · S4: 55 h).

### Sprint 0: Arquitectura, empresas, usuarios y roles (T001–T013)

| ID | Rol | Funcionalidad | Prioridad | Horas | Plataforma |
| :--- | :--- | :--- | :--- | :---: | :--- |
| T001 | Dev Team (Arquitectura) | Definición de la arquitectura general del sistema | Alta | 5 | Arquitectura |
| T002 | Dev Team (Backend) | Configuración inicial del proyecto Backend con FastAPI | Alta | 4 | Backend |
| T003 | Dev Team (Frontend) | Configuración inicial de la plataforma Web con Angular | Alta | 4 | Web |
| T004 | Dev Team (Mobile) | Configuración inicial de la aplicación Móvil con Flutter | Alta | 4 | Móvil |
| T005 | Dev Team (Backend) | Configuración de la conexión con PostgreSQL | Alta | 4 | Backend |
| T006 | Dev Team (Backend) | Diseño del modelo de datos para empresas, usuarios, roles y productos | Alta | 5 | Base de Datos |
| T007 | Dev Team (Backend) | Definición de entidades y relaciones principales del sistema | Alta | 4 | Base de Datos |
| T008 | Dev Team (Backend) | Gestión de empresas y configuración multiempresa (API REST) | Alta | 5 | Backend |
| T009 | Dev Team (Frontend) | Interfaz de gestión de empresas (UI Angular) | Alta | 4 | Web |
| T010 | Dev Team (Backend) | Gestión de usuarios del sistema (API REST) | Alta | 5 | Backend |
| T011 | Dev Team (Frontend) | Interfaz de administración de usuarios (UI Angular) | Alta | 4 | Web |
| T012 | Dev Team (Backend) | Roles y permisos de usuarios (RBAC) | Alta | 5 | Backend |
| T013 | Dev Team (Frontend) | Interfaz de asignación de roles y permisos (UI Angular) | Alta | 4 | Web |

### Sprint 1: Autenticación y gestión de productos (T014–T025)

| ID | Rol | Funcionalidad | Prioridad | Horas | Plataforma |
| :--- | :--- | :--- | :--- | :---: | :--- |
| T014 | Dev Team (Backend) | Autenticación y recuperación de contraseña (JWT + OAuth2) | Alta | 5 | Backend |
| T015 | Dev Team (Frontend) | Interfaz de inicio de sesión y recuperación de contraseña (UI Angular) | Alta | 4 | Web |
| T016 | Dev Team (Mobile) | Interfaz de autenticación de usuarios (UI Flutter) | Alta | 4 | Móvil |
| T017 | Dev Team (Backend) | Gestión de productos y variantes (API REST) | Alta | 5 | Backend |
| T018 | Dev Team (Frontend) | Interfaz de registro y edición de productos y variantes (UI Angular) | Alta | 5 | Web |
| T019 | Dev Team (Backend) | Categorías y atributos de productos (API REST) | Media | 4 | Backend |
| T020 | Dev Team (Frontend) | Interfaz de gestión de categorías y catálogo por empresa (UI Angular) | Alta | 4 | Web |
| T021 | Dev Team (Backend) | Certificaciones y especificaciones técnicas (API REST) | Media | 4 | Backend |
| T022 | Dev Team (Frontend) | Interfaz de gestión de certificaciones técnicas (UI Angular) | Media | 4 | Web |
| T023 | Dev Team (Backend) | Gestión de actores de la cadena de suministro (API REST) | Media | 4 | Backend |
| T024 | Dev Team (Backend) | Gestión de ubicaciones físicas (API REST) | Media | 4 | Backend |
| T025 | Dev Team (Frontend) | Interfaz de actores y ubicaciones físicas (UI Angular) | Media | 4 | Web |

### Sprint 2: Compras, unidades y logística (T026–T037)

| ID | Rol | Funcionalidad | Prioridad | Horas | Plataforma |
| :--- | :--- | :--- | :--- | :---: | :--- |
| T026 | Dev Team (Backend) | Gestión de órdenes de compra (API REST) | Alta | 5 | Backend |
| T027 | Dev Team (Frontend) | Interfaz de creación y consulta de órdenes de compra (UI Angular) | Alta | 4 | Web |
| T028 | Dev Team (Backend) | Aprobación y rechazo de órdenes de compra | Alta | 4 | Backend |
| T029 | Dev Team (Backend) | Recepción de mercancía y actualización de existencias | Alta | 5 | Backend |
| T030 | Dev Team (Frontend) | Interfaz de recepción y consulta de mercancía (UI Angular) | Alta | 4 | Web |
| T031 | Dev Team (Backend) | Registro y gestión de unidades individuales | Alta | 5 | Backend |
| T032 | Dev Team (Backend) | Asignación de identificadores únicos a unidades (Serial/IMEI/EID) | Alta | 4 | Backend |
| T033 | Dev Team (Frontend) | Interfaz de administración de unidades individuales (UI Angular) | Alta | 4 | Web |
| T034 | Dev Team (Backend) | Generación de códigos QR únicos por unidad | Alta | 4 | Backend |
| T035 | Dev Team (Frontend) | Interfaz de generación y descarga de códigos QR (UI Angular) | Alta | 4 | Web |
| T036 | Dev Team (Backend) | Envíos, movimientos y asignación de unidades | Alta | 5 | Backend |
| T037 | Dev Team (Mobile) | Registro de recepción, transporte y condiciones mediante app móvil | Alta | 5 | Móvil |

### Sprint 3: Trazabilidad, blockchain y autenticidad (T038–T049)

| ID | Rol | Funcionalidad | Prioridad | Horas | Plataforma |
| :--- | :--- | :--- | :--- | :---: | :--- |
| T038 | Dev Team (Backend) | Registro de eventos de trazabilidad (API REST) | Alta | 5 | Backend |
| T039 | Dev Team (Blockchain) | Conexión con la red Blockchain Ethereum (Testnet) | Alta | 4 | Blockchain |
| T040 | Dev Team (Blockchain) | Diseño del Smart Contract para registro de eventos | Alta | 5 | Blockchain |
| T041 | Dev Team (Blockchain) | Registro de eventos mediante Smart Contract | Alta | 5 | Blockchain |
| T042 | Dev Team (Backend) | Integración de FastAPI con Smart Contracts mediante Web3 | Alta | 5 | Backend |
| T043 | Dev Team (Backend) | Asociación de eventos con actor, ubicación, fecha y transacción | Alta | 4 | Backend |
| T044 | Dev Team (Backend) | Almacenamiento de hashes e identificadores Blockchain en PostgreSQL | Alta | 4 | Backend |
| T045 | Dev Team (Blockchain) | Consulta y validación de registros Blockchain | Alta | 5 | Blockchain |
| T046 | Dev Team (Mobile) | Escaneo de códigos QR mediante cámara (UI Flutter) | Alta | 4 | Móvil |
| T047 | Dev Team (Mobile) | Consulta del historial y datos de trazabilidad mediante QR (UI Flutter) | Alta | 5 | Móvil |
| T048 | Dev Team (Backend) | Verificación de autenticidad y reporte de falsificación (API REST) | Alta | 5 | Backend |
| T049 | Dev Team (Backend) | Carga y asociación de documentos a unidades (API REST) | Media | 4 | Backend |

### Sprint 4: Ventas, consumidor, devoluciones y reportes (T050–T061)

| ID | Rol | Funcionalidad | Prioridad | Horas | Plataforma |
| :--- | :--- | :--- | :--- | :---: | :--- |
| T050 | Dev Team (Backend) | Gestión de ventas y asignación de unidades (API REST) | Alta | 5 | Backend |
| T051 | Dev Team (Frontend) | Interfaz de gestión de ventas y unidades asociadas (UI Angular) | Alta | 5 | Web |
| T052 | Dev Team (Backend) | Pagos y registro de transacciones (API REST) | Media | 5 | Backend |
| T053 | Dev Team (Backend) | Devoluciones y asignación de unidades devueltas | Alta | 5 | Backend |
| T054 | Dev Team (Frontend) | Interfaz de devoluciones y garantías por unidad (UI Angular) | Alta | 4 | Web |
| T055 | Dev Team (Backend) | Gestión de garantías por unidad (API REST) | Alta | 4 | Backend |
| T056 | Dev Team (Backend) | Historial de compras y preferencias del usuario | Media | 4 | Backend |
| T057 | Dev Team (Frontend) | Interfaz de historial de compras y preferencias (UI Angular) | Media | 4 | Web |
| T058 | Dev Team (Backend) | Notificaciones y alertas de incidencias (API REST) | Alta | 5 | Backend |
| T059 | Dev Team (Frontend) | Interfaz de notificaciones y alertas (UI Angular) | Media | 4 | Web |
| T060 | Dev Team (Backend) | Generación de certificados digitales y reportes de trazabilidad | Alta | 5 | Backend |
| T061 | Dev Team (Frontend) | Dashboard administrativo y visualización de reportes (UI Angular) | Alta | 5 | Web |

---

## 6. Requisitos funcionales (RF-01 a RF-30)

| ID | Funcionalidad | Descripción | Plataforma | Prioridad |
| :--- | :--- | :--- | :--- | :--- |
| RF-01 | Autenticación de usuarios | Inicio y cierre de sesión con credenciales, generar y renovar tokens JWT, invalidar sesiones cerradas y limitar intentos repetidos de acceso. Las funcionalidades dependen del rol. | Ambas | Alta |
| RF-02 | Gestión de roles y permisos | Crear, editar y desactivar cuentas, asignar un rol principal y administrar permisos por rol según el alcance (global o por empresa). Roles: Super Administrador, Administrador de Empresa, Gestor de Operaciones, Gestor de Ventas y Postventa, Consumidor y Auditor. | Web / Backend | Alta |
| RF-03 | Registro y verificación de usuarios | Autorregistro mediante formulario y verificación de correo; creación y validación de cuentas operativas y de auditoría mediante aprobación administrativa. | Ambas | Alta |
| RF-04 | Recuperación de contraseña | Solicitar recuperación mediante enlace enviado por correo y restablecerla de forma segura. | Ambas | Media |
| RF-05 | Bitácora de accesos y actividades | Registrar intentos de inicio de sesión, cambios de contraseña y operaciones sensibles, con consulta para auditoría y supervisión. | Backend | Media |
| RF-06 | Gestión de empresas (tenants) | Crear, configurar, suspender y eliminar empresas, garantizando el aislamiento de datos entre cada una. | Web / Backend | Alta |
| RF-07 | Registro de productos (catálogo) | Registrar y editar productos del catálogo (modelo, especificaciones técnicas, capacidad, color y precio base) manteniendo historial de cambios. | Web | Alta |
| RF-08 | Gestión de categorías y atributos | Crear, editar y organizar categorías y atributos diferenciadores de los productos. | Web | Media |
| RF-09 | Registro de certificaciones técnicas | Asociar certificaciones (FCC, CE, RoHS, Energy Star, garantía internacional) a cada producto y mostrarlas en su ficha. | Web | Media |
| RF-10 | Gestión de órdenes de compra e importación | Registrar órdenes de compra a proveedores en el extranjero, someterlas a flujo de aprobación y actualizar su estado durante la importación. | Web | Alta |
| RF-11 | Registro de unidades individuales | Registrar cada unidad física recibida con su identificador único (serial, IMEI o EID) y vincularla a la orden de compra. | Web | Alta |
| RF-12 | Generación de códigos QR/NFC | Generar automáticamente un QR o etiqueta NFC único por unidad, derivado de su identificador, con impresión o descarga. | Backend | Alta |
| RF-13 | Registro de movimientos logísticos | Registrar movimientos de una unidad o envío (origen, destino, fechas, medio de transporte y responsable de cada tramo). | Ambas | Alta |
| RF-14 | Registro de eventos de actores externos | Asociar cada evento a un participante externo (proveedor, transportista, aduana) sin requerir que tenga cuenta. | Backend | Alta |
| RF-15 | Registro de condiciones de transporte | Registrar temperatura, humedad y vibración de cada envío, de forma manual o mediante sensores IoT. | Móvil / Backend | Alta |
| RF-16 | Registro de incidencias en la cadena de suministro | Registrar incidencias en transporte, despacho aduanero o almacenamiento, clasificadas por tipo y gravedad. | Ambas | Alta |
| RF-17 | Gestión de devoluciones y garantías | Registrar devoluciones asociadas a una unidad, gestionar el estado de su garantía y adjuntar documentos de respaldo. | Web | Alta |
| RF-18 | Historial de trazabilidad | Construir y presentar el historial cronológico completo de una unidad, desde su compra en el país de origen hasta su entrega al consumidor. | Ambas | Alta |
| RF-19 | Registro de eventos en blockchain | Registrar de forma inmutable los eventos críticos, generando hash y marca de tiempo verificable. | Backend / Blockchain | Alta |
| RF-20 | Consulta de registros blockchain | Consultar registros en blockchain y comparar su integridad frente a los datos operativos de la base de datos relacional. | Web / Backend | Alta |
| RF-21 | Verificación de autenticidad del producto | Verificar la autenticidad y el origen legal de un dispositivo a partir de su identificador digital y registros de trazabilidad. | Ambas | Alta |
| RF-22 | Escaneo de código QR/NFC | Escanear el código con la cámara o lector NFC y consultar de inmediato la información asociada. | Móvil | Alta |
| RF-23 | Acceso público sin registro | Consultar el historial de una unidad escaneada sin registro ni inicio de sesión. | Ambas | Media |
| RF-24 | Portal de consulta del consumidor y exposición externa | Presentar origen, condiciones de transporte, despacho aduanero y autenticidad en formato claro. Misma información disponible por API REST documentada (OpenAPI/Swagger) con clave de API para plataformas e-commerce externas, sin gestionar la compra. | Ambas | Alta |
| RF-25 | Favoritos e historial personal | Guardar unidades como favoritas y consultar el historial de escaneos y compras previas de la cuenta. | Ambas | Media |
| RF-26 | Reporte de sospecha de falsificación | Reportar una unidad sospechosa registrando la denuncia con la evidencia proporcionada. | Ambas | Media |
| RF-27 | Generación de certificados digitales | Generar automáticamente un certificado digital de trazabilidad por unidad al momento de su venta, respaldado por blockchain. | Backend / Web | Alta |
| RF-28 | Descarga y visualización de certificados | Visualizar y descargar en PDF el certificado digital de trazabilidad de una unidad. | Ambas | Alta |
| RF-29 | Notificaciones y alertas | Generar y enviar notificaciones ante incidencias, retiros de producto o eventos relevantes asociados a las unidades del usuario. | Ambas | Alta |
| RF-30 | Reportes y análisis de trazabilidad | Indicadores y reportes sobre tiempos de importación, incidencias, ventas, cumplimiento normativo y estado de la cadena, con filtros por periodo y exportación. | Web | Alta |

**Resumen:** 30 RF; Alta: 23 · Media: 7.

---

## 7. Requisitos no funcionales (RNF-01 a RNF-19)

| ID | Requisito | Actores | Objetivo asociado | RF asociados | Descripción | Import. | Urg. | Estab. | Comentarios |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| RNF-01 | Rendimiento: tiempo de respuesta en consultas críticas | Todos | Tiempos de respuesta rápidos en consultas y gestiones críticas | RF-18, 21, 22, 24 | Tiempo de respuesta promedio ≤ 2 segundos en operaciones críticas de consulta y gestión (excluye confirmación blockchain, ver RNF-19). | Alta | Alta | Alta | Medible con pruebas de carga. |
| RNF-02 | Disponibilidad: continuidad operativa | Todos | Mantener el sistema operativo la mayor parte del tiempo | RF-13, 18, 19, 29 | Disponibilidad mínima del 99,5% considerando la infraestructura en la nube. | Alta | Media | Alta | Depende del proveedor cloud. |
| RNF-03 | Escalabilidad: crecimiento de empresas y datos | Super Administrador, Administrador de Empresa | Crecer en empresas, usuarios y eventos sin rediseñar la arquitectura | RF-06, 07, 10, 13, 19, 30 | La arquitectura debe permitir incrementar recursos de servidores y nodos. | Alta | Media | Media | Prioritario por el modelo multi-tenant. |
| RNF-04 | Seguridad: autenticación y comunicaciones seguras | Todos | Proteger credenciales y comunicaciones | RF-01, 02, 03, 04 | Proteger credenciales y comunicaciones mediante autenticación, autorización y cifrado en tránsito (HTTPS/TLS). | Vital | Inmediata | Alta | Base de la confianza del sistema. |
| RNF-05 | Control de acceso: permisos según rol | Todos | Restringir funciones y datos según el rol | RF-01, 02 | Cada usuario accede únicamente a las funcionalidades y datos de su rol. | Vital | Inmediata | Alta | Complementa a RNF-13. |
| RNF-06 | Integridad de datos: consistencia operativa | Gestor de Operaciones, Administrador de Empresa | Mantener consistencia de la información operativa | RF-07, 10, 11, 13, 16 | La base de datos conserva consistencia mediante validaciones y transacciones controladas. | Alta | Alta | Alta | Aplica a PostgreSQL. |
| RNF-07 | Inmutabilidad: registros blockchain no alterables | Gestor de Operaciones, Auditor, Super Administrador | Que los eventos no se alteren retroactivamente | RF-19, 20 | Los eventos en blockchain se conservan de forma inmutable, permitiendo detectar cualquier alteración. | Vital | Inmediata | Alta | Pilar tecnológico central del proyecto. |
| RNF-08 | Auditabilidad: trazabilidad de actores y eventos | Auditor, Super Administrador | Reconstruir el historial de responsables y eventos | RF-05, 18, 20, 30 | Los eventos identifican actor responsable, fecha, hora e información de cada operación. | Alta | Media | Alta | Respaldado por el rol Auditor. |
| RNF-09 | Interoperabilidad: integración con sistemas externos | Administrador de Empresa, Gestor de Ventas y Postventa | Integración con e-commerce y ERP | RF-24, 27 | APIs REST documentadas para comunicar backend, web, móvil y servicios externos. | Media | Media | Media | Depende de acuerdos con terceros. |
| RNF-10 | Usabilidad: facilidad de uso por rol | Consumidor Registrado, Gestor de Operaciones, Gestor de Ventas y Postventa | Uso sin conocimientos técnicos especializados | RF-13, 22, 24 | Un usuario nuevo completa las tareas principales de su rol en máximo 3 intentos en pruebas de usabilidad. | Media | Media | Media | Métrica verificable en pruebas. |
| RNF-11 | Compatibilidad: soporte multiplataforma | Consumidor Registrado, Gestor de Operaciones | Funcionamiento en distintos dispositivos y navegadores | RF-22, 23 | App móvil en Android e iOS compatibles con Flutter; web accesible desde navegadores modernos. | Alta | Media | Media | — |
| RNF-12 | Mantenibilidad: arquitectura modular | Super Administrador (equipo técnico) | Actualizar componentes sin afectar todo el sistema | RF-01 a RF-30 | Arquitectura modular que facilite el mantenimiento y actualización independiente de sus componentes. | Media | Media | Media | Transversal a toda la plataforma. |
| RNF-13 | Aislamiento multi-tenant: separación de datos entre empresas | Super Administrador, Administrador de Empresa | Evitar que una empresa vea datos de otra | RF-06, 07 | Los datos de una empresa nunca son accesibles para usuarios de otra, sin importar el rol. | Vital | Inmediata | Alta | Crítico para el modelo multiempresa. |
| RNF-14 | Privacidad: protección de datos personales y comerciales | Consumidor Registrado, Gestor de Ventas y Postventa, Auditor | Proteger la confidencialidad de datos personales y documentación comercial | RF-10, 17, 25 | Proteger datos personales de consumidores y documentación comercial sensible (facturas, documentos aduaneros), restringiendo el acceso por rol y propósito. | Vital | Alta | Alta | Relacionado con documentación aduanera y garantías. |
| RNF-15 | Seguridad: gestión de claves criptográficas | Super Administrador | Evitar la exposición de claves privadas de blockchain | RF-19, 20 | Almacenar y gestionar las claves privadas con un servicio dedicado de secretos, sin exponerlas en código o configuración. | Vital | Inmediata | Alta | Soporta RNF-07. |
| RNF-16 | Continuidad: recuperación ante desastres | Super Administrador | Restaurar el sistema ante fallos de infraestructura | RF-06, 18 | Copias de respaldo periódicas de la base de datos y procedimientos de recuperación con tiempo objetivo de restauración definido. | Alta | Media | Media | Depende del proveedor cloud. |
| RNF-17 | Consistencia: sincronización base de datos–blockchain | Gestor de Operaciones, Super Administrador | Sincronizar registros operativos con los de blockchain | RF-19, 20 | Todo evento en la base relacional debe finalizar sincronizado con su registro en blockchain, aunque no sea en tiempo real. | Alta | Alta | Media | Riesgo propio de la arquitectura híbrida. |
| RNF-18 | Disponibilidad: modo offline de la app móvil | Consumidor Registrado, Gestor de Operaciones | Consultar productos escaneados sin internet | RF-22, 25 | Consultar productos previamente escaneados sin conexión, sincronizando al restablecerse la conectividad. | Media | Media | Media | Solo app móvil (Flutter). |
| RNF-19 | Rendimiento: latencia de confirmación blockchain | Gestor de Operaciones, Consumidor Registrado | Informar el envío a blockchain sin esperar la confirmación final | RF-19 | Confirmar visualmente en máximo 2 segundos que un evento fue enviado a blockchain, con estado "pendiente" hasta confirmación de red. | Alta | Alta | Media | Evita la percepción de lentitud. |

**Resumen:** 19 RNF; Importancia Vital: 6 (RNF-04, 05, 07, 13, 14, 15) · Alta: 8 · Media: 5.

---

## Fuentes

- `Doc_Grupo-5-proyecto.md` (archivo del proyecto):
  - Sección 5 "Alcance" y módulos 5.1.1 a 5.1.8
  - Sección 7 "Tecnología"
  - Cap. 3.2.4 "Usuarios del sistema" y 3.5 "Funciones del producto"
  - Cap. 3.6 "Product Backlog" (Sprints 0 a 4, tareas T001–T061, "Casos de uso cubiertos")
  - Cap. 3.7 "Requisitos funcionales" y 3.8 "Requisitos no funcionales"
  - Cap. 3.9 "Lista de casos de uso" y 3.10 "Paquetes y casos de uso"
- `Documento_sin_título.md` (Sprint 2): objetivos, casos de uso y Sprint Backlog del Sprint 2.
- Los totales (horas, conteos por prioridad y por sprint) y la columna "Actor" de CU-002, 005, 009, 011, 024, 027, 031 se calcularon o inferieron a partir de las tablas anteriores.
