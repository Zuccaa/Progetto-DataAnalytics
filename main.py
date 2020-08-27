from graphics import plot_bars_of_loads, create_graph
from loadAnalysis import create_loads_dataframe, compute_normal_loads, compute_loads_with_exceptions
from min_paths import compute_min_path
from utils import dict_as_group_by, import_data
import json
import igraph as ig

stop_times, trips, routes, exceptions_service, calendar, stops = import_data()

stop_times_load = stop_times.copy()
stop_times_load = stop_times_load.drop(['stop_sequence'], axis=1)

#create_graph_table(stop_times, trips)
'''exceptions_service_dict = dict_as_group_by(exceptions_service, 'service_id', 'date')
for element in exceptions_service_dict:
    exceptions_service_dict[element] = str(exceptions_service_dict[element])

year = 2018
#week = [52, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 49]
week = 52
station = '1581'
title = "Carico giornaliero (Lunedì) di LISSONE-MUGGIO'"
file_with_exceptions = 'loads_complete_with_exceptions_' + str(year) + str(week) + '.json'
file_without_exceptions = 'loads_complete.json'
#loads = create_loads_dataframe(trips, calendar, stop_times_load)
#compute_normal_loads(loads)
''''''for w in week:
    if w == 52:
        print('Settimana ' + str(w) + " dell'anno 2018 in corso")
        compute_loads_with_exceptions(loads, exceptions_service_dict, 2018, w)
    else:
        print('Settimana ' + str(w) + " dell'anno 2019 in corso")
        compute_loads_with_exceptions(loads, exceptions_service_dict, 2019, w)
    print('FATTO!')
    print('-----------------------------------------------------------')'''

#compute_loads_with_exceptions(loads, exceptions_service_dict, year, week)
#plot_bars_of_loads(file_with_exceptions, 'tuesday', station, title)

'''with open('exceptions_service.json', 'w') as f:
    json.dump(exceptions_service_dict, f)'''

'''days_with_exceptions = set()
for index, row in exceptions_service.iterrows():
    days_with_exceptions.add(row['date'])

with open('days_with_exceptions.txt', 'w') as f:
    for item in days_with_exceptions:
        f.write("%s\n" % item)'''

#create_graph(stops)

'''g = ig.Graph(directed=False)
g.add_vertices(n=5)
g.add_edges([[0, 1], [1, 2], [2, 3], [3, 1], [4, 0], [4, 2]])
for edge in g.es:
    edge['weight'] = 1.5

print(g.is_weighted())
g.write_graphml('prova.graphml')'''

loads = create_loads_dataframe(trips, calendar, stop_times_load)
stations_routes_dict = dict_as_group_by(loads, 'stop_id', 'route_id', repetition=False)
compute_min_path(loads.copy(), stations_routes_dict, '1581', '1711', '19:00:00', 'monday', 1)