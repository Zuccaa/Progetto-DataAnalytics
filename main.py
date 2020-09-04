from attack_handling import remove_nodes_analysis
from graphics import plot_bars_of_loads, create_graph, create_graph_with_switches, create_graph_for_loads
from load_analysis import create_loads_dataframe, compute_normal_loads, compute_loads_with_exceptions
from min_paths import compute_min_path, compute_switches_from_station
from utils import dict_as_group_by, import_data, add_direction_column, create_routes_adjacency_dict, \
    create_graph_from_XML
from pre_analysis import compute_assortativity
import json
import igraph as ig
import numpy as np

stop_times, trips, routes, exceptions_service, calendar, stops, trips_with_stop_times = import_data()

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

#graph = create_graph(stops)

#stations_routes_dict = dict_as_group_by(trips_with_stop_times, 'stop_id', 'route_id', repetition=False)
#routes_stations_dict = dict_as_group_by(trips_with_stop_times, 'route_id', 'stop_id', repetition=False)
#routes_adjacency_dict = create_routes_adjacency_dict(stations_routes_dict, routes_stations_dict)
#switches_from_station_dict = compute_switches_from_station('1581', routes_adjacency_dict, stations_routes_dict,
                                                           #routes_stations_dict)
#create_graph_with_switches(switches_from_station_dict, stops)
#print(switches_from_station_dict)

#compute_min_path(trips_with_stop_times.copy(), stations_routes_dict, '1581', '734', '09:00:00', 'monday', 2,
#                 stops)
graph_no_multiple_edges = create_graph_from_XML('CompleteGraph_NoMultipleEdges.xml', multiple_edges=False)
graph = create_graph_from_XML('Complete_TrenordNetwork.xml')
#compute_assortativity(graph_no_multiple_edges, graph_no_multiple_edges.degree((np.arange(graph_no_multiple_edges.vcount()))))
metrics = ['betweenness', 'degree', 'closeness']
remove_nodes_analysis(graph, graph_no_multiple_edges, metrics)

create_graph_for_loads(trips_with_stop_times, stops)