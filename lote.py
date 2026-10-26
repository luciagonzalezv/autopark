from calculo import liquidar_estadia
from validaciones import (
    minutos_entre,
    normalizar_patente,
    normalizar_tipo,
    parsear_lavado,
    patente_valida,
)


def procesar_lote(movimientos, tarifas, configuracion, fecha_operacion):
    validos = []
    rechazados = []
    ids_vistos = set()

    for movimiento in movimientos:
        if not isinstance(movimiento, dict):
            rechazados.append(
                {
                    "id": "",
                    "patente": "",
                    "tipo_vehiculo": "",
                    "entrada": "",
                    "salida": "",
                    "motivo": "Movimiento inválido",
                }
            )
            continue

        id_movimiento = movimiento.get("id")
        patente_original = movimiento.get("patente")
        tipo_original = movimiento.get("tipo_vehiculo")
        entrada = movimiento.get("entrada")
        salida = movimiento.get("salida")
        lavado_raw = movimiento.get("solicito_lavado", False)
        motivo = None
        lavado = False

        if not isinstance(id_movimiento, str) or not id_movimiento.strip():
            motivo = "ID inválido"
        elif id_movimiento in ids_vistos:
            motivo = "ID repetido"
        else:
            ids_vistos.add(id_movimiento)

        patente = normalizar_patente(patente_original)
        tipo = normalizar_tipo(tipo_original, tarifas)

        if motivo is None and not patente_valida(patente):
            motivo = "Patente inválida"
        if motivo is None and tipo is None:
            motivo = "Tipo de vehículo inválido"

        if motivo is None:
            if lavado_raw is None:
                lavado = False
            elif isinstance(lavado_raw, bool):
                lavado = lavado_raw
            else:
                try:
                    lavado = parsear_lavado(lavado_raw)
                except ValueError:
                    motivo = "Valor de lavado inválido"

        if motivo is None:
            try:
                minutos_entre(entrada, salida)
            except ValueError as error:
                motivo = str(error)

        if motivo is not None:
            rechazados.append(
                {
                    "id": id_movimiento,
                    "patente": patente_original,
                    "tipo_vehiculo": tipo_original,
                    "entrada": entrada,
                    "salida": salida,
                    "motivo": motivo,
                }
            )
            continue

        resultado = liquidar_estadia(
            tipo,
            0,
            entrada,
            salida,
            lavado,
            tarifas,
            configuracion,
        )
        registro = {
            "id": id_movimiento,
            "fecha_operacion": fecha_operacion,
            "patente": patente,
            "tipo_vehiculo": tipo,
            "entrada": entrada,
            "salida": salida,
            "minutos": resultado["minutos"],
            "base": resultado["base"],
            "bonificacion": resultado["bonificacion"],
            "lavado": resultado["lavado"],
            "total_cobrado": resultado["total_cobrado"],
        }
        validos.append(registro)

    resumen = {
        "procesados": len(validos),
        "rechazados": len(rechazados),
        "total_recaudado": sum(registro["total_cobrado"] for registro in validos),
        "por_tipo": {},
        "lavados": sum(1 for registro in validos if registro["lavado"] > 0),
    }
    for registro in validos:
        tipo = registro["tipo_vehiculo"]
        datos_tipo = resumen["por_tipo"].setdefault(
            tipo, {"cantidad": 0, "total": 0}
        )
        datos_tipo["cantidad"] += 1
        datos_tipo["total"] += registro["total_cobrado"]

    return validos, rechazados, resumen
