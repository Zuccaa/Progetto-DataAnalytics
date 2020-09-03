import pandas as pd
import igraph as ig
import numpy as np

from graphics import plot_metric_results


def remove_nodes_analysis(graph, metric):

    number_of_nodes = graph.vcount()
    if metric == 'betweenness':
        nodes_betweenness = np.asarray(graph.betweenness(directed=False)) / \
                            (((number_of_nodes - 1) * (number_of_nodes - 2)) / 2)
        nodes_betweenness, nodes_to_remove = sort_metric_results(nodes_betweenness, graph)

    if metric == 'degree':
        nodes_degree = graph.degree(np.arange(number_of_nodes))
        nodes_degree, nodes_to_remove = sort_metric_results(nodes_degree, graph)

    S = [compute_S_metric(graph, number_of_nodes)]

    for node in nodes_to_remove:
        graph.delete_vertices([graph.vs.find(name=node)])
        S.append(compute_S_metric(graph, number_of_nodes))

    print(S)

    plot_metric_results(S)


def compute_S_metric(graph, number_of_nodes):

    number_of_nodes_of_component = len(graph.components().giant().vs)

    return number_of_nodes_of_component / number_of_nodes


def sort_metric_results(metric_results, graph):

    nodes_to_remove = []
    def take_second(elem):
        return elem[1]

    nodes_with_indexes = []
    number_of_nodes = len(metric_results)
    for i in range(number_of_nodes):
        nodes_with_indexes.append([i, nodes_with_indexes[i]])

    nodes_with_indexes.sort(key=take_second, reverse=True)

    for i in range(int(number_of_nodes / 2)):
        nodes_to_remove.append(graph.vs[nodes_with_indexes[i][0]]['name'])

    return metric_results, nodes_to_remove
