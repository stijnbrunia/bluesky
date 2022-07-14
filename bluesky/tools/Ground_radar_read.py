import linecache
from datetime import datetime
import pytz
import numpy as np
import pandas as pd

import bluesky as bs

'''  Variables '''
directory = 'C:\\Users\\stijn\\Documents\\Administratie\\Aerospace Engineering\\Master\\Master Thesis\\Code\\Data\\Astra\\'
park_time = 600

''' Main Functions'''
def update(self):
    """
        Function: One of two main functions for plotting Ground Radar Data, this is where you enter this file
        Args: Traffic Entity (self)
        Returns: -

        Created by: Stijn Brunia
        Date = 15-6-2022
    """
    # Only enters this statement when you start plotting ground radar data, its sets some initial variables
    if self.current_line == 0 or self.current_line > self.n_lines:
        bs.sim.setutc(self.GR_date[0], self.GR_date[1], self.GR_date[2], self.GR_date[3])
        self.GR_file        = self.GR_directory + date2file([self.GR_date[0], self.GR_date[1], self.GR_date[2], self.GR_date[3]])
        self.n_lines        = number_of_lines(self.GR_file)
        self.current_line   = timestamp_to_line(self.GR_file, int(datetime.timestamp(pytz.utc.localize(bs.sim.utc))), self.n_lines)
        self.start_time     = int(datetime.timestamp(pytz.utc.localize(bs.sim.utc)))

    # Only enters this statement every whole second, this is the radar frequency so more is not needed
    if len(str(bs.sim.utc)) == 19:
        sim_time = int(datetime.timestamp(pytz.utc.localize(bs.sim.utc)))
        lines = get_time_lines(self, sim_time)
        update_traffic(self, lines, sim_time)

def update_traffic(self, lines, sim_time):
    """
        Function: Second main ground radar function, this is where the AC get created and moved according to the data
        Args: Traffic Entity (self), lines of data (lines), simulation time (sim_time)
        Returns: -

        Created by: Stijn Brunia
        Date = 15-6-2022
    """

    for line in lines:
        lat, lon = get_latlon(int(line[4]), int(line[3]))

        if actual_ac(line[8]):
            # Check if aircraft has appeared before to see if MOVE or CRE command should be given
            if self.active_ac['AC_id'].str.contains(line[8]).sum() > 0:
                i = np.where(self.active_ac['AC_id'] == line[8])
                if i[0].size > 0:  # to prevent no index error

                    # Dataframe updates
                    self.active_ac.at[i[0][0], 'time'] = line[0]
                    if location_check(self.active_ac.iloc[i[0][0]]['lat'], self.active_ac.iloc[i[0][0]]['lon'], lat, lon):
                        self.active_ac.at[i[0][0], 'park_count'] = self.active_ac.iloc[i[0][0]]['park_count'] + 1
                    else:
                        self.active_ac.at[i[0][0], 'lat'] = lat
                        self.active_ac.at[i[0][0], 'lon'] = lon

                    idx = bs.traf.id2idx(line[8])
                    bs.traf.move(idx, lat, lon)
            else:
                self.active_ac = self.active_ac.append({'AC_id': line[8], 'time': line[0], 'lat': lat, 'lon': lon, 'park_count': 0},ignore_index=True)
                bs.traf.cre(line[8], "B737", lat, lon)
                if inbound_check(lat, lon) and sim_time > self.start_time:
                    bay = which_bay(lat,lon)
                    self.where_created = self.where_created.append({'AC_id': line[8], 'time': bs.sim.utc, 'lat': lat, 'lon': lon, 'bay': bay},ignore_index=True)
                gate_recording(self)

        # Deleting aircraft when needed
        location_delete(self)
        time_delete(self, sim_time)


''' Gate Recording '''
def gate_recording(self):
    if self.record_gates:
        writer = pd.ExcelWriter(self.gates_file, engine='xlsxwriter')

        self.where_created.to_excel(writer, sheet_name='sheet_1')
        writer.save()

def inbound_check(lat, lon):
    if 52.2857 <= lat <= 52.3226:
        if 4.7291 <= lon <= 4.8170:
            return True
    else:
        return False

def which_bay(lat, lon):
    bay = "unknown"
    # Easy Bays first
    if 52.30820 < lat < 52.31402:
        if 4.74278 < lon < 4.74890:
            bay = "JP"
            return bay
    if 52.30421 < lat < 52.30633:
        if 4.74208 < lon < 4.74484:
            bay = "Y"
            return bay
    if 52.30825 < lat < 52.314414:
        if 4.75000 < lon < 4.75700:
            bay = "GH"
            return bay
    if 52.31103 < lat < 52.314380:
        if 4.75710 < lon < 4.762112:
            bay = "FG"
            return bay
    if 52.30745 < lat < 52.30950:
        if 4.76992 < lon < 4.77469:
            bay = "D"
            return bay
    if 52.29892 < lat < 52.30587:
        if 4.75119 < lon < 4.7640:
            bay = "A"
            return bay

    # Split Bays
    if 52.30850 < lat < 52.30954:
        if 4.76554 < lon < 4.76995:
            bay = "DE"
            return bay
    if 52.30809 < lat < 52.31014:
        if 4.76995 < lon < 4.77469:
            bay = "DE"
            return bay
    if 52.31042 < lat < 52.314414:
        if 4.75700 < lon < 4.76378:
            bay = "EF"
            return bay
    if 52.30700 < lat < 52.30853:
        if 4.76459 < lon < 4.77000:
            bay = "CD"
            return bay
    if 52.30678 < lat < 52.30744:
        if 4.77000 < lon < 4.77417:
            bay = "CD"
            return bay

    # Split by inclined line
    if 52.3100 < lat < 52.3150:
        if 4.76482 < lon < 4.76770:
            side = side_of_line(52.30290, 4.76382, 52.30573, 4.76081, lat, lon)
            if side < 0:
                bay = "DE"
                return bay
            else:
                bay = "EF"
                return bay

    if 52.31110 < lat < 52.31482:
        if 4.76770 < lon < 4.77120:
            side = side_of_line(52.31011, 4.76487, 52.31463, 4.76979, lat, lon)
            if side < 0:
                bay = "DE"
                return bay
            else:
                bay = "EF"
                return bay

    if 52.30424 < lat < 52.30714:
        if 4.76427 < lon < 4.76865:
            side = side_of_line(52.30705, 4.76480, 52.30433, 4.76707, lat, lon)
            if side < 0:
                bay = "BC"
                return bay
            else:
                bay = "CD"
                return bay

    if 52.30267 < lat < 52.30588:
        if 4.7640 < lon < 4.76865:
            side = side_of_line(52.30573, 4.76081, 52.30290, 4.76382, lat, lon)
            if side < 0:
                bay = "B"
                return bay
            else:
                bay = "BC"
                return bay

    if 52.30244 < lat < 52.30267:
        if 4.7640 < lon < 4.76495:
            side = side_of_line(52.30290, 4.76382, 52.30573, 4.76081, lat, lon)
            if side < 0:
                bay = "B"
                return bay
            else:
                bay = "BC"
                return bay
    return bay

def side_of_line(lat_1, lon_1, lat_2, lon_2, lat, lon):
    position = np.sign((lon_2 - lon_1) * (lat - lat_1) - (lat_2 - lat_1) * (lon - lon_1))
    return position

''' Text Reading Functions '''
def read_line(file, x):
    """ Reads line x of file """
    line = linecache.getline(file, x)
    return line

def timestamp_to_line(file, time, n_lines):
    """
       Function: This function will find the line in (file) at which the data for (time) starts
       Args: Data file (file), a timestamp (time), Number of lines (n_lines)
       Returns: Line index (line_idx)

       Created by: Stijn Brunia
       Date = 15-6-2022
    """

    # Check if the time is located at the first line
    if time == int(read_line(file, 1)[0:10]):
        line_idx = 1

    else:
        # Using Binary Search to find a line that starts with (time)
        low = 0
        high = n_lines
        search1 = True
        hist_search = []

        while search1:
            search_line = (high+low)/2
            timestamp = int(read_line(file, int(search_line))[0:10])

            if timestamp == time:
                search1 = False
            elif timestamp < time:
                low = search_line
            elif timestamp > time:
                high = search_line

            if search_line not in hist_search:
                hist_search.append(search_line)
            else:
                search1 = False

        # Find the first line that starts with (time) among the several lines that start with this value
        search2 = True
        while search2:
            search_line -= 1
            # print(search_line, time)
            timestamp = int(read_line(file, int(search_line))[0:10])
            if timestamp == (time - 1):
                search_line += 1
                search2 = False
        line_idx = int(search_line)

    return line_idx

def get_time_lines(self, sim_time):
    """
       Function: This function will collect all datalines with command that need to be executes at the current timestamp
       Args: Traffic Entity (self), current simulation timestamp (sim_time)
       Returns: All lines that belong to current simulation timestamp (lines)

       Created by: Stijn Brunia
       Date = 15-6-2022
    """
    lines = []
    x = 0
    reading = True
    while reading:
        line = read_line(self.GR_file, self.current_line + x).split(';')
        lines.append(line)
        x += 1
        if line[0] == str(sim_time + 1):
            reading = False
            lines = lines[0:-1]

    self.current_line += x-1
    return lines

def number_of_lines(file):
    # Finds the number of lines in the file
    with open(file, 'r') as fp:
        for count, line in enumerate(fp):
            pass
    return count + 1

''' Smaller General Functions '''
def time_delete(self, sim_time):
    """
      Function: Checks if there are any AC that have not had a new command for (parktime) seconds, if so delete AC
      Args: Traffic Entity (self), current simulation timestamp (sim_time)
      Returns:

      Created by: Stijn Brunia
      Date = 15-6-2022
    """
    ac_parked = self.active_ac.index[(self.active_ac['time'] == (str(sim_time - self.parktime)))]
    ac_del = self.active_ac.iloc[ac_parked]
    ac_del = ac_del['AC_id'].tolist()
    for ac in ac_del:
        if ac[-2:] != " p":
            i = np.where(self.active_ac['AC_id'] == ac)
            self.active_ac.at[i[0][0], 'AC_id'] = ac + " p"
            idx = bs.traf.id2idx(ac)
            bs.traf.delete(idx)

def location_delete(self):
    """
      Function: Checks if there are any AC that have been standing in the same place for a long time, if so delete
      Args: Traffic Entity (self)
      Returns:

      Created by: Stijn Brunia
      Date = 15-6-2022
    """
    ac_parked = self.active_ac.index[(self.active_ac['park_count'] == self.parktime)]
    ac_del = self.active_ac.iloc[ac_parked]
    ac_del = ac_del['AC_id'].tolist()
    for ac in ac_del:
        if ac[-2:] != " p":
            i = np.where(self.active_ac['AC_id'] == ac)
            self.active_ac.at[i[0][0], 'AC_id'] = ac + " p"
            idx = bs.traf.id2idx(ac)
            bs.traf.delete(idx)

def location_check(old_lat, old_lon, new_lat, new_lon):
    """" Checks if aircraft is standing in the same location as previously """
    delta_lat = abs(old_lat - new_lat)
    delta_lon = abs(old_lon - new_lon)
    if delta_lat < 0.00001 and delta_lon < 0.00001:
        return True
    else:
        return False

def actual_ac(ac_id):
    """ Filters out some AC with a specific ac_id, mostly vehicles instead of aircraft """
    if ac_id == "":
        return False
    elif ac_id[0:4] == "FUEL":
        return False
    elif ac_id[0:4] == "AMBU":
        return False
    elif ac_id[0:5] == "LIFEL":
        return False
    elif ac_id[0:5] == "MEDIC":
        return False
    elif len(ac_id) <= 4:
        return False
    elif ac_id[0:3] == "BRW":
        return False
    else:
        return True

def date2file(date):
    """ creates a filename from the selected date """
    filename = str(date[2]) + '\\' + str(date[1]) + '\\' + str(date[0]) + '_' + str(date[1]) + '_' + str(date[2]) + '.txt'
    return filename

''' Location Functions '''
def get_latlon(x,y):
    """
        Function: Calculate coordinates from x and y position
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date = 22-11-2021
    """

    base_lat = 52 + 18 / 60 + 27 / 3600
    base_lon = 4 + 45 / 60 + 44 / 3600

    lat = y
    lon = x

    #angle
    qdr = np.degrees(np.arctan2(lat, lon))
    qdr = np.where(qdr < 0, qdr + 360, qdr)
    #distance
    d = np.array(np.sqrt(lat ** 2 + lon ** 2))

    #wrt airport reference point
    lat, lon = qdrpos(base_lat, base_lon, qdr, d)
    return lat,lon

def rwgs84(latd):
    """ Calculate the earths radius with WGS'84 geoid definition
        In:  lat [deg] (latitude)
        Out: R   [m]   (earth radius)
        Created for Original BlueSky, slightly altered by Stijn Brunia """
    lat    = np.radians(latd)
    a      = 6378137.0       # [m] Major semi-axis WGS-84
    b      = 6356752.314245  # [m] Minor semi-axis WGS-84
    coslat = np.cos(lat)
    sinlat = np.sin(lat)

    an     = a * a * coslat
    bn     = b * b * sinlat
    ad     = a * coslat
    bd     = b * sinlat

    # Calculate radius in meters
    r = np.sqrt((an * an + bn * bn) / (ad * ad + bd * bd))

    return r

def qdrpos(latd1, lond1, qdr, dist):
    """ Calculate vector with positions from vectors of reference position,
        bearing and distance.
        In:
             latd1,lond1  [deg]   ref position(s)
             qdr          [deg]   bearing (vector) from 1 to 2
             dist         [m]    distance (vector) between 1 and 2
        Out:
             latd2,lond2 (IN DEGREES!)
        Ref for qdrpos: http://www.movable-type.co.uk/scripts/latlong.html
        Created for Original BlueSky, slightly altered by Stijn Brunia """

    # Unit conversion
    R = rwgs84(latd1)
    lat1 = np.radians(latd1)
    lon1 = np.radians(lond1)

    # Calculate new position
    lat2 = np.arcsin(np.sin(lat1)*np.cos(dist/R) +
                     np.cos(lat1)*np.sin(dist/R)*np.cos(np.radians(qdr)))

    lon2 = lon1 + np.arctan2(np.sin(np.radians(qdr))*np.sin(dist/R)*np.cos(lat1),
                             np.cos(dist/R) - np.sin(lat1)*np.sin(lat2))
    return np.degrees(lat2), np.degrees(lon2)