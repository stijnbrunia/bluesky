''' Traffic OpenGL visualisation. '''
import numpy as np
import itertools
from bluesky.ui.qtgl import glhelpers as glh
from bluesky.ui.qtgl import console

import bluesky as bs
from bluesky.tools import geo
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
        self.hdg = glh.GLBuffer()
        self.rpz = glh.GLBuffer()
        self.lat = glh.GLBuffer()
        self.lon = glh.GLBuffer()
        self.alt = glh.GLBuffer()
        self.tas = glh.GLBuffer()
        self.color = glh.GLBuffer()
        self.lbl = glh.GLBuffer()
        self.asasn = glh.GLBuffer()
        self.asase = glh.GLBuffer()
        self.histsymblat = glh.GLBuffer()
        self.histsymblon = glh.GLBuffer()

        self.ssd = glh.VertexArrayObject(glh.gl.GL_POINTS, shader_type='ssd')
        self.protectedzone = glh.Circle()
        # self.ac_symbol = glh.VertexArrayObject(glh.gl.GL_TRIANGLE_FAN)
        self.ac_symbol = glh.VertexArrayObject(glh.gl.GL_LINE_LOOP)
        self.hist_symbol = glh.VertexArrayObject(glh.gl.GL_POINTS)
        self.aclabels = glh.Text(settings.text_size, (7, 4))
        self.cpalines = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.route = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.routelbl = glh.Text(settings.text_size, (12, 2))
        self.rwaypoints = glh.VertexArrayObject(glh.gl.GL_LINE_LOOP)
        self.traillines = glh.VertexArrayObject(glh.gl.GL_LINES)

        bs.net.actnodedata_changed.connect(self.actdata_changed)

    def create(self):
        ac_size = settings.ac_size
        wpt_size = settings.wpt_size
        self.hdg.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.lat.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.lon.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.alt.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.tas.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.color.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.lbl.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.asasn.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.asase.create(MAX_NAIRCRAFT * 24, glh.GLBuffer.StreamDraw)
        self.rpz.create(MAX_NAIRCRAFT * 4, glh.GLBuffer.StreamDraw)
        self.histsymblat.create(MAX_NAIRCRAFT * 16, glh.GLBuffer.StreamDraw)
        self.histsymblon.create(MAX_NAIRCRAFT * 16, glh.GLBuffer.StreamDraw)

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

        # acvertices = np.array([(0.0, 0.5 * ac_size), (-0.5 * ac_size, -0.5 * ac_size),
        #                        (0.0, -0.25 * ac_size), (0.5 * ac_size, -0.5 * ac_size)],
        #                       dtype=np.float32)

        acvertices_sizevar = 0.4
        acvertices = np.array([(-acvertices_sizevar * ac_size, -acvertices_sizevar * ac_size),
                               (acvertices_sizevar * ac_size, acvertices_sizevar * ac_size),
                               (acvertices_sizevar * ac_size, -acvertices_sizevar * ac_size),
                               (-acvertices_sizevar * ac_size, acvertices_sizevar * ac_size),
                               (-acvertices_sizevar * ac_size, -acvertices_sizevar * ac_size),
                               (acvertices_sizevar * ac_size, -acvertices_sizevar * ac_size),
                               (acvertices_sizevar * ac_size, acvertices_sizevar * ac_size),
                               (-acvertices_sizevar * ac_size, acvertices_sizevar * ac_size)],
                              dtype=np.float32)  # a square

        self.ac_symbol.create(vertex=acvertices)

        # self.ac_symbol.set_attribs(lat=self.lat, lon=self.lon, color=self.color,
        #                            orientation=self.hdg, instance_divisor=1)

        self.ac_symbol.set_attribs(lat=self.lat, lon=self.lon, color=self.color,
                                    instance_divisor=1)

        self.hist_symbol.create(vertex=np.array([(0, 0)], dtype=np.float32))
        self.hist_symbol.set_attribs(lat=self.histsymblat, lon=self.histsymblon,
                                     color=palette.aircraft, instance_divisor=1)

        self.aclabels.create(self.lbl, self.lat, self.lon, self.color,
                             (ac_size, -0.5 * ac_size), instanced=True)

        self.cpalines.create(vertex=MAX_NCONFLICTS * 16, color=palette.conflict, usage=glh.GLBuffer.StreamDraw)

        # ------- Aircraft Route -------------------------
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

        # # --------Aircraft Trails------------------------------------------------
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
        self.ac_symbol.draw(n_instances=actdata.naircraft)

        if actdata.show_histsymb:
            glh.gl.glPointSize(2)
            self.hist_symbol.draw(n_instances=len(actdata.acdata.histsymblat))

        if self.routelbl.n_instances:
            self.rwaypoints.draw(n_instances=self.routelbl.n_instances)
            self.routelbl.draw()

        if actdata.show_lbl:
            self.aclabels.draw(n_instances=actdata.naircraft)

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
        if 'ACDATA' in changed_elems or 'CMDDATA' in changed_elems:
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
            if hasattr(data, 'asasn') and hasattr(data, 'asase'):
                self.asasn.update(np.array(data.asasn, dtype=np.float32))
                self.asase.update(np.array(data.asase, dtype=np.float32))

            # CPA lines to indicate conflicts
            ncpalines = np.count_nonzero(data.inconf)

            cpalines = np.zeros(4 * ncpalines, dtype=np.float32)
            self.cpalines.set_vertex_count(2 * ncpalines)

            # Labels and colors
            rawlabel = ''
            color = np.empty(
                (min(naircraft, MAX_NAIRCRAFT), 4), dtype=np.uint8)
            selssd = np.zeros(naircraft, dtype=np.uint8)
            confidx = 0

            zdata = zip(data.id, data.ingroup, data.inconf, data.tcpamax, data.selhdg, data.trk, data.gs,
                        data.cas, data.selspd, data.vs, data.selalt, data.alt, data.lat, data.lon, data.flighttype,
                        data.wtc, data.uco, data.type, data.arr, data.sid)
            for i, (acid, ingroup, inconf, tcpa,
                    selhdg, trk, gs, cas, selspd, vs, selalt, alt, lat, lon,
                    flighttype, wtc, uco, type, arr, sid) in enumerate(zdata):
                if i >= MAX_NAIRCRAFT:
                    break

                # Make label: 4 lines of 7 characters per aircraft
                if actdata.show_lbl >= 1:
                    # Line 1
                    rawlabel += '%-7s' % acid[:7]

                    if actdata.show_lbl == 2:  # and flighttype in ['INBOUND', 'OUTBOUND']:
                        # Line 2
                        rawlabel += '%-3s' % leading_zeros(alt/ft/100)[-3:]
                        rawlabel += '%-1s' % ' '
                        if uco and selalt != 0:
                            rawlabel += '%-3s' % leading_zeros(selalt/ft/100)[-3:]
                        else:
                            rawlabel += '%-3s' % '   '

                        # Line 3
                        rawlabel += '%-4s' % str(type)[:4]
                        if flighttype == 'INBOUND' and not uco:
                            rawlabel += '%-3s' % str(arr)[:3]
                        elif flighttype == 'OUTBOUND' and not uco:
                            rawlabel += '%-3s' % str(sid)[:3]
                        elif uco and selhdg != 0:
                            rawlabel += '%-3s' % leading_zeros(selhdg)[:3]
                        else:
                            rawlabel += '%-3s' % '   '

                        # Line 4
                        rawlabel += '%-3s' % leading_zeros(gs/kts)[:3]
                        if wtc.upper() == 'H' or wtc.upper() == 'J':
                            rawlabel += '%-1s' % str(wtc)[:1]
                        else:
                            rawlabel += '%-1s' % ' '
                        if uco:
                            rawlabel += '%-3s' % leading_zeros(selspd/kts)[:3]
                        else:
                            rawlabel += '%-3s' % 'SPD'
                    else:
                        rawlabel += 21*' '

                if inconf:
                    if actdata.ssd_conflicts:
                        selssd[i] = 255
                    color[i, :] = palette.conflict + (255,)
                    lat1, lon1 = geo.qdrpos(lat, lon, trk, tcpa * gs / nm)
                    cpalines[4 * confidx: 4 * confidx +
                             4] = [lat, lon, lat1, lon1]
                    confidx += 1
                # Selected aircraft
                elif acid == console.Console._instance.id_select:
                    rgb = (227, 227, 49) + (255,)
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
            self.lbl.update(np.array(rawlabel.encode('utf8'), dtype=np.string_))
            
            # If there is a visible route, update the start position
            if self.route_acid in data.id:
                idx = data.id.index(self.route_acid)
                self.route.vertex.update(np.array([data.lat[idx], data.lon[idx]], dtype=np.float32))


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
