import os
import re
import geo

# files = ['28.scn', '40.scn', '35.scn', '21.scn', '38.scn', '26.scn', '42.scn', '31.scn', '23.scn', '33.scn', '18.scn']
# pfiles = ['210.scn', '211.scn', '212.scn', '213.scn', '214.scn', '215.scn', '216.scn', '217.scn', '218.scn', '219.scn', '220.scn']
files = ['71.scn', '72.scn', '73.scn', '74.scn', '75.scn', '76.scn']
pfiles = ['238.scn', '239.scn', '240.scn', '241.scn', '242.scn', '243.scn']
dist = [2., 4., 6., 8.]

path = os.path.expanduser("~") + "\\PycharmProjects\\bluesky\\scenario\\LVNL\\Maps\\mapid\\"
i = 0
for file in files:
    f = open(path+file, 'r')
    pf = open(path+pfiles[i], 'w')
    delpf = open(path+'del_'+pfiles[i], 'w')
    for line in f.readlines():
        if line[0] == '0':
            line = line.strip('\n')
            cmd = line.split('>')[1]
            cmd = re.split(',| ', cmd)

            if cmd[1][-1] == '1':
                lat0 = float(cmd[2])
                lon0 = float(cmd[3])
                lat1 = float(cmd[4])
                lon1 = float(cmd[5])

                qdr, d = geo.qdrdist(lat0, lon0, lat1, lon1)

                j = 1
                pf.write("0:00:00.00>POINT POINT"+pfiles[i].strip('.scn')+"_"+str(j)+" "+str(lat0)+","+str(lon0)+"\n")
                delpf.write("0:00:00.00>DEL POINT"+pfiles[i].strip('.scn')+"_"+str(j)+"\n")
                j += 1
                for d in dist:
                    lati, loni = geo.qdrpos(lat0, lon0, qdr, d)
                    pf.write("0:00:00.00>POINT POINT"+pfiles[i].strip('.scn')+"_"+str(j)+" "+str(lati)+","+str(loni)+"\n")
                    delpf.write("0:00:00.00>DEL POINT"+pfiles[i].strip('.scn')+"_"+str(j)+"\n")
                    j += 1
                pf.write("0:00:00.00>POINT POINT"+pfiles[i].strip('.scn')+"_"+str(j)+" "+str(lat1)+","+str(lon1)+"\n")
                delpf.write("0:00:00.00>DEL POINT"+pfiles[i].strip('.scn')+"_"+str(j)+"\n")
            else:
                lat0 = float(cmd[2])
                lon0 = float(cmd[3])
                lat1 = float(cmd[4])
                lon1 = float(cmd[5])

                pf.write("0:00:00.00>POINT POINT"+pfiles[i].strip('.scn')+"_7 "+str(lat0)+","+str(lon0)+"\n")
                delpf.write("0:00:00.00>DEL POINT"+pfiles[i].strip('.scn')+"_7\n")
                pf.write("0:00:00.00>POINT POINT"+pfiles[i].strip('.scn')+"_8 "+str(lat1)+","+str(lon1)+"\n")
                delpf.write("0:00:00.00>DEL POINT"+pfiles[i].strip('.scn')+"_8\n")
    f.close()
    pf.close()
    delpf.close()

    i += 1
