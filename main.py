from graphics import plot_bars_of_loads, create_graph_table
from loadAnalysis import create_loads_dataframe, compute_normal_loads, compute_loads_with_exceptions
from utils import dict_as_group_by, import_data
import json

stop_times, trips, routes, exceptions_service, calendar = import_data()

stop_times_load = stop_times.copy()
stop_times_load = stop_times_load.drop(['stop_sequence'], axis=1)

create_graph_table(stop_times, trips)
'''exceptions_service_dict = dict_as_group_by(exceptions_service, 'service_id', 'date')
for element in exceptions_service_dict:
    exceptions_service_dict[element] = str(exceptions_service_dict[element])

year = 2019
week = [52, 2, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 49]
station = '1707'
title = "Carico giornaliero (Lunedì) di Milano Bovisa FNM"
file_with_exceptions = 'loads_complete_with_exceptions_' + str(year) + str(week) + '.json'
file_without_exceptions = 'loads_complete.json'
loads = create_loads_dataframe(trips, calendar, stop_times_load)
#compute_normal_loads(loads)
for w in week:
    if w == 52:
        print('Settimana' + w + "dell'anno 2018 in corso")
        compute_loads_with_exceptions(loads, exceptions_service_dict, 2018, w)
    else:
        print('Settimana' + w + "dell'anno 2019 in corso")
        compute_loads_with_exceptions(loads, exceptions_service_dict, 2019, w)
    print('FATTO!')
    print('-----------------------------------------------------------')

#compute_loads_with_exceptions(loads, exceptions_service_dict, year, week)
#plot_bars_of_loads(file_with_exceptions, 'sunday', station, title)'''

'''with open('exceptions_service.json', 'w') as f:
    json.dump(exceptions_service_dict, f)'''

'''days_with_exceptions = set()
for index, row in exceptions_service.iterrows():
    days_with_exceptions.add(row['date'])

with open('days_with_exceptions.txt', 'w') as f:
    for item in days_with_exceptions:
        f.write("%s\n" % item)'''