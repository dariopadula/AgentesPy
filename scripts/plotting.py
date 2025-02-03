import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

import time


def setup_plot(G, nodes_gdf):
    # Configurar el gráfico inicial

        ###############################
    #### Grafico iterativo
    ## Posiciones de los nodos del grafo
    pos = {node: (row['x'], row['y']) for node, row in nodes_gdf.iterrows()}

    # here we are creating sub plots
    figure, ax = plt.subplots(figsize=(10, 8))

    nx.draw(G, pos, ax=ax, with_labels=False, node_size=10, node_color="gray", edge_color="lightgray", alpha=0.1, width=0.1)

    x, y = [], []
    agents, = ax.plot(x, y, 'go', markersize=1)  # Usa un tamaño mayor

    return figure, ax, agents

#def update_plot(modelo, agents, ax):
    # Actualizar los agentes en el gráfico


#    ...

#### Adapta el frame


def update(frames, 
            modelo, 
            nodes_gdf, 
            ax, 
            agents, 
            aristas_dibujadas, 
            conteo_aristas, 
            step_counter, 
            max_steps, 
            figure, 
            alpha_incremento = 0.005,
            peso_decremento = 0.8,
            start = 0,
            cmap = mcolors.LinearSegmentedColormap.from_list("white_red", ["white", "red"])
):

    modelo.step()

    #step_counter += 1
    tiempo_actual = modelo.time
    step_counter = tiempo_actual - start*60
    print(f"step_counter: {step_counter}")
    #print(f"Tiempo actual: {tiempo_actual}")

    new_x, new_y = [], []
    for agente in modelo.schedule.agents:
        if agente.en_movimiento and agente.posicion_actual is not None:
            nodo_actual = nodes_gdf.loc[agente.posicion_actual]
            new_x.append(nodo_actual['x'])
            new_y.append(nodo_actual['y'])

            if len(agente.ruta) > 1:
                nodo_siguiente = agente.ruta[0]
                arista = (agente.posicion_actual, nodo_siguiente)
                conteo_aristas[arista] += 1

    for linea in aristas_dibujadas:
        linea.remove()
    aristas_dibujadas.clear()


    # Normalizar pesos para usarlos en la escala de colores
    if conteo_aristas:
        max_peso = max(conteo_aristas.values())  # Encontrar el máximo peso
    else:
        max_peso = 1  # Evitar división por cero

    norm = mcolors.Normalize(vmin=0, vmax=max_peso)  # Normalizar pesos
    scalar_map = cm.ScalarMappable(norm=norm, cmap=cmap)  # Crear el mapeo de colores

    for arist, peso in conteo_aristas.items():
        if peso > 0.1:
            nodo_origen, nodo_destino = arist
            alpha = min(1, 0 + alpha_incremento * max(0, peso))
            color = scalar_map.to_rgba(peso)
            x_vals = [nodes_gdf.loc[nodo_origen]['x'], nodes_gdf.loc[nodo_destino]['x']]
            y_vals = [nodes_gdf.loc[nodo_origen]['y'], nodes_gdf.loc[nodo_destino]['y']]
            #linea, = ax.plot(x_vals, y_vals, 'b-', alpha=alpha)
            linea, = ax.plot(x_vals, y_vals, color=color, linewidth=1)
            aristas_dibujadas.append(linea)

    for k in conteo_aristas:
        conteo_aristas[k] = (1 - peso_decremento)*conteo_aristas[k]
        #conteo_aristas[k] -= 0.8
        conteo_aristas[k] = max(0, conteo_aristas[k])

    agents.set_xdata(new_x)
    agents.set_ydata(new_y)

    # Agregar o actualizar la barra de colores
    if not hasattr(ax, 'colorbar'):
        cbar = figure.colorbar(scalar_map, ax=ax, orientation="vertical", fraction=0.05, pad=0.02)
        cbar.set_label("Frecuencia de Uso")
        ax.colorbar = cbar  # Guardar la referencia
    else:
        ax.colorbar.update_normal(scalar_map)  # Actualizar colorbar si ya existe

    if step_counter >= max_steps:
        #ani.event_source.stop()
        time.sleep(3)
        plt.close(figure)

    return agents, *aristas_dibujadas

