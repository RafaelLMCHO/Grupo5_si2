"""T041 - Compila TraceabilityRegistry.sol y genera el artefacto (ABI + bytecode).

Uso:
    python blockchain/scripts/compile_contracts.py

Genera ``blockchain/build/TraceabilityRegistry.json`` que consume
``app/services/blockchain/contract_registry.py``.

Requiere `py-solc-x` (``pip install py-solc-x``); la primera ejecución descarga
el binario de solc de la versión indicada en SOLC_VERSION.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import solcx
except ImportError:  # pragma: no cover
    print("Falta py-solc-x. Instálelo con: pip install py-solc-x", file=sys.stderr)
    raise SystemExit(1)

SOLC_VERSION = "0.8.26"

BASE_DIR = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = BASE_DIR / "contracts"
BUILD_DIR = BASE_DIR / "build"

CONTRACTS = ["TraceabilityRegistry.sol"]


def ensure_solc() -> None:
    installed = {str(v) for v in solcx.get_installed_solc_versions()}
    if SOLC_VERSION not in installed:
        print(f"Instalando solc {SOLC_VERSION} ...")
        solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)


def compile_all() -> None:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for filename in CONTRACTS:
        source_path = CONTRACTS_DIR / filename
        if not source_path.is_file():
            print(f"Contrato no encontrado: {source_path}", file=sys.stderr)
            raise SystemExit(1)

        compiled = solcx.compile_files(
            [str(source_path)],
            output_values=["abi", "bin", "metadata", "hashes"],
            optimize=True,
            solc_version=SOLC_VERSION,
        )

        key = f"{source_path}:{source_path.stem}"
        if key not in compiled:
            # solcx puede usar rutas relativas; tomamos la única clave del archivo.
            key = next((k for k in compiled if k.endswith(source_path.stem)), None)
        if key is None:
            print(f"No se pudo compilar {filename}", file=sys.stderr)
            raise SystemExit(1)

        data = compiled[key]
        artifact = {
            "contractName": source_path.stem,
            "compilerVersion": SOLC_VERSION,
            "abi": data["abi"],
            "bytecode": "0x" + data["bin"],
        }
        out_path = BUILD_DIR / f"{source_path.stem}.json"
        out_path.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        print(f"OK -> {out_path}  (ABI: {len(artifact['abi'])} entries)")


if __name__ == "__main__":
    ensure_solc()
    compile_all()
