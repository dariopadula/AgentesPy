import networkx as nx
import osmnx as ox
import geopandas as gpd
import geopy.distance


def encontrar_lineas_que_llevan_al_destino(parada_linea_dict, destino, min_distancia_parada = 500):
    """Encuentra líneas de bus que tienen paradas cercanas al destino."""
    lineas_validas = []
    for nodo in parada_linea_dict.keys():
        x, y = nodo[0], nodo[1]
        #distancia = ox.distance.euclidean_dist_vec(y, x, destino[1], destino[0])
        coords_1 = (y, x)
        coords_2 = (destino[1], destino[0])
        distancia = geopy.distance.geodesic(coords_1, coords_2).m
        if distancia < min_distancia_parada:  # Consideramos 500m como radio de acceso
            print(distancia)
            lineas_validas.append(parada_linea_dict[nodo])
            break
    lista_aplanada = [elem for sublista in lineas_validas for elem in (sublista if isinstance(sublista, list) else [sublista])]  
    lista_unicos = list(set(lista_aplanada))  

    return lista_unicos


def encontrar_mejor_parada(G_l, origen):
    """Encuentra la parada más cercana dentro de un subgrafo de línea de bus."""
    return ox.distance.nearest_nodes(G_l, origen[0], origen[1])

def encontrar_camino_en_linea(G_l, parada_origen, parada_destino):
    """Calcula la ruta más corta dentro del subgrafo de una línea de bus."""
    return nx.shortest_path(G_l, parada_origen, parada_destino, weight="length")

def asignar_viaje_bus(origen, destino, subgrafos_buses):
    """
    Asigna la mejor ruta en bus considerando las líneas disponibles.
    Si no hay línea directa, considera transbordos.
    """
    lineas_candidatas = encontrar_lineas_que_llevan_al_destino(subgrafos_buses, destino)

    if not lineas_candidatas:
        return None  # No hay ruta en bus posible

    mejor_ruta = None
    mejor_distancia = float('inf')

    for linea in lineas_candidatas:
        G_l = subgrafos_buses[linea]
        parada_origen = encontrar_mejor_parada(G_l, origen)
        parada_destino = encontrar_mejor_parada(G_l, destino)

        if parada_origen and parada_destino:
            try:
                ruta = encontrar_camino_en_linea(G_l, parada_origen, parada_destino)
                distancia = sum(G_l[u][v][0]['length'] for u, v in zip(ruta[:-1], ruta[1:]))

                if distancia < mejor_distancia:
                    mejor_ruta = ruta
                    mejor_distancia = distancia
            except nx.NetworkXNoPath:
                continue

    return mejor_ruta
