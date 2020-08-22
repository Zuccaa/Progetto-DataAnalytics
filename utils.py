import pandas as pd

def dict_as_group_by(dataframe, key_field, value_field):
    dict_grouped_by = {}
    for index, row in dataframe.iterrows():
        key = row[key_field]
        if key in dict_grouped_by:
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

    return stop_times, trips, routes, exceptions_service, calendar