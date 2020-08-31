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


def create_graph_min_path(edge_list, station_source, station_target, start_time, day, recursion_times):

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
        g.add_edge(node2, node1, route=edge[2], departure_time=edge[3], arrival_time=edge[4], trip=trip)
        g.vs.find(name=node2)['arrival_time'] = edge[4]
        g.vs.find(name=node1)['departure_time'] = edge[3]

    g = connect_trips(g, station_source, station_target, start_time, recursion_times)

    g.write_graphml('minPath_from' + station_source + 'to' + station_target + '_at' +
                    start_time.replace(':', '-') + '_on' + day + '_with' + str(recursion_times) +
                    'switches.graphml')


def connect_trips(graph, station_source, station_target, start_time, number_of_switches):

    clusters = graph.components(mode='WEAK')
    graph.add_vertex(name='START')
    graph.add_vertex(name='FINISH')

    clusters_dict = {'START': [], 'FINISH': [], 'NOTHING': []}
    for cluster in clusters:
        cluster = sort_cluster(cluster, graph)
        nothing = True
        vertex_attributes = graph.vs[cluster[0]].attributes()
        vertex_name = vertex_attributes['name']
        if vertex_name[:vertex_name.find('-')] == station_source:
            edge_attributes = graph.es[graph.get_eid(graph.vs[cluster[1]], graph.vs[cluster[0]])].attributes()
            graph.add_edge(vertex_name, 'START', route='-', departure_time=start_time,
                           arrival_time=edge_attributes['departure_time'], trip=edge_attributes['trip'])
            graph.vs.find(name=vertex_name)['arrival_time'] = edge_attributes['departure_time']
            graph.vs.find(name='START')['departure_time'] = start_time
            clusters_dict['START'].append(cluster)
            nothing = False

        vertex_attributes = graph.vs[cluster[len(cluster) - 1]].attributes()
        vertex_name = vertex_attributes['name']
        if vertex_name[:vertex_name.find('-')] == station_target:
            edge_attributes = graph.es[graph.get_eid(graph.vs[cluster[len(cluster) - 1]],
                                                        graph.vs[cluster[len(cluster) - 2]])].attributes()
            graph.add_edge('FINISH', vertex_name, route='-', departure_time=edge_attributes['arrival_time'],
                            arrival_time=edge_attributes['arrival_time'], trip=edge_attributes['trip'])
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
    print(sorted_cluster)
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
            clusters_dict['START'].add(cluster_list)
            clusters_dict['NOTHING'].remove(cluster_list)
        create_additional_edges(graph, clusters_dict, number_of_switches - 1)


def connect_clusters(graph, clusters1, clusters2):

    clusters_linked = set()
    if clusters2:
        for cluster in clusters1:
            for node in cluster:
                for f_cluster in clusters2:
                    for f_node in f_cluster:
                        source = graph.vs[node].attributes()
                        target = graph.vs[f_node].attributes()
                        if source['name'][:source['name'].find('-')] == \
                                target['name'][:target['name'].find('-')]:
                            if source['arrival_time'] < target['departure_time']:
                                graph.add_edge(target['name'], source['name'], route='switch',
                                               departure_time=source['arrival_time'],
                                               arrival_time=target['departure_time'], trip=None)
                                graph.vs.find(name=target['name'])['arrival_time'] = source['arrival_time']
                                graph.vs.find(name=source['name'])['departure_time'] = target['departure_time']

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
        g.add_edge(node2, node1, route=edge[2], departure_time=edge[3], arrival_time=edge[4], trip=trip)

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