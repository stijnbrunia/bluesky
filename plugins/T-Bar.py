""" Add the DTG to the label for the T-Bar concept """

import numpy as np
import bluesky as bs
from bluesky.ui.qtgl.gltraffic import Traffic
from bluesky import core, stack


def init_plugin():
    ''' Plugin initialisation function. '''

    commands = Commands()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'TBAR',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'gui',
        }

    # init_plugin() should always return a configuration dict.
    return config


class Commands(core.Entity):
    def __init__(self):
        super().__init__()
        self.initialized = False
        self.tbarlbl = None
        self.lbloffset = []

    @stack.command(name='SHOWDTG',)
    def showdtg(self):
        if not self.initialized:
            self.tbarlbl = TBarLabel()
            self.tbarlbl.plugin_init((4, 1))
            #actdata = bs.net.no
            bs.net.actnodedata_changed.connect(self.updatedtg)
            print('init finished')

    def updatedtg(self, nodeid, nodedata, changed_elems):
        if 'ACDATA' in changed_elems:
            rawlabel = ''
            for idx in range(len(nodedata.acdata.id)):
                rawlabel += '1234'
            self.tbarlbl.pluginlbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
            print('update')


class TBarLabel(Traffic):
    def __init__(self):
        super(TBarLabel, self).__init__()

