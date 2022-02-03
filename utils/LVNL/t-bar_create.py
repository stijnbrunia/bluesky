"""
This python file creates the required scenario files for the T-bars

Created by: Bob van Dillen
Date: 22-12-2021
"""

import pandas as pd
import re

# Read waypoint data
wptdata = pd.read_excel(r"C:\Users\LVNL_ILAB3\PycharmProjects\bluesky\scenario\LVNL\T-Bar_wpts.xlsx")
wptdata.drop_duplicates(subset=['Name'], keep='first', inplace=True)

# Get the latitude and longitude
latlon = wptdata['Position'].str.strip('N ').str.split('E ', expand=True)
lat = latlon[0].str.split(':', expand=True)
lon = latlon[1].str.split(':', expand=True)
wptdata['Lat'] = lat[0].astype("float") + lat[1].astype("float")/60 + lat[2].astype("float")/3600
wptdata['Lon'] = lon[0].astype("float") + lon[1].astype("float")/60 + lon[2].astype("float")/3600
wptdata['LatLon'] = wptdata['Lat'].astype("str") + " " + wptdata['Lon'].astype("str")

# Set index
wptdata.set_index(wptdata['Name'], inplace=True)

# Create scenario file to add required waypoints
fwpts = open('/scenario/LVNL/T-Bars.scn', 'w')
fwpts.write("# Define new waypoints\n")
for i in range(len(wptdata)):
    fwpts.write("00:00:00.00>DEFWPT "+wptdata['Name'].iloc[i]+" "+wptdata['LatLon'].iloc[i]+"\n")
fwpts.close()

# Create scenario file to draw line segments
# tbars = {'NIRSI': [['GAL01', 'NIRSI'],
#                    ['GAL02', 'NIRSI'],
#                    ['AM603', 'NIRSI'],
#                    ['NIRSI', 'AM607'],
#                    ['AM607', 'AM608'],
#                    ['AM608', 'AM621']],
#          'SOKS2': [['GAL03', 'SOKS2'],
#                    ['GAL04', 'SOKS2'],
#                    ['GAL05', 'SOKS2'],
#                    ['SOKS2', 'AM613'],
#                    ['AM613', 'AM614'],
#                    ['AM614', 'AM609']],
#          'GALIS': [['GAL08', 'GALIS'],
#                    ['GAL09', 'GALIS'],
#                    ['GAL10', 'GALIS'],
#                    ['GALIS', 'GAL07'],
#                    ['GAL07', 'GAL06'],
#                    ['GAL06', 'AM608'],
#                    ['AM608', 'AM621']]}

# for tbar in tbars.keys():
#     fcre = open("C:\\Users\\LVNL_ILAB3\PycharmProjects\\bluesky\\scenario\\T-bar\\"+tbar+".scn", "w")
#     fdel = open("C:\\Users\\LVNL_ILAB3\PycharmProjects\\bluesky\\scenario\\T-bar\\del_"+tbar+".scn", "w")
#
#     for i in range(len(tbars[tbar])):
#         pos0 = tbars[tbar][i][0]
#         pos1 = tbars[tbar][i][1]
#         wptlatlon = wptdata['LatLon']
#         fcre.write("00:00:00.00>LINE "+tbar+"_"+str(i)+" "+wptlatlon.loc[pos0]+" "+wptlatlon.loc[pos1]+"\n")
#         fdel.write("00:00:00.00>DEL "+tbar+"_"+str(i)+"\n")
#
#     fcre.close()
#     fdel.close()

