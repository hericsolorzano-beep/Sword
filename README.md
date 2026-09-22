# Sword

Automatización con Python para negocios que pierden horas en tareas repetitivas.

## ¿Qué hace?

Une **todos los archivos Excel** de una carpeta en uno solo **limpio**:

- ✅ Normaliza nombres de columnas (mayúsculas, espacios)
- ✅ Quita filas duplicadas
- ✅ Elimina filas vacías y espacios en blanco
- ✅ Unifica archivos `.xlsx` y `.xls`

## Uso

Requisito: Python 3.8+

```bash
# 1. Crear entorno e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install pandas openpyxl

# 2. Colocar tus Excels en una carpeta y ejecutar:
python sword.py carpeta_con_excels

# Resultado: resultado_limpio.xlsx (o define otro con -o)
python sword.py carpeta_con_excels -o ventas_unidas.xlsx
```

## Ejemplo

Dados `ventas_ene.xlsx` y `ventas_feb.xlsx` con datos mezclados, duplicados y espacios:

```
python sword.py datos_prueba
# 2 archivos unidos -> 4 filas en resultado_limpio.xlsx
```

## Servicios relacionados

- 🧹 Limpieza y unión de archivos Excel
- 📝 Llenado automático de formularios
- 🌐 Extracción de datos web
- 📊 Reportes automáticos

¿Tu negocio pierde horas en tareas repetitivas? Este proyecto es un ejemplo de automatización a medida que se entrega listo para usar.