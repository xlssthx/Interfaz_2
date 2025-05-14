import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import datetime

class SistemaSeguridadVista:
    def __init__(self, root):
        """Inicializa la interfaz gráfica del sistema de seguridad."""
        self.root = root
        self.root.title("Sistema de Seguridad con IA")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f0f0f0")

        # Variables de control
        self.threshold_var = tk.IntVar(value=70)
        self.video_captures = {}

        # Título principal
        self.titulo_principal = tk.Label(
            root, 
            text="Sistema de Seguridad con Visión por Computadora e IA", 
            font=("Arial", 16, "bold"),
            bg="#f0f0f0"
        )
        self.titulo_principal.pack(pady=10, anchor="w", padx=20)

        # Contenedor de estado del sistema (lado derecho superior)
        self.frame_estado = tk.Frame(root, bg="#f0f0f0")
        self.frame_estado.place(relx=0.99, rely=0.06, anchor="e")
        
        self.label_estado = tk.Label(
            self.frame_estado, 
            text="Estado: En mantenimiento", 
            font=("Arial", 12, "bold"), 
            fg="red",
            bg="#f0f0f0"
        )
        self.label_estado.pack()

        # Controles
        self.frame_controles = tk.Frame(root, bg="#f0f0f0")
        self.frame_controles.pack(fill="x", padx=20, pady=5)
        
        # Botones
        self.btn_iniciar = tk.Button(
            self.frame_controles, 
            text="Iniciar Monitoreo", 
            command=self.iniciar_monitoreo,
            relief=tk.RAISED,
            width=15
        )
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_detener = tk.Button(
            self.frame_controles, 
            text="Detener", 
            command=self.detener_monitoreo,
            width=10
        )
        self.btn_detener.pack(side=tk.LEFT, padx=5)
        
        # Control de umbral los porcentajes pueden variar pero se configurara mas adelante 
        tk.Label(
            self.frame_controles, 
            text="Umbral de alerta (%):", 
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(20, 0))
        
        self.slider_umbral = tk.Scale(
            self.frame_controles, 
            variable=self.threshold_var, 
            from_=50, 
            to=100, 
            orient="horizontal",
            length=150,
            bg="#f0f0f0"
        )
        self.slider_umbral.pack(side=tk.LEFT, padx=0)
        
        # Mostrar valor actual
        tk.Label(
            self.frame_controles, 
            textvariable=self.threshold_var,
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=5)
        
        self.btn_aplicar = tk.Button(
            self.frame_controles, 
            text="Aplicar", 
            command=self.aplicar_umbral,
            width=10
        )
        self.btn_aplicar.pack(side=tk.LEFT, padx=5)

        # Columnas
        self.frame_principal = tk.Frame(root, bg="#f0f0f0")
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Columna izquierda: Cámaras
        self.frame_camaras = tk.LabelFrame(
            self.frame_principal, 
            text="Cámaras disponibles",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.frame_camaras.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Crear grid para las cámaras
        self.frame_grid_camaras = tk.Frame(self.frame_camaras, bg="#f0f0f0")
        self.frame_grid_camaras.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Columna derecha: Alertas
        self.frame_alertas = tk.LabelFrame(
            self.frame_principal, 
            text="Alertas y Eventos",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0"
        )
        self.frame_alertas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Panel de alertas activas
        tk.Label(
            self.frame_alertas, 
            text="Alertas Activas", 
            anchor="w",
            bg="#f0f0f0"
        ).pack(fill="x", anchor="w", pady=(5, 0))
        
        self.frame_alertas_activas = tk.Frame(self.frame_alertas, bg="#ffcccc", height=120)
        self.frame_alertas_activas.pack(fill="x", expand=False, pady=5)
        
        # Historial de eventos
        tk.Label(
            self.frame_alertas, 
            text="Historial de Eventos", 
            anchor="w",
            bg="#f0f0f0"
        ).pack(fill="x", anchor="w", pady=(10, 0))
        
        # Tabla de historial
        columns = ("ID", "Fecha/Hora", "Cámara", "Tipo") #esto puede cambiar mas adelante
        self.history_tree = ttk.Treeview(self.frame_alertas, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(fill="both", expand=True, pady=5)
        
        # Botón para agregar cámara, esto es mas adorno, dependiendo si se agregaran mas o no 
        self.btn_agregar_camara = tk.Button(
            self.frame_camaras, 
            text="Agregar Cámara", 
            command=self.agregar_camara
        )
        self.btn_agregar_camara.pack(side=tk.BOTTOM, pady=10)
        
        # Barra inferior
        self.frame_barra_estado = tk.Frame(root, bg="#d9d9d9", height=25)
        self.frame_barra_estado.pack(fill="x", side=tk.BOTTOM)
        
        # Mostrar fecha y hora
        self.label_fecha_hora = tk.Label(
            self.frame_barra_estado, 
            text=f"Fecha y hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            bg="#d9d9d9"
        )
        self.label_fecha_hora.pack(side=tk.LEFT, padx=10)
        
        # Actualizar la fecha y hora cada segundo
        self.actualizar_fecha_hora()
        
    def actualizar_fecha_hora(self):
        """Actualiza la fecha y hora en la barra de estado."""
        self.label_fecha_hora.config(
            text=f"Fecha y hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        self.root.after(1000, self.actualizar_fecha_hora)

    def actualizar_estado(self, estado):
        """Actualiza el estado del sistema en la interfaz."""
        self.label_estado.config(
            text=f"Estado: {estado}", 
            fg="red"
        )

    def mostrar_mensaje(self, titulo, mensaje):
        """Muestra un mensaje emergente."""
        messagebox.showinfo(titulo, mensaje)

    def mostrar_alerta(self, alerta):
        """Muestra una nueva alerta en la interfaz."""
        # Agregar al historial
        self.history_tree.insert("", "end", values=(
            alerta["id_alerta"], 
            alerta["timestamp"].strftime("%H:%M:%S"),
            f"Cámara {alerta['id_camara'].replace('sim', '')}",
            alerta["tipo_anomalia"]
        ))
        
        # Mostrar alerta activa
        alerta_frame = tk.Frame(self.frame_alertas_activas, bg="#ffcccc", pady=5)
        alerta_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(
            alerta_frame,
            text=f"¡ALERTA! {alerta['tipo_anomalia']} detectado en Cámara {alerta['id_camara'].replace('sim', '')}",
            bg="#ffcccc",
            fg="red",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            alerta_frame,
            text="Revisar",
            command=lambda a=alerta["id_alerta"], f=alerta_frame: self.revisar_alerta(a, f)
        ).pack(side=tk.RIGHT, padx=5)

    def revisar_alerta(self, id_alerta, frame):
        """Marca una alerta como revisada y elimina la notificación."""
        self.marcar_revisada(id_alerta)
        frame.destroy()

    def crear_feed_video(self, id_camara, nombre):
        """Crea un marco de video para una cámara."""
        # Obtener el número de cámaras actuales para determinar la posición en el grid
        num_camaras = len(self.video_captures)
        fila = num_camaras // 2
        columna = num_camaras % 2
        
        # Crear el frame para la cámara
        frame = tk.Frame(self.frame_grid_camaras, borderwidth=1, relief="sunken", bg="white")
        frame.grid(row=fila, column=columna, padx=5, pady=5, sticky="nsew")
        
        # Configurar el nombre de la cámara
        label_nombre = tk.Label(
            frame, 
            text=nombre,
            bg="white",
            font=("Arial", 9)
        )
        label_nombre.pack(anchor="w", padx=5, pady=2)
        
        # Panel de video
        video_panel = tk.Label(frame, width=200, height=150, bg="black")
        video_panel.pack(padx=5, pady=2)
        
        # Guardar referencia al panel de video
        self.video_captures[id_camara] = video_panel
        
        # Configurar el grid para que se expanda correctamente
        self.frame_grid_camaras.grid_columnconfigure(0, weight=1)
        self.frame_grid_camaras.grid_columnconfigure(1, weight=1)

    # Métodos que serán reemplazados por el controlador
    def iniciar_monitoreo(self):
        pass
        
    def detener_monitoreo(self):
        pass
        
    def aplicar_umbral(self):
        pass
        
    def agregar_camara(self):
        pass
        
    def marcar_revisada(self, id_alerta=None):
        pass
