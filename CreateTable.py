import pandas as pd
import numpy as np

stop_times = pd.read_csv('trenord-gtfs-csv//stop_times.csv')
stop_times = stop_times.drop(['stop_headsign', 'pickup_type', 'drop_off_type', 'shape_dist_traveled'], axis=1)
routes = pd.read_csv('trenord-gtfs-csv//routes.csv')

trips = pd.read_csv('trenord-gtfs-csv//trips.csv')
trips = trips.drop(['trip_headsign', 'direction_id', 'block_id', 'shape_id'], axis=1)

trips_per_route = {}

for index, row in trips.iterrows():
    if row['route_id'] in trips_per_route:
        trips_per_route[row['route_id']].append(row['trip_id'])
    else:
        trips_per_route[row['route_id']] = [row['trip_id']]

'''import json

with open('trips_per_route.json', 'w') as fp:
    json.dump(trips_per_route, fp)'''

route_stops = np.zeros((len(trips_per_route), 42))

i = 0
for key in trips_per_route.keys():
    for trip in trips_per_route[key]:
        for index, row in stop_times.iterrows():
            element = route_stops[i, row['stop_sequence'] - 1]
            if row['trip_id'] == trip:
                if row['stop_id'] != element and element != 0:
                    print("Ciao ", key, " ", row['stop_id'], " ", element, " ", row['stop_sequence'] - 1)
                    element = row['stop_id']
    i = i + 1