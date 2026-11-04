from modelos import Cliente, Solicitud, Solucion

# ---------------------------------------------------------------
# Aquí se guarda la información en memoria (RAM) usando listas.
# No hay base de datos: al cerrar el programa, lo que se agregó,
# editó o eliminó se pierde y vuelve a empezar con estos datos.
# Para empezar sin datos de ejemplo, deja las tres listas vacías: []
# ---------------------------------------------------------------

clientes = [
    Cliente(1, "María Gómez", "maria@fincalaesperanza.com", "Productor agrícola", "88881234"),
    Cliente(2, "Carlos Ruiz", "carlos@agroinsumos.com", "Empresa agrícola", "22334455"),
    Cliente(3, "Lucía Pérez", "lucia@coopverde.org", "Cooperativa", "77665544"),
]

solicitudes = [
    Solicitud(1, 1, "Control manual del riego",
              "Hoy anoto el riego en un cuaderno y se me olvidan los turnos de cada lote.",
              "En análisis", "Riego", "Alta", "28/10/2026"),
    Solicitud(2, 2, "Inventario de insumos desordenado",
              "No sabemos cuánto fertilizante queda en bodega hasta que se acaba.",
              "Pendiente", "Inventario e insumos", "Media", "30/10/2026"),
    Solicitud(3, 3, "Seguimiento de la producción",
              "Queremos registrar la cosecha de cada socio y ver totales por temporada.",
              "Pendiente", "Gestión de cultivos", "Media", "01/11/2026"),
]

soluciones = [
    Solucion(1, 1, "Sistema de registro de riego",
             "Aplicación para programar y registrar los turnos de riego por lote.",
             "En desarrollo"),
]

# Siguiente id que se le asignará a cada registro nuevo
# (si dejas las listas vacías, cámbialos a 1)
contador_clientes = 4
contador_solicitudes = 4
contador_soluciones = 2

# Opciones fijas que usan los formularios y las validaciones
TIPOS_CLIENTE = ["Productor agrícola", "Agrónomo", "Empresa agrícola", "Cooperativa", "Otro"]
CATEGORIAS = ["Gestión de cultivos", "Control de plagas", "Riego", "Inventario e insumos",
              "Ventas y comercialización", "Otro"]
PRIORIDADES = ["Baja", "Media", "Alta"]
ESTADOS = ["Pendiente", "En análisis", "Aprobada", "Rechazada", "Finalizada"]
ESTADOS_SOLUCION = ["Propuesta", "En desarrollo", "Entregada"]
