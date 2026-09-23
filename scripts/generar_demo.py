"""Regenera los archivos de ejemplo en datos_prueba/.

Uso:
    python scripts/generar_demo.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "datos_prueba"


def principal() -> None:
    CARPETA.mkdir(exist_ok=True)

    pd.DataFrame(
        {
            "Nombre": ["Ana", "Luis", "Ana"],
            "Edad": [25, 30, 25],
            "Ciudad": ["Caracas", "Maracaibo", "Caracas"],
        }
    ).to_excel(CARPETA / "ventas_ene.xlsx", index=False)

    pd.DataFrame(
        {
            "Nombre": ["Pedro", "Ana", " ", "Rosa"],
            "Edad": [40.0, 25.0, float("nan"), 35.0],
            "Ciudad": ["Valencia", "Caracas", None, "Mérida"],
        }
    ).to_excel(CARPETA / "ventas_feb.xlsx", index=False)

    print(f"Demo regenerada en {CARPETA}")


if __name__ == "__main__":
    principal()