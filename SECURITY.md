# Política de seguridad

## Versiones con soporte

| Versión | Recibe correcciones |
|---|---|
| 1.1.x | Sí |
| 1.0.x | No |

## Qué datos toca Sword

Sword procesa archivos locales y **no envía nada a ningún servidor**: no hay
telemetría, ni analítica, ni conexión a internet en tiempo de ejecución. Todo
ocurre en tu equipo.

Lo que sí hace:

- **Lee** los archivos Excel de la carpeta que le indiques.
- **Escribe** un archivo de salida nuevo. Nunca modifica tus originales.

Como regla general, haz una copia de tus datos antes de la primera ejecución.

## Cómo reportar un fallo de seguridad

No abras un issue público. Escríbeme por correo o de forma privada en GitHub
([perfil](https://github.com/hericsolorzano-beep)) e incluye:

- Qué ocurre y cómo reproducirlo.
- El tipo de archivo de entrada que lo dispara, si puedes compartirlo.
- Tu sistema operativo y versión de Python.

Me comprometo a acusar recibo en 72 horas y a publicar una corrección o una
explicación de por qué no es un problema.

## Alcance

Este proyecto es una utilidad local de escritorio. No tiene superficie de
ataque de red. Aun así, si encuentras algo —por ejemplo, que una entrada
concreta provoque una escritura fuera de la carpeta esperada—, trátalo como
válido y repórtalo.
