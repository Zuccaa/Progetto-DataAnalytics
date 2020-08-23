from utils import dict_as_group_by, import_data
import csv
import json
import matplotlib.pylab as plt
import numpy as np

def create_graph_table(stop_times, trips):
    stop_times, trips, routes, *_ = import_data()

    trips_per_route = dict_as_group_by(trips, 'route_id', 'trip_id')

    routes_dict = {}

    print("Lunghezza iniziale", len(stop_times.index))
    for key in trips_per_route.keys():
        routes_dict[key] = []
        for index, row in stop_times.iterrows():
            if row['trip_id'] in trips_per_route[key]:
                if index != stop_times.index[-1]:
                    next_row = stop_times.loc[index + 1]
                    if next_row['stop_sequence'] > row['stop_sequence']:
                        edge = {row['stop_id'], next_row['stop_id']}
                        if edge not in routes_dict[key]:
                            routes_dict[key].append(edge)
                stop_times = stop_times.drop(index)
        stop_times = stop_times.reset_index(drop=True)
        print(key, " fatta, lunghezza di stop_times ora è ", len(stop_times.index))

    save_graph_table(routes_dict, routes)

def save_graph_table(routes_dict, routes):
    with open('routes_dict.csv', 'w', newline='') as file:
        fieldnames = ['Linea', 'Stazione 1', 'Stazione 2', 'Colore']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for key in routes_dict.keys():
            selected_row = routes.loc[routes['route_id'] == key]
            color = '#' + selected_row['route_color'].values[0]
            for set_list in routes_dict[key]:
                writer.writerow({'Linea': key, 'Stazione 1': set_list.pop(),
                                 'Stazione 2': set_list.pop(), 'Colore': color})

def plot_bars_of_loads(file, day, route, title):
    with open(file, 'r') as fp:
        data = json.load(fp)

    bar_dict = {}
    day_list = data[day]

    i = 4
    for dict in day_list:
        if route in dict['Stazioni']:
            bar_dict[i] = dict['Stazioni'][route]
        else:
            bar_dict[i] = 0
        i += 1

    bar = plt.bar(np.arange(len(bar_dict.keys())) + 0.25, bar_dict.values(), color="green")
    plt.xticks(np.arange(24) - 0.25, labels=['04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00',
                                             '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
                                             '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '00:00',
                                             '01:00', '02:00'], rotation='vertical')
    plt.title(title)
    plt.xlabel("Orario")
    plt.ylabel("Numero di treni")
    counter = 0
    list_of_values = list(bar_dict.values())
    for rect in bar:
        plt.text(rect.get_x() + 0.4, rect.get_height() + 0.3, list_of_values[counter], ha='center', va='bottom')
        counter += 1

    plt.show()