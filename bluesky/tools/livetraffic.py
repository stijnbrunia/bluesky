"""
This python file is used to get live data as data source

Created by: Bob van Dillen
Date: 14-1-2022
"""

import requests
import pandas as pd

class OpenSkySource:
    """
    Class definition: OpenSky as data source for data feed
    Methods:
        update_trackdata(): Update the track data

    Created by: Bob van Dillen
    Date: 14-1-2022
    """

    def __init__(self):
        self.latmin = 50.564026
        self.latmax = 54.670686
        self.lonmin = 2.956581
        self.lonmax = 7.80055

    def update_trackdata(self):
        return
