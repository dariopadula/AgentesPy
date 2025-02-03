
## Genera agentes

from mesa import Agent
import networkx as nx
from datetime import timedelta

######################################

class Auto(Agent):
    def __init__(self, unique_id, model, origen, destino, tiempo_salida):
        super().__init__(model)
        self.origen = origen
        self.destino = destino
        self.tiempo_salida = tiempo_salida
        self.unique_id = unique_id

        # Calcular ruta con manejo de errores
        try:
            self.ruta = nx.shortest_path(model.grafo, source=origen, target=destino, weight="length")
        except nx.NetworkXNoPath:
            self.ruta = []  # Ruta vacía si no hay camino
        self.posicion_actual = self.ruta[0] if self.ruta else None
        self.en_movimiento = False

    def step(self):
        #print(f"Tiempo del modelo desde el agente: {self.model.time}")
        if timedelta(self.model.time) >= self.tiempo_salida and not self.en_movimiento:
        #if self.model.time >= self.tiempo_salida.total_seconds()/60 and not self.en_movimiento:
            self.en_movimiento = True
        
        if self.en_movimiento and self.ruta:
            self.posicion_actual = self.ruta.pop(0)
            if not self.ruta:  # Llegó al destino
                self.en_movimiento = False
                self.model.schedule.remove(self)
                self.model.agentes_completados += 1

