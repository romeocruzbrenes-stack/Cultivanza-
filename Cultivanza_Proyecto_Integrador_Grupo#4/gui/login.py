from tkinter import ttk, messagebox

import funciones
from gui.dashboard import DashboardCliente, DashboardAdmin

# Credenciales de prueba del administrador
ADMIN_USUARIO = "admin"
ADMIN_CLAVE = "1234"


class Login:
    def __init__(self, ventana):
        self.ventana = ventana
        self.mostrar()

    def mostrar(self):
        """Dibuja la pantalla de login (también se usa al cerrar sesión)."""
        for widget in self.ventana.winfo_children():
            widget.destroy()
        self.ventana.title("Cultivanza - Iniciar sesión")

        self.marco = ttk.Frame(self.ventana, padding=30)
        self.marco.pack(expand=True)
        ttk.Label(self.marco, text="CULTIVANZA", font=("Arial", 24, "bold")).pack(pady=10)
        ttk.Label(self.marco, text="Tecnología que impulsa el campo").pack(pady=5)

        ttk.Label(self.marco, text="Tipo de usuario").pack(anchor="w")
        self.tipo = ttk.Combobox(self.marco, values=["Cliente", "Administrador"], state="readonly")
        self.tipo.current(0)
        self.tipo.pack(fill="x", pady=5)

        ttk.Label(self.marco, text="Usuario o correo").pack(anchor="w")
        self.usuario = ttk.Entry(self.marco)
        self.usuario.pack(fill="x", pady=5)

        ttk.Label(self.marco, text="Contraseña").pack(anchor="w")
        self.clave = ttk.Entry(self.marco, show="*")
        self.clave.pack(fill="x", pady=5)

        ttk.Button(self.marco, text="Iniciar sesión", command=self.ingresar).pack(fill="x", pady=15)
        ttk.Label(self.marco, text="Cliente: tu correo y cualquier contraseña (prototipo)").pack()
        ttk.Label(self.marco, text="Administrador de prueba: admin / 1234").pack()

    def ingresar(self):
        usuario = self.usuario.get().strip()
        clave = self.clave.get()
        if not usuario or not clave:
            messagebox.showwarning("Aviso", "Usuario y contraseña son obligatorios.")
        elif self.tipo.get() == "Administrador":
            if usuario == ADMIN_USUARIO and clave == ADMIN_CLAVE:
                self.marco.destroy()
                DashboardAdmin(self.ventana, self.mostrar)
            else:
                messagebox.showerror("Error", "Credenciales incorrectas.")
        else:
            error = funciones.validar_correo(usuario)
            if error:
                messagebox.showwarning("Aviso", "Los clientes ingresan con su correo.\n" + error)
            else:
                self.marco.destroy()
                DashboardCliente(self.ventana, self.mostrar, usuario)
