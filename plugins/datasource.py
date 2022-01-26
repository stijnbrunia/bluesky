""" Feed aircraft states data to simulation from data source """

import os
import numpy as np
import bluesky as bs
from bluesky import core, stack
from bluesky.tools import livetraffic, misc, vemmisread
from bluesky.stack import simstack

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
        setlive():          Load live data into BlueSky
        setinitial():       Take initial aircraft positions from data source
        update_trackdata(): Update the track data for the current simulation time

    Created by: Bob van Dillen
    Date: 14-1-2022
    """

    def __init__(self):
        super().__init__()

        self.swreplay = False
        self.swlive = False
        self.swinitial = False
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
        self.swlive = False
        self.swinitial = False
        self.datasource = None

    @stack.command(name='REPLAY', brief='REPLAY DATATYPE FOLDER (DATE [dd-mm-yyyy] TIME [HH:MM:SS])')
    def setreplay(self, datatype: 'txt', folder: 'txt', date0: 'txt' = '', time0: 'txt' = ''):
        """
        Function: Replay scenario from data source
        Args:
            datatype:   data type [str]
            folder:     folder name [str]
            date0:      start date [str]
            time0:      start time [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        # --------------- Check inputs ---------------
        # Modes
        if self.swreplay:
            return False, 'REPLAY: Already in REPLAY mode'
        if self.swlive:
            return False, 'REPLAY: Already in LIVE mode'
        if self.swinitial:
            return False, 'REPLAY: Already in INITIAL mode'

        # Data type
        if datatype.upper() not in ['VEMMIS']:
            return False, 'REPLAY: Data type not supported'

        # Other inputs
        succes, message = check_inputs(folder=folder, date=date0, time=time0)
        if not succes:
            return False, 'REPLAY: ' + message

        # Files
        datapath = os.getcwd() + "\\scenario\\" + folder.lower()
        if not files_check(datatype, datapath):
            return False, 'REPLAY: The folder does not contain all the required files'

        # --------------- Access data ---------------
        # Get data type
        if datatype.upper() == 'VEMMIS':
            self.datasource = vemmisread.VEMMISSource()

        # Get commands data
        commands, commandstime = self.datasource.replay(datapath, date0, time0)
        simstack.stack_commands(commandstime, commands)

        # Set replay
        self.swreplay = True

    @stack.command(name='LIVE', brief='LIVE DATATYPE')
    def setlive(self, datatype: str):
        """
        Function: Load live data into BlueSky
        Args:
            datatype:   data type [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 15-1-2022
        """

        # --------------- Check inputs ---------------
        # Modes
        if self.swreplay:
            return False, 'LIVE: Already in REPLAY mode'
        if self.swlive:
            return False, 'LIVE: Already in LIVE mode'
        if self.swinitial:
            return False, 'LIVE: Already in INITIAL mode'

        # Data type
        if datatype.upper() not in ['OPENSKY']:
            return False, 'LIVE: Data type not supported'

        # --------------- Access data ---------------
        # Get data type
        if datatype.upper() == 'OPENSKY':
            self.datasource = livetraffic.OpenSkySource()

        # Get commands data
        commands, commandstime = self.datasource.live()
        simstack.stack_commands(commandstime, commands)

        # Set live
        self.swlive = True

    @stack.command(name='INITIAL', brief='INITIAL DATATYPE FOLDER (DATE [dd-mm-yyyy] TIME [HH:MM:SS])')
    def setinitial(self, datatype: str, folder: str = '', date0: str = '', time0: str = ''):
        """
        Function: Take initial aircraft positions from data source
        Args:
            datatype:   data type [str]
            folder:     folder name [str]
            date0:      start date [str]
            time0:      start time [str]
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        # --------------- Check inputs ---------------
        # Modes
        if self.swreplay:
            return False, 'INITIAL: Already in REPLAY mode'
        if self.swlive:
            return False, 'INITIAL: Already in LIVE mode'
        if self.swinitial:
            return False, 'INITIAL: Already in INITIAL mode'

        # Data type
        if datatype.upper() not in ['VEMMIS', 'OPENSKY']:
            return False, 'INITIAL: Data type not supported'

        # Other inputs
        datapath = os.getcwd() + "\\scenario\\" + folder.lower()
        if datatype.upper() not in ['OPENSKY']:
            succes, message = check_inputs(folder=folder, date=date0, time=time0)
            if not succes:
                return False, 'INITIAL: ' + message

            # Files
            if not files_check(datatype, datapath):
                return False, 'INITIAL: The folder does not contain all the required files'

        # --------------- Access data ---------------
        # Get data type
        if datatype.upper() == 'VEMMIS':
            self.datasource = vemmisread.VEMMISSource()
        elif datatype.upper() == 'OPENSKY':
            self.datasource = livetraffic.OpenSkySource()

        # Get commands data
        commands, commandstime = self.datasource.initial(datapath, date0, time0)
        simstack.stack_commands(commandstime, commands)

        # Set initial
        self.swinitial = True

    @core.timed_function(name='datafeed', dt=0.5)
    def update_trackdata(self):
        """
        Function: Update the track data for the current simulation time
        Args: -
        Returns: -

        Created by: Bob van Dillen
        Date: 14-1-2022
        """

        # Check if update is needed
        if not self.swreplay and not self.swlive:
            return

        # Get data
        cmds, ids, lat, lon, hdg, alt, gs = self.datasource.update_trackdata(bs.sim.simt)

        # Create track data
        trackdata = {'id': ids,
                     'lat': lat,
                     'lon': lon,
                     'hdg': hdg,
                     'alt': alt,
                     'gs': gs}

        # Send trackdata
        bs.traf.trafdatafeed.trackdata = trackdata

        # Stack commands
        for cmd in cmds:
            bs.stack.stack(cmd)


"""
Static functions
"""


def check_inputs(folder=None, date=None, time=None):
    """
    Function: Check if inputs are valid
    Args:
        folder:     folder input [str]
        date:       date [str]
        time:       time [str]
    Returns:
        True/False: Inputs are correct/incorrect [bool]
        string:     Message [str]

    Created by: Bob van Dillen
    Date: 26-1-2022
    """

    # Check folder input
    if folder:
        datapath = os.getcwd() + "\\scenario\\" + folder.lower()
        if not os.path.isdir(datapath):
            return False, 'Folder does not exist'

    # Check date input
    if date:
        date = date.split('-')
        if len(date) != 3:
            return False, 'Invalid date'
        for item in date:
            if not item.isnumeric():
                return False, 'Invalid date'

    # Check time input
    if time:
        time = time.split(':')
        if len(time) != 3:
            return False, 'Invalid time'
        for item in time:
            if not item.isnumeric():
                return False, 'Invalid time'

    return True, ''


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

    if datatype.upper() == 'VEMMIS':
        for root, dirs, files in os.walk(datapath):
            for file in files:
                if file.upper().startswith('FLIGHTS'):
                    file_array = np.append(file_array, 'FLIGHTS')
                elif file.upper().startswith('FLIGHTTIMES'):
                    file_array = np.append(file_array, 'FLIGHTTIMES')
                elif file.upper().startswith('TRACK'):
                    file_array = np.append(file_array, 'TRACK')

        if len(file_array) == 3 and len(np.unique(file_array)) == 3:
            return True

    return False
