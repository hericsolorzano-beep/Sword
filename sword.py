import argparse
import sys
from pathlib import Path

import pandas as pd


def hallar_archivos(carpeta: Path) -> list[Path]:
    archivos = list(carpeta.glob("*.xlsx")) + list(carpeta.glob("*.xls"))
    if not archivos:
        print("No se encontraron archivos Excel en la carpeta.")
        sys.exit(1)
    return archivos


def limpiar_texto(df: pd.DataFrame) -> pd.DataFrame:
    return df.apply(lambda col: col.map(lambda v: str(v).strip() if isinstance(v, str) else v))


def cargar_y_limpiar(ruta: Path) -> pd.DataFrame:
    df = pd.read_excel(ruta)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    df = limpiar_texto(df)
    return df


def unir(carpeta: Path, salida: Path) -> None:
    archivos = hallar_archivos(carpeta)
    frames = [cargar_y_limpiar(a) for a in archivos]
    combinado = pd.concat(frames, ignore_index=True)
    columnas = [c for c in combinado.columns if str(c) != "nan"]
    combinado = combinado[columnas]
    combinado = combinado.replace(r"^\s*$", pd.NA, regex=True).dropna(how="all")
    combinado = combinado.drop_duplicates().reset_index(drop=True)
    combinado.to_excel(salida, index=False)
    print(f"{len(archivos)} archivos unidos -> {len(combinado)} filas en {salida}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sword: limpia y une archivos Excel.")
    parser.add_argument("carpeta", type=Path, nargs="?", default=Path("."), help="Carpeta con los Excel")
    parser.add_argument("-o", "--salida", type=Path, default=Path("resultado_limpio.xlsx"), help="Archivo de salida")
    args = parser.parse_args()

    if not args.carpeta.is_dir():
        print("La carpeta no existe.")
        sys.exit(1)
    unir(args.carpeta, args.salida)


if __name__ == "__main__":
    main()