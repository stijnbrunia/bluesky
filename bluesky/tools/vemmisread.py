"""
This python file is used for reading and preparing the VEMMIS data

Created by: Bob van Dillen
Date: 22-11-2021
"""

import datetime
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

    def __init__(self, data_path, time0=None, deltat=None):
        self.data_path = data_path

        self.time0 = time0

        self.deltat = deltat

        self.lat0 = 52+18/60+29/3600
        self.lon0 = 4+45/60+51/3600

        self.flights = None
        self.flighttimes = None
        self.tracks = None
        self.flightdata = None
        self.routedata = None
        self.trackdata = None

        self.datetime0 = None

        self.read_data()
        self.delete_nan()
        self.convert_data()
        self.relevant_data()
        self.get_coordinates()
        self.get_altitude()
        self.merge_data()
        self.sort_data()
        self.get_simtime()

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

    def delete_nan(self):
        """
        Function: Delete data points with NaN in the relevant columns
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 25-11-2021
        """

        self.flights = self.flights.dropna(subset=['FLIGHT_ID', 'CALLSIGN', 'ICAO_ACTYPE', 'ADEP', 'DEST', 'STATUS'])
        self.tracks = self.tracks.dropna(subset=['TIME', 'X', 'Y', 'MODE_C', 'SPEED', 'HEADING',
                                                 'FLIGHT_ID', 'T_START', 'T_END'])
        self.flighttimes = self.flighttimes.dropna(subset=['FLIGHT_ID', 'LOCATION_TYPE',
                                                           'LOCATION_NAME', 'TIME_TYPE', 'TIME'])

    def convert_data(self):
        """
        Function: Convert data to correct data types and determine the actual time
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.flights['T_UPDATE'] = pd.to_datetime(self.flights['T_UPDATE'], format="%d-%m-%Y %H:%M:%S")
        self.flights['T0'] = pd.to_datetime(self.flights['T0'], format="%d-%m-%Y %H:%M:%S")

        self.tracks['TIME'] = pd.to_timedelta(self.tracks['TIME']/100, unit='seconds')
        self.tracks['X'] = self.tracks['X'].str.replace(',', '.').astype('float')
        self.tracks['Y'] = self.tracks['Y'].str.replace(',', '.').astype('float')
        self.tracks['MODE_C'] = self.tracks['MODE_C'].str.replace(',', '.').astype('float')
        self.tracks['TRK_ROCD'] = self.tracks['TRK_ROCD'].str.replace(',', '.').astype('float')
        self.tracks['T_UPDATE'] = pd.to_datetime(self.tracks['T_UPDATE'], format="%d-%m-%Y %H:%M:%S")
        self.tracks['T_START'] = pd.to_datetime(self.tracks['T_START'], format="%d-%m-%Y %H:%M:%S")
        self.tracks['T_END'] = pd.to_datetime(self.tracks['T_END'], format="%d-%m-%Y %H:%M:%S")

        self.tracks['ACTUAL_TIME'] = self.tracks['T_START'] + self.tracks['TIME']

    def relevant_data(self):
        """
        Function: Select relevant data
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 22-11-2021
        """

        # Cancelled flights
        indx_delete = self.flights.index[self.flights['STATUS'].str.contains('CANCELLED')]
        self.flights = self.flights.drop(indx_delete)

        # Waypoints
        self.flighttimes = self.flighttimes.loc[self.flighttimes['TIME_TYPE'] == 'ACTUAL']
        self.flighttimes = self.flighttimes.loc[self.flighttimes['LOCATION_TYPE'] == 'RP']

        # Start time
        if self.time0:
            # Convert to datetime
            datetime0 = min(self.flights['T0'])
            self.time0 = datetime.datetime.strptime(self.time0, '%H:%M:%S')
            self.time0 = self.time0.replace(year=datetime0.year, month=datetime0.month, day=datetime0.day)

            self.tracks = self.tracks.loc[self.tracks['ACTUAL_TIME'] >= self.time0]

    def get_coordinates(self):
        """
        Function: Calculate coordinates from x and y position
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.tracks['LATITUDE'] = self.tracks['X']/128
        self.tracks['LONGITUDE'] = self.tracks['Y']/128

        qdr = np.degrees(np.arctan2(self.tracks['LATITUDE'], self.tracks['LONGITUDE']))
        qdr = np.where(qdr < 0, qdr+360, qdr)
        d = np.array(np.sqrt(self.tracks['LATITUDE']**2 + self.tracks['LONGITUDE']**2))

        self.tracks['LATITUDE'], self.tracks['LONGITUDE'] = qdrpos(self.lat0, self.lon0, qdr, d)

    def get_altitude(self):
        """
        Function: Determine altitude from MODE_C
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.tracks['ALTITUDE'] = self.tracks['MODE_C']*100

    def merge_data(self):
        """
        Function: Merge flights data into the other data, to get e.g. callsign
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.flightdata = pd.merge(self.flights, self.tracks[['FLIGHT_ID', 'ACTUAL_TIME', 'T_END', 'LATITUDE',
                                                              'LONGITUDE', 'HEADING', 'ALTITUDE', 'SPEED']],
                                   on='FLIGHT_ID')
        self.flightdata = self.flightdata.sort_values(by=['ACTUAL_TIME'])
        self.flightdata.drop_duplicates(subset='FLIGHT_ID', keep='first', inplace=True)

        self.routedata = pd.merge(self.flighttimes, self.flights[['FLIGHT_ID', 'CALLSIGN']], on='FLIGHT_ID')

        self.trackdata = pd.merge(self.tracks, self.flights[['FLIGHT_ID', 'CALLSIGN']], on='FLIGHT_ID')

    def sort_data(self):
        """
        Function: Sort the data by time
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        # Take out first and last data point for safe aircraft create/delete
        indx_first = list(self.trackdata.index[~self.trackdata.duplicated(subset='FLIGHT_ID', keep='first')])
        indx_last = list(self.trackdata.index[~self.trackdata.duplicated(subset='FLIGHT_ID', keep='last')])
        self.trackdata.drop(indx_first+indx_last, inplace=True)

        # Select flights that have data points
        flightids = self.trackdata['FLIGHT_ID'].unique()
        self.flightdata = self.flightdata.loc[self.flightdata['FLIGHT_ID'].isin(flightids)]

        # Sort
        self.flightdata = self.flightdata.sort_values(by=['ACTUAL_TIME'])
        self.trackdata = self.trackdata.sort_values(by=['ACTUAL_TIME'])

    def get_simtime(self):
        """
        Function: Determine the simulation time and optionally apply the fixed update rate
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
        """

        self.datetime0 = min(self.flightdata['ACTUAL_TIME'])

        self.flightdata['SIM_START'] = (self.flightdata['ACTUAL_TIME'] - self.datetime0).dt.total_seconds()
        self.flightdata['SIM_END'] = (self.flightdata['T_END'] - self.datetime0).dt.total_seconds()
        self.trackdata['SIM_TIME'] = (self.trackdata['ACTUAL_TIME'] - self.datetime0).dt.total_seconds()

        if self.deltat:
            self.flightdata['SIM_START'] = (self.flightdata['SIM_START'] / self.deltat).apply(np.ceil) * self.deltat
            self.flightdata['SIM_END'] = (self.flightdata['SIM_END'] / self.deltat).apply(np.ceil) * self.deltat
            self.trackdata['SIM_TIME'] = (self.trackdata['SIM_TIME'] / self.deltat).apply(np.ceil) * self.deltat
            self.trackdata.drop_duplicates(subset=['SIM_TIME', 'CALLSIGN'], keep='last', inplace=True)

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

        datetime_start = self.datetime0
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

        # Initial commands
        command = ["DATE "+str(simday)+", "+str(simmonth)+", "+str(simyear)+", "+simtime, "MAP 252", "MAP 752"]
        commandtime = [0., 0., 0.]

        # Create commands
        acflightid = self.flightdata['FLIGHT_ID'].astype(str)
        acid = self.flightdata['CALLSIGN']
        actype = self.flightdata['ICAO_ACTYPE']
        aclat = self.flightdata['LATITUDE'].astype(str)
        aclon = self.flightdata['LONGITUDE'].astype(str)
        achdg = self.flightdata['HEADING'].astype(str)
        acalt = self.flightdata['ALTITUDE'].astype(str)
        acspd = self.flightdata['SPEED'].astype(str)

        create = list("CREREPLAY "+acflightid+", "+acid+", "+actype+", " +
                      aclat+", "+aclon+", "+achdg+", "+acalt+", "+acspd)
        origin = list("ORIG "+acid+", "+self.flightdata['ADEP'])
        destination = list("DEST "+acid+", "+self.flightdata['DEST'])
        delete = list("DEL "+acid)

        tcreate = list(self.flightdata['SIM_START'])
        torigin = list(self.flightdata['SIM_START']+0.01)
        tdestination = list(self.flightdata['SIM_START']+0.01)
        tdelete = list(self.flightdata['SIM_END'])

        command += create + origin + destination + delete
        commandtime += tcreate + torigin + tdestination + tdelete

        # for acid in self.trackdata['CALLSIGN'].unique():
        #     flight = self.flights.loc[self.flights['CALLSIGN'] == acid].iloc[0]
        #     track = self.trackdata.loc[self.trackdata['CALLSIGN'] == acid]
        #
        #     t_cre = track['SIM_TIME'].iloc[0]
        #     t_del = track['SIM_TIME'].iloc[-1]
        #
        #     acflightid = str(flight['FLIGHT_ID'])
        #     actype = flight['ICAO_ACTYPE']
        #     orig = flight['ADEP']
        #     dest = flight['DEST']
        #     wpts, wptst = self.get_wpts(acid, t_cre, orig, dest)
        #
        #     lat = str(track['LATITUDE'].iloc[0])
        #     lon = str(track['LONGITUDE'].iloc[0])
        #     hdg = str(track['HEADING'].iloc[0])
        #     alt = str(track['ALTITUDE'].iloc[0])
        #     spd = str(track['SPEED'].iloc[0])
        #
        #     # str_cre = "CRE "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd
        #     str_crereplay = "CREREPLAY "+acflightid+", "+acid+", "+actype+", "+lat+", "+lon+", "+hdg+", "+alt+", "+spd
        #     str_orig = "ORIG "+acid+" "+orig
        #     str_dest = "DEST "+acid+" "+dest
        #     str_del = "DEL "+acid
        #     command += [str_crereplay, str_orig, str_dest] + wpts + [str_del]
        #     commandtime += [t_cre] + [t_cre+0.005]*2+wptst + [t_del]
        #
        #     i_cre = track.index[0]
        #     i_del = track.index[-1]
        #     self.trackdata = self.trackdata.drop([i_cre, i_del])

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
        lat = np.array(self.trackdata['LATITUDE'])
        lon = np.array(self.trackdata['LONGITUDE'])
        hdg = np.array(self.trackdata['HEADING'])
        alt = np.array(self.trackdata['ALTITUDE'])*ft
        spd = np.array(self.trackdata['SPEED'])*kts
        return simt, simt_count, flightid, acid, lat, lon, hdg, alt, spd


if __name__ == '__main__':
    path = os.path.expanduser("~") + r"\PycharmProjects\bluesky\scenario\vemmis1209"
    v = VEMMISRead(path, deltat=0.05)
