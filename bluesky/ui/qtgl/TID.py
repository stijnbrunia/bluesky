from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QDialog

from PyQt5 import uic


class showTID(QDialog):
    def __init__(self):
        super().__init__()

    def setbuttons(self, tid):
        uic.loadUi('C:/Users/LVNL_ILAB3/Desktop/bluesky-lvnl_2/bluesky-master2/data/graphics/TID_Base.ui', self)
        tid_load = 'bs.ui.qtgl.TID_layouts.' + tid
        dlgbuttons = eval(tid_load)

        for i in range(len(dlgbuttons)):
            loop_button = 'pushButton_' + str(dlgbuttons[i][0])
            exec('self.' + loop_button + '.setText(str(dlgbuttons[i][1]))')
            if dlgbuttons[i][2] != None:
                for func in dlgbuttons[i][2].split('|'):
                    exec('self.' + loop_button + '.clicked.connect(' + func + ')')
            else:
                exec('self.' + loop_button + '.setStyleSheet("border: 0px solid red;")')

        self.setWindowTitle(str(tid))

    def show(self):
        self.setWindowModality(Qt.WindowModal)
        self.showMaximized()
        self.exec()
