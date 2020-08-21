import pandas as pd
import numpy as np
import json
import csv
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

exceptions_service = pd.read_csv('trenord-gtfs-csv//calendar_dates.csv')
exceptions_service = exceptions_service.drop(['exception_type'], axis=1)

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

i = 4
route_to_consider = '1841'
for dict in monday_list:
    if route_to_consider in dict['Stazioni']:
        histogram_dict[i] = dict['Stazioni'][route_to_consider]
    else:
        histogram_dict[i] = 0
    i += 1

bar = plt.bar(np.arange(len(histogram_dict.keys())) + 0.25, histogram_dict.values(), color="green")
plt.xticks(np.arange(24) - 0.25, labels=['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                                         '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                                         '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '00:00',
                                         '01:00', '02:00'], rotation='vertical')
plt.title("Carico giornaliero (Lunedì) di Monza")
plt.xlabel("Orario")
plt.ylabel("Numero di treni")
counter = 0
list_of_values = list(histogram_dict.values())
for rect in bar:
    plt.text(rect.get_x() + 0.4, rect.get_height() + 0.3, list_of_values[counter], ha='center', va='bottom')
    counter += 1

#plt.show()

days_with_exceptions = set()
for index, row in exceptions_service.iterrows():
    days_with_exceptions.add(row['date'])

with open('days_with_exceptions.txt', 'w') as f:
    for item in days_with_exceptions:
        f.write("%s\n" % item)