import csv

from calculo import liquidar_estadia
from config import CSV_MANUAL
from csv_repo import agregar_liquidacion_manual
from utilidades import fecha_hoy, formato_pesos, generar_id_manual
from validaciones import (
    minutos_entre,
    normalizar_patente,
    normalizar_tipo,
    parsear_dias,
    parsear_hora,
    parsear_lavado,
    patente_valida,
)


def pedir_patente():
    while True:
        patente = normalizar_patente(input("Patente (ABC123 o AA123BB): "))
        if patente_valida(patente):
            return patente
        print("Patente inválida. Usá ABC123 o AA123BB.")


def pedir_tipo(tarifas):
    while True:
        tipo = normalizar_tipo(input("Tipo (auto/moto/camioneta): "), tarifas)
        if tipo is not None:
            return tipo
        print("Tipo de vehículo inválido.")


def pedir_dias():
    while True:
        try:
            return parsear_dias(input("¿Cuántos días pasaron? (0 si es mismo día): "))
        except ValueError as error:
            print(error)


def pedir_hora(mensaje):
    while True:
        texto = input(mensaje)
        minutos = parsear_hora(texto)
        if minutos is None:
            print("Hora inválida. Usá HH:MM.")
            continue
        return f"{minutos // 60:02d}:{minutos % 60:02d}"


def pedir_lavado():
    while True:
        respuesta = input("¿Solicitó lavado? (S/N): ").strip()
        if respuesta == "":
            print("Ingresá S o N.")
            continue
        try:
            return parsear_lavado(respuesta)
        except ValueError as error:
            print(error)


def registrar_cobro(tarifas, configuracion):
    print("\n--- Registro de cobro manual ---")
    try:
        patente = pedir_patente()
        tipo = pedir_tipo(tarifas)
        dias = pedir_dias()

        if dias > 0:
            print("Se liquidará por días completos a costo fijo.")
            entrada = ""
            salida = ""
        else:
            entrada = pedir_hora("Hora de entrada (HH:MM): ")
            salida = pedir_hora("Hora de salida (HH:MM): ")
            try:
                minutos_entre(entrada, salida)
            except ValueError as error:
                print(f"Error: {error}")
                return

        lavado = pedir_lavado()
        resultado = liquidar_estadia(
            tipo,
            dias,
            entrada,
            salida,
            lavado,
            tarifas,
            configuracion,
        )
    except ValueError as error:
        print(f"Error: {error}")
        return

    registro = {
        "id": generar_id_manual(),
        "fecha_operacion": fecha_hoy(),
        "patente": patente,
        "tipo_vehiculo": tipo,
        "dias": dias,
        "entrada": resultado["entrada"],
        "salida": resultado["salida"],
        "minutos": resultado["minutos"],
        "base": resultado["base"],
        "bonificacion": resultado["bonificacion"],
        "lavado": resultado["lavado"],
        "total_cobrado": resultado["total_cobrado"],
    }

    print("\n--- Desglose de la liquidación ---")
    print(f"Patente: {patente}")
    print(f"Tipo: {tipo}")
    print(f"Días: {dias}")
    if dias == 0:
        print(f"Minutos: {resultado['minutos']}")
    print(f"Base: {formato_pesos(resultado['base'])}")
    print(f"Bonificación: {formato_pesos(resultado['bonificacion'])}")
    print(f"Lavado: {formato_pesos(resultado['lavado'])}")
    print(f"Total a pagar: {formato_pesos(resultado['total_cobrado'])}")

    try:
        agregar_liquidacion_manual(registro)
    except OSError as error:
        print(f"No se pudo guardar el registro: {error}")
        return

    print("Registro guardado en liquidacion-manual.csv.")


def consultar_liquidaciones():
    if not CSV_MANUAL.exists() or CSV_MANUAL.stat().st_size == 0:
        print("No hay liquidaciones manuales registradas.")
        return

    try:
        with open(CSV_MANUAL, "r", newline="", encoding="utf-8") as archivo:
            filas = list(csv.DictReader(archivo))
    except OSError as error:
        print(f"No se pudo leer el archivo: {error}")
        return

    if not filas:
        print("No hay liquidaciones manuales registradas.")
        return

    print("\n--- Últimas liquidaciones manuales ---")
    print(f"{'ID':<28} {'Patente':<10} {'Tipo':<10} {'Días':<5} {'Total':>12}")
    for fila in filas[-10:]:
        total = formato_pesos(fila.get("total_cobrado", 0))
        print(
            f"{fila.get('id', ''):<28} "
            f"{fila.get('patente', ''):<10} "
            f"{fila.get('tipo_vehiculo', ''):<10} "
            f"{fila.get('dias', ''):<5} "
            f"{total:>12}"
        )
