"""
This python file contains a class for managing replay flights, which state is taken from data (database/file/... etc.).

Created by: Bob van Dillen
Date: 25-11-2021
"""


import copy
import numpy as np
import os
import bluesky as bs
from bluesky import stack
from bluesky.core import Entity
from bluesky.tools import aero, misc, vemmisread
from bluesky.stack import stackbase


"""
Classes
"""


class TrafficReplay(Entity):
    """
    Class definition: Replay traffic based on data (VEMMIS)
    Methods:
        clear():                Reset variables
        crereplay():            Create aircraft which are updated from data
        delreplay():            Remove aircraft from replay callsigns list
        update():               Perform an update (step)
        update_fromtrackdata(): Update aircraft data from trackdata
        update_fromprevious():  Update aircraft data from previous data point
        update_speed():         Calculate the different speeds
        uco_replay():           Stop taking the aircraft state from data (simulate the aircraft)
        store_prev():           Store the previous data point
        indices_update():       Get the indices for the traffic arrays and the trackdata

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
            self.replay = np.array([], dtype=np.bool)  # Take aircraft state from data/file

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

    def create(self, n=1):
        """
        Function: Create an aircraft
        Args:
            n:  number of aircraft
        Returns: -

        Created by: Bob van Dillen
        Date: 24-12-2021
        """

        super().create(n)

        self.store_prev()

    def delete(self, idx):
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

        super().delete(idx)

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
            im = self.i_next+ac_count  # Last index + 1 for slicing (e.g. i=1; ac_count=2, therefore [1:3])

            # Get indices
            itraf_up, itrackdata, ireplay = self.indices_update(self.trackdata[self.iid][i0: im])
            itraf_prev = misc.get_indices(bs.traf.id, np.delete(self.replayid, ireplay))
            iprev = misc.get_indices(self.id_prev, np.delete(self.replayid, ireplay))

            # Update traffic data
            self.update_fromtrackdata(i0, im, itraf_up, itrackdata)
            self.update_fromprev(itraf_prev, iprev)

            # Update variables
            self.store_prev()
            self.i_next = im
            self.t_next = self.trackdata[self.isimt][self.i_next]

        else:
            # Get indices when there is no new data point
            itraf_prev = misc.get_indices(bs.traf.id, self.replayid)
            iprev = misc.get_indices(self.id_prev, self.replayid)

            # Update traffic data
            self.update_fromprev(itraf_prev, iprev)

        # Update other speeds (wind)
        self.update_speed()

    def update_fromtrackdata(self, i0, im, itraf_update, itrackdata):
        """
        Function: Update aircraft data from trackdata
        Args:
            i0:             first index (for slicing) [int]
            im:             last index + 1 (for slicing) [int]
            itraf_update:   indices for traffic arrays [list, array]
            itrackdata:     indices for trackdata [list, array]
        Returns: -

        Created by: Bob van Dillen
        Date: 17-12-2021
        """

        bs.traf.lat[itraf_update] = self.trackdata[self.ilat][i0: im][itrackdata]
        bs.traf.lon[itraf_update] = self.trackdata[self.ilon][i0: im][itrackdata]
        bs.traf.hdg[itraf_update] = self.trackdata[self.ihdg][i0: im][itrackdata]
        bs.traf.alt[itraf_update] = self.trackdata[self.ialt][i0: im][itrackdata]
        bs.traf.gs[itraf_update] = self.trackdata[self.ispd][i0: im][itrackdata]

    def update_fromprev(self, itraf_previous, i_previous):
        """
        Function: Update aircraft data from previous data point
        Args:
            itraf_previous: indices for traffic arrays [list, array]
            i_previous:     indices for previous traffic arrays [list, array]
        Returns: -

        Created by: Bob van Dillen
        Date: 17-12-2021
        """

        bs.traf.lat[itraf_previous] = self.lat_prev[i_previous]
        bs.traf.lon[itraf_previous] = self.lon_prev[i_previous]
        bs.traf.hdg[itraf_previous] = self.hdg_prev[i_previous]
        bs.traf.alt[itraf_previous] = self.alt_prev[i_previous]
        bs.traf.gs[itraf_previous] = self.gs_prev[i_previous]

    def update_speed(self):
        """
        Function: Calculate the different speeds
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 1-12-2021
        """

        # Get indices for traffic arrays
        itraf = misc.get_indices(bs.traf.id, self.replayid)

        # No wind
        if bs.traf.wind.winddim == 0:
            # Decompose ground speed
            bs.traf.gsnorth[itraf] = bs.traf.gs[itraf]*np.cos(np.radians(bs.traf.hdg[itraf]))
            bs.traf.gseast[itraf] = bs.traf.gs[itraf]*np.sin(np.radians(bs.traf.hdg[itraf]))

            # Determine true airspeed
            bs.traf.tas[itraf] = bs.traf.gs[itraf]

            # Determine calibrated airspeed
            bs.traf.cas[itraf] = aero.vtas2cas(bs.traf.tas[itraf], bs.traf.alt[itraf])

            # Determine mach
            bs.traf.M[itraf] = aero.vtas2mach(bs.traf.tas[itraf], bs.traf.alt[itraf])

            # Determine track
            bs.traf.trk[itraf] = bs.traf.hdg[itraf]

        # Wind
        else:
            # Decompose ground speed
            bs.traf.gsnorth[itraf] = bs.traf.gs[itraf]*np.cos(np.radians(bs.traf.hdg[itraf]))
            bs.traf.gseast[itraf] = bs.traf.gs[itraf]*np.sin(np.radians(bs.traf.hdg[itraf]))

            # Wind when airborn
            applywind = bs.traf.alt[itraf] > 50.*aero.ft

            # Get wind data
            bs.traf.windnorth[itraf], bs.traf.windeast[itraf] = bs.traf.wind.getdata(bs.traf.lat[itraf],
                                                                                     bs.traf.lon[itraf],
                                                                                     bs.traf.alt[itraf])

            # Determine true airspeed
            tasnorth = bs.traf.gsnorth[itraf] - bs.traf.windnorth[itraf]*applywind
            taseast = bs.traf.gseast[itraf] - bs.traf.windeast[itraf]*applywind
            bs.traf.tas[itraf] = np.sqrt(tasnorth*tasnorth + taseast*taseast)

            # Determine calibrated airspeed
            bs.traf.cas[itraf] = aero.vtas2cas(bs.traf.tas[itraf], bs.traf.alt[itraf])

            # Determine mach
            bs.traf.M[itraf] = aero.vtas2mach(bs.traf.tas[itraf], bs.traf.alt[itraf])

            # Determine track
            bs.traf.trk[itraf] = np.logical_not(applywind)*bs.traf.hdg[itraf] +\
                                 applywind*np.degrees(np.arctan2(bs.traf.gseast[itraf], bs.traf.gsnorth[itraf])) % 360.

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
        itraf_update = misc.get_indices(bs.traf.id, id_update)

        return itraf_update, itrackdata, ireplay

    @stack.command(name='ADDREPLAY')
    def setreplay(self, idx: 'acid'):
        """
        Function: Add aircraft to replay mode
        Args:
            idx:    index for traffic arrays [int]
        Returns: -

        Created by: Bob van Dillen
        Date: 24-12-2021
        """

        acid = np.array(bs.traf.id)[idx]
        self.replayid.append(acid)
        self.replay[idx] = True


"""
Static functions
"""


def read_replay(datatype, folder, time0=None):
    """
    Function: Read and process track data for trafficreplay
    Args:
        datatype:   type of flight data
        folder:     name of the folder containing the files [str]
        time0:      start time in seconds [int, float]
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
