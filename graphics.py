from utils import dict_as_group_by, import_data, compute_travel_time
import csv
import json
import matplotlib.pylab as plt
import numpy as np
import igraph as ig
import random
import datetime


def create_graph(stops):

    colors_used = set()
    graph_definitive = ig.Graph(directed=False)
    graph_tmp = ig.Graph(directed=False)
    for index, row in stops.iterrows():
        graph_definitive.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                     lat=row['stop_lat'] * -4200, lon=row['stop_lon'] * 4200)
        graph_tmp.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                     lat=row['stop_lat'] * -4200, lon=row['stop_lon'] * 4200)

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

        while True:
            color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            if color not in colors_used:
                colors_used.add(color)
                break

        for edge in graph_tmp.es:
            graph_definitive.add_edge(edge.tuple[0], edge.tuple[1], route=route, color=color)

        graph_tmp.delete_edges(graph_tmp.es)

        print(route, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

    graph_definitive.write_graphml("Complete_TrenordNetwork.graphml")

    return graph_definitive


def create_graph_with_switches(switches_from_station_dict, stops):

    station_source = str(list(switches_from_station_dict.keys())[0])

    graph_definitive = ig.Graph(directed=False)
    graph_tmp = ig.Graph(directed=False)
    for index, row in stops.iterrows():
        graph_definitive.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                                    lat=row['stop_lat'] * -4200, lon=row['stop_lon'] * 4200,
                                    switch=switches_from_station_dict[row['stop_id']], show_name='')
        graph_tmp.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                             lat=row['stop_lat'] * -4200, lon=row['stop_lon'] * 4200,
                             switch=switches_from_station_dict[row['stop_id']], show_name='')

    stop_times, trips, routes, *_ = import_data()

    trips_per_route = dict_as_group_by(trips, 'route_id', 'trip_id')

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
            index = graph_definitive.get_eid(edge.tuple[0], edge.tuple[1],
                                                            directed=False, error=False)
            if index == -1:
                graph_definitive.add_edge(edge.tuple[0], edge.tuple[1])

        graph_tmp.delete_edges(graph_tmp.es)

        print(route, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

    graph_definitive.vs.find(name=station_source)['show_name'] = station_source

    graph_definitive.write_graphml(str(list(switches_from_station_dict.keys())[0]) + "_graph.graphml")


def create_graph_min_path(edge_list, station_source, station_target, start_time, recursion_times, stops):

    g = ig.Graph(directed=True)

    for edge in edge_list:
        trip = str(edge[5])
        node1 = str(edge[0]) + '-' + trip
        node2 = str(edge[1]) + '-' + trip
        if not g.vs:
            g.add_vertex(name=node1)
            g.add_vertex(name=node2)
        if node1 not in g.vs['name']:
            g.add_vertex(name=node1)
        if node2 not in g.vs['name']:
            g.add_vertex(name=node2)
        g.add_edge(node1, node2, route=edge[2], departure_time=edge[3], arrival_time=edge[4], trip=trip,
                   weight=compute_travel_time(edge[3], edge[4]))
        g.vs.find(name=node2)['arrival_time'] = edge[4]
        g.vs.find(name=node2)['station_name'] = stops.loc[stops['stop_id'] == edge[1]]['stop_name'].values[0]
        g.vs.find(name=node1)['departure_time'] = edge[3]
        g.vs.find(name=node1)['station_name'] = stops.loc[stops['stop_id'] == edge[0]]['stop_name'].values[0]
    g = connect_trips(g, station_source, station_target, start_time, recursion_times)

    return g


def connect_trips(graph, station_source, station_target, start_time, number_of_switches):

    clusters = graph.components(mode='WEAK')
    graph.add_vertex(name='START')
    graph.vs.find(name='START')['station_name'] = 'START'
    graph.add_vertex(name='FINISH')
    graph.vs.find(name='FINISH')['station_name'] = 'FINISH'

    clusters_dict = {'START': [], 'FINISH': [], 'NOTHING': []}
    for cluster in clusters:
        cluster = sort_cluster(cluster, graph)
        nothing = True
        vertex_attributes = graph.vs[cluster[0]].attributes()
        vertex_name = vertex_attributes['name']
        if vertex_name[:vertex_name.find('-')] == station_source:
            edge_attributes = graph.es[graph.get_eid(graph.vs[cluster[0]], graph.vs[cluster[1]])].attributes()
            graph.add_edge('START', vertex_name, route='-', departure_time=start_time,
                           arrival_time=edge_attributes['departure_time'], trip=edge_attributes['trip'],
                           weight=compute_travel_time(start_time, edge_attributes['departure_time']))
            graph.vs.find(name=vertex_name)['arrival_time'] = edge_attributes['departure_time']
            graph.vs.find(name='START')['departure_time'] = start_time
            clusters_dict['START'].append(cluster)
            nothing = False

        vertex_attributes = graph.vs[cluster[len(cluster) - 1]].attributes()
        vertex_name = vertex_attributes['name']
        if vertex_name[:vertex_name.find('-')] == station_target:
            edge_attributes = graph.es[graph.get_eid(graph.vs[cluster[len(cluster) - 2]],
                                                        graph.vs[cluster[len(cluster) - 1]])].attributes()
            graph.add_edge(vertex_name, 'FINISH', route='-', departure_time=edge_attributes['arrival_time'],
                           arrival_time=edge_attributes['arrival_time'], trip=edge_attributes['trip'],
                           weight=0)
            graph.vs.find(name='FINISH')['arrival_time'] = edge_attributes['arrival_time']
            graph.vs.find(name=vertex_name)['departure_time'] = edge_attributes['arrival_time']
            if nothing:
                clusters_dict['FINISH'].append(cluster)
                nothing = False

        if nothing:
            clusters_dict['NOTHING'].append(cluster)

    create_additional_edges(graph, clusters_dict, number_of_switches)

    return graph


def sort_cluster(cluster, graph):

    sorted_cluster = []
    for node in cluster:
        arrival_time = graph.vs[node].attributes()['arrival_time']
        if arrival_time:
            sorted_cluster.append([node, arrival_time])
        else:
            sorted_cluster.append([node, '00:00:00'])

    def take_second(elem):
        return elem[1]

    sorted_cluster.sort(key=take_second)
    return list(list(zip(*sorted_cluster))[0])


def create_additional_edges(graph, clusters_dict, number_of_switches):

    if number_of_switches == 0:
        return
    if number_of_switches == 1:
        _ = connect_clusters(graph, clusters_dict['START'], clusters_dict['FINISH'])
        return
    if number_of_switches > 1:
        clusters_linked = connect_clusters(graph, clusters_dict['START'], clusters_dict['NOTHING'])
        for cluster in clusters_linked:
            cluster_list = list(cluster)
            clusters_dict['START'].append(cluster_list)
            clusters_dict['NOTHING'].remove(cluster_list)
        create_additional_edges(graph, clusters_dict, number_of_switches - 1)


def connect_clusters(graph, clusters1, clusters2):

    clusters_linked = set()
    if clusters2:
        for cluster in clusters1:
            for node in cluster:
                source = graph.vs[node].attributes()
                name_source = source['name'][:source['name'].find('-')]
                for f_cluster in clusters2:
                    for f_node in f_cluster:
                        target = graph.vs[f_node].attributes()
                        if name_source == \
                                target['name'][:target['name'].find('-')]:
                            if target['departure_time'] and source['arrival_time'] and \
                                        source['arrival_time'] < target['departure_time']:
                                graph.add_edge(source['name'], target['name'], route='switch',
                                               departure_time=source['arrival_time'],
                                               arrival_time=target['departure_time'], trip=None,
                                               weight=compute_travel_time(source['arrival_time'],
                                                                          target['departure_time']))

                                clusters_linked.add(tuple(f_cluster))

    return clusters_linked


def create_graph_min_path_connected(edge_list, station_source, station_target, start_time, day,
                                    number_of_switches):

    g = ig.Graph(directed=True)

    for edge in edge_list:
        trip = str(edge[5])
        node1 = str(edge[0])
        node2 = str(edge[1])
        if not g.vs:
            g.add_vertex(name=node1)
            g.add_vertex(name=node2)
        if node1 not in g.vs['name']:
            g.add_vertex(name=node1)
        if node2 not in g.vs['name']:
            g.add_vertex(name=node2)
        g.add_edge(node1, node2, route=edge[2], departure_time=edge[3], arrival_time=edge[4], trip=trip,
                   weight=compute_travel_time(edge[3], edge[4]))

    g.write_graphml('minPath_from' + station_source + 'to' + station_target + '_at' +
                    start_time.replace(':', '-') + '_on' + day + '_with' + str(number_of_switches) +
                    'switches_CONNECTED.graphml')


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


def plot_metric_results(metric_results):

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

    plt.matshow(degree_correlation_matrix, cmap='hot')
    plt.title('Degree correlation matrix')

    plt.show()


def create_graph_for_loads(loads_dataframe, stops):

    graph = ig.Graph(directed=True)

    for index, row in stops.iterrows():
        graph.add_vertex(name=str(row['stop_id']), long_name=row['stop_name'],
                         lat=row['stop_lat'] * -4200,
                         lon=row['stop_lon'] * 4200)

    loads_grouped_by_trip = loads_dataframe.groupby(['trip_id'])
    for key, item in loads_grouped_by_trip:
        for index, row in item.iterrows():
            if index != item.index[-1]:
                next_row = item.loc[index + 1]
                departure_time = row['departure_time']
                departure_time = datetime.timedelta(hours=int(departure_time[0:2]),
                                                    minutes=int(departure_time[3:5]),
                                                    seconds=int(departure_time[6:8])).total_seconds()
                arrival_time = next_row['arrival_time']
                arrival_time = datetime.timedelta(hours=int(arrival_time[0:2]),
                                                  minutes=int(arrival_time[3:5]),
                                                  seconds=int(arrival_time[6:8])).total_seconds()

                graph.add_edge(str(row['stop_id']), str(next_row['stop_id']), trip_id=str(row['trip_id']),
                               departure_time=departure_time, arrival_time=arrival_time,
                               route=row['route_id'], monday=int(row['monday']), tuesday=int(row['tuesday']),
                               wednesday=int(row['wednesday']), thursday=int(row['thursday']),
                               friday=int(row['friday']), saturday=int(row['saturday']),
                               sunday=int(row['sunday']))

    graph.write_graphml('Loads_Trenord.graphml')


def create_graph_for_attack_handling(graph_no_multiple_edges, nodes_to_remove, graphs):

    metrics = ['betweenness', 'degree', 'closeness']
    for index, metric in enumerate(metrics):
        attribute = metric + '_results'
        for vertex in nodes_to_remove[index]:
            graph_no_multiple_edges.vs.find(name=vertex)[attribute] = 1
        for vertex in graphs[index].components().giant().vs:
            print(vertex.name)
            graph_no_multiple_edges.vs.find(name=vertex)[attribute] = 2

    graph_no_multiple_edges.write_graphml('AttackHandling_Trenord.graphml')
