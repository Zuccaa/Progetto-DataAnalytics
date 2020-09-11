'''
attack_handling(): script che gestisce la parte relativa
                   alla rimozione di nodi nella rete
--------------------------------------------------------------
Creato da:
    Stefano Zuccarella n.816482
    Matteo Paolella n.816933
'''

import numpy as np
import random

from graphs import create_graph_for_attack_handling
from plots import plot_metric_results


def remove_nodes_analysis(graph, graph_no_multiple_edges, metrics):

    number_of_nodes = graph.vcount()
    static_S = []
    static_nodes_to_remove = []
    static_graphs = []
    dynamic_S = []
    dynamic_nodes_to_remove = []
    dynamic_graphs = []

    # Per ogni metrica, calcolo il valore associato dei nodi e li ordino
    # decrescentemente per identificare i nodi più importanti che verranno
    # rimossi uno alla volta per calcolare S
    for metric in metrics:
        graph_for_static_metric = graph.copy()
        graph_for_dynamic_metric = graph.copy()
        static_S_results, static_nodes_removed, static_final_graph = \
            compute_static_remove(metric, number_of_nodes, graph_for_static_metric)
        dynamic_S_results, dynamic_nodes_removed, dynamic_final_graph = \
            compute_dynamic_remove(metric, number_of_nodes, graph_for_dynamic_metric)
        static_S.append(static_S_results)
        dynamic_S.append(dynamic_S_results)
        if metric != 'random':
            static_nodes_to_remove.append(static_nodes_removed)
            static_graphs.append(static_final_graph)
            dynamic_nodes_to_remove.append(dynamic_nodes_removed)
            dynamic_graphs.append(dynamic_final_graph)

    # Creo un grafo che contiene l'informazione dei nodi tolti e dei nodi
    # che fanno parte della principale componente connessa
    create_graph_for_attack_handling(graph_no_multiple_edges, static_nodes_to_remove, static_graphs)
    create_graph_for_attack_handling(graph_no_multiple_edges, dynamic_nodes_to_remove, dynamic_graphs)

    # Creo un plot che illustra il rapporto tra nodi rimossi e S
    plot_metric_results(static_S)
    plot_metric_results(dynamic_S)


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


def compute_static_remove(metric, number_of_nodes, graph):

    nodes_to_remove = []
    S = None

    if metric == 'betweenness':
        nodes_betweenness = np.asarray(graph.betweenness(directed=False)) / \
                            (((number_of_nodes - 1) * (number_of_nodes - 2)) / 2)
        nodes_betweenness, nodes_to_remove = get_sorted_metric_results(nodes_betweenness, graph)

        S = [compute_S_metric(graph, number_of_nodes)]

        for node in nodes_to_remove:
            graph.delete_vertices([graph.vs.find(name=node)])
            S.append(compute_S_metric(graph, number_of_nodes))

    if metric == 'degree':
        nodes_degree = graph.degree(np.arange(number_of_nodes))
        nodes_degree, nodes_to_remove = get_sorted_metric_results(nodes_degree, graph)

        S = [compute_S_metric(graph, number_of_nodes)]

        for node in nodes_to_remove:
            graph.delete_vertices([graph.vs.find(name=node)])
            S.append(compute_S_metric(graph, number_of_nodes))

    if metric == 'closeness':
        nodes_closeness = graph.closeness()
        nodes_closeness, nodes_to_remove = get_sorted_metric_results(nodes_closeness, graph)

        S = [compute_S_metric(graph, number_of_nodes)]

        for node in nodes_to_remove:
            graph.delete_vertices([graph.vs.find(name=node)])
            S.append(compute_S_metric(graph, number_of_nodes))

    if metric == 'random':
        S = np.zeros(int(number_of_nodes / 2) + 1)
        number_of_iterations = 100
        for i in range(number_of_iterations):
            graph_random = graph.copy()
            S[0] += compute_S_metric(graph_random, number_of_nodes)
            for j in range(1, int(number_of_nodes / 2) + 1):
                node_to_remove = graph_random.vs[random.randint(0, graph_random.vcount() - 1)]
                graph_random.delete_vertices(node_to_remove)
                S[j] += compute_S_metric(graph_random, number_of_nodes)

        S /= number_of_iterations

    return S, nodes_to_remove, graph


def compute_dynamic_remove(metric, number_of_nodes, graph):

    nodes_removed = []
    S = None

    if metric == 'betweenness':
        S = [compute_S_metric(graph, number_of_nodes)]
        for i in range(1, int(number_of_nodes / 2) + 1):
            nodes_betweenness = np.asarray(graph.betweenness(directed=False)) / \
                                (((number_of_nodes - 1) * (number_of_nodes - 2)) / 2)
            nodes_betweenness, nodes_to_remove = get_sorted_metric_results(nodes_betweenness, graph)

            nodes_removed.append(nodes_to_remove[0])
            graph.delete_vertices([graph.vs.find(name=nodes_to_remove[0])])
            S.append(compute_S_metric(graph, number_of_nodes))

    if metric == 'degree':
        S = [compute_S_metric(graph, number_of_nodes)]
        for i in range(1, int(number_of_nodes / 2) + 1):
            nodes_degree = graph.degree(np.arange(number_of_nodes - i + 1))
            nodes_degree, nodes_to_remove = get_sorted_metric_results(nodes_degree, graph)

            nodes_removed.append(nodes_to_remove[0])
            graph.delete_vertices([graph.vs.find(name=nodes_to_remove[0])])
            S.append(compute_S_metric(graph, number_of_nodes))

    if metric == 'closeness':
        S = [compute_S_metric(graph, number_of_nodes)]
        '''for i in range(1, int(number_of_nodes / 2) + 1):
            nodes_closeness = graph.closeness()
            nodes_closeness, nodes_to_remove = get_sorted_metric_results(nodes_closeness, graph)

            nodes_removed.append(nodes_to_remove[0])
            graph.delete_vertices([graph.vs.find(name=nodes_to_remove[0])])
            S.append(compute_S_metric(graph, number_of_nodes))'''

    if metric == 'random':
        S = np.zeros(int(number_of_nodes / 2) + 1)
        number_of_iterations = 100
        for i in range(number_of_iterations):
            graph_random = graph.copy()
            S[0] += compute_S_metric(graph_random, number_of_nodes)
            for j in range(1, int(number_of_nodes / 2) + 1):
                node_to_remove = graph_random.vs[random.randint(0, graph_random.vcount() - 1)]
                graph_random.delete_vertices(node_to_remove)
                S[j] += compute_S_metric(graph_random, number_of_nodes)

        S /= number_of_iterations

    return S, nodes_removed, graph
