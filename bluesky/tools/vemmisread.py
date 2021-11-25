"""
This python file is used for reading and preparing the VEMMIS data

Created by: Bob van Dillen
Date: 22-11-2021
"""

import pandas as pd
import numpy as np
import datetime
import os
from .geo import qdrpos
from .aero import kts, ft


class VEMMISRead:
    """
    Class definition: Read and prepare the VEMMIS data
    Methods:
            read_data():        Read vemmis csv files
            relevant_data():    Select relevant flights
            merge_data():       Merge flights data into the other data, to get e.g. callsign
            get_coordinates():  Calculate coordinates from x and y position
            get_altitude():     Determine altitude from MODE_C
            get_time():         Determine the actual time
            get_starttime():    Get the time of the first data point
            get_simtime():      Determine the simulation time and optionally apply the fixed update rate
            delete_nan():       Delete data points with NaN in the relevant columns
            sort_data():        Sort the data by time and take the relevant columns for the track data
            add_createdelete(): Determine at which data point the aircraft need to be created and deleted
            get_datetime():     Get the date and time for the simulation
            get_commands():     Get the commands that need to be executed in the simulation
            get_trackdata():    Get the track data for the simulation

    Created by: Bob van Dillen
    Date: 22-11-2021
    """

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

        self.delete_nan()
        self.sort_data()

        self.add_createdelete()

    def read_data(self):
        """
        Function: Read vemmis csv files
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 22-11-2021
        """
        for root, dirs, files in os.walk(self.data_path):
            self.flights = pd.read_csv(self.data_path+'\\'+files[1], sep=';')
            self.flighttimes = pd.read_csv(self.data_path+'\\'+files[2], sep=';')
            self.tracks = pd.read_csv(self.data_path+'\\'+files[5], sep=';')

    def relevant_data(self):
        """
        Function: Select relevant flights
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 22-11-2021
        """
        i_delete = list(self.flights.index[self.flights['ICAO_ACTYPE'].isna()]) + \
                   list(self.flights.index[self.flights['STATUS'].isin(['CANCELLED'])])
        self.flights = self.flights.drop(list(set(i_delete)))

    def merge_data(self):
        """
        Function: Merge flights data into the other data, to get e.g. callsign
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        columns_flights = self.flights.columns.values
        columns_tracks = self.tracks.columns.values

        i_delete = np.where(np.isin(columns_flights, columns_tracks))
        columns_flights_merge = list(np.delete(columns_flights, i_delete)) + ['FLIGHT_ID', 'REGISTRATION']

        columns_tracks_merge = list(columns_tracks)
        columns_tracks_merge.remove('REGISTRATION')

        self.tracks_merged = pd.merge(self.tracks[columns_tracks_merge], self.flights[columns_flights_merge])

        self.tracks_merged['CREATE'] = [False]*len(self.tracks_merged)
        self.tracks_merged['DELETE'] = [False]*len(self.tracks_merged)

    def get_coordinates(self):
        """
        Function: Calculate coordinates from x and y position
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
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
        """
        Function: Determine altitude from MODE_C
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        self.tracks_merged['MODE_C'] = self.tracks_merged['MODE_C'].str.replace(',', '.').astype('float')*100
        self.tracks_merged = self.tracks_merged.rename(columns={'MODE_C': 'ALTITUDE'})

    def get_time(self):
        """
        Function: Determine the actual time
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        self.tracks_merged['T0'] = pd.to_datetime(self.tracks_merged['T0'])
        self.tracks_merged['TIME'] = pd.to_timedelta(self.tracks_merged['TIME']/100, unit='seconds')

        self.tracks_merged['ACTUAL_TIME'] = self.tracks_merged['T0'] + self.tracks_merged['TIME']

    def get_starttime(self):
        """
        Function: Get the time of the first data point
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        self.datetime0 = min(self.tracks_merged['ACTUAL_TIME'])

    def get_simtime(self):
        """
        Function: Determine the simulation time and optionally apply the fixed update rate
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        self.tracks_merged['SIM_TIME'] = self.tracks_merged['ACTUAL_TIME'] - self.datetime0
        self.tracks_merged['SIM_TIME'] = self.tracks_merged['SIM_TIME'].dt.total_seconds()
        if self.fixed_rate:
            self.tracks_merged['SIM_TIME'] = (self.tracks_merged['SIM_TIME']/self.deltat).apply(np.ceil)*self.deltat
            self.tracks_merged = self.tracks_merged.drop_duplicates(subset=['SIM_TIME', 'CALLSIGN'], keep='last')

    def delete_nan(self):
        """
        Function: Delete data points with NaN in the relevant columns
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 25-11-2021
        """
        self.tracks_merged = self.tracks_merged.dropna(subset=['CALLSIGN', 'ICAO_ACTYPE', 'LATITUDE', 'LONGITUDE',
                                                               'HEADING', 'ALTITUDE', 'SPEED'])

    def sort_data(self):
        """
        Function: Sort the data by time and take the relevant columns for the track data
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        self.tracks_merged = self.tracks_merged.sort_values(by=['SIM_TIME'])
        self.tracks_merged = self.tracks_merged[self.tracks_merged['SIM_TIME'] >= self.time0]
        self.tracks_merged['SIM_TIME'] = self.tracks_merged['SIM_TIME'] - self.tracks_merged['SIM_TIME'].iloc[0]

        columns = ['SIM_TIME', 'CALLSIGN', 'ICAO_ACTYPE', 'LATITUDE', 'LONGITUDE',
                   'ALTITUDE', 'HEADING', 'SPEED', 'CREATE', 'DELETE']
        self.trackdata = self.tracks_merged[columns]
        self.trackdata['SIM_TIME'] = self.trackdata['SIM_TIME'] - self.trackdata['SIM_TIME'].iloc[0]

    def add_createdelete(self):
        """
        Function: Determine at which data point the aircraft need to be created and deleted
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 24-11-2021
        """
        for acid in self.trackdata['CALLSIGN'].unique():
            track = self.trackdata[self.trackdata['CALLSIGN'] == acid]

            i_cre = track.index[0]
            i_del = track.index[-1]
            self.trackdata.loc[i_cre, 'CREATE'] = True
            self.trackdata.loc[i_del, 'DELETE'] = True

    def get_datetime(self):
        """
        Function: Get the date and time for the simulation
        Args: -
        Returns:
            day:    day of the simulation [int]
            month:  month of the simulation [int]
            year:   year of the simulation [int]
            time:   time of the simulation [str]

        Created by: Bob van Dillen
        Date = 25-11-2021
        """
        datetime_start = self.datetime0 + datetime.timedelta(seconds=self.time0)
        day = datetime_start.day
        month = datetime_start.month
        year = datetime_start.year
        time = datetime_start.strftime("%H:%M:%S")
        return day, month, year, time

    def get_commands(self):
        """
        Function: Get the commands that need to be executed in the simulation
        Args: -
        Returns:
            command:        the commands [lst(str)]
            commandtime:    the time when the command needs to be executed [lst(float)]

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
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
            self.trackdata.loc[i_cre, 'CREATE'] = True
            self.trackdata.loc[i_del, 'DELETE'] = True
            # self.trackdata = self.trackdata.drop([i_cre, i_del])

        command_df = pd.DataFrame({'COMMAND': command, 'TIME': commandtime})
        command_df = command_df.sort_values(by=['TIME'])

        return list(command_df['COMMAND']), list(command_df['TIME'])

    def get_trackdata(self):
        """
        Function: Get the track data for the simulation
        Args: -
        Returns:
            simt:   simulation time [array(float)]
            simt_i: indices with the same simulation time [lst(lst(int))]
            id:     callsign [lst(str)]
            actype: aircraft type [lst(str)]
            lat:    latitude [array(float)]
            lon:    longitude [array(float)]
            hdg:    heading [array(float)]
            alt:    altitude [array(float)]
            spd:    ground speed [array(float)]
            create: if an aircraft needs to be created [array(bool)]
            delete: if an aircraft needs to be deleted [array(bool)]

        Created by: Bob van Dillen
        Date = 22-11-2021
        """
        simt = np.array(self.trackdata['SIM_TIME'])
        unique, i, count = np.unique(simt, return_index=True, return_counts=True)
        simt_i = []
        for j in range(len(unique)):
            for c in range(count[j]):
                simt_i.append(list(range(i[j], i[j] + count[j])))

        id = list(self.trackdata['CALLSIGN'])
        actype = list(self.trackdata['ICAO_ACTYPE'])
        lat = np.array(self.trackdata['LATITUDE'])
        lon = np.array(self.trackdata['LONGITUDE'])
        hdg = np.array(self.trackdata['HEADING'])
        alt = np.array(self.trackdata['ALTITUDE'])*ft
        spd = np.array(self.trackdata['SPEED'])*kts
        create = np.array(self.trackdata['CREATE'], dtype=np.bool)
        delete = np.array(self.trackdata['DELETE'], dtype=np.bool)
        return simt, simt_i, id, actype, lat, lon, hdg, alt, spd, create, delete
