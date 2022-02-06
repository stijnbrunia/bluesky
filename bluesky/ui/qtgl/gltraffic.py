''' Traffic OpenGL visualisation. '''
import numpy as np
import itertools
from bluesky.ui.qtgl import glhelpers as glh
from bluesky.ui.qtgl import console

import bluesky as bs
from bluesky.tools import geo, misc
from bluesky import settings
from bluesky.ui import palette
from bluesky.tools.aero import ft, nm, kts

# Register settings defaults
settings.set_variable_defaults(
    text_size=13, ac_size=16,
    asas_vmin=200.0, asas_vmax=500.0)

palette.set_default_colours(
    aircraft=(0, 255, 0),
    conflict=(255, 160, 0),
    route=(255, 0, 255),
    trails=(0, 255, 255))

# Static defines
MAX_NAIRCRAFT = 10000
MAX_NCONFLICTS = 25000
MAX_ROUTE_LENGTH = 500
ROUTE_SIZE = 500
TRAILS_SIZE = 1000000


class Traffic(glh.RenderObject, layer=100):
    ''' Traffic OpenGL object. '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initialized = False
        self.route_acid = ''
        self.asas_vmin = settings.asas_vmin
        self.asas_vmax = settings.asas_vmax

        # --------------- Aircraft data ---------------

        self.hdg = glh.GLBuffer()
        self.rpz = glh.GLBuffer()
        self.lat = glh.GLBuffer()
        self.lon = glh.GLBuffer()
        self.alt = glh.GLBuffer()
        self.tas = glh.GLBuffer()
        self.color = glh.GLBuffer()
        self.asasn = glh.GLBuffer()
        self.asase = glh.GLBuffer()
        self.histsymblat = glh.GLBuffer()
        self.histsymblon = glh.GLBuffer()
        self.leadlinelat = glh.GLBuffer()
        self.leadlinelon = glh.GLBuffer()

        # --------------- Label data ---------------

        self.lbl = glh.GLBuffer()
        self.lbl_ll = glh.GLBuffer()
        self.lbl_lc = glh.GLBuffer()
        self.lbl_lr = glh.GLBuffer()
        self.lbl_cl = glh.GLBuffer()
        self.lbl_cr = glh.GLBuffer()
        self.lbl_ul = glh.GLBuffer()
        self.lbl_uc = glh.GLBuffer()
        self.lbl_ur = glh.GLBuffer()
        self.ssrlbl = glh.GLBuffer()
        self.mlbl = glh.GLBuffer()

        # --------------- Aircraft objects ---------------

        self.ssd = glh.VertexArrayObject(glh.gl.GL_POINTS, shader_type='ssd')
        self.protectedzone = glh.Circle()
        self.ac_symbol = glh.VertexArrayObject(glh.gl.GL_TRIANGLE_FAN)
        self.ac_symbollvnl = glh.VertexArrayObject(glh.gl.GL_LINE_LOOP)
        self.hist_symbol = glh.VertexArrayObject(glh.gl.GL_TRIANGLE_FAN)
        self.cpalines = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.route = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.routelbl = glh.Text(settings.text_size, (12, 2))
        self.rwaypoints = glh.VertexArrayObject(glh.gl.GL_LINE_LOOP)
        self.traillines = glh.VertexArrayObject(glh.gl.GL_LINES)

        # --------------- Label objects ---------------

        self.aclabels = glh.Text(settings.text_size, (8, 3))     # BlueSky default (ATC mode BLUESKY)
        self.aclabels_ll = glh.Text(settings.text_size, (8, 4))  # lower-left
        self.aclabels_lc = glh.Text(settings.text_size, (8, 4))  # lower-center
        self.aclabels_lr = glh.Text(settings.text_size, (8, 4))  # lower-right
        self.aclabels_cl = glh.Text(settings.text_size, (8, 4))  # center-left
        self.aclabels_cr = glh.Text(settings.text_size, (8, 4))  # center-right
        self.aclabels_ul = glh.Text(settings.text_size, (8, 4))  # upper-left
        self.aclabels_uc = glh.Text(settings.text_size, (8, 4))  # upper-center
        self.aclabels_ur = glh.Text(settings.text_size, (8, 4))  # upper-right
        self.leaderlines = glh.VertexArrayObject(glh.gl.GL_LINES)

        self.ssrlabels = glh.Text(0.95*settings.text_size, (7, 3))
        self.microlabels = glh.Text(0.95*settings.text_size, (3, 1))

        bs.net.actnodedata_changed.connect(self.actdata_changed)

    def create(self):
        ac_size = settings.ac_size
        text_size = settings.text_size
        text_width = text_size
        text_height = text_size*1.2307692307692308
        wpt_size = settings.wpt_size

        # --------------- Aircraft data ---------------

        self.hdg.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.lat.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.lon.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.alt.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.tas.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.color.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.asasn.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.asase.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.rpz.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.histsymblat.create(MAX_NAIRCRAFT * 16, glh.GLBuffer.StreamDraw)
        self.histsymblon.create(MAX_NAIRCRAFT * 16, glh.GLBuffer.StreamDraw)
        self.leadlinelat.create(MAX_NAIRCRAFT * 8, glh.GLBuffer.StreamDraw)
        self.leadlinelon.create(MAX_NAIRCRAFT * 8, glh.GLBuffer.StreamDraw)

        # --------------- Label data ---------------

        self.lbl.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_ll.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_lc.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_lr.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_cl.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_cr.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_ul.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_uc.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.lbl_ur.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.ssrlbl.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.mlbl.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)

        # --------------- SSD ---------------

        self.ssd.create(lat1=self.lat, lon1=self.lon, alt1=self.alt,
                        tas1=self.tas, trk1=self.hdg)
        self.ssd.set_attribs(selssd=MAX_NAIRCRAFT, instance_divisor=1,
                             datatype=glh.gl.GL_UNSIGNED_BYTE, normalize=True)
        self.ssd.set_attribs(lat0=self.lat, lon0=self.lon,
                             alt0=self.alt, tas0=self.tas,
                             trk0=self.hdg, asasn=self.asasn,
                             asase=self.asase, instance_divisor=1)

        self.protectedzone.create(radius=1.0)
        self.protectedzone.set_attribs(lat=self.lat, lon=self.lon, scale=self.rpz,
                                       color=self.color, instance_divisor=1)

        # --------------- Aircraft symbols ---------------

        acvertices = np.array([(0.0, 0.5 * ac_size), (-0.5 * ac_size, -0.5 * ac_size),
                               (0.0, -0.25 * ac_size), (0.5 * ac_size, -0.5 * ac_size)],
                              dtype=np.float32)
        self.ac_symbol.create(vertex=acvertices)
        self.ac_symbol.set_attribs(lat=self.lat, lon=self.lon, color=self.color, orientation=self.hdg,
                                   instance_divisor=1)

        acverticeslvnl = np.array([(-0.5 * ac_size, -0.5 * ac_size),
                                   (0.5 * ac_size, 0.5 * ac_size),
                                   (0.5 * ac_size, -0.5 * ac_size),
                                   (-0.5 * ac_size, 0.5 * ac_size),
                                   (-0.5 * ac_size, -0.5 * ac_size),
                                   (0.5 * ac_size, -0.5 * ac_size),
                                   (0.5 * ac_size, 0.5 * ac_size),
                                   (-0.5 * ac_size, 0.5 * ac_size)],
                              dtype=np.float32)  # a square
        self.ac_symbollvnl.create(vertex=acverticeslvnl)
        self.ac_symbollvnl.set_attribs(lat=self.lat, lon=self.lon, color=self.color, instance_divisor=1)

        # --------------- History symbols ---------------

        histsymbol_size = 2
        self.hist_symbol.create(vertex=np.array([(histsymbol_size/2, histsymbol_size/2),
                                                 (-histsymbol_size/2, histsymbol_size/2),
                                                 (-histsymbol_size/2, -histsymbol_size/2),
                                                 (histsymbol_size/2, -histsymbol_size/2)], dtype=np.float32))
        self.hist_symbol.set_attribs(lat=self.histsymblat, lon=self.histsymblon,
                                     color=palette.aircraft, instance_divisor=1)

        # --------------- Aircraft labels ---------------
        self.aclabels.create(self.lbl, self.lat, self.lon, self.color,
                             (ac_size, -0.5 * ac_size), instanced=True)
        self.aclabels_ll.create(self.lbl_ll, self.lat, self.lon, self.color,
                                (-8*text_size-5*ac_size, -text_height-5*ac_size),
                                instanced=True)
        self.aclabels_lc.create(self.lbl_lc, self.lat, self.lon, self.color,
                                (ac_size, -text_height-ac_size),
                                instanced=True)
        self.aclabels_lr.create(self.lbl_lr, self.lat, self.lon, self.color,
                                (5*ac_size, -text_height-5*ac_size),
                                instanced=True)
        self.aclabels_cl.create(self.lbl_cl, self.lat, self.lon, self.color,
                                (-8*text_size-7*ac_size, 0),
                                instanced=True)
        self.aclabels_cr.create(self.lbl_cr, self.lat, self.lon, self.color,
                                (7*ac_size, 0), instanced=True)
        self.aclabels_ul.create(self.lbl_ul, self.lat, self.lon, self.color,
                                (-8*text_size-5*ac_size, 3*text_height+5*ac_size),
                                instanced=True)
        self.aclabels_uc.create(self.lbl_uc, self.lat, self.lon, self.color,
                                (ac_size, 3*text_height+ac_size),
                                instanced=True)
        self.aclabels_ur.create(self.lbl_ur, self.lat, self.lon, self.color,
                                (5*ac_size, 3*text_height+5*ac_size),
                                instanced=True)

        self.ssrlabels.create(self.ssrlbl, self.lat, self.lon, self.color,
                              (ac_size, -1.1*ac_size), instanced=True)
        self.microlabels.create(self.mlbl, self.lat, self.lon, self.color,
                                (-3*0.8*text_size-ac_size, 0.5*ac_size), instanced=True)

        # --------------- Leader lines ---------------

        self.leaderlines.create(vertex=MAX_NAIRCRAFT * 4, color=palette.aircraft)
        self.leaderlines.set_attribs(lat=self.leadlinelat, lon=self.leadlinelon)

        # --------------- CPA lines ---------------

        self.cpalines.create(vertex=MAX_NCONFLICTS * 16, color=palette.conflict, usage=glh.GLBuffer.StreamDraw)

        # --------------- Aircraft Route ---------------
        self.route.create(vertex=ROUTE_SIZE * 8, color=palette.route, usage=glh.gl.GL_DYNAMIC_DRAW)

        self.routelbl.create(ROUTE_SIZE * 24, ROUTE_SIZE * 4, ROUTE_SIZE * 4,
                             palette.route, (wpt_size, 0.5 * wpt_size), instanced=True)
        rwptvertices = np.array([(-0.2 * wpt_size, -0.2 * wpt_size),
                                 (0.0,            -0.8 * wpt_size),
                                 (0.2 * wpt_size, -0.2 * wpt_size),
                                 (0.8 * wpt_size,  0.0),
                                 (0.2 * wpt_size,  0.2 * wpt_size),
                                 (0.0,             0.8 * wpt_size),
                                 (-0.2 * wpt_size,  0.2 * wpt_size),
                                 (-0.8 * wpt_size,  0.0)], dtype=np.float32)
        self.rwaypoints.create(vertex=rwptvertices, color=palette.route)
        self.rwaypoints.set_attribs(lat=self.routelbl.lat, lon=self.routelbl.lon, instance_divisor=1)

        # --------------- Aircraft Trails ---------------
        self.traillines.create(vertex=TRAILS_SIZE * 16, color=palette.trails)
        self.initialized = True

    def draw(self):
        ''' Draw all traffic graphics. '''
        # Get data for active node
        actdata = bs.net.get_nodedata()
        if actdata.naircraft == 0 or not actdata.show_traf:
            return

        # Send the (possibly) updated global uniforms to the buffer
        self.shaderset.set_vertex_scale_type(self.shaderset.VERTEX_IS_LATLON)
        self.shaderset.enable_wrap(False)

        self.route.draw()
        self.cpalines.draw()
        self.traillines.draw()

        # --- DRAW THE INSTANCED AIRCRAFT SHAPES ------------------------------
        # update wrap longitude and direction for the instanced objects
        self.shaderset.enable_wrap(True)

        # PZ circles only when they are bigger than the A/C symbols
        if actdata.show_pz and actdata.zoom >= 0.15:
            self.shaderset.set_vertex_scale_type(
                self.shaderset.VERTEX_IS_METERS)
            self.protectedzone.draw(n_instances=actdata.naircraft)

        self.shaderset.set_vertex_scale_type(self.shaderset.VERTEX_IS_SCREEN)

        # Draw traffic symbols
        if actdata.atcmode == 'BLUESKY':
            self.ac_symbol.draw(n_instances=actdata.naircraft)
        else:
            self.ac_symbollvnl.draw(n_instances=actdata.naircraft)

        if actdata.show_histsymb and len(actdata.acdata.histsymblat) != 0:
            self.hist_symbol.set_attribs(color=palette.aircraft)
            self.hist_symbol.draw(n_instances=len(actdata.acdata.histsymblat))

        if self.routelbl.n_instances:
            self.rwaypoints.draw(n_instances=self.routelbl.n_instances)
            self.routelbl.draw()

        if actdata.atcmode == 'BLUESKY':
            if actdata.show_lbl >= 1:
                self.aclabels.draw(n_instances=actdata.naircraft)
        else:
            self.aclabels_ll.draw(n_instances=actdata.naircraft)
            self.aclabels_lc.draw(n_instances=actdata.naircraft)
            self.aclabels_lr.draw(n_instances=actdata.naircraft)
            self.aclabels_cl.draw(n_instances=actdata.naircraft)
            self.aclabels_cr.draw(n_instances=actdata.naircraft)
            self.aclabels_ul.draw(n_instances=actdata.naircraft)
            self.aclabels_uc.draw(n_instances=actdata.naircraft)
            self.aclabels_ur.draw(n_instances=actdata.naircraft)
            self.ssrlabels.draw(n_instances=actdata.naircraft)
            self.microlabels.draw(n_instances=actdata.naircraft)
            self.leaderlines.draw()

        # SSD
        if actdata.ssd_all or actdata.ssd_conflicts or len(actdata.ssd_ownship) > 0:
            ssd_shader = glh.ShaderSet.get_shader('ssd')
            ssd_shader.bind()
            glh.gl.glUniform3f(ssd_shader.uniforms['Vlimits'].loc, self.asas_vmin **
                           2, self.asas_vmax ** 2, self.asas_vmax)
            glh.gl.glUniform1i(ssd_shader.uniforms['n_ac'].loc, actdata.naircraft)
            self.ssd.draw(vertex_count=actdata.naircraft,
                          n_instances=actdata.naircraft)

    def actdata_changed(self, nodeid, nodedata, changed_elems):
        ''' Process incoming traffic data. '''
        if 'ACDATA' in changed_elems:
            self.update_aircraft_data(nodedata.acdata)
        if 'ROUTEDATA' in changed_elems:
            self.update_route_data(nodedata.routedata)
        if 'TRAILS' in changed_elems:
            self.update_trails_data(nodedata.traillat0,
                                    nodedata.traillon0,
                                    nodedata.traillat1,
                                    nodedata.traillon1)

    def update_trails_data(self, lat0, lon0, lat1, lon1):
        ''' Update GPU buffers with route data from simulation. '''
        if not self.initialized:
            return
        self.glsurface.makeCurrent()
        self.traillines.set_vertex_count(len(lat0))
        if len(lat0) > 0:
            self.traillines.update(vertex=np.array(
                    list(zip(lat0, lon0,
                             lat1, lon1)), dtype=np.float32))

    def update_route_data(self, data):
        ''' Update GPU buffers with route data from simulation. '''
        if not self.initialized:
            return
        self.glsurface.makeCurrent()
        actdata = bs.net.get_nodedata()

        self.route_acid = data.acid
        if data.acid != "" and len(data.wplat) > 0:
            nsegments = len(data.wplat)
            data.iactwp = min(max(0, data.iactwp), nsegments - 1)
            self.routelbl.n_instances = nsegments
            self.route.set_vertex_count(2 * nsegments)
            routedata = np.empty(4 * nsegments, dtype=np.float32)
            routedata[0:4] = [data.aclat, data.aclon,
                              data.wplat[data.iactwp], data.wplon[data.iactwp]]

            routedata[4::4] = data.wplat[:-1]
            routedata[5::4] = data.wplon[:-1]
            routedata[6::4] = data.wplat[1:]
            routedata[7::4] = data.wplon[1:]

            self.route.update(vertex=routedata)
            wpname = ''
            for wp, alt, spd in zip(data.wpname, data.wpalt, data.wpspd):
                if alt < 0. and spd < 0.:
                    txt = wp[:12].ljust(24)  # No second line
                else:
                    txt = wp[:12].ljust(12)  # Two lines
                    if alt < 0:
                        txt += "-----/"
                    elif alt > actdata.translvl:
                        FL = int(round((alt / (100. * ft))))
                        txt += "FL%03d/" % FL
                    else:
                        txt += "%05d/" % int(round(alt / ft))

                    # Speed
                    if spd < 0:
                        txt += "--- "
                    elif spd > 2.0:
                        txt += "%03d" % int(round(spd / kts))
                    else:
                        txt += "M{:.2f}".format(spd)  # Mach number

                wpname += txt.ljust(24)  # Fill out with spaces
            self.routelbl.update(texdepth=np.array(wpname.encode('ascii', 'ignore')),
                                 lat=np.array(data.wplat, dtype=np.float32),
                                 lon=np.array(data.wplon, dtype=np.float32))
        else:
            self.route.set_vertex_count(0)
            self.routelbl.n_instances = 0

    def update_aircraft_data(self, data):
        ''' Update GPU buffers with new aircraft simulation data. '''
        if not self.initialized:
            return

        self.glsurface.makeCurrent()
        actdata = bs.net.get_nodedata()
        if actdata.filteralt:
            idx = np.where(
                (data.alt >= actdata.filteralt[0]) * (data.alt <= actdata.filteralt[1]))
            data.lat = data.lat[idx]
            data.lon = data.lon[idx]
            data.selhdg = data.selhdg[idx]
            data.trk = data.trk[idx]
            data.selalt = data.selalt[idx]
            data.alt = data.alt[idx]
            data.tas = data.tas[idx]
            data.vs = data.vs[idx]
            data.rpz = data.rpz[idx]
            data.type = data.type[idx]
        naircraft = len(data.lat)
        actdata.translvl = data.translvl
        # self.asas_vmin = data.vmin # TODO: array should be attribute not uniform
        # self.asas_vmax = data.vmax

        if naircraft == 0:
            self.cpalines.set_vertex_count(0)
        else:
            # Update data in GPU buffers
            self.lat.update(np.array(data.lat, dtype=np.float32))
            self.lon.update(np.array(data.lon, dtype=np.float32))
            self.hdg.update(np.array(data.trk, dtype=np.float32))
            self.alt.update(np.array(data.alt, dtype=np.float32))
            self.tas.update(np.array(data.tas, dtype=np.float32))
            self.rpz.update(np.array(data.rpz, dtype=np.float32))
            self.histsymblat.update(np.array(data.histsymblat, dtype=np.float32))
            self.histsymblon.update(np.array(data.histsymblon, dtype=np.float32))
            self.leadlinelat.update(np.repeat(np.array(data.lat, dtype=np.float32), 2))
            self.leadlinelon.update(np.repeat(np.array(data.lon, dtype=np.float32), 2))
            if hasattr(data, 'asasn') and hasattr(data, 'asase'):
                self.asasn.update(np.array(data.asasn, dtype=np.float32))
                self.asase.update(np.array(data.asase, dtype=np.float32))

            # CPA lines to indicate conflicts
            ncpalines = np.count_nonzero(data.inconf)

            cpalines = np.zeros(4 * ncpalines, dtype=np.float32)
            self.cpalines.set_vertex_count(2 * ncpalines)

            # Labels and colors
            rawlabel = ''
            rawlabels = ['', '', '',
                         '', '',
                         '', '', '']
            rawmlabel = ''
            rawssrlabel = ''
            leaderlines = []
            color = np.empty(
                (min(naircraft, MAX_NAIRCRAFT), 4), dtype=np.uint8)
            selssd = np.zeros(naircraft, dtype=np.uint8)
            confidx = 0

            zdata = zip(data.gs, data.id, data.inconf, data.ingroup, data.lat, data.lon, data.tcpamax, data.trk)
            for i, (gs, acid, inconf, ingroup, lat, lon, tcpa, trk) in enumerate(zdata):

                if i >= MAX_NAIRCRAFT:
                    break

                # BlueSky default label (ATC mode BLUESKY)
                if actdata.atcmode == 'BLUESKY':
                    rawlabel = baselabel(rawlabel, actdata, data, i)
                # LVNL labels
                else:
                    # Labels
                    rawlabels, rawmlabel, rawssrlabel = create_aclabel(rawlabels, rawmlabel, rawssrlabel,
                                                                       actdata, data, i)
                    # Leaderlines
                    leaderlines = leaderline_vertex(leaderlines, actdata, data, i)

                # Colours
                if inconf:
                    if actdata.ssd_conflicts:
                        selssd[i] = 255
                    color[i, :] = palette.conflict + (255,)
                    lat1, lon1 = geo.qdrpos(lat, lon, trk, tcpa * gs / nm)
                    cpalines[4 * confidx: 4 * confidx +
                             4] = [lat, lon, lat1, lon1]
                    confidx += 1
                # Selected aircraft
                elif acid == console.Console._instance.id_select and actdata.atcmode != 'BLUESKY':
                    rgb = (218, 218, 0) + (255,)
                    color[i, :] = rgb
                else:
                    # Get custom color if available, else default
                    rgb = palette.aircraft
                    if ingroup:
                        for groupmask, groupcolor in actdata.custgrclr.items():
                            if ingroup & groupmask:
                                rgb = groupcolor
                                break
                    rgb = actdata.custacclr.get(acid, rgb)
                    color[i, :] = tuple(rgb) + (255,)

                #  Check if aircraft is selected to show SSD
                if actdata.ssd_all or acid in actdata.ssd_ownship:
                    selssd[i] = 255

            if len(actdata.ssd_ownship) > 0 or actdata.ssd_conflicts or actdata.ssd_all:
                self.ssd.update(selssd=selssd)

            self.cpalines.update(vertex=cpalines)
            self.color.update(color)

            # BlueSky default label (ATC mode BLUESKY)
            if actdata.atcmode == 'BLUESKY':
                self.lbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
            # LVNL labels
            else:
                # Update track label
                self.lbl_ll.update(np.array(rawlabels[5].encode('utf8'), dtype=np.string_))
                self.lbl_lc.update(np.array(rawlabels[6].encode('utf8'), dtype=np.string_))
                self.lbl_lr.update(np.array(rawlabels[7].encode('utf8'), dtype=np.string_))
                self.lbl_cl.update(np.array(rawlabels[3].encode('utf8'), dtype=np.string_))
                self.lbl_cr.update(np.array(rawlabels[4].encode('utf8'), dtype=np.string_))
                self.lbl_ul.update(np.array(rawlabels[0].encode('utf8'), dtype=np.string_))
                self.lbl_uc.update(np.array(rawlabels[1].encode('utf8'), dtype=np.string_))
                self.lbl_ur.update(np.array(rawlabels[2].encode('utf8'), dtype=np.string_))
                # Update SSR label
                self.ssrlbl.update(np.array(rawssrlabel.encode('utf8'), dtype=np.string_))
                # Update micro label
                self.mlbl.update(np.array(rawmlabel.encode('utf8'), dtype=np.string_))
                # Leader line update
                leaderlines = np.array(leaderlines, dtype=np.float32)
                self.leaderlines.set_vertex_count(int(len(leaderlines)/2))
                self.leaderlines.update(vertex=leaderlines)
            
            # If there is a visible route, update the start position
            if self.route_acid in data.id:
                idx = data.id.index(self.route_acid)
                self.route.vertex.update(np.array([data.lat[idx], data.lon[idx]], dtype=np.float32))


"""
Create label functions
"""


def baselabel(rawlabel, actdata, data, i):
    """
    Function: Create base label
    Args:
        rawlabel:   string to add label [str]
        actdata:    node data [class]
        data:       aircraft data [class]
        i:          index for data [int]
    Returns:
        rawlabel:   label string [str]

    Created by: Bob van Dillen
    Date: 13-1-2022
    """

    rawlabel += '%-8s' % data.id[i][:8]
    if actdata.show_lbl == 2:
        if data.alt[i] <= data.translvl:
            rawlabel += '%-5d' % int(data.alt[i] / ft + 0.5)
        else:
            rawlabel += 'FL%03d' % int(data.alt[i] / ft / 100. + 0.5)
        vsarrow = 30 if data.vs[i] > 0.25 else 31 if data.vs[i] < -0.25 else 32
        rawlabel += '%1s  %-8d' % (chr(vsarrow),
                                   int(data.cas[i] / kts + 0.5))
    else:
        rawlabel += 2*8*' '
    return rawlabel


def create_aclabel(rawlabels, rawmlabel, rawssrlabel, actdata, data, i):
    """
    Function: Create the labels for an aircraft
    Args:
        rawlabels:      aircraft labels [list]
        rawmlabel:      micro label [str]
        rawssrlabel:    ssr label [str]
        actdata:        node data [class]
        data:           aircraft data [class]
        i:              index for data [int]
    Returns:
        rawlabels:      aircraft labels [list]
        rawmlabel:      micro label [str]
        rawssrlabel:    ssr label [str]

    Created by: Bob van Dillen
    Date: 12-1-2022
    """

    # Get track label position
    lbl_i = get_lblpos(data.lblpos[i])
    # Other track label positions are empty
    for n in range(len(rawlabels)):
        if n != lbl_i:
            rawlabels[n] += 8*4*' '

    # APP mode
    if actdata.atcmode == 'APP':
        rawlabels[lbl_i], rawmlabel, rawssrlabel = applabel(rawlabels[lbl_i], rawmlabel, rawssrlabel, actdata,
                                                            data, i)
    # ACC mode
    elif actdata.atcmode == 'ACC':
        rawlabels[lbl_i], rawmlabel, rawssrlabel = acclabel(rawlabels[lbl_i], rawmlabel, rawssrlabel, actdata,
                                                            data, i)
    # TWR mode
    elif actdata.atcmode == 'TWR':
        rawlabels[lbl_i] = twrlabel(rawlabels[lbl_i], actdata, data, i)
        rawmlabel += 3*' '
        rawssrlabel += 7*3*' '

    return rawlabels, rawmlabel, rawssrlabel


def get_lblpos(lblpos):
    """
    Function: Get the position of the label for the label list
    Args:
        lblpos: position of the label [str]
    Returns:
        index for rawlabels list [int]

    Created by: Bob van Dillen
    Date: 12-1-2022
    """

    if lblpos == 'LL':
        return 5
    if lblpos == 'LC':
        return 6
    if lblpos == 'LR':
        return 7
    if lblpos == 'CL':
        return 3
    if lblpos == 'CR':
        return 4
    if lblpos == 'UL':
        return 0
    if lblpos == 'UC':
        return 1
    if lblpos == 'UR':
        return 2


def applabel(rawlabel, rawmlabel, rawssrlabel, actdata, data, i):
    """
    Function: Create approach label
    Args:
        rawlabel:       string to add label [str]
        rawmlabel:      string to add micro label [str]
        rawssrlabel:    string to add ssr label [str]
        actdata:        node data [class]
        data:           aircraft data [class]
        i:              index for data [int]
    Returns:
        rawlabel:       track label string [str]
        rawmlabel:      micro label string [str]
        rawssrlabel:    ssr label string [str]

    Created by: Bob van Dillen
    Date: 21-12-2021
    """

    # Track label
    if data.tracklbl[i]:
        # Line 1
        rawlabel += '%-8s' % data.id[i][:8]

        # Line 2
        rawlabel += '%-3s' % leading_zeros(data.alt[i]/ft/100)[-3:]
        if data.alt[i] < actdata.translvl:
            rawlabel += '%-1s' % 'A'
        else:
            rawlabel += '%-1s' % ' '
        if data.uco[i] and data.selalt[i] != 0:
            rawlabel += '%-3s' % leading_zeros(data.selalt[i]/ft/100)[-3:]
        else:
            rawlabel += '%-3s' % '   '
        rawlabel += '%-1s' % ' '

        # Line 3
        rawlabel += '%-4s' % str(data.type[i])[:4]
        if data.uco[i] and data.selhdg[i] != 0:
            rawlabel += '%-3s' % leading_zeros(data.selhdg[i])[:3]
        elif data.flighttype[i] == 'INBOUND':
            rawlabel += '%-3s' % data.arr[i].replace('ARTIP', 'ATP')[:3]
        elif data.flighttype[i] == 'OUTBOUND':
            rawlabel += '%-3s' % data.sid[i][:3]
        else:
            rawlabel += '%-3s' % '   '
        rawlabel += '%-1s' % ' '

        # Line 4
        rawlabel += '%-3s' % leading_zeros(data.gs[i]/kts)[:3]
        if data.wtc[i].upper() == 'H' or data.wtc[i].upper() == 'J':
            rawlabel += '%-1s' % str(data.wtc[i])[:1]
        else:
            rawlabel += '%-1s' % ' '
        if data.uco[i] and data.selspd[i] != 0:
            rawlabel += '%-3s' % leading_zeros(data.selspd[i]/kts)[:3]
        else:
            rawlabel += '%-3s' % 'SPD'
        rawlabel += '%-1s' % ' '
    else:
        rawlabel += 8*4*' '

    # Micro label
    if data.mlbl[i]:
        if data.flighttype[i].upper() == 'OUTBOUND':
            rawmlabel += '  '+chr(30)
        else:
            rawmlabel += '%-3s' % data.rwy[i][:3]
    else:
        rawmlabel += 3*' '

    # SSR label
    ssrlbl = data.ssrlbl[i].split(';')
    # Mode A
    if 'A' in ssrlbl and data.ssr[i] != 0:
        rawssrlabel += '%-7s' % str(data.ssr[i])[:7]
    else:
        rawssrlabel += 7*' '
    # Mode C
    if 'C' in ssrlbl:
        rawssrlabel += '%-3s' % leading_zeros(data.alt[i]/ft/100)[:3]
        if data.alt[i] < actdata.translvl:
            rawssrlabel += '%-4s' % 'A   '
        else:
            rawssrlabel += '%-4s' % '    '
    else:
        rawssrlabel += 7*' '
    # ACID
    if 'ACID' in ssrlbl:
        rawssrlabel += '%-7s' % data.id[i][:7]
    else:
        rawssrlabel += 7*' '

    return rawlabel, rawmlabel, rawssrlabel


def acclabel(rawlabel, rawmlabel, rawssrlabel, actdata, data, i):
    """
    Function: Create acc label
    Args:
        rawlabel:       string to add label [str]
        rawmlabel:      string to add micro label [str]
        rawssrlabel:    string to add ssr label [str]
        actdata:        node data [class]
        data:           aircraft data [class]
        i:              index for data [int]
    Returns:
        rawlabel:       track label string [str]
        rawmlabel:      micro label string [str]
        rawssrlabel:    ssr label string [str]

    Created by: Bob van Dillen
    Date: 21-12-2021
    """

    # Track label
    if data.tracklbl[i]:
        # Line 1
        rawlabel += '%-8s' % data.id[i][:8]

        # Line 2
        rawlabel += '%-3s' % leading_zeros(data.alt[i]/ft/100)[-3:]
        if data.alt[i] < actdata.translvl:
            rawlabel += '%-1s' % 'A'
        else:
            rawlabel += '%-1s' % ' '
        if data.uco[i] and data.selalt[i] != 0:
            rawlabel += '%-3s' % leading_zeros(data.selalt[i]/ft/100)[-3:]
        else:
            rawlabel += '%-3s' % '   '
        rawlabel += '%-1s' % ' '

        # Line 3
        rawlabel += '%-3s' % '...'
        rawlabel += '%-1s' % ' '
        rawlabel += '%-3s' % leading_zeros(data.gs[i]/kts)[:3]
        if data.wtc[i].upper() == 'H' or data.wtc[i].upper() == 'J':
            rawlabel += '%-1s' % str(data.wtc[i])[:1]
        else:
            rawlabel += '%-1s' % ' '

        # Line 4
        if data.uco[i] and data.selspd[i] != 0:
            rawlabel += '%-1s' % 'I'
            rawlabel += '%-3s' % leading_zeros(data.selspd[i]/kts)[:3]
        else:
            rawlabel += '%-4s' % '    '
        rawlabel += '%-4s' % data.type[i][:4]
    else:
        rawlabel += 8*4*' '

    # Micro label
    if data.mlbl[i]:
        if data.flighttype[i].upper() == 'INBOUND':
            rawmlabel += '  '+chr(31)
        else:
            rawmlabel += 3*' '
    else:
        rawmlabel += 3*' '

    # SSR label
    ssrlbl = data.ssrlbl[i].split(';')
    # ACID
    if 'ACID' in ssrlbl:
        rawssrlabel += '%-7s' % data.id[i][:7]
    else:
        rawssrlabel += 7*' '
    # Mode A
    if 'A' in ssrlbl and data.ssr[i] != 0:
        rawssrlabel += '%-7s' % str(data.ssr[i])[:7]
    else:
        rawssrlabel += 7*' '
    # Mode C
    if 'C' in ssrlbl:
        rawssrlabel += '%-3s' % leading_zeros(data.alt[i]/ft/100)[:3]
        if data.alt[i] < actdata.translvl:
            rawssrlabel += '%-4s' % 'A   '
        else:
            rawssrlabel += '%-4s' % '    '
    else:
        rawssrlabel += 7*' '

    return rawlabel, rawmlabel, rawssrlabel


def twrlabel(rawlabel, actdata, data, i):
    """
    Function: Create acc label
    Args:
        rawlabel:       string to add label [str]
        actdata:        node data [dict]
        data:           aircraft data [dict]
        i:              index for data [int]
    Returns:
        rawlabel:       track label string [str]
        rawmlabel:      micro label string [str]
        rawssrlabel:    ssr label string [str]

    Created by: Bob van Dillen
    Date: 21-12-2021
    """

    # Line 1
    rawlabel += '%-8s' % data.id[i][:8]
    if actdata.show_lbl == 2:
        # Line 2
        if data.flighttype[i] == "INBOUND":
            rawlabel += 8*' '
        else:
            rawlabel += '%-5s' % data.sid[i][:5]
            rawlabel += ' '
            rawlabel += '%-2s' % data.rwy[i][-2:]
        # Line 3
        rawlabel += '%-8s' % data.type[i][:8]
        # Line 4
        rawlabel += 8*' '
    else:
        rawlabel += 8*3*' '

    return rawlabel


def leading_zeros(number):
    """
    Function: Add leading zeros to number string (e.g. 005)
    Args:
        number: number to be displayed [int, float]
    Returns:
        number: number with leading zeros [str]

    Created by: Bob van Dillen
    Date: 16-12-2021
    """

    if number < 0:
        number = 0
    if number < 10:
        return '00'+str(round(number))
    elif number < 100:
        return '0'+str(round(number))
    else:
        return str(round(number))


def leaderline_vertex(leaderlines, actdata, data, i):
    """
    Function: Get the vertex for the leader line
    Args:
        leaderlines:    leader lines vertices [array]
        data:           aircraft data [class]
        i:              index for data [int]
    Returns:
        leaderlines:    leader lines vertices [array]

    Created by: Bob van Dillen
    Date: 2-2-2022
    """

    ac_size = settings.ac_size
    text_size = settings.text_size
    text_width = text_size
    text_height = text_size*1.2307692307692308

    # APP does not use the last character of the track label
    if data.tracklbl[i] and actdata.atcmode == 'APP':
        vertices = [[(-ac_size, ac_size), (-5*ac_size-text_width, 5*ac_size)], [(0, ac_size), (0, ac_size+3*text_height)], [(ac_size, ac_size), (5*ac_size, 5*ac_size)],
                    [(-ac_size, 0,), (-7*ac_size-text_width, 0)], [(ac_size, 0), (7*ac_size, 0)],
                    [(-ac_size, -ac_size), (-5*ac_size-text_width, -5*ac_size)], [(0, -ac_size), (0, -3*text_height-ac_size)], [(ac_size, -ac_size), (5*ac_size, -5*ac_size)]]
    elif data.tracklbl[i] and actdata.atcmode == 'ACC':
        vertices = [[(-ac_size, ac_size), (-5*ac_size, 5*ac_size)], [(0, ac_size), (0, ac_size+3*text_height)], [(ac_size, ac_size), (5*ac_size, 5*ac_size)],
                    [(-ac_size, 0,), (-7*ac_size, 0)], [(ac_size, 0), (7*ac_size, 0)],
                    [(-ac_size, -ac_size), (-5*ac_size, -5*ac_size)], [(0, -ac_size), (0, -3*text_height-ac_size)], [(ac_size, -ac_size), (5*ac_size, -5*ac_size)]]
    else:
        vertices = [[(0, 0), (0, 0)], [(0, 0), (0, 0)], [(0, 0), (0, 0)],
                    [(0, 0), (0, 0)], [(0, 0), (0, 0)],
                    [(0, 0), (0, 0)], [(0, 0), (0, 0)], [(0, 0), (0, 0)]]

    j = get_lblpos(data.lblpos[i])

    leaderlines.append(vertices[j][0])
    leaderlines.append(vertices[j][1])

    return leaderlines

