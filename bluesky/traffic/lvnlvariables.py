"""
This python file is used to create traffic variables used by the LVNL

Created by: Bob van Dillen
Date: 24-12-2021
"""


import numpy as np
from bluesky.core import Entity
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
            self.arr = []                           # Arrival/Stack
            self.flighttype = []                    # Flight type
            self.lblpos = []                        # Label position
            self.rel = np.array([], dtype=np.bool)  # Release
            self.rwy = []                           # Runway
            self.sid = []                           # SID
            self.uco = np.array([], dtype=np.bool)  # Under Control
            self.wtc = []                           # Wake Turbulence Category

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

    @stack.command(name='ARR', brief='ARR CALLSIGN ARRIVAL/STACK', aliases=('STACK',))
    def setarr(self, idx: 'acid', arr: str = ''):
        """
        Function: Set the arrival/stack
        Args:
            idx:    index for traffic arrays [int]
            arr:    arrival/stack [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        if isinstance(arr, str):
            self.arr[idx] = arr.upper()

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
    def setsid(self, idx: 'acid', sid: str = ''):
        """
        Function: Set the SID
        Args:
            idx:    index for traffic arrays [int]
            sid:    SID [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        if isinstance(sid, str):
            self.sid[idx] = sid.upper()

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

    @stack.command(name='POSLABEL', brief='POSLABEL CALLSIGN LL/LC/LR/CL/CR/UL/UC/UR')
    def poslabel(self, idx: 'acidselect', labelposition: str):
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
