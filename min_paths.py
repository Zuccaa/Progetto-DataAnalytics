import pandas as pd
import igraph as ig

from utils import compute_travel_time


def compute_min_path(trips, stations_routes_dict, station_source,
                     station_target, start_time, day, number_of_switches):

    trips = trips.loc[trips[day] == 1].reset_index(drop=True).\
        drop(['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'], axis=1)

    edge_list = min_path_from_station(trips, stations_routes_dict, station_source, station_target, start_time,
                                      number_of_switches)

    return edge_list

def min_path_from_station(trips_init, stations_routes_dict, station_source, station_target,
                          start_time, number_of_switches, routes_to_exclude=None):

    trips = trips_init.loc[start_time < trips_init['departure_time']].reset_index(drop=True)
    edge_list = []
    if routes_to_exclude:
        route_list = list(set(stations_routes_dict[int(station_source)]) - routes_to_exclude)
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

        print(trip_selected)
        if trip_selected:
            trips_section = trips.loc[trip_selected[0]:trip_selected[1]]
            offset = True
            for index, row in trips_section.iterrows():
                if index != trips_section.index[-1]:
                    next_row = trips_section.loc[index + 1]
                    weight_edge = compute_travel_time(row['departure_time'], next_row['arrival_time'])
                    if offset:
                        weight_edge += compute_travel_time(start_time, row['departure_time'])
                        offset = False
                    else:
                        weight_edge += compute_travel_time(row['arrival_time'], row['departure_time'])
                    edge_list.append([row['stop_id'], next_row['stop_id'], route, weight_edge, row['trip_id']])
        elif number_of_switches > 0 and not trips_in_stations_source.empty:
            trips_in_stations_source = trips_in_stations_source.sort_values(by=['departure_time'])
            first_trip_available = trips_in_stations_source.iloc[0]
            switch_trip_selected = trips.loc[trips['trip_id'] == int(first_trip_available['trip_id'])]
            switch_trip_selected = switch_trip_selected.loc[first_trip_available.name:]
            if routes_to_exclude:
                routes_to_exclude.add(route)
            else:
                routes_to_exclude = {route}
            offset = True
            for index, row in switch_trip_selected.iterrows():
                if index != switch_trip_selected.index[-1]:
                    next_row = switch_trip_selected.loc[index + 1]
                    weight_edge = compute_travel_time(row['departure_time'], next_row['arrival_time'])
                    if offset:
                        weight_edge += compute_travel_time(start_time, row['departure_time'])
                        offset = False
                    else:
                        weight_edge += compute_travel_time(row['arrival_time'], row['departure_time'])
                    edge_list_tmp = min_path_from_station(trips, stations_routes_dict, next_row['stop_id'],
                                                          station_target, row['arrival_time'],
                                                          number_of_switches - 1, routes_to_exclude)
                    if edge_list_tmp:
                        edge_list.append([row['stop_id'], next_row['stop_id'], route, weight_edge, row['trip_id']])

                for edge in edge_list_tmp:
                    if edge not in edge_list:
                        edge_list.append(edge)

    return edge_list