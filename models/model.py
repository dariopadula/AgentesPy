from mesa import Model
from mesa.time import RandomActivation
from datetime import timedelta
import random
from models.agent import Auto


class ModeloMovilidad(Model):
    def __init__(self, grafo, viajes, seed=None, start = 0):
        self.random = random.Random(seed)
        self.grafo = grafo
        self.schedule = RandomActivation(self)
        self.time = start*60
        self.viajes_pendientes = viajes
        
        self.agentes_completados = 0

        super().__init__()

    def generar_agentes(self):

        # Convertir el tiempo actual del modelo a timedelta
        tiempo_actual = timedelta(minutes=self.time)

        viajes_a_iniciar = [v for v in self.viajes_pendientes if v["tiempo_salida"] <= tiempo_actual]
        for viaje in viajes_a_iniciar:
            #print(f"Tiempo actual: {tiempo_actual} -> Teimepo salida {viaje['tiempo_salida']}")
            agente = Auto(
                unique_id=self.schedule.get_agent_count() + 1, 
                model=self,
                origen=viaje["origen"],
                destino=viaje["destino"],
                tiempo_salida=viaje["tiempo_salida"]
            )
            self.schedule.add(agente)
        self.viajes_pendientes = [v for v in self.viajes_pendientes if v["tiempo_salida"] > tiempo_actual]

    def step(self):
        self.generar_agentes()
        self.schedule.step()
        self.time += 1

        print(f"Paso {self.time} - Generando agentes")
    
        # Depurar el número de agentes generados y en movimiento
        print(f"Agentes generados: {len(self.schedule.agents)}")
        print(f"Agentes en movimiento: {sum(1 for agente in self.schedule.agents if agente.en_movimiento)}")
