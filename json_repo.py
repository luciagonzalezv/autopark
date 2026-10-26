import json
from datetime import datetime

from config import ARCHIVO_MOVIMIENTOS, ARCHIVO_TARIFAS, FORMATO_FECHA

CLAVES_CONFIGURACION = (
    "minutos_bloque_inicial",
    "minutos_limite_primer_tramo",
    "minutos_hora_adicional",
    "minutos_dia_completo",
)
CLAVES_TARIFA = (
    "precio_bloque_30min",
    "precio_hora_adicional",
    "tope_dia",
    "precio_lavado",
)


def cargar_json(ruta):
    with open(ruta, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def cargar_tarifas(ruta=ARCHIVO_TARIFAS):
    datos = cargar_json(ruta)
    if not isinstance(datos, dict):
        raise ValueError("El archivo de tarifas debe contener un objeto JSON.")
    if "configuracion" not in datos or "tarifas" not in datos:
        raise ValueError("El archivo de tarifas debe tener 'configuracion' y 'tarifas'.")

    configuracion = datos["configuracion"]
    tarifas = datos["tarifas"]
    if not isinstance(configuracion, dict) or not isinstance(tarifas, dict):
        raise ValueError("'configuracion' y 'tarifas' deben ser objetos JSON.")

    for clave in CLAVES_CONFIGURACION:
        valor = configuracion.get(clave)
        if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
            raise ValueError(f"La configuración '{clave}' debe ser un entero positivo.")

    for tipo, tarifa in tarifas.items():
        if not isinstance(tarifa, dict):
            raise ValueError(f"La tarifa '{tipo}' debe ser un objeto JSON.")
        for clave in CLAVES_TARIFA:
            valor = tarifa.get(clave)
            if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor < 0:
                raise ValueError(f"La tarifa '{clave}' de '{tipo}' debe ser numérica.")

    return configuracion, tarifas


def cargar_movimientos(ruta=ARCHIVO_MOVIMIENTOS):
    datos = cargar_json(ruta)
    if not isinstance(datos, dict):
        raise ValueError("El archivo de movimientos debe contener un objeto JSON.")
    if "fecha_operacion" not in datos or "movimientos" not in datos:
        raise ValueError("El archivo de movimientos debe tener 'fecha_operacion' y 'movimientos'.")
    if not isinstance(datos["movimientos"], list):
        raise ValueError("'movimientos' debe ser una lista.")
    try:
        datetime.strptime(datos["fecha_operacion"], FORMATO_FECHA)
    except (TypeError, ValueError) as error:
        raise ValueError("'fecha_operacion' debe tener formato YYYY-MM-DD.") from error
    return datos
