import tkinter as tk
import threading
import cv2
import random
import datetime
import time
import numpy as np
from PIL import Image, ImageTk
from modelo import SistemaSeguridad
from vista import SistemaSeguridadVista

class SistemaSeguridadControlador:
    def __init__(self, root):
        """Inicializa el controlador y conecta la vista con el modelo."""
        self.modelo = SistemaSeguridad()
        self.vista = SistemaSeguridadVista(root)
        
        # Conectar eventos de la vista con métodos del controlador
        self.vista.iniciar_monitoreo = self.iniciar_monitoreo
        self.vista.detener_monitoreo = self.detener_monitoreo
        self.vista.aplicar_umbral = self.aplicar_umbral
        self.vista.agregar_camara = self.agregar_camara
        self.vista.marcar_revisada = self.marcar_revisada
        
        # Variables de control
        self.monitoreo_activo = False
        self.hilos_camara = {}
        
        # Añadir una lista para guardar los IDs de las alertas programadas
        self.alertas_programadas = []
        
        # Añadir cámaras simuladas al inicio
        self.agregar_camara_simulada("sim1", "Cam1", "Caja")
        self.agregar_camara_simulada("sim2", "Cam 2", "Pasillo 1")
        self.agregar_camara_simulada("sim3", "Cam 3", "Pasillo 2")
        self.agregar_camara_simulada("sim4", "Cam 4", "Pasillo 3")
        
        # Iniciar monitoreo automáticamente después de un breve retraso
        root.after(1000, self.iniciar_demostracion)

    def iniciar_demostracion(self):
        """Inicia el monitoreo automáticamente y programa alertas simuladas."""
        self.iniciar_monitoreo()
        
        # Simular alertas con retrasos y guardar sus IDs
        id1 = self.vista.root.after(3000, self.generar_alerta_simulada, "sim1", "Intruso")
        id2 = self.vista.root.after(7000, self.generar_alerta_simulada, "sim3", "Objeto abandonado")
        id3 = self.vista.root.after(12000, self.generar_alerta_simulada, "sim2", "Comportamiento sospechoso")
        
        # Guardar los IDs para poder cancelarlos más tarde
        self.alertas_programadas.extend([id1, id2, id3])

    def iniciar_monitoreo(self):
        """Inicia el monitoreo de todas las cámaras."""
        if self.monitoreo_activo:
            return
        
        self.monitoreo_activo = True
        self.modelo.estado_sistema = "Monitoreo"
        self.vista.actualizar_estado("Monitoreo")
        
        # Iniciar un hilo para cada cámara
        for camara in self.modelo.camaras_activas:
            id_camara = camara["id"]
            hilo = threading.Thread(target=self.procesar_video, args=(id_camara,))
            hilo.daemon = True
            hilo.start()
            self.hilos_camara[id_camara] = hilo
        
        self.vista.mostrar_mensaje("Monitoreo", "El monitoreo se ha iniciado")

    def detener_monitoreo(self):
        """Detiene el monitoreo de todas las cámaras."""
        if not self.monitoreo_activo:
            return
        
        self.monitoreo_activo = False
        self.modelo.estado_sistema = "Detenido"
        self.vista.actualizar_estado("Detenido")
        
        # Cancelar todas las alertas programadas
        for id_alerta in self.alertas_programadas:
            self.vista.root.after_cancel(id_alerta)
        self.alertas_programadas = []
        
        # Los hilos terminarán automáticamente al salir del bucle
        self.hilos_camara.clear()
        
        self.vista.mostrar_mensaje("Monitoreo", "El monitoreo se ha detenido")

    def agregar_camara_simulada(self, id_camara, nombre, ubicacion):
        """Agrega una cámara simulada al sistema."""
        if any(cam["id"] == id_camara for cam in self.modelo.camaras_activas):
            return
        
        self.modelo.agregar_camara(id_camara, nombre, ubicacion)
        self.vista.crear_feed_video(id_camara, f"{nombre} ({ubicacion})")

    def procesar_video(self, id_camara):
        """Procesa el video de una cámara, ya sea real o simulada."""
        while self.monitoreo_activo:
            if id_camara.startswith("sim"):
                # Generar imagen simulada
                frame = self.generar_frame_simulado(id_camara)
            else:
                # Leer de la cámara real
                if id_camara not in self.vista.video_captures:
                    break
                cap = self.vista.video_captures[id_camara]
                ret, frame = cap.read()
                if not ret:
                    break
            
            # Convertir a formato para mostrar en Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((200, 150))
            img_tk = ImageTk.PhotoImage(image=img)
            
            # Actualizar la etiqueta de video en la interfaz
            self.vista.root.after(0, self.actualizar_label_video, id_camara, img_tk)
            
            # Simular detección de anomalías con baja probabilidad
            if random.random() < 0.001 and self.monitoreo_activo:  # Verificación adicional
                tipos_anomalia = ["Movimiento sospechoso", "Objeto abandonado", "Intruso", "Exceso de personas"]
                self.generar_alerta_simulada(id_camara, random.choice(tipos_anomalia))
            
            time.sleep(0.1)  # Reducir la carga de CPU

    def actualizar_label_video(self, id_camara, img_tk):
        """Actualiza la etiqueta de video en la interfaz."""
        if id_camara in self.vista.video_captures:
            label = self.vista.video_captures[id_camara]
            label.imgtk = img_tk  # Mantener referencia para evitar garbage collection
            label.configure(image=img_tk)

    def generar_frame_simulado(self, id_camara):
        """Genera un frame simulado para una cámara."""
        # Crear un marco negro de 320x240
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        
        # Añadir texto según la cámara
        texto = ""
        for camara in self.modelo.camaras_activas:
            if camara["id"] == id_camara:
                texto = f"{camara['nombre']} - {camara['ubicacion']}"
                break
        
        # Añadir fecha y hora
        tiempo = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Colocar texto en el marco
        cv2.putText(frame, texto, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, tiempo, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Simular movimiento aleatorio (puntos brillantes)
        for _ in range(10):
            x = random.randint(0, 319)
            y = random.randint(0, 239)
            cv2.circle(frame, (x, y), 1, (0, 255, 0), 1)
        
        return frame

    def generar_alerta_simulada(self, id_camara, tipo_anomalia):
        """Genera una alerta simulada para demostración."""
        if not self.monitoreo_activo:
            return
        
        confianza = random.randint(75, 95)
        alerta = {
            "id_alerta": len(self.modelo.historial_alertas) + 1,
            "id_camara": id_camara,
            "tipo_anomalia": tipo_anomalia,
            "nivel_confianza": confianza,
            "timestamp": datetime.datetime.now(),
            "estado": "Nueva"
        }
        
        self.modelo.historial_alertas.append(alerta)
        self.modelo.estado_sistema = "Alerta"
        
        self.vista.mostrar_alerta(alerta)
        self.vista.actualizar_estado("Alerta")

    def aplicar_umbral(self):
        """Aplica el nuevo umbral de confianza para alertas."""
        nuevo_umbral = self.vista.threshold_var.get()
        if self.modelo.cambiar_umbral(nuevo_umbral):
            self.vista.mostrar_mensaje("Umbral actualizado", 
                                      f"Nuevo umbral de alerta: {nuevo_umbral}%")
        else:
            self.vista.mostrar_mensaje("Error", "El umbral debe estar entre 50% y 100%")
#Esto esta en pendiente, es por si se llega a necesitar pero hay que hacer modificaciones
    def agregar_camara(self): 
        """Agrega una nueva cámara al sistema."""
        opciones = {
            "0": "Cámara web (si está disponible)",
            "sim5": "Cámara simulada 5 (Almacén)",
            "sim6": "Cámara simulada 6 (Entrada del establecimiento)"
        }
        
        dialog = tk.Toplevel(self.vista.root)
        dialog.title("Agregar Cámara")
        dialog.geometry("300x200")
        dialog.transient(self.vista.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Seleccione una cámara:").pack(pady=10)
        seleccion = tk.StringVar(dialog)
        seleccion.set("sim5")

        for valor, texto in opciones.items():
            tk.Radiobutton(dialog, text=texto, variable=seleccion, value=valor).pack(anchor=tk.W, padx=20)
        
        def confirmar():
            id_camara = seleccion.get()
            nombre = opciones[id_camara].split('(')[0].strip()
            ubicacion = opciones[id_camara].split('(')[1].rstrip(')') if "(" in opciones[id_camara] else "Desconocida"

            if any(cam["id"] == id_camara for cam in self.modelo.camaras_activas):
                self.vista.mostrar_mensaje("Error", "Esta cámara ya está agregada")
                dialog.destroy()
                return
            
            if id_camara.isdigit():
                try:
                    cap = cv2.VideoCapture(int(id_camara))
                    if not cap.isOpened():
                        self.vista.mostrar_mensaje("Error", "No se pudo conectar a la cámara web")
                        dialog.destroy()
                        return
                    self.vista.video_captures[id_camara] = cap
                except Exception as e:
                    self.vista.mostrar_mensaje("Error", f"Error al conectar: {str(e)}")
                    dialog.destroy()
                    return
            
            self.modelo.agregar_camara(id_camara, nombre, ubicacion)
            self.vista.crear_feed_video(id_camara, f"{nombre} ({ubicacion})")
            
            if self.monitoreo_activo:
                hilo = threading.Thread(target=self.procesar_video, args=(id_camara,))
                hilo.daemon = True
                hilo.start()
                self.hilos_camara[id_camara] = hilo
            
            dialog.destroy()
        
        tk.Button(dialog, text="Agregar", command=confirmar).pack(side=tk.LEFT, expand=True, padx=10, pady=20)
        tk.Button(dialog, text="Cancelar", command=dialog.destroy).pack(side=tk.RIGHT, expand=True, padx=10, pady=20)
        
        self.vista.root.wait_window(dialog)

    def marcar_revisada(self, id_alerta=None):
        """Marca una alerta seleccionada como revisada."""
        if id_alerta is not None:
            # Cuando se llama directamente desde el botón de revisar
            if self.modelo.marcar_alerta_revisada(id_alerta):
                # Actualizar estado del árbol de historial
                for item in self.vista.history_tree.get_children():
                    valores = self.vista.history_tree.item(item)['values']
                    if valores[0] == id_alerta:
                        # No es necesario actualizar el estado visualmente
                        # ya que el frame de alerta ya se eliminó
                        break
            else:
                self.vista.mostrar_mensaje("Error", "No se pudo marcar la alerta como revisada")
        else:
            # Cuando se llama desde el botón general (selección en la tabla)
            seleccion = self.vista.history_tree.selection()
            if not seleccion:
                self.vista.mostrar_mensaje("Error", "Debe seleccionar una alerta")
                return
            
            item = self.vista.history_tree.item(seleccion[0])
            id_alerta = int(item['values'][0])
            
            if self.modelo.marcar_alerta_revisada(id_alerta):
                # No es necesario actualizar el estado visualmente en la tabla
                pass
            else:
                self.vista.mostrar_mensaje("Error", "No se pudo marcar la alerta como revisada")
