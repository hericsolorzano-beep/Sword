from pathlib import Path

import pandas as pd
import pytest

from sword.cli import main
from sword.core import (
    SwordError,
    hallar_archivos,
    leer_excel,
    limpiar_texto,
    normalizar_columnas,
    ruta_de_salida,
    unir,
)


class TestHallarArchivos:
    def test_encuentra_todos_los_excel(self, carpeta_excels):
        archivos = hallar_archivos(carpeta_excels)
        assert [a.name for a in archivos] == ["enero.xlsx", "febrero.xlsx"]

    def test_excluye_archivos_temporales(self, carpeta_excels):
        (carpeta_excels / "~$enero.xlsx").write_bytes(b"")
        (carpeta_excels / ".oculto.xlsx").write_bytes(b"")
        assert len(hallar_archivos(carpeta_excels)) == 2

    def test_sin_excel_lanza_error_claro(self, carpeta_sin_excel):
        with pytest.raises(SwordError, match="No se encontraron archivos"):
            hallar_archivos(carpeta_sin_excel)

    def test_carpeta_inexistente_lanza_error(self, tmp_path):
        with pytest.raises(SwordError, match="No existe la carpeta"):
            hallar_archivos(tmp_path / "nope")

    def test_puede_excluir_un_archivo_concreto(self, carpeta_excels):
        objetivo = carpeta_excels / "febrero.xlsx"
        encontrados = hallar_archivos(carpeta_excels, excluir=objetivo)
        assert [a.name for a in encontrados] == ["enero.xlsx"]


class TestRutaDeSalida:
    def test_conserva_csv_y_xlsx(self, tmp_path):
        assert ruta_de_salida(tmp_path / "a.csv") == tmp_path / "a.csv"
        assert ruta_de_salida(tmp_path / "a.xlsx") == tmp_path / "a.xlsx"

    def test_convierte_otros_formatos_a_xlsx(self, tmp_path):
        assert ruta_de_salida(tmp_path / "a.txt") == tmp_path / "a.xlsx"
        assert ruta_de_salida(tmp_path / "a.xlsm") == tmp_path / "a.xlsx"
        sin_extension = tmp_path / "sin_extension"
        assert ruta_de_salida(sin_extension) == tmp_path / "sin_extension.xlsx"

    def test_rechaza_xls(self, tmp_path):
        with pytest.raises(SwordError, match=r'"\.xls"'):
            ruta_de_salida(tmp_path / "a.xls")


class TestLimpieza:
    def test_normaliza_nombres_de_columnas(self):
        df = pd.DataFrame({"Nombre ": [1], " C IUDAD ": [2], "Nombre": [3]})
        limpio = normalizar_columnas(df)
        assert list(limpio.columns) == ["nombre", "c_iudad", "nombre_2"]

    def test_quita_espacios_alrededor_de_texto(self):
        df = pd.DataFrame({"a": [" x ", "  ", "y"]})
        limpio = limpiar_texto(df)
        assert limpio["a"].tolist()[0] == "x"
        assert limpio["a"].tolist()[2] == "y"

    def test_celda_con_solo_espacios_queda_vacia(self):
        df = pd.DataFrame({"a": ["  ", "ok"]})
        limpio = limpiar_texto(df)
        assert pd.isna(limpio["a"].iloc[0])
        assert limpio["a"].iloc[1] == "ok"


class TestUnir:
    def test_une_dos_archivos_y_limpia(self, carpeta_excels, tmp_path):
        salida = tmp_path / "out.xlsx"
        resumen = unir(carpeta_excels, salida)
        assert resumen.archivos == 2
        # entrada: 3 (enero) + 4 (febrero) = 7 filas
        assert resumen.filas_entrada == 7
        # 1 fila vacía eliminada; "Ana" aparece 3 veces -> 2 duplicados
        assert resumen.filas_vacias_eliminadas == 1
        assert resumen.duplicados_eliminados == 2
        assert resumen.filas_salida == 4
        resultado = pd.read_excel(salida)
        assert resultado["nombre"].tolist() == ["Ana", "Luis", "Pedro", "Rosa"]

    def test_conserva_duplicados(self, carpeta_excels, tmp_path):
        resumen = unir(carpeta_excels, tmp_path / "out.xlsx", conservar_duplicados=True)
        assert resumen.duplicados_eliminados == 0
        assert resumen.filas_salida == 6

    def test_sin_limpiar_conserva_filas_vacias(self, carpeta_excels, tmp_path):
        resumen = unir(carpeta_excels, tmp_path / "out.xlsx", limpiar=False)
        assert resumen.filas_vacias_eliminadas == 0
        # la fila en blanco se conserva; solo se quitan los duplicados
        assert resumen.duplicados_eliminados == 2
        assert resumen.filas_salida == 5

    def test_salida_csv(self, carpeta_excels, tmp_path):
        salida = tmp_path / "out.csv"
        unir(carpeta_excels, salida)
        resultado = pd.read_csv(salida)
        assert len(resultado) == 4

    def test_recursivo(self, tmp_path):
        carpeta = tmp_path / "raiz"
        (carpeta / "sub").mkdir(parents=True)
        pd.DataFrame({"a": [1]}).to_excel(carpeta / "a.xlsx", index=False)
        pd.DataFrame({"a": [2]}).to_excel(carpeta / "sub" / "b.xlsx", index=False)
        resumen = unir(carpeta, tmp_path / "o.xlsx", recursivo=False)
        assert resumen.archivos == 1
        resumen = unir(carpeta, tmp_path / "o.xlsx", recursivo=True)
        assert resumen.archivos == 2

    def test_columnas_comunes(self, tmp_path):
        carpeta = tmp_path / "c"
        carpeta.mkdir()
        pd.DataFrame({"a": [1], "b": [2]}).to_excel(carpeta / "1.xlsx", index=False)
        pd.DataFrame({"a": [3], "c": [4]}).to_excel(carpeta / "2.xlsx", index=False)
        unir(carpeta, tmp_path / "o.xlsx", columnas_comunes=True)
        resultado = pd.read_excel(tmp_path / "o.xlsx")
        assert list(resultado.columns) == ["a"]

    def test_columnas_comunes_ignora_archivos_sin_encabezados(self, tmp_path):
        """Un Excel vacío no debe borrar las columnas de los demás.

        La intersección se calculaba sobre el primer archivo alfabético. Si ese
        archivo venía sin columnas, el resultado quedaba vacío y todos los datos
        se perdían sin avisar.
        """
        carpeta = tmp_path / "con_vacio"
        carpeta.mkdir()
        pd.DataFrame().to_excel(carpeta / "a_vacio.xlsx", index=False)
        pd.DataFrame({"nombre": ["Ana"], "edad": [25]}).to_excel(
            carpeta / "b_datos.xlsx", index=False
        )

        unir(carpeta, tmp_path / "o.xlsx", columnas_comunes=True)
        resultado = pd.read_excel(tmp_path / "o.xlsx")
        assert list(resultado.columns) == ["nombre", "edad"]
        assert resultado["nombre"].tolist() == ["Ana"]

    def test_columnas_comunes_conservan_el_orden_del_primer_archivo(self, tmp_path):
        """Regresión: el orden salía del `set` y cambiaba entre ejecuciones.

        Con PYTHONHASHSEED distinto, `list(set(...))` produce órdenes distintos.
        La salida debe ser reproducible y seguir el orden del primer archivo.
        """
        carpeta = tmp_path / "orden"
        carpeta.mkdir()
        columnas = {"zeta": [1], "alfa": [2], "media": [3]}
        for nombre in ("1.xlsx", "2.xlsx"):
            pd.DataFrame(columnas).to_excel(carpeta / nombre, index=False)

        unir(carpeta, tmp_path / "o.xlsx", columnas_comunes=True)
        assert list(pd.read_excel(tmp_path / "o.xlsx").columns) == [
            "zeta",
            "alfa",
            "media",
        ]

    def test_no_relee_su_propia_salida(self, tmp_path):
        """Regresión: Sword se comía el resultado de una ejecución anterior.

        La salida por defecto (`resultado_limpio.xlsx`) cae dentro de la carpeta
        de entrada, así que la segunda corrida encontraba 3 archivos en vez de 2.
        """
        carpeta = tmp_path / "entrada"
        carpeta.mkdir()
        pd.DataFrame({"a": [1, 2]}).to_excel(carpeta / "1.xlsx", index=False)
        pd.DataFrame({"a": [3]}).to_excel(carpeta / "2.xlsx", index=False)
        salida = carpeta / "resultado_limpio.xlsx"

        primera = unir(carpeta, salida)
        assert primera.archivos == 2

        segunda = unir(carpeta, salida)
        assert segunda.archivos == 2
        assert segunda.filas_salida == primera.filas_salida == 3
        assert pd.read_excel(salida)["a"].tolist() == [1, 2, 3]

    def test_salida_en_mayusculas_se_normaliza(self, carpeta_excels, tmp_path):
        """Some editores de Windows guardan con `.XLSX` en mayúsculas.

        El archivo debe quedar escrito y con la extensión en minúsculas, que es
        lo que entienden los escritores de pandas.
        """
        resumen = unir(carpeta_excels, tmp_path / "SALIDA.XLSX")
        assert resumen.salida.name == "SALIDA.xlsx"
        assert resumen.salida.exists()
        assert len(pd.read_excel(resumen.salida)) == 4

    def test_sin_nombre_de_salida_avisa(self, carpeta_excels, tmp_path):
        with pytest.raises(SwordError, match="Falta el nombre"):
            unir(carpeta_excels, Path())

    def test_rechaza_salida_xls_en_vez_de_escribir_un_archivo_mentiroso(
        self, carpeta_excels, tmp_path
    ):
        """Regresión: `-o out.xls` escribía un xlsx renombrado.

        El archivo resultante era OOXML con extensión .xls, ilegible para
        cualquier lector que elija el motor por extensión (xlrd >= 2 no lee
        xlsx). Ahora se avisa al usuario.
        """
        with pytest.raises(SwordError, match="No se puede guardar"):
            unir(carpeta_excels, tmp_path / "out.xls")
        assert not (tmp_path / "out.xls").exists()

    def test_resumen_cuenta_filas_correctamente(self, carpeta_excels, tmp_path):
        resumen = unir(carpeta_excels, tmp_path / "o.xlsx")
        assert resumen.salida.exists()
        assert resumen.duplicados_eliminados >= 1
        assert resumen.filas_vacias_eliminadas >= 1
        assert resumen.columnas == 3

    def test_carpeta_inexistente_al_unir(self, tmp_path):
        with pytest.raises(SwordError, match="No existe"):
            unir(tmp_path / "nope", tmp_path / "o.xlsx")

    def test_elimina_columnas_vacias_del_excel(self, tmp_path):
        """Los Excel exportados por otros programas traen columnas `Unnamed: N`
        al final. Sword debe descartarlas en vez de ensuciar la salida."""
        carpeta = tmp_path / "con_basura"
        carpeta.mkdir()
        pd.DataFrame({"a": [1, 2]}).to_excel(
            carpeta / "1.xlsx", index=False
        )  # pandas deja "Unnamed: 0" si se exporta con index

        resumen = unir(carpeta, tmp_path / "o.xlsx")
        assert list(pd.read_excel(resumen.salida).columns) == ["a"]
        assert resumen.columnas == 1

    def test_resultado_sin_filas_avisa_por_consola(self, tmp_path, capsys):
        """Un Excel sin datos debe producir un aviso, no un fallo silencioso."""
        carpeta = tmp_path / "vacia_datos"
        carpeta.mkdir()
        pd.DataFrame().to_excel(carpeta / "1.xlsx", index=False)

        codigo = main([str(carpeta), "-o", str(tmp_path / "o.xlsx")])
        assert codigo == 0
        assert "Advertencia" in capsys.readouterr().out


class TestLeerExcel:
    def test_lee_hoja_por_nombre_o_indice(self, tmp_path):
        archivo = tmp_path / "multi.xlsx"
        with pd.ExcelWriter(archivo) as writer:
            pd.DataFrame({"x": [1]}).to_excel(writer, sheet_name="Primera", index=False)
            pd.DataFrame({"y": [2]}).to_excel(writer, sheet_name="Segunda", index=False)
        assert leer_excel(archivo, hoja=0)["x"].tolist() == [1]
        assert leer_excel(archivo, hoja="Segunda")["y"].tolist() == [2]

    def test_archivo_ilegible_da_error_amigable(self, tmp_path):
        archivo = tmp_path / "falso.xlsx"
        archivo.write_bytes(b"no soy un excel")
        with pytest.raises(SwordError, match="No pude leer"):
            leer_excel(archivo)
