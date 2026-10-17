// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title TraceabilityRegistry
 * @notice T040/T041 - Registro inmutable de eventos de trazabilidad.
 *
 * Diseño:
 *  - Cada evento de trazabilidad generado por el backend (tabla
 *    `eventotrazabilidad`) se ancla on-chain mediante `eventId` (su clave
 *    primaria) y un `payloadHash` (hash del payload canónico del evento).
 *  - El contrato solo guarda metadatos ligeros + el hash; la evidencia pesada
 *    (imágenes, documentos) permanece off-chain (modelo híbrido).
 *  - Control de acceso por roles: `owner` administra `registrar`.
 *  - Un `eventId` solo puede registrarse una vez (inmutabilidad).
 *
 * Los datos trazables (actor, ubicación, fecha) viajan dentro del payload del
 * backend; on-chain se anclan `tenantId`, `eventType`, `occurredAt` y el hash
 * para permitir verificación y consulta sin exponer información sensible.
 */
contract TraceabilityRegistry {
    /// @dev Versión del contrato, útil para compatibilidad del backend.
    string public constant VERSION = "1.0.0";

    struct TraceEvent {
        bytes32 payloadHash; // hash del payload canónico del evento
        uint256 tenantId; // empresa (tenant) que origina el evento
        uint64 occurredAt; // timestamp UNIX del hecho (no del minado)
        uint64 registeredAt; // timestamp del bloque de registro
        string eventType; // tipo de evento (fabricacion, transporte, ...)
        string metadataURI; // URI opcional de metadatos/evidencia off-chain
        address recordedBy; // cuenta que ancló el evento
        bool exists;
    }

    address public owner;
    uint256 public totalEvents;
    uint256 public totalRegistrars;

    mapping(uint256 => TraceEvent) private _events;
    mapping(address => bool) public isRegistrar;

    event RegistrarAdded(address indexed registrar);
    event RegistrarRemoved(address indexed registrar);
    event EventRegistered(
        uint256 indexed eventId,
        uint256 indexed tenantId,
        bytes32 indexed payloadHash,
        string eventType,
        address recordedBy
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "TraceabilityRegistry: solo el owner");
        _;
    }

    modifier onlyRegistrar() {
        require(isRegistrar[msg.sender], "TraceabilityRegistry: no autorizado");
        _;
    }

    constructor() {
        owner = msg.sender;
        isRegistrar[msg.sender] = true;
        totalRegistrars = 1;
    }

    // ── Administración de registradores ────────────────────────────────────
    function addRegistrar(address registrar) external onlyOwner {
        require(registrar != address(0), "TraceabilityRegistry: direccion cero");
        require(!isRegistrar[registrar], "TraceabilityRegistry: ya es registrador");
        isRegistrar[registrar] = true;
        totalRegistrars += 1;
        emit RegistrarAdded(registrar);
    }

    function removeRegistrar(address registrar) external onlyOwner {
        require(isRegistrar[registrar], "TraceabilityRegistry: no es registrador");
        isRegistrar[registrar] = false;
        totalRegistrars -= 1;
        emit RegistrarRemoved(registrar);
    }

    // ── Registro de eventos ────────────────────────────────────────────────
    function registerEvent(
        uint256 eventId,
        bytes32 payloadHash,
        uint256 tenantId,
        uint64 occurredAt,
        string calldata eventType,
        string calldata metadataURI
    ) external onlyRegistrar returns (bool) {
        require(eventId != 0, "TraceabilityRegistry: eventId invalido");
        require(payloadHash != bytes32(0), "TraceabilityRegistry: hash invalido");
        require(!_events[eventId].exists, "TraceabilityRegistry: evento ya registrado");

        _events[eventId] = TraceEvent({
            payloadHash: payloadHash,
            tenantId: tenantId,
            occurredAt: occurredAt,
            registeredAt: uint64(block.timestamp),
            eventType: eventType,
            metadataURI: metadataURI,
            recordedBy: msg.sender,
            exists: true
        });
        totalEvents += 1;

        emit EventRegistered(eventId, tenantId, payloadHash, eventType, msg.sender);
        return true;
    }

    /// @notice Registra varios eventos en una sola transacción.
    function registerEventBatch(
        uint256[] calldata eventIds,
        bytes32[] calldata payloadHashes,
        uint256[] calldata tenantIds,
        uint64[] calldata occurredAts,
        string[] calldata eventTypes
    ) external onlyRegistrar returns (bool) {
        uint256 n = eventIds.length;
        require(
            n == payloadHashes.length &&
                n == tenantIds.length &&
                n == occurredAts.length &&
                n == eventTypes.length,
            "TraceabilityRegistry: arreglos de distinta longitud"
        );

        for (uint256 i = 0; i < n; i++) {
            uint256 eventId = eventIds[i];
            require(eventId != 0, "TraceabilityRegistry: eventId invalido");
            require(payloadHashes[i] != bytes32(0), "TraceabilityRegistry: hash invalido");
            require(!_events[eventId].exists, "TraceabilityRegistry: evento ya registrado");

            _events[eventId] = TraceEvent({
                payloadHash: payloadHashes[i],
                tenantId: tenantIds[i],
                occurredAt: occurredAts[i],
                registeredAt: uint64(block.timestamp),
                eventType: eventTypes[i],
                metadataURI: "",
                recordedBy: msg.sender,
                exists: true
            });
            totalEvents += 1;

            emit EventRegistered(eventId, tenantIds[i], payloadHashes[i], eventTypes[i], msg.sender);
        }
        return true;
    }

    // ── Consulta y verificación ────────────────────────────────────────────
    function eventExists(uint256 eventId) external view returns (bool) {
        return _events[eventId].exists;
    }

    function getEvent(uint256 eventId)
        external
        view
        returns (
            bytes32 payloadHash,
            uint256 tenantId,
            uint64 occurredAt,
            uint64 registeredAt,
            string memory eventType,
            string memory metadataURI,
            address recordedBy
        )
    {
        TraceEvent storage e = _events[eventId];
        require(e.exists, "TraceabilityRegistry: evento inexistente");
        return (
            e.payloadHash,
            e.tenantId,
            e.occurredAt,
            e.registeredAt,
            e.eventType,
            e.metadataURI,
            e.recordedBy
        );
    }

    /// @notice Verifica que `payloadHash` coincida con el anclado para `eventId`.
    function verifyEvent(uint256 eventId, bytes32 payloadHash) external view returns (bool) {
        TraceEvent storage e = _events[eventId];
        return e.exists && e.payloadHash == payloadHash;
    }
}
