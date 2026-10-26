import tkinter as tk
from tkinter import messagebox, ttk

from calculo import liquidar_estadia
from config import TITULO_VENTANA
from csv_repo import agregar_liquidacion_manual
from utilidades import fecha_hoy, formato_pesos, generar_id_manual
from validaciones import (
    normalizar_patente,
    normalizar_tipo,
    parsear_dias,
    patente_valida,
)


class VentanaCobroManual:
    def __init__(self, root, tarifas, configuracion):
        self.root = root
        self.tarifas = tarifas
        self.configuracion = configuracion
        self.var_patente = tk.StringVar()
        self.var_tipo = tk.StringVar()
        self.var_dias = tk.StringVar(value="0")
        self.var_entrada = tk.StringVar()
        self.var_salida = tk.StringVar()
        self.var_lavado = tk.BooleanVar(value=False)
        self.var_aviso = tk.StringVar(value="")
        self.var_minutos = tk.StringVar(value="—")
        self.var_base = tk.StringVar(value="—")
        self.var_bonificacion = tk.StringVar(value="—")
        self.var_lavado_monto = tk.StringVar(value="—")
        self.var_total = tk.StringVar(value="—")
        self.actualizando = False

        self.construir()
        self.conectar_eventos()
        self.actualizar_estado_horas()
        self.actualizar_total()

    def construir(self):
        self.root.title(TITULO_VENTANA)
        self.root.geometry("540x480")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        estilo = ttk.Style(self.root)
        estilo.configure("Total.TLabel", font=("Segoe UI", 11, "bold"))

        contenedor = ttk.Frame(self.root, padding=14)
        contenedor.grid(row=0, column=0, sticky="nsew")
        contenedor.columnconfigure(0, weight=1)

        datos = ttk.LabelFrame(contenedor, text="Datos del vehículo", padding=10)
        datos.grid(row=0, column=0, sticky="ew")
        datos.columnconfigure(1, weight=1)

        ttk.Label(datos, text="Patente:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_patente = ttk.Entry(datos, textvariable=self.var_patente)
        self.entry_patente.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(datos, text="Tipo:").grid(row=1, column=0, sticky="w", pady=3)
        valores_tipo = sorted(self.tarifas)
        self.combo_tipo = ttk.Combobox(
            datos,
            textvariable=self.var_tipo,
            values=valores_tipo,
            state="readonly",
        )
        self.combo_tipo.grid(row=1, column=1, sticky="ew", pady=3)
        if valores_tipo:
            self.var_tipo.set("auto" if "auto" in self.tarifas else valores_tipo[0])

        ttk.Label(datos, text="Días:").grid(row=2, column=0, sticky="w", pady=3)
        self.spin_dias = ttk.Spinbox(
            datos,
            from_=0,
            to=365,
            textvariable=self.var_dias,
            width=8,
        )
        self.spin_dias.grid(row=2, column=1, sticky="w", pady=3)

        self.label_aviso = ttk.Label(
            datos,
            textvariable=self.var_aviso,
            foreground="#555555",
        )
        self.label_aviso.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 3))

        ttk.Label(datos, text="Hora de entrada:").grid(
            row=4, column=0, sticky="w", pady=3
        )
        self.entry_entrada = ttk.Entry(datos, textvariable=self.var_entrada)
        self.entry_entrada.grid(row=4, column=1, sticky="ew", pady=3)

        ttk.Label(datos, text="Hora de salida:").grid(
            row=5, column=0, sticky="w", pady=3
        )
        self.entry_salida = ttk.Entry(datos, textvariable=self.var_salida)
        self.entry_salida.grid(row=5, column=1, sticky="ew", pady=3)

        self.check_lavado = ttk.Checkbutton(
            datos,
            text="Solicitó servicio de lavado",
            variable=self.var_lavado,
            command=self.actualizar_total,
        )
        self.check_lavado.grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))

        resultado = ttk.LabelFrame(contenedor, text="Resultado", padding=10)
        resultado.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        resultado.columnconfigure(1, weight=1)

        ttk.Label(resultado, text="Tiempo:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(resultado, textvariable=self.var_minutos).grid(
            row=0, column=1, sticky="e", pady=2
        )
        ttk.Label(resultado, text="Base:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(resultado, textvariable=self.var_base).grid(
            row=1, column=1, sticky="e", pady=2
        )
        ttk.Label(resultado, text="Bonificación:").grid(
            row=2, column=0, sticky="w", pady=2
        )
        ttk.Label(resultado, textvariable=self.var_bonificacion).grid(
            row=2, column=1, sticky="e", pady=2
        )
        ttk.Label(resultado, text="Lavado:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(resultado, textvariable=self.var_lavado_monto).grid(
            row=3, column=1, sticky="e", pady=2
        )
        ttk.Label(resultado, text="Total a pagar:", style="Total.TLabel").grid(
            row=4, column=0, sticky="w", pady=(6, 0)
        )
        ttk.Label(
            resultado,
            textvariable=self.var_total,
            style="Total.TLabel",
        ).grid(row=4, column=1, sticky="e", pady=(6, 0))

        botones = ttk.Frame(contenedor)
        botones.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        botones.columnconfigure(0, weight=1)
        ttk.Button(
            botones,
            text="Liquidar y Guardar",
            command=self.liquidar,
        ).grid(row=0, column=0, sticky="w")
        ttk.Button(botones, text="Limpiar", command=self.limpiar).grid(
            row=0, column=1, padx=6
        )
        ttk.Button(botones, text="Cerrar", command=self.root.destroy).grid(
            row=0, column=2
        )

        self.entry_patente.focus_set()

    def conectar_eventos(self):
        self.var_patente.trace_add("write", self.actualizar_total)
        self.var_tipo.trace_add("write", self.actualizar_total)
        self.var_dias.trace_add("write", self._al_cambiar_dias)
        self.var_entrada.trace_add("write", self.actualizar_total)
        self.var_salida.trace_add("write", self.actualizar_total)
        self.entry_patente.bind("<Return>", lambda event: self.liquidar())
        self.entry_entrada.bind("<Return>", lambda event: self.liquidar())
        self.entry_salida.bind("<Return>", lambda event: self.liquidar())

    def _al_cambiar_dias(self, *args):
        self.actualizar_estado_horas()
        self.actualizar_total()

    def actualizar_estado_horas(self):
        try:
            dias = parsear_dias(self.var_dias.get())
        except ValueError:
            dias = 0
        estado = "disabled" if dias > 0 else "normal"
        self.entry_entrada.configure(state=estado)
        self.entry_salida.configure(state=estado)
        if dias > 0:
            self.var_aviso.set("Se liquida por días completos a costo fijo.")
        else:
            self.var_aviso.set("")

    def _leer_formulario(self):
        patente = normalizar_patente(self.var_patente.get())
        if not patente_valida(patente):
            raise ValueError("Patente inválida. Usá ABC123 o AA123BB.")

        tipo = normalizar_tipo(self.var_tipo.get(), self.tarifas)
        if tipo is None:
            raise ValueError("Tipo de vehículo inválido.")

        dias = parsear_dias(self.var_dias.get())
        return {
            "patente": patente,
            "tipo": tipo,
            "dias": dias,
            "entrada": self.var_entrada.get().strip(),
            "salida": self.var_salida.get().strip(),
            "lavado": bool(self.var_lavado.get()),
        }

    def _mostrar_guiones(self):
        self.var_minutos.set("—")
        self.var_base.set("—")
        self.var_bonificacion.set("—")
        self.var_lavado_monto.set("—")
        self.var_total.set("—")

    def actualizar_total(self, *args):
        if self.actualizando:
            return
        self.actualizando = True
        try:
            datos = self._leer_formulario()
            resultado = liquidar_estadia(
                datos["tipo"],
                datos["dias"],
                datos["entrada"],
                datos["salida"],
                datos["lavado"],
                self.tarifas,
                self.configuracion,
            )
        except (ValueError, TypeError):
            self._mostrar_guiones()
            return
        finally:
            self.actualizando = False

        if resultado["dias"] > 0:
            self.var_minutos.set(f"{resultado['dias']} día(s)")
        else:
            self.var_minutos.set(f"{resultado['minutos']} min")
        self.var_base.set(formato_pesos(resultado["base"]))
        self.var_bonificacion.set(formato_pesos(resultado["bonificacion"]))
        self.var_lavado_monto.set(formato_pesos(resultado["lavado"]))
        self.var_total.set(formato_pesos(resultado["total_cobrado"]))

    def liquidar(self):
        try:
            datos = self._leer_formulario()
            resultado = liquidar_estadia(
                datos["tipo"],
                datos["dias"],
                datos["entrada"],
                datos["salida"],
                datos["lavado"],
                self.tarifas,
                self.configuracion,
            )
        except (ValueError, TypeError) as error:
            messagebox.showerror("Datos inválidos", str(error), parent=self.root)
            return

        registro = {
            "id": generar_id_manual(),
            "fecha_operacion": fecha_hoy(),
            "patente": datos["patente"],
            "tipo_vehiculo": datos["tipo"],
            "dias": datos["dias"],
            "entrada": resultado["entrada"],
            "salida": resultado["salida"],
            "minutos": resultado["minutos"],
            "base": resultado["base"],
            "bonificacion": resultado["bonificacion"],
            "lavado": resultado["lavado"],
            "total_cobrado": resultado["total_cobrado"],
        }

        try:
            agregar_liquidacion_manual(registro)
        except OSError as error:
            messagebox.showerror(
                "Error al guardar",
                f"No se pudo guardar el CSV:\n{error}",
                parent=self.root,
            )
            return

        mensaje = (
            f"Patente: {datos['patente']}\n"
            f"Tipo: {datos['tipo']}\n"
            f"Días: {datos['dias']}\n"
        )
        if datos["dias"] == 0:
            mensaje += f"Minutos: {resultado['minutos']}\n"
        mensaje += (
            f"Base: {formato_pesos(resultado['base'])}\n"
            f"Bonificación: {formato_pesos(resultado['bonificacion'])}\n"
            f"Lavado: {formato_pesos(resultado['lavado'])}\n"
            f"Total: {formato_pesos(resultado['total_cobrado'])}"
        )
        messagebox.showinfo("Liquidación registrada", mensaje, parent=self.root)
        self.limpiar()

    def limpiar(self):
        self.var_patente.set("")
        self.var_entrada.set("")
        self.var_salida.set("")
        self.var_dias.set("0")
        self.var_lavado.set(False)
        self.actualizar_estado_horas()
        self.actualizar_total()
        self.entry_patente.focus_set()


def abrir_ventana_manual(tarifas, configuracion):
    root = tk.Tk()
    VentanaCobroManual(root, tarifas, configuracion)
    root.mainloop()
