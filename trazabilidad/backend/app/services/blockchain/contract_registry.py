"""T041 - Carga, despliegue y acceso al Smart Contract TraceabilityRegistry.

El artefacto compilado (ABI + bytecode) se genera con
``blockchain/scripts/compile_contracts.py`` y se guarda en
``blockchain/build/TraceabilityRegistry.json``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings
from app.services.blockchain.web3_client import BlockchainError, ethereum_client

logger = logging.getLogger(__name__)

BUILD_DIR = Path(__file__).resolve().parents[3] / "blockchain" / "build"
DEFAULT_ARTIFACT = BUILD_DIR / "TraceabilityRegistry.json"


class ContractRegistry:
    """Localiza el artefacto y construye instancias de contrato listas para usar."""

    def __init__(self, artifact_path: Path = DEFAULT_ARTIFACT) -> None:
        self._artifact_path = artifact_path
        self._artifact: Optional[Dict[str, Any]] = None

    # ── Artefacto compilado ────────────────────────────────────────────────
    @property
    def artifact_path(self) -> Path:
        return self._artifact_path

    def artifact_exists(self) -> bool:
        return self._artifact_path.is_file()

    def load_artifact(self) -> Dict[str, Any]:
        if self._artifact is None:
            if not self.artifact_exists():
                raise BlockchainError(
                    f"No se encontró el artefacto del contrato en "
                    f"'{self._artifact_path}'. Ejecute "
                    f"'python blockchain/scripts/compile_contracts.py'."
                )
            self._artifact = json.loads(self._artifact_path.read_text(encoding="utf-8"))
        return self._artifact

    @property
    def abi(self) -> list:
        return self.load_artifact()["abi"]

    @property
    def bytecode(self) -> str:
        return self.load_artifact()["bytecode"]

    # ── Instancia de contrato ──────────────────────────────────────────────
    def get_contract(self, address: Optional[str] = None):
        """Devuelve una instancia `web3.contract.Contract` del registro."""
        contract_address = address or settings.SMART_CONTRACT_ADDRESS
        if not contract_address:
            raise BlockchainError(
                "SMART_CONTRACT_ADDRESS no está configurado y no se indicó dirección."
            )
        web3 = ethereum_client.get_web3()
        return web3.eth.contract(
            address=web3.to_checksum_address(contract_address),
            abi=self.abi,
        )

    def is_deployed(self) -> bool:
        if not (ethereum_client.is_configured() and settings.SMART_CONTRACT_ADDRESS):
            return False
        try:
            code = ethereum_client.get_web3().eth.get_code(
                ethereum_client.get_web3().to_checksum_address(
                    settings.SMART_CONTRACT_ADDRESS
                )
            )
            return bool(code) and code != b"\x00"
        except Exception as exc:  # pragma: no cover - red no disponible
            logger.warning("No se pudo verificar el contrato desplegado: %s", exc)
            return False

    def deploy(self, *, from_address: Optional[str] = None) -> Dict[str, Any]:
        """Despliega el contrato y devuelve tx_hash, address y receipt."""
        web3 = ethereum_client.get_web3()
        account = ethereum_client.get_account()
        sender = from_address or account.address

        contract = web3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        nonce = web3.eth.get_transaction_count(sender)

        tx = contract.constructor().build_transaction(
            {
                "from": sender,
                "nonce": nonce,
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
            "address": receipt.contractAddress,
            "block_number": receipt.blockNumber,
            "status": receipt.status,
        }


contract_registry = ContractRegistry()
