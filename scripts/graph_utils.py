
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point

def load_graph(agranda_zona_kilom = 0):
    # Definir el bounding box y cargar el grafo
    # Coordenadas originales del bounding box
    lat_min, lat_max = -34.91668, -34.87668
    lon_min, lon_max = -56.20937, -56.16937

    # Expansión de 3 km en todas las direcciones
    lat_expand = agranda_zona_kilom / 111  # ~0.027 grados
    lon_expand = agranda_zona_kilom / 96   # ~0.031 grados

    # Nuevas coordenadas del bounding box
    lat_min_new = lat_min - lat_expand
    lat_max_new = lat_max + lat_expand
    lon_min_new = lon_min - lon_expand
    lon_max_new = lon_max + lon_expand

    # Crear el grafo con el nuevo bounding box
    G = ox.graph_from_bbox((lon_min_new, lat_min_new, lon_max_new, lat_max_new), network_type='drive')

    # Asignar el peso de las aristas al largo (longitud)
    for u, v, data in G.edges(data=True):
        data['weight'] = data.get('length', 1)  # Usa 'length' o un valor por defecto de 1 si no está disponible


    return G

############################

def process_nodes(G, shapefile_path):
    # Procesar nodos y realizar intersección espacial
    # Crear un GeoDataFrame con los nodos
    nodes = ox.graph_to_gdfs(G, edges=False)
    nodes['geometry'] = nodes.apply(lambda row: Point(row['x'], row['y']), axis=1)
    nodes_gdf = gpd.GeoDataFrame(nodes, geometry='geometry', crs="EPSG:4326")

    # Leer las zonas como un GeoDataFrame (por ejemplo, un shapefile)
    zonas_gdf = gpd.read_file(shapefile_path)
    zonas_gdf.head()

    # Realizar la intersección espacial
    nodes_with_zones = gpd.sjoin(nodes_gdf, zonas_gdf[["geometry", "CODSEG", "P_TOT"]].to_crs("EPSG:4326"), how="left")
    # Crear un diccionario para nodos por zona
    nodos_por_zona = nodes_with_zones.groupby("CODSEG").apply(
        lambda df: df.index.tolist()
    ).to_dict()

    return nodes_with_zones, nodos_por_zona, nodes_gdf