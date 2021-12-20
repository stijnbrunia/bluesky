import bluesky as bs
import requests
import json
import pandas as pd
import datetime
import numpy as np


class LiveTraffic:
    def __init__(self, lat_min=50.5681, lon_min=1.7543, lat_max=55.8395, lon_max=7.6876):
        self.lat_min = lat_min
        self.lon_min = lon_min
        self.lat_max = lat_max
        self.lon_max = lon_max

        self.url_data = 'https://opensky-network.org/api/states/all?lamin='+str(self.lat_min) + \
                        '&lomin='+str(self.lon_min)+'&lamax='+str(self.lat_max)+'&lomax='+str(self.lon_max)

        self.trackdata = None

    def update(self):
        response = requests.get(self.url_data).json()

        date_time = datetime.datetime.fromtimestamp(response['time'])

        col_name = ['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact', 'lon', 'lat',
                    'baro_altitude', 'on_ground', 'velocity', 'true_track', 'vertical_rate', 'sensors',
                    'geo_altitude', 'squawk', 'spi', 'position_source', 'none']
        flight_df = pd.DataFrame(response['states'], columns=col_name)

        ids = np.array(flight_df['callsign'])
        actype = 'B738'

        ids_new = np.setdiff1d(ids, bs.traf.id)

        i_idsnew = bs.traf.trafreplay.get_indices(ids, ids_new)
        for i in i_idsnew:

            bs.traf.trafreplay.crereplay(ids[0], actype)


