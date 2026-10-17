"""Servicios de integración con la red Blockchain Ethereum (Sprint 3 - CU-033).

Expone:
- ``ethereum_client``: conexión de bajo nivel a la Testnet (T039).
- ``contract_registry``: carga y despliegue del Smart Contract (T041/T042).
"""

from app.services.blockchain.web3_client import EthereumClient, ethereum_client
from app.services.blockchain.contract_registry import (
    ContractRegistry,
    contract_registry,
)

__all__ = [
    "EthereumClient",
    "ethereum_client",
    "ContractRegistry",
    "contract_registry",
]
