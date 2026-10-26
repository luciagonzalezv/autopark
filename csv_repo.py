import csv
from pathlib import Path

from config import (
    CSV_LIQUIDACION,
    CSV_MANUAL,
    CSV_RECHAZADOS,
    SEPARADOR,
)

COLUMNAS_LIQUIDACION = (
    "id",
    "fecha_operacion",
    "patente",
    "tipo_vehiculo",
    "entrada",
    "salida",
    "minutos",
    "base",
    "bonificacion",
    "lavado",
    "total_cobrado",
)
COLUMNAS_MANUAL = (
    "id",
    "fecha_operacion",
    "patente",
    "tipo_vehiculo",
    "dias",
    "entrada",
    "salida",
    "minutos",
    "base",
    "bonificacion",
    "lavado",
    "total_cobrado",
)
COLUMNAS_RECHAZADOS = (
    "id",
    "patente",
    "tipo_vehiculo",
    "entrada",
    "salida",
    "motivo",
)
CAMPOS_MONTO = ("base", "bonificacion", "lavado", "total_cobrado")


def _formatear_registro(registro, columnas):
    fila = {}
    for columna in columnas:
        valor = registro.get(columna, "")
        if columna in CAMPOS_MONTO and valor != "":
            fila[columna] = f"{float(valor):.2f}"
        else:
            fila[columna] = valor
    return fila


def _escribir(ruta, columnas, registros):
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=columnas,
            delimiter=SEPARADOR,
            extrasaction="ignore",
        )
        escritor.writeheader()
        for registro in registros:
            escritor.writerow(_formatear_registro(registro, columnas))


def escribir_liquidacion(registros, ruta=CSV_LIQUIDACION):
    _escribir(ruta, COLUMNAS_LIQUIDACION, registros)


def escribir_rechazados(registros, ruta=CSV_RECHAZADOS):
    _escribir(ruta, COLUMNAS_RECHAZADOS, registros)


def agregar_liquidacion_manual(registro, ruta=CSV_MANUAL):
    ruta = Path(ruta)
    existe = ruta.exists() and ruta.stat().st_size > 0
    with open(ruta, "a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=COLUMNAS_MANUAL,
            delimiter=SEPARADOR,
            extrasaction="ignore",
        )
        if not existe:
            escritor.writeheader()
        escritor.writerow(_formatear_registro(registro, COLUMNAS_MANUAL))
