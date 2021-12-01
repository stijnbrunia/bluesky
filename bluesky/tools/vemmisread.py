"""
This python file is used for reading and preparing the VEMMIS data

Created by: Bob van Dillen
Date: 22-11-2021
"""

import pandas as pd
import numpy as np
import os
from bluesky.tools.geo import qdrpos
from bluesky.tools.aero import kts, ft


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
        self.trackdata = None
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

        i_delete = list(self.flights.index[self.flights['ICAO_ACTYPE'].isna()]) +\
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

        self.trackdata = pd.merge(self.tracks[columns_tracks_merge], self.flights[columns_flights_merge])

    def get_coordinates(self):
        """
        Function: Calculate coordinates from x and y position
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.trackdata['X'] = self.trackdata['X'].str.replace(',', '.').astype('float')
        self.trackdata['Y'] = self.trackdata['Y'].str.replace(',', '.').astype('float')

        self.trackdata['X'] = self.trackdata['X']/128
        self.trackdata['Y'] = self.trackdata['Y']/128

        qdr = np.degrees(np.arctan2(self.trackdata['X'], self.trackdata['Y']))
        qdr = np.where(qdr < 0, qdr+360, qdr)
        d = np.array(np.sqrt(self.trackdata['X']**2 + self.trackdata['Y']**2))

        self.trackdata['X'], self.trackdata['Y'] = qdrpos(self.lat0, self.lon0, qdr, d)
        self.trackdata = self.trackdata.rename(columns={'X': 'LATITUDE', 'Y': 'LONGITUDE'})

    def get_altitude(self):
        """
        Function: Determine altitude from MODE_C
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.trackdata['MODE_C'] = self.trackdata['MODE_C'].str.replace(',', '.').astype('float')*100
        self.trackdata = self.trackdata.rename(columns={'MODE_C': 'ALTITUDE'})

    def get_time(self):
        """
        Function: Determine the actual time
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.trackdata['T_START'] = pd.to_datetime(self.trackdata['T_START'], format="%d-%m-%Y %H:%M:%S")
        self.trackdata['TIME'] = pd.to_timedelta(self.trackdata['TIME']/100, unit='seconds')

        self.trackdata['ACTUAL_TIME'] = self.trackdata['T_START'] + self.trackdata['TIME']

    def get_starttime(self):
        """
        Function: Get the time of the first data point
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.datetime0 = min(self.trackdata['ACTUAL_TIME'])

    def get_simtime(self):
        """
        Function: Determine the simulation time and optionally apply the fixed update rate
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.trackdata['SIM_TIME'] = self.trackdata['ACTUAL_TIME'] - self.datetime0
        self.trackdata['SIM_TIME'] = self.trackdata['SIM_TIME'].dt.total_seconds()
        if self.fixed_rate:
            self.trackdata['SIM_TIME'] = (self.trackdata['SIM_TIME']/self.deltat).apply(np.ceil)*self.deltat
            self.trackdata = self.trackdata.drop_duplicates(subset=['SIM_TIME', 'CALLSIGN'], keep='last')

    def delete_nan(self):
        """
        Function: Delete data points with NaN in the relevant columns
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 25-11-2021
        """

        self.trackdata = self.trackdata.dropna(subset=['CALLSIGN', 'ICAO_ACTYPE', 'LATITUDE', 'LONGITUDE',
                                                       'HEADING', 'ALTITUDE', 'SPEED'])

    def sort_data(self):
        """
        Function: Sort the data by time and take the relevant columns for the track data
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.trackdata = self.trackdata.sort_values(by=['SIM_TIME'])
        self.trackdata = self.trackdata.loc[self.trackdata['SIM_TIME'] >= self.time0]
        self.trackdata['SIM_TIME'] = self.trackdata['SIM_TIME'] - self.trackdata['SIM_TIME'].iloc[0]

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

        datetime_start = min(self.trackdata['ACTUAL_TIME'])
        day = datetime_start.day
        month = datetime_start.month
        year = datetime_start.year
        time = datetime_start.strftime("%H:%M:%S")
        return day, month, year, time

    def get_flightdata(self):
        """
        Function: Get the commands that need to be executed in the simulation
        Args: -
        Returns:
            command:        the commands [lst(str)]
            commandtime:    the time when the command needs to be executed [lst(float)]

        Remark: this function needs to be executed before get_trackdata()

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        simday, simmonth, simyear, simtime = self.get_datetime()

        command = ["DATE "+str(simday)+", "+str(simmonth)+", "+str(simyear)+", "+simtime]
        commandtime = [0.]

        for acid in self.trackdata['CALLSIGN'].unique():
            flight = self.flights.loc[self.flights['CALLSIGN'] == acid].iloc[0]
            track = self.trackdata.loc[self.trackdata['CALLSIGN'] == acid]

            t_cre = track['SIM_TIME'].iloc[0]
            t_del = track['SIM_TIME'].iloc[-1]

            acflightid = str(flight['FLIGHT_ID'])
            actype = flight['ICAO_ACTYPE']
            orig = flight['ADEP']
            dest = flight['DEST']

            lat = str(track['LATITUDE'].iloc[0])
            lon = str(track['LONGITUDE'].iloc[0])
            hdg = str(track['HEADING'].iloc[0])
            alt = str(track['ALTITUDE'].iloc[0])
            spd = str(track['SPEED'].iloc[0])

            # str_cre = "CRE "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd
            str_crefromdata = "CREFROMDATA "+acflightid+", "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd
            str_orig = "ORIG "+acid+" "+orig
            str_dest = "DEST "+acid+" "+dest
            # str_del = "DEL "+acid
            str_delfromdata = "DELFROMDATA "+acflightid+", "+acid
            command += [str_crefromdata, str_orig, str_dest, str_delfromdata]
            commandtime += [t_cre] + [t_cre+0.1]*2 + [t_del]

            i_cre = track.index[0]
            i_del = track.index[-1]
            self.trackdata = self.trackdata.drop([i_cre, i_del])

        command_df = pd.DataFrame({'COMMAND': command, 'TIME': commandtime})
        command_df = command_df.sort_values(by=['TIME'])

        return list(command_df['COMMAND']), list(command_df['TIME'])

    def get_trackdata(self):
        """
        Function: Get the track data for the simulation
        Args: -
        Returns:
            simt:       simulation time [array(float)]
            simt_i:     indices with the same simulation time [lst(lst(int))]
            flightid:   flight id [array(int/float)]
            id:         callsign [lst(str)]
            actype:     aircraft type [lst(str)]
            lat:        latitude [array(float)]
            lon:        longitude [array(float)]
            hdg:        heading [array(float)]
            alt:        altitude [array(float)]
            spd:        ground speed [array(float)]

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        simt = np.array(self.trackdata['SIM_TIME'])
        unique, i, count = np.unique(simt, return_index=True, return_counts=True)
        simt_i = []
        for j in range(len(unique)):
            for c in range(count[j]):
                simt_i.append(list(range(i[j], i[j] + count[j])))

        flightid = np.array(self.trackdata['FLIGHT_ID'])
        acid = list(self.trackdata['CALLSIGN'])
        actype = list(self.trackdata['ICAO_ACTYPE'])
        lat = np.array(self.trackdata['LATITUDE'])
        lon = np.array(self.trackdata['LONGITUDE'])
        hdg = np.array(self.trackdata['HEADING'])
        alt = np.array(self.trackdata['ALTITUDE'])*ft
        spd = np.array(self.trackdata['SPEED'])*kts
        return simt, simt_i, flightid, acid, actype, lat, lon, hdg, alt, spd


if __name__ == '__main__':
    path = r"C:\Users\LVNL_ILAB3\PycharmProjects\bluesky\scenario\vemmis1209"
    vemmis1209 = VEMMISRead(path, 0)
    print(vemmis1209.trackdata[['ACTUAL_TIME', 'SIM_TIME', 'CALLSIGN']])
