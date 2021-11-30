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
from bluesky.stack import simstack, stackbase


"""
Classes
"""


class TrafficFromData(Entity):
    """
    Traffic class definition    : Traffic data
    Methods:
        TrafficFromData()    : constructor
        create()             : create aircraft
        delete()             : delete an aircraft from traffic data
        deletall()           : delete all traffic
        update(sim)          : do a numerical integration step
        id2idx(name)         : return index in traffic database of given call sign
        engchange(i,engtype) : change engine type of an aircraft
        setnoise(A)          : Add turbulence
    Members: see create
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

    @stack.command
    def crefromdata(self, acid: str, acflightid: int):
        """
        Function: Create aircraft which are updated from data
        Args:
            acid:       callsign [str, list]
            acflightid: flight id [int, array]
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Get index
        idx = self.get_idx(acid)
        # Update flight data
        self.flightid[idx] = acflightid
        self.fromdata[idx] = True
        self.flightid_fromdata = np.append(self.flightid_fromdata, acflightid)
        # Update previous data point
        self.store_prev()

    @stack.command
    def delfromdata(self, acid: str):
        """
        Function: Delete aircraft which are updated from data
        Args:
            acid:   callsign [str, list]
        Returns: -

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        # Get index
        idx = self.get_idx(acid)
        # Get flight id
        flightid = self.flightid[idx]
        # Delete from flighid_fromdata
        delfromdata = np.nonzero(self.flightid_fromdata[:, None] == flightid)[0]
        self.flightid_fromdata = np.delete(self.flightid_fromdata, delfromdata)
        # Delete aircraft
        bs.traf.delete(idx)
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

            # Update variables
            self.store_prev()
            self.i_next = i[-1]+1
            self.t_next = self.trackdata[self.isimt][self.i_next]

        else:
            # Get indices when there is no new data point
            itraf_prev = self.indices_prev()

        # Other traffic
        bs.traf.lat[itraf_prev] = self.lat_prev[itraf_prev]
        bs.traf.lon[itraf_prev] = self.lon_prev[itraf_prev]
        bs.traf.hdg[itraf_prev] = self.hdg_prev[itraf_prev]
        bs.traf.alt[itraf_prev] = self.alt_prev[itraf_prev]
        bs.traf.gs[itraf_prev] = self.gs_prev[itraf_prev]

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
        itraf_update = np.nonzero(self.flightid[:, None] == flightid_update)[0]
        itraf_prev = np.nonzero(self.flightid[:, None] == np.delete(self.flightid_fromdata, ifromdata))[0]

        return itraf_update, itraf_prev, itrackdata

    def indices_prev(self):
        itraf = np.nonzero(self.flightid[:, None] == self.flightid_fromdata)[0]
        return itraf



    @staticmethod
    def get_idx(acid):
        """
        Function: Get the index for the traffic arrays
        Args:
            acid:   callsign [str, lst]
        Returns:
            idx:    index [array]

        Created by: Bob van Dillen
        Date: 30-11-2021
        """

        if isinstance(acid, str):
            idx = np.nonzero(np.array(bs.traf.id)[:, None] == np.array([acid]))[0]
        else:
            idx = np.nonzero(np.array(bs.traf.id)[:, None] == np.array(acid))[0]

        return idx


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

    with cachefile.openfile(folder+'_'+str(time0)+'.p') as cache:
        try:
            bs.traf.traffromdata.trackdata = cache.load()
            commands = cache.load()
            commandstime = cache.load()

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
                with cachefile.openfile(folder+'_'+str(time0)+'.p') as cache:
                    cache.dump(bs.traf.traffromdata.trackdata)
                    cache.dump(commands)
                    cache.dump(commandstime)
            else:
                return False, f"TRACKDATA: Folder does not exist"

    # Initialize simulation
    bs.scr.echo('Initialize simulation ...')
    # Create first aircraft
    print(commands[:5])
    stackbase.Stack.scencmd = commands
    stackbase.Stack.scentime = commandstime
    # Get the index and the SIM_TIME of the next data point
    bs.traf.traffromdata.i_next = 0
    bs.traf.traffromdata.t_next = bs.traf.traffromdata.trackdata[0][bs.traf.traffromdata.i_next]

    bs.scr.echo('Done')

