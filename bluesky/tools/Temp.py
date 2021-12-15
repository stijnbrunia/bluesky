import numpy as np

simt = np.array([0., 6., 6., 9., 12., 12., 12., 15., 15., 18., 18., 18.])
unique, indx, count = np.unique(simt, return_index=True, return_counts=True)