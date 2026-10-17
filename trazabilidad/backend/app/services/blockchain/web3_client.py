"""T039 - Conexión con la red Blockchain Ethereum (Testnet).

Cliente de bajo nivel basado en `web3.py`. El import de `web3` es perezoso para
que el resto del backend arranque aunque la dependencia no esté instalada o la
red no esté configurada (``BLOCKCHAIN_ENABLED=false`` por defecto).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

try:  # pragma: no cover - depende del entorno
    from web3 import Web3
    from web3.middleware import ExtraDataToPOAMiddleware

    WEB3_AVAILABLE = True
except ImportError:  # pragma: no cover
    Web3 = None  # type: ignore[assignment]
    ExtraDataToPOAMiddleware = None  # type: ignore[assignment]
    WEB3_AVAILABLE = False


class BlockchainError(RuntimeError):
    """Error de configuración o comunicación con la red Blockchain."""


class EthereumClient:
    """Gestiona la conexión a la Testnet y la cuenta firmante."""

    def __init__(self) -> None:
        self._web3: Optional["Web3"] = None
        self._account = None

    # ── Configuración ──────────────────────────────────────────────────────
    @property
    def enabled(self) -> bool:
        return bool(settings.BLOCKCHAIN_ENABLED)

    @property
    def rpc_url(self) -> Optional[str]:
        return settings.ETHEREUM_RPC_URL

    def is_configured(self) -> bool:
        """Indica si hay RPC configurado y la librería web3 disponible."""
        return bool(WEB3_AVAILABLE and self.rpc_url)

    # ── Conexión ───────────────────────────────────────────────────────────
    def connect(self) -> "Web3":
        """Construye (y cachea) la instancia de Web3."""
        if not WEB3_AVAILABLE:
            raise BlockchainError(
                "La dependencia 'web3' no está instalada. Ejecute "
                "'pip install -r requirements.txt'."
            )
        if not self.rpc_url:
            raise BlockchainError(
                "ETHEREUM_RPC_URL no está configurado en el entorno."
            )

        if self._web3 is None:
            self._web3 = Web3(
                Web3.HTTPProvider(
                    self.rpc_url,
                    request_kwargs={"timeout": settings.BLOCKCHAIN_TIMEOUT_SECONDS},
                )
            )
            # Compatibilidad con redes PoA (p. ej. algunas testnets) que incluyen
            # el campo extraData de 32 bytes en los bloques.
            try:
                self._web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
            except Exception:  # pragma: no cover - solo si no aplica
                pass
        return self._web3

    def get_web3(self) -> "Web3":
        return self.connect()

    def is_connected(self) -> bool:
        """True si hay RPC y el nodo responde."""
        if not self.is_configured():
            return False
        try:
            return bool(self.connect().is_connected())
        except Exception as exc:  # pragma: no cover - red no disponible
            logger.warning("No se pudo conectar a la red Ethereum: %s", exc)
            return False

    # ── Metadatos de la red ────────────────────────────────────────────────
    def get_chain_id(self) -> int:
        return int(self.connect().eth.chain_id)

    def get_block_number(self) -> int:
        return int(self.connect().eth.block_number)

    def get_network_name(self) -> str:
        return settings.ETHEREUM_NETWORK

    # ── Cuenta firmante ────────────────────────────────────────────────────
    def get_account(self):
        """Devuelve la cuenta firmante derivada de BLOCKCHAIN_PRIVATE_KEY."""
        if self._account is not None:
            return self._account
        private_key = settings.BLOCKCHAIN_PRIVATE_KEY
        if not private_key:
            raise BlockchainError(
                "BLOCKCHAIN_PRIVATE_KEY no está configurado; no se puede firmar."
            )
        self._account = self.connect().eth.account.from_key(private_key)
        return self._account

    def get_balance_wei(self) -> int:
        return int(self.connect().eth.get_balance(self.get_account().address))

    # ── Diagnóstico ────────────────────────────────────────────────────────
    def health(self) -> Dict[str, Any]:
        """Resumen del estado de la conexión (no lanza excepciones)."""
        info: Dict[str, Any] = {
            "enabled": self.enabled,
            "web3_installed": WEB3_AVAILABLE,
            "rpc_configured": bool(self.rpc_url),
            "network": settings.ETHEREUM_NETWORK,
            "expected_chain_id": settings.ETHEREUM_CHAIN_ID,
            "connected": False,
            "chain_id": None,
            "block_number": None,
            "contract_address": settings.SMART_CONTRACT_ADDRESS,
        }
        if not self.is_connected():
            return info
        try:
            info["connected"] = True
            info["chain_id"] = self.get_chain_id()
            info["block_number"] = self.get_block_number()
        except Exception as exc:  # pragma: no cover
            info["error"] = str(exc)
        return info


ethereum_client = EthereumClient()
