# Sword: limpiar y unir archivos Excel en segundos.
# Tareas útiles para desarrollo y distribución.

PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: install test lint tipos check demo build clean help

help:
	@echo "Objetivos disponibles:"
	@echo "  make install      Instala Sword y las herramientas de desarrollo"
	@echo "  make test         Ejecuta las pruebas con cobertura"
	@echo "  make lint         Revisa estilo y errores comunes (ruff)"
	@echo "  make tipos        Revisa las anotaciones de tipo (mypy)"
	@echo "  make check        test + lint + tipos (lo mismo que la CI exige)"
	@echo "  make demo         Une los Excel de ejemplo (datos_prueba)"
	@echo "  make build        Genera Sword.exe (Windows, requiere PyInstaller)"
	@echo "  make clean        Borra entorno, cachés y archivos generados"

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e . --no-deps

test:
	$(PY) -m pytest -v

lint:
	$(PY) -m ruff check .

tipos:
	$(PY) -m mypy

check: test lint tipos

demo:
	$(PY) -m sword datos_prueba -o resultado_limpio.xlsx

build:
	$(PIP) install pyinstaller
	$(PY) -m pyinstaller --onefile --name Sword --console sword/cli.py

clean:
	rm -rf .venv build dist *.spec .pytest_cache .mypy_cache .ruff_cache __pycache__
	rm -f resultado_limpio.xlsx coverage.xml .coverage
	rm -rf htmlcov
