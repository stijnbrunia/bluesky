import bluesky as bs
from bluesky.tools.aero import vcasormach
from bluesky.stack.stackbase import Stack

import numpy as np

def update_radardata(func):
    def inner(*args, **kwargs):
        # Disable normal traffic update routine
        ntraf_temp = bs.traf.ntraf
        bs.traf.ntraf = 0
        func(*args, **kwargs)
        bs.traf.ntraf = ntraf_temp

        # Check if data points are reached
        i = np.where(bs.traf.vemmis_trackdata.T[0] == round(bs.sim.simt, 1))[0]
        if len(i) > 0:
            idx = np.nonzero(bs.traf.vemmis_trackdata.T[1][i][:, None] == bs.traf.id)[1]

            bs.traf.lat[idx] = bs.traf.vemmis_trackdata.T[2][i]
            bs.traf.lon[idx] = bs.traf.vemmis_trackdata.T[3][i]
            bs.traf.alt[idx] = bs.traf.vemmis_trackdata.T[4][i]
            bs.traf.hdg[idx] = bs.traf.vemmis_trackdata.T[5][i]
            bs.traf.cas[idx] = bs.traf.vemmis_trackdata.T[6][i]

            bs.traf.trk[idx] = bs.traf.hdg[idx]
            bs.traf.tas[idx], bs.traf.cas[idx], bs.traf.M[idx] = vcasormach(bs.traf.cas[idx],
                                                                            bs.traf.alt[idx])
            bs.traf.gs[idx] = bs.traf.tas[idx]

            bs.traf.trails.update()

            # Delet aircraft
            # if True in bs.traf.vemmis_del[i]:
            #     acid_del = bs.traf.vemmis_id[np.where(bs.traf.vemmis_del[i])]
            #     idx_del = np.where(np.isin(bs.traf.id, acid_del))[0]
            #     for j in idx_del:
            #         bs.traf.delete(j)
            #         print('\tDeleted', acid_del)
            bs.traf.vemmis_trackdata = np.delete(bs.traf.vemmis_trackdata, 0, axis=0)

    return inner
