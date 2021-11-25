# """
# This python file contains a class for managing flights which state is taken from data (database/file/... etc.).
#
# Created by: Bob van Dillen
# Date: 25-11-2021
# """
#
# import numpy as np
# import os
# import bluesky as bs
# try:
#     from collections.abc import Collection
# except ImportError:
#     # In python <3.3 collections.abc doesn't exist
#     from collections import Collection
# from bluesky.core import Entity
# from bluesky.tools import aero, vemmisread
# from .autopilot import Autopilot
#
#
# """
# Classes
# """
#
#
# class TrafficFromData(Entity):
#     """
#     Traffic class definition    : Traffic data
#     Methods:
#         TrafficFromData()    : constructor
#         create()             : create aircraft
#         delete()             : delete an aircraft from traffic data
#         deletall()           : delete all traffic
#         update(sim)          : do a numerical integration step
#         id2idx(name)         : return index in traffic database of given call sign
#         engchange(i,engtype) : change engine type of an aircraft
#         setnoise(A)          : Add turbulence
#     Members: see create
#     Created by  : Jacco M. Hoekstra
#     """
#     def __init__(self):
#         super().__init__()
#
#         self.ntraf_fromdata = 0
#
#         self.trackdata = ()
#         self.i_next = 0
#         self.t_next = 0.0
#
#         with self.settrafarrays():
#             self.id = []
#             self.type = []
#             self.lat = np.array([])
#             self.lon = np.array([])
#             self.alt = np.array([])
#             self.selalt = np.array([])
#             self.hdg = np.array([])
#             self.selhdg = np.array([])
#             self.trk = np.array([])
#             self.tas = np.array([])
#             self.cas = np.array([])
#             self.gs = np.array([])
#             self.M = np.array([])
#             self.vs = np.array([])
#
#             self.ap = Autopilot()
#
#             # self. = bs.traf.groups.ingroup
#             # self. = bs.traf.cd.inconf
#             # self. = bs.traf.cd.tcpamax
#             # self. = bs.traf.cd.rpz
#             # self. = len(bs.traf.cd.confpairs_unique)
#             # self. = len(bs.traf.cd.confpairs_all)
#             # self. = len(bs.traf.cd.lospairs_unique)
#             # self. = len(bs.traf.cd.lospairs_all)
#
#     def reset(self):
#         """
#         Function: Clear all traffic data upon simulation reset
#         Args: -
#         Returns: -
#
#         Created by: Bob van Dillen
#         Date: 25-11-2021
#         """
#         # Some child reset functions depend on a correct value of self.ntraf
#         self.ntraf_fromdata = 0
#         # This ensures that the traffic arrays (which size is dynamic)
#         # are all reset as well, so all lat,lon,sdp etc but also objects adsb
#         super().reset()
#
#     def cre(self, acid, actype=None, aclat=52., aclon=4., achdg=0, acalt=0, acspd=0):
#         """
#         Function: Create one or more aircraft
#         Args:
#             acid:   callsign [str, list]
#             actype: aircraft type [str, lst]
#             aclat:  latitude [int, float, list, array]
#             aclon:  longitude [int, float, list, array]
#             achdg:  heading [str, int, float, list, array]
#             acalt:  altitude [in, float, list, array]
#             acspd:  calibrated airspeed [int, float, list, array]
#         Returns: -
#
#         Created by: Bob van Dillen
#         Date: 25-11-2021
#         """
#
#         # Determine number of aircraft to create from array length of acid
#         n = 1 if isinstance(acid, str) else len(acid)
#
#         # Adjust the size of all traffic arrays
#         super().create(n)
#
#         self.ntraf_fromdata += n
#
#         # Aircraft Info
#         self.id[-n:] = acid
#         self.type[-n:] = actype
#         # Positions
#         self.lat[-n:] = aclat
#         self.lon[-n:] = aclon
#         self.alt[-n:] = acalt
#         self.hdg[-n:] = achdg
#         self.trk[-n:] = achdg
#         # Velocities
#         self.tas[-n:], self.cas[-n:], self.M[-n:] = aero.vcasormach(acspd, acalt)
#         self.gs[-n:] = self.tas[-n:]
#         # Traffic autopilot settings
#         # self.selspd[-n:] = self.cas[-n:]
#         # self.aptas[-n:]  = self.tas[-n:]
#         # self.selalt[-n:] = self.alt[-n:]
#         # Miscallaneous
#         # self.coslat[-n:] = np.cos(np.radians(aclat))  # Cosine of latitude for flat-earth aproximations
#         # self.eps[-n:] = 0.01
#
#         # Finally call create for child TrafficArrays. This only needs to be done
#         # manually in Traffic.
#         self.create_children(n)
#
#     def delete(self, idx):
#         """
#         Function: Delete an aircraft
#         Args:
#             idx:  callsign [int]
#         Returns:
#             True [bool]
#
#         Created by: Bob van Dillen
#         Date: 25-11-2021
#         """
#         # If this is a multiple delete, sort first for list delete
#         # (which will use list in reverse order to avoid index confusion)
#         if isinstance(idx, Collection):
#             idx = np.sort(idx)
#
#         # Call the actual delete function
#         super().delete(idx)
#
#         # Update number of aircraft
#         self.ntraf_fromdata = len(self.lat)
#
#         return True
#
#     def update(self):
#         """
#         Function: Perform an update (step)
#         Args: -
#         Returns: -
#
#         Remark: Slicing is used for accessing the track data (i[0]: i[-1])
#
#         Created by: Bob van Dillen
#         Date: 25-11-2021
#         """
#
#         # Check if there are aircraft
#         if self.ntraf_fromdata == 0:
#             return
#
#         # Check if we have reached the time stamp of next data point
#         if self.t_next <= bs.sim.simt:
#             i = self.trackdata[1][self.i_next]
#
#             # Check if aircraft have to be created
#             create = self.trackdata[10][i[0]: i[-1]]
#             if True in create:
#                 # Get flight info
#                 acid = list(np.array(self.trackdata[2][i[0]: i[-1] + 1])[create])
#                 actype = list(np.array(self.trackdata[3][i[0]: i[-1] + 1])[create])
#                 lat = self.trackdata[4][i[0]: i[-1] + 1][create]
#                 lon = self.trackdata[5][i[0]: i[-1] + 1][create]
#                 hdg = self.trackdata[6][i[0]: i[-1] + 1][create]
#                 alt = self.trackdata[7][i[0]: i[-1] + 1][create]
#                 spd = self.trackdata[8][i[0]: i[-1] + 1][create]
#                 # Create the aircraft
#                 self.cre(acid, actype, lat, lon, hdg, alt, spd)
#
#             # Get indices for traffic arrays
#             idx = np.nonzero(np.array(self.trackdata[2][i[0]: i[-1] + 1])[:, None] == self.id)[1]
#
#             # Update the traffic arrays
#             self.lat[idx] = self.trackdata[4][i[0]: i[-1]+1]
#             self.lon[idx] = self.trackdata[5][i[0]: i[-1]+1]
#             self.hdg[idx] = self.trackdata[6][i[0]: i[-1]+1]
#             self.alt[idx] = self.trackdata[7][i[0]: i[-1]+1]
#             self.gs[idx] = self.trackdata[8][i[0]: i[-1]+1]
#
#             # Get the index and the SIM_TIME of the next data point
#             self.i_next = i[-1]+1
#             self.t_next = self.trackdata[0][self.i_next]
#
#
#
#
#
# """
# Static functions
# """
#
#
# def read_trackdata(folder, time0):
#     """
#     Function: Read and process track data for traffic_fromdata
#     Args:
#         folder: name of the folder containing the files [str]
#         time0:  start time in seconds [int, float]
#     Returns: -
#
#     Created by: Bob van Dillen
#     Date: 25-11-2021
#     """
#
#     # Get path of the directory
#     path = os.getcwd()+"\\scenario\\"+folder.lower()
#
#     # Check if directory exists
#     if os.path.isdir(path):
#         # Check if it contains the correct files
#         for root, dirs, files in os.walk(path):
#             if len(files) < 6:
#                 return False, f"TRACKDATA: The folder does not contain all the (correct) files"
#             if len(files) > 6:
#                 return False, f"TRACKDATA: The folder does contain too many files"
#
#         # Reset the simulation
#         bs.sim.reset()
#
#         # Prepare the data
#         bs.scr.echo('Preparing data from '+path+' ...')
#         vemmisdata = vemmisread.VEMMISRead(path, time0)
#
#         # Load track data
#         bs.scr.echo('Loading track data ...')
#         bs.traf.trackdata = vemmisdata.get_trackdata()
#
#         # Initialize simulation
#         bs.scr.echo('Initialize simulation ...')
#         # Create first aircraft
#         i = bs.traf.trackdata[1][0]
#         acid = bs.traf.trackdata[2][i[0]: i[-1]+1]
#         actype = bs.traf.trackdata[3][i[0]: i[-1]+1]
#         lat = bs.traf.trackdata[4][i[0]: i[-1]+1]
#         lon = bs.traf.trackdata[5][i[0]: i[-1]+1]
#         hdg = bs.traf.trackdata[6][i[0]: i[-1]+1]
#         alt = bs.traf.trackdata[7][i[0]: i[-1]+1]
#         spd = bs.traf.trackdata[8][i[0]: i[-1]+1]
#         bs.traf.cre(acid, actype, lat, lon, hdg, alt, spd, True)
#         # Initialize previous data point
#         bs.traf.trackdata_prev = (bs.traf.trackdata[2][i[0]: i[-1]+1], bs.traf.trackdata[4][i[0]: i[-1]+1],
#                                   bs.traf.trackdata[5][i[0]: i[-1]+1], bs.traf.trackdata[6][i[0]: i[-1]+1],
#                                   bs.traf.trackdata[7][i[0]: i[-1]+1], bs.traf.trackdata[8][i[0]: i[-1]+1])
#         bs.traf.i_next = i[-1]+1
#         bs.traf.t_next = bs.traf.trackdata[0][bs.traf.i_next]
#
#         bs.scr.echo('Done')
#     else:
#         return False, f"TRACKDATA: Folder does not exist"
