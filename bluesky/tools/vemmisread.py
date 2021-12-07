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

    def __init__(self, data_path, time0, deltat=None):
        self.data_path = data_path

        self.time0 = time0

        self.deltat = deltat

        self.lat0 = 52+18/60+29/3600
        self.lon0 = 4+45/60+51/3600

        self.flights = None
        self.flighttimes = None
        self.tracks = None
        self.routedata = None
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

        i_delete = list(self.flights.index[self.flights['ICAO_ACTYPE'].isna()])
        self.flights = self.flights.drop(i_delete)

        self.flighttimes = self.flighttimes.loc[self.flighttimes['TIME_TYPE'] == 'ACTUAL']
        self.flighttimes = self.flighttimes.loc[self.flighttimes['LOCATION_TYPE'] == 'RP']

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

        self.routedata = pd.merge(self.flighttimes, self.flights[['FLIGHT_ID', 'CALLSIGN']])
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

        self.routedata['TIME'] = pd.to_datetime(self.routedata['TIME'], format="%d-%m-%Y %H:%M:%S")

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

        self.routedata['SIM_TIME'] = self.routedata['TIME'] - self.datetime0
        self.routedata['SIM_TIME'] = self.routedata['SIM_TIME'].dt.total_seconds()

        self.trackdata['SIM_TIME'] = self.trackdata['ACTUAL_TIME'] - self.datetime0
        self.trackdata['SIM_TIME'] = self.trackdata['SIM_TIME'].dt.total_seconds()
        if self.deltat:
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

        self.routedata = self.routedata.sort_values(by=['SIM_TIME'])
        self.routedata = self.routedata.loc[self.routedata['SIM_TIME'] >= self.time0]
        self.routedata['SIM_TIME'] = self.routedata['SIM_TIME'] - self.routedata['SIM_TIME'].iloc[0]

        self.trackdata = self.trackdata.sort_values(by=['SIM_TIME'])
        self.trackdata = self.trackdata.loc[self.trackdata['SIM_TIME'] >= self.time0]
        self.trackdata['SIM_TIME'] = self.trackdata['SIM_TIME'] - self.trackdata['SIM_TIME'].iloc[0]

    def get_wpts(self, callsign, time_create, orig, dest):
        """
        Function: Get the commands string for adding the waypoints
        Args:
            callsign:       callsign [str]
            time_create:    simulation time of aircraft create [float]
            orig:           origin [str]
            dest:           destination [str]
        Returns:
            strlst:         list with strings for adding waypoints

        Created: Bob van Dillen
        Date: 1-12-2021
        """

        route = self.routedata.loc[self.routedata['CALLSIGN'] == callsign]

        strlst = []
        tlst = []
        wptstr = ""
        for wpt in range(len(route)):
            wptname = route['LOCATION_NAME'].iloc[wpt]
            wpttime = route['SIM_TIME'].iloc[wpt]
            if wpttime > time_create and wptname != orig and wptname != dest:
                if len(strlst) == 0:
                    strlst.append("ADDWPT "+callsign+", "+wptname)
                    tlst.append(time_create+0.01)  # Add 0.01 to ensure the right order
                    wptstr = callsign+" AFTER "+wptname+" ADDWPT "
                else:
                    strlst.append(wptstr+wptname)
                    tlst.append(tlst[-1]+0.01)  # Add 0.01 to ensure the right order
                    wptstr = callsign+" AFTER "+wptname+" ADDWPT "

        return strlst, tlst

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

        command = ["DATE "+str(simday)+", "+str(simmonth)+", "+str(simyear)+", "+simtime, "MAP 252", "MAP 752"]
        commandtime = [0., 0., 0.]

        for acid in self.trackdata['CALLSIGN'].unique():
            flight = self.flights.loc[self.flights['CALLSIGN'] == acid].iloc[0]
            track = self.trackdata.loc[self.trackdata['CALLSIGN'] == acid]

            t_cre = track['SIM_TIME'].iloc[0]
            t_del = track['SIM_TIME'].iloc[-1]

            acflightid = str(flight['FLIGHT_ID'])
            actype = flight['ICAO_ACTYPE']
            orig = flight['ADEP']
            dest = flight['DEST']
            wpts, wptst = self.get_wpts(acid, t_cre, orig, dest)

            lat = str(track['LATITUDE'].iloc[0])
            lon = str(track['LONGITUDE'].iloc[0])
            hdg = str(track['HEADING'].iloc[0])
            alt = str(track['ALTITUDE'].iloc[0])
            spd = str(track['SPEED'].iloc[0])

            # str_cre = "CRE "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd
            str_crereplay = "CREREPLAY "+acflightid+", "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd
            str_orig = "ORIG "+acid+" "+orig
            str_dest = "DEST "+acid+" "+dest
            str_del = "DEL "+acid
            command += [str_crereplay, str_orig, str_dest] + wpts + [str_del]
            commandtime += [t_cre] + [t_cre+0.005]*2+wptst + [t_del]

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
        # Get the number of data points with the same time stamp
        unique, count = np.unique(simt, return_counts=True)
        simt_count = np.repeat(count, count)

        flightid = np.array(self.trackdata['FLIGHT_ID'])
        acid = list(self.trackdata['CALLSIGN'])
        actype = list(self.trackdata['ICAO_ACTYPE'])
        lat = np.array(self.trackdata['LATITUDE'])
        lon = np.array(self.trackdata['LONGITUDE'])
        hdg = np.array(self.trackdata['HEADING'])
        alt = np.array(self.trackdata['ALTITUDE'])*ft
        spd = np.array(self.trackdata['SPEED'])*kts
        return simt, simt_count, flightid, acid, actype, lat, lon, hdg, alt, spd


if __name__ == '__main__':
    path = os.path.expanduser("~") + r"\PycharmProjects\bluesky\scenario\vemmis1209"
    vemmis1209 = VEMMISRead(path, 0)
