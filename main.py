import sys

from csv_repo import escribir_liquidacion, escribir_rechazados
from json_repo import cargar_movimientos, cargar_tarifas
from lote import procesar_lote
from manual_consola import consultar_liquidaciones, registrar_cobro
from utilidades import formato_pesos

def configurar_consola():
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except (AttributeError, OSError):
            pass
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


configurar_consola()

SEPARADOR_MENU = "=" * 50


def menu_manual(tarifas, configuracion):
    while True:
        print("\n--- Cobro manual ---")
        print("1. Registrar cobro con ventana gráfica")
        print("2. Registrar cobro por consola")
        print("3. Consultar liquidaciones manuales")
        print("4. Volver")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                from gui_manual import abrir_ventana_manual
            except ImportError:
                print("GUI no disponible. Usá la opción 2.")
                continue
            try:
                abrir_ventana_manual(tarifas, configuracion)
            except Exception as error:
                print(f"No se pudo abrir la ventana: {error}")
        elif opcion == "2":
            registrar_cobro(tarifas, configuracion)
        elif opcion == "3":
            consultar_liquidaciones()
        elif opcion == "4":
            break
        else:
            print("Opción inválida. Ingrese 1, 2, 3 o 4.")


def procesar_lote_menu(tarifas, configuracion):
    try:
        datos = cargar_movimientos()
    except (OSError, ValueError) as error:
        print(f"Error al cargar movimientos.json: {error}")
        return

    validos, rechazados, resumen = procesar_lote(
        datos["movimientos"],
        tarifas,
        configuracion,
        datos["fecha_operacion"],
    )

    try:
        escribir_liquidacion(validos)
        escribir_rechazados(rechazados)
    except OSError as error:
        print(f"Error al escribir los CSV: {error}")
        return

    print("\n--- Resumen del lote ---")
    print(f"Procesados: {resumen['procesados']}")
    print(f"Rechazados: {resumen['rechazados']}")
    print(f"Total recaudado: {formato_pesos(resumen['total_recaudado'])}")
    for tipo in sorted(resumen["por_tipo"]):
        datos_tipo = resumen["por_tipo"][tipo]
        print(
            f"  {tipo.capitalize()}: {datos_tipo['cantidad']} "
            f"-> {formato_pesos(datos_tipo['total'])}"
        )
    print(f"  Lavados: {resumen['lavados']}")

    if rechazados:
        print("\n--- Movimientos rechazados ---")
        for registro in rechazados:
            print(
                f"  {registro['id']} | {registro['patente']} | "
                f"{registro['motivo']}"
            )

    print(
        f"\nArchivos generados: liquidacion.csv ({len(validos)}) "
        f"y rechazados.csv ({len(rechazados)})"
    )


def main():
    try:
        configuracion, tarifas = cargar_tarifas()
    except (OSError, ValueError) as error:
        print(f"Error al cargar tarifas.json: {error}")
        return 1

    while True:
        print(f"\n{SEPARADOR_MENU}")
        print("SISTEMA DE GESTIÓN DE ESTACIONAMIENTO AUTOPARK")
        print(SEPARADOR_MENU)
        print("1. Registrar / Consultar cobro manual")
        print("2. Procesar lote de movimientos (JSON -> CSV)")
        print("3. Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            menu_manual(tarifas, configuracion)
        elif opcion == "2":
            procesar_lote_menu(tarifas, configuracion)
        elif opcion == "3":
            print("Hasta luego.")
            return 0
        else:
            print("Opción inválida. Ingrese 1, 2 o 3.")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo...")
        raise SystemExit(0)
