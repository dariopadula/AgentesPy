
import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import pickle

from get.get_lineas_subgrafo import *


# Descargar la red de calles de Montevideo para vehículos
#G_mvd = ox.graph_from_place("Montevideo, Uruguay", network_type="drive")
# Guardar en disco para no descargarlo cada vez
#ox.save_graphml(G_mvd, "SHP/montevideo_drive.graphml")
# Cargar el grafo de toda la ciudad
G_mvd = ox.load_graphml("../SHP/montevideo_drive.graphml")

###
# ruta lina buses
# Leer las zonas como un GeoDataFrame (por ejemplo, un shapefile)
rutasbus_gdf = gpd.read_file("../SHP/v_uptu_lsv/v_uptu_lsv.shp").to_crs("EPSG:4326")


subgrafos_buses = map_bus_routes_shortest_path(G = G_mvd, rutas_buses_shape = rutasbus_gdf)

print(f"El total de sub grafos es: {len(subgrafos_buses)}")

print('Guardo el diccionario de rutas')



# Guardar en un archivo
with open("../SHP/subgrafos_buses.pkl", "wb") as f:
    pickle.dump(subgrafos_buses, f)



print('corrio todo bien')


