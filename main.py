'''
main(): script da runnare per eseguire il codice
-------------------------------------------------
Creato da:
    Stefano Zuccarella n.816482
    Matteo Paolella n.816933
'''

from attack_handling import remove_nodes_analysis
from graphs import create_graph_for_loads, create_graph_with_switches
from load_analysis import compute_loads_with_exceptions
from min_paths import compute_min_path, compute_switches_from_station
from utils import dict_as_group_by, import_data, create_routes_adjacency_dict, import_graphs
from pre_analysis import compute_assortativity
from plots import plot_bars_of_loads

import numpy as np


def do_pre_analysis(graph):

    # Calcolo il numero di edge per il grafo con un solo link tra stazioni
    degree_results = graph.degree((np.arange(graph.vcount())))

    # Analizzo se la rete è assortativa o meno
    compute_assortativity(graph, degree_results)


def do_load_analysis(station, day, exceptions_service, stops, trips_with_stop_times):

    # Creo un dizionario per avere i servizi cancellati con i relativi giorni di annullamento
    '''exceptions_service_dict = dict_as_group_by(exceptions_service, 'service_id', 'date')
    for element in exceptions_service_dict:
        exceptions_service_dict[element] = str(exceptions_service_dict[element])'''

    # Codice eseguito per avere dei file già pronti, visto che ci vogliono
    # diversi minuti per creare un singolo file
    '''week = [52, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 49]
    for w in week:
        if w == 52:
            print('Settimana ' + str(w) + " dell'anno 2018 in corso")
            compute_loads_with_exceptions(trips_with_stop_times, exceptions_service_dict, 2018, w)
        else:
            print('Settimana ' + str(w) + " dell'anno 2019 in corso")
            compute_loads_with_exceptions(trips_with_stop_times, exceptions_service_dict, 2019, w)
        print('FATTO!')
        print('-----------------------------------------------------------')'''

    week = 10
    year = 2019
    # Riga commentata in quanto i file sono già disponibili
    # compute_loads_with_exceptions(trips_with_stop_times, exceptions_service_dict, year, week)

    file_with_exceptions = 'Carichi//loads_complete_with_exceptions_' + str(year) + str(week) + '.json'

    # Illustro su un plot i risultati
    plot_bars_of_loads(file_with_exceptions, day, station, 'Carico di Monza (' + day + ')')

    # Creo un grafo contenente tutti i trip con i relativi percorsi
    # create_graph_for_loads(trips_with_stop_times, stops)


def do_min_path_analysis(station_source, station_target, hour, day, number_of_switches,
                         trips_with_stop_times, stops, stop_times, trips, graph):

    # Creo un dizionario con chiave la stazione e con valori le linee
    # che passano in quella stazione
    stations_routes_dict = dict_as_group_by(trips_with_stop_times, 'stop_id', 'route_id', repetition=False)

    # Calcolo il cammino minimo tra due stazioni e creo il grafo relativo
    compute_min_path(trips_with_stop_times.copy(), stations_routes_dict, station_source, station_target,
                     hour, day, number_of_switches, stops)

    # Creo un dizionario con chiave la linea e con valori le fermate
    # in cui passa quella linea
    routes_stations_dict = dict_as_group_by(trips_with_stop_times, 'route_id', 'stop_id', repetition=False)

    # Creo un dizionario con chiave la linea e con valori le altre linee
    # raggiungibili da quella linea
    routes_adjacency_dict = create_routes_adjacency_dict(stations_routes_dict, routes_stations_dict)

    # Creo un dizionario in cui per ogni stazione viene associato il numero
    # minimo di cambi da dover fare per raggiungerla a partire da una
    # particolare stazione
    switches_from_station_dict = compute_switches_from_station('1728', routes_adjacency_dict,
                                                               stations_routes_dict,
                                                               routes_stations_dict)
    create_graph_with_switches(graph, switches_from_station_dict)


def do_attack_handling_analysis(graph, graph_no_multiple_edges):

    # Analizzo i casi in cui vengono rimossi nodi in base alla metrica scelta
    metrics = ['betweenness', 'degree', 'closeness', 'random']
    remove_nodes_analysis(graph, graph_no_multiple_edges, metrics)


def main():

    # Importo le tabelle del dataset e i grafi
    stop_times, trips, routes, exceptions_service, calendar, stops, trips_with_stop_times = import_data()
    stop_times_load = stop_times.copy().drop(['stop_sequence'], axis=1)

    graph_with_routes, graph_no_multiple_edges = import_graphs('XML files//Complete_TrenordNetwork.xml',
                                                               'XML files//CompleteGraph_NoMultipleEdges.xml')

    # Svolgo le varie fasi dell'analisi
    print('Pre analisi in corso')
    do_pre_analysis(graph_with_routes)
    print('Studio dei carichi in corso')
    do_load_analysis('1841', 'monday', exceptions_service, stops, trips_with_stop_times)
    print('Studio dei percorsi minimi in corso')
    do_min_path_analysis('1581', '1711', '09:00:00', 'monday', 0, trips_with_stop_times, stops, stop_times,
                         trips, graph_no_multiple_edges)
    print('Studio della gestione degli attacchi in corso')
    do_attack_handling_analysis(graph_with_routes, graph_no_multiple_edges)
    print('Fine!')


if __name__ == "__main__":
    main()
