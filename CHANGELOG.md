# Changelog

Todas las novedades de Sword se anotan aquí.
El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto usa [versiones semánticas](https://semver.org/lang/es/).

## [1.1.0] — 2026-09-27

### Corregido

- **Sword ya no se cae en Windows al terminar.** En la consola de Windows
  (codificación cp1252) no existen el símbolo `✔` ni los emojis del resumen. Al
  no poder codificarlos, Python lanzaba `UnicodeEncodeError` y el programa
  terminaba **con error después de haber unido los archivos correctamente**: el
  cliente veía un fallo justo en el mensaje de éxito. Ahora los flujos de
  salida se reconfiguran con `errors="replace"` y el carácter se degrada en vez
  de tumbar la herramienta. Este defecto no lo detectaban las pruebas
  anteriores porque capturaban la salida sin pasar por una consola real; lo
  encontró la CI en `windows-latest`, que es justo para lo que sirve.
- **Sword ya no relee su propia salida.** Cuando la salida se guardaba dentro de
  la carpeta de entrada —cosa que pasa por defecto si ejecutas Sword desde
  dentro de esa carpeta, o si usas `-o` con una ruta dentro de ella— el programa
  encontraba su propio resultado entre los archivos de entrada y lo volvía a
  mezclar. Ahora la salida queda excluida de la búsqueda, y las ejecuciones
  repetidas son idempotentes.
- **`--columnas-comunes` ya no cambia el orden de las columnas entre
  ejecuciones.** El orden se sacaba de un `set`, cuyo orden depende del hash de
  las cadenas y cambia entre proceso y proceso. Eso hacía la salida
  irreproducible y rompía las comparaciones entre meses. Ahora sigue el orden de
  columnas del primer archivo.
- **`--columnas-comunes` ya no pierde datos cuando hay un Excel vacío.** La
  intersección de columnas se calculaba sobre el primer archivo alfabético. Si
  ese archivo venía sin encabezados, la intersección quedaba vacía, el archivo
  de salida salía sin ninguna columna y **todos los datos se perdían sin
  ningún aviso**. Ahora los archivos sin encabezados se ignoran al calcular la
  intersección.
- **Los Excel vacíos ya no dejan columnas basura.** Al leer una hoja sin datos
  se conservaba una columna `Unnamed: 0`, que contaminaba la limpieza y la
  intersección de columnas. Ahora las columnas espurias se descartan siempre,
  tengan filas o no.
- **Ya no se escriben archivos `.xls` con extensión mentirosa.** `sword -o
  salida.xls` guardaba en realidad un xlsx (OOXML) con el nombre `.xls`, un
  archivo que Excel toleraba pero que cualquier lector que elija el motor por
  extensión — como `xlrd>=2` — no podía abrir. Ahora se avisa al usuario y se
  sugiere `.xlsx` o `.csv`. **Esto no rompe a nadie:** la salida `.xls` nunca
  funcionó, porque el archivo que producía estaba corrupto por diseño.
- `-o SALIDA.XLSX` ya no falla. La extensión se normaliza a minúsculas, que es
  lo que entienden los escritores de pandas.
- `-o` con una ruta sin nombre (por ejemplo `-o .`) daba un error interno en vez
  de un mensaje claro. Ahora se explica qué falta.
- Se eliminó una variable muerta en `sword/core.py` que Sword calculaba y nunca
  usaba.
- La firma de `_ArgumentParser.error` se corrigió para que coincida con la de
  `argparse` (mypy ya no se queja).

### Añadido

- **macOS entra en la CI.** La documentación afirmaba soporte para macOS sin que
  ninguna prueba lo cubriera. Ahora se prueba en Windows, Linux y macOS, que es
  lo que hace verdadera la promesa.
- Linter y verificador de tipos en la CI (`ruff` y `mypy`) con configuración
  dentro de `pyproject.toml`.
- Cobertura de pruebas medida en cada ejecución, con un mínimo del 85 % para que
  una regresión no pase inadvertida.
- Prueba de humo que ejecuta el comando `sword` **ya instalado**, y no solo
  `python -m sword`. Es el punto de entrada que usa el cliente final.
- El proceso de release compila y verifica un binario para **Windows, macOS y
  Linux** en cada versión publicada.
- `CHANGELOG.md`, `SECURITY.md`, `CONTRIBUTING.md` y plantillas de issues.
- `Dependabot` configurado para mantener las dependencias al día.

### Cambiado

- La versión se declara en un solo sitio (`sword/__init__.py`) y `pyproject.toml`
  la lee de ahí, de modo que ya no pueden quedar desincronizadas.
- La ayuda de `-o` ya no anuncia `.xls` entre los formatos de salida. Sword
  **sigue leyendo** archivos `.xls`; lo que deja de hacer es producirlos.

## [1.0.0] — 2026-09-23

### Añadido

- Primera versión pública: une y limpia los archivos Excel de una carpeta.
- Interfaz de consola con resumen del proceso.
- Instaladores para Windows y Linux, y `Sword.exe` en GitHub Releases.
- Pruebas automatizadas en Windows y Linux.
