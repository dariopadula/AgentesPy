import pandas as pd
from datetime import timedelta
import random

def load_data(file_path):
    return pd.read_csv(file_path)
    
##############################

def filter_data(matriz_od, nodes_with_zones,SacoIntra = True , zonas_origen = None, zonas_destino = None):
    # Filtrar matriz OD según zonas válidas
    zonas_validas = nodes_with_zones["CODSEG"].unique()
    # Filtrar la matriz OD para mantener solo viajes dentro de las zonas de interés
    matriz_filtrada = matriz_od[
        matriz_od["CODSEG_subida"].isin(zonas_validas) & 
        matriz_od["CODSEG_bajada"].isin(zonas_validas)
    ]

    # Calculo los viajes diarios
    matriz_filtrada = matriz_filtrada.assign(
        ndia = (matriz_filtrada['nViajes']/22).round().astype(int)
    )
    # saco las filas que no tienen viajes
    matriz_filtrada = matriz_filtrada[matriz_filtrada['ndia'] > 0]



 ## Saco viajes inter zona  
    if SacoIntra:
        matriz_filtrada = matriz_filtrada[matriz_filtrada["CODSEG_subida"] != matriz_filtrada["CODSEG_bajada"]]
 ## Filtro zona origen y destino

    if zonas_origen is not None:
        matriz_filtrada = matriz_filtrada[matriz_filtrada["CODSEG_subida"].isin(zonas_origen)] 
    if zonas_destino is not None:
        matriz_filtrada = matriz_filtrada[matriz_filtrada["CODSEG_bajada"].isin(zonas_destino)]
    
    return matriz_filtrada

##############################

def generar_viajes(matriz_od, nodos_por_zona, intervalo_minutos=60, start = 0):
    viajes = []
    matriz_od = matriz_od[matriz_od["hora"] >= start]
    for _, fila in matriz_od.iterrows():
        origen_zona = fila["CODSEG_subida"]
        destino_zona = fila["CODSEG_bajada"]
        viajes_cantidad = fila["ndia"].astype(int)
        tiempo_inicio = fila["hora"]

        # Sorteo de viajes
        for _ in range(viajes_cantidad):
            # Sortear tiempo dentro del rango
            tiempo_viaje = timedelta(hours=tiempo_inicio) + timedelta(minutes=random.uniform(0, intervalo_minutos))
            
            # Sortear nodo origen y destino
            nodo_origen = random.choice(nodos_por_zona[origen_zona])
            nodo_destino = random.choice(nodos_por_zona[destino_zona])
            
            viajes.append({"origen": nodo_origen, 
                           "destino": nodo_destino, 
                           "tiempo_salida": tiempo_viaje})
    return viajes, start
