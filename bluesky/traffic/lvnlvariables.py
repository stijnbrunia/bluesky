"""
This python file is used to create traffic variables used by the LVNL

Created by: Bob van Dillen
Date: 24-12-2021
"""


import numpy as np
import bluesky as bs
from bluesky.core import Entity, timed_function
from bluesky.tools import misc, geo
from bluesky import stack


"""
Classes
"""


class LVNLVariables(Entity):
    """
    Definition: Class containing variables used by LVNL
    Methods:
        setarr():           Set the arrival/stack
        setflighttype():    Set the flight type
        setrwy():           Set the runway
        setsid():           Set the SID
        setwtc():           Set the wtc

    Created by: Bob van Dillen
    Date: 24-12-2021
    """

    def __init__(self):
        super().__init__()

        with self.settrafarrays():
            self.arr = []                                # Arrival/Stack
            self.dtg_tbar = np.array([])                 # Distance to T-Bar point
            self.flighttype = []                         # Flight type
            self.lblpos = []                             # Label position
            self.mlbl = np.array([], dtype=np.bool)      # Show micro label
            self.rel = np.array([], dtype=np.bool)       # Release
            self.rwy = []                                # Runway
            self.sid = []                                # SID
            self.ssr = np.array([], dtype=np.int)        # SSR code
            self.ssrlbl = []                             # Show SSR label
            self.tracklbl = np.array([], dtype=np.bool)  # Show track label
            self.uco = np.array([], dtype=np.bool)       # Under Control
            self.wtc = []                                # Wake Turbulence Category

    def create(self, n=1):
        """
        Function: Create an aircraft
        Args:
            n:  number of aircraft
        Returns: -

        Created by: Bob van Dillen
        Date: 12-1-2022
        """

        super().create(n)

        self.lblpos[-n:] = ['CR']
        self.tracklbl[-n:] = True
        self.ssrlbl[-n:] = [[]]
        self.mlbl[-n:] = False

    @timed_function(name='lvnlvars', dt=0.1)
    def update(self):
        """
        Function: Update LVNL variables
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 1-2-2022
        """

        # Distance to
        inirsi_gal1 = misc.get_indices(self.arr, "NIRSI_GAL01")
        inirsi_gal2 = misc.get_indices(self.arr, "NIRSI_GAL02")
        inirsi_603 = misc.get_indices(self.arr, "NIRSI_AM603")

        self.dtg_tbar[inirsi_gal1] = geo.kwikdist_matrix(bs.traf.lat[inirsi_gal1], bs.traf.lon[inirsi_gal1],
                                                         np.ones(len(inirsi_gal1))*52.47962777777778,
                                                         np.ones(len(inirsi_gal1))*4.513372222222222)
        self.dtg_tbar[inirsi_gal2] = geo.kwikdist_matrix(bs.traf.lat[inirsi_gal2], bs.traf.lon[inirsi_gal2],
                                                         np.ones(len(inirsi_gal2))*52.58375277777778,
                                                         np.ones(len(inirsi_gal2))*4.342225)
        self.dtg_tbar[inirsi_603] = geo.kwikdist_matrix(bs.traf.lat[inirsi_603], bs.traf.lon[inirsi_603],
                                                        np.ones(len(inirsi_603))*52.68805555555555,
                                                        np.ones(len(inirsi_603))*4.513333333333334)

        return

    @stack.command(name='UCO')
    def selucocmd(self, idx: 'acid'):
        """
        Function: Set UCO for aircraft
        Args:
            idx:    index for traffic arrays
        Returns: -
        """

        # Autopilot modes
        bs.traf.swlnav[idx] = True
        bs.traf.swvnav[idx] = True
        bs.traf.swvnavspd[idx] = True

        # Labels
        self.tracklbl[idx] = True
        self.ssrlbl[idx] = []

        bs.traf.trafdatafeed.uco(idx)
        self.uco[idx] = True
        self.rel[idx] = False

    @stack.command(name='REL',)
    def setrelcmd(self, idx: 'acid'):
        """
        Function: Set REL for aircraft
        Args:
            idx:    index for traffic arrays
        Returns: -

        Created by: Bob van Dillen
        """

        # Autopilot modes
        bs.traf.swlnav[idx] = True
        bs.traf.swvnav[idx] = True
        bs.traf.swvnavspd[idx] = True

        # Labels
        self.tracklbl[idx] = False
        self.ssrlbl[idx] = ['C']

        self.uco[idx] = False
        self.rel[idx] = True

    @stack.command(name='ARR', brief='ARR CALLSIGN ARRIVAL/STACK (ADDWPTS [ON/OFF])', aliases=('STACK',))
    def setarr(self, idx: 'acid', arr: str = '', addwpts: 'onoff' = True):
        """
        Function: Set the arrival/stack
        Args:
            idx:        index for traffic arrays [int]
            arr:        arrival/stack [str]
            addwpts:    add waypoints [bool]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        self.arr[idx] = arr.upper()

        if addwpts:
            acid = bs.traf.id[idx]
            cmd = 'PCALL LVNL/Routes/ARR/'+arr.upper()+' '+acid
            stack.stack(cmd)

    @stack.command(name='FLIGHTTYPE', brief='FLIGHTTYPE CALLSIGN TYPE')
    def setflighttype(self, idx: 'acid', flighttype: str):
        """
        Function: Set the flight type
        Args:
            idx:        index for traffic arrays [int]
            flighttype: flight type [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        if isinstance(flighttype, str):
            self.flighttype[idx] = flighttype.upper()

    @stack.command(name='POSLABEL', brief='POSLABEL CALLSIGN LL/LC/LR/CL/CR/UL/UC/UR')
    def poslabel(self, idx: 'acid', labelposition: str):
        """
        Function: Set position of the label
        Args:
            idx:            index for traffic arrays [int]
            labelposition:  position of the label [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 12-1-2021
        """

        if labelposition.upper() in ['LL', 'LC', 'LR', 'CL', 'CR', 'UL', 'UC', 'UR']:
            self.lblpos[idx] = labelposition.upper()
        else:
            return False, 'POSLABEL: Not a valid label position'

    @stack.command(name='MICROLABEL', brief='MICROLABEL CALLSIGN')
    def setmlabel(self, idx: 'acid'):
        """
        Function: Set the micro label
        Args:
            idx:    index for traffic arrays [int]
        Returns: -

        Created by: Bob van Dillen
        Date: 24-1-2022
        """

        self.mlbl[idx] = not self.mlbl[idx]

    @stack.command(name='RWY', brief='RWY CALLSIGN RUNWAY', aliases=('RW',))
    def setrwy(self, idx: 'acid', rwy: str):
        """
        Function: Set the runway
        Args:
            idx:    index for traffic arrays [int]
            rwy:    runway [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        if isinstance(rwy, str):
            self.rwy[idx] = rwy.upper()

    @stack.command(name='SID', brief='SID CALLSIGN SID')
    def setsid(self, idx: 'acid', sid: str = '', addwpts: 'onoff' = True):
        """
        Function: Set the SID
        Args:
            idx:    index for traffic arrays [int]
            sid:    SID [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        self.sid[idx] = sid.upper()

        if addwpts:
            acid = bs.traf.id[idx]
            cmd = 'PCALL LVNL/Routes/ARR/'+sid.upper()+' '+acid
            stack.stack(cmd)

    @stack.command(name='SSRCODE', brief='SSRCODE CALLSIGN SSR')
    def setssr(self, idx: 'acid', ssr: float):
        """
        Function: Set the SSR code
        Args:
            idx:    index for traffic arrays [int]
            ssr:    SSR code [int]
        Returns: -

        Created by: Bob van Dillen
        Date: 25-1-2022
        """

        self.ssr[idx] = int(ssr)

    @stack.command(name='SSRLABEL', brief='SSRLABEL CALLSIGN MODE')
    def setssrlabel(self, idx: 'acid', ssrmode: str):
        """
        Function: Set the SSR label
        Args:
            idx:        index for traffic arrays [int]
            ssrmode:    ssr label mode [int]
        Returns: -

        Created by: Bob van Dillen
        Date: 24-1-2022
        """

        ssrmode = ssrmode.upper()

        if ssrmode in ['A', 'C', 'ACID']:
            if ssrmode in self.ssrlbl[idx]:
                self.ssrlbl[idx].remove(ssrmode)
            else:
                self.ssrlbl[idx].append(ssrmode)
        else:
            return False, 'SSRLABEL: Not a valid SSR label item'

    @stack.command(name='TRACKLABEL', brief='TRACKLABEL CALLSIGN')
    def settracklabel(self, idx: 'acid'):
        """
        Function: Set the track label
        Args:
            idx:        index for traffic arrays [int]
        Returns: -

        Created by: Bob van Dillen
        Date: 24-1-2022
        """

        self.tracklbl[idx] = not self.tracklbl[idx]

    @stack.command(name='WTC', brief='WTC CALLSIGN WTC')
    def setwtc(self, idx: 'acid', wtc: str = ''):
        """
        Function: Set the wtc
        Args:
            idx:    index for traffic arrays [int]
            wtc:    wtc [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        if isinstance(wtc, str):
            self.wtc[idx] = wtc.upper()
