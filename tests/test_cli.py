"""Pruebas de la interfaz de consola (comportamiento del comando `sword`)."""

import pandas as pd

from sword.cli import main


def _crear_excels(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_excel(carpeta / "1.xlsx", index=False)
    pd.DataFrame({"a": [3], "b": ["z"]}).to_excel(carpeta / "2.xlsx", index=False)


class TestCli:
    def test_version_imprimible(self, capsys):
        with pytest_raises_version():
            main(["--version"])
        out = capsys.readouterr().out
        assert "sword" in out

    def test_une_y_sale_0(self, tmp_path, capsys):
        _crear_excels(tmp_path / "datos")
        codigo = main([str(tmp_path / "datos"), "-o", str(tmp_path / "out.xlsx")])
        assert codigo == 0
        out = capsys.readouterr().out
        assert "Listo" in out
        assert pd.read_excel(tmp_path / "out.xlsx")["a"].tolist() == [1, 2, 3]

    def test_quieto_minimal(self, tmp_path, capsys):
        _crear_excels(tmp_path / "datos")
        main([str(tmp_path / "datos"), "-q", "-o", str(tmp_path / "o.xlsx")])
        out = capsys.readouterr().out
        assert "▓" not in out  # sin tabla

    def test_carpeta_inexistente_sale_1(self, tmp_path, capsys):
        codigo = main([str(tmp_path / "nada")])
        assert codigo == 1
        assert "No existe la carpeta" in capsys.readouterr().err

    def test_sin_excel_sale_1(self, tmp_path, capsys):
        (tmp_path / "vacia").mkdir()
        codigo = main([str(tmp_path / "vacia")])
        assert codigo == 1
        assert "No se encontraron archivos" in capsys.readouterr().err


def pytest_raises_version():
    """El parser de versiones sale con SystemExit(0); lo normalizamos."""
    import contextlib

    @contextlib.contextmanager
    def _salida():
        try:
            yield
        except SystemExit:
            pass

    return _salida()