'''
attack_handling(): script che gestisce la parte relativa
                   alla rimozione di nodi nella rete
--------------------------------------------------------------
Creato da:
    Stefano Zuccarella n.816482
    Matteo Paolella n.816933
'''

import numpy as np

from graphs import create_graph_for_attack_handling
from plots import plot_metric_results


def remove_nodes_analysis(graph, graph_no_multiple_edges, metrics):

    number_of_nodes = graph.vcount()

    # Per ogni metrica, calcolo il valore associato dei nodi e li ordino
    # decrescentemente per identificare i nodi più importanti che verranno
    # rimossi uno alla volta per calcolare S
    for metric in metrics:
        if metric == 'betweenness':
            graph_betweenness = graph.copy()
            nodes_betweenness = np.asarray(graph_betweenness.betweenness(directed=False)) / \
                                (((number_of_nodes - 1) * (number_of_nodes - 2)) / 2)
            nodes_betweenness, nodes_to_remove_betweenness = \
                get_sorted_metric_results(nodes_betweenness, graph_betweenness)

            S_betweenness = [compute_S_metric(graph_betweenness, number_of_nodes)]

            for node in nodes_to_remove_betweenness:
                graph_betweenness.delete_vertices([graph_betweenness.vs.find(name=node)])
                S_betweenness.append(compute_S_metric(graph_betweenness, number_of_nodes))

        if metric == 'degree':
            graph_degree = graph.copy()
            nodes_degree = graph_degree.degree(np.arange(number_of_nodes))
            nodes_degree, nodes_to_remove_degree = get_sorted_metric_results(nodes_degree, graph_degree)

            S_degree = [compute_S_metric(graph_degree, number_of_nodes)]

            for node in nodes_to_remove_degree:
                graph_degree.delete_vertices([graph_degree.vs.find(name=node)])
                S_degree.append(compute_S_metric(graph_degree, number_of_nodes))

        if metric == 'closeness':
            graph_closeness = graph.copy()
            nodes_closeness = graph_closeness.closeness()
            nodes_closeness, nodes_to_remove_closeness = \
                get_sorted_metric_results(nodes_closeness, graph_closeness)

            S_closeness = [compute_S_metric(graph_closeness, number_of_nodes)]

            for node in nodes_to_remove_closeness:
                graph_closeness.delete_vertices([graph_closeness.vs.find(name=node)])
                S_closeness.append(compute_S_metric(graph_closeness, number_of_nodes))

    print(S_betweenness, S_degree, S_closeness)

    S = [S_betweenness, S_degree, S_closeness]
    nodes_to_remove = [nodes_to_remove_betweenness, nodes_to_remove_degree, nodes_to_remove_closeness]
    graphs = [graph_betweenness, graph_degree, graph_closeness]

    # Creo un grafo che contiene l'informazione dei nodi tolti e dei nodi
    # che fanno parte della principale componente connessa
    create_graph_for_attack_handling(graph_no_multiple_edges, nodes_to_remove, graphs)

    # Creo un plot che illustra il rapporto tra nodi rimossi e S
    plot_metric_results(S)


def compute_S_metric(graph, number_of_nodes):

    number_of_nodes_of_component = len(graph.components().giant().vs)

    # Calcolo la metrica relativa ad S
    return number_of_nodes_of_component / number_of_nodes


def get_sorted_metric_results(metric_results, graph):

    nodes_to_remove = []

    def take_second(elem):
        return elem[1]

    # Ordino i valori dei nodi decrescentemente, ed individuo
    # i nodi da dover rimuovere nel grafo
    nodes_with_indexes = []
    number_of_nodes = len(metric_results)
    for i in range(number_of_nodes):
        nodes_with_indexes.append([i, metric_results[i]])

    nodes_with_indexes.sort(key=take_second, reverse=True)

    for i in range(int(number_of_nodes / 2)):
        nodes_to_remove.append(graph.vs[nodes_with_indexes[i][0]]['name'])

    return metric_results, nodes_to_remove
