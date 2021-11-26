"""
This python file contains a class for managing flights which state is taken from data (database/file/... etc.).

Created by: Bob van Dillen
Date: 25-11-2021
"""

import numpy as np
import os
import bluesky as bs
try:
    from collections.abc import Collection
except ImportError:
    # In python <3.3 collections.abc doesn't exist
    from collections import Collection
from bluesky.tools import aero, vemmisread
from .autopilot import Autopilot
# from .asas import ConflictDetection
# from .performance.perfbase import PerfBase
# from .windsim import WindSim


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
    Created by  : Jacco M. Hoekstra
    """

    def __init__(self):
        # self.wind = WindSim()

        # Aircraft count
        self.ntraf_fromdata = 0
        # Parameters used for update
        self.trackdata = ()
        self.i_next = 0
        self.t_next = 0.0

        # Aircraft Info
        self.id = []
        self.type = []
        # Positions
        self.lat = np.array([])
        self.lon = np.array([])
        self.alt = np.array([])
        self.selalt = np.array([])
        self.hdg = np.array([])
        self.selhdg = np.array([])
        self.trk = np.array([])
        # Velocities
        self.tas = np.array([])
        self.cas = np.array([])
        self.selspd = np.array([])
        self.gs = np.array([])
        self.gsnorth = np.array([])
        self.gseast = np.array([])
        self.M = np.array([])
        self.vs = np.array([])
        # Flight Models
        # self.cd = ConflictDetection()
        self.ap = Autopilot()
        # self.perf = PerfBase()
        # Miscellaneous
        self.coslat = np.array([])
        self.eps = np.array([])

        # self. = bs.traf.groups.ingroup
        # self. = bs.traf.cd.inconf
        # self. = bs.traf.cd.tcpamax
        # self. = bs.traf.cd.rpz
        # self. = len(bs.traf.cd.confpairs_unique)
        # self. = len(bs.traf.cd.confpairs_all)
        # self. = len(bs.traf.cd.lospairs_unique)
        # self. = len(bs.traf.cd.lospairs_all)

    @staticmethod
    def reset():
        """
        Function: Clear all traffic data upon simulation reset
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 25-11-2021
        """

        bs.traf_fd = TrafficFromData()

    def cre(self, acid, actype=None, aclat=52., aclon=4., achdg=0, acalt=0, acspd=0):
        """
        Function: Create one or more aircraft
        Args:
            acid:   callsign [str, list]
            actype: aircraft type [str, lst]
            aclat:  latitude [int, float, list, array]
            aclon:  longitude [int, float, list, array]
            achdg:  heading [str, int, float, list, array]
            acalt:  altitude [in, float, list, array]
            acspd:  calibrated airspeed [int, float, list, array]
        Returns: -

        Created by: Bob van Dillen
        Date: 25-11-2021
        """

        # Determine number of aircraft to create from array length of acid
        n = 1 if isinstance(acid, str) else len(acid)

        self.ntraf_fromdata += n

        # Aircraft Info
        if isinstance(acid, list):
            self.id += acid
            self.type += actype
        else:
            self.id += [acid]
            self.type += [actype]
        # Positions
        self.lat = np.append(self.lat, aclat)
        self.lon = np.append(self.lon, aclon)
        self.alt = np.append(self.alt, acalt)
        self.hdg = np.append(self.hdg, achdg)
        self.trk = np.append(self.trk, achdg)
        # Velocities
        self.gs = np.append(self.gs, acspd)
        self.gsnorth = np.append(self.gsnorth, acspd*np.cos(np.radians(achdg)))
        self.gseast = np.append(self.gseast, acspd*np.sin(np.radians(achdg)))
        self.tas = np.append(self.tas, self.gs[-n:])
        self.cas = np.append(self.cas, aero.vtas2cas(self.tas[-n:], acalt))
        self.M = np.append(self.M, aero.vtas2mach(self.tas[-n:], acalt))
        # Traffic autopilot settings
        self.selspd = np.append(self.selspd, self.cas[-n:])
        self.selalt = np.append(self.selalt, acalt)
        # Miscellaneous
        self.coslat = np.append(self.coslat, np.cos(np.radians(aclat)))  # Cosine of latitude for flat-earth aproximations
        self.eps = np.append(self.eps, 0.01)

    def delete(self, acid):
        """
        Function: Delete an aircraft
        Args:
            idx:  callsign [int]
        Returns:
            True [bool]

        Created by: Bob van Dillen
        Date: 25-11-2021
        """
        # Get index
        idx = (np.array(self.id)[:, None] == np.array(acid)).argmax(axis=0)

        # Delete from arrays
        # Aircraft Info
        self.id = list(np.delete(np.array(self.id), idx))
        self.type = list(np.delete(np.array(self.type), idx))
        # Positions
        self.lat = np.delete(self.lat, idx)
        self.lon = np.delete(self.lon, idx)
        self.alt = np.delete(self.alt, idx)
        self.hdg = np.delete(self.hdg, idx)
        self.trk = np.delete(self.trk, idx)
        # Velocities
        self.gs = np.delete(self.gs, idx)
        self.gsnorth = np.delete(self.gsnorth, idx)
        self.gseast = np.delete(self.gseast, idx)
        self.tas = np.delete(self.tas, idx)
        self.cas = np.delete(self.cas, idx)
        self.M = np.delete(self.M, idx)
        # Traffic autopilot settings
        self.selspd = np.delete(self.selspd, idx)
        self.selalt = np.delete(self.selalt, idx)
        # Miscellaneous
        self.coslat = np.delete(np.coslat, idx)  # Cosine of latitude for flat-earth aproximations
        self.eps = np.delete(np.eps, idx)

        # Update aircraft count
        self.ntraf_fromdata = len(self.id)

        return True

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
        if self.ntraf_fromdata == 0:
            return

        # Check if we have reached the time stamp of next data point
        if self.t_next <= bs.sim.simt:
            i = self.trackdata[1][self.i_next]

            # Check if aircraft have to be created
            create = self.trackdata[9][i[0]: i[-1]]
            if True in create:
                # Get flight info
                acid = list(np.array(self.trackdata[2][i[0]: i[-1] + 1])[create])
                actype = list(np.array(self.trackdata[3][i[0]: i[-1] + 1])[create])
                lat = self.trackdata[4][i[0]: i[-1] + 1][create]
                lon = self.trackdata[5][i[0]: i[-1] + 1][create]
                hdg = self.trackdata[6][i[0]: i[-1] + 1][create]
                alt = self.trackdata[7][i[0]: i[-1] + 1][create]
                spd = self.trackdata[8][i[0]: i[-1] + 1][create]
                # Create the aircraft
                self.cre(acid, actype, lat, lon, hdg, alt, spd)

            # Get indices for traffic arrays
            idx = np.nonzero(np.array(self.trackdata[2][i[0]: i[-1] + 1])[:, None] == self.id)[1]

            # Update the traffic arrays
            self.lat[idx] = self.trackdata[4][i[0]: i[-1]+1]
            self.lon[idx] = self.trackdata[5][i[0]: i[-1]+1]
            self.hdg[idx] = self.trackdata[6][i[0]: i[-1]+1]
            self.alt[idx] = self.trackdata[7][i[0]: i[-1]+1]
            self.gs[idx] = self.trackdata[8][i[0]: i[-1]+1]

            # Check if aircraft have to be deleted
            delete = self.trackdata[10][i[0]: i[-1]]
            if True in delete:
                # Get id for traffic arrays
                acid_del = np.array(self.trackdata[2][i[0]: i[-1]+1])[delete]
                # Delete the aircraft
                self.delete(acid_del)

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

        # Load track data
        bs.scr.echo('Loading track data ...')
        bs.traf_fd.trackdata = vemmisdata.get_trackdata()

        # Initialize simulation
        bs.scr.echo('Initialize simulation ...')
        # Set date and time
        simday, simmonth, simyear, simtime = vemmisdata.get_datetime()
        bs.sim.setutc(simday, simmonth, simyear, simtime)
        # Create first aircraft
        i = bs.traf_fd.trackdata[1][0]
        acid = bs.traf_fd.trackdata[2][i[0]: i[-1]+1]
        actype = bs.traf_fd.trackdata[3][i[0]: i[-1]+1]
        lat = bs.traf_fd.trackdata[4][i[0]: i[-1]+1]
        lon = bs.traf_fd.trackdata[5][i[0]: i[-1]+1]
        hdg = bs.traf_fd.trackdata[6][i[0]: i[-1]+1]
        alt = bs.traf_fd.trackdata[7][i[0]: i[-1]+1]
        spd = bs.traf_fd.trackdata[8][i[0]: i[-1]+1]
        bs.traf_fd.cre(acid, actype, lat, lon, hdg, alt, spd)
        # Get the index and the SIM_TIME of the next data point
        bs.traf_fd.i_next = i[-1]+1
        bs.traf_fd.t_next = bs.traf_fd.trackdata[0][bs.traf_fd.i_next]

        bs.scr.echo('Done')
    else:
        return False, f"TRACKDATA: Folder does not exist"

