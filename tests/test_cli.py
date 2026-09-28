"""Pruebas de la interfaz de consola (comportamiento del comando `sword`)."""

import contextlib
import pathlib
import subprocess
import sys

import pandas as pd
import pytest

from sword.cli import main


def _crear_excels(carpeta):
    carpeta.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_excel(carpeta / "1.xlsx", index=False)
    pd.DataFrame({"a": [3], "b": ["z"]}).to_excel(carpeta / "2.xlsx", index=False)


@contextlib.contextmanager
def _tolera_salida():
    """`--version` termina con SystemExit(0); lo normalizamos para poder probar."""
    with contextlib.suppress(SystemExit):
        yield

class TestCli:
    def test_version_imprimible(self, capsys):
        with _tolera_salida():
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
        # En modo quieto no se imprime la tabla de resumen.
        assert "Resumen" not in out
        assert "Listo" in out

    def test_carpeta_inexistente_sale_1(self, tmp_path, capsys):
        codigo = main([str(tmp_path / "nada")])
        assert codigo == 1
        assert "No existe la carpeta" in capsys.readouterr().err

    def test_sin_excel_sale_1(self, tmp_path, capsys):
        (tmp_path / "vacia").mkdir()
        codigo = main([str(tmp_path / "vacia")])
        assert codigo == 1
        assert "No se encontraron archivos" in capsys.readouterr().err

    def test_salida_xls_avisa_y_sale_1(self, tmp_path, capsys):
        """Regresión: antes escribía un xlsx con extensión .xls en silencio."""
        _crear_excels(tmp_path / "datos")
        codigo = main([str(tmp_path / "datos"), "-o", str(tmp_path / "out.xls")])
        assert codigo == 1
        assert "No se puede guardar" in capsys.readouterr().err
        assert not (tmp_path / "out.xls").exists()

    def test_ayuda_no_falla_sin_argumentos(self, capsys):
        with _tolera_salida():
            main(["--help"])
        assert "CARPETA" in capsys.readouterr().out

    def test_argumento_invalido_sale_2(self):
        with pytest.raises(SystemExit) as exc:
            main(["--opcion-que-no-existe"])
        assert exc.value.code == 2


class TestModulo:
    """`python -m sword` es un punto de entrada documentado: se prueba aparte."""

    def test_python_m_sword_muestra_la_version(self):
        resultado = subprocess.run(
            [sys.executable, "-m", "sword", "--version"],
            capture_output=True,
            text=True,
            cwd=str(pathlib.Path(__file__).resolve().parent.parent),
        )
        assert resultado.returncode == 0, resultado.stderr
        assert "sword" in resultado.stdout

    def test_python_m_sword_une_archivos(self, tmp_path):
        datos = tmp_path / "datos"
        _crear_excels(datos)
        salida = tmp_path / "salida.xlsx"
        resultado = subprocess.run(
            [sys.executable, "-m", "sword", str(datos), "-o", str(salida)],
            capture_output=True,
            text=True,
            cwd=str(pathlib.Path(__file__).resolve().parent.parent),
        )
        assert resultado.returncode == 0, resultado.stderr
        assert pd.read_excel(salida)["a"].tolist() == [1, 2, 3]
