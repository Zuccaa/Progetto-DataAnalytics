'''
pre_analysis(): script che gestisce la creazione
                della degree correlation matrix
----------------------------------------------------------
Creato da:
    Stefano Zuccarella n.816482
    Matteo Paolella n.816933
'''

import numpy as np
from plots import plot_assortativity_matrix


def compute_assortativity(graph, degree_results):

    size = max(degree_results) + 1
    degree_correlation_matrix = np.zeros((size, size))

    # Riempio la degree correlation matrix
    for edge in graph.es:
        degree_node1 = degree_results[edge.tuple[0]]
        degree_node2 = degree_results[edge.tuple[1]]
        degree_correlation_matrix[degree_node1, degree_node2] += 1
        if degree_node1 != degree_node2:
            degree_correlation_matrix[degree_node2, degree_node1] += 1

    # Normalizzo la matrice
    sum_values = sum(sum(degree_correlation_matrix))
    degree_correlation_matrix = degree_correlation_matrix / sum_values

    # Plotto la matrice
    plot_assortativity_matrix(degree_correlation_matrix)
