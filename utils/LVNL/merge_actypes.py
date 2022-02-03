"""
This pyhton file is used to merge to aircraft types databases

Created by: Bob van Dillen
Date: 3-2-2022
"""

import os
import pandas as pd

# Read data
acdata1 = pd.read_csv('aircraftDatabase.csv', sep=',')
acdata2 = pd.read_csv('aircraft_db.csv', sep=',')

# Drop not usable data
acdata1.dropna(subset=['icao24', 'typecode'], inplace=True)
acdata2['mdl'].replace('0000', float("NaN"), inplace=True)
acdata2.dropna(subset=['icao', 'mdl'], inplace=True)
acdata2.rename(columns={'icao': 'icao24', 'mdl': 'typecode'}, inplace=True)

# Capital letter
acdata1['typecode'] = acdata1['typecode'].str.upper()
acdata2['typecode'] = acdata2['typecode'].str.upper()

# Append and take unique
acdata = acdata1[['icao24', 'typecode']].append(acdata2[['icao24', 'typecode']])
acdata.drop_duplicates(subset=['icao24'], inplace=True, keep='first', ignore_index=True)

# Save file
path = os.path.expanduser("~") + '\\PycharmProjects\\bluesky\\data\\'
acdata.to_csv(path+'actypes.csv', index=False, sep=';')
