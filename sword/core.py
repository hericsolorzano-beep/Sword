"""Núcleo de Sword: lectura, limpieza y unión de archivos Excel.

Este módulo no depende de la interfaz de consola: puede usarse como una
librería dentro de cualquier otro script de automatización.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

log = logging.getLogger("sword")

EXTENSIONES_EXCEL = (".xlsx", ".xls", ".xlsm")
"""Extensiones que Sword reconoce como archivos Excel."""


class SwordError(Exception):
    """Error esperado, con mensaje claro para el usuario final."""


@dataclass
class Resumen:
    """Resultado de una unión, listo para mostrarse en pantalla."""

    archivos: int = 0
    filas_entrada: int = 0
    filas_salida: int = 0
    duplicados_eliminados: int = 0
    filas_vacias_eliminadas: int = 0
    columnas: int = 0
    salida: Path | None = None
    detalles: list[tuple[str, int, int]] = field(default_factory=list)
    """Lista de (archivo, filas de entrada, filas de salida)."""


def hallar_archivos(
    carpeta: Path,
    recursivo: bool = False,
    *,
    excluir: Path | None = None,
) -> list[Path]:
    """Devuelve todos los archivos Excel dentro de `carpeta`, ordenados.

    `excluir` ignora un archivo concreto. Sword lo usa para no releer su propia
    salida cuando ésta queda guardada dentro de la carpeta de entrada.
    """
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        raise SwordError(
            f'No existe la carpeta "{carpeta}". Revisa la ruta e inténtalo de nuevo.'
        )

    generador = carpeta.rglob("*") if recursivo else carpeta.glob("*")
    descartado = Path(excluir).resolve() if excluir is not None else None
    archivos = sorted(
        p
        for p in generador
        if p.is_file()
        and p.suffix.lower() in EXTENSIONES_EXCEL
        and not p.name.startswith("~$")
        and not p.name.startswith(".")
        and (descartado is None or p.resolve() != descartado)
    )
    if not archivos:
        ext = ", ".join(EXTENSIONES_EXCEL)
        raise SwordError(f'No se encontraron archivos Excel ({ext}) en "{carpeta}".')
    log.debug("Archivos encontrados: %s", [a.name for a in archivos])
    return archivos


def _nombre_limpio(nombre: object, vistos: dict[str, int]) -> str:
    base = str(nombre).strip().lower().replace(" ", "_")
    base = base or "columna"
    vistos[base] = vistos.get(base, 0) + 1
    if vistos[base] == 1:
        return base
    return f"{base}_{vistos[base]}"


def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza los encabezados: minúsculas, sin espacios, sin repetidos."""
    vistos: dict[str, int] = {}
    df.columns = [_nombre_limpio(c, vistos) for c in df.columns]
    return df


def limpiar_texto(df: pd.DataFrame) -> pd.DataFrame:
    """Quita espacios sobrantes y convierte celdas vacías (ej. "   ") en NA."""
    for col in df.columns:
        serie = df[col]
        es_texto = serie.dtype == object or isinstance(serie.dtype, pd.StringDtype)
        if es_texto:
            serie = serie.map(lambda v: v.strip() if isinstance(v, str) else v)
            df[col] = serie.replace(r"^\s*$", pd.NA, regex=True)
        else:
            df[col] = serie
    return df


def _dropear_columnas_espurias(df: pd.DataFrame) -> pd.DataFrame:
    espias = [
        c
        for c in df.columns
        if str(c).lower() == "nan" or str(c).startswith("Unnamed:")
    ]
    if espias:
        df = df.drop(columns=espias)
    return df


def leer_excel(
    ruta: Path,
    hoja: str | int = 0,
    *,
    conservar_columnas: bool = False,
) -> pd.DataFrame:
    """Lee una hoja de un Excel y la devuelve como DataFrame limpio."""
    try:
        df = pd.read_excel(ruta, sheet_name=hoja)
    except Exception as exc:  # noqa: BLE001 - se convierte en error amigable
        raise SwordError(f'No pude leer "{ruta.name}". Motivo: {exc}') from exc

    # Las columnas espurias se quitan siempre, tengan filas o no: un Excel vacío
    # exportado con índice deja un "Unnamed: 0" que, si sobrevive, contamina la
    # intersección de `--columnas-comunes` y termina descartando todas las
    # columnas de los demás archivos.
    df = _dropear_columnas_espurias(df)
    if not conservar_columnas:
        df = normalizar_columnas(df)
    return df


def unir(
    carpeta: Path,
    salida: Path,
    *,
    recursivo: bool = False,
    hoja: str | int = 0,
    columnas_comunes: bool = False,
    conservar_columnas: bool = False,
    conservar_duplicados: bool = False,
    limpiar: bool = True,
) -> Resumen:
    """Une todos los Excel de `carpeta` en uno limpio y lo guarda en `salida`."""
    salida = ruta_de_salida(salida)
    archivos = hallar_archivos(carpeta, recursivo, excluir=salida)

    frames: list[pd.DataFrame] = []
    resumen = Resumen()
    resumen.archivos = len(archivos)

    for ruta in archivos:
        df = leer_excel(ruta, hoja=hoja, conservar_columnas=conservar_columnas)
        antes = len(df)

        if not df.empty and limpiar:
            df = limpiar_texto(df)
            filas_vacias = df.dropna(how="all")
            resumen.filas_vacias_eliminadas += len(df) - len(filas_vacias)
            df = filas_vacias.reset_index(drop=True)

        frames.append(df)
        resumen.detalles.append((ruta.name, antes, len(df)))
        resumen.filas_entrada += antes
        log.debug("%-40s entrada=%d salida=%d", ruta.name, antes, len(df))

    if columnas_comunes and frames:
        # Un archivo sin encabezados no aporta columnas, pero tampoco puede
        # decir que "no comparte" ninguna: si entrara en la intersección la
        # vaciaría y se perderían los datos de todos los demás, en silencio.
        con_columnas = [f for f in frames if len(f.columns)]
        if con_columnas:
            # La base es el primer archivo *con* columnas, y el orden sale de
            # ella y no de un set: el orden de un set de cadenas cambia entre
            # ejecuciones y haría la salida irreproducible.
            base = con_columnas[0]
            comunes = set(base.columns)
            for df in con_columnas[1:]:
                comunes &= set(df.columns)
            orden = [c for c in base.columns if c in comunes]
            frames = [df[orden] if len(df.columns) else df for df in frames]

    combinado = pd.concat(frames, ignore_index=True, sort=False)
    combinado = _dropear_columnas_espurias(combinado)

    if limpiar and not combinado.empty:
        combinado = combinado.dropna(how="all")

    resumen.columnas = combinado.shape[1]

    if not conservar_duplicados and not combinado.empty:
        antes = len(combinado)
        combinado = combinado.drop_duplicates().reset_index(drop=True)
        resumen.duplicados_eliminados = antes - len(combinado)

    resumen.filas_salida = len(combinado)
    salida = _escribir(combinado, salida)
    resumen.salida = salida
    return resumen


def ruta_de_salida(salida: Path) -> Path:
    """Normaliza la ruta de salida antes de leer o escribir nada.

    Solo se admiten `.xlsx` y `.csv`. Cualquier otra extensión se cambia a
    `.xlsx`, salvo `.xls`, que se rechaza: el formato antiguo de Excel no se
    puede escribir de forma fiable y produciría un archivo con extensión
    mentirosa.

    La extensión se devuelve siempre en minúsculas porque algunos escritores
    eligen el motor de forma literal y no aceptan un nombre como "OUT.XLSX".
    """
    salida = Path(salida)
    if not salida.name:
        raise SwordError(
            "Falta el nombre del archivo de salida. "
            'Prueba con: sword ventas -o total.xlsx'
        )

    extension = salida.suffix.lower()

    if extension == ".xls":
        raise SwordError(
            'No se puede guardar en ".xls" (formato antiguo de Excel). '
            'Usa ".xlsx" o ".csv": los dos se abren en cualquier Excel.'
        )
    if extension in (".csv", ".xlsx"):
        # Se reconstruye la ruta para dejar la extensión en minúsculas: algunos
        # escritores eligen el motor de forma literal y no aceptan "OUT.XLSX".
        return salida.with_suffix(extension)
    return salida.with_suffix(".xlsx")


def _escribir(df: pd.DataFrame, salida: Path) -> Path:
    """Escribe el DataFrame. `salida` debe venir de `ruta_de_salida`."""
    if salida.suffix.lower() == ".csv":
        salida.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(salida, index=False, encoding="utf-8-sig")
        return salida

    salida.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        # openpyxl no puede escribir una hoja sin filas: se añade una columna
        # vacía solo para que el archivo exista y sea abrible.
        df = df.assign(__sword_placeholder__=pd.Series(dtype="float"))
    df.to_excel(salida, index=False)
    return salida
