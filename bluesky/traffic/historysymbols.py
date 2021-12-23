"""
This python file is used to create history symbols for aircraft

Created by: Bob van Dillen
Date: 17-12-2021
"""

import numpy as np
import bluesky as bs
from bluesky.core import Entity, timed_function
from bluesky.tools import misc


class HistorySymbols(Entity):
    """
    Class definition: Histroy symbols for aircraft
    Methods:
        clear():    Reset variables
        update():   Update the history symbols
        update_history():   Update the history locations
        setHistory():       Enable/Disable history symbols

    Created by: Bob van Dillen
    Date: 17-12-2021
    """

    def __init__(self):
        super().__init__()

        self.active = True

        self.lat = np.array([])
        self.lon = np.array([])

        self.t_prev = 0.

        with self.settrafarrays():
            self.swhistory = np.array([], dtype=np.bool)

            self.lat1 = np.array([])
            self.lon1 = np.array([])

            self.lat2 = np.array([])
            self.lon2 = np.array([])

            self.lat3 = np.array([])
            self.lon3 = np.array([])

            self.lat4 = np.array([])
            self.lon4 = np.array([])

            self.lat5 = np.array([])
            self.lon5 = np.array([])

    def clear(self):
        """
        Function: Reset variables
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 20-12-2021
        """

        self.lat = np.array([])
        self.lon = np.array([])

        self.t_prev = 0.

    @timed_function(name='historysymbols', dt=0.5)
    def update(self):
        """
        Function: Update the history symbols
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 20-12-2021
        """

        if self.active:
            # Get latitudes and longitudes for all history symbols
            self.lat = np.append(self.lat1, (self.lat2, self.lat3, self.lat4, self.lat5))
            self.lon = np.append(self.lon1, (self.lon2, self.lon3, self.lon4, self.lon5))
            self.lat = self.lat[self.lat != 0.]
            self.lon = self.lon[self.lon != 0.]

            # Replay/playback traffic
            if len(bs.traf.trafreplay.replayid) > 0:
                itrafreplay = misc.get_indices(bs.traf.id, bs.traf.trafreplay.replayid)
                # Replay traffic that received an update
                itrafnew = np.nonzero(bs.traf.lat != self.lat1)[0]
                ireplay_new = np.intersect1d(itrafreplay, itrafnew, assume_unique=True)
            else:
                itrafreplay = np.array([])
                ireplay_new = np.array([])

            # Simulated traffic
            deltat = bs.sim.simt - self.t_prev
            if deltat >= bs.settings.screendt:
                itraf_new = np.setdiff1d(np.arange(bs.traf.ntraf), itrafreplay)
                self.t_prev = bs.sim.simt
            else:
                itraf_new = np.array([])

            # Merge indices and update history
            i_new = np.append(ireplay_new, itraf_new)
            i_new = i_new.astype(np.int32)

            # Every other position gets a history symbol
            i_swhistory = np.nonzero(self.swhistory)[0]
            i_update = np.intersect1d(i_new, i_swhistory)
            self.swhistory[i_new] = ~self.swhistory[i_new]

            # Update the history symbols
            self.update_history(i_update)

    def update_history(self, indices):
        """
        Function: Update the history locations
        Args:
            indices:    indices of the update
        Returns: -

        Created by: Bob van Dillen
        Date: 20-12-2021
        """

        self.lat5[indices] = self.lat4[indices]
        self.lon5[indices] = self.lon4[indices]

        self.lat4[indices] = self.lat3[indices]
        self.lon4[indices] = self.lon3[indices]

        self.lat3[indices] = self.lat2[indices]
        self.lon3[indices] = self.lon2[indices]

        self.lat2[indices] = self.lat1[indices]
        self.lon2[indices] = self.lon1[indices]

        self.lat1[indices] = bs.traf.lat[indices]
        self.lon1[indices] = bs.traf.lon[indices]

    def setHistory(self, *args):
        """
        Function: Enable/Disable history symbols
        Args:
            *args:  arguments
        Returns: -

        Created by: Bob van Dillen
        Date: 23-12-2021
        """

        if type(args[0]) == bool:
            self.active = args[0]
            if not self.active:
                self.lat = np.array([])
                self.lon = np.array([])

        return True
