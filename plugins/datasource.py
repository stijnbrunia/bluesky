""" Feed aircraft states data to simulation from data source """

import os
import numpy as np
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
        reset():            Reset variables
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

    def reset(self):
        """
        Function: Reset variables
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        super().reset()

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

        # --------------- Check inputs ---------------
        # Data type
        if datatype.upper() not in ['VEMMIS']:
            return False, 'REPLAY: Data type not supported'
        # Folder
        datapath = os.getcwd() + "\\scenario\\" + folder.lower()
        if not os.path.isdir(datapath):
            return False, 'REPLAY: Folder does not exist'
        # Files
        if not files_check(datatype, datapath):
            return False, 'REPLAY: The folder does not contain all the required files'

        # --------------- Access data ---------------
        # Get data type
        if datatype.upper() == 'VEMMIS':
            self.datasource = vemmisread.VEMMISSource()
        # Get commands data
        commands, commandstime = self.datasource.replay(datapath, time0)
        stack.set_scendata(commandstime, commands)
        # Set replay
        self.swreplay = True

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

        # --------------- Check inputs ---------------
        # Data type
        if datatype.upper() not in ['VEMMIS']:
            return False, 'INITIAL: Data type not supported'
        # Folder
        datapath = os.getcwd() + "\\scenario\\" + folder.lower()
        if not os.path.isdir(datapath):
            return False, 'INITIAL: Folder does not exist'
        # Files
        if not files_check(datatype, datapath):
            return False, 'INITIAL: The folder does not contain all the required files'

        # --------------- Access data ---------------
        # Get data type
        if datatype.upper() == 'VEMMIS':
            self.datasource = vemmisread.VEMMISSource()
        # Get commands data
        commands, commandstime = self.datasource.initial(datapath, time0)
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


"""
Static functions
"""


def files_check(datatype, datapath):
    """
    Function: Check if the folder contains the required files
    Args:
        datatype:   data type [str]
        datapath:   path to the folder [str]
    Returns:
        True/False: True if required files are present, else False [bool]

    Created by: Bob van Dillen
    Date: 14-1-2022
    """

    file_array = np.array([])

    if datatype == 'VEMMIS':
        for root, dirs, files in os.walk(datapath):
            for file in files:
                if file.upper().startswith('FLIGHTS'):
                    file_array = np.append(file_array, 'FLIGHTS')
                elif file.upper().startswith('FLIGHTTIMES'):
                    file_array = np.append(file_array, 'FLIGHTTIMES')
                elif file.upper().startswith('TRACKS'):
                    file_array = np.append(file_array, 'TRACKS')

        if len(file_array) == 3 and len(np.unique(file_array)) == 3:
            return True

    return False
