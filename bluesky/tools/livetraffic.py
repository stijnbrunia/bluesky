"""
This python file is used to get live data as data source

Created by: Bob van Dillen
Date: 14-1-2022
"""

import requests
import pandas as pd
import numpy as np
import datetime
import bluesky as bs
from bluesky.tools import aero, misc

bs.settings.set_variable_defaults(data_path='data')


"""
Classes
"""


class OpenSkySource:
    """
    Class definition: OpenSky as data source for data feed
    Methods:
        reset():            Reset variables
        live():             Initiate live traffic
        initial():          Take initial aircraft positions from live data
        update_trackdata(): Update the track data
        create_new():       Create new aircraft and delete from track data

    Created by: Bob van Dillen
    Date: 14-1-2022
    """

    def __init__(self):
        self.mode = None

        self.latmin = 50.564026
        self.latmax = 54.670686
        self.lonmin = 2.956581
        self.lonmax = 7.80055

        self.url = 'https://opensky-network.org/api/states/all?lamin='+str(self.latmin)+'&lomin='+str(self.lonmin)+\
                   '&lamax='+str(self.latmax)+'&lomax='+str(self.lonmax)
        self.cols = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'lon', 'lat',
                     'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 'sensors',
                     'geo_altitude', 'squawk', 'spi', 'position_source', 'none']

        actypesf = open(bs.settings.data_path + '\\aircraft_db.csv', 'r')
        self.actypes = dict([line.split(',')[0:3:2] for line in actypesf])
        actypesf.close()

        self.t_prev = 0.

    def reset(self):
        """
        Function: Reset variables
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 17-1-2022
        """

        self.mode = None
        self.t_prev = 0.

    def live(self):
        """
        Function: Initiate live traffic
        Args: -
        Returns:
            commands:       initial commands [list]
            commandstime:   initial commands time [list]

        Created by: Bob van Dillen
        Date: 15-1-2022
        """

        try:
            # Request data
            data = requests.get(self.url).json()
            # Process data
            data_df = pd.DataFrame(data['states'], columns=self.cols)
            data_df['callsign'] = data_df['callsign'].str.strip()
            data_df['callsign'].replace('', float('NaN'), inplace=True)
            data_df.dropna(subset=['callsign', 'lon', 'lat', 'baro_altitude', 'velocity', 'true_track'],
                           inplace=True)
            data_df['actype'] = [self.actypes.get(str(i), 'B738').upper() for i in data_df['icao24']]

            # Date and time
            epochtime = data['time']
            datetime0 = datetime.datetime.utcfromtimestamp(epochtime)

            # Initial commands
            cmds = ["DATE "+datetime0.strftime('%d %m %Y %H:%M:%S')]
            cmdst = [0.]

            # Get aircraft data
            acid = data_df['callsign'].str.strip()
            actype = data_df['actype']
            aclat = data_df['lat'].astype(str)
            aclon = data_df['lon'].astype(str)
            achdg = data_df['true_track'].astype(str)
            acalt = (data_df['baro_altitude']/aero.ft).astype(str)
            data_df['cas'] = aero.vtas2cas(data_df['velocity'], data_df['baro_altitude'])/aero.kts  # Assume GS = TAS
            acspd = data_df['cas'].astype(str)

            # Get commands
            # Create
            cmds += list("CRE "+acid+", "+actype+", "+aclat+" "+aclon+" "+achdg+" "+acalt+" "+acspd)
            cmdst += [0.]*len(data_df)

            # Data feed
            cmds += list("SETDATAFEED "+acid+", OPENSKY")
            cmdst += [0.01]*len(data_df)

            # SSR Code
            ssrdata = data_df.dropna(subset=['squawk'])
            cmds += list("SSRCODE "+ssrdata['callsign']+", "+ssrdata['squawk'])
            cmdst += [0.01]*len(ssrdata)

            # Sort
            cmds_df = pd.DataFrame({'COMMAND': cmds, 'TIME': cmdst})
            cmds_df = cmds_df.sort_values(by=['TIME'])
            cmds = list(cmds_df['COMMAND'])
            cmdst = list(cmds_df['TIME'])

        except:
            bs.scr.echo("LIVE: Initializing live traffic failed. Reset and try again.")
            cmds = []
            cmdst = []

        return cmds, cmdst

    def update_trackdata(self, simtime):
        """
        Function: Update the track data for the current simulation time
        Args:
            simtime:    simulation time [float]
        Returns:
            ids:        callsigns [list]
            lat:        latitudes [array]
            lon:        longitudes [array]
            hdg:        headings [array]
            alt:        altitudes [array]
            gs:         ground speeds [array]

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        # Set running
        running = True

        # Get new data every 12.5 seconds
        if simtime-self.t_prev > 12.5:
            try:
                # Request data
                data = requests.get(self.url).json()
                # Process data
                data_df = pd.DataFrame(data['states'], columns=self.cols)
                data_df['callsign'] = data_df['callsign'].str.strip()
                data_df['callsign'].replace('', float('NaN'), inplace=True)
                data_df.dropna(subset=['callsign', 'lon', 'lat', 'baro_altitude', 'velocity', 'true_track'],
                               inplace=True)
                data_df['actype'] = [self.actypes.get(str(i), 'B738').upper() for i in data_df['icao24']]
            except:
                data_df = pd.DataFrame(columns=self.cols+['actype'])

            # Commands
            cmds = []

            # Create new aircraft commands
            cmds, data_df = self.create_new(cmds, data_df)

            # Get aircraft data
            ids = list(data_df['callsign'])
            lat = np.array(data_df['lat'])
            lon = np.array(data_df['lon'])
            hdg = np.array(data_df['true_track'])
            alt = np.array(data_df['baro_altitude'])
            gs = np.array(data_df['velocity'])

            # Delete inactive aircraft
            self.delete_old(cmds)

            # Set new previous time
            self.t_prev = simtime

        else:
            cmds = []
            ids = []
            lat = np.array([])
            lon = np.array([])
            hdg = np.array([])
            alt = np.array([])
            gs = np.array([])

        return running, cmds, ids, lat, lon, hdg, alt, gs

    @staticmethod
    def create_new(cmds, data_df):
        """
        Function: Create new aircraft and delete from trackdata
        Args:
            cmds:       commands [list]
            data_df:    data frame containing the new data [DataFrame]
            mode:       datasource mode [str]
        Returns:
            cmds:       commands [list]
            data_df:    data frame containing the new data [DataFrame]

        Created by: Bob van Dillen
        Date: 17-1-2022
        """

        ids = list(data_df['callsign'])
        types = list(data_df['actype'])
        lat = np.array(data_df['lat'])
        lon = np.array(data_df['lon'])
        hdg = np.array(data_df['true_track'])
        alt = np.array(data_df['baro_altitude'])
        gs = np.array(data_df['velocity'])

        new_ids = np.setdiff1d(ids, bs.traf.id)
        inew = misc.get_indices(ids, new_ids)

        # Loop over new aircraft
        for i in inew:
            # Aircraft data
            acid = ids[i]
            actype = types[i]
            aclat = str(lat[i])
            aclon = str(lon[i])
            achdg = str(hdg[i])
            acalt = str(alt[i]/aero.ft)
            acspd = str(aero.tas2cas(gs[i], alt[i])/aero.kts)  # Assume GS = TAS

            # Create commands
            cmds.append("CRE "+acid+", "+actype+", "+aclat+", "+aclon+", "+achdg+", "+acalt+", "+acspd)
            cmds.append("SETDATAFEED "+acid+" OPENSKY")

            # Remove aircraft from track data
            idrop = data_df.index[data_df['callsign'] == acid]
            data_df.drop(idrop, inplace=True)

        return cmds, data_df

    @staticmethod
    def delete_old(cmds):
        """
        Function: Delete old aircraft
        Args:
            cmds:   commands [list]
        Returns:
            cmds:   commands [list]

        Created by: Bob van Dillen
        Date: 17-1-2022
        """

        ilive = np.nonzero(np.array(bs.traf.trafdatafeed.source) == 'OPENSKY')[0]
        iold = np.nonzero(bs.traf.trafdatafeed.lastupdate >= 1*60.)[0]

        idelete = np.intersect1d(ilive, iold)
        ids = np.array(bs.traf.id)[idelete]

        for acid in ids:
            cmds.append("DEL "+acid)

        return cmds

