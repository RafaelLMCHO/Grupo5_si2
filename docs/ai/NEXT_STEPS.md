# Próximos Pasos Operativos (Next Steps - Agentes de IA)

> **Documento:** Checklist Táctico y Cola de Trabajo Inmediata para Agentes  
> **Ubicación:** `docs/ai/NEXT_STEPS.md`  
> **Metodología:** SCRUM · **Sprint Activo:** **Sprint 3 (Trazabilidad, Blockchain y Autenticidad)**  
> **Estado de Base de Código:** Sprints 0, 1 y 2 **100% Implementados y Verificados (120 tests verdes)**  

---

## 1. Contexto Operativo Inmediato

Nos encontramos en **SPRINT 3**. El equipo y los agentes tienen como misión completar la trazabilidad de unidades físicas y su anclaje criptográfico inmutable en la red blockchain.

Toda la base de los sprints anteriores (Multi-tenant, Usuarios, Roles, Catálogo Apple, Órdenes de Compra, Recepción, Unidades Serial/IMEI, QR y Envíos Logísticos) está construida y respaldada por **120 tests unitarios y de integración verdes en `trazabilidad/backend/tests/`**.

---

## 2. Cola de Tareas Inmediatas de Sprint 3 (T038–T049)

```mermaid
flowchart TD
    subgraph BackendEventos ["1. Eventos de Trazabilidad"]
        T038["T038: Endpoints REST para Eventos de Trazabilidad\n(Paquete P4)"]
        T043["T043: Enriquecimiento con Actor, Ubicación y Fechas\n(Paquete P4)"]
    end

    subgraph BlockchainWeb3 ["2. Capa Blockchain Ethereum"]
        T039["T039: Conexión Web3.py a Testnet Sepolia/Amoy"]
        T040["T040: Smart Contract Solidity de Notarización"]
        T041["T041: Lógica de Minado de Hash en Smart Contract"]
        T042["T042: Servicio de Integración FastAPI + Web3.py"]
        T044["T044: Persistencia de txHash y blockNumber en PostgreSQL"]
        T045["T045: Endpoint de Verificación Criptográfica On-Chain"]
    end

    subgraph FrontYMobile ["3. Mobile y Verificación"]
        T046["T046 / T047: Escaneo QR Móvil con Cámara (Flutter)"]
        T048["T048: Endpoint de Verificación de Autenticidad (CU-022)"]
        T049["T049: Carga de Documentos con Hashing SHA-256 (CU-032)"]
    end

    BackendEventos --> BlockchainWeb3
    BlockchainWeb3 --> FrontYMobile
```

### Checklist Detallado de Ejecución

- [ ] **T038 (Backend P4):** Crear endpoints para registrar eventos físicos de trazabilidad y condiciones ambientales (temperatura, humedad, vibración) asociados a envíos y unidades.
- [ ] **T039 / T042 (Backend P6 / Web3):** Configurar el cliente `Web3.py` en `trazabilidad/backend/blockchain/` apuntando al RPC de Ethereum Sepolia/Amoy con clave privada almacenada en `.env`.
- [ ] **T040 / T041 (Solidity P6):** Finalizar y compilar el Smart Contract de trazabilidad (`contracts/Traceability.sol` o similar), exponiendo `recordEvent(uint256 unitId, bytes32 eventHash, uint8 eventType)`.
- [ ] **T044 (DB P4/P6):** Guardar en la tabla de eventos de PostgreSQL el `tx_hash`, `block_number` y estado de confirmación (`confirmado` / `pendiente`).
- [ ] **T045 / T048 (Backend P4/P6):** Implementar la verificación criptográfica que compara el hash recalculado de la base de datos contra el `eventHash` almacenado en el Smart Contract.
- [ ] **T049 (Backend P5):** Endpoint para adjuntar facturas y pólizas de importación a unidades, calculando y persistiendo su hash SHA-256.

---

## 3. Tareas Técnicas de Refactorización y Soporte

El proceso de empaquetado por módulos funcionales (`ADR-003`) se encuentra en ejecución:

1. **Empaquetado Modular en `app/packages/`:**
   * [x] **P1 Seguridad (`app/packages/p1_seguridad/`):** Completado. CU-001 a CU-005 migrados con shims y router agregador integrado. 162/162 tests verdes.
   * [x] **P2 Catálogo y Abastecimiento (`app/packages/p2_catalogo/`):** Completado. CU-006 a CU-012 migrados con shims y `router.py`. Tests 100% verdes.
   * [x] **P3 Actores y Ubicaciones (`app/packages/p3_actores/`):** Completado. CU-013 y CU-014 migrados con shims y `router.py`. Tests 100% verdes.
   * [ ] **P4 Inventario y Trazabilidad Core (`app/packages/p4_trazabilidad/`):** CU-015 a CU-024.
   * [ ] **P5 Comercialización (`app/packages/p5_comercial/`):** CU-032.
   * [ ] **P6 Blockchain (`app/packages/p6_blockchain/`):** CU-033 y CU-034.
   * [ ] **P7 Reportes (`app/packages/p7_reportes/`).**
   * **Validación obligatoria por paquete:** Correr `pytest tests/ -v` asegurando 100% de tests verdes sin alterar URLs `/api/v1/...`.

---

## 4. Criterios de Aceptación para el Agente (DoD por Tarea)

1. **Aislamiento Multi-Tenant:** Cualquier endpoint creado debe recibir `tenant_id: int = Depends(resolve_tenant_id)` y aplicarlo en las consultas.
2. **Control de Acceso RBAC:** Rutas de mutación (`POST`, `PUT`, `DELETE`) deben incluir `dependencies=[Depends(require_roles([Rol.GESTOR_OPERACIONES, Rol.ADMIN_EMPRESA, ...]))]`.
3. **Tests Automatizados:** Cada CU nuevo debe incluir su archivo de prueba correspondiente en `trazabilidad/backend/tests/test_sprint3_*.py`.
4. **Actualización de Handoff:** Al finalizar cualquier intervención, actualizar inmediatamente `docs/ai/HANDOFF_LATEST.md` y `docs/ai/CURRENT_STATE.md`.
