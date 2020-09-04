import numpy as np
from graphics import plot_assortativity_matrix

def compute_assortativity(graph, degree_results):

    size = max(degree_results) + 1
    degree_correlation_matrix = np.zeros((size, size))

    for edge in graph.es:
        degree_node1 = degree_results[edge.tuple[0]]
        degree_node2 = degree_results[edge.tuple[1]]
        degree_correlation_matrix[degree_node1, degree_node2] += 1
        if degree_node1 != degree_node2:
            degree_correlation_matrix[degree_node2, degree_node1] += 1

    sum_values = sum(sum(degree_correlation_matrix))
    degree_correlation_matrix = degree_correlation_matrix / sum_values
    print(degree_correlation_matrix)

    plot_assortativity_matrix(degree_correlation_matrix)