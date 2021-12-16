"""
This python file contains a class for managing replay flights which state is taken from data (database/file/... etc.).

Created by: Bob van Dillen
Date: 25-11-2021
"""

import copy
import numpy as np
import os
import bluesky as bs
from bluesky import stack
from bluesky.core import Entity
from bluesky.tools import aero, vemmisread
from bluesky.stack import stackbase


"""
Classes
"""


class TrafficReplay(Entity):
    """
    Class definition: Replay traffic based on data (VEMMIS)
    Methods:
        reset():            Reset variables
        crereplay():        Create aircraft which are updated from data
        delreplay():        Remove aircraft from replay callsigns list
        update():           Perform an update (step)
        uco_replay():       Stop taking the aircraft state from data (simulate the aircraft)
        store_prev():       Store the previous data point
        indices_update():   Get the indices for the traffic arrays and the trackdata
        get_indices():      Get indices of items in array/list

    Created by  : Bob van Dillen
    Date: 25-11-2021
    """

    isimt = 0
    isimt_count = 1
    iid = 2
    ilat = 3
    ilon = 4
    ihdg = 5
    ialt = 6
    ispd = 7

    def __init__(self):
        super().__init__()

        # Flight and track data
        self.trackdata = ()
        # Array with callsigns which state is taken from data/file
        self.replayid = []
        # Store parameters
        self.id_prev = None
        self.lat_prev = None
        self.lon_prev = None
        self.hdg_prev = None
        self.alt_prev = None
        self.gs_prev = None
        # Parameters used for update
        self.i_next = 0
        self.t_next = 0.0

        with self.settrafarrays():
            self.arr = []
            self.sid = []
            self.flighttype = []
            self.replay = np.array([], dtype=np.bool)  # Take aircraft state from data/file
            self.sid = []
            self.uco = np.array([], dtype=np.bool)
            self.wtc = []
            self.empt = []

    def reset(self):
        """
        Function: Reset variables
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 2-12-2021
        """

        # Flight and track data
        self.trackdata = ()
        # Array with callsigns which state is taken from data/file
        self.replayid = []
        # Store parameters
        self.id_prev = None
        self.lat_prev = None
        self.lon_prev = None
        self.hdg_prev = None
        self.alt_prev = None
        self.gs_prev = None
        # Parameters used for update
        self.i_next = 0
        self.t_next = 0.0

    @stack.command
    def crereplay(self, acid: str, actype: str, aclat: float, aclon: float, achdg: float, acalt: float, acspd: float,
                  acflighttype: str = '', acwtc: str = ''):
        """
        Function: Create aircraft which are updated from data
        Args:
            acid:           callsign [str, list]
            actype:         aircraft type [str, list]
            aclat:          latitude [float, array]
            aclon:          longitude [float, array]
            achdg:          heading [float, array]
            acalt:          altitude [float, array]
            acspd:          calibrated airspeed [float, array]
            acflighttype:   flight type [str]
            acwtc:          aircraft wtc [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """
        # Determine number of aircraft to create from array length of acid
        n = 1 if isinstance(acid, str) else len(acid)

        bs.traf.cre(acid, actype, aclat, aclon, achdg, acalt, acspd)

        # Update flight data
        self.flighttype[-n:] = [acflighttype]
        self.replay[-n:] = True
        self.wtc[-n:] = [acwtc]

        if acflighttype == 'INBOUND':
            self.arr[-n:] = ['ARR']
        elif acflighttype == 'OUTBOUND':
            self.sid[-n:] = ['SID']

        self.replayid = np.append(self.replayid, acid).tolist()
        # Update previous data point
        self.store_prev()

    def delreplay(self, idx):
        """
        Function: Remove aircraft from replay callsigns list
        Args:
            idx:    indices for traffic arrays
        Returns: -

        Created by: Bob van Dillen
        Date: 15-12-2021
        """

        ids = np.array(bs.traf.id)[idx]

        for acid in ids:
            # Check if this callsign was updated from data
            if acid in self.replayid:
                self.replayid.remove(acid)

    def update(self):
        """
        Function: Perform an update (step)
        Args: -
        Returns: -

        Remark: Slicing is used for accessing the track data ([i0: im])

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Check if there are aircraft
        if len(self.replayid) == 0:
            return

        # Check if the next data point is reached
        if self.t_next <= bs.sim.simt:
            # Track data index
            ac_count = self.trackdata[self.isimt_count][self.i_next]
            i0 = self.i_next  # First index
            im = self.i_next+ac_count  # Last index + 1 for slicing (e.g. i=0; ac_count=1, therefore [0:1])

            # Get indices
            itraf_up, itrackdata, ireplay = self.indices_update(self.trackdata[self.iid][i0: im])

            # Traffic with an update from the track data
            bs.traf.lat[itraf_up] = self.trackdata[self.ilat][i0: im][itrackdata]
            bs.traf.lon[itraf_up] = self.trackdata[self.ilon][i0: im][itrackdata]
            bs.traf.hdg[itraf_up] = self.trackdata[self.ihdg][i0: im][itrackdata]
            bs.traf.alt[itraf_up] = self.trackdata[self.ialt][i0: im][itrackdata]
            bs.traf.gs[itraf_up] = self.trackdata[self.ispd][i0: im][itrackdata]

            # Update variables
            self.store_prev()
            self.i_next = im
            self.t_next = self.trackdata[self.isimt][self.i_next]

            # Get indices for aircraft with no new data
            itraf_prev = self.get_indices(bs.traf.id, np.delete(self.replayid, ireplay))
            iprev = self.get_indices(self.id_prev, np.delete(self.replayid, ireplay))

        else:
            # Get indices when there is no new data point
            itraf_prev = self.get_indices(bs.traf.id, self.replayid)
            iprev = self.get_indices(self.id_prev, self.replayid)

        # Other traffic
        bs.traf.lat[itraf_prev] = self.lat_prev[iprev]
        bs.traf.lon[itraf_prev] = self.lon_prev[iprev]
        bs.traf.hdg[itraf_prev] = self.hdg_prev[iprev]
        bs.traf.alt[itraf_prev] = self.alt_prev[iprev]
        bs.traf.gs[itraf_prev] = self.gs_prev[iprev]

        # Update other speeds (wind)
        self.update_speed()

    def update_speed(self):
        """
        Function: Calculate the different speeds
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 1-12-2021
        """

        # Get indices for traffic arrays
        itraf = self.get_indices(bs.traf.id, self.replayid)

        # Check if there is no wind
        if bs.traf.wind.winddim == 0:
            bs.traf.gsnorth[itraf] = bs.traf.gs[itraf]*np.cos(np.radians(bs.traf.hdg[itraf]))
            bs.traf.gseast[itraf] = bs.traf.gs[itraf]*np.cos(np.radians(bs.traf.hdg[itraf]))
            bs.traf.tas[itraf] = bs.traf.gs[itraf]
            bs.traf.trk[itraf] = bs.traf.hdg[itraf]

        else:
            applywind = bs.traf.alt[itraf] > 50.*aero.ft

            bs.traf.windnorth[itraf], bs.traf.windeast[itraf] = bs.traf.wind.getdata(bs.traf.lat[itraf],
                                                                                     bs.traf.lon[itraf],
                                                                                     bs.traf.alt[itraf])
            tasnorth = bs.traf.gsnorth[itraf] - bs.traf.windnorth[itraf]*applywind
            taseast = bs.traf.gseast[itraf] - bs.traf.windnorth[itraf]*applywind
            bs.traf.tas[itraf] = np.sqrt(tasnorth*tasnorth + taseast*taseast)

            bs.traf.trk[itraf] = np.logical_not(applywind)*bs.traf.tas[itraf] +\
                                 applywind*np.degrees(np.arctan2(bs.traf.gseast[itraf], bs.traf.gsnorth[itraf])) % 360

    def uco_replay(self, idx):
        """
        Function: Stop taking the aircraft state from data (simulate the aircraft)
        Args:
            idx:    index for traffic arrays
        Returns: -

        Created by: Bob van Dillen
        Date: 1-12-2021
        """

        acid = bs.traf.id[idx]
        if acid in self.replayid:
            self.replay[idx] = False
            self.replayid.remove(acid)
            bs.stack.stackbase.del_scencmds(idx)

    def store_prev(self):
        """
        Function: Store the previous data point
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        self.id_prev = copy.deepcopy(bs.traf.id)
        self.lat_prev = copy.deepcopy(bs.traf.lat)
        self.lon_prev = copy.deepcopy(bs.traf.lon)
        self.hdg_prev = copy.deepcopy(bs.traf.hdg)
        self.alt_prev = copy.deepcopy(bs.traf.alt)
        self.gs_prev = copy.deepcopy(bs.traf.gs)

    def indices_update(self, id_trackdata):
        """
        Function: Get the indices for the traffic arrays and the trackdata
        Args:
            id_trackdata:   callsigns with available data [array]
        Returns:
            itraf_update:   index track data update for the traffic arrays [array]
            itrackdata:     index for the trackdata [array]
            itraf_prev:     index previous update for the traffic arrays [array]
            iprev:          index previous update for prev arrays [array]

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Get callsigns that need an update and index for trackdata
        id_update, ireplay, itrackdata = np.intersect1d(self.replayid, id_trackdata, return_indices=True)
        # Get index for traffic arrays
        itraf_update = self.get_indices(bs.traf.id, id_update)

        return itraf_update, itrackdata, ireplay

    @staticmethod
    def get_indices(arr, items):
        """
        Function: Get indices of items in array/list
        Args:
            arr:    array/list containing the items [array, list]
            items:  get indices of items [int, float, str, list, array]
        Returns:
            i:      indices [array]

        Created by: Bob van Dillen
        Date: 1-12-2021
        """

        if isinstance(items, (str, int, float)):
            i = np.nonzero(np.array([items])[:, None] == arr)[1]
        else:
            i = np.nonzero(np.array(items)[:, None] == arr)[1]
        return i


"""
Static functions
"""


# def delreplay(func):
#     """
#     Function: Decorator function for deleting an aircraft
#     Args:
#         func:   function
#     Returns: -
#
#     Created by: Bob van Dillen
#     Date: 30-11-2021
#     """
#
#     def inner(*args, **kwargs):
#         # Multiple delete
#         if len(args[1]) > 1:
#             # Get callsigns
#             ids = np.array(bs.traf.id)[args[1]].tolist()
#             for acid in ids:
#                 # Delete from replay callsigns
#                 if acid in bs.traf.trafreplay.replayid:
#                     ireplay = bs.traf.trafreplay.get_indices(bs.traf.trafreplay.replayid, acid)
#                     bs.traf.trafreplay.replayid = list(np.delete(bs.traf.trafreplay.replayid, ireplay))
#
#         # Single delete
#         else:
#             # Get callsign
#             acid = np.array(bs.traf.id)[args[1]]
#             # Delete from replay callsigns
#             if acid in bs.traf.trafreplay.replayid:
#                 ireplay = bs.traf.trafreplay.get_indices(bs.traf.trafreplay.replayid, acid)
#                 bs.traf.trafreplay.replayid = list(np.delete(bs.traf.trafreplay.replayid, ireplay))
#
#         # Delete aircraft
#         func(*args, **kwargs)
#
#         # Update previous data point
#         bs.traf.trafreplay.store_prev()
#
#     return inner


def read_replay(datatype, folder, time0=None):
    """
    Function: Read and process track data for trafficreplay
    Args:
        datatype:   type of flight data
        folder: name of the folder containing the files [str]
        time0:  start time in seconds [int, float]
    Returns: -

    Created by: Bob van Dillen
    Date: 25-11-2021
    """

    # Get path of the directory
    path = os.getcwd()+"\\scenario\\"+folder.lower()

    # Check if directory exists
    if os.path.isdir(path):
        # Reset the simulation
        bs.sim.reset()

        # VEMMIS Data
        if datatype.upper() == 'VEMMIS':
            # Check if it contains the correct files
            if not vemmisread.files_check(path):
                return False, f"REPLAY: The folder does not contain all the required files"

            # Prepare the data
            bs.scr.echo('Preparing data from '+path+' ...')
            vemmisdata = vemmisread.VEMMISRead(path, time0, deltat=bs.sim.simdt)
            # Load flight data
            bs.scr.echo('Loading flight data ...')
            commands, commandstime = vemmisdata.get_flightdata()
            # Load track data
            bs.scr.echo('Loading track data ...')
            bs.traf.trafreplay.trackdata = vemmisdata.get_trackdata()

        else:
            return False, f"REPLAY: Type is not supported"
    else:
        return False, f"REPLAY: Folder does not exist"

    # Initialize simulation
    bs.scr.echo('Initialize simulation ...')
    # Create first aircraft
    stackbase.Stack.scencmd = commands
    stackbase.Stack.scentime = commandstime
    # Get the index and the SIM_TIME of the next data point
    bs.traf.trafreplay.i_next = 0
    bs.traf.trafreplay.t_next = bs.traf.trafreplay.trackdata[0][bs.traf.trafreplay.i_next]

    bs.scr.echo('Done')
