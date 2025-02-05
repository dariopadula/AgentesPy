
## Genera agentes

from mesa import Agent
import networkx as nx
from datetime import timedelta
import numpy as np

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

##### Explorar esta forma


class AgenteMovil(Agent):
    VELOCIDADES = {
        "auto": 50_000 / 60,  # 50 km/h -> metros por minuto
        "bus": 30_000 / 60,   # 30 km/h
        "moto": 25_000 / 60,   # 30 km/h
        "bicicleta": 15_000 / 60,  # 15 km/h
        "caminata": 5_000 / 60  # 5 km/h
    }

    modo_colores = {
    "auto": "blue",
    "bus": "red",
    "moto": "black",
    "bicicleta": "orange",
    "caminata": "green"
    }


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
        self.tiempo_restante_arista = 0  # Tiempo restante para completar la arista

        # Calcular distancia total del viaje
        self.distancia_total = sum(
            model.grafo[self.ruta[i]][self.ruta[i+1]][0]['length']
            for i in range(len(self.ruta) - 1)
        ) if len(self.ruta) > 1 else 0

        # Elegir el modo de transporte según la distancia total del viaje
        self.modo_transporte = self.seleccionar_modo_transporte(self.distancia_total)
        self.color = self.modo_colores.get(self.modo_transporte, "gray")
        self.velocidad = self.VELOCIDADES[self.modo_transporte]

    def seleccionar_modo_transporte(self, distancia):
        opciones = ['auto','moto','bus','bicicleta','caminata']
        """ Selecciona el modo de transporte en función de la distancia del viaje """
        if distancia > 2_000:  # Más de 10 km → Auto o bus
            probabilidades = [0.4,0.2,0.3,0.1,0]
            selecciones = np.random.choice(opciones, size=1, replace=False, p=probabilidades)
            return selecciones[0]
        elif distancia > 1_000:  # Entre 3 km y 10 km → Bus o bicicleta
            probabilidades = [0.2,0.2,0.1,0.2,0.3]
            selecciones = np.random.choice(opciones, size=1, replace=False, p=probabilidades)
            return selecciones[0]
        elif distancia > 0:  # Menos de 3 km → Caminata o bicicleta
            probabilidades = [0.05,0.1,0,0.05,0.8]
            selecciones = np.random.choice(opciones, size=1, replace=False, p=probabilidades)
            return selecciones[0]
        else:  # Si la distancia es 0, evitar None
            return "caminata"

    def step(self):
        """ Simula el movimiento del agente en cada paso del modelo """
        if timedelta(self.model.time) >= self.tiempo_salida and not self.en_movimiento:
            self.en_movimiento = True

        if self.en_movimiento and self.ruta:
            if self.tiempo_restante_arista <= 0:  # Si no está a mitad de una arista
                if len(self.ruta) > 1:  # Verifica que hay una siguiente arista
                    nodo_actual = self.ruta.pop(0)
                    nodo_siguiente = self.ruta[0]
                    distancia_arista = self.model.grafo[nodo_actual][nodo_siguiente][0]["length"]

                    # Calcular tiempo necesario para recorrer esta arista
                    self.tiempo_restante_arista = distancia_arista / self.velocidad

            # Reducir el tiempo restante en este paso del modelo
            self.tiempo_restante_arista -= 1  # Asumiendo que cada step equivale a 1 minuto

            # Si el tiempo restante es 0 o menor, se mueve al siguiente nodo
            if self.tiempo_restante_arista <= 0:
                self.posicion_actual = self.ruta[0]

                # Si llegó al destino
                if not self.ruta[1:]:
                    self.en_movimiento = False
                    self.model.schedule.remove(self)
                    self.model.agentes_completados += 1
