from utils import dict_as_group_by, import_data
import csv
import json
import matplotlib.pylab as plt
import numpy as np
import igraph as ig

def create_graph_table():
    stop_times, trips, routes, *_ = import_data()

    trips_per_route = dict_as_group_by(trips, 'route_id', 'trip_id')

    routes_dict = {}

    print("Lunghezza iniziale", len(stop_times.index))
    for key in trips_per_route.keys():
        routes_dict[key] = []
        for index, row in stop_times.iterrows():
            if row['trip_id'] in trips_per_route[key]:
                if index != stop_times.index[-1]:
                    next_row = stop_times.loc[index + 1]
                    if next_row['stop_sequence'] > row['stop_sequence']:
                        edge = {row['stop_id'], next_row['stop_id']}
                        if edge not in routes_dict[key]:
                            routes_dict[key].append(edge)
                stop_times = stop_times.drop(index)
        stop_times = stop_times.reset_index(drop=True)
        print(key, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

    save_graph_table(routes_dict, routes)

def save_graph_table(routes_dict, routes):
    with open('routes_dict.csv', 'w', newline='') as file:
        fieldnames = ['Linea', 'Stazione 1', 'Stazione 2', 'Colore']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for key in routes_dict.keys():
            selected_row = routes.loc[routes['route_id'] == key]
            color = '#' + selected_row['route_color'].values[0]
            for set_list in routes_dict[key]:
                writer.writerow({'Linea': key, 'Stazione 1': set_list.pop(),
                                 'Stazione 2': set_list.pop(), 'Colore': color})

def create_graph(stops):

    graph_definitive = ig.Graph(directed=False)
    graph_tmp = ig.Graph(directed=False)
    for index, row in stops.iterrows():
        graph_definitive.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                     lat=row['stop_lat'], lon=row['stop_lon'])
        graph_tmp.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                     lat=row['stop_lat'], lon=row['stop_lon'])

    '''for edge in G.es:
        print(edge.tuple)
        G1.add_edge(edge.tuple[0], edge.tuple[1], route=edge['route'])

    G1.delete_edges([('1707', '1581')])'''
    stop_times, trips, routes, *_ = import_data()

    trips_per_route = dict_as_group_by(trips, 'route_id', 'trip_id')

    print("Lunghezza iniziale", len(stop_times.index))
    for route in trips_per_route:
        if route == 'R3':
            linked_stops_not_consecutive = []
            for index, row in stop_times.iterrows():
                if row['trip_id'] in trips_per_route[route]:
                    if index != stop_times.index[-1]:
                        next_row = stop_times.loc[index + 1]
                        if next_row['stop_sequence'] == row['stop_sequence'] + 1 and \
                            graph_tmp.get_eid(str(row['stop_id']), str(next_row['stop_id']),
                                              directed=False, error=False) == -1:
                            graph_tmp.add_edge(str(row['stop_id']), str(next_row['stop_id']))
                            print('Arco aggiunto tra ' + str(row['stop_id']) + ' e ' +
                                  str(next_row['stop_id']))
                        elif next_row['stop_sequence'] > row['stop_sequence'] + 1 and \
                                {str(row['stop_id']), str(next_row['stop_id'])} not in linked_stops_not_consecutive:
                            linked_stops_not_consecutive.append({str(row['stop_id']), str(next_row['stop_id'])})
                    stop_times = stop_times.drop(index)
            stop_times = stop_times.reset_index(drop=True)

            for linked_stop in linked_stops_not_consecutive:
                print(linked_stop)
                node1 = linked_stop.pop()
                node2 = linked_stop.pop()
                if graph_tmp.shortest_paths_dijkstra(node1, node2)[0][0] == float('inf'):
                    graph_tmp.add_edge(node1, node2)
                    print(node1, node2)

            for edge in graph_tmp.es:
                graph_definitive.add_edge(edge.tuple[0], edge.tuple[1], route=route)

            for edge in graph_tmp.es:
                graph_tmp.delete_edges([(edge.tuple[0], edge.tuple[1])])

        print(route, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

    graph_definitive.write_graphml("TrenordNetwork.graphml")

def plot_bars_of_loads(file, day, route, title):
    with open(file, 'r') as fp:
        data = json.load(fp)

    bar_dict = {}
    day_list = data[day]

    i = 4
    for dict in day_list:
        if route in dict['Stazioni']:
            bar_dict[i] = dict['Stazioni'][route]
        else:
            bar_dict[i] = 0
        i += 1

    bar = plt.bar(np.arange(len(bar_dict.keys())) + 0.25, bar_dict.values(), color="green")
    plt.xticks(np.arange(24) - 0.25, labels=['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                                             '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                                             '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '00:00',
                                             '01:00', '02:00'], rotation='vertical')
    plt.title(title)
    plt.xlabel("Orario")
    plt.ylabel("Numero di treni")
    counter = 0
    list_of_values = list(bar_dict.values())
    for rect in bar:
        plt.text(rect.get_x() + 0.4, rect.get_height() + 0.3, list_of_values[counter], ha='center', va='bottom')
        counter += 1

    plt.show()