import pandas as pd
import pytest

from sword.core import SwordError, hallar_archivos, leer_excel, limpiar_texto, normalizar_columnas, unir


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
        resumen = unir(carpeta, tmp_path / "o.xlsx", columnas_comunes=True)
        resultado = pd.read_excel(tmp_path / "o.xlsx")
        assert list(resultado.columns) == ["a"]

    def test_resumen_cuenta_filas_correctamente(self, carpeta_excels, tmp_path):
        resumen = unir(carpeta_excels, tmp_path / "o.xlsx")
        assert resumen.salida.exists()
        assert resumen.duplicados_eliminados >= 1
        assert resumen.filas_vacias_eliminadas >= 1
        assert resumen.columnas == 3

    def test_carpeta_inexistente_al_unir(self, tmp_path):
        with pytest.raises(SwordError, match="No existe"):
            unir(tmp_path / "nope", tmp_path / "o.xlsx")


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