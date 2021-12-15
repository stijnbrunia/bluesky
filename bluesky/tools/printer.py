import bluesky as bs
import numpy as np


def printing():
    print('PRINTER:')
    print('\t', np.array(bs.traf.ap.route)[0].wpname)
    print('\t', np.array(bs.traf.ap.route)[0].wptype)
    print('\t', np.array(bs.traf.ap.route)[0].iactwp)
