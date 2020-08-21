import pandas as pd
import numpy as np
import csv
import json
import matplotlib.pylab as plt

stop_times = pd.read_csv('trenord-gtfs-csv//stop_times.csv')
stop_times = stop_times.drop(['stop_headsign', 'pickup_type',
                              'drop_off_type', 'shape_dist_traveled'], axis=1)
stop_times = stop_times.sort_values(by=['trip_id', 'stop_sequence']).reset_index(drop=True)

stop_times_load = stop_times.copy()
stop_times_load = stop_times_load.drop(['stop_sequence'], axis=1)

routes = pd.read_csv('trenord-gtfs-csv//routes.csv')
routes = routes.drop(['agency_id', 'route_short_name', 'route_desc', 'route_type', 'route_url',
                      'route_text_color'], axis=1)

trips = pd.read_csv('trenord-gtfs-csv//trips.csv')
trips = trips.drop(['trip_headsign', 'trip_short_name', 'direction_id', 'block_id', 'shape_id'], axis=1)

'''trips_per_route = {}

for index, row in trips.iterrows():
    if row['route_id'] in trips_per_route:
        trips_per_route[row['route_id']].append(row['trip_id'])
    else:
        trips_per_route[row['route_id']] = [row['trip_id']]

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

with open('routes_dict.csv', 'w', newline='') as file:
    fieldnames = ['Linea', 'Stazione 1', 'Stazione 2', 'Colore']
    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    for key in routes_dict.keys():
        selected_row = routes.loc[routes['route_id'] == key]
        color = '#' + selected_row['route_color'].values[0]
        for set_list in routes_dict[key]:
            writer.writerow({'Linea': key, 'Stazione 1': set_list.pop(),
                             'Stazione 2': set_list.pop(), 'Colore': color})'''

calendar = pd.read_csv('trenord-gtfs-csv//calendar.csv')
calendar = calendar.drop(['start_date', 'end_date'], axis=1)

loads = trips.merge(calendar, on='service_id').copy()
loads = loads.merge(stop_times_load, on='trip_id')

np.savetxt(r'loads.txt', loads.values, fmt='%s')

'''frequencies_dict = {}
days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
hours = []
for i in range(4, 26, 1):
    if i < 10:
        hours.append('0' + str(i) + ':00:00')
    else:
        hours.append(str(i) + ':00:00')

for day in days:
    frequencies_dict[day] = []
    temporary_dict = {}
    for index_hour, hour in enumerate(hours):
        if index_hour + 1 < len(hours):
            temporary_dict['Inizio'] = hour
            temporary_dict['Fine'] = hours[index_hour + 1]
            routes_dict = {}
            for index_row, row in loads.iterrows():
                key = row['stop_id']
                if row[day] == 1 and hour <= row['arrival_time'] < hours[index_hour + 1]:
                    if key not in routes_dict:
                        routes_dict[key] = 1
                    else:
                        routes_dict[key] += 1
            #sorted_routes = sorted(routes_dict.items(), key=lambda x: x[1], reverse=True)
            temporary_dict['Stazioni'] = routes_dict.copy()
        frequencies_dict[day].append(temporary_dict.copy())
        print(hour)
    print(day)

with open('loads_complete.json', 'w') as fp:
    json.dump(frequencies_dict, fp)'''

with open('loads_complete.json', 'r') as fp:
    data = json.load(fp)

histogram_dict = {}
monday_list = data['monday']

i = 0
for dict in monday_list:
    for element in dict['Stazioni']:
        if element == '1707':
            histogram_dict[i] = dict['Stazioni']['1707']
            break
    i += 1

lists = sorted(histogram_dict.items()) # sorted by key, return a list of tuples

x, y = zip(*lists) # unpack a list of pairs into two tuples

plt.plot(x, y)
plt.show()