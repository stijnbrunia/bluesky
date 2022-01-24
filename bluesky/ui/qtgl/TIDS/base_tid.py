import bluesky as bs
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from bluesky.ui.qtgl import console
from bluesky.ui.qtgl.TIDS import *
from bluesky.tools import misc
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
        exec(name+'.'+loop_button+'.setText(dlgbuttons[i][1])')
        if dlgbuttons[i][2] != None:
            # Check for multiple functions
            if isinstance(dlgbuttons[i][2], list):
                for func in dlgbuttons[i][2]:
                    exec(name + '.' + loop_button + '.clicked.connect(' + func + ')')
            else:
                exec(name + '.' + loop_button + '.clicked.connect(' + dlgbuttons[i][2] + ')')
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


def tid_cmds(tidcmd):
    """
    Function: Process commands coming from the TID
    Args:
        tidcmd: command [str]
    Returns: -

    Created by: Bob van Dillen
    Date: 21-1-2022
    """

    # Get simulation data
    actdata = bs.net.get_nodedata()
    id_select = actdata.cmddata.idsel

    # Get command line
    cmdline = console.get_cmdline()

    # Split the command line
    cmdlinelst = cmdline.split(';')
    cmdlst = []
    argslst = []
    # Loop over the command lines
    for line in cmdlinelst:
        # Get command and arguments
        cmd, args = misc.cmdsplit(line, actdata.acdata.id)
        cmdlst.append(cmd)
        argslst.append(args)

    # Commands that need more than 1 input
    if cmdlst[-1].upper() in ['HDG', 'ALT', 'SPD', 'SSRLABEL']:
        if len(argslst[-1]) > 1:
            # Altitude command
            if tidcmd.upper() == 'ALT':
                cmdline += ' ; ' + id_select + ' ' + tidcmd + ' FL'
            # Other commands
            else:
                cmdline += ' ; ' + id_select + ' ' + tidcmd + ' '
        # Leave out last command
        else:
            cmdline = ''
            for i in range(len(cmdlinelst)-1):
                cmdline += cmdlinelst[i] + ' ; '
            cmdline += id_select + ' ' + tidcmd + ' '

    # Commands that only need 1 input
    elif len(argslst[-1]) > 0:
        # Altitude command
        if tidcmd.upper() == 'ALT':
            cmdline += ' ; ' + id_select + ' ' + tidcmd + ' FL'
        # Other commands
        else:
            cmdline += ' ; ' + id_select + ' ' + tidcmd + ' '

    # Leave out last command
    else:
        cmdline = ''
        for i in range(len(cmdlinelst) - 1):
            cmdline += cmdlinelst[i] + ' ; '
        cmdline += id_select + ' ' + tidcmd + ' '

    # Set the command line
    console.Console._instance.set_cmdline(cmdline)
