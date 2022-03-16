'''
    AAA ATCo Interface Client for BlueSky
'''
try:
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
except ImportError:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit

import bluesky as bs
bs.init('client')
from bluesky.ui.qtgl.mainwindow import DiscoveryDialog

from atcoclient import ATCOClient
from radarwidget import RadarWidget





class Echobox(QTextEdit):
    ''' Text box to show echoed text coming from BlueSky. '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(150)
        self.setReadOnly(True)
        # self.setFocusPolicy(Qt.NoFocus)

    def echo(self, text, flags=None):
        ''' Add text to this echo box. '''
        self.append(text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class Cmdline(QTextEdit):
    ''' Wrapper class for the command line. '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(21)
        # self.setFocusPolicy(Qt.StrongFocus)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def keyPressEvent(self, event):
        ''' Handle Enter keypress to send a command to BlueSky. '''
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if bsclient is not None:
                bsclient.stack(self.toPlainText())
            self.setText('')
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    bs.init('client')

    print('gui type:', bs.gui_type)

    # Construct the Qt main object
    app = QApplication([])



    # Create a window with a stack text box and a command line
    win = QWidget()
    win.setWindowTitle('Example external client for BlueSky')
    layout = QVBoxLayout()
    win.setLayout(layout)

    # Create and start BlueSky client
    bsclient = ATCOClient()
    # bsclient.connect(event_port=11000, stream_port=11001)
    dialog = DiscoveryDialog(win)
    dialog.show()
    bs.net.start_discovery()

    radarwidget = RadarWidget(win)
    # echobox = Echobox(win)
    cmdline = Cmdline(win)
    layout.addWidget(radarwidget)
    # layout.addWidget(echobox)
    layout.addWidget(cmdline)
    
    gltimer = QTimer(win)
    gltimer.timeout.connect(radarwidget.update)
    gltimer.start(50)
    
    # radarwidget.show()
    win.show()

    
    # Start the Qt main loop
    app.exec()