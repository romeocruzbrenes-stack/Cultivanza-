from dataclasses import dataclass


@dataclass
class Cliente:
    id_cliente: int
    nombre: str
    correo: str
    tipo_empresa: str
    telefono: str


@dataclass
class Solicitud:
    id_solicitud: int
    id_cliente: int
    titulo_solicitud: str
    descripcion: str
    estado: str = "Pendiente"
    categoria: str = "Otro"
    prioridad: str = "Media"
    fecha: str = ""


@dataclass
class Solucion:
    id_solucion: int
    id_solicitud: int
    titulo: str
    descripcion: str
    estado: str = "Propuesta"
