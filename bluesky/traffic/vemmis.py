import bluesky as bs
from bluesky.tools.aero import vcasormach

import numpy as np

def update_radardata(func):
    def inner(*args, **kwargs):
        ntraf_temp = bs.traf.ntraf
        bs.traf.ntraf = 0
        func(*args, **kwargs)
        bs.traf.ntraf = ntraf_temp

        i = np.where(bs.traf.vemmis_simt == bs.sim.simt)
        if True in bs.traf.vemmis_cre[i]:
            i_cre = np.where(bs.traf.vemmis_cre[i])
            acid_cre = bs.traf.vemmis_id[i_cre]
            bs.traf.cre(acid_cre, 'B738', bs.traf.vemmis_lat[i_cre], bs.traf.vemmis_lon[i_cre],
                        bs.traf.vemmis_hdg[i_cre], bs.traf.vemmis_alt[i_cre], bs.traf.vemmis_spd[i_cre])

        if True in bs.traf.vemmis_del[i]:
            acid_del = bs.traf.vemmis_del[np.where(bs.traf.vemmis_del[i])]
            idx_del = np.where(np.isin(bs.traf.id, acid_del))
            bs.traf.delete(idx_del)


        idx = np.nonzero(bs.traf.vemmis_id[i][:, None] == bs.traf.id)

        bs.traf.lat[idx] = bs.traf.vemmis_lat[i]
        bs.traf.lon[idx] = bs.traf.vemmis_lon[i]
        bs.traf.alt[idx] = bs.traf.vemmis_alt[i]
        bs.traf.hdg[idx] = bs.traf.vemmis_alt[i]
        bs.traf.cas[idx] = bs.traf.vemmis_spd[i]

        bs.traf.trk[idx] = bs.traf.vemmis_hdg[i]
        bs.traf.tas[idx], bs.traf.cas[idx], bs.traf.M[idx] = vcasormach(bs.traf.vemmis_spd, bs.traf.vemmis_alt)
        bs.traf.gs[idx] = bs.traf.tas[idx]

    return inner