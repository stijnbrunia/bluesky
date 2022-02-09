import os

files = []

path = os.path.expanduser("~") + "/PycharmProjects/bluesky/scenario/LVNL/Maps/mapid/"
for file in files:
    f = open(path+file, 'r')
    lines = f.readlines()
    f.close()

    f = open(path+file, 'w')
    for line in lines:
        f.write(line)
        line = line.split('>')
        cmds = line[1].split(' ')
        name = cmds[1].strip()
        f.write('0:00:00.00>COLOR '+name+' 80,200,80\n')

    f.close()
