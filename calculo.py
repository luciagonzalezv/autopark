from validaciones import minutos_entre, parsear_dias, parsear_lavado


def calcular_estacionamiento_recursivo(
    minutos_restantes,
    tipo,
    tarifas,
    configuracion,
    minutos_tarifados=0,
):
    if tipo not in tarifas:
        raise ValueError("Tipo de vehículo inválido.")
    if minutos_restantes <= 0:
        return 0

    tarifa = tarifas[tipo]
    bloque = configuracion["minutos_bloque_inicial"]
    limite = configuracion["minutos_limite_primer_tramo"]
    hora = configuracion["minutos_hora_adicional"]

    if minutos_tarifados < limite:
        return tarifa["precio_bloque_30min"] + calcular_estacionamiento_recursivo(
            minutos_restantes - bloque,
            tipo,
            tarifas,
            configuracion,
            minutos_tarifados + bloque,
        )

    return tarifa["precio_hora_adicional"] + calcular_estacionamiento_recursivo(
        minutos_restantes - hora,
        tipo,
        tarifas,
        configuracion,
        minutos_tarifados + hora,
    )


def calcular_estacionamiento(minutos, tipo, tarifas, configuracion):
    if tipo not in tarifas:
        raise ValueError("Tipo de vehículo inválido.")
    if minutos <= 0:
        return 0
    total = calcular_estacionamiento_recursivo(minutos, tipo, tarifas, configuracion)
    return min(total, tarifas[tipo]["tope_dia"])


def calcular_excedente(minutos, tipo, tarifas, configuracion):
    limite = configuracion["minutos_limite_primer_tramo"]
    if minutos <= limite:
        return 0
    total = calcular_estacionamiento_recursivo(
        minutos - limite,
        tipo,
        tarifas,
        configuracion,
        minutos_tarifados=limite,
    )
    return min(total, tarifas[tipo]["tope_dia"])


def liquidar_estadia(tipo, dias, entrada, salida, lavado, tarifas, configuracion):
    if tipo not in tarifas:
        raise ValueError("Tipo de vehículo inválido.")

    dias = parsear_dias(dias)
    lavado = parsear_lavado(lavado)

    if dias > 0:
        base = dias * tarifas[tipo]["tope_dia"]
        minutos = dias * configuracion["minutos_dia_completo"]
        estacionamiento_cobrado = base
        bonificacion = 0
        entrada_registro = ""
        salida_registro = ""
    else:
        minutos = minutos_entre(entrada, salida)
        base = calcular_estacionamiento(minutos, tipo, tarifas, configuracion)
        if lavado and minutos <= configuracion["minutos_limite_primer_tramo"]:
            estacionamiento_cobrado = 0
        elif lavado:
            estacionamiento_cobrado = calcular_excedente(
                minutos, tipo, tarifas, configuracion
            )
        else:
            estacionamiento_cobrado = base
        bonificacion = base - estacionamiento_cobrado
        entrada_registro = entrada
        salida_registro = salida

    valor_lavado = tarifas[tipo]["precio_lavado"] if lavado else 0
    total_cobrado = estacionamiento_cobrado + valor_lavado

    return {
        "dias": dias,
        "minutos": minutos,
        "base": base,
        "bonificacion": bonificacion,
        "lavado": valor_lavado,
        "total_cobrado": total_cobrado,
        "entrada": entrada_registro,
        "salida": salida_registro,
    }
