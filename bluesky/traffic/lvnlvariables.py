"""
This python file is used to create traffic variables used by the LVNL

Created by: Bob van Dillen
Date: 24-12-2021
"""


import numpy as np
import bluesky as bs
from bluesky.core import Entity, timed_function
from bluesky import stack


"""
Classes
"""


class LVNLVariables(Entity):
    def __init__(self):
        super().__init__()

        with self.settrafarrays():
            self.arr = []                           # Arrival/Stack
            self.flighttype = []                    # Flight type
            self.rel = np.array([], dtype=np.bool)  # Release
            self.rwy = []                           # Runway
            self.sid = []                           # SID
            self.uco = np.array([], dtype=np.bool)  # Under Control
            self.wtc = []                           # Wake Turbulence Category

    @stack.command(name='ARR')
    def setarr(self, idx: 'acid', arr: str = ''):
        """
        Function: Set the arrival
        Args:
            idx:    index for traffic arrays [int]
            arr:    arrival/stack [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 21-12-2021
        """

        if isinstance(arr, str):
            self.arr[idx] = arr

    @stack.command(name='FLIGHTTYPE')
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
            self.flighttype[idx] = flighttype

    @stack.command(name='RWY')
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
            self.rwy[idx] = rwy

    @stack.command(name='SID')
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
            self.sid[idx] = sid

    @stack.command(name='WTC')
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
            self.wtc[idx] = wtc
