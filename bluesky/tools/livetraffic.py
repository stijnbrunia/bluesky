"""
This python file is used to get live data as data source

Created by: Bob van Dillen
Date: 14-1-2022
"""

import requests
import pandas as pd
import numpy as np
import bluesky as bs
from bluesky.tools import aero, misc


"""
Classes
"""


class OpenSkySource:
    """
    Class definition: OpenSky as data source for data feed
    Methods:
        update_trackdata(): Update the track data

    Created by: Bob van Dillen
    Date: 14-1-2022
    """

    def __init__(self):
        self.latmin = 50.564026
        self.latmax = 54.670686
        self.lonmin = 2.956581
        self.lonmax = 7.80055

        self.url = 'https://opensky-network.org/api/states/all?lamin='+str(self.latmin)+'&lomin='+str(self.lonmin)+\
                   '&lamax='+str(self.latmax)+'&lomax='+str(self.lonmax)
        self.cols = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'lon', 'lat',
                     'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 'sensors',
                     'geo_altitude', 'squawk', 'spi', 'position_source', 'none']

        self.t_prev = 0.

    def live(self):
        try:
            data = requests.get(self.url).json()
            data_df = pd.DataFrame(data['states'], columns=self.cols)
            data_df.dropna(subset=['callsign', 'lon', 'lat', 'baro_altitude', 'velocity', 'true_track'],
                           inplace=True)

            commands = ['SWRAD HISTORY']
            commandstime = [0.]

            acid = data_df['callsign'].str.strip()
            aclat = data_df['lat'].astype(str)
            aclon = data_df['lon'].astype(str)
            achdg = data_df['true_track'].astype(str)
            acalt = (data_df['baro_altitude']/aero.ft).astype(str)
            acspd = (data_df['velocity']/aero.kts).astype(str)

            create = list("CRE "+acid+" B738 "+aclat+" "+aclon+" "+achdg+" "+acalt+" "+acspd)
            datafeed = list("ADDDATAFEED "+acid)

            commands += create + datafeed
            commandstime += [0.]*len(create) + [0.01]*len(datafeed)
        except:
            commands = []
            commandstime = []

        return commands, commandstime

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

        if simtime-self.t_prev >= 11.:
            try:
                data = requests.get(self.url).json()
                data_df = pd.DataFrame(data['states'], columns=self.cols)
                data_df.dropna(subset=['callsign', 'lon', 'lat', 'baro_altitude', 'velocity', 'true_track'],
                               inplace=True)

                ids = list(data_df['callsign'].str.strip())
                lat = np.array(data_df['lat'])
                lon = np.array(data_df['lon'])
                hdg = np.array(data_df['true_track'])
                alt = np.array(data_df['baro_altitude'])
                gs = np.array(data_df['velocity'])

                new_ids = np.setdiff1d(ids, bs.traf.id)
                inew = misc.get_indices(ids, new_ids)
                for i in range(len(new_ids)):
                    bs.traf.cre(new_ids[i], 'B738', lat[inew[i]], lon[inew[i]], hdg[inew[i]], alt[inew[i]], gs[inew[i]])
                    idx = misc.get_indices(bs.traf.id, new_ids[i])
                    bs.traf.trafdatafeed.setdatafeed(idx[0])

            except:
                ids = []
                lat = np.array([])
                lon = np.array([])
                hdg = np.array([])
                alt = np.array([])
                gs = np.array([])

            self.t_prev = simtime

        else:
            ids = []
            lat = np.array([])
            lon = np.array([])
            hdg = np.array([])
            alt = np.array([])
            gs = np.array([])

        return ids, lat, lon, hdg, alt, gs
