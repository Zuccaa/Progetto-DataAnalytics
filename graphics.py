from utils import dict_as_group_by, import_data
import csv
import json
import matplotlib.pylab as plt
import numpy as np
import igraph as ig

def create_graph(stops):

    graph_definitive = ig.Graph(directed=False)
    graph_tmp = ig.Graph(directed=False)
    for index, row in stops.iterrows():
        graph_definitive.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                     lat=row['stop_lat'], lon=row['stop_lon'])
        graph_tmp.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                     lat=row['stop_lat'], lon=row['stop_lon'])

    stop_times, trips, routes, *_ = import_data()

    trips_per_route = dict_as_group_by(trips, 'route_id', 'trip_id')

    print("Lunghezza iniziale", len(stop_times.index))

    def take_second(elem):
        return elem[1]

    for route in trips_per_route:
        linked_stops_not_consecutive = []
        for index, row in stop_times.iterrows():
            if row['trip_id'] in trips_per_route[route]:
                if index != stop_times.index[-1]:
                    next_row = stop_times.loc[index + 1]
                    if next_row['stop_sequence'] == row['stop_sequence'] + 1 and \
                        graph_tmp.get_eid(str(row['stop_id']), str(next_row['stop_id']),
                                            directed=False, error=False) == -1:
                        graph_tmp.add_edge(str(row['stop_id']), str(next_row['stop_id']))
                    elif next_row['stop_sequence'] > row['stop_sequence'] + 1 and (
                            not linked_stops_not_consecutive or
                            {str(row['stop_id']), str(next_row['stop_id'])}
                            not in list(list(zip(*linked_stops_not_consecutive))[0])):
                        linked_stops_not_consecutive.append([
                            {str(row['stop_id']), str(next_row['stop_id'])},
                            next_row['stop_sequence'] - row['stop_sequence']])
                stop_times = stop_times.drop(index)
        stop_times = stop_times.reset_index(drop=True)

        linked_stops_not_consecutive.sort(key=take_second)

        for linked_stop in linked_stops_not_consecutive:
            node1 = linked_stop[0].pop()
            node2 = linked_stop[0].pop()
            if graph_tmp.shortest_paths_dijkstra(node1, node2)[0][0] == float('inf'):
                graph_tmp.add_edge(node1, node2)

        color = '#' + str(routes.loc[routes['route_id'] == route]['route_color'].values[0])
        for edge in graph_tmp.es:
            graph_definitive.add_edge(edge.tuple[0], edge.tuple[1], route=route, color=color)

        graph_tmp.delete_edges(graph_tmp.es)

        print(route, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

    graph_definitive.write_graphml("TrenordNetwork1.graphml")

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