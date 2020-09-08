'''
plots(): script che gestisce la creazione dei
         plot all'interno del programma
-------------------------------------------------
Creato da:
    Stefano Zuccarella n.816482
    Matteo Paolella n.816933
'''

import json
import matplotlib.pylab as plt
import numpy as np


def plot_bars_of_loads(file, day, station, title):

    with open(file, 'r') as fp:
        data = json.load(fp)

    # Creo un dizionario a cui associare, per ogni bar, il carico della stazione in analisi
    bar_dict = {}
    day_list = data[day]

    i = 4
    for dict in day_list:
        if station in dict['Stazioni']:
            bar_dict[i] = dict['Stazioni'][station]
        else:
            bar_dict[i] = 0
        i += 1

    bar = plt.bar(np.arange(len(bar_dict.keys())) + 0.25, bar_dict.values(), color="green")
    plt.xticks(np.arange(24) - 0.25, labels=['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                                             '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                                             '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '00:00',
                                             '01:00', '02:00'], rotation='vertical')
    #plt.title(title)
    plt.xlabel("Orario")
    plt.ylabel("Numero di treni")
    counter = 0
    list_of_values = list(bar_dict.values())
    for rect in bar:
        plt.text(rect.get_x() + 0.4, rect.get_height() + 0.3, list_of_values[counter], ha='center', va='bottom')
        counter += 1

    plt.show()


def plot_metric_results(metric_results):

    # Per ogni metrica, illustro i risultati di S in relazione alla
    # percentuale di nodi rimossi nel grafo

    betweenness_results = metric_results[0]
    degree_results = metric_results[1]
    closeness_results = metric_results[2]

    plt.plot(np.arange(0, 0.5, 0.5 / len(betweenness_results)), betweenness_results, 'ro', markersize=1.5,
             linestyle='solid', linewidth=0.5)
    plt.plot(np.arange(0, 0.5, 0.5 / len(degree_results)), degree_results, 'bo', markersize=1.5,
             linestyle='solid', linewidth=0.5)
    plt.plot(np.arange(0, 0.5, 0.5 / len(closeness_results)), closeness_results, 'go', markersize=1.5,
             linestyle='solid', linewidth=0.5)

    plt.xlabel("Percentuale di nodi rimossi")
    plt.ylabel("Valore di S")
    plt.legend(('Betweenness', 'Degree', 'Closeness'))

    plt.show()


def plot_assortativity_matrix(degree_correlation_matrix):

    # Rappresento la degree correlation matrix con matshow

    plt.matshow(degree_correlation_matrix, cmap='hot')
    plt.title('Degree correlation matrix')

    plt.show()
