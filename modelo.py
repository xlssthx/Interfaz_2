import datetime
import random  # Solo para simular detecciones, pendiente el banco de datos
class SistemaSeguridad:
    def __init__(self):
        """Inicializa el sistema de seguridad con valores predeterminados."""
        self.historial_alertas = []  # Lista de alertas generadas
        self.estado_sistema = "Monitoreo"  # Estado del sistema (Monitoreo, Alerta, etc.)
        self.camaras_activas = []  # Lista de cámaras activas en el sistema (4)
        self.umbral_confianza = 80  # Umbral mínimo de confianza para alertas (en %)

    def cambiar_umbral(self, nuevo_umbral):
        """Cambia el umbral de confianza para las alertas si está en el rango permitido."""
        if 50 <= nuevo_umbral <= 100:
            self.umbral_confianza = nuevo_umbral
            return True
        return False

    def agregar_camara(self, id_camara, nombre, ubicacion):
        """Añade una nueva cámara al sistema."""
        self.camaras_activas.append({"id": id_camara, "nombre": nombre, "ubicacion": ubicacion})

    def marcar_alerta_revisada(self, id_alerta):
        """Marca una alerta específica como revisada."""
        for alerta in self.historial_alertas:
            if alerta["id_alerta"] == id_alerta:
                alerta["estado"] = "Revisada"
                return True
        return False
