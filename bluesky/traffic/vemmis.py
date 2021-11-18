import bluesky as bs
from bluesky.tools.aero import vcasormach

import numpy as np


def update_radardata(func):
    def inner(*args, **kwargs):
        ntraf_temp = bs.traf.ntraf
        bs.traf.ntraf = 0
        func(*args, **kwargs)
        bs.traf.ntraf = ntraf_temp

        # TODO make more efficient by check if next datapoint is reached

        i = np.where(np.round(bs.traf.vemmis_simt, 1)+1 == round(bs.sim.simt, 1))[0]

        if True in bs.traf.vemmis_cre[i]:
            i_cre = np.where(bs.traf.vemmis_cre[i])[0]
            for j in i_cre:
                bs.traf.cre(bs.traf.vemmis_id[i][j], bs.traf.vemmis_type[i][j],
                            bs.traf.vemmis_lat[i][j], bs.traf.vemmis_lon[i][j],
                            str(bs.traf.vemmis_hdg[i][j]), bs.traf.vemmis_alt[i][j], bs.traf.vemmis_spd[i][j])
                print('\n'+str(round(bs.sim.simt, 1))+'s: Created '+bs.traf.vemmis_id[i][j])

        idx = np.nonzero(bs.traf.vemmis_id[i][:, None] == bs.traf.id)

        if len(i) > 0:
            idx = idx[1]

            bs.traf.lat[idx] = bs.traf.vemmis_lat[i]
            bs.traf.lon[idx] = bs.traf.vemmis_lon[i]
            bs.traf.alt[idx] = bs.traf.vemmis_alt[i]
            bs.traf.hdg[idx] = bs.traf.vemmis_alt[i]
            bs.traf.cas[idx] = bs.traf.vemmis_spd[i]

            bs.traf.trk[idx] = bs.traf.vemmis_hdg[i]
            bs.traf.tas[idx], bs.traf.cas[idx], bs.traf.M[idx] = vcasormach(bs.traf.vemmis_spd[idx],
                                                                            bs.traf.vemmis_alt[idx])
            bs.traf.gs[idx] = bs.traf.tas[idx]

            bs.traf.trails.update()

            print('\n'+str(round(bs.sim.simt, 1))+'s: Moved '+str(bs.traf.vemmis_id[i])+' ('+str(np.array(bs.traf.id)[idx])+')')
            print(bs.traf.cas)

        if True in bs.traf.vemmis_del[i]:
            acid_del = bs.traf.vemmis_id[np.where(bs.traf.vemmis_del[i])]
            print('Delete', acid_del)
            idx_del = np.where(np.isin(bs.traf.id, acid_del))[0]
            print(idx_del)
            for j in idx_del:
                print(j)
                bs.traf.delete(j)

    return inner
