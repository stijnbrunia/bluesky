"""
This python file contains a class for managing flights which state is taken from data (database/file/... etc.).

Created by: Bob van Dillen
Date: 25-11-2021
"""

import numpy as np
import os
import bluesky as bs
from bluesky.tools import aero, vemmisread
from bluesky.stack import simstack, stackbase

"""
Classes
"""


class TrafficFromData:
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

    def __init__(self):
        # Flight and track data
        self.trackdata = ()
        # Parameters used for update
        self.i_next = 0
        self.t_next = 0.0

        # Aircraft Info
        self.flightid = np.array([])
        # Positions
        self.lat = np.array([])
        self.lon = np.array([])
        self.hdg = np.array([])
        self.selhdg = np.array([])
        self.trk = np.array([])
        self.alt = np.array([])
        self.selalt = np.array([])
        # Velocities
        self.tas = np.array([])
        self.cas = np.array([])
        self.selspd = np.array([])
        self.gs = np.array([])
        self.gsnorth = np.array([])
        self.gseast = np.array([])
        self.M = np.array([])
        self.vs = np.array([])

    def reset(self):
        """
        Function: Clear all traffic data upon simulation reset
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 25-11-2021
        """

        self.__init__()

    def update(self):
        """
        Function: Perform an update (step)
        Args: -
        Returns: -

        Remark: Slicing is used for accessing the track data ([i[0]: i[-1]])

        Created by: Bob van Dillen
        Date: 25-11-2021
        """

        # Check if there are aircraft
        if len(self.lat) == 0:
            return

        # Check if we have reached the time stamp of next data point
        if self.t_next <= bs.sim.simt:
            i = self.trackdata[1][self.i_next]

            # Get indices for traffic arrays
            idx = np.nonzero(np.array(self.trackdata[2][i[0]: i[-1] + 1])[:, None] == self.flightid)[1]

            # Update the traffic arrays
            self.lat[idx] = self.trackdata[4][i[0]: i[-1]+1]
            self.lon[idx] = self.trackdata[5][i[0]: i[-1]+1]
            self.hdg[idx] = self.trackdata[6][i[0]: i[-1]+1]
            self.alt[idx] = self.trackdata[7][i[0]: i[-1]+1]
            self.gs[idx] = self.trackdata[8][i[0]: i[-1]+1]

            # Get the index and the SIM_TIME of the next data point
            self.i_next = i[-1]+1
            self.t_next = self.trackdata[0][self.i_next]


"""
Static functions
"""


def read_trackdata(folder, time0):
    """
    Function: Read and process track data for traffic_fromdata
    Args:
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
        # Check if it contains the correct files
        for root, dirs, files in os.walk(path):
            if len(files) < 6:
                return False, f"TRACKDATA: The folder does not contain all the (correct) files"
            if len(files) > 6:
                return False, f"TRACKDATA: The folder does contain too many files"

        # Reset the simulation
        bs.sim.reset()

        # Prepare the data
        bs.scr.echo('Preparing data from '+path+' ...')
        vemmisdata = vemmisread.VEMMISRead(path, time0)

        # Load flight data
        bs.scr.echo('Loading flight data ...')
        commands, commandstime = vemmisdata.get_flightdata()

        # Load track data
        bs.scr.echo('Loading track data ...')
        bs.traf.traffromdata.trackdata = vemmisdata.get_trackdata()

        # Initialize simulation
        bs.scr.echo('Initialize simulation ...')
        # Set date and time
        simday, simmonth, simyear, simtime = vemmisdata.get_datetime()
        bs.sim.setutc(simday, simmonth, simyear, simtime)
        # Create first aircraft
        stackbase.Stack.scencmd = commands
        stackbase.Stack.scentime = commandstime
        # Get the index and the SIM_TIME of the next data point
        i = bs.traf.traffromdata.trackdata[1][0]
        bs.traf.traffromdata.i_next = i[-1]+1
        bs.traf.traffromdata.t_next = bs.traf.traffromdata.trackdata[0][bs.traf.traffromdata.i_next]

        bs.scr.echo('Done')
    else:
        return False, f"TRACKDATA: Folder does not exist"

