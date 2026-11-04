import tkinter as tk
from tkinter import ttk, messagebox

import datos
import funciones

# Esta pantalla solo captura los eventos de los botones y llama a las
# funciones de funciones.py. Aquí no hay lógica de negocio.


# ===================== FUNCIONES DE APOYO =====================

def crear_tabla(padre, columnas, anchos):
    marco = ttk.Frame(padre)
    marco.pack(fill="both", expand=True, pady=8)
    tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=12)
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    for columna, ancho in zip(columnas, anchos):
        tabla.heading(columna, text=columna)
        tabla.column(columna, width=ancho)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return tabla


def vaciar_tabla(tabla):
    for fila in tabla.get_children():
        tabla.delete(fila)


def id_seleccionado(tabla, mensaje):
    """Devuelve el ID (primera columna) de la fila elegida o None si no hay selección."""
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showwarning("Aviso", mensaje)
        return None
    try:
        return int(tabla.item(seleccion[0], "values")[0])
    except (ValueError, IndexError):
        messagebox.showerror("Error", "No se pudo leer el registro seleccionado.")
        return None


def solo_numeros(valor):
    return valor.isdigit() or valor == ""


def restringir_a_numeros(entrada):
    validar = (entrada.register(solo_numeros), "%P")
    entrada.configure(validate="key", validatecommand=validar)


def texto_detalle(solicitud, con_cliente):
    texto = ""
    if con_cliente:
        cliente = funciones.buscar_cliente(solicitud.id_cliente)
        if cliente is not None:
            texto += (f"Cliente: {cliente.nombre}\nCorreo: {cliente.correo}\n"
                      f"Tipo: {cliente.tipo_empresa}\nTeléfono: {cliente.telefono}\n\n")
    texto += (f"Título: {solicitud.titulo_solicitud}\nCategoría: {solicitud.categoria}\n"
              f"Prioridad: {solicitud.prioridad}\nEstado: {solicitud.estado}\n"
              f"Fecha: {solicitud.fecha}\nDescripción: {solicitud.descripcion}")
    soluciones = funciones.listar_soluciones_de_solicitud(solicitud.id_solicitud)
    if len(soluciones) > 0:
        texto += "\n\nSoluciones:"
        for solucion in soluciones:
            texto += f"\n- {solucion.titulo} ({solucion.estado})"
    else:
        texto += "\n\nAún no hay soluciones asociadas."
    return texto


def abrir_editor_solicitud(ventana, id_solicitud, es_admin, al_guardar):
    """Ventana para editar una solicitud. El cliente no puede cambiar el estado."""
    solicitud = funciones.buscar_solicitud(id_solicitud)
    if solicitud is None:
        messagebox.showerror("Error", "No se encontró la solicitud.")
        return

    editor = tk.Toplevel(ventana)
    editor.title("Editar solicitud")
    editor.geometry("470x440")
    marco = ttk.Frame(editor, padding=15)
    marco.pack(fill="both", expand=True)
    marco.columnconfigure(1, weight=1)

    ttk.Label(marco, text="Título:").grid(row=0, column=0, sticky="w", pady=6)
    titulo = ttk.Entry(marco)
    titulo.grid(row=0, column=1, sticky="ew", pady=6)
    titulo.insert(0, solicitud.titulo_solicitud)

    ttk.Label(marco, text="Categoría:").grid(row=1, column=0, sticky="w", pady=6)
    categoria = ttk.Combobox(marco, values=datos.CATEGORIAS, state="readonly")
    categoria.grid(row=1, column=1, sticky="ew", pady=6)
    categoria.set(solicitud.categoria)

    ttk.Label(marco, text="Prioridad:").grid(row=2, column=0, sticky="w", pady=6)
    prioridad = ttk.Combobox(marco, values=datos.PRIORIDADES, state="readonly")
    prioridad.grid(row=2, column=1, sticky="ew", pady=6)
    prioridad.set(solicitud.prioridad)

    ttk.Label(marco, text="Estado:").grid(row=3, column=0, sticky="w", pady=6)
    estado = ttk.Combobox(marco, values=datos.ESTADOS,
                          state="readonly" if es_admin else "disabled")
    estado.grid(row=3, column=1, sticky="ew", pady=6)
    estado.set(solicitud.estado)

    ttk.Label(marco, text="Descripción:").grid(row=4, column=0, sticky="nw", pady=6)
    descripcion = tk.Text(marco, height=8, wrap="word")
    descripcion.grid(row=4, column=1, sticky="ew", pady=6)
    descripcion.insert("1.0", solicitud.descripcion)

    def guardar():
        try:
            funciones.editar_solicitud(id_solicitud, titulo.get(), descripcion.get("1.0", tk.END),
                                       estado.get(), categoria.get(), prioridad.get())
        except ValueError as error:
            messagebox.showwarning("Revisa los datos", str(error), parent=editor)
        else:
            editor.destroy()
            al_guardar()
            messagebox.showinfo("Cultivanza", "Solicitud actualizada.")

    botones = ttk.Frame(marco)
    botones.grid(row=5, column=0, columnspan=2, pady=12)
    ttk.Button(botones, text="Guardar cambios", command=guardar).pack(side="left", padx=5)
    ttk.Button(botones, text="Cancelar", command=editor.destroy).pack(side="left", padx=5)


# ===================== DASHBOARD DEL CLIENTE =====================

class DashboardCliente:
    def __init__(self, ventana, cerrar_sesion, correo):
        self.ventana = ventana
        self.cerrar_sesion = cerrar_sesion
        self.correo = correo.strip().lower()
        self.marco = ttk.Frame(ventana, padding=18)
        self.marco.pack(fill="both", expand=True)
        self.menu_principal()

    def limpiar(self):
        for widget in self.marco.winfo_children():
            widget.destroy()

    # ---------- menú principal ----------
    def menu_principal(self):
        self.ventana.title("Cultivanza - Menú del cliente")
        self.limpiar()
        cliente = funciones.buscar_cliente_por_correo(self.correo)
        if cliente is not None:
            saludo = "Hola, " + cliente.nombre
        else:
            saludo = "Bienvenido a Cultivanza"
        ttk.Label(self.marco, text=saludo, font=("Arial", 20, "bold")).pack(pady=(40, 5))
        ttk.Label(self.marco, text="Sesión: " + self.correo).pack(pady=5)
        ttk.Label(self.marco, text="¿Qué deseas hacer?").pack(pady=15)
        ttk.Button(self.marco, text="Registrar una necesidad o problema", width=40,
                   command=self.formulario_solicitud).pack(pady=6)
        ttk.Button(self.marco, text="Mis solicitudes", width=40,
                   command=self.mis_solicitudes).pack(pady=6)
        ttk.Button(self.marco, text="Conocer Cultivanza", width=40,
                   command=self.sobre_cultivanza).pack(pady=6)
        ttk.Button(self.marco, text="Cerrar sesión", width=40,
                   command=self.cerrar_sesion).pack(pady=6)

    # ---------- nueva solicitud ----------
    def formulario_solicitud(self):
        self.ventana.title("Cultivanza - Nueva solicitud")
        self.limpiar()
        ttk.Label(self.marco, text="Cuéntanos tu necesidad", font=("Arial", 18, "bold")).pack(pady=8)

        formulario = ttk.Frame(self.marco)
        formulario.pack(fill="x", padx=60)
        formulario.columnconfigure(1, weight=1)

        campos = [("Nombre completo", "nombre"), ("Correo electrónico", "correo"),
                  ("Tipo de cliente", "tipo"), ("Número de teléfono", "telefono"),
                  ("Categoría del problema", "categoria"), ("Prioridad", "prioridad"),
                  ("Título del problema", "titulo")]
        self.entradas = {}
        for fila, (etiqueta, clave) in enumerate(campos):
            ttk.Label(formulario, text=etiqueta + ":").grid(row=fila, column=0, sticky="w", pady=5)
            if clave == "tipo":
                entrada = ttk.Combobox(formulario, values=datos.TIPOS_CLIENTE, state="readonly")
            elif clave == "categoria":
                entrada = ttk.Combobox(formulario, values=datos.CATEGORIAS, state="readonly")
            elif clave == "prioridad":
                entrada = ttk.Combobox(formulario, values=datos.PRIORIDADES, state="readonly")
            else:
                entrada = ttk.Entry(formulario)
            entrada.grid(row=fila, column=1, sticky="ew", pady=5, padx=(10, 0))
            self.entradas[clave] = entrada

        ttk.Label(formulario, text="Descripción:").grid(row=len(campos), column=0, sticky="nw", pady=5)
        self.descripcion = tk.Text(formulario, height=6, wrap="word")
        self.descripcion.grid(row=len(campos), column=1, sticky="ew", pady=5, padx=(10, 0))

        restringir_a_numeros(self.entradas["telefono"])

        # El correo es el de la sesión; si el cliente ya existe, se rellenan sus datos
        self.entradas["correo"].insert(0, self.correo)
        self.entradas["correo"].configure(state="readonly")
        cliente = funciones.buscar_cliente_por_correo(self.correo)
        if cliente is not None:
            self.entradas["nombre"].insert(0, cliente.nombre)
            self.entradas["tipo"].set(cliente.tipo_empresa)
            self.entradas["telefono"].insert(0, cliente.telefono)
        self.entradas["prioridad"].set("Media")

        botones = ttk.Frame(self.marco)
        botones.pack(pady=15)
        ttk.Button(botones, text="Enviar solicitud", command=self.guardar_solicitud).pack(side="left", padx=5)
        ttk.Button(botones, text="Limpiar", command=self.limpiar_formulario).pack(side="left", padx=5)
        ttk.Button(botones, text="Volver al menú", command=self.menu_principal).pack(side="left", padx=5)

    def limpiar_formulario(self):
        for clave, entrada in self.entradas.items():
            if clave == "correo":
                continue  # el correo es el de la sesión y no se borra
            if isinstance(entrada, ttk.Combobox):
                entrada.set("")
            else:
                entrada.delete(0, tk.END)
        self.entradas["prioridad"].set("Media")
        self.descripcion.delete("1.0", tk.END)

    def guardar_solicitud(self):
        valores = {}
        for clave, entrada in self.entradas.items():
            valores[clave] = entrada.get().strip()
        descripcion = self.descripcion.get("1.0", tk.END).strip()
        try:
            funciones.registrar_solicitud(valores["nombre"], valores["correo"], valores["tipo"],
                                          valores["telefono"], valores["titulo"], descripcion,
                                          valores["categoria"], valores["prioridad"])
        except ValueError as error:
            messagebox.showwarning("Revisa los datos", str(error))
        else:
            self.confirmacion()

    def confirmacion(self):
        self.ventana.title("Cultivanza - Solicitud enviada")
        self.limpiar()
        ttk.Label(self.marco, text="¡Solicitud enviada!", font=("Arial", 20, "bold")).pack(pady=(60, 10))
        ttk.Label(self.marco, text="Nuestro equipo analizará tu caso y te propondrá una solución.").pack(pady=5)
        ttk.Button(self.marco, text="Registrar otra solicitud", width=32,
                   command=self.formulario_solicitud).pack(pady=6)
        ttk.Button(self.marco, text="Ver mis solicitudes", width=32,
                   command=self.mis_solicitudes).pack(pady=6)
        ttk.Button(self.marco, text="Volver al menú", width=32,
                   command=self.menu_principal).pack(pady=6)

    # ---------- mis solicitudes ----------
    def mis_solicitudes(self):
        self.ventana.title("Cultivanza - Mis solicitudes")
        self.limpiar()
        ttk.Label(self.marco, text="Mis solicitudes", font=("Arial", 18, "bold")).pack(pady=8)

        columnas = ("ID", "Título", "Categoría", "Prioridad", "Estado", "Fecha", "Soluciones")
        anchos = (40, 230, 150, 80, 100, 90, 80)
        self.tabla = crear_tabla(self.marco, columnas, anchos)
        self.aviso = ttk.Label(self.marco, text="")
        self.aviso.pack()

        botones = ttk.Frame(self.marco)
        botones.pack(pady=10)
        ttk.Button(botones, text="Ver detalle", command=self.ver_detalle).pack(side="left", padx=5)
        ttk.Button(botones, text="Editar", command=self.editar).pack(side="left", padx=5)
        ttk.Button(botones, text="Cancelar solicitud", command=self.eliminar).pack(side="left", padx=5)
        ttk.Button(botones, text="Volver al menú", command=self.menu_principal).pack(side="left", padx=5)
        self.cargar_tabla()

    def cargar_tabla(self):
        vaciar_tabla(self.tabla)
        lista = []
        cliente = funciones.buscar_cliente_por_correo(self.correo)
        if cliente is not None:
            lista = funciones.listar_solicitudes_de_cliente(cliente.id_cliente)
        for s in lista:
            cantidad = len(funciones.listar_soluciones_de_solicitud(s.id_solicitud))
            self.tabla.insert("", tk.END, values=(s.id_solicitud, s.titulo_solicitud, s.categoria,
                                                  s.prioridad, s.estado, s.fecha, cantidad))
        if len(lista) == 0:
            self.aviso.configure(text="Aún no has registrado solicitudes.")
        else:
            self.aviso.configure(text="")

    def solicitud_elegida(self):
        id_solicitud = id_seleccionado(self.tabla, "Selecciona una solicitud.")
        if id_solicitud is None:
            return None
        solicitud = funciones.buscar_solicitud(id_solicitud)
        if solicitud is None:
            messagebox.showerror("Error", "No se encontró la solicitud.")
            self.cargar_tabla()
        return solicitud

    def ver_detalle(self):
        solicitud = self.solicitud_elegida()
        if solicitud is not None:
            messagebox.showinfo("Detalle de la solicitud", texto_detalle(solicitud, False))

    def editar(self):
        solicitud = self.solicitud_elegida()
        if solicitud is None:
            return
        if solicitud.estado != "Pendiente":
            messagebox.showwarning("Aviso", "Solo puedes editar solicitudes en estado Pendiente.")
            return
        abrir_editor_solicitud(self.ventana, solicitud.id_solicitud, False, self.cargar_tabla)

    def eliminar(self):
        solicitud = self.solicitud_elegida()
        if solicitud is None:
            return
        if solicitud.estado != "Pendiente":
            messagebox.showwarning("Aviso", "Solo puedes cancelar solicitudes en estado Pendiente.")
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres cancelar esta solicitud?"):
            return
        try:
            funciones.eliminar_solicitud(solicitud.id_solicitud)
        except ValueError as error:
            messagebox.showwarning("Aviso", str(error))
        else:
            messagebox.showinfo("Cultivanza", "La solicitud fue cancelada.")
        finally:
            self.cargar_tabla()  # la tabla se refresca siempre, haya salido bien o mal

    # ---------- sobre Cultivanza ----------
    def sobre_cultivanza(self):
        self.ventana.title("Cultivanza - Conocer Cultivanza")
        self.limpiar()
        ttk.Label(self.marco, text="¿Cómo funciona Cultivanza?", font=("Arial", 18, "bold")).pack(pady=(30, 10))
        texto = ("Cultivanza conecta a agrónomos, productores y empresas agrícolas\n"
                 "con un equipo que desarrolla software a la medida.\n\n"
                 "1. Cuéntanos tu necesidad, problema o dificultad.\n"
                 "2. Nuestro equipo analiza tu caso.\n"
                 "3. Te proponemos una solución de software adaptada a ti.\n"
                 "4. Desarrollamos, entregamos y damos seguimiento.")
        ttk.Label(self.marco, text=texto, justify="center").pack(pady=10)
        ttk.Button(self.marco, text="Volver al menú", command=self.menu_principal).pack(pady=15)


# ===================== DASHBOARD DEL ADMINISTRADOR =====================

class DashboardAdmin:
    def __init__(self, ventana, cerrar_sesion):
        self.ventana = ventana
        ventana.title("Cultivanza - Administración")
        self.marco = ttk.Frame(ventana, padding=15)
        self.marco.pack(fill="both", expand=True)

        encabezado = ttk.Frame(self.marco)
        encabezado.pack(fill="x", pady=(0, 8))
        ttk.Label(encabezado, text="Panel de administración", font=("Arial", 18, "bold")).pack(side="left")
        ttk.Button(encabezado, text="Cerrar sesión", command=cerrar_sesion).pack(side="right")

        self.pestanas = ttk.Notebook(self.marco)
        self.pestanas.pack(fill="both", expand=True)
        self.tab_resumen = ttk.Frame(self.pestanas, padding=15)
        self.tab_solicitudes = ttk.Frame(self.pestanas, padding=10)
        self.tab_clientes = ttk.Frame(self.pestanas, padding=10)
        self.tab_soluciones = ttk.Frame(self.pestanas, padding=10)
        self.pestanas.add(self.tab_resumen, text="Resumen")
        self.pestanas.add(self.tab_solicitudes, text="Solicitudes")
        self.pestanas.add(self.tab_clientes, text="Clientes")
        self.pestanas.add(self.tab_soluciones, text="Soluciones")

        self.crear_resumen()
        self.crear_solicitudes()
        self.crear_clientes()
        self.crear_soluciones()
        # Al cambiar de pestaña se refrescan los datos que muestra
        self.pestanas.bind("<<NotebookTabChanged>>", self.al_cambiar_pestana)

    def al_cambiar_pestana(self, evento):
        indice = self.pestanas.index("current")
        if indice == 0:
            self.cargar_resumen()
        elif indice == 1:
            self.cargar_solicitudes()
        elif indice == 2:
            self.cargar_clientes()
        else:
            self.cargar_soluciones()

    # ---------------------- RESUMEN ----------------------
    def crear_resumen(self):
        ttk.Label(self.tab_resumen, text="Resumen general", font=("Arial", 14, "bold")).pack(anchor="w")
        self.lbl_totales = ttk.Label(self.tab_resumen, justify="left")
        self.lbl_totales.pack(anchor="w", pady=8)
        ttk.Label(self.tab_resumen, text="Solicitudes por estado", font=("Arial", 12, "bold")).pack(anchor="w")
        self.lbl_estados = ttk.Label(self.tab_resumen, justify="left")
        self.lbl_estados.pack(anchor="w", pady=8)
        ttk.Label(self.tab_resumen, text="Solicitudes por categoría", font=("Arial", 12, "bold")).pack(anchor="w")
        self.lbl_categorias = ttk.Label(self.tab_resumen, justify="left")
        self.lbl_categorias.pack(anchor="w", pady=8)
        self.cargar_resumen()

    def cargar_resumen(self):
        self.lbl_totales.configure(
            text=f"Clientes: {len(funciones.listar_clientes())}\n"
                 f"Solicitudes: {len(funciones.listar_solicitudes())}\n"
                 f"Soluciones: {len(funciones.listar_soluciones())}")
        texto = ""
        for estado, cantidad in funciones.contar_por_estado().items():
            texto += f"- {estado}: {cantidad}\n"
        self.lbl_estados.configure(text=texto)
        texto = ""
        for categoria, cantidad in funciones.contar_por_categoria().items():
            texto += f"- {categoria}: {cantidad}\n"
        self.lbl_categorias.configure(text=texto)

    # ---------------------- SOLICITUDES ----------------------
    def crear_solicitudes(self):
        barra = ttk.Frame(self.tab_solicitudes)
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar (cliente o título):").pack(side="left")
        self.sol_buscar = ttk.Entry(barra, width=22)
        self.sol_buscar.pack(side="left", padx=5)
        ttk.Label(barra, text="Estado:").pack(side="left")
        self.sol_estado = ttk.Combobox(barra, values=["Todos"] + datos.ESTADOS, state="readonly", width=12)
        self.sol_estado.set("Todos")
        self.sol_estado.pack(side="left", padx=5)
        ttk.Label(barra, text="Ordenar por:").pack(side="left")
        self.sol_orden = ttk.Combobox(barra, values=["ID", "Prioridad (alta primero)", "Cliente (A-Z)",
                                                     "Título (A-Z)"], state="readonly", width=22)
        self.sol_orden.set("ID")
        self.sol_orden.pack(side="left", padx=5)
        ttk.Button(barra, text="Aplicar", command=self.aplicar_filtros).pack(side="left", padx=3)
        ttk.Button(barra, text="Mostrar todos", command=self.mostrar_todas_solicitudes).pack(side="left")

        columnas = ("ID", "Cliente", "Correo", "Título", "Categoría", "Prioridad", "Estado", "Fecha")
        anchos = (40, 120, 160, 190, 130, 70, 90, 80)
        self.sol_tabla = crear_tabla(self.tab_solicitudes, columnas, anchos)

        botones = ttk.Frame(self.tab_solicitudes)
        botones.pack(pady=5)
        ttk.Button(botones, text="Ver detalle", command=self.ver_solicitud).pack(side="left", padx=5)
        ttk.Button(botones, text="Editar", command=self.editar_solicitud).pack(side="left", padx=5)
        ttk.Button(botones, text="Cambiar estado", command=self.cambiar_estado).pack(side="left", padx=5)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_solicitud).pack(side="left", padx=5)
        self.cargar_solicitudes()

    def cargar_solicitudes(self):
        """Busca, filtra por estado y ordena según lo elegido, y llena la tabla."""
        estado = self.sol_estado.get()
        filtradas = []
        for s in funciones.buscar_solicitudes(self.sol_buscar.get()):
            if estado == "Todos" or s.estado == estado:
                filtradas.append(s)
        lista = funciones.ordenar_solicitudes(filtradas, self.sol_orden.get())

        vaciar_tabla(self.sol_tabla)
        for s in lista:
            cliente = funciones.buscar_cliente(s.id_cliente)
            nombre = cliente.nombre if cliente is not None else "(sin cliente)"
            correo = cliente.correo if cliente is not None else ""
            self.sol_tabla.insert("", tk.END, values=(s.id_solicitud, nombre, correo, s.titulo_solicitud,
                                                      s.categoria, s.prioridad, s.estado, s.fecha))
        return len(lista)

    def aplicar_filtros(self):
        if self.cargar_solicitudes() == 0:
            messagebox.showinfo("Sin resultados", "No se encontró ninguna solicitud con esos datos.")

    def mostrar_todas_solicitudes(self):
        self.sol_buscar.delete(0, tk.END)
        self.sol_estado.set("Todos")
        self.sol_orden.set("ID")
        self.cargar_solicitudes()

    def solicitud_elegida(self):
        id_solicitud = id_seleccionado(self.sol_tabla, "Selecciona una solicitud.")
        if id_solicitud is None:
            return None
        solicitud = funciones.buscar_solicitud(id_solicitud)
        if solicitud is None:
            messagebox.showerror("Error", "No se encontró la solicitud.")
            self.cargar_solicitudes()
        return solicitud

    def ver_solicitud(self):
        solicitud = self.solicitud_elegida()
        if solicitud is not None:
            messagebox.showinfo("Detalle de la solicitud", texto_detalle(solicitud, True))

    def editar_solicitud(self):
        solicitud = self.solicitud_elegida()
        if solicitud is not None:
            abrir_editor_solicitud(self.ventana, solicitud.id_solicitud, True, self.cargar_solicitudes)

    def cambiar_estado(self):
        solicitud = self.solicitud_elegida()
        if solicitud is None:
            return
        ventana = tk.Toplevel(self.ventana)
        ventana.title("Cambiar estado")
        ventana.geometry("320x160")
        ttk.Label(ventana, text="Nuevo estado:").pack(pady=10)
        combo = ttk.Combobox(ventana, values=datos.ESTADOS, state="readonly")
        combo.pack(pady=5)
        combo.set(solicitud.estado)

        def guardar_estado():
            try:
                funciones.cambiar_estado_solicitud(solicitud.id_solicitud, combo.get())
            except ValueError as error:
                messagebox.showwarning("Aviso", str(error), parent=ventana)
            else:
                ventana.destroy()
                self.cargar_solicitudes()
                messagebox.showinfo("Cultivanza", "El estado se cambió correctamente.")

        ttk.Button(ventana, text="Guardar", command=guardar_estado).pack(pady=10)

    def eliminar_solicitud(self):
        solicitud = self.solicitud_elegida()
        if solicitud is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta solicitud?"):
            return
        try:
            funciones.eliminar_solicitud(solicitud.id_solicitud)
        except ValueError as error:
            messagebox.showwarning("Aviso", str(error))
        else:
            messagebox.showinfo("Cultivanza", "La solicitud fue eliminada.")
        finally:
            self.cargar_solicitudes()

    # ---------------------- CLIENTES ----------------------
    def crear_clientes(self):
        barra = ttk.Frame(self.tab_clientes)
        barra.pack(fill="x")
        ttk.Label(barra, text="Buscar (nombre o correo):").pack(side="left")
        self.cli_buscar = ttk.Entry(barra, width=28)
        self.cli_buscar.pack(side="left", padx=5)
        ttk.Button(barra, text="Buscar", command=self.cargar_clientes).pack(side="left", padx=5)
        ttk.Button(barra, text="Mostrar todos", command=self.mostrar_todos_clientes).pack(side="left")

        columnas = ("ID", "Nombre", "Correo", "Tipo", "Teléfono", "Solicitudes")
        anchos = (40, 170, 210, 140, 100, 80)
        self.cli_tabla = crear_tabla(self.tab_clientes, columnas, anchos)

        botones = ttk.Frame(self.tab_clientes)
        botones.pack(pady=5)
        ttk.Button(botones, text="Nuevo cliente", command=self.nuevo_cliente).pack(side="left", padx=5)
        ttk.Button(botones, text="Editar", command=self.editar_cliente).pack(side="left", padx=5)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_cliente).pack(side="left", padx=5)
        self.cargar_clientes()

    def cargar_clientes(self):
        vaciar_tabla(self.cli_tabla)
        for c in funciones.buscar_clientes(self.cli_buscar.get()):
            cantidad = len(funciones.listar_solicitudes_de_cliente(c.id_cliente))
            self.cli_tabla.insert("", tk.END, values=(c.id_cliente, c.nombre, c.correo,
                                                      c.tipo_empresa, c.telefono, cantidad))

    def mostrar_todos_clientes(self):
        self.cli_buscar.delete(0, tk.END)
        self.cargar_clientes()

    def nuevo_cliente(self):
        self.formulario_cliente(None)

    def editar_cliente(self):
        id_cliente = id_seleccionado(self.cli_tabla, "Selecciona un cliente.")
        if id_cliente is not None:
            self.formulario_cliente(id_cliente)

    def eliminar_cliente(self):
        id_cliente = id_seleccionado(self.cli_tabla, "Selecciona un cliente.")
        if id_cliente is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este cliente?"):
            return
        try:
            funciones.eliminar_cliente(id_cliente)
        except ValueError as error:
            messagebox.showwarning("Aviso", str(error))
        else:
            messagebox.showinfo("Cultivanza", "El cliente fue eliminado.")
        finally:
            self.cargar_clientes()

    def formulario_cliente(self, id_cliente):
        """Si id_cliente es None guarda un cliente nuevo; si no, edita el existente."""
        cliente = None
        if id_cliente is not None:
            cliente = funciones.buscar_cliente(id_cliente)
            if cliente is None:
                messagebox.showerror("Error", "No se encontró el cliente.")
                return

        ventana = tk.Toplevel(self.ventana)
        ventana.title("Nuevo cliente" if cliente is None else "Editar cliente")
        ventana.geometry("430x290")
        marco = ttk.Frame(ventana, padding=15)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(1, weight=1)

        ttk.Label(marco, text="Nombre:").grid(row=0, column=0, sticky="w", pady=6)
        nombre = ttk.Entry(marco)
        nombre.grid(row=0, column=1, sticky="ew", pady=6)
        ttk.Label(marco, text="Correo:").grid(row=1, column=0, sticky="w", pady=6)
        correo = ttk.Entry(marco)
        correo.grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Label(marco, text="Tipo de cliente:").grid(row=2, column=0, sticky="w", pady=6)
        tipo = ttk.Combobox(marco, values=datos.TIPOS_CLIENTE, state="readonly")
        tipo.grid(row=2, column=1, sticky="ew", pady=6)
        ttk.Label(marco, text="Teléfono:").grid(row=3, column=0, sticky="w", pady=6)
        telefono = ttk.Entry(marco)
        telefono.grid(row=3, column=1, sticky="ew", pady=6)
        restringir_a_numeros(telefono)

        if cliente is not None:
            nombre.insert(0, cliente.nombre)
            correo.insert(0, cliente.correo)
            tipo.set(cliente.tipo_empresa)
            telefono.insert(0, cliente.telefono)

        def guardar():
            try:
                if cliente is None:
                    funciones.guardar_cliente(nombre.get(), correo.get(), tipo.get(), telefono.get())
                else:
                    funciones.editar_cliente(id_cliente, nombre.get(), correo.get(),
                                             tipo.get(), telefono.get())
            except ValueError as error:
                messagebox.showwarning("Revisa los datos", str(error), parent=ventana)
            else:
                ventana.destroy()
                self.cargar_clientes()
                messagebox.showinfo("Cultivanza", "Cliente guardado correctamente.")

        botones = ttk.Frame(marco)
        botones.grid(row=4, column=0, columnspan=2, pady=15)
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="left", padx=5)
        ttk.Button(botones, text="Cancelar", command=ventana.destroy).pack(side="left", padx=5)

    # ---------------------- SOLUCIONES ----------------------
    def crear_soluciones(self):
        ttk.Label(self.tab_soluciones, text="Soluciones de software propuestas a cada solicitud").pack(anchor="w")
        columnas = ("ID", "Solicitud", "Cliente", "Solución", "Estado")
        anchos = (40, 220, 140, 230, 100)
        self.sul_tabla = crear_tabla(self.tab_soluciones, columnas, anchos)

        botones = ttk.Frame(self.tab_soluciones)
        botones.pack(pady=5)
        ttk.Button(botones, text="Nueva solución", command=self.nueva_solucion).pack(side="left", padx=5)
        ttk.Button(botones, text="Ver detalle", command=self.ver_solucion).pack(side="left", padx=5)
        ttk.Button(botones, text="Editar", command=self.editar_solucion).pack(side="left", padx=5)
        ttk.Button(botones, text="Eliminar", command=self.eliminar_solucion).pack(side="left", padx=5)
        self.cargar_soluciones()

    def cargar_soluciones(self):
        vaciar_tabla(self.sul_tabla)
        for sol in funciones.listar_soluciones():
            texto_solicitud = ""
            nombre = ""
            solicitud = funciones.buscar_solicitud(sol.id_solicitud)
            if solicitud is not None:
                texto_solicitud = f"#{solicitud.id_solicitud} {solicitud.titulo_solicitud}"
                cliente = funciones.buscar_cliente(solicitud.id_cliente)
                if cliente is not None:
                    nombre = cliente.nombre
            self.sul_tabla.insert("", tk.END, values=(sol.id_solucion, texto_solicitud, nombre,
                                                      sol.titulo, sol.estado))

    def solucion_elegida(self):
        id_solucion = id_seleccionado(self.sul_tabla, "Selecciona una solución.")
        if id_solucion is None:
            return None
        solucion = funciones.buscar_solucion(id_solucion)
        if solucion is None:
            messagebox.showerror("Error", "No se encontró la solución.")
            self.cargar_soluciones()
        return solucion

    def ver_solucion(self):
        sol = self.solucion_elegida()
        if sol is not None:
            messagebox.showinfo("Detalle de la solución",
                                f"Título: {sol.titulo}\nEstado: {sol.estado}\n\nDescripción: {sol.descripcion}")

    def nueva_solucion(self):
        self.formulario_solucion(None)

    def editar_solucion(self):
        sol = self.solucion_elegida()
        if sol is not None:
            self.formulario_solucion(sol)

    def eliminar_solucion(self):
        sol = self.solucion_elegida()
        if sol is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar esta solución?"):
            return
        try:
            funciones.eliminar_solucion(sol.id_solucion)
        except ValueError as error:
            messagebox.showwarning("Aviso", str(error))
        else:
            messagebox.showinfo("Cultivanza", "La solución fue eliminada.")
        finally:
            self.cargar_soluciones()

    def formulario_solucion(self, solucion):
        """Si solucion es None guarda una nueva; si no, edita la existente."""
        opciones = []
        if solucion is None:
            for s in funciones.listar_solicitudes():
                opciones.append(f"{s.id_solicitud} - {s.titulo_solicitud}")
            if len(opciones) == 0:
                messagebox.showinfo("Aviso", "Primero debe existir al menos una solicitud.")
                return

        ventana = tk.Toplevel(self.ventana)
        ventana.title("Nueva solución" if solucion is None else "Editar solución")
        ventana.geometry("500x400")
        marco = ttk.Frame(ventana, padding=15)
        marco.pack(fill="both", expand=True)
        marco.columnconfigure(1, weight=1)

        ttk.Label(marco, text="Solicitud:").grid(row=0, column=0, sticky="w", pady=6)
        if solucion is None:
            combo_solicitud = ttk.Combobox(marco, values=opciones, state="readonly")
            combo_solicitud.grid(row=0, column=1, sticky="ew", pady=6)
        else:
            texto = f"#{solucion.id_solicitud}"
            solicitud = funciones.buscar_solicitud(solucion.id_solicitud)
            if solicitud is not None:
                texto += " " + solicitud.titulo_solicitud
            ttk.Label(marco, text=texto).grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(marco, text="Título:").grid(row=1, column=0, sticky="w", pady=6)
        titulo = ttk.Entry(marco)
        titulo.grid(row=1, column=1, sticky="ew", pady=6)
        ttk.Label(marco, text="Estado:").grid(row=2, column=0, sticky="w", pady=6)
        estado = ttk.Combobox(marco, values=datos.ESTADOS_SOLUCION, state="readonly")
        estado.grid(row=2, column=1, sticky="ew", pady=6)
        estado.set("Propuesta")
        ttk.Label(marco, text="Descripción:").grid(row=3, column=0, sticky="nw", pady=6)
        descripcion = tk.Text(marco, height=8, wrap="word")
        descripcion.grid(row=3, column=1, sticky="ew", pady=6)

        if solucion is not None:
            titulo.insert(0, solucion.titulo)
            estado.set(solucion.estado)
            descripcion.insert("1.0", solucion.descripcion)

        def guardar():
            id_solicitud = None
            if solucion is None:
                try:
                    id_solicitud = int(combo_solicitud.get().split(" - ", 1)[0])
                except ValueError:
                    messagebox.showwarning("Aviso", "Debes seleccionar una solicitud.", parent=ventana)
                    return
            texto_descripcion = descripcion.get("1.0", tk.END)
            try:
                if solucion is None:
                    funciones.guardar_solucion(id_solicitud, titulo.get(), texto_descripcion, estado.get())
                else:
                    funciones.editar_solucion(solucion.id_solucion, titulo.get(),
                                              texto_descripcion, estado.get())
            except ValueError as error:
                messagebox.showwarning("Revisa los datos", str(error), parent=ventana)
            else:
                ventana.destroy()
                self.cargar_soluciones()
                messagebox.showinfo("Cultivanza", "Solución guardada correctamente.")

        botones = ttk.Frame(marco)
        botones.grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="left", padx=5)
        ttk.Button(botones, text="Cancelar", command=ventana.destroy).pack(side="left", padx=5)
