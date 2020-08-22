import json
import numpy as np
from datetime import date
import calendar

def create_loads_dataframe(trips, calendar, stop_times_load):
    loads = trips.merge(calendar, on='service_id').copy()
    loads = loads.merge(stop_times_load, on='trip_id')

    np.savetxt(r'loads.txt', loads.values, fmt='%s')

    return loads

def compute_normal_loads(loads_dataframe):

    frequencies_dict = {}
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
                for index_row, row in loads_dataframe.iterrows():
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
        json.dump(frequencies_dict, fp)

def compute_loads_with_exceptions(loads_dataframe, exceptions_service_dict, year, week):

    frequencies_dict = {}
    hours = []
    for i in range(4, 26, 1):
        if i < 10:
            hours.append('0' + str(i) + ':00:00')
        else:
            hours.append(str(i) + ':00:00')

    for i in range(1, 2):
        date_to_consider = date.fromisocalendar(year, week, i)
        day = calendar.day_name[date_to_consider.weekday()].lower()
        frequencies_dict[day] = []
        temporary_dict = {}
        for index_hour, hour in enumerate(hours):
            if index_hour + 1 < len(hours):
                temporary_dict['Inizio'] = hour
                temporary_dict['Fine'] = hours[index_hour + 1]
                routes_dict = {}
                for index_row, row in loads_dataframe.iterrows():
                    key = row['stop_id']
                    date_string = str(date_to_consider).replace('-', '')
                    if row[day] == 1 and check_service_exception(exceptions_service_dict, row['service_id'],
                        date_string) and hour <= row['arrival_time'] < hours[index_hour + 1]:
                        if key not in routes_dict:
                            routes_dict[key] = 1
                        else:
                            routes_dict[key] += 1
                # sorted_routes = sorted(routes_dict.items(), key=lambda x: x[1], reverse=True)
                temporary_dict['Stazioni'] = routes_dict.copy()
            frequencies_dict[day].append(temporary_dict.copy())
            print(hour)
        print(i)

    with open('loads_complete_with_exceptions_' + str(year) + str(week) + '.json', 'w') as fp:
        json.dump(frequencies_dict, fp)

def check_service_exception(exceptions_service_dict, service_id, date):

    if service_id in exceptions_service_dict:
        if date not in exceptions_service_dict[service_id]:
            return True

    return False
