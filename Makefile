# Sword: limpiar y unir archivos Excel en segundos.
# Tareas útiles para desarrollo y distribución.

PY := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: install test demo build-exe clean help

help:
	@echo "Objetivos disponibles:"
	@echo "  make install      Instala Sword en un entorno virtual"
	@echo "  make test         Ejecuta las pruebas automatizadas"
	@echo "  make demo         Une los Excel de ejemplo (datos_prueba)"
	@echo "  make build-exe    Genera Sword.exe (Windows, requiere PyInstaller)"
	@echo "  make clean        Borra entorno, cachés y archivos generados"

install:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test:
	$(PY) -m pytest -v

demo:
	$(PY) -m sword datos_prueba -o resultado_limpio.xlsx

build-exe:
	$(PIP) install pyinstaller
	pyinstaller --onefile --name Sword --console sword/cli.py

clean:
	rm -rf .venv build dist *.spec .pytest_cache __pycache__
	rm -f resultado_limpio.xlsx