"""T042/T044 - Integración FastAPI <-> Smart Contract y persistencia del anclaje.

Responsabilidades:
- Calcular el hash canónico del payload de un `EventoTrazabilidad`.
- Anclar (registrar) el evento en la red Blockchain vía Web3.
- Persistir el resultado en `registroblockchain` (txhash, blocknumber, estado...).
- Verificar y consultar los registros anclados.

Modo degradado: si `BLOCKCHAIN_ENABLED=false` (o el contrato no está desplegado)
el servicio NO falla; deja el registro en estado `pendiente` para poder anclarlo
después, de modo que el backend sigue operativo sin la red.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.cu021_eventos_transporte.transport_event import EventoTrazabilidad
from app.models.cu033_blockchain.registro_blockchain import RegistroBlockchain
from app.services.blockchain.contract_registry import contract_registry
from app.services.blockchain.web3_client import BlockchainError, ethereum_client

logger = logging.getLogger(__name__)


def _bolivia_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=-4))).replace(tzinfo=None)


class BlockchainRegistryService:
    """Orquesta el anclaje de eventos de trazabilidad en la Blockchain."""

    # ── Hash del payload ───────────────────────────────────────────────────
    @staticmethod
    def compute_payload_hash(event: EventoTrazabilidad) -> str:
        """SHA-256 del payload canónico del evento (hex de 64 caracteres)."""
        payload = {
            "idevento": event.idevento,
            "idtenant": event.idtenant,
            "tipoevento": str(event.tipoevento),
            "fechahora": event.fechahora.isoformat() if event.fechahora else None,
            "idactororigen": event.idactororigen,
            "idactordestino": event.idactordestino,
            "idubicacion": event.idubicacion,
            "idusuarioresponsable": event.idusuarioresponsable,
            "descripcion": event.descripcion,
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _to_bytes32(payloadhash_hex: str) -> bytes:
        """Convierte el hash hex de 32 bytes a bytes32 para el contrato."""
        try:
            raw = bytes.fromhex(payloadhash_hex)
        except (ValueError, TypeError) as exc:
            raise BlockchainError(f"Payload hash inválido: {payloadhash_hex!r}") from exc
        if len(raw) != 32:
            raise BlockchainError("El payload hash debe representar 32 bytes (SHA-256).")
        return raw

    # ── Configuración ──────────────────────────────────────────────────────
    @staticmethod
    def is_ready() -> bool:
        """True si hay red configurada y el contrato desplegado."""
        return (
            ethereum_client.enabled
            and ethereum_client.is_configured()
            and contract_registry.is_deployed()
        )

    def status(self) -> Dict[str, Any]:
        info = ethereum_client.health()
        info["contract_deployed"] = contract_registry.is_deployed()
        info["artifact_available"] = contract_registry.artifact_exists()
        info["ready"] = self.is_ready()
        return info

    # ── Persistencia ───────────────────────────────────────────────────────
    @staticmethod
    def get_registro(db: Session, idevento: int) -> Optional[RegistroBlockchain]:
        return db.execute(
            select(RegistroBlockchain).where(RegistroBlockchain.idevento == idevento)
        ).scalar_one_or_none()

    def _get_or_create_registro(
        self, db: Session, event: EventoTrazabilidad, payloadhash: str
    ) -> RegistroBlockchain:
        registro = self.get_registro(db, event.idevento)
        if registro is None:
            registro = RegistroBlockchain(
                idevento=event.idevento,
                payloadhash=payloadhash,
                network=settings.ETHEREUM_NETWORK,
                chainid=str(settings.ETHEREUM_CHAIN_ID),
                contractaddress=settings.SMART_CONTRACT_ADDRESS,
                estado="pendiente",
                numeroconfirmaciones=0,
            )
            db.add(registro)
            db.flush()
        else:
            registro.payloadhash = payloadhash
        return registro

    # ── Anclaje ────────────────────────────────────────────────────────────
    def anchor_event(
        self,
        db: Session,
        event: EventoTrazabilidad,
        *,
        commit: bool = True,
        force: bool = False,
    ) -> RegistroBlockchain:
        """Ancla el evento en la Blockchain y persiste el resultado.

        Args:
            commit: hace commit al finalizar (útil en tests con rollback).
            force: reintenta aunque ya exista un registro confirmado.
        """
        payloadhash = event.payloadhash or self.compute_payload_hash(event)
        registro = self._get_or_create_registro(db, event, payloadhash)

        if registro.estado == "confirmado" and not force:
            return registro

        if not self.is_ready():
            registro.estado = "pendiente"
            registro.network = settings.ETHEREUM_NETWORK
            registro.chainid = str(settings.ETHEREUM_CHAIN_ID)
            registro.contractaddress = settings.SMART_CONTRACT_ADDRESS
            registro.mensajeerror = (
                "Blockchain no disponible: falta configuración, red o contrato "
                "desplegado. El evento queda pendiente de anclaje."
            )
            if commit:
                db.commit()
                db.refresh(registro)
            return registro

        try:
            txinfo = self._send_anchor_transaction(event, payloadhash)
            registro.txhash = txinfo["tx_hash"]
            registro.blocknumber = txinfo["block_number"]
            registro.network = settings.ETHEREUM_NETWORK
            registro.chainid = str(settings.ETHEREUM_CHAIN_ID)
            registro.contractaddress = settings.SMART_CONTRACT_ADDRESS
            registro.fechaenvio = _bolivia_now()
            registro.fechaconfirmacion = _bolivia_now()
            registro.estado = "confirmado"
            registro.numeroconfirmaciones = settings.BLOCKCHAIN_CONFIRMATIONS
            registro.mensajeerror = None
            event.estadoverificacion = "verificado"
        except Exception as exc:  # pragma: no cover - requiere red real
            logger.exception("Fallo al anclar el evento %s en Blockchain", event.idevento)
            registro.estado = "rechazado"
            registro.mensajeerror = str(exc)[:2000]
            registro.fechaenvio = _bolivia_now()

        if commit:
            db.commit()
            db.refresh(registro)
        return registro

    @staticmethod
    def _send_anchor_transaction(event: EventoTrazabilidad, payloadhash: str) -> Dict[str, Any]:
        web3 = ethereum_client.get_web3()
        account = ethereum_client.get_account()
        contract = contract_registry.get_contract()

        occurred_at = int(event.fechahora.timestamp()) if event.fechahora else 0
        tx = contract.functions.registerEvent(
            int(event.idevento),
            BlockchainRegistryService._to_bytes32(payloadhash),
            int(event.idtenant),
            occurred_at,
            str(event.tipoevento),
            "",
        ).build_transaction(
            {
                "from": account.address,
                "nonce": web3.eth.get_transaction_count(account.address),
                "chainId": settings.ETHEREUM_CHAIN_ID,
                "gasPrice": web3.eth.gas_price,
            }
        )
        tx["gas"] = int(web3.eth.estimate_gas(tx))

        signed = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = web3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=settings.BLOCKCHAIN_TIMEOUT_SECONDS * 4
        )
        return {
            "tx_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "status": receipt.status,
        }

    # ── Consulta y verificación (T045) ─────────────────────────────────────
    def verify_event(self, db: Session, event: EventoTrazabilidad) -> Dict[str, Any]:
        """Compara el hash local con el anclado on-chain (si el contrato está listo)."""
        payloadhash = event.payloadhash or self.compute_payload_hash(event)
        registro = self.get_registro(db, event.idevento)

        result: Dict[str, Any] = {
            "idevento": event.idevento,
            "payloadhash": payloadhash,
            "registro_estado": registro.estado if registro else None,
            "txhash": registro.txhash if registro else None,
            "en_blockchain": False,
            "coincide": False,
            "verificado": False,
        }
        if not self.is_ready():
            result["detalle"] = "Blockchain no disponible; verificación on-chain omitida."
            result["coincide"] = registro is not None and registro.payloadhash == payloadhash
            return result

        try:
            contract = contract_registry.get_contract()
            exists = contract.functions.eventExists(int(event.idevento)).call()
            if exists:
                onchain_hash = contract.functions.getEvent(int(event.idevento)).call()[0]
                result["en_blockchain"] = True
                result["onchain_payloadhash"] = onchain_hash.hex()
                result["coincide"] = onchain_hash == self._to_bytes32(payloadhash)
                result["verificado"] = result["coincide"]
        except Exception as exc:  # pragma: no cover - requiere red real
            result["detalle"] = f"Error consultando la red: {exc}"
        return result

    def get_onchain_event(self, idevento: int) -> Optional[Dict[str, Any]]:
        """Lee un evento directamente del contrato (requiere red disponible)."""
        if not self.is_ready():
            return None
        contract = contract_registry.get_contract()
        if not contract.functions.eventExists(int(idevento)).call():
            return None
        data = contract.functions.getEvent(int(idevento)).call()
        return {
            "payload_hash": data[0].hex(),
            "tenant_id": data[1],
            "occurred_at": data[2],
            "registered_at": data[3],
            "event_type": data[4],
            "metadata_uri": data[5],
            "recorded_by": data[6],
        }

    def list_registros(self, db: Session, idtenant: int) -> List[RegistroBlockchain]:
        stmt = (
            select(RegistroBlockchain)
            .join(EventoTrazabilidad, EventoTrazabilidad.idevento == RegistroBlockchain.idevento)
            .where(EventoTrazabilidad.idtenant == idtenant)
            .order_by(RegistroBlockchain.idregistro.desc())
        )
        return list(db.execute(stmt).scalars().all())


blockchain_registry = BlockchainRegistryService()
