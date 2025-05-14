import tkinter as tk
from controlador import SistemaSeguridadControlador

if __name__ == "__main__":
    root = tk.Tk()
    app = SistemaSeguridadControlador(root)
    root.mainloop()
