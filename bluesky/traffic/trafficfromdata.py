"""
This python file contains a class for managing flights which state is taken from data (database/file/... etc.).

Created by: Bob van Dillen
Date: 25-11-2021
"""
import pickle

import numpy as np
import os
import bluesky as bs
from bluesky import stack
from bluesky.core import Entity
from bluesky.tools import aero, cachefile, vemmisread
from bluesky.stack import stackbase


"""
Classes
"""


class TrafficFromData(Entity):
    """
    Class definition: Traffic updated from data/file
    Methods:
        reset():            Reset variables
        crefromdata():      Create aircraft which are updated from data
        delfromdata():      Delete aircraft which are updated from data
        update():           Perform an update (step)
        uco_fromdata():     Stop taking the aircraft state from data (simulate the aircraft)
        store_prev():       Store the previous data point
        indices_update():   Get the indices for the traffic arrays and the trackdata
        get_indices():      Get indices of items in array/list

    Created by  : Bob van Dillen
    Date: 25-11-2021
    """

    isimt = 0
    isimt_i = 1
    iflightid = 2
    iid = 3
    itype = 4
    ilat = 5
    ilon = 6
    ihdg = 7
    ialt = 8
    ispd = 9

    def __init__(self):
        super().__init__()

        # Flight and track data
        self.trackdata = ()
        # Array with flight ids which state is taken from data/file
        self.flightid_fromdata = np.array([])
        # Store parameters
        self.lat_prev = None
        self.lon_prev = None
        self.hdg_prev = None
        self.alt_prev = None
        self.gs_prev = None
        # Parameters used for update
        self.i_next = 0
        self.t_next = 0.0

        with self.settrafarrays():
            self.flightid = np.array([])                 # Flight ID
            self.fromdata = np.array([], dtype=np.bool)  # Take aircraft state from data/file

    def reset(self):
        """
        Function: Reset variables
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 2-12-2021
        """

        super().reset()

        # Flight and track data
        self.trackdata = ()
        # Array with flight ids which state is taken from data/file
        self.flightid_fromdata = np.array([])
        # Store parameters
        self.lat_prev = None
        self.lon_prev = None
        self.hdg_prev = None
        self.alt_prev = None
        self.gs_prev = None
        # Parameters used for update
        self.i_next = 0
        self.t_next = 0.0

    @stack.command
    def crefromdata(self, acflightid: int,
                    acid: str, actype: str, aclat: float, aclon: float, achdg: float, acalt: float, acspd: float):
        """
        Function: Create aircraft which are updated from data
        Args:
            acflightid: flight id [int, array]
            acid:       callsign [str, list]
            actype:     aircraft type [str, list]
            aclat:      latitude [float, array]
            aclon:      longitude [float, array]
            achdg:      heading [float, array]
            acalt:      altitude [float, array]
            acspd:      calibrated airspeed [float, array]
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        bs.traf.cre(acid, actype, aclat, aclon, achdg, acalt, acspd)

        # Get index
        idx = self.get_indices(bs.traf.id, acid)
        # Update flight data
        self.flightid[idx] = acflightid
        self.fromdata[idx] = True
        self.flightid_fromdata = np.append(self.flightid_fromdata, acflightid)
        # Update previous data point
        self.store_prev()

    @stack.command
    def delfromdata(self, acflightid: int, acid: str):
        """
        Function: Delete aircraft which are updated from data
        Args:
            acflightid: flightid [int, array]
            acid:       callsign [str, list]
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Get index
        idx = self.get_indices(bs.traf.id, acid)

        # Delete aircraft
        bs.traf.delete(idx)

        # Delete from flighid_fromdata
        ifromdata = self.get_indices(self.flightid_fromdata, acflightid)
        self.flightid_fromdata = np.delete(self.flightid_fromdata, ifromdata)
        # Update previous data point
        self.store_prev()

    def update(self):
        """
        Function: Perform an update (step)
        Args: -
        Returns: -

        Remark: Slicing is used for accessing the track data ([i[0]: i[-1]])

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Check if there are aircraft
        if len(self.flightid_fromdata) == 0:
            return

        # Check if the next data point is reached
        if self.t_next <= bs.sim.simt:
            # Track data index
            i = self.trackdata[self.isimt_i][self.i_next]

            # Get indices
            itraf_up, itraf_prev, itrackdata = self.indices_update(self.trackdata[self.iflightid][i[0]: i[-1]+1])

            # Traffic with an update from the track data
            bs.traf.lat[itraf_up] = self.trackdata[self.ilat][i[0]: i[-1]+1][itrackdata]
            bs.traf.lon[itraf_up] = self.trackdata[self.ilon][i[0]: i[-1]+1][itrackdata]
            bs.traf.hdg[itraf_up] = self.trackdata[self.ihdg][i[0]: i[-1]+1][itrackdata]
            bs.traf.alt[itraf_up] = self.trackdata[self.ialt][i[0]: i[-1]+1][itrackdata]
            bs.traf.gs[itraf_up] = self.trackdata[self.ispd][i[0]: i[-1]+1][itrackdata]
            bs.traf.selalt[itraf_up] = self.trackdata[self.ialt][i[0]: i[-1]+1][itrackdata]

            # Update variables
            self.store_prev()
            self.i_next = i[-1]+1
            self.t_next = self.trackdata[self.isimt][self.i_next]

        else:
            # Get indices when there is no new data point
            itraf_prev = self.get_indices(self.flightid, self.flightid_fromdata)

        # Other traffic
        bs.traf.lat[itraf_prev] = self.lat_prev[itraf_prev]
        bs.traf.lon[itraf_prev] = self.lon_prev[itraf_prev]
        bs.traf.hdg[itraf_prev] = self.hdg_prev[itraf_prev]
        bs.traf.alt[itraf_prev] = self.alt_prev[itraf_prev]
        bs.traf.gs[itraf_prev] = self.gs_prev[itraf_prev]
        bs.traf.selalt[itraf_prev] = self.alt_prev[itraf_prev]

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
        itraf = self.get_indices(self.flightid, self.flightid_fromdata)

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

    def uco_fromdata(self, idx):
        """
        Function: Stop taking the aircraft state from data (simulate the aircraft)
        Args:
            idx:    index for traffic arrays
        Returns: -

        Created by: Bob van Dillen
        Date: 1-12-2021
        """

        self.fromdata[idx] = False
        acflightid = self.flightid[idx]
        iacflightid = self.get_indices(self.flightid_fromdata, acflightid)
        self.flightid_fromdata = np.delete(self.flightid_fromdata, iacflightid)

    def store_prev(self):
        """
        Function: Store the previous data point
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        self.lat_prev = bs.traf.lat
        self.lon_prev = bs.traf.lon
        self.hdg_prev = bs.traf.hdg
        self.alt_prev = bs.traf.alt
        self.gs_prev = bs.traf.gs

    def indices_update(self, flightid_trackdata):
        """
        Function: Get the indices for the traffic arrays and the trackdata
        Args:
            flightid_trackdata: flight ids with available data [array]
        Returns:
            itraf_update:       index track data update for the traffic arrays [array]
            itraf_prev:         index previous update for the traffic arrays [array]
            itrackdata:         index for the trackdata [array]

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Get flight ids that need an update and index for trackdata
        flightid_update, ifromdata, itrackdata = np.intersect1d(self.flightid_fromdata,
                                                                flightid_trackdata, return_indices=True)
        # Get index for traffic arrays
        itraf_update = self.get_indices(self.flightid, flightid_update)
        itraf_prev = self.get_indices(self.flightid, np.delete(self.flightid_fromdata, ifromdata))

        return itraf_update, itraf_prev, itrackdata

    @staticmethod
    def get_indices(arr, items):
        """
        Function: Get indices of items in array/list
        Args:
            arr:    array/list containing the items [array, list]
            items:  get indices of items [int, float, str, list, array]
        Returns:
            i:      inices [array]

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


def read_trackdata(folder, time0=0.):
    """
    Function: Read and process track data for traffic_fromdata
    Args:
        folder: name of the folder containing the files [str]
        time0:  start time in seconds [int, float]
    Returns: -

    Created by: Bob van Dillen
    Date: 25-11-2021
    """

    with cachefile.openfile(folder+'_'+str(time0)+'.p') as cacheload:
        try:
            bs.traf.traffromdata.trackdata = cacheload.load()
            commands = cacheload.load()
            commandstime = cacheload.load()

        except (pickle.PickleError, cachefile.CacheError):
            # Get path of the directory
            path = os.getcwd()+"\\scenario\\"+folder.lower()

            # Check if directory exists
            if os.path.isdir(path):
                # Reset the simulation
                bs.sim.reset()

                # Check if it contains the correct files
                for root, dirs, files in os.walk(path):
                    if len(files) < 6:
                        return False, f"TRACKDATA: The folder does not contain all the (correct) files"
                    if len(files) > 6:
                        return False, f"TRACKDATA: The folder does contain too many files"

                # Prepare the data
                bs.scr.echo('Preparing data from '+path+' ...')
                vemmisdata = vemmisread.VEMMISRead(path, time0)
                # Load flight data
                bs.scr.echo('Loading flight data ...')
                commands, commandstime = vemmisdata.get_flightdata()
                # Load track data
                bs.scr.echo('Loading track data ...')
                bs.traf.traffromdata.trackdata = vemmisdata.get_trackdata()

                # Save variables for fast reopen
                with cachefile.openfile(folder+'_'+str(time0)+'.p') as cachedump:
                    cachedump.dump(bs.traf.traffromdata.trackdata)
                    cachedump.dump(commands)
                    cachedump.dump(commandstime)
            else:
                return False, f"TRACKDATA: Folder does not exist"

    # Initialize simulation
    bs.scr.echo('Initialize simulation ...')
    # Create first aircraft
    stackbase.Stack.scencmd = commands
    stackbase.Stack.scentime = commandstime
    # Get the index and the SIM_TIME of the next data point
    bs.traf.traffromdata.i_next = 0
    bs.traf.traffromdata.t_next = bs.traf.traffromdata.trackdata[0][bs.traf.traffromdata.i_next]

    bs.scr.echo('Done')
