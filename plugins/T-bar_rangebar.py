""" Show the DTG of all a/c in a horizontal bar """

import numpy as np
import bluesky as bs
from bluesky import settings, stack, core
from bluesky.tools import geo, misc
from bluesky.ui import palette
from bluesky.ui.qtgl import glhelpers as glh
from bluesky.ui.qtgl import console
from bluesky.ui.qtgl.gltraffic import Traffic, leading_zeros

settings.set_variable_defaults(
    text_size=13,
    ac_size=16,
    asas_vmin=200.0,
    asas_vmax=500.0
)

palette.set_default_colours(
    aircraft=(0, 255, 0),
    conflict=(255, 160, 0),
    route=(255, 0, 255),
    trails=(0, 255, 255)
)

MAX_NAIRCRAFT       = 10000
MAX_NCONFLICTS      = 25000
MAX_ROUTE_LENGTH    = 500
ROUTE_SIZE          = 500
TRAILS_SIZE         = 1000000

### Initialization function of the plugin
def init_plugin():
    ''' Plugin initialisation function. '''

    dtg = tbar_ac()

    # Configuration parameters
    config = {
        # The name of your plugin
        'plugin_name':     'RANGEBAR',

        # The type of this plugin. For now, only simulation plugins are possible.
        'plugin_type':     'gui',
        }

    # init_plugin() should always return a configuration dict.
    return config


'''
Classes
'''


# class TBar_rangebar(glh.RenderObject, layer=100): # core.Entity):
#     """
#     Definition: Class used to initialize and update DTG to horizontal T-Bar range indicator
#     Methods:
#         showdtg():      Initialize the DTG label
#         update_tbar():  Update T-Bar graphics
#     """
#     print('plugin started!!')
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.initialized = False
#         self.show_range_bar = False
#
#         # --------------- Label position ---------------
#         self.id_prev = []
#         self.labelpos = np.array([], dtype=np.float32)
#         self.leaderlinepos = np.array([], dtype=np.float32)
#         bs.Signal('labelpos').connect(self.update_labelpos)
#
#         # ----------------- Label data -------------------
#         self.range_bar_lbl = glh.GLBuffer()
#         self.tbar_lbloffset = glh.GLBuffer()
#
#         # ---------------- Aircraft data ----------------
#         self.dtg = glh.GLBuffer()
#         self.lon = glh.GLBuffer()
#         self.color = glh.GLBuffer()
#
#         # --------------- Aircraft objects ---------------
#         self.ac_symbol_tbar = glh.VertexArrayObject(glh.gl.GL_LINE_LOOP)
#
#         # --------------- Label objects ---------------
#         self.aclabels_tbar = glh.Text(settings.text_size, (8, 1))
#         self.leaderlines = glh.Line()
#
#         # Set update function
#         bs.net.actnodedata_changed.connect(self.update_tbar)
#
#     @stack.command(name='RANGEBAR',)
#     def create_range_bar(self):
#         """
#         Function: Initialize the DTG BAR
#         Args: -
#         Returns: -
#
#         Created by: Mitchell de Keijzer
#         Date: 17-03-2022
#         """
#
#         print('command doet het')
#         ac_size = settings.ac_size
#         text_size = settings.text_size
#         if not self.initialized:
#
#
#             # ---------------- Aircraft data ----------------
#             self.dtg.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
#             self.lon.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
#             self.color.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
#
#             # ----------------- Label data -------------------
#             self.range_bar_lbl.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
#             self.tbar_lbloffset.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
#
#             # --------------- Aircraft symbols ---------------
#             acverticeslvnl = np.array([(-0.5 * ac_size, -0.5 * ac_size),
#                                        (0.5 * ac_size, 0.5 * ac_size),
#                                        (0.5 * ac_size, -0.5 * ac_size),
#                                        (-0.5 * ac_size, 0.5 * ac_size),
#                                        (-0.5 * ac_size, -0.5 * ac_size),
#                                        (0.5 * ac_size, -0.5 * ac_size),
#                                        (0.5 * ac_size, 0.5 * ac_size),
#                                        (-0.5 * ac_size, 0.5 * ac_size)],
#                                       dtype=np.float32)  # a square
#
#             self.ac_symbol_tbar.create(vertex=acverticeslvnl)
#             self.ac_symbol_tbar.set_attribs(lat=51.57070200000000, lon=self.lon, color=self.color, instance_divisor=1)
#
#             # --------------- Aircraft labels ---------------
#             self.aclabels_tbar.create(self.range_bar_lbl, 51.57070200000000, self.lon, self.color,
#                                       self.tbar_lbloffset, instanced=True)
#
#             # --------------- Leader lines ---------------
#             self.leaderlines.create(vertex=MAX_NAIRCRAFT * 4, lat=MAX_NAIRCRAFT * 4, lon=MAX_NAIRCRAFT * 4,
#                                     color=MAX_NAIRCRAFT * 4)
#
#             self.initialized = True
#         else:
#             self.show_range_bar = not self.show_range_bar
#
#         # # Check if we need to initialize
#         # if not self.initialized:
#         #     # Get current node data
#         #     actdata = bs.net.get_nodedata()
#         #
#         #     # Class to access Traffic graphics
#         #     self.range_bar = Traffic()
#         #
#         #     # Initialize plugin label
#         #     self.range_bar.plugin_init(blocksize=(3, 1), position=(2, 7))
#         #
#         #     # Update label with current data
#         #     rawlabel = ''
#         #     for idx in range(len(actdata.acdata.id)):
#         #         rawlabel += 3*' '
#         #
#         #     self.tbarlbl.pluginlbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
#         #
#         #     # Initialization completed
#         #     self.initialized = True
#         # else:
#         #     self.tbarlbl.show_pluginlabel = not self.tbarlbl.show_pluginlabel
#
#     def draw_tbar(self):
#         actdata = bs.net.get_nodedata()
#         if actdata.naircraft == 0 or not actdata.show_traf:
#             return
#
#         # Draw ac symbols on t-bar
#         if self.ac_symbol_tbar is not None and self.show_range_bar:
#             self.ac_symbol_tbar.draw(n_instances=actdata.naircraft)
#
#         # Draw t-bar labels
#         if self.aclabels_tbar is not None and self.show_range_bar:
#             if actdata.show_lbl >= 1:
#                 self.aclabels_tbar.draw(n_instances=actdata.naircraft)
#
#         if self.leaderlines is not None and self.show_range_bar:
#             self.leaderlines.draw()
#
#     def update_tbar(self, nodeid, nodedata, changed_elems):
#         """
#         Function: Update T-Bar graphics
#         Args:
#             nodeid:         Node identifier []
#             nodedata:       Node data [class]
#             changed_elems:  Changed elements [list]
#         Returns: -
#
#         Created by: Bob van Dillen
#         Date: 25-2-2022
#         """
#
#         if self.initialized:
#             if 'ACDATA' in changed_elems:
#                 self.glsurface.makeCurrent()
#                 actdata = bs.net.get_nodedata()
#                 data = nodedata.acdata
#                 naircraft = len(data.lat)
#
#                 lat, lon = geo.kwikpos(51.57070200000000, 2.25580600000000, 90, self.dtg)
#                 self.lon.update(np.array(lon, dtype=np.float32))
#                 self.dtg.update(np.array(data.dtg, dtype=np.float32))
#
#                 # Update DTG label
#                 rawlabel = ''
#                 if data.id != self.id_prev:
#                     idchange = True
#                     idcreate = np.setdiff1d(data.id, self.id_prev).tolist()
#                 else:
#                     idchange = False
#                     idcreate = []
#
#                 labelpos = np.empty((min(naircraft, MAX_NAIRCRAFT), 2), dtype=np.float32)
#                 leaderlinepos = np.empty((min(naircraft, MAX_NAIRCRAFT), 4), dtype=np.float32)
#
#                 color = np.empty((min(naircraft, MAX_NAIRCRAFT), 4), dtype=np.uint8)
#
#                 selssd = np.zeros(naircraft, dtype=np.uint8)
#                 confidx = 0
#
#                 zdata = zip(data.gs, data.id, data.inconf, data.ingroup, data.lat, data.lon, data.tcpamax, data.trk)
#                 for i, (gs, acid, inconf, ingroup, lat, lon, tcpa, trk) in enumerate(zdata):
#                     # Check for maximum aircraft
#                     if i >= MAX_NAIRCRAFT:
#                         break
#                         # Labels
#                     rawlabel += baselabel(actdata, data, i)
#
#                     # Label position
#                     if idchange:
#                         if acid in idcreate:
#                             labelpos[i] = [50, 0]
#                             leaderlinepos[i] = leaderline_vertices(actdata, 50, 0)
#                         else:
#                             i_prev = self.id_prev.index(acid)
#                             labelpos[i] = self.labelpos[i_prev]
#                             if data.tracklbl[i]:
#                                 leaderlinepos[i] = leaderline_vertices(actdata, labelpos[i][0], labelpos[i][1])
#                             else:
#                                 leaderlinepos[i] = [0, 0, 0, 0]
#                     else:
#                         labelpos[i] = self.labelpos[i]
#                         if data.tracklbl[i]:
#                             leaderlinepos[i] = leaderline_vertices(actdata, labelpos[i][0], labelpos[i][1])
#                         else:
#                             leaderlinepos[i] = [0, 0, 0, 0]
#
#                     # # colours
#                     # if inconf:
#                     #     if actdata.ssd_conflicts:
#                     #         selssd[i] = 255
#                     #     color[i, :] = palette.conflict + (255,)
#                     #     lat1, lon1 = geo.qdrpos(lat, lon, trk, tcpa * gs / nm)
#                     #     cpalines[4 * confidx: 4 * confidx +
#                     #                           4] = [lat, lon, lat1, lon1]
#                     #     confidx += 1
#
#                 self.range_bar_lbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
#
#                 # Label position
#                 self.labelpos = labelpos
#                 self.id_prev = data.id
#                 self.tbar_lbloffset.update(np.array(self.labelpos, dtype=np.float32))
#
#                 self.leaderlinepos = leaderlinepos
#                 self.leaderlines.update(vertex=self.leaderlinepos, lat=data.lat, lon=data.lon, color=color)
#
#                 # for idx in range(len(nodedata.acdata.id)):
#                 #     acid = nodedata.acdata.id[idx]
#                 #     dtg = nodedata.acdata.dtg[idx]
#                 #     tracklbl = nodedata.acdata.tracklbl[idx]
#                 #     if tracklbl and self.dtg != 0. and acid == console.Console._instance.id_select:
#                 #         rawlabel += '%-8s' % leading_zeros(acid)[:8]
#                 #     else:
#                 #         rawlabel += 8*' '
#                 # self.tbarlbl.pluginlbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
#
#     def update_labelpos(self, x, y):
#         """
#         Function: Update the label position for the selected aircraft
#         Args:
#             x:  Cursor x pixel coordinate
#             y:  Cursor y pixel coordinate
#         Returns: -
#
#         Created by: Bob van Dillen
#         Date: 22-2-2022
#         """
#
#         # Sizes
#         ac_size = settings.ac_size
#         text_size = settings.text_size
#         text_width = text_size
#         text_height = text_size * 1.2307692307692308
#         block_size = (4*text_height, 8*text_width)
#
#         # Node data
#         actdata = bs.net.get_nodedata()
#
#         # Get index selected aircraft
#         idx = misc.get_indices(actdata.acdata.id, console.Console._instance.id_select)
#
#         # Check if selected aircraft exists
#         if len(idx) != 0 and actdata.acdata.tracklbl[idx]:
#             idx = idx[0]
#
#             # Get cursor position change
#             dx = x - self.glsurface.prevmousepos[0]
#             dy = y - self.glsurface.prevmousepos[1]
#
#             # Add cursor position change to label position
#             self.labelpos[idx][0] += dx
#             self.labelpos[idx][1] -= dy
#
#             # Update label offset
#             self.tbar_lbloffset.update(np.array(self.labelpos, dtype=np.float32))
#
#             # Leader lines
#             self.leaderlinepos[idx] = leaderline_vertices(actdata, self.labelpos[idx][0], self.labelpos[idx][1])
#
#             self.leaderlines.update(vertex=self.leaderlinepos)
#
# def baselabel(actdata, data, i):
#     """
#     Function: Create base label
#     Args:
#         actdata:    node data [class]
#         data:       aircraft data [class]
#         i:          index for data [int]
#     Returns:
#         rawlabel:   label string [str]
#
#     Created by: Bob van Dillen
#     Date: 13-1-2022
#     """
#
#     # Empty label
#     label = ''
#     label += '%-8s' % data.id[i][:8]
#
#     return label
#
#
# def leaderline_vertices(actdata, offsetx, offsety):
#     """
#     Function: Compute the vertices for the leader line
#     Args:
#         actdata:    node data [class]
#         offsetx:    label offset x pixel coordinates [int]
#         offsety:    label offset y pixel coordinates [int]
#     Returns: -
#
#     Created by: Bob van Dillen
#     Date: 23-2-2022
#     """
#
#     # Sizes
#     ac_size = settings.ac_size
#     text_size = settings.text_size
#     text_width = text_size
#     text_height = text_size * 1.2307692307692308
#
#     block_size = (1*text_height, 8*text_width)
#
#     # Compute the angle
#     angle = np.arctan2(offsety, offsetx)
#
#     # Label is on top of aircaft symbol
#     if -block_size[1] <= offsetx <= 0 and -text_height <= offsety <= 3*text_height:
#         vertices = [0, 0, 0, 0]
#     # Label is to the right of the aircraft symbol
#     elif offsetx >= 0:
#         vertices = [ac_size*np.cos(angle), ac_size*np.sin(angle), offsetx, offsety]
#     # Label is above the aircraft symbol
#     elif offsetx >= -block_size[1] and offsety >= 0:
#         vertices = [ac_size*np.cos(angle), ac_size*np.sin(angle), offsetx+0.5*block_size[1], offsety-3*text_height]
#     # Label is below the aircraft symbol
#     elif offsetx >= -block_size[1] and offsety <= 0:
#         vertices = [ac_size*np.cos(angle), ac_size*np.sin(angle), offsetx+0.5*block_size[1], offsety+text_height]
#     # Label is to the left of the aircraft sym
#     elif offsetx < 0:
#         vertices = [ac_size*np.cos(angle), ac_size*np.sin(angle), offsetx+block_size[1], offsety]
#     # For safety every other situation
#     else:
#         vertices = [0, 0, 0, 0]
#
#     return vertices





class tbar_ac(core.Entity):

    def __init__(self):
        super().__init__()
        self.initialized = False
        self.tbar_ac = None

        bs.net.actnodedata_changed.connect(self.update_tbar_ac)

    @stack.command(name='RANGEBAR')
    def show_rangebar(self):
        if not self.initialized:
            # Get current node data
            actdata = bs.net.get_nodedata()
            # print('actdata', actdata)
            # Class to access Traffic graphics
            self.tbar_ac = Traffic()
            # Initialize plugin t-bar aircraft and label
            self.tbar_ac.tbarrange(blocksize=(8, 1), position=(0, 0))
            print('Komt hier wel langs')
            rawlabel = ''
            for idx in range(len(actdata.acdata.id)):
                rawlabel += 8*' '
            # print('rawlabel', rawlabel)
            self.tbar_ac.tbar_lbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))

            self.initialized = True
            # print('Initialized:', self.initialized)
        else:
            self.tbar_ac.show_tbar_ac = not self.tbar_ac.show_tbar_ac

    def update_tbar_ac(self, nodeid, nodedata, changed_elems):
        if self.initialized:
            if 'ACDATA' in changed_elems:
                rawlabel = ''
                lon = []
                lat = []

                for idx in range(len(nodedata.acdata.id)):
                    acid = nodedata.acdata.id[idx]
                    dtg = nodedata.acdata.dtg[idx]

                    if dtg > 60:
                        latd = None
                        lond = None
                        rawlabel += 8*' '
                    else:
                        latd, lond = geo.kwikpos(51.57070200000000, 2.25580600000000, 90, dtg)
                        rawlabel += '%-8s' % acid[:8]
                    lon.append(lond)
                    lat.append(latd)
                print('rawlabel', rawlabel)

                self.tbar_ac.tbar_lbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
                self.tbar_ac.tbar_lon.update(np.array(lon, dtype=np.float32))
                self.tbar_ac.tbar_lat.update(np.array(lat, dtype=np.float32))
