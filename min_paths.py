import pandas as pd
import igraph as ig

from utils import compute_travel_time
from graphics import create_graph_min_path, create_graph_min_path_connected


def compute_min_path(trips, stations_routes_dict, station_source,
                     station_target, start_time, day, recursion_times, stops):
    trips = trips.loc[trips[day] == 1].reset_index(drop=True). \
        drop(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'], axis=1)

    edge_list = min_path_from_station(trips, stations_routes_dict, station_source, station_target, start_time,
                                      recursion_times)

    graph = create_graph_min_path(edge_list, station_source, station_target, start_time, recursion_times,
                                  stops)
    try:
        min_path = graph.get_shortest_paths('START', to='FINISH', weights='weight', output='vpath')[0]
    except Exception:
        print("ERROR! Path not found: increase the number of switches permitted")
        exit(1)

    graph.es['min_path'] = '0'
    graph.vs['min_path'] = '0'
    graph.vs[min_path]['min_path'] = '1'
    travel_time = 0
    for index in range(1, len(min_path)):
        edge = graph.get_eid(graph.vs[min_path[index - 1]], graph.vs[min_path[index]])
        graph.es[edge]['min_path'] = '1'
        if graph.es[edge]['min_path'] == '1':
            graph.es[edge]['show_weight'] = graph.es[edge]['weight']
        else:
            graph.es[edge]['show_weight'] = ''
        travel_time += graph.es[edge]['weight']

    for vertex in graph.vs:
        if vertex['min_path'] == '1':
            vertex['show_name'] = vertex['station_name']
        else:
            vertex['show_name'] = ''

    graph.write_graphml('MinPaths//minPath_from' + station_source + 'to' + station_target + '_at' +
                        start_time.replace(':', '-') + '_on' + day + '_with' + str(recursion_times) +
                        'switches.graphml')

    print(travel_time)


def min_path_from_station(trips_init, stations_routes_dict, station_source, station_target,
                          start_time, recursion_times, prec_edges=None):
    trips = trips_init.loc[start_time < trips_init['departure_time']].reset_index(drop=True)
    edge_list = []

    if prec_edges:
        routes_to_exclude = []
        for element in prec_edges:
            if element[2] not in routes_to_exclude:
                routes_to_exclude.append(element[2])
        route_list = list(set(stations_routes_dict[int(station_source)]) - set(routes_to_exclude))
    else:
        route_list = stations_routes_dict[int(station_source)]

    for route in route_list:
        trips_in_stations_target = trips.loc[(trips['stop_id'] == int(station_target)) &
                                             (trips['route_id'] == route)]
        trips_in_stations_source = trips.loc[(trips['stop_id'] == int(station_source)) &
                                             (trips['route_id'] == route)]
        trips_in_stations = pd.concat([trips_in_stations_source, trips_in_stations_target]).sort_index()

        trips_in_stations_grouped = trips_in_stations.groupby(['trip_id'])
        trip_selected = []
        for key, item in trips_in_stations_grouped:
            if item.shape[0] == 2:
                first_row = item.iloc[0]
                second_row = item.iloc[1]
                if first_row['stop_id'] == int(station_source) and second_row['stop_id'] == int(station_target):
                    if not trip_selected or first_row['departure_time'] < \
                            trips_in_stations.loc[trip_selected[0]]['departure_time']:
                        trip_selected = [first_row.name, second_row.name]

        if trip_selected:
            trips_section = trips.loc[trip_selected[0]:trip_selected[1]]
            for index, row in trips_section.iterrows():
                if index != trips_section.index[-1]:
                    next_row = trips_section.loc[index + 1]
                    edge_list.append([row['stop_id'], next_row['stop_id'], route, row['departure_time'],
                                      next_row['departure_time'], row['trip_id']])
        elif recursion_times > 0 and not trips_in_stations_source.empty:
            trips_in_stations_source = trips_in_stations_source.sort_values(by=['departure_time'])
            first_trip_available = trips_in_stations_source.iloc[0]
            edge_list = compute_switched_trip_path(first_trip_available, trips, prec_edges, route,
                                                   start_time, stations_routes_dict, station_target,
                                                   recursion_times, edge_list)
            opposite_trip_dataframe = trips_in_stations_source[trips_in_stations_source['direction'] !=
                                                               first_trip_available['direction']]
            if opposite_trip_dataframe.shape[0] > 0:
                opposite_trip_available = opposite_trip_dataframe.iloc[0]
                edge_list = compute_switched_trip_path(opposite_trip_available, trips, prec_edges, route,
                                                       start_time, stations_routes_dict, station_target,
                                                       recursion_times, edge_list)

    return edge_list


def compute_switched_trip_path(trip_available, trips, prec_edges, route, start_time,
                               stations_routes_dict, station_target, recursion_times, edge_list):

    edge_list_tmp = []
    switch_trip_selected = trips.loc[trips['trip_id'] == int(trip_available['trip_id'])]
    switch_trip_selected = switch_trip_selected.loc[trip_available.name:]
    for index, row in switch_trip_selected.iterrows():
        if index != switch_trip_selected.index[-1]:
            next_row = switch_trip_selected.loc[index + 1]
            if prec_edges:
                prec_edges.append([row['stop_id'], next_row['stop_id'], route, row['departure_time'],
                                   next_row['departure_time'], row['trip_id']])
            else:
                prec_edges = [[row['stop_id'], next_row['stop_id'], route, row['departure_time'],
                               next_row['departure_time'], row['trip_id']]]
            edge_list_tmp = min_path_from_station(trips, stations_routes_dict, next_row['stop_id'],
                                                  station_target, row['arrival_time'],
                                                  recursion_times - 1, prec_edges)

        if edge_list_tmp:
            for edge in prec_edges:
                if edge not in edge_list:
                    edge_list.append(edge)

        for edge in edge_list_tmp:
            if edge not in edge_list:
                edge_list.append(edge)

    return edge_list


def compute_switches_from_station(station_source, routes_adjacency_dict,
                                  stations_routes_dict, routes_stations_dict):

    i = 0
    switches_from_station_dict = {int(station_source): -1}
    routes_from_stations = set(stations_routes_dict[int(station_source)])
    routes_to_exclude = set()

    while len(stations_routes_dict) != len(switches_from_station_dict):
        routes_from_stations_tmp = set()
        for route in list(routes_from_stations - routes_to_exclude):
            for station in routes_stations_dict[route]:
                if station not in switches_from_station_dict:
                    switches_from_station_dict[station] = i
            for element in routes_adjacency_dict[route]:
                routes_from_stations_tmp.add(element)
            routes_to_exclude.add(route)

        routes_from_stations = routes_from_stations_tmp.copy()
        i += 1

    return switches_from_station_dict
