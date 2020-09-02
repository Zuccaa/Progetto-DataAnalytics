import pandas as pd
import subprocess
import datetime

def dict_as_group_by(dataframe, key_field, value_field, repetition=True):
    dict_grouped_by = {}
    for index, row in dataframe.iterrows():
        key = row[key_field]
        if key in dict_grouped_by:
            if repetition or row[value_field] not in dict_grouped_by[key]:
                dict_grouped_by[key].append(row[value_field])
        else:
            dict_grouped_by[key] = [row[value_field]]
    return dict_grouped_by

def import_data():
    stop_times = pd.read_csv('trenord-gtfs-csv//stop_times.csv')
    stop_times = stop_times.drop(['stop_headsign', 'pickup_type',
                                  'drop_off_type', 'shape_dist_traveled'], axis=1)
    stop_times = stop_times.sort_values(by=['trip_id', 'stop_sequence']).reset_index(drop=True)

    trips = pd.read_csv('trenord-gtfs-csv//trips.csv')
    trips = trips.drop(['trip_headsign', 'trip_short_name', 'direction_id', 'block_id', 'shape_id'], axis=1)

    routes = pd.read_csv('trenord-gtfs-csv//routes.csv')
    routes = routes.drop(['agency_id', 'route_short_name', 'route_desc', 'route_type', 'route_url',
                          'route_text_color'], axis=1)

    exceptions_service = pd.read_csv('trenord-gtfs-csv//calendar_dates.csv')
    exceptions_service = exceptions_service.drop(['exception_type'], axis=1)

    calendar = pd.read_csv('trenord-gtfs-csv//calendar.csv')
    calendar = calendar.drop(['start_date', 'end_date'], axis=1)

    stops = pd.read_csv('trenord-gtfs-csv//stops.csv')
    stops = stops.drop(['stop_code', 'stop_desc', 'stop_url', 'location_type', 'parent_station'], axis=1)

    trips_with_stop_times = pd.read_csv('trenord-gtfs-csv//trips_with_stop_times.csv')

    return stop_times, trips, routes, exceptions_service, calendar, stops, trips_with_stop_times


def compute_travel_time(departure_time, arrival_time):

    departure_time_in_seconds = datetime.timedelta(hours=int(departure_time[0:2]),
                                                   minutes=int(departure_time[3:5]),
                                                   seconds=int(departure_time[6:8])).total_seconds()
    arrival_time_in_seconds = datetime.timedelta(hours=int(arrival_time[0:2]),
                                                 minutes=int(arrival_time[3:5]),
                                                 seconds=int(arrival_time[6:8])).total_seconds()
    travel_time_in_seconds = arrival_time_in_seconds - departure_time_in_seconds

    return travel_time_in_seconds / 60


def add_direction_column(dataframe):
    dataframe['direction'] = -1
    dataframe_grouped = dataframe.groupby(['trip_id'])
    dataframe_list = []

    for key, item in dataframe_grouped:
        dataframe_list.append([item, item.shape[0]])

    def take_second(elem):
        return elem[1]

    dataframe_list.sort(key=take_second, reverse=True)
    dataframe_dict = {}

    for element in dataframe_list:
        dataframe_tmp = element[0]
        f_row = dataframe_tmp.iloc[0]
        first_in_dict = False
        pair_already_in = False
        if f_row['route_id'] not in dataframe_dict.keys():
            first_in_dict = True
            dataframe_dict[f_row['route_id']] = []
        for index, row in dataframe_tmp.iterrows():
            if index != dataframe_tmp.index[-1]:
                n_row = dataframe_tmp.loc[index + 1]
                route_in_dict = dataframe_dict[row['route_id']]
                pair = [row['stop_id'], n_row['stop_id']]
                if first_in_dict:
                    route_in_dict.append(pair)
                    dataframe.loc[index, 'direction'] = 0
                    dataframe.loc[index + 1, 'direction'] = 0
                else:
                    if pair in route_in_dict:
                        pair_already_in = True

        for index, row in dataframe_tmp.iterrows():
            if not first_in_dict:
                if pair_already_in:
                    dataframe.loc[index, 'direction'] = 0
                else:
                    dataframe.loc[index, 'direction'] = 1

    dataframe.to_csv('trenord-gtfs-csv//trips_with_stop_times.csv', index=False, header=True)


def create_routes_adjacency_dict(stations_routes_dict, routes_stations_dict):

    routes_adjacency_dict = {}

    for route in routes_stations_dict:
        routes_set = set()
        for station in routes_stations_dict[route]:
            routes_on_station = stations_routes_dict[station]
            for element in routes_on_station:
                if element is not route:
                    routes_set.add(element)
        routes_adjacency_dict[route] = routes_set.copy()

    return routes_adjacency_dict