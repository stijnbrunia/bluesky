import bluesky as bs
import pandas as pd
import numpy as np
import os
from .geo import qdrpos
from .aero import kts, ft

class VEMMISRead:
    def __init__(self, data_path, time0, fixed_rate=True, deltat=5.):
        self.data_path = data_path

        self.time0 = time0

        self.fixed_rate = fixed_rate
        self.deltat = deltat

        self.lat0 = 52+18/60+29/3600
        self.lon0 = 4+45/60+51/3600

        self.flights = None
        self.flighttimes = None
        self.tracks = None
        self.flighttimes_merged = None
        self.tracks_merged = None
        self.trackdata = None

        self.read_data()
        self.relevant_data()
        self.merge_data()
        self.get_coordinates()
        self.get_altitude()
        self.get_time()

        self.datetime0 = None

        self.get_starttime()
        self.get_simtime()

        self.sort_data()

    def read_data(self):
        for root, dirs, files in os.walk(self.data_path):
            self.flights = pd.read_csv(self.data_path+'\\'+files[1], sep=';')
            self.flighttimes = pd.read_csv(self.data_path+'\\'+files[2], sep=';')
            self.tracks = pd.read_csv(self.data_path+'\\'+files[5], sep=';')

    def relevant_data(self):
        i_delete = list(self.flights.index[self.flights['ICAO_ACTYPE'].isna()]) + \
                   list(self.flights.index[self.flights['STATUS'].isin(['CANCELLED'])])
        self.flights = self.flights.drop(list(set(i_delete)))

    def merge_data(self):
        columns_flights = self.flights.columns.values
        columns_tracks = self.tracks.columns.values

        i_delete = np.where(np.isin(columns_flights, columns_tracks))
        columns_flights_merge = list(np.delete(columns_flights, i_delete)) + ['FLIGHT_ID', 'REGISTRATION']

        columns_tracks_merge = list(columns_tracks)
        columns_tracks_merge.remove('REGISTRATION')

        self.tracks_merged = pd.merge(self.tracks[columns_tracks_merge], self.flights[columns_flights_merge])

    def get_coordinates(self):
        self.tracks_merged['X'] = self.tracks_merged['X'].str.replace(',', '.').astype('float')
        self.tracks_merged['Y'] = self.tracks_merged['Y'].str.replace(',', '.').astype('float')

        self.tracks_merged['X'] = self.tracks_merged['X']/128
        self.tracks_merged['Y'] = self.tracks_merged['Y']/128

        qdr = np.degrees(np.arctan2(self.tracks_merged['X'], self.tracks_merged['Y']))
        qdr = np.where(qdr < 0, qdr+360, qdr)
        d = np.array(np.sqrt(self.tracks_merged['X']**2 + self.tracks_merged['Y']**2))

        self.tracks_merged['X'], self.tracks_merged['Y'] = qdrpos(self.lat0, self.lon0, qdr, d)
        self.tracks_merged = self.tracks_merged.rename(columns={'X': 'LATITUDE', 'Y': 'LONGITUDE'})

    def get_altitude(self):
        self.tracks_merged['MODE_C'] = self.tracks_merged['MODE_C'].str.replace(',', '.').astype('float')*100
        self.tracks_merged = self.tracks_merged.rename(columns={'MODE_C': 'ALTITUDE'})

    def get_time(self):
        self.tracks_merged['T0'] = pd.to_datetime(self.tracks_merged['T0'])
        self.tracks_merged['TIME'] = pd.to_timedelta(self.tracks_merged['TIME']/100, unit='seconds')

        self.tracks_merged['ACTUAL_TIME'] = self.tracks_merged['T0'] + self.tracks_merged['TIME']

    def get_starttime(self):
        self.datetime0 = min(self.tracks_merged['ACTUAL_TIME'])

    def get_simtime(self):
        self.tracks_merged['SIM_TIME'] = self.tracks_merged['ACTUAL_TIME'] - self.datetime0
        self.tracks_merged['SIM_TIME'] = self.tracks_merged['SIM_TIME'].dt.total_seconds()
        if self.fixed_rate:
            self.tracks_merged['SIM_TIME'] = (self.tracks_merged['SIM_TIME']/self.deltat).astype(int)*self.deltat
            self.tracks_merged = self.tracks_merged.drop_duplicates(subset=['SIM_TIME', 'CALLSIGN'], keep='last')

    def sort_data(self):
        self.tracks_merged = self.tracks_merged.sort_values(by=['SIM_TIME'])
        self.tracks_merged = self.tracks_merged[self.tracks_merged['SIM_TIME'] >= self.time0]

        columns = ['SIM_TIME', 'CALLSIGN', 'LATITUDE', 'LONGITUDE', 'ALTITUDE', 'HEADING', 'SPEED']
        self.trackdata = self.tracks_merged[columns]

    def get_commands(self):
        command = []
        commandtime = []
        for acid in self.tracks_merged['CALLSIGN'].unique():
            flight = self.flights.loc[self.flights['CALLSIGN'] == acid].iloc[0]
            track = self.tracks_merged[self.tracks_merged['CALLSIGN'] == acid]

            t_cre = track['SIM_TIME'].iloc[0]
            t_del = track['SIM_TIME'].iloc[-1]

            actype = flight['ICAO_ACTYPE']
            orig = flight['ADEP']
            dest = flight['DEST']

            lat = str(track['LATITUDE'].iloc[0])
            lon = str(track['LONGITUDE'].iloc[0])
            hdg = str(track['HEADING'].iloc[0])
            alt = str(track['ALTITUDE'].iloc[0])
            spd = str(track['SPEED'].iloc[0])

            str_cre = "CRE "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd+", ON"
            str_orig = "ORIG "+acid+" "+orig
            str_dest = "DEST "+acid+" "+dest
            str_del = "DEL "+acid
            command += [str_cre, str_orig, str_dest, str_del]
            commandtime += [t_cre]*3 + [t_del]

            i_cre = track.index[0]
            i_del = track.index[-1]
            self.trackdata = self.trackdata.drop([i_cre, i_del])

        command_df = pd.DataFrame({'COMMAND': command, 'TIME': commandtime})
        command_df = command_df.sort_values(by=['TIME'])

        return list(command_df['COMMAND']), list(command_df['TIME'])

    def get_trackdata(self):
        simt = np.array(self.trackdata['SIM_TIME'])
        unique, i, count = np.unique(simt, return_index=True, return_counts=True)
        simt_i = []
        for j in range(len(unique)):
            for c in range(count[j]):
                simt_i.append(list(range(i[j], i[j] + count[j])))

        id = list(self.trackdata['CALLSIGN'])
        lat = np.array(self.trackdata['LATITUDE'])
        lon = np.array(self.trackdata['LONGITUDE'])
        alt = np.array(self.trackdata['ALTITUDE'])*ft
        hdg = np.array(self.trackdata['HEADING'])
        spd = np.array(self.trackdata['SPEED'])*kts
        return simt, simt_i, id, lat, lon, alt, hdg, spd
