"""Interfaz de consola de Sword.

Uso típico:

    sword CARPETA_CON_EXCELS
    sword CARPETA_CON_EXCELS -o ventas_unidas.xlsx
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

import sword
from sword.core import SwordError, unir

console = Console()
error_console = Console(stderr=True, style="bold red")


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # salida limpia de errores
        error_console.print(f"[bold]Error:[/bold] {message}")
        self.print_usage(file=sys.stderr)
        raise SystemExit(2)


def _tipo_hoja(valor: str) -> str | int:
    return int(valor) if valor.isdigit() else valor


def crear_parser() -> argparse.ArgumentParser:
    parser = _ArgumentParser(
        prog="sword",
        description="Limpia y une archivos Excel en segundos.",
        epilog=(
            "ejemplos:\n"
            "  sword ventas                une todos los Excel de la carpeta 'ventas'\n"
            "  sword ventas -o total.xlsx  guarda el resultado como total.xlsx\n"
            "  sword ventas -r             incluye archivos de subcarpetas\n"
            "  sword --version             muestra la versión\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "carpeta",
        nargs="?",
        default=".",
        metavar="CARPETA",
        help="Carpeta con los archivos Excel (por defecto: la actual)",
    )
    parser.add_argument(
        "-o", "--salida",
        default="resultado_limpio.xlsx",
        metavar="ARCHIVO",
        help="Archivo de salida (.xlsx, .xls o .csv). Por defecto: resultado_limpio.xlsx",
    )
    parser.add_argument(
        "-r", "--recursivo",
        action="store_true",
        help="Buscar Excel también dentro de subcarpetas",
    )
    parser.add_argument(
        "-s", "--hoja",
        default="0",
        type=_tipo_hoja,
        help="Nombre (o número, empezando en 0) de la hoja a leer. Por defecto: la primera",
    )
    parser.add_argument(
        "--columnas-comunes",
        action="store_true",
        help="Conservar solo las columnas que aparecen en todos los archivos",
    )
    parser.add_argument(
        "--conservar-columnas",
        action="store_true",
        help="No normalizar los nombres de las columnas (mantener como están)",
    )
    parser.add_argument(
        "--conservar-duplicados",
        action="store_true",
        help="No eliminar filas duplicadas",
    )
    parser.add_argument(
        "--sin-limpiar",
        action="store_true",
        help="Saltar la limpieza (espacios y filas vacías se conservan)",
    )
    parser.add_argument("-q", "--quieto", action="store_true", help="Mostrar solo lo esencial")
    parser.add_argument("-v", "--verboso", action="store_true", help="Mostrar detalle de cada archivo")
    parser.add_argument("-V", "--version", action="version", version=f"sword {sword.__version__}")
    return parser


def _configurar_logging(verboso: bool = False, quieto: bool = False) -> None:
    nivel = logging.WARNING if quieto else (logging.DEBUG if verboso else logging.INFO)
    logging.basicConfig(
        level=nivel,
        format="%(levelname)s  %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def _mostrar_resumen(resumen, quieto: bool = False, verboso: bool = False) -> None:
    if quieto:
        console.print(f"Listo: {resumen.archivos} archivo(s) -> {resumen.salida} "
                      f"({resumen.filas_salida} filas)")
        return

    if resumen.filas_salida == 0:
        console.print(Panel(
            "[bold yellow]Advertencia:[/bold yellow] el resultado quedó sin filas. "
            "Revisa que tus archivos tengan datos en la hoja indicada.",
            box=box.ROUNDED,
        ))

    tabla = Table(box=box.ROUNDED, title="[bold green]Resumen[/bold green]")
    tabla.add_column("Archivo", style="cyan", no_wrap=True)
    tabla.add_column("Filas de entrada", justify="right")
    tabla.add_column("Filas de salida", justify="right")

    for nombre, antes, despues in resumen.detalles:
        tabla.add_row(nombre, str(antes), str(despues))
    if len(resumen.detalles) > 1:
        tabla.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{resumen.filas_entrada}[/bold]",
            f"[bold]{resumen.filas_salida}[/bold]",
            style="bold",
        )
    console.print(tabla)

    console.print(
        f"[bold green]✔ Listo![/bold green] {resumen.archivos} archivo(s) unido(s) "
        f"en [bold]{resumen.salida}[/bold] "
        f"([cyan]{resumen.filas_salida}[/cyan] filas, "
        f"[cyan]{resumen.columnas}[/cyan] columnas)."
    )
    if resumen.duplicados_eliminados:
        console.print(f"  🗑  {resumen.duplicados_eliminados} fila(s) duplicada(s) eliminada(s)")
    if resumen.filas_vacias_eliminadas:
        console.print(f"  🧹 {resumen.filas_vacias_eliminadas} fila(s) vacía(s) eliminada(s)")


def main(argv: list[str] | None = None) -> int:
    args = crear_parser().parse_args(argv)
    _configurar_logging(args.verboso, args.quieto)

    try:
        resumen = unir(
            Path(args.carpeta),
            Path(args.salida),
            recursivo=args.recursivo,
            hoja=args.hoja,
            columnas_comunes=args.columnas_comunes,
            conservar_columnas=args.conservar_columnas,
            conservar_duplicados=args.conservar_duplicados,
            limpiar=not args.sin_limpiar,
        )
    except SwordError as exc:
        error_console.print(f"[bold]✘ {exc}[/bold]")
        return 1
    except KeyboardInterrupt:
        console.print("\nInterrumpido por el usuario.")
        return 130
    except Exception as exc:  # noqa: BLE001 - nunca mostrar tracebacks al cliente
        if args.verboso:
            raise
        error_console.print(f"[bold]✘ Ocurrió un error inesperado:[/bold] {exc}")
        error_console.print("Reintenta con -v para ver el detalle técnico.")
        return 1

    _mostrar_resumen(resumen, quieto=args.quieto, verboso=args.verboso)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())