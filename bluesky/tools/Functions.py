import psycopg2
import pandas as pd
from math import floor, ceil


def Connect_SQL_DB(dbname):
    conn = psycopg2.connect(
        host="localhost",
        database=dbname,
        user="postgres",
        password="lucht_1")
    return conn

def query_DB_to_DF(dbname, query):
    """ Function that creates a dataframe from data that is inside the SQL Database """
    conn = Connect_SQL_DB(dbname)
    sql_query = pd.read_sql_query(query, conn)
    df = pd.DataFrame(sql_query, columns=['timestamp_data', 'timestamp_prediction', 'lon', 'lat', 'alt', 'uwind', 'vwind'])
    return df

def find_datapoint_timeframe(df, point): #point is [time,alt,lat,lon]
    """ Function that calculates the correct meteo values, interpolating over alt,lat,lon  """
    lon_min  = floor(point[3] * 10) / 10
    lon_plus = ceil(point[3]  * 10) / 10
    lat_min  = floor(point[2] * 10) / 10
    lat_plus = ceil(point[2]  * 10) / 10

    value_mmm, value_pmm = find_height_levels(df, point, lat_min, lon_min)
    value_mmp, value_pmp = find_height_levels(df, point, lat_min, lon_plus)
    value_mpm, value_ppm = find_height_levels(df, point, lat_plus, lon_min)
    value_mpp, value_ppp = find_height_levels(df, point, lat_plus, lon_plus)

    timeless_value  = interpolation(value_mmm, value_mmp, value_mpm, value_mpp, value_pmm, value_pmp, value_ppm, value_ppp, point[1], point[2], point[3])
    value           = [point[0], timeless_value[0], timeless_value[1], timeless_value[2], timeless_value[3], timeless_value[4]]
    return value

def find_height_levels(df, point, lat, lon):
    " Function that finds the closest height levels above and below the actual height, needed for interpolation "
    df_t = df.query('lat == ' + str(lat) + ' and lon ==' + str(lon))
    layer_min = layer_plus = -1
    value_m = value_p = -1
    for i in range(len(df_t)):
        if point[1] > df_t.iloc[i][4]:
            if i - 1 >= 0:
                layer_min = i
                layer_plus = i - 1
                break
    if layer_min != -1 and layer_plus != -1:
        value_m = [df_t.iloc[layer_min][4], lat, lon, df_t.iloc[layer_min][5], df_t.iloc[layer_min][6]]
        value_p = [df_t.iloc[layer_plus][4], lat, lon, df_t.iloc[layer_plus][5], df_t.iloc[layer_plus][6]]
    return value_m, value_p

def interpolation(value_mmm, value_mmp, value_mpm, value_mpp, value_pmm, value_pmp, value_ppm, value_ppp, alt, lat, lon): #values are [time,alt,lat,lon, uwind, vwind]
    """ Function with the interpolation structure over first alt, second lat and finally lon """
    if value_mmm != -1 and value_mmp != -1 and value_mpm != -1 and value_mpp != -1 and value_pmm != -1 and value_pmp != -1 and value_ppm != -1 and value_ppp != -1:
        value_mm = [value_mmm[0], value_mmm[1], lon, interpolate(lon, value_mmm[2], value_mmp[2], value_mmm[3], value_mmp[3]), interpolate(lon, value_mmm[2], value_mmp[2], value_mmm[4], value_mmp[4])]
        value_mp = [value_mpm[0], value_mpm[1], lon, interpolate(lon, value_mpm[2], value_mpp[2], value_mpm[3], value_mpp[3]), interpolate(lon, value_mpm[2], value_mpp[2], value_mpm[4], value_mpp[4])]
        value_pm = [value_pmm[0], value_pmm[1], lon, interpolate(lon, value_pmm[2], value_pmp[2], value_pmm[3], value_pmp[3]), interpolate(lon, value_pmm[2], value_pmp[2], value_pmm[4], value_pmp[4])]
        value_pp = [value_ppm[0], value_ppm[1], lon, interpolate(lon, value_ppm[2], value_ppp[2], value_ppm[3], value_ppp[3]), interpolate(lon, value_ppm[2], value_ppp[2], value_ppm[4], value_ppp[4])]

        value_m  = [value_mm[0], lat, lon, interpolate(lat, value_mm[1], value_mp[1], value_mm[3], value_mp[3]), interpolate(lat, value_mm[1], value_mp[1], value_mm[4], value_mp[4])]
        value_p  = [value_pm[0], lat, lon, interpolate(lat, value_pm[1], value_pp[1], value_pm[3], value_pp[3]), interpolate(lat, value_pm[1], value_pp[1], value_pm[4], value_pp[4])]

        value    = [alt, lat, lon, round(interpolate(alt, value_m[0], value_p[0], value_m[3], value_p[3]),4), round(interpolate(alt, value_m[0], value_p[0], value_m[4], value_p[4]),4)]

    else:
        value = [alt, lat, lon, 0, 0]
    return value

def interpolate(value , value_a , value_b, answer_a , answer_b):
    """ Actual interpolation function """
    if value_a != value_b:
        answer = (value - value_a)/(value_b - value_a) * (answer_b-answer_a) + answer_a
        return answer
    return answer_a

def time_interpolation(timefrac , answer_a , answer_b):
    """ Performce the interpolation over time """
    answer = timefrac * (answer_b-answer_a) + answer_a
    return answer

def utc2stamps(utc):
    """ Goes from utc to timestamp """
    utc     = str(utc)
    day     = utc[8:10]
    month   = utc[5:7]
    year    = utc[0:4]
    hour    = utc[11:13]
    minutes = utc[14:16]

    stamp1 = year[2:] + month + day + hour + minutes[0]
    if int(minutes[0]) < 5:
        stamp2 = str(int(stamp1) + 1)
    else:
        stamp2 = str(int(stamp1) + 10 - int(minutes[0]))
        if int(stamp2[6:8]) > 23:
            stamp2 = str(int(stamp2) + 760 )
            days = days_in_month(int(stamp2[2:4]), int("20" + stamp2[0:2]))
            if int(stamp2[4:6]) > days:
                stamp2 = str(int(stamp2) + 100000 - days*1000)
                if int(stamp2[2:4]) > 12:
                    stamp2 = str(int(stamp2) +8800000)
    return stamp1, stamp2

def utc2frac(utc, stamp):
    """ Goes from UTC to time fraction using the first timestamp, needed for time interpolation """
    utc             = str(utc)
    stamp           = str(stamp)
    minutes_utc     = utc[14:16]
    seconds_utc     = utc[17:19]
    minutes_stamp   = stamp[8] + "0"
    d_minutes       = int(minutes_utc) - int(minutes_stamp)
    d_seconds       = int(d_minutes) * 60 + int(seconds_utc)
    frac            = d_seconds/600

    return frac

def days_in_month(month, year):
    """ Check the number of days in the month"""
    days = 31;
    if month == 2:
        days = 28;
        if floor(year / 4) == (year / 4):
            days = 29
    if month == 4:
        days = 30
    if month == 6:
        days = 30
    if month == 9:
        days = 30
    if month == 11:
        days = 30
    return days