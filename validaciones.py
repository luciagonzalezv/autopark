import re

from config import PATRON_PATENTE


def normalizar_patente(texto):
    if not isinstance(texto, str):
        return ""
    return re.sub(r"\s+", "", texto).upper()


def patente_valida(patente):
    if not isinstance(patente, str):
        return False
    return re.fullmatch(PATRON_PATENTE, patente) is not None


def normalizar_tipo(texto, tarifas):
    if not isinstance(texto, str):
        return None
    tipo = texto.strip().lower()
    return tipo if tipo in tarifas else None


def parsear_hora(texto):
    if not isinstance(texto, str):
        return None
    texto = texto.strip()
    if re.fullmatch(r"(?:[01]?\d|2[0-3]):[0-5]\d", texto) is None:
        return None
    hora, minuto = texto.split(":")
    return int(hora) * 60 + int(minuto)


def minutos_entre(entrada, salida):
    minutos_entrada = parsear_hora(entrada)
    minutos_salida = parsear_hora(salida)
    if minutos_entrada is None or minutos_salida is None:
        raise ValueError("Hora inválida. Usá HH:MM.")
    if minutos_salida <= minutos_entrada:
        raise ValueError("La salida debe ser posterior a la entrada.")
    return minutos_salida - minutos_entrada


def parsear_dias(texto):
    if isinstance(texto, bool):
        raise ValueError("Días debe ser un entero mayor o igual a 0.")
    if isinstance(texto, int):
        dias = texto
    elif isinstance(texto, str):
        texto = texto.strip()
        if not texto.isdigit():
            raise ValueError("Días debe ser un entero mayor o igual a 0.")
        dias = int(texto)
    else:
        raise ValueError("Días debe ser un entero mayor o igual a 0.")
    if dias < 0:
        raise ValueError("Días debe ser un entero mayor o igual a 0.")
    return dias


def parsear_lavado(texto):
    if isinstance(texto, bool):
        return texto
    if isinstance(texto, str):
        respuesta = texto.strip().lower()
        if respuesta in ("s", "si", "sí", "true", "1"):
            return True
        if respuesta in ("n", "no", "false", "0", ""):
            return False
    raise ValueError("Respuesta de lavado inválida. Usá S o N.")
