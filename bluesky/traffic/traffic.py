""" BlueSky traffic implementation."""
from __future__ import print_function

import pandas as pd

try:
    from collections.abc import Collection
except ImportError:
    # In python <3.3 collections.abc doesn't exist
    from collections import Collection
from math import *
from random import randint
import numpy as np

import bluesky as bs
from bluesky.core import Entity, timed_function
from bluesky.stack import refdata
from bluesky.stack.recorder import savecmd
from bluesky.tools import geo, Functions, Ground_radar_read
from bluesky.tools.misc import latlon2txt, angleFromCoordinate, get_indices
from bluesky.tools.aero import cas2tas, casormach2tas, fpm, kts, ft, g0, Rearth, nm, tas2cas,\
                         vatmos,  vtas2cas, vtas2mach, vcasormach

from bluesky.traffic.asas import ConflictDetection, ConflictResolution
from .windsim import WindSim
from .conditional import Condition
from .trails import Trails
from .adsbmodel import ADSB
from .aporasas import APorASAS
from .autopilot import Autopilot
from .activewpdata import ActiveWaypoint
from .lvnlvariables import LVNLVariables
from .turbulence import Turbulence
from .trafficdatafeed import TrafficDataFeed
from .trafficgroups import TrafficGroups
from .performance.perfbase import PerfBase
from .historysymbols import HistorySymbols

# Register settings defaults
bs.settings.set_variable_defaults(performance_model='openap', asas_dt=1.0)

# if bs.settings.performance_model == 'bada':
#     try:
#         print('Using BADA Performance model')
#         from .performance.bada.perfbada import PerfBADA as Perf
#     except Exception as err:# ImportError as err:
#         print(err)
#         print('Falling back to Open Aircraft Performance (OpenAP) model')
#         bs.settings.performance_model = "openap"
#         from .performance.openap import OpenAP as Perf
# elif bs.settings.performance_model == 'openap':
#     print('Using Open Aircraft Performance (OpenAP) model')
#     from .performance.openap import OpenAP as Perf
# else:
#     print('Using BlueSky legacy performance model')
#     from .performance.legacy.perfbs import PerfBS as Perf


class Traffic(Entity):
    """
    Traffic class definition    : Traffic data
    Methods:
        Traffic()            :  constructor
        reset()              :  Reset traffic database w.r.t a/c data
        create(acid,actype,aclat,aclon,achdg,acalt,acspd) : create aircraft
        delete(acid)         : delete an aircraft from traffic data
        deletall()           : delete all traffic
        update(sim)          : do a numerical integration step
        id2idx(name)         : return index in traffic database of given call sign
        engchange(i,engtype) : change engine type of an aircraft
        setnoise(A)          : Add turbulence
    Members: see create
    Created by  : Jacco M. Hoekstra
    """

    def __init__(self):
        super().__init__()

        # Traffic is the toplevel trafficarrays object
        self.setroot(self)

        self.ntraf = 0

        self.cond = Condition()  # Conditional commands list
        self.wind = WindSim()
        self.turbulence = Turbulence()
        self.translvl = 5000.*ft # [m] Default transition level

        self.HighRes = False
        self.Wind_DB = ""

        self.df_1 = ""
        self.df_2 = ""
        self.HR_Loaded = False
        self.activate_HR = False

        self.id_select = ''  # aircraft that previously received a command

        self.trafdatafeed = TrafficDataFeed()

        #Ground Radar
        self.Ground_Radar_mode = False
        self.GR_directory = Ground_radar_read.directory
        self.GR_file = ""

        self.GR_date = [1,1,2018, '07:00:00']
        self.current_line = 0
        self.n_lines = 10
        self.start_time = 0

        self.parktime = Ground_radar_read.park_time
        self.active_ac = pd.DataFrame(columns=["AC_id", "time", "lat", "lon", "V", "heading", "altitude", "park_count"])

        self.record_gates = True
        self.where_created = pd.DataFrame(columns=["AC_id", "time", "lat", "lon", "bay"])
        self.gates_file = 'C:\\Users\\stijn\\Documents\\Administratie\\Aerospace Engineering\\Master\\Master Thesis\\Code\\Data\\Astra_Gates\\1-1-2018.xlsx'

        with self.settrafarrays():
            # Aircraft Info
            self.id      = []  # identifier (string)
            self.type    = []  # aircaft type (string)

            # Positions
            self.lat     = np.array([])  # latitude [deg]
            self.lon     = np.array([])  # longitude [deg]
            self.distflown = np.array([])  # distance travelled [m]
            self.alt     = np.array([])  # altitude [m]
            self.hdg     = np.array([])  # traffic heading [deg]
            self.trk     = np.array([])  # track angle [deg]

            # Timestamps
            self.prev_timestamp = 0
            self.next_timestamp = 0

            # Velocities
            self.tas     = np.array([])  # true airspeed [m/s]
            self.gs      = np.array([])  # ground speed [m/s]
            self.gsnorth = np.array([])  # ground speed [m/s]
            self.gseast  = np.array([])  # ground speed [m/s]
            self.cas     = np.array([])  # calibrated airspeed [m/s]
            self.M       = np.array([])  # mach number
            self.vs      = np.array([])  # vertical speed [m/s]

            # Acceleration
            self.ax = np.array([])  # [m/s2] current longitudinal acceleration

            # Atmosphere
            self.p       = np.array([])  # air pressure [N/m2]
            self.rho     = np.array([])  # air density [kg/m3]
            self.Temp    = np.array([])  # air temperature [K]
            self.dtemp   = np.array([])  # delta t for non-ISA conditions
            self.topwind = pd.DataFrame  # dataframe for the wind on

            # Wind speeds
            self.windnorth = np.array([])  # wind speed north component a/c pos [m/s]
            self.windeast  = np.array([])  # wind speed east component a/c pos [m/s]

            # Traffic autopilot settings
            self.selspd = np.array([])  # selected spd(CAS or Mach) [m/s or -]
            self.aptas  = np.array([])  # just for initializing
            self.selalt = np.array([])  # selected alt[m]
            self.selvs  = np.array([])  # selected vertical speed [m/s]
            self.selhdg = np.array([])  # selected heading [deg]

            # Whether to perform LNAV and VNAV
            self.swlnav    = np.array([], dtype=np.bool)
            self.swvnav    = np.array([], dtype=np.bool)
            self.swvnavspd = np.array([], dtype=np.bool)
            self.manual = np.array([], dtype=np.bool)

            # Flight Models
            self.cd       = ConflictDetection()
            self.cr       = ConflictResolution()
            self.ap       = Autopilot()
            self.aporasas = APorASAS()
            self.adsb     = ADSB()
            self.trails   = Trails()
            self.actwp    = ActiveWaypoint()
            self.perf     = PerfBase()
            self.histsymb = HistorySymbols()

            # Group Logic
            self.groups = TrafficGroups()

            # Traffic autopilot data
            self.swhdgsel = np.array([], dtype=np.bool)  # determines whether aircraft is turning

            # Traffic autothrottle settings
            self.swats    = np.array([], dtype=np.bool)  # Switch indicating whether autothrottle system is on/off
            self.thr      = np.array([])        # Thottle seeting (0.0-1.0), negative = non-valid/auto

            # Display information on label
            self.label       = []  # Text and bitmap of traffic label

            # Miscallaneous
            self.coslat = np.array([])  # Cosine of latitude for computations
            self.eps    = np.array([])  # Small nonzero numbers
            self.work   = np.array([])  # Work done throughout the flight

            # LVNL Variables
            self.lvnlvars = LVNLVariables()  # Variables used by LVNL

        # Default bank angles per flight phase
        self.bphase = np.deg2rad(np.array([15, 35, 35, 35, 15, 45]))

    def reset(self):
        ''' Clear all traffic data upon simulation reset. '''
        # Some child reset functions depend on a correct value of self.ntraf
        self.ntraf = 0
        # This ensures that the traffic arrays (which size is dynamic)
        # are all reset as well, so all lat,lon,sdp etc but also objects adsb
        super().reset()

        # reset performance model
        self.perf.reset()

        # Reset models
        self.wind.clear()

        # Build new modules for turbulence
        self.turbulence.reset()

        # Noise (turbulence, ADBS-transmission noise, ADSB-truncated effect)
        self.setnoise(False)

        # Reset transition level to default value
        self.translvl = 5000.*ft

    def mcre(self, n, actype="B744", acalt=None, acspd=None, dest=None):
        """ Create one or more random aircraft in a specified area """
        area = bs.scr.getviewbounds()

        # Generate random callsigns
        idtmp = chr(randint(65, 90)) + chr(randint(65, 90)) + '{:>05}'
        acid = [idtmp.format(i) for i in range(n)]

        # Generate random positions
        aclat = np.random.rand(n) * (area[1] - area[0]) + area[0]
        aclon = np.random.rand(n) * (area[3] - area[2]) + area[2]
        achdg = np.random.randint(1, 360, n)
        acalt = acalt or np.random.randint(2000, 39000, n) * ft
        acspd = acspd or np.random.randint(250, 450, n) * kts

        self.cre(acid, actype, aclat, aclon, achdg, acalt, acspd)

    def cre(self, acid, actype="B744", aclat=52., aclon=4., achdg=None, acalt=0, acspd=0):
        """ Create one or more aircraft. """
        # Determine number of aircraft to create from array length of acid
        n = 1 if isinstance(acid, str) else len(acid)

        if isinstance(acid, str):
            # Check if not already exist
            if self.id.count(acid.upper()) > 0:
                return False, acid + " already exists."  # already exists do nothing
            acid = n * [acid]

        # Adjust the size of all traffic arrays
        super().create(n)
        self.ntraf += n

        if isinstance(actype, str):
            actype = n * [actype]

        if isinstance(aclat, (float, int)):
            aclat = np.array(n * [aclat])

        if isinstance(aclon, (float, int)):
            aclon = np.array(n * [aclon])

        # Limit longitude to [-180.0, 180.0]
        aclon[aclon > 180.0] -= 360.0
        aclon[aclon < -180.0] += 360.0

        achdg = (refdata.hdg or 0.0) if achdg is None else achdg

        # Aircraft Info
        self.id[-n:]   = acid
        self.type[-n:] = actype

        # Positions
        self.lat[-n:]  = aclat
        self.lon[-n:]  = aclon
        self.alt[-n:]  = acalt

        if isinstance(achdg, str):
            if achdg.upper() in bs.navdb.wpid:
                index = bs.navdb.wpid.index(achdg.upper())
                templat_hdg = bs.navdb.wplat[index]
                templon_hdg = bs.navdb.wplon[index]
                templat_ac = aclat
                templon_ac = aclon

                achdg = angleFromCoordinate(templat_ac, templon_ac, templat_hdg, templon_hdg)

            else:
                achdg = float(achdg)
        elif isinstance(achdg, (int, float)):
            achdg = np.array(n * [achdg])

        self.hdg[-n:]  = achdg
        self.trk[-n:]  = achdg

        # Velocities
        self.tas[-n:], self.cas[-n:], self.M[-n:] = vcasormach(acspd, acalt)
        self.gs[-n:]      = self.tas[-n:]
        hdgrad = np.radians(achdg)
        self.gsnorth[-n:] = self.tas[-n:] * np.cos(hdgrad)
        self.gseast[-n:] = self.tas[-n:] * np.sin(hdgrad)

        # Atmosphere
        self.p[-n:], self.rho[-n:], self.Temp[-n:] = vatmos(acalt)

        # Wind
        if self.wind.winddim > 0:
            if self.HighRes:
                self.windnorth[-n:] = 0.0
                self.windeast[-n:] = 0.0
            else:
                applywind         = self.alt[-n:]> 50.*ft
                self.windnorth[-n:], self.windeast[-n:]  = self.wind.getdata(self.lat[-n:], self.lon[-n:], self.alt[-n:])
                self.gsnorth[-n:] = self.gsnorth[-n:] + self.windnorth[-n:]*applywind
                self.gseast[-n:]  = self.gseast[-n:]  + self.windeast[-n:]*applywind
                self.trk[-n:]     = np.logical_not(applywind)*achdg + \
                                    applywind*np.degrees(np.arctan2(self.gseast[-n:], self.gsnorth[-n:]))
                self.gs[-n:]      = np.sqrt(self.gsnorth[-n:]**2 + self.gseast[-n:]**2)
        else:
            self.windnorth[-n:] = 0.0
            self.windeast[-n:]  = 0.0

        # Traffic autopilot settings
        self.selspd[-n:] = self.cas[-n:]
        self.aptas[-n:]  = self.tas[-n:]
        self.selalt[-n:] = self.alt[-n:]

        # Display information on label
        self.label[-n:] = n*[['', '', '', 0]]

        # Miscallaneous
        self.coslat[-n:] = np.cos(np.radians(aclat))  # Cosine of latitude for flat-earth aproximations
        self.eps[-n:] = 0.01

        # Finally call create for child TrafficArrays. This only needs to be done
        # manually in Traffic.
        self.create_children(n)

        # Record as individual CRE commands for repeatability
        #print(self.ntraf-n,self.ntraf)
        for j in range(self.ntraf-n,self.ntraf):
            # Reconstruct CRE command
            line = "CRE "+",".join([self.id[j],self.type[j],
                                    str(self.lat[j]),str(self.lon[j]),
                                    str(round(self.trk[j])),str(round(self.alt[j]/ft)),
                                    str(round(self.cas[j]/kts))])
            # Savecmd(cmd,line): line is saved, cmd is used to prevent recording PAN & ZOOM commands and CRE
            # So insert a dummy command to record the line
            savecmd("---",line)

    def creconfs(self, acid, actype, targetidx, dpsi, dcpa, tlosh, dH=None, tlosv=None, spd=None):
        ''' Create an aircraft in conflict with target aircraft.

            Arguments:
            - acid: callsign of new aircraft
            - actype: aircraft type of new aircraft
            - targetidx: id (callsign) of target aircraft
            - dpsi: Conflict angle (angle between tracks of ownship and intruder) (deg)
            - cpa: Predicted distance at closest point of approach (NM)
            - tlosh: Horizontal time to loss of separation ((hh:mm:)sec)
            - dH: Vertical distance (ft)
            - tlosv: Vertical time to loss of separation
            - spd: Speed of new aircraft (CAS/Mach, kts/-) manual
        '''
        latref  = self.lat[targetidx]  # deg
        lonref  = self.lon[targetidx]  # deg
        altref  = self.alt[targetidx]  # m
        trkref  = radians(self.trk[targetidx])
        gsref   = self.gs[targetidx]   # m/s
        tasref  = self.tas[targetidx]   # m/s
        vsref   = self.vs[targetidx]   # m/s
        cpa     = dcpa * nm
        pzr     = bs.settings.asas_pzr * nm
        pzh     = bs.settings.asas_pzh * ft
        trk     = trkref + radians(dpsi)

        if dH is None:
            acalt = altref
            acvs  = 0.0
        else:
            acalt = altref + dH
            tlosv = tlosh if tlosv is None else tlosv
            acvs  = vsref - np.sign(dH) * (abs(dH) - pzh) / tlosv

        if spd:
            # CAS or Mach provided: convert to groundspeed, assuming that
            # wind at intruder position is similar to wind at ownship position
            tas = tasref if spd is None else casormach2tas(spd, acalt)
            tasn, tase = tas * cos(trk), tas * sin(trk)
            wn, we = self.wind.getdata(latref, lonref, acalt)
            gsn, gse = tasn + wn, tase + we
        else:
            # Groundspeed is the same as ownship
            gsn, gse = gsref * cos(trk), gsref * sin(trk)

        # Horizontal relative velocity vector
        vreln, vrele = gsref * cos(trkref) - gsn, gsref * sin(trkref) - gse
        # Relative velocity magnitude
        vrel    = sqrt(vreln * vreln + vrele * vrele)
        # Relative travel distance to closest point of approach
        drelcpa = tlosh * vrel + (0 if cpa > pzr else sqrt(pzr * pzr - cpa * cpa))
        # Initial intruder distance
        dist    = sqrt(drelcpa * drelcpa + cpa * cpa)
        # Rotation matrix diagonal and cross elements for distance vector
        rd      = drelcpa / dist
        rx      = cpa / dist
        # Rotate relative velocity vector to obtain intruder bearing
        brn     = degrees(atan2(-rx * vreln + rd * vrele,
                                 rd * vreln + rx * vrele))

        # Calculate intruder lat/lon
        aclat, aclon = geo.kwikpos(latref, lonref, brn, dist / nm)
        # convert groundspeed to CAS, and track to heading using actual
        # intruder position
        wn, we     = self.wind.getdata(aclat, aclon, acalt)
        tasn, tase = gsn - wn, gse - we
        acspd      = tas2cas(sqrt(tasn * tasn + tase * tase), acalt)
        achdg      = degrees(atan2(tase, tasn))

        # Create and, when necessary, set vertical speed
        self.cre(acid, actype, aclat, aclon, achdg, acalt, acspd)
        self.ap.selaltcmd(len(self.lat) - 1, altref, acvs)
        self.vs[-1] = acvs

    def delete(self, idx):
        """Delete an aircraft"""
        # If this is a multiple delete, sort first for list delete
        # (which will use list in reverse order to avoid index confusion)
        if isinstance(idx, Collection):
            idx = np.sort(idx)

        # Call the actual delete function
        super().delete(idx)

        # Update number of aircraft
        self.ntraf = len(self.lat)
        return True

    def update(self):
        # Ground radar mode should be able to update without traffic
        if self.Ground_Radar_mode:
            Ground_radar_read.update(self)

        # Update only if there is traffic ---------------------
        if self.ntraf == 0:
            return
        #---------- Atmosphere --------------------------------
        self.p, self.rho, self.Temp = vatmos(self.alt)

        #---------- HighRes Meteo -----------------------------
        if self.HighRes == True:
            self.updateHighRes()

        #---------- ADSB Update -------------------------------
        self.adsb.update()

        #---------- Fly the Aircraft --------------------------
        self.ap.update()  # Autopilot logic
        self.update_asas()  # Airborne Separation Assurance
        self.aporasas.update()   # Decide to use autopilot or ASAS for commands

        #---------- Performance Update ------------------------
        self.perf.update()

        #---------- Limit commanded speeds based on performance ------------------------------
        self.aporasas.tas, self.aporasas.vs, self.aporasas.alt = \
            self.perf.limits(self.aporasas.tas, self.aporasas.vs,
                             self.aporasas.alt, self.ax)

        #---------- Kinematics --------------------------------
        self.update_airspeed()
        self.update_groundspeed()
        self.update_pos()

        # --------- Update from data --------------------------
        self.trafdatafeed.update()

        #---------- Simulate Turbulence -----------------------
        self.turbulence.update()

        # Check whether new traffic state triggers conditional commands
        self.cond.update()

        #---------- Aftermath ---------------------------------
        self.trails.update()

    @timed_function(name='asas', dt=bs.settings.asas_dt, manual=True)
    def update_asas(self):
        # Conflict detection and resolution
        self.cd.update(self, self)
        self.cr.update(self.cd, self, self)

    def update_airspeed(self):
        # Compute horizontal acceleration
        delta_spd = self.aporasas.tas - self.tas
        need_ax = np.abs(delta_spd) > np.abs(bs.sim.simdt * self.perf.axmax)
        self.ax = need_ax * np.sign(delta_spd) * self.perf.axmax
        # Update velocities
        self.tas = np.where(need_ax, self.tas + self.ax * bs.sim.simdt, self.aporasas.tas)
        self.cas = vtas2cas(self.tas, self.alt)
        self.M = vtas2mach(self.tas, self.alt)

        # Turning
        turnrate = np.degrees(g0 * np.tan(np.where(self.ap.turnphi>self.eps,self.ap.turnphi,self.ap.bankdef) \
                                          / np.maximum(self.tas, self.eps)))
        delhdg = (self.aporasas.hdg - self.hdg + 180) % 360 - 180  # [deg]
        self.swhdgsel = np.abs(delhdg) > np.abs(bs.sim.simdt * turnrate)

        # Update heading
        self.hdg = np.where(self.swhdgsel, 
                            self.hdg + bs.sim.simdt * turnrate * np.sign(delhdg), self.aporasas.hdg) % 360.0

        # Update vertical speed (alt select, capture and hold autopilot mode)
        delta_alt = self.aporasas.alt - self.alt
        # Old dead band version:
        #        self.swaltsel = np.abs(delta_alt) > np.maximum(
        #            10 * ft, np.abs(2 * bs.sim.simdt * self.vs))

        # Update version: time based engage of altitude capture (to adapt for UAV vs airliner scale)
        self.swaltsel = np.abs(delta_alt) >  1.05*np.maximum(np.abs(bs.sim.simdt * self.aporasas.vs), \
                                                         np.abs(bs.sim.simdt * self.vs))
        target_vs = self.swaltsel * np.sign(delta_alt) * np.abs(self.aporasas.vs)
        delta_vs = target_vs - self.vs
        # print(delta_vs / fpm)
        need_az = np.abs(delta_vs) > 300 * fpm   # small threshold
        self.az = need_az * np.sign(delta_vs) * (300 * fpm)   # fixed vertical acc approx 1.6 m/s^2
        self.vs = np.where(need_az, self.vs+self.az*bs.sim.simdt, target_vs)
        self.vs = np.where(np.isfinite(self.vs), self.vs, 0)    # fix vs nan issue

    def update_groundspeed(self):
        # Compute ground speed and track from heading, airspeed and wind
        if self.wind.winddim == 0:  # no wind
            self.gsnorth  = self.tas * np.cos(np.radians(self.hdg))
            self.gseast   = self.tas * np.sin(np.radians(self.hdg))

            self.gs  = self.tas
            self.trk = self.hdg
            self.windnorth[:], self.windeast[:] = 0.0,0.0
        else:
            applywind = self.alt>50.*ft # Only apply wind when airborne

            # Meteo data is loaded in here :)
            vnwnd,vewnd = self.wind.getdata(self.lat, self.lon, self.alt)
            # print(vnwnd)
            self.windnorth[:], self.windeast[:] = vnwnd,vewnd
            self.gsnorth  = self.tas * np.cos(np.radians(self.hdg)) + self.windnorth*applywind
            self.gseast   = self.tas * np.sin(np.radians(self.hdg)) + self.windeast*applywind
            self.gs  = np.logical_not(applywind)*self.tas + \
                       applywind*np.sqrt(self.gsnorth**2 + self.gseast**2)

            self.trk = np.logical_not(applywind)*self.hdg + \
                       applywind*np.degrees(np.arctan2(self.gseast, self.gsnorth)) % 360.

        self.work += (self.perf.thrust * bs.sim.simdt * np.sqrt(self.gs * self.gs + self.vs * self.vs))

    def update_pos(self):
        # Update position
        self.alt = np.where(self.swaltsel, np.round(self.alt + self.vs * bs.sim.simdt, 6), self.aporasas.alt)
        self.lat = self.lat + np.degrees(bs.sim.simdt * self.gsnorth / Rearth)
        self.coslat = np.cos(np.deg2rad(self.lat))
        self.lon = self.lon + np.degrees(bs.sim.simdt * self.gseast / self.coslat / Rearth)
        # Update distflown only for simulated aircraft
        itrafsim = np.setdiff1d(np.arange(0, self.ntraf), get_indices(self.id, bs.traf.trafdatafeed.datafeedids))
        self.distflown[itrafsim] += self.gs[itrafsim] * bs.sim.simdt

    def id2idx(self, acid):
        """Find index of aircraft id"""
        if not isinstance(acid, str):
            # id2idx is called for multiple id's
            # Fast way of finding indices of all ACID's in a given list
            tmp = dict((v, i) for i, v in enumerate(self.id))
            return [tmp.get(acidi, -1) for acidi in acid]
        else:
             # Catch last created id (* or # symbol)
            if acid in ('#', '*'):
                return self.ntraf - 1

            try:
                return self.id.index(acid.upper())
            except:
                return -1

    def idselect2idx(self):
        """
        Function: Get the index of the selected aircraft (when it exists)
        Args: -
        Returns:
            index of the selected aircraft [int] or -1 when there is no index

        Created by: Bob van Dillen
        Date: 10-12-2021
        """

        if self.id_select != '':
            try:
                return self.id.index(self.id_select.upper())
            except:
                return -1
        else:
            return -1

    def mnual(self, idx, flag=None):
        """
            Function:   Manual function in which an aircraft can be put in manual mode, this can be used when
                        having a scenario file, the function then deletes all aircraft specific instructions
            Args:
                - self
                - idx: aircraft index number
                - flag: the on/off switch
            Returns: -

            Created by: Stijn Brunia
            Date: 14-09-2021
        """
        self.manual[idx] = flag
        route = self.ap.route[idx]
        if len(route.wpname) == 0:
            print("ADSB FILE")
            """ When there are no waypoints, the sim is running on a scn-file made from radar or ADSB"""
            bs.stack.stackbase.manual_del()
        else:
            """" There are waypoints, so the ac has a route to follow"""
            if flag:
                """ Manual Mode on """
                print("MANUAL ON")
                bs.traf.swlnav[idx] = False

            elif not flag:
                """ Manual Mode off """
                print("MANUAL OFF")

    def meteo(self, flag):
        """
            Function:   Meteo function that activates a high resolution meteo data demo with data of 1-10-2021
            Args:
                - self
                - flag: the on/off switch
            Returns: -

            Created by: Stijn Brunia
            Date: 16-11-2021
        """
        if flag:
            self.activate_HighRes("bluesky_demo", True)
            bs.sim.setutc(1, 10, 2021, "00:30:00")
        else:
            self.activate_HighRes("bluesky_demo", False)

    def activate_HighRes(self, name,  flag=None):
        """
            Function:   Function that activates the high resolution meteo data mode.
            Args:
                - self
                - name: the name of the database in which the meteo data is stored
                - flag: the on/off switch
            Returns: -

            Created by: Stijn Brunia
            Date: 03-11-2021
        """

        self.HighRes = flag
        self.Wind_DB = name
        if self.HighRes:
            print("HighResolution Meteo mode has been initialised.")
            self.wind.winddim = 1
            self.activate_HR = True
        else:
            print("HighResolution Meteo mode has been disabled.")
            self.wind.winddim = 0

    def updateHighRes(self):
        """
            Function:   Updates the highres meteo data every minute, and loads the new data every 10 minutes
            Args:
                - self
            Returns: -

            Created by: Stijn Brunia
            Date: 29-11-2021
        """
        if len(str(bs.sim.utc)) == 19 and str(bs.sim.utc)[18] == "0":
            """ Only goes here when 10 seconds have past. """
            if (str(bs.sim.utc)[17:] == "00" and str(bs.sim.utc)[15] == "0") or self.activate_HR == True:
                """ Only goes here every 10 minutes, which is when the new weather data must be loaded. """
                self.prev_timestamp, self.next_timestamp = Functions.utc2stamps(bs.sim.utc)
                self.df_1 = Functions.query_DB_to_DF(self.Wind_DB,"SELECT * FROM " + self.Wind_DB + " WHERE timestamp_data = " + str(self.prev_timestamp))
                self.df_2 = Functions.query_DB_to_DF(self.Wind_DB,"SELECT * FROM " + self.Wind_DB + " WHERE timestamp_data = " + str(self.next_timestamp))
                self.HR_Loaded = True
                self.activate_HR = False

            if self.HR_Loaded:
                base = floor(len(self.lat) * int(str(bs.sim.utc)[17:])/60)
                top  = ceil(len(self.lat) * int(str(bs.sim.utc)[17:])/60) + ceil(len(self.lat) * 10/60)
                if top >= len(self.lat):
                    top -= 1
                for idx in range(top - base):
                    """ Fill the uwind and vwind variables. """
                    timefrac = Functions.utc2frac(bs.sim.utc, self.prev_timestamp)
                    if self.lat[idx + base] >= 49 and self.lat[idx + base] <= 55.9 and self.lon[idx + base] >= -1 and self.lon[idx + base] <= 9.9:
                        value1 = Functions.find_datapoint_timeframe(self.df_1,[self.prev_timestamp, self.alt[idx + base] / 0.3048,self.lat[idx + base], self.lon[idx + base]])
                        value2 = Functions.find_datapoint_timeframe(self.df_2,[self.next_timestamp, self.alt[idx + base] / 0.3048,self.lat[idx + base], self.lon[idx + base]])
                        self.windnorth[idx + base] = Functions.time_interpolation(timefrac, value1[4], value2[4])
                        self.windeast[idx + base] = Functions.time_interpolation(timefrac, value1[5], value2[5])

    def activate_GroundRadar(self, flag, *args):
        """
            Function:   Function that activates the ground radar
            Args:
                - self
                - args: the date of the traffic data
                - flag: the on/off switch
            Returns: -

            Created by: Stijn Brunia
            Date: 15-06-2022
        """
        if args:
            self.GR_date = [args[0], args[1], args[2], args[3]]
        self.Ground_Radar_mode = flag
        if self.Ground_Radar_mode:
            print("Ground Radar mode has been initialised.")
        else:
            print("Ground Radar mode has been disabled.")

    def setnoise(self, noise=None):
        """Noise (turbulence, ADBS-transmission noise, ADSB-truncated effect)"""
        if noise is None:
            return True, "Noise is currently " + ("on" if self.turbulence.active else "off")

        self.turbulence.setnoise(noise)
        self.adsb.setnoise(noise)
        return True

    def engchange(self, acid, engid):
        """Change of engines"""
        self.perf.engchange(acid, engid)
        return

    def move(self, idx, lat, lon, alt=None, hdg=None, casmach=None, vspd=None):
        self.lat[idx]      = lat
        self.lon[idx]      = lon

        if alt is not None:
            self.alt[idx]    = alt
            self.selalt[idx] = alt

        if hdg is not None:
            self.hdg[idx]  = hdg
            self.ap.trk[idx] = hdg

        if casmach is not None:
            self.tas[idx], self.selspd[idx], _ = vcasormach(casmach, alt)

        if vspd is not None:
            self.vs[idx]     = vspd
            self.swvnav[idx] = False

    def poscommand(self, idxorwp):# Show info on aircraft(int) or waypoint or airport (str)
        """POS command: Show info or an aircraft, airport, waypoint or navaid"""
        # Aircraft index

        if type(idxorwp)==int and idxorwp >= 0:

            idx           = idxorwp
            acid          = self.id[idx]
            actype        = self.type[idx]
            latlon        = latlon2txt(self.lat[idx], self.lon[idx])
            alt           = round(self.alt[idx] / ft)
            hdg           = round(self.hdg[idx])
            trk           = round(self.trk[idx])
            cas           = round(self.cas[idx] / kts)
            tas           = round(self.tas[idx] / kts)
            gs            = round(self.gs[idx]/kts)
            M             = self.M[idx]
            VS            = round(self.vs[idx]/ft*60.)
            route         = self.ap.route[idx]

            # Position report
            lines = "Info on %s %s index = %d\n" %(acid, actype, idx)     \
                  + "Pos: "+latlon+ "\n"                                  \
                  + "Hdg: %03d   Trk: %03d\n"        %(hdg, trk)              \
                  + "Alt: %d ft  V/S: %d fpm\n"  %(alt,VS)                \
                  + "CAS/TAS/GS: %d/%d/%d kts   M: %.3f\n"%(cas,tas,gs,M)

            # FMS AP modes
            if self.swlnav[idx] and route.nwp > 0 and route.iactwp >= 0:

                if self.swvnav[idx]:
                    if self.swvnavspd[idx]:
                        lines = lines + "VNAV (incl.VNAVSPD), "
                    else:
                        lines = lines + "VNAV (NOT VNAVSPD), "

                lines += "LNAV to " + route.wpname[route.iactwp] + "\n"

            # Flight info: Destination and origin
            if self.ap.orig[idx] != "" or self.ap.dest[idx] != "":
                lines = lines +  "Flying"

                if self.ap.orig[idx] != "":
                    lines = lines +  " from " + self.ap.orig[idx]

                if self.ap.dest[idx] != "":
                    lines = lines +  " to " + self.ap.dest[idx]

            # Show a/c info and highlight route of aircraft in radar window
            # and pan to a/c (to show route)
            bs.scr.showroute(acid)

            # Select aircraft for acidselect commands
            self.id_select = acid

            return True, lines

        # Waypoint: airport, navaid or fix
        else:
            wp = idxorwp.upper()

            # Reference position for finding nearest
            reflat, reflon = bs.scr.getviewctr()

            lines = "Info on "+wp+":\n"

            # First try airports (most used and shorter, hence faster list)
            iap = bs.navdb.getaptidx(wp)
            if iap>=0:
                aptypes = ["large","medium","small"]
                lines = lines + bs.navdb.aptname[iap]+"\n"                 \
                        + "is a "+ aptypes[max(-1,bs.navdb.aptype[iap]-1)] \
                        +" airport at:\n"                                    \
                        + latlon2txt(bs.navdb.aptlat[iap],                 \
                                     bs.navdb.aptlon[iap]) + "\n"          \
                        + "Elevation: "                                      \
                        + str(int(round(bs.navdb.aptelev[iap]/ft)))        \
                        + " ft \n"

               # Show country name
                try:
                    ico = bs.navdb.cocode2.index(bs.navdb.aptco[iap].upper())
                    lines = lines + "in "+bs.navdb.coname[ico]+" ("+      \
                             bs.navdb.aptco[iap]+")"
                except:
                    ico = -1
                    lines = lines + "Country code: "+bs.navdb.aptco[iap]
                try:
                    runways = bs.navdb.rwythresholds[bs.navdb.aptid[iap]].keys()
                    if runways:
                        lines = lines + "\nRunways: " + ", ".join(runways)
                except KeyError:
                    pass

            # Not found as airport, try waypoints & navaids
            else:
                iwps = bs.navdb.getwpindices(wp,reflat,reflon)
                if iwps[0]>=0:
                    typetxt = ""
                    desctxt = ""
                    lastdesc = "XXXXXXXX"
                    for i in iwps:

                        # One line type text
                        if typetxt == "":
                            typetxt = typetxt+bs.navdb.wptype[i]
                        else:
                            typetxt = typetxt+" and "+bs.navdb.wptype[i]

                        # Description: multi-line
                        samedesc = bs.navdb.wpdesc[i]==lastdesc
                        if desctxt == "":
                            desctxt = desctxt +bs.navdb.wpdesc[i]
                            lastdesc = bs.navdb.wpdesc[i]
                        elif not samedesc:
                            desctxt = desctxt +"\n"+bs.navdb.wpdesc[i]
                            lastdesc = bs.navdb.wpdesc[i]

                        # Navaid: frequency
                        if bs.navdb.wptype[i] in ["VOR","DME","TACAN"] and not samedesc:
                            desctxt = desctxt + " "+ str(bs.navdb.wpfreq[i])+" MHz"
                        elif bs.navdb.wptype[i]=="NDB" and not samedesc:
                            desctxt = desctxt+ " " + str(bs.navdb.wpfreq[i])+" kHz"

                    iwp = iwps[0]

                    # Basic info
                    lines = lines + wp +" is a "+ typetxt       \
                           + " at\n"\
                           + latlon2txt(bs.navdb.wplat[iwp],  \
                                        bs.navdb.wplon[iwp])
                    # Navaids have description
                    if len(desctxt)>0:
                        lines = lines+ "\n" + desctxt

                    # VOR give variation
                    if bs.navdb.wptype[iwp]=="VOR":
                        lines = lines + "\nVariation: "+ \
                                     str(bs.navdb.wpvar[iwp])+" deg"


                    # How many others?
                    nother = bs.navdb.wpid.count(wp)-len(iwps)
                    if nother>0:
                        verb = ["is ","are "][min(1,max(0,nother-1))]
                        lines = lines +"\nThere "+verb + str(nother) +\
                                   " other waypoint(s) also named " + wp

                    # In which airways?
                    connect = ""
                    # connect = bs.navdb.listconnections(wp, \
                    #                             bs.navdb.wplat[iwp],
                    #                             bs.navdb.wplon[iwp])
                    if len(connect)>0:
                        awset = set([])
                        for c in connect:
                            awset.add(c[0])

                        lines = lines+"\nAirways: "+"-".join(awset)


               # Try airway id
                else:  # airway
                    awid = wp
                    airway = bs.navdb.listairway(awid)
                    if len(airway)>0:
                        lines = ""
                        for segment in airway:
                            lines = lines+"Airway "+ awid + ": " + \
                                    " - ".join(segment)+"\n"
                        lines = lines[:-1] # cut off final newline
                    else:
                        return False,idxorwp+" not found as a/c, airport, navaid or waypoint"

            # Show what we found on airport and navaid/waypoint
            return True, lines

    def airwaycmd(self, key):
        ''' Show conections of a waypoint or airway. '''
        reflat, reflon = bs.scr.getviewctr()

        if bs.navdb.awid.count(key) > 0:
            return self.poscommand(key)

        # Find connecting airway legs
        wpid = key
        iwp = bs.navdb.getwpidx(wpid,reflat,reflon)
        if iwp < 0:
            return False,key + " not found."

        wplat = bs.navdb.wplat[iwp]
        wplon = bs.navdb.wplon[iwp]
        # connect = bs.navdb.listconnections(key, wplat, wplon)
        if connect:
            lines = ""
            for c in connect:
                if len(c)>=2:
                    # Add airway, direction, waypoint
                    lines = lines+ c[0]+": to "+c[1]+"\n"
            return True, lines[:-1]  # exclude final newline
        return False, f"No airway legs found for {key}"

    def settrans(self, alt=-999.):
        """ Set or show transition level"""
        # in case a valid value is ginve set it
        if alt > -900.:
            if alt > 0.:
                self.translvl = alt
                return True
            return False,"Transition level needs to be ft/FL and larger than zero"

        # In case no value is given, show it
        tlvl = int(round(self.translvl/ft))
        return True, f"Transition level = {tlvl}/FL{int(round(tlvl/100.))}"

    def setbanklim(self, idx, bankangle=None):
        ''' Set bank limit for given aircraft. '''
        if bankangle:
            self.ap.bankdef[idx] = np.radians(bankangle) # [rad]
            return True
        return True, f"Banklimit of {self.id[idx]} is {int(np.degrees(self.ap.bankdef[idx]))} deg"

    def setthrottle(self,idx,throttle=""):
        """Set throttle to given value or AUTO, meaning autothrottle on (default)"""

        if throttle:
            if throttle in ('AUTO', 'OFF'): # throttle mode off, ATS on
                self.swats[idx] = True   # Autothrottle on
                self.thr[idx] = -999.    # Set to invalid

            elif throttle == "IDLE":
                self.swats[idx] = False
                self.thr[idx] = 0.0

            else:
                # Check for percent unit
                if throttle.count("%")==1:
                    throttle= throttle.replace("%","")
                    factor = 0.01
                else:
                    factor = 1.0

                # Remaining option is that it is a float, so try conversion
                try:
                    x = factor*float(throttle)
                except:
                    return False,"THR invalid argument "+throttle

                # Check whether value makes sense
                if x<0.0 or x>1.0:
                    return False, "THR invalid value " + throttle +". Needs to be [0.0 , 1.0]"

                 # Valid value, set throttle and disable autothrottle
                self.swats[idx] = False
                self.thr[idx] = x

            return True

        if self.swats[idx]:
            return True,"ATS of "+self.id[idx]+" is ON"
        return True, "ATS of " + self.id[idx] + " is OFF. THR is "+str(self.thr[idx])