from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ARCHIVO_TARIFAS = BASE_DIR / "tarifas.json"
ARCHIVO_MOVIMIENTOS = BASE_DIR / "movimientos.json"
CSV_LIQUIDACION = BASE_DIR / "liquidacion.csv"
CSV_RECHAZADOS = BASE_DIR / "rechazados.csv"
CSV_MANUAL = BASE_DIR / "liquidacion-manual.csv"

SEPARADOR = ","
FORMATO_FECHA = "%Y-%m-%d"
PATRON_PATENTE = r"^(?:[A-Z]{3}\d{3}|[A-Z]{2}\d{3}[A-Z]{2})$"
TITULO_VENTANA = "AutoPark - Cobro Manual"
