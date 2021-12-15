import bluesky as bs
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from bluesky.ui.qtgl import console
from bluesky.ui.qtgl.TIDS.APP import *
import platform
import os


def show_basetid(name, layout):
    globals()[str(name)] = QDialog()
    uic.loadUi(os.path.join(bs.settings.gfx_path, 'TID_Base.ui'), globals()[str(name)])
#    uic.loadUi('C:/Users/LVNL_ILAB3/Desktop/bluesky-lvnl_2/bluesky-master2/data/graphics/TID_Base.ui', globals()[str(name)])

    tid_load = 'bs.ui.qtgl.TID_layouts.' + layout
    dlgbuttons = eval(tid_load)

    for i in range(len(dlgbuttons)):
        loop_button = 'pushButton_'+str(dlgbuttons[i][0])
        exec(name+'.'+ loop_button+'.setText(dlgbuttons[i][1])')
        if dlgbuttons[i][2] != None:
            for func in dlgbuttons[i][2].split('|'):
                exec(name + '.' + loop_button + '.clicked.connect(' + func + ')')
        else:
            exec(name+'.' + loop_button + '.setStyleSheet("border: 0px solid red;")')

    globals()[str(name)].setWindowTitle("TID")
    globals()[str(name)].setWindowModality(Qt.WindowModal)
    globals()[str(name)].showMaximized()
    globals()[str(name)].setWindowFlag(Qt.WindowMinMaxButtonsHint)
    globals()[str(name)].exec()

# def tidclose(command, dialogname):
def tidclose(command, dialogname):
    lambda: command
    globals()[str(dialogname)].close()
    bs.ui.qtgl.console.Console._instance.stack(bs.ui.qtgl.console.Console._instance.command_line)


def open_map(command, mapid):
    console.Console._instance.stack("MAP "+str(mapid))
    lambda: command
