import pandas as pd
import igraph as ig

from utils import compute_travel_time
from graphics import create_graph_min_path


def compute_min_path(trips, stations_routes_dict, station_source,
                     station_target, start_time, day, number_of_switches):

    trips = trips.loc[trips[day] == 1].reset_index(drop=True).\
        drop(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'], axis=1)

    edge_list = min_path_from_station(trips, stations_routes_dict, station_source, station_target, start_time,
                                      number_of_switches)

    print(edge_list)

    create_graph_min_path(edge_list, station_source, station_target, start_time, day, number_of_switches)


def min_path_from_station(trips_init, stations_routes_dict, station_source, station_target,
                          start_time, number_of_switches, prec_edges=None):

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
                                      next_row['arrival_time'], row['trip_id']])
        elif number_of_switches > 0 and not trips_in_stations_source.empty:
            trips_in_stations_source = trips_in_stations_source.sort_values(by=['departure_time'])
            first_trip_available = trips_in_stations_source.iloc[0]
            edge_list = compute_switched_trip_path(first_trip_available, trips, prec_edges, route,
                                                   start_time, stations_routes_dict, station_target,
                                                   number_of_switches, edge_list)
            opposite_trip_dataframe = trips_in_stations_source[trips_in_stations_source['direction'] !=
                                        first_trip_available['direction']]
            if opposite_trip_dataframe.shape[0] > 0:
                opposite_trip_available = opposite_trip_dataframe.iloc[0]
                edge_list = compute_switched_trip_path(opposite_trip_available, trips, prec_edges, route,
                                                       start_time, stations_routes_dict, station_target,
                                                       number_of_switches, edge_list)

    return edge_list


def compute_switched_trip_path(trip_available, trips, prec_edges, route, start_time,
                               stations_routes_dict, station_target, number_of_switches, edge_list):

    edge_list_tmp = []
    switch_trip_selected = trips.loc[trips['trip_id'] == int(trip_available['trip_id'])]
    switch_trip_selected = switch_trip_selected.loc[trip_available.name:]
    for index, row in switch_trip_selected.iterrows():
        if index != switch_trip_selected.index[-1]:
            next_row = switch_trip_selected.loc[index + 1]
            if prec_edges:
                prec_edges.append([row['stop_id'], next_row['stop_id'], route, row['departure_time'],
                                   next_row['arrival_time'], row['trip_id']])
            else:
                prec_edges = [[row['stop_id'], next_row['stop_id'], route, row['departure_time'],
                                   next_row['arrival_time'], row['trip_id']]]
            edge_list_tmp = min_path_from_station(trips, stations_routes_dict, next_row['stop_id'],
                                                  station_target, row['arrival_time'],
                                                  number_of_switches - 1, prec_edges)

        if edge_list_tmp:
            for edge in prec_edges:
                if edge not in edge_list:
                    edge_list.append(edge)

        for edge in edge_list_tmp:
            if edge not in edge_list:
                edge_list.append(edge)

    return edge_list