# Cómo contribuir a Sword

Gracias por querer ayudar. Sword es un proyecto pequeño y las revisiones grandes
son bienvenidas.

## Antes de abrir un issue

Si es un error, incluye el mensaje completo de la consola, tu sistema operativo
y la versión de Sword (`sword --version`). Si es una petición, explica el
trabajo manual que quieres eliminar: eso ayuda a decidir si vale la pena.

## Montar el entorno

```bash
git clone https://github.com/hericsolorzano-beep/Sword
cd Sword
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e . --no-deps
```

## Antes de abrir un pull request

```bash
make check      # corre las tres puertas: test + lint + tipos
```

O a mano:

```bash
pytest                    # pruebas, con reporte de cobertura
ruff check .              # estilo y errores comunes
mypy                      # tipos
```

La cobertura se mide siempre, pero **el mínimo del 85 % solo lo exige la CI**
(mediante `--cov-fail-under=85`). Si quieres replicarlo en tu máquina:

```bash
pytest --cov-fail-under=85
```

## Cómo escribo el código

- Español en los mensajes para el usuario final y en los docstrings. Es la
  lengua de quien usa la herramienta.
- Los errores se acompañan de `SwordError` con un mensaje que dice qué hacer, no
  solo qué falló. El usuario no debería ver un traceback.
- Toda corrección de bug viene con su prueba de regresión. Si no se puede
  escribir una prueba que falle antes del arreglo, probablemente no sea un bug.
- Funciones cortas y con una responsabilidad. El núcleo (`sword/core.py`) no
  sabe nada de la consola; la consola (`sword/cli.py`) no toca pandas.
- Sin dependencias nuevas sin una razón explicada en el issue.

## Commits

Mensajes en modo imperativo y en inglés, siguiendo
[Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):

```
fix: no releer el archivo de salida como entrada
feat: agregar --conservar-espacios
docs: aclarar el límite de .xls
```

## Reportes de seguridad

No abras un issue público. Sigue [SECURITY.md](SECURITY.md).

## Al enviar un cambio

Aclara en la descripción qué problema resuelve y cómo lo verificaste. Si toca el
formato de salida, adjunta un ejemplo de los datos antes y después.
