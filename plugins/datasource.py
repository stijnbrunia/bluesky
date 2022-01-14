""" Feed aircraft states data to simulation from data source """

import bluesky as bs
from bluesky import core, stack
from bluesky.tools import vemmisread

### Initialization function of the plugin
def init_plugin():
    ''' Plugin initialisation function. '''
    # Instantiate class
    datasource = DataSource()

    # Configuration parameters
    config = {
        # The name of the plugin
        'plugin_name':     'DATASOURCE',

        # The type of the plugin
        'plugin_type':     'sim',
        }

    return config


"""
Classes
"""


class DataSource(core.Entity):
    """
    Class definition: Take data from data source and feed to simulation
    Methods:
        setreplay():        Replay scenario from data source
        setinitial():       Take initial aircraft positions from data source
        update_trackdata(): Update the track data for the current simulation time

    Created by: Bob van Dillen
    Date: 14-1-2022
    """
    def __init__(self):
        super().__init__()

        self.swreplay = False

        self.datasource = None

    @stack.command(name='REPLAY', brief='REPLAY DATATYPE FOLDER (TIME [HH:MM:SS])')
    def setreplay(self, datatype: str, folder: str, time0: str = ''):
        """
        Function: Replay scenario from data source
        Args:
            datatype:   data type [str]
            folder:     folder name [str]
            time0:      start time [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        self.swreplay = True

        if datatype.upper() == 'VEMMIS':
            self.datasource = vemmisread.VEMMISSource()

        commands, commandstime = self.datasource.replay(folder, time0)
        stack.set_scendata(commandstime, commands)

    @stack.command(name='INITIAL', brief='INITIAL DATATYPE FOLDER (TIME [HH:MM:SS])')
    def setinitial(self, datatype: str, folder: str, time0: str = ''):
        """
        Function: Take initial aircraft positions from data source
        Args:
            datatype:   data type [str]
            folder:     folder name [str]
            time0:      start time [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        if datatype.upper() == 'VEMMIS':
            self.datasource = vemmisread.VEMMISSource()

        commands, commandstime = self.datasource.initial(folder, time0)
        stack.set_scendata(commandstime, commands)

    @core.timed_function(name='datafeed', dt=0.5)
    def update_trackdata(self):
        """
        Function: Update the track data for the current simulation time
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        if not self.swreplay:
            return

        ids, lat, lon, hdg, alt, gs = self.datasource.update_trackdata(bs.sim.simt)

        trackdata = {'id': ids,
                     'lat': lat,
                     'lon': lon,
                     'hdg': hdg,
                     'alt': alt,
                     'gs': gs}

        bs.traf.trafdatafeed.trackdata = trackdata
