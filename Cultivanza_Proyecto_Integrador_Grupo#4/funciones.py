from datetime import date

import datos
from modelos import Cliente, Solicitud, Solucion

# Toda la lógica del programa está aquí: validaciones, CRUD (guardar, editar,
# buscar, listar, eliminar), búsqueda, ordenamiento y conteos.
# Cuando algo sale mal, las funciones lanzan ValueError con un mensaje claro;
# la interfaz (gui) lo captura con try/except y se lo muestra al usuario.


# ======================= VALIDACIONES =======================
# Devuelven "" si el dato es correcto o un texto con el error.

def primer_error(*errores):
    for error in errores:
        if error:
            return error
    return ""


def validar_texto(valor, campo, minimo, maximo):
    valor = valor.strip()
    if not valor:
        return f"El campo {campo} es obligatorio."
    if len(valor) < minimo:
        return f"El campo {campo} debe tener al menos {minimo} caracteres."
    if len(valor) > maximo:
        return f"El campo {campo} no puede superar los {maximo} caracteres."
    return ""


def validar_opcion(valor, opciones, campo):
    if not valor.strip():
        return f"Debes seleccionar una opción en {campo}."
    if valor not in opciones:
        return f"La opción elegida para {campo} no es válida."
    return ""


def validar_nombre(nombre):
    error = validar_texto(nombre, "nombre", 3, 60)
    if error:
        return error
    for letra in nombre:
        if letra.isdigit():
            return "El nombre no debe contener números."
    return ""


def validar_correo(correo):
    correo = correo.strip()
    if not correo:
        return "El campo correo es obligatorio."
    if " " in correo or correo.count("@") != 1:
        return "El correo electrónico no es válido."
    usuario, dominio = correo.split("@")
    if not usuario or "." not in dominio or dominio.startswith(".") or dominio.endswith("."):
        return "El correo electrónico no es válido."
    return ""


def validar_telefono(telefono):
    telefono = telefono.strip()
    if not telefono:
        return "El campo teléfono es obligatorio."
    if not telefono.isdigit():
        return "El teléfono debe contener solo números."
    if len(telefono) < 7 or len(telefono) > 15:
        return "El teléfono debe tener entre 7 y 15 dígitos."
    return ""


def validar_cliente(nombre, correo, tipo_empresa, telefono):
    return primer_error(
        validar_nombre(nombre),
        validar_correo(correo),
        validar_opcion(tipo_empresa, datos.TIPOS_CLIENTE, "tipo de cliente"),
        validar_telefono(telefono),
    )


def validar_solicitud(titulo, descripcion, categoria, prioridad):
    return primer_error(
        validar_texto(titulo, "título", 5, 80),
        validar_texto(descripcion, "descripción", 10, 500),
        validar_opcion(categoria, datos.CATEGORIAS, "categoría"),
        validar_opcion(prioridad, datos.PRIORIDADES, "prioridad"),
    )


def validar_solucion(titulo, descripcion, estado):
    return primer_error(
        validar_texto(titulo, "título", 5, 80),
        validar_texto(descripcion, "descripción", 10, 500),
        validar_opcion(estado, datos.ESTADOS_SOLUCION, "estado"),
    )


# ======================= CLIENTES =======================

def listar_clientes():
    return datos.clientes


def buscar_cliente(id_cliente):
    """Búsqueda secuencial: recorre la lista hasta encontrar el id."""
    for cliente in datos.clientes:
        if cliente.id_cliente == id_cliente:
            return cliente
    return None


def buscar_cliente_por_correo(correo):
    correo = correo.strip().lower()
    for cliente in datos.clientes:
        if cliente.correo == correo:
            return cliente
    return None


def buscar_clientes(palabra):
    """Devuelve los clientes cuyo nombre o correo contienen la palabra."""
    palabra = palabra.strip().lower()
    encontrados = []
    for cliente in datos.clientes:
        if palabra in cliente.nombre.lower() or palabra in cliente.correo:
            encontrados.append(cliente)
    return encontrados


def guardar_cliente(nombre, correo, tipo_empresa, telefono):
    error = validar_cliente(nombre, correo, tipo_empresa, telefono)
    if error:
        raise ValueError(error)
    if buscar_cliente_por_correo(correo) is not None:
        raise ValueError("Ya existe un cliente con ese correo.")
    cliente = Cliente(datos.contador_clientes, nombre.strip(), correo.strip().lower(),
                      tipo_empresa.strip(), telefono.strip())
    datos.contador_clientes += 1
    datos.clientes.append(cliente)
    return cliente


def editar_cliente(id_cliente, nombre, correo, tipo_empresa, telefono):
    cliente = buscar_cliente(id_cliente)
    if cliente is None:
        raise ValueError("No se encontró el cliente.")
    error = validar_cliente(nombre, correo, tipo_empresa, telefono)
    if error:
        raise ValueError(error)
    otro = buscar_cliente_por_correo(correo)
    if otro is not None and otro.id_cliente != id_cliente:
        raise ValueError("Ya existe otro cliente con ese correo.")
    cliente.nombre = nombre.strip()
    cliente.correo = correo.strip().lower()
    cliente.tipo_empresa = tipo_empresa.strip()
    cliente.telefono = telefono.strip()


def eliminar_cliente(id_cliente):
    cliente = buscar_cliente(id_cliente)
    if cliente is None:
        raise ValueError("No se encontró el cliente.")
    if len(listar_solicitudes_de_cliente(id_cliente)) > 0:
        raise ValueError("No se puede eliminar: el cliente tiene solicitudes registradas.\n"
                         "Elimina primero sus solicitudes.")
    datos.clientes.remove(cliente)


# ====================== SOLICITUDES ======================

def listar_solicitudes():
    return datos.solicitudes


def listar_solicitudes_de_cliente(id_cliente):
    resultado = []
    for solicitud in datos.solicitudes:
        if solicitud.id_cliente == id_cliente:
            resultado.append(solicitud)
    return resultado


def buscar_solicitud(id_solicitud):
    for solicitud in datos.solicitudes:
        if solicitud.id_solicitud == id_solicitud:
            return solicitud
    return None


def buscar_solicitudes(palabra):
    """Busca por nombre del cliente o por título. Con texto vacío devuelve todas."""
    palabra = palabra.strip().lower()
    encontradas = []
    for solicitud in datos.solicitudes:
        cliente = buscar_cliente(solicitud.id_cliente)
        nombre = cliente.nombre.lower() if cliente is not None else ""
        if palabra in nombre or palabra in solicitud.titulo_solicitud.lower():
            encontradas.append(solicitud)
    return encontradas


def guardar_solicitud(id_cliente, titulo, descripcion, categoria, prioridad):
    if buscar_cliente(id_cliente) is None:
        raise ValueError("No se encontró el cliente de la solicitud.")
    error = validar_solicitud(titulo, descripcion, categoria, prioridad)
    if error:
        raise ValueError(error)
    solicitud = Solicitud(datos.contador_solicitudes, id_cliente, titulo.strip(),
                          descripcion.strip(), "Pendiente", categoria, prioridad,
                          date.today().strftime("%d/%m/%Y"))
    datos.contador_solicitudes += 1
    datos.solicitudes.append(solicitud)
    return solicitud


def registrar_solicitud(nombre, correo, tipo_empresa, telefono, titulo, descripcion,
                        categoria, prioridad):
    """Formulario del cliente: valida todo y, si el correo ya existe, reutiliza al cliente."""
    error = primer_error(
        validar_cliente(nombre, correo, tipo_empresa, telefono),
        validar_solicitud(titulo, descripcion, categoria, prioridad),
    )
    if error:
        raise ValueError(error)
    cliente = buscar_cliente_por_correo(correo)
    if cliente is None:
        cliente = guardar_cliente(nombre, correo, tipo_empresa, telefono)
    return guardar_solicitud(cliente.id_cliente, titulo, descripcion, categoria, prioridad)


def editar_solicitud(id_solicitud, titulo, descripcion, estado, categoria, prioridad):
    solicitud = buscar_solicitud(id_solicitud)
    if solicitud is None:
        raise ValueError("No se encontró la solicitud.")
    error = primer_error(
        validar_solicitud(titulo, descripcion, categoria, prioridad),
        validar_opcion(estado, datos.ESTADOS, "estado"),
    )
    if error:
        raise ValueError(error)
    solicitud.titulo_solicitud = titulo.strip()
    solicitud.descripcion = descripcion.strip()
    solicitud.estado = estado
    solicitud.categoria = categoria
    solicitud.prioridad = prioridad


def cambiar_estado_solicitud(id_solicitud, estado):
    solicitud = buscar_solicitud(id_solicitud)
    if solicitud is None:
        raise ValueError("No se encontró la solicitud.")
    error = validar_opcion(estado, datos.ESTADOS, "estado")
    if error:
        raise ValueError(error)
    solicitud.estado = estado


def eliminar_solicitud(id_solicitud):
    solicitud = buscar_solicitud(id_solicitud)
    if solicitud is None:
        raise ValueError("No se encontró la solicitud.")
    if len(listar_soluciones_de_solicitud(id_solicitud)) > 0:
        raise ValueError("No se puede eliminar: la solicitud tiene soluciones asociadas.\n"
                         "Elimina primero esas soluciones.")
    datos.solicitudes.remove(solicitud)


# ---------------------- ORDENAMIENTO ----------------------

def valor_para_ordenar(solicitud, criterio):
    """Devuelve el dato por el cual se compara cada solicitud."""
    if criterio == "Prioridad (alta primero)":
        # Alta = 0, Media = 1, Baja = 2
        return len(datos.PRIORIDADES) - 1 - datos.PRIORIDADES.index(solicitud.prioridad)
    if criterio == "Cliente (A-Z)":
        cliente = buscar_cliente(solicitud.id_cliente)
        return cliente.nombre.lower() if cliente is not None else ""
    if criterio == "Título (A-Z)":
        return solicitud.titulo_solicitud.lower()
    return solicitud.id_solicitud


def ordenar_solicitudes(lista, criterio):
    """Ordenamiento burbuja. Devuelve una copia ordenada; la lista original no cambia."""
    ordenada = list(lista)
    cantidad = len(ordenada)
    for i in range(cantidad - 1):
        for j in range(cantidad - 1 - i):
            if valor_para_ordenar(ordenada[j], criterio) > valor_para_ordenar(ordenada[j + 1], criterio):
                auxiliar = ordenada[j]
                ordenada[j] = ordenada[j + 1]
                ordenada[j + 1] = auxiliar
    return ordenada


# ---------------------- CONTEOS (para el resumen) ----------------------

def contar_por_estado():
    conteo = {}
    for estado in datos.ESTADOS:
        conteo[estado] = 0
    for solicitud in datos.solicitudes:
        conteo[solicitud.estado] += 1
    return conteo


def contar_por_categoria():
    conteo = {}
    for categoria in datos.CATEGORIAS:
        conteo[categoria] = 0
    for solicitud in datos.solicitudes:
        conteo[solicitud.categoria] += 1
    return conteo


# ======================= SOLUCIONES =======================

def listar_soluciones():
    return datos.soluciones


def listar_soluciones_de_solicitud(id_solicitud):
    resultado = []
    for solucion in datos.soluciones:
        if solucion.id_solicitud == id_solicitud:
            resultado.append(solucion)
    return resultado


def buscar_solucion(id_solucion):
    for solucion in datos.soluciones:
        if solucion.id_solucion == id_solucion:
            return solucion
    return None


def guardar_solucion(id_solicitud, titulo, descripcion, estado):
    if buscar_solicitud(id_solicitud) is None:
        raise ValueError("No se encontró la solicitud a la que pertenece la solución.")
    error = validar_solucion(titulo, descripcion, estado)
    if error:
        raise ValueError(error)
    solucion = Solucion(datos.contador_soluciones, id_solicitud, titulo.strip(),
                        descripcion.strip(), estado)
    datos.contador_soluciones += 1
    datos.soluciones.append(solucion)
    return solucion


def editar_solucion(id_solucion, titulo, descripcion, estado):
    solucion = buscar_solucion(id_solucion)
    if solucion is None:
        raise ValueError("No se encontró la solución.")
    error = validar_solucion(titulo, descripcion, estado)
    if error:
        raise ValueError(error)
    solucion.titulo = titulo.strip()
    solucion.descripcion = descripcion.strip()
    solucion.estado = estado


def eliminar_solucion(id_solucion):
    solucion = buscar_solucion(id_solucion)
    if solucion is None:
        raise ValueError("No se encontró la solución.")
    datos.soluciones.remove(solucion)
