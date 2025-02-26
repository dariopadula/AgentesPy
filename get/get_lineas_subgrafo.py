
import osmnx as ox
import networkx as nx
import geopandas as gpd
import pickle
import sklearn
from shapely.geometry import LineString
from scipy.spatial import cKDTree
from collections import deque
import geopy.distance

### Arma un arbol para agilizar la búsqueda de puntos cercanos

def precomputar_nodos_cercanos(G):
    nodos_coords = [(data['x'], data['y']) for _, data in G.nodes(data=True)]
    kdtree = cKDTree(nodos_coords)
    return kdtree, list(G.nodes)

### Encuentra puntos cercanos en funcion del arbol
def encontrar_nodos_cercanos(kdtree, nodos_grafo, puntos_ruta):
    nodos_ruta = []
    for punto in puntos_ruta:
        dist, idx = kdtree.query(punto)
        nodos_ruta.append(nodos_grafo[idx])
    return nodos_ruta

######## Eliminar ciclos en los sub grafos

def eliminar_ciclos_dfs(grafo, cola_puntos = 10):
    ciclos = set()
    visited = set()
    
    def dfs(v, parent):
        visited.add(v)
        for neighbor in grafo.neighbors(v):
            if neighbor not in visited[-cola_puntos:]:
                if dfs(neighbor, v):
                    return True
            elif neighbor != parent:
                ciclos.add((v, neighbor))
                return True
        return False

    # Ejecutamos DFS sobre cada nodo
    for node in grafo.nodes:
        if node not in visited:
            dfs(node, None)
    
    # Eliminamos las aristas que forman parte de los ciclos
    for u, v in ciclos:
        if grafo.has_edge(u, v):
            grafo.remove_edge(u, v)

    return grafo

#### Otra forma de eliminar ciclos (genera grafos no conexos)
def eliminar_ciclos(grafo):
    """
    Encuentra y elimina ciclos en un grafo dirigido utilizando NetworkX.
    """
    ciclos = True
    while ciclos:
        try:
            ciclo = nx.find_cycle(grafo, orientation="original")  # Encuentra un ciclo
            for edge in ciclo:
                u, v = edge[:2]  # Tomamos solo los nodos (ignoramos key/orientación)
                if grafo.has_edge(u, v):
                    grafo.remove_edge(u, v)  # Eliminamos la arista del ciclo
        except nx.NetworkXNoCycle:
            ciclos = False  # No hay más ciclos, terminamos
    
    #  Eliminar nodos que quedaron sin conexiones
    nodos_aislados = list(nx.isolates(grafo))
    if len(nodos_aislados) > 0:
        grafo.remove_nodes_from(nodos_aislados)        

    return grafo


######################################
### Encuentra subgrafo de cada linea variante

def map_bus_routes_shortest_path(G, rutas_buses_shape, elimina_ciclos = False):
    """
    Asigna rutas de buses al grafo G asegurando que solo se incluyan las aristas recorridas realmente.
    """
    kdtree, nodos_grafo = precomputar_nodos_cercanos(G)
    #rutas_buses = gpd.read_file(rutas_shapefile).to_crs("EPSG:4326")
    nodos_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)  # Extraer nodos como GeoDataFrame
    subgrafos_buses = {}

    for _, row in rutas_buses_shape.iterrows():
        linea_bus = row["COD_VARIAN"]
        geom = row["geometry"]
        print(linea_bus)
        if not isinstance(geom, LineString):
            continue  

        #  Obtener los puntos de la LineString
        puntos_ruta = list(geom.coords)

        #  Encontrar los nodos más cercanos en el grafo
        #nodos_ruta = [ox.distance.nearest_nodes(G, x, y) for x, y in puntos_ruta]
        nodos_ruta = encontrar_nodos_cercanos(kdtree, nodos_grafo, puntos_ruta)

        #  Construir la ruta más corta entre los nodos consecutivos
        edges_recorridos = set()
        #print(edges_recorridos)
        for nodo_inicio, nodo_fin in zip(nodos_ruta[:-1], nodos_ruta[1:]):
            try:
                camino = nx.shortest_path(G, nodo_inicio, nodo_fin, weight="length")
                for u, v in zip(camino[:-1], camino[1:]):
                    if G.is_multigraph():
                        for key in G[u][v]:
                            edges_recorridos.add((u, v, key))
                    else:
                        edges_recorridos.add((u, v))
            except nx.NetworkXNoPath:
                continue  # Ignorar si no hay un camino

        #  Crear el subgrafo con solo las aristas recorridas
        G_l = G.edge_subgraph(edges_recorridos).copy()
        # Eliminar ciclos en el subgrafo
        if not nx.is_directed_acyclic_graph(G_l) and elimina_ciclos:
            G_l = eliminar_ciclos(G_l)

        
        subgrafos_buses[linea_bus] = G_l


    return subgrafos_buses







