import csv
import tempfile
from pathlib import Path

from calculo import (
    calcular_estacionamiento,
    calcular_estacionamiento_recursivo,
    calcular_excedente,
    liquidar_estadia,
)
from csv_repo import (
    agregar_liquidacion_manual,
    escribir_liquidacion,
    escribir_rechazados,
)
from json_repo import cargar_movimientos, cargar_tarifas
from lote import procesar_lote
from utilidades import formato_pesos
from validaciones import (
    minutos_entre,
    normalizar_patente,
    normalizar_tipo,
    parsear_dias,
    parsear_hora,
    parsear_lavado,
    patente_valida,
)


def ejecutar_pruebas():
    configuracion, tarifas = cargar_tarifas()

    assert normalizar_patente(" BF 901 GG ") == "BF901GG"
    assert normalizar_patente("aa123bb") == "AA123BB"
    assert patente_valida("ABC123")
    assert patente_valida("AA123BB")
    assert not patente_valida("PATENTE99")
    assert not patente_valida("AB1234")

    assert normalizar_tipo(" MOTO ", tarifas) == "moto"
    assert normalizar_tipo("AUTO", tarifas) == "auto"
    assert normalizar_tipo(" camioneta", tarifas) == "camioneta"
    assert normalizar_tipo("tractor", tarifas) is None

    assert parsear_hora("8:00") == 480
    assert parsear_hora("08:00") == 480
    assert parsear_hora("23:59") == 1439
    assert parsear_hora("24:00") is None
    assert parsear_hora("08:60") is None
    assert minutos_entre("08:00", "09:15") == 75
    assert minutos_entre("23:00", "23:30") == 30

    assert parsear_dias("0") == 0
    assert parsear_dias("2") == 2
    assert parsear_dias(3) == 3
    try:
        parsear_dias("-1")
        raise AssertionError("Días negativos debe rechazarlos")
    except ValueError:
        pass

    assert parsear_lavado("S") is True
    assert parsear_lavado("si") is True
    assert parsear_lavado("N") is False
    assert parsear_lavado("no") is False
    assert parsear_lavado(True) is True

    assert formato_pesos(7400) == "$ 7.400,00"
    assert formato_pesos(129000) == "$ 129.000,00"

    assert calcular_estacionamiento_recursivo(135, "auto", tarifas, configuracion) == 4000
    assert calcular_estacionamiento(210, "auto", tarifas, configuracion) == 5200
    assert calcular_estacionamiento(1000, "auto", tarifas, configuracion) == 16000
    assert calcular_excedente(210, "auto", tarifas, configuracion) == 2400
    assert calcular_excedente(120, "auto", tarifas, configuracion) == 0

    resultado = liquidar_estadia(
        "auto", 0, "09:00", "12:30", True, tarifas, configuracion
    )
    assert resultado["minutos"] == 210
    assert resultado["base"] == 5200
    assert resultado["bonificacion"] == 2800
    assert resultado["lavado"] == 5000
    assert resultado["total_cobrado"] == 7400

    resultado = liquidar_estadia(
        "moto", 0, "08:10", "08:55", True, tarifas, configuracion
    )
    assert resultado["base"] == 800
    assert resultado["bonificacion"] == 800
    assert resultado["total_cobrado"] == 2500

    resultado = liquidar_estadia(
        "camioneta", 2, "", "", True, tarifas, configuracion
    )
    assert resultado["base"] == 48000
    assert resultado["bonificacion"] == 0
    assert resultado["minutos"] == 2880
    assert resultado["total_cobrado"] == 55500

    datos = cargar_movimientos()
    validos, rechazados, resumen = procesar_lote(
        datos["movimientos"],
        tarifas,
        configuracion,
        datos["fecha_operacion"],
    )
    assert len(validos) == 30
    assert len(rechazados) == 3
    assert resumen["procesados"] == 30
    assert resumen["rechazados"] == 3
    assert resumen["total_recaudado"] == 129000
    assert resumen["lavados"] == 13
    assert resumen["por_tipo"]["auto"] == {"cantidad": 13, "total": 49500}
    assert resumen["por_tipo"]["moto"] == {"cantidad": 8, "total": 14600}
    assert resumen["por_tipo"]["camioneta"] == {"cantidad": 9, "total": 64900}
    assert {registro["id"] for registro in rechazados} == {
        "MOV031",
        "MOV032",
        "MOV033",
    }
    assert all(registro["tipo_vehiculo"] in tarifas for registro in validos)
    assert any(registro["patente"] == "BF901GG" for registro in validos)

    with tempfile.TemporaryDirectory() as temporal:
        ruta = Path(temporal)

        ruta_liquidacion = ruta / "liquidacion.csv"
        escribir_liquidacion(validos, ruta_liquidacion)
        with open(ruta_liquidacion, "r", newline="", encoding="utf-8") as archivo:
            filas = list(csv.DictReader(archivo))
        assert len(filas) == 30
        assert filas[0]["id"] == "MOV001"
        assert filas[0]["total_cobrado"] == "700.00"

        ruta_rechazados = ruta / "rechazados.csv"
        escribir_rechazados(rechazados, ruta_rechazados)
        with open(ruta_rechazados, "r", newline="", encoding="utf-8") as archivo:
            filas = list(csv.DictReader(archivo))
        assert len(filas) == 3

        ruta_manual = ruta / "liquidacion-manual.csv"
        registro_manual = dict(validos[4])
        registro_manual["id"] = "MAN-TEST-1"
        registro_manual["dias"] = 0
        agregar_liquidacion_manual(registro_manual, ruta_manual)
        registro_manual["id"] = "MAN-TEST-2"
        agregar_liquidacion_manual(registro_manual, ruta_manual)
        with open(ruta_manual, "r", newline="", encoding="utf-8") as archivo:
            filas = list(csv.DictReader(archivo))
        assert len(filas) == 2
        assert filas[0]["id"] == "MAN-TEST-1"
        assert filas[1]["id"] == "MAN-TEST-2"
        assert filas[0]["total_cobrado"] == "7400.00"

    print("Todas las pruebas pasaron.")


if __name__ == "__main__":
    ejecutar_pruebas()
