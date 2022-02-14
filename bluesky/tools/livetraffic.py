"""
This python file is used to get live data as data source

Created by: Bob van Dillen
Date: 14-1-2022
"""

import requests
import pandas as pd
import pickle
import numpy as np
import datetime
import bluesky as bs
from bluesky.tools import aero, cachefile, misc

bs.settings.set_variable_defaults(data_path='data')


# Global variables
actypes_version = 'v20220203'


"""
Classes
"""


class OpenSkySource:
    """
    Class definition: OpenSky as data source for data feed
    Methods:
        reset():            Reset variables
        load_actypes():     Load aircaft types dictionary
        request_data():     Request the data
        live():             Initiate live traffic
        update_trackdata(): Update the track data
        create_new():       Create new aircraft and delete from track data
        delete_old():       Delete old aircraft

    Created by: Bob van Dillen
    Date: 14-1-2022
    """

    actypes = None

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

        self.load_actypes()

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

    def load_actypes(self):
        """
        Function: Load aircaft types dictionary
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 3-2-2022
        """

        if self.actypes is None:
            with cachefile.openfile('actypes.p', actypes_version) as cache:
                try:
                    self.actypes = cache.load()
                except (pickle.PickleError, cachefile.CacheError) as e:
                    print(e.args[0])

                    # Read file
                    acdata = pd.read_csv(bs.settings.data_path + '/actypes.csv', sep=';')
                    # Drop not usable rows for relevant columns
                    acdata.dropna(subset=['icao24', 'typecode'], inplace=True)
                    # Change the index in icao24
                    acdata.set_index('icao24', inplace=True)

                    self.actypes = dict(acdata['typecode'])

                    cache.dump(self.actypes)

    def request_data(self):
        """
        Function: Request the data
        Args: -
        Returns:
            data:   live aircraft data [DataFrame]

        Created by: Bob van Dillen
        Date: 3-2-2022
        """

        try:
            # Get "raw" json data
            rawdata = requests.get(self.url).json()

            # Convert to pandas DataFrame
            data = pd.DataFrame(rawdata['states'])
            if data.shape[1] == 17:
                data.columns = self.cols[:-1]
            else:
                data.columns = self.cols

            # Process data
            data['callsign'] = data['callsign'].str.replace(' ', '')
            data['callsign'].replace('', float('NaN'), inplace=True)
            data.dropna(subset=['icao24', 'callsign', 'lon', 'lat', 'baro_altitude', 'velocity', 'true_track'],
                        inplace=True)

            # Get the date and time
            epochtime = rawdata['time']
            data_datetime = datetime.datetime.utcfromtimestamp(epochtime)

        except requests.exceptions.RequestException as e:
            print(e)
            data = pd.DataFrame(columns=self.cols)
            data_datetime = datetime.datetime.now()

        return data_datetime, data

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

        data_datetime, data = self.request_data()

        if len(data) > 0:
            # Initial commands
            cmds = ["DATE "+data_datetime.strftime('%d %m %Y %H:%M:%S'), 'HISTORY 3']
            cmdst = [0.]*2

            # Get aircraft data
            acid           = data['callsign'].str.strip()
            data['actype'] = [self.actypes.get(str(icao24), 'B738') for icao24 in data['icao24']]
            actype         = data['actype']
            aclat          = data['lat'].astype(str)
            aclon          = data['lon'].astype(str)
            achdg          = data['true_track'].astype(str)
            acalt          = (data['baro_altitude']/aero.ft).astype(str)
            data['cas']    = aero.vtas2cas(data['velocity'], data['baro_altitude'])/aero.kts  # Assume GS = TAS
            acspd          = data['cas'].astype(str)

            # Get commands
            # Create
            cmds  += list("CRE "+acid+", "+actype+", "+aclat+" "+aclon+" "+achdg+" "+acalt+" "+acspd)
            cmdst += [0.]*len(data)

            # Data feed
            cmds  += list("SETDATAFEED "+acid+", OPENSKY")
            cmdst += [0.01]*len(data)

            # SSR Code
            ssrdata = data.dropna(subset=['squawk'])
            cmds   += list("SSRCODE "+ssrdata['callsign']+", "+ssrdata['squawk'])
            cmdst  += [0.01]*len(ssrdata)

            # Labels
            ssrlabel = data.loc[(data['baro_altitude']/aero.ft <= 1500) | (data['baro_altitude']/aero.ft >= 24500)]
            cmds += list("SSRLABEL "+ssrlabel['callsign']+", ON")
            cmds += list("TRACKLABEL "+ssrlabel['callsign']+", OFF")
            cmdst += [0.01]*2*len(ssrlabel)

            # Sort
            cmds_df = pd.DataFrame({'COMMAND': cmds, 'TIME': cmdst})
            cmds_df = cmds_df.sort_values(by=['TIME'])
            cmds    = list(cmds_df['COMMAND'])
            cmdst   = list(cmds_df['TIME'])

        else:
            bs.scr.echo("LIVE: Initializing live traffic failed. Reset and try again.")
            cmds  = []
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
        if simtime-self.t_prev >= 12.5:
            data_datetime, data = self.request_data()

            # Commands
            cmds = []

            # Create new aircraft commands
            cmds, data = self.create_new(cmds, data)

            # Get aircraft data
            ids = list(data['callsign'])
            lat = np.array(data['lat'])
            lon = np.array(data['lon'])
            hdg = np.array(data['true_track'])
            alt = np.array(data['baro_altitude'])
            gs = np.array(data['velocity'])

            # Set labels
            ssrlabel = data.loc[(data['baro_altitude']/aero.ft <= 1500) | (data['baro_altitude']/aero.ft >= 24500)]
            tracklabel = data.loc[(1500 <= data['baro_altitude']/aero.ft) & (data['baro_altitude'] <= 24500)]
            cmds += list('TRACKLABEL '+tracklabel['callsign']+', ON')
            cmds += list('TRACKLABEL '+ssrlabel['callsign']+', OFF')
            cmds += list('SSRLABEL '+tracklabel['callsign']+', OFF')
            cmds += list('SSRLABEL '+ssrlabel['callsign']+', ON')

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

    def create_new(self, cmds, data):
        """
        Function: Create new aircraft and delete from trackdata
        Args:
            cmds:       commands [list]
            data:       aircraft data [DataFrame]
        Returns:
            cmds:       commands [list]
            data_df:    aircraft data [DataFrame]

        Created by: Bob van Dillen
        Date: 17-1-2022
        """

        ids = list(data['callsign'])

        new_ids = np.setdiff1d(ids, bs.traf.id)
        inew    = misc.get_indices(ids, new_ids)

        # No new aircraft
        if len(inew) == 0:
            return cmds, data

        # Aircraft data
        icao24 = list(data['icao24'])
        lat    = np.array(data['lat'])
        lon    = np.array(data['lon'])
        hdg    = np.array(data['true_track'])
        alt    = np.array(data['baro_altitude'])
        gs     = np.array(data['velocity'])

        # Loop over new aircraft
        for i in inew:
            # Aircraft data
            acid   = ids[i]
            actype = self.actypes.get(icao24[i], 'B738')
            aclat  = str(lat[i])
            aclon  = str(lon[i])
            achdg  = str(hdg[i])
            acalt  = str(alt[i]/aero.ft)
            acspd  = str(aero.tas2cas(gs[i], alt[i])/aero.kts)  # Assume GS = TAS

            # Create commands
            cmds.append("CRE "+acid+", "+actype+", "+aclat+", "+aclon+", "+achdg+", "+acalt+", "+acspd)
            cmds.append("SETDATAFEED "+acid+" OPENSKY")
            if float(acalt) <= 1500 or float(acalt) >= 24500:
                cmds.append("SSRLABEL "+acid+", ON")
                cmds.append("TRACKLABEL "+acid+", OFF")

            # Remove aircraft from track data
            idrop = data.index[data['callsign'] == acid]
            data.drop(idrop, inplace=True)

        return cmds, data

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
        iold  = np.nonzero(bs.traf.trafdatafeed.lastupdate >= 1*60.)[0]

        idelete = np.intersect1d(ilive, iold)
        ids     = np.array(bs.traf.id)[idelete]

        for acid in ids:
            cmds.append("DEL "+acid)

        return cmds

