from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QDialog

from PyQt5 import uic

import os

class showTID(QDialog):
    def __init__(self):
        super().__init__()

    def setbuttons(self, tid):
        uic.loadUi(os.path.expanduser("~")+'/PycharmProjects/bluesky/data/graphics/TID_Base.ui', self)
        tid_load = 'bs.ui.qtgl.TID_layouts.' + tid
        dlgbuttons = eval(tid_load)

        for i in range(len(dlgbuttons)):
            loop_button = 'pushButton_' + str(dlgbuttons[i][0])
            exec('self.' + loop_button + '.setText(str(dlgbuttons[i][1]))')
            if dlgbuttons[i][2] != None:
                # Check for multiple functions
                if isinstance(dlgbuttons[i][2], list):
                    for func in dlgbuttons[i][2]:
                        exec('self.' + loop_button + '.clicked.connect(' + func + ')')
                else:
                    exec('self.' + loop_button + '.clicked.connect(' + dlgbuttons[i][2] + ')')
            else:
                exec('self.' + loop_button + '.setStyleSheet("border: 0px solid red;")')

        self.setWindowTitle(str(tid))

    def show(self):
        self.setWindowModality(Qt.WindowModal)
        self.showMaximized()
        self.exec()
