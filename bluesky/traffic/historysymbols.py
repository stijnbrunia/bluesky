"""
This python file is used to create history symbols for aircraft

Created by: Bob van Dillen
Date: 17-12-2021
"""

import numpy as np
import bluesky as bs
from bluesky.core import TrafficArrays

class HistorySymbols(TrafficArrays):
    """
    Class definition: Histroy symbols for aircraft
    Methods:


    Created by: Bob van Dillen
    Date: 17-12-2021
    """

    def __init__(self):
        super().__init__()

        self.lat = np.array([])
        self.lon = np.array([])

        self.swsend = 0

        with self.settrafarrays():
            self.lat1 = np.array([])
            self.lon1 = np.array([])
            self.lat2 = np.array([])
            self.lon2 = np.array([])
            self.lat3 = np.array([])
            self.lon3 = np.array([])
            self.lat4 = np.array([])
            self.lon4 = np.array([])

    def send(self):
        """
        Function: Merge history symbol positions, when needed
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 17-12-2021
        """

        if self.swsend == 1:
            self.lat = np.append(self.lat1, (self.lat2, self.lat3, self.lat4))
            self.lon = np.append(self.lon1, (self.lon2, self.lon3, self.lon4))
            self.lat = self.lat[self.lat != 0.]
            self.lon = self.lon[self.lon != 0.]

            self.lat4 = self.lat3
            self.lon4 = self.lon3
            self.lat3 = self.lat2
            self.lon3 = self.lon2
            self.lat2 = self.lat1
            self.lon2 = self.lon1
            self.lat1 = bs.traf.lat
            self.lon1 = bs.traf.lon

            self.swsend = 0
        else:
            self.swsend += 1
