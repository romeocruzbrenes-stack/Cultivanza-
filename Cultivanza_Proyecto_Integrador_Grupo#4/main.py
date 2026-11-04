import tkinter as tk

from gui.login import Login


def main():
    ventana = tk.Tk()
    ventana.title("Cultivanza")
    ventana.geometry("1050x700")
    ventana.minsize(900, 620)
    Login(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()
