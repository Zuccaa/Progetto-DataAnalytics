import pandas as pd
import igraph as ig

from utils import compute_travel_time


def compute_min_path(trips, stations_routes_dict, station_source,
                     station_target, start_time, day, number_of_switches):
    indexes_to_remove = []
    for index, row in trips.iterrows():
        if start_time > row['departure_time'] or row[day] != 1:
            indexes_to_remove.append(index)

    trips = trips.drop(indexes_to_remove).reset_index(drop=True)
    trips = trips.drop(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'], axis=1)

    edge_list = min_path_from_station(trips, stations_routes_dict, station_source,
                              station_target, start_time, number_of_switches)

def min_path_from_station(trips, stations_routes_dict, station_source, station_target,
                          start_time, number_of_switches):
    edge_list = []
    for route in stations_routes_dict[station_source]:
        trips_in_stations = trips.loc[((trips['stop_id'] == int(station_source)) |
                                      (trips['stop_id'] == int(station_target))) & (trips['route_id'] == route)]
        trips_in_stations_grouped = trips_in_stations.groupby(['trip_id'])
        trip_selected = []
        for key, item in trips_in_stations_grouped:
            if item.shape[0] == 2:
                first_row = item.iloc[0]
                second_row = item.iloc[1]
                if first_row['stop_id'] == station_source and second_row['stop_id'] == station_target:
                    if not trip_selected or first_row['departure_time'] < \
                            trips_in_stations.loc[trip_selected[0]]['departure_time']:
                        trip_selected = [first_row.name, second_row.name]

        if not trip_selected:
            trips_section = trips.loc[trip_selected[0]:trip_selected[1] + 1]
            for index, row in trips_section.iterrows():
                if index != trips.section.index[-1]:
                    next_row = trips_section.loc[index + 1]
                    weight_edge = compute_travel_time(row['departure_time'], next_row['arrival_time'])
                    edge_list.append([row['stop_id'], next_row['stop_id'], route, weight_edge])

        return edge_list