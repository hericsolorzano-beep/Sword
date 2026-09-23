import pandas as pd
import pytest


@pytest.fixture()
def carpeta_excels(tmp_path):
    """Crea una carpeta con dos Excel de ejemplo (con suciedad real)."""
    carpeta = tmp_path / "excels"
    carpeta.mkdir()

    pd.DataFrame(
        {
            "Nombre": ["Ana", "Luis", "Ana"],
            "Edad": [25, 30, 25],
            "Ciudad": ["Caracas", "Maracaibo", "Caracas"],
        }
    ).to_excel(carpeta / "enero.xlsx", index=False)

    pd.DataFrame(
        {
            "Nombre": ["  Pedro", "", "Ana", "Rosa"],
            "Edad": [40, None, 25.0, 35],
            "Ciudad": ["Valencia", None, "Caracas", "Mérida"],
        }
    ).to_excel(carpeta / "febrero.xlsx", index=False)

    return carpeta


@pytest.fixture()
def carpeta_sin_excel(tmp_path):
    """Carpeta sin ningún archivo Excel."""
    carpeta = tmp_path / "vacia"
    carpeta.mkdir()
    (carpeta / "notas.txt").write_text("hola", encoding="utf-8")
    return carpeta