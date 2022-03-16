try:
    from PyQt5.QtCore import QTimer
except ImportError:
    from PyQt6.QtCore import QTimer

from bluesky.ui.qtgl.guiclient import GuiClient


class ATCOClient(GuiClient):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

        self.subscribe(b'SIMINFO')
        self.subscribe(b'ACDATA')

    def event(self, name, data, sender_id):
        ''' Overridden event function. '''
        pass

    def echo(self, text, flags=None, sender_id=None):
        ''' Overload Client's echo function. '''
        print('ECHO:', text)

    def actnode_changed(self, newact):
        pass

    def stream(self, name, data, sender_id):
        pass
