import networkx as nx
import osmnx as ox
import geopandas as gpd
import geopy.distance


def encontrar_lineas_que_llevan_al_destino(parada_linea_dict, destino):
    """Encuentra líneas de bus que tienen paradas cercanas al destino."""
    lineas_validas = []
    for nodo in parada_linea_dict.keys():
        x, y = nodo[0], nodo[1]
        #distancia = ox.distance.euclidean_dist_vec(y, x, destino[1], destino[0])
        coords_1 = (y, x)
        coords_2 = (destino[1], destino[0])
        distancia = geopy.distance.geodesic(coords_1, coords_2).m
        if distancia < 500:  # Consideramos 500m como radio de acceso
            print(distancia)
            lineas_validas.append(parada_linea_dict[nodo])
            break
    lista_aplanada = [elem for sublista in lineas_validas for elem in (sublista if isinstance(sublista, list) else [sublista])]  
    lista_unicos = list(set(lista_aplanada))  

    return lista_unicos
