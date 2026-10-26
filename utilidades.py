from datetime import date, datetime


def formato_pesos(valor):
    return f"$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fecha_hoy():
    return date.today().strftime("%Y-%m-%d")


def generar_id_manual():
    return "MAN-" + datetime.now().strftime("%Y%m%d%H%M%S%f")
