import pandas as pd
import json

stop_times = pd.read_csv('trenord-gtfs-csv//stop_times.csv')
stop_times = stop_times.drop(['stop_headsign', 'pickup_type', 'drop_off_type', 'shape_dist_traveled'], axis=1)
stop_times = stop_times.sort_values(by=['trip_id', 'stop_sequence']).reset_index(drop=True)
routes = pd.read_csv('trenord-gtfs-csv//routes.csv')

trips = pd.read_csv('trenord-gtfs-csv//trips.csv')
trips = trips.drop(['trip_headsign', 'direction_id', 'block_id', 'shape_id'], axis=1)

trips_per_route = {}

for index, row in trips.iterrows():
    if row['route_id'] in trips_per_route:
        trips_per_route[row['route_id']].append(row['trip_id'])
    else:
        trips_per_route[row['route_id']] = [row['trip_id']]

'''
with open('trips_per_route.json', 'w') as fp:
    json.dump(trips_per_route, fp)'''

routes_dict = {}

print("Lunghezza iniziale", len(stop_times.index))
for key in trips_per_route.keys():
    routes_dict[key] = []
    for index, row in stop_times.iterrows():
        if row['trip_id'] in trips_per_route[key]:
            if index != stop_times.index[-1]:
                next_row = stop_times.loc[index + 1]
                if next_row['stop_sequence'] == row['stop_sequence'] + 1:
                    edge = {row['stop_id'], next_row['stop_id']}
                    if edge not in routes_dict[key]:
                        routes_dict[key].append(edge)
            stop_times = stop_times.drop(index)
    stop_times = stop_times.reset_index(drop=True)
    print(key, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

'''with open('routes_dict.txt', 'w') as f:
    print(routes_dict, file=f)'''

import csv

with open('routes_dict.csv', 'w', newline='') as file:
    fieldnames = ['Linea', 'Stazione 1', 'Stazione 2']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    for key in routes_dict.keys():
        for set_list in routes_dict[key]:
            writer.writerow({'Linea': key, 'Stazione 1': set_list.pop(), 'Stazione 2': set_list.pop()})

'''i = 0
for key in trips_per_route.keys():
    for index, row in stop_times.iterrows():
        if row['trip_id'] in trips_per_route[key]:
            element = route_stops[i, row['stop_sequence'] - 1]
            if row['stop_id'] != element and element != 0:
                print("Ciao ", key, " ", row['stop_id'], " ", element, " ", row['stop_sequence'] - 1)
            route_stops[i, row['stop_sequence'] - 1] = row['stop_id']
            stop_times.drop(index)
    print("Linea ", key, " fatta!")'''