'''
load_analysis(): script che gestisce l'analisi
                 relativa ai carichi
----------------------------------------------------
Creato da:
    Stefano Zuccarella n.816482
    Matteo Paolella n.816933
'''

import json
import numpy as np
from datetime import date
import calendar


def compute_loads_with_exceptions(loads_dataframe, exceptions_service_dict, year, week):

    # Creo un dizionario che contiene le frequenze giornaliere per ogni stazione
    frequencies_dict = {}
    hours = []
    # Riempio la lista di ore
    for i in range(4, 26, 1):
        if i < 10:
            hours.append('0' + str(i) + ':00:00')
        else:
            hours.append(str(i) + ':00:00')

    for i in range(1, 8):
        date_to_consider = date.fromisocalendar(year, week, i)
        date_string = str(date_to_consider).replace('-', '')
        day = calendar.day_name[date_to_consider.weekday()].lower()
        frequencies_dict[day] = []

        '''Questo dizionario temporaneo contiene:
            - 'Inizio' -> ora d'inizio dell'analisi dei carichi
            - 'Fine' -> ora di fine dell'analisi dei carichi
            - 'Stazioni' -> oggetto contenente il numero di treni che passano nelle stazioni
                            nell'intervallo di tempo individuato da inizio e fine'''
        temporary_dict = {}
        for index_hour, hour in enumerate(hours):
            if index_hour + 1 < len(hours):
                temporary_dict['Inizio'] = hour
                temporary_dict['Fine'] = hours[index_hour + 1]

                # Creo un dizionario che rappresenta l'oggetto da inserire nella chiave 'Stazioni'
                routes_dict = {}
                for index_row, row in loads_dataframe.iterrows():
                    key = row['stop_id']
                    # Controllo che il treno non sia stato cancellato
                    if row[day] == 1 and hour <= row['arrival_time'] < hours[index_hour + 1] and \
                            check_no_service_exception(exceptions_service_dict, row['service_id'],
                                                       date_string):
                        if key not in routes_dict:
                            routes_dict[key] = 1
                        else:
                            routes_dict[key] += 1
                temporary_dict['Stazioni'] = routes_dict.copy()
            frequencies_dict[day].append(temporary_dict.copy())

    if week < 10:
        week_string = "0" + str(week)
    else:
        week_string = str(week)

    # Salvo il file come oggetto JSON
    with open('Carichi//loads_complete_with_exceptions_' + str(year) + week_string + '.json', 'w') as fp:
        json.dump(frequencies_dict, fp)


def check_no_service_exception(exceptions_service_dict, service_id, date):

    # Controllo se un servizio sia presente o meno tra i servizi che vengono cancellati
    # in una certa data
    if service_id in exceptions_service_dict:
        if date in exceptions_service_dict[service_id]:
            return False
        else:
            return True
    else:
        return True
