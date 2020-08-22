from graphics import plot_bars_of_loads
from loadAnalysis import create_loads_dataframe, compute_normal_loads, compute_loads_with_exceptions
from utils import dict_as_group_by, import_data
import json

stop_times, trips, routes, exceptions_service, calendar = import_data()

stop_times_load = stop_times.copy()
stop_times_load = stop_times_load.drop(['stop_sequence'], axis=1)


exceptions_service_dict = dict_as_group_by(exceptions_service, 'service_id', 'date')
year = 2019
week = 42
station = '1841'
loads = create_loads_dataframe(trips, calendar, stop_times_load)
#compute_normal_loads(loads)
compute_loads_with_exceptions(loads, exceptions_service_dict, year, week)
plot_bars_of_loads('loads_complete_with_exceptions_' + str(year) + str(week) + '.json', 'monday', station)

'''with open('exceptions_service.json', 'w') as f:
    json.dump(exceptions_service_dict, f)'''

'''days_with_exceptions = set()
for index, row in exceptions_service.iterrows():
    days_with_exceptions.add(row['date'])

with open('days_with_exceptions.txt', 'w') as f:
    for item in days_with_exceptions:
        f.write("%s\n" % item)'''