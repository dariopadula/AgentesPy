from scripts.graph_utils import load_graph, process_nodes
from scripts.data_processing import load_data, filter_data, generar_viajes
from models.model import ModeloMovilidad
from scripts.plotting import setup_plot, update #, update_plot



import folium
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import display, clear_output
from collections import defaultdict

import contextily as ctx



# Cargar el grafo y los datos
G = load_graph(agranda_zona_kilom = 1)
nodes_with_zones, nodos_por_zona, nodes_gdf = process_nodes(G, "data/Marco2011_SEG_Montevideo_Total/Marco2011_SEG_Montevideo_Total.shp")
matriz_od = load_data("data/datAll_Hora_kernelDist_AllMes.csv")


# Filtrar y generar viajes
zorigen = [101003, 104001, 115104, 115106, 115204,115306,101001,106103]
# zorigen = None
zdestino = zorigen
matriz_filtrada = filter_data(matriz_od, nodes_with_zones,zonas_origen = zorigen, zonas_destino = zdestino)
# matriz_filtrada = filter_data(matriz_od, nodes_with_zones,zonas_origen = None, zonas_destino = None)
viajes, start = generar_viajes(matriz_filtrada, nodos_por_zona, start=10)

# Inicializar el modelo
modelo = ModeloMovilidad(G, viajes, start=start)

# Configurar la visualización

figure, ax, agents, scatter = setup_plot(G = G, nodes_gdf = nodes_gdf, scatter = True)
#ctx.add_basemap(ax, crs=nodes_gdf.crs.to_string(), source=ctx.providers.CartoDB.Positron)



# Contador de pasos
step_counter = 0
max_steps = 180  # Número máximo de pasos

# Inicializar un diccionario para contar aristas recorridas
conteo_aristas = defaultdict(int)
aristas_dibujadas = []



from functools import partial

# Preconfigurar la función update con los parámetros que no cambian
update_partial = partial(update, modelo=modelo, 
                        nodes_gdf=nodes_gdf, 
                        ax=ax, 
                        agents=agents, 
                        aristas_dibujadas=aristas_dibujadas, 
                        conteo_aristas=conteo_aristas, 
                        step_counter=step_counter, 
                        max_steps=max_steps, 
                        figure=figure,
                        alpha_incremento = 0.1,
                        peso_decremento = 0.8,
                        start = start,
                        scatter = scatter)

# Crear la animación usando FuncAnimation
ani = FuncAnimation(figure, update_partial, frames=range(max_steps), blit=True)
plt.show()

# Crear la animación
#ani = None
#ani = FuncAnimation(
#    figure, update, frames=range(max_steps), blit=False,
#    fargs=(modelo, nodes_gdf, ax, agents, aristas_dibujadas, conteo_aristas, step_counter, max_steps, figure, ani)
#)

#plt.show()


