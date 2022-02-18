''' BlueSky OpenGL line and polygon (areafilter) drawing. '''
import numpy as np
import bluesky as bs
from bluesky import settings
from bluesky.ui import palette
from bluesky.ui.qtgl import console
from bluesky.ui.qtgl import glhelpers as glh
from bluesky.tools import geo

# Default settings
settings.set_variable_defaults(
    point_size=3
)

# Default pallete
palette.set_default_colours(
    polys=(0, 255, 255),
    previewpoly=(0, 204, 255)
) 

# Static defines
POLYPREV_SIZE = 100
POLY_SIZE = 2000
l_dotted = 3    # [pixels]
l_dashed = 10   # [pixels]

class Poly(glh.RenderObject, layer=-20):
    ''' Poly OpenGL object. '''

    def __init__(self, parent=None):
        super().__init__(parent)
        # Polygon preview object
        self.polyprev = glh.VertexArrayObject(glh.gl.GL_LINE_LOOP)

        # Fixed polygons
        self.allpolys = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.alldotted = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.alldashed = glh.VertexArrayObject(glh.gl.GL_LINES)
        self.allpfill = glh.VertexArrayObject(glh.gl.GL_TRIANGLES)
        # Points
        self.allpoints = glh.VertexArrayObject(glh.gl.GL_TRIANGLE_FAN)
        self.pointslat = glh.GLBuffer()
        self.pointslon = glh.GLBuffer()

        self.prevmousepos = (0, 0)

        bs.Signal('cmdline_stacked').connect(self.cmdline_stacked)
        bs.Signal('radarmouse').connect(self.previewpoly)
        bs.Signal('panzoom').connect(self.dotted_dashed)
        bs.net.actnodedata_changed.connect(self.actdata_changed)

    def create(self):
        # --------------- Preview poly ---------------
        self.polyprev.create(vertex=POLYPREV_SIZE * 8,
                             color=palette.previewpoly, usage=glh.gl.GL_DYNAMIC_DRAW)

        # --------------- Polys ---------------
        self.allpolys.create(vertex=POLY_SIZE * 16, color=POLY_SIZE * 8)

        # --------------- Dotted lines ---------------
        self.alldotted.create(vertex=POLY_SIZE * 16, color=POLY_SIZE * 8)

        # --------------- Dotted lines ---------------
        self.alldashed.create(vertex=POLY_SIZE * 16, color=POLY_SIZE * 8)

        # --------------- Fills ---------------
        self.allpfill.create(vertex=POLY_SIZE * 24,
                             color=np.append(palette.polys, 50))

        # --------------- Points ---------------
        # OpenGL Buffers
        self.pointslat.create(POLY_SIZE * 16)
        self.pointslon.create(POLY_SIZE * 16)

        # Define vertices
        point_size = settings.point_size
        num_vert = 6
        angles = np.linspace(0., 2 * np.pi, num_vert)
        x = (point_size / 2) * np.sin(angles)
        y = (point_size / 2) * np.cos(angles)
        point_vert = np.empty((num_vert, 2), dtype=np.float32)
        point_vert.T[0] = x
        point_vert.T[1] = y

        # Define VAO
        self.allpoints.create(vertex=point_vert)
        self.allpoints.set_attribs(lat=self.pointslat, lon=self.pointslon, color=POLY_SIZE * 8,
                                   instance_divisor=1)

    def draw(self):
        actdata = bs.net.get_nodedata()
        # Send the (possibly) updated global uniforms to the buffer
        self.shaderset.set_vertex_scale_type(self.shaderset.VERTEX_IS_LATLON)

        # --- DRAW THE MAP AND COASTLINES ---------------------------------------------
        # Map and coastlines: don't wrap around in the shader
        self.shaderset.enable_wrap(False)

        # --- DRAW PREVIEW SHAPE (WHEN AVAILABLE) -----------------------------
        self.polyprev.draw()

        # --- DRAW CUSTOM SHAPES (WHEN AVAILABLE) -----------------------------
        if actdata.show_poly > 0:
            # Polys
            self.allpolys.draw()

            # Points (set vertex is screen size)
            self.shaderset.set_vertex_scale_type(self.shaderset.VERTEX_IS_SCREEN)
            self.allpoints.draw(n_instances=len(actdata.points))

            # Draw fills
            if actdata.show_poly > 1:
                self.shaderset.set_vertex_scale_type(self.shaderset.VERTEX_IS_LATLON)
                self.allpfill.draw()
        
    def cmdline_stacked(self, cmd, args):
        if cmd in ['AREA', 'BOX', 'POLY', 'POLYGON', 'CIRCLE', 'LINE', 'POLYLINE']:
            self.polyprev.set_vertex_count(0)

    # def previewpoly(self, shape_type, data_in=None):
    def previewpoly(self, mouseevent):
        if mouseevent.type() != mouseevent.MouseMove:
            return
        mousepos = (mouseevent.x(), mouseevent.y())
        # Check if we are updating a preview poly
        if mousepos != self.prevmousepos:
            cmd = console.get_cmd()
            nargs = len(console.get_args())
            if cmd in ['AREA', 'BOX', 'POLY', 'POLYLINE',
                        'POLYALT', 'POLYGON', 'CIRCLE', 'LINE'] and nargs >= 2:
                self.prevmousepos = mousepos
                try:
                    # get the largest even number of points
                    start = 0 if cmd == 'AREA' else 3 if cmd == 'POLYALT' else 1
                    end = ((nargs - start) // 2) * 2 + start
                    data = [float(v) for v in console.get_args()[start:end]]
                    data += self.glsurface.pixelCoordsToLatLon(*mousepos)
                    self.glsurface.makeCurrent()
                    if cmd is None:
                        self.polyprev.set_vertex_count(0)
                        return
                    if cmd in ['BOX', 'AREA']:
                        # For a box (an area is a box) we need to add two additional corners
                        polydata = np.zeros(8, dtype=np.float32)
                        polydata[0:2] = data[0:2]
                        polydata[2:4] = data[2], data[1]
                        polydata[4:6] = data[2:4]
                        polydata[6:8] = data[0], data[3]
                    else:
                        polydata = np.array(data, dtype=np.float32)

                    if cmd[-4:] == 'LINE':
                        self.polyprev.set_primitive_type(glh.gl.GL_LINE_STRIP)
                    else:
                        self.polyprev.set_primitive_type(glh.gl.GL_LINE_LOOP)

                    self.polyprev.update(vertex=polydata)


                except ValueError:
                    pass

    def dotted_dashed(self, finished=False):
        """
        Function: Update the dotted and dashed line segments
        Args:
            finished:   Not used
        Returns: -

        Created by: Bob van Dillen
        Date: 18-2-2022
        """

        # Get node data
        actdata = bs.net.get_nodedata()

        # Get coordinates of dotted/dashed line segments
        contours, fills, colors = zip(*actdata.dotted.values())
        dotted_coords = np.concatenate(contours)
        contours, fills, colors = zip(*actdata.dashed.values())
        dashed_coords = np.concatenate(contours)

        # Convert lat/lon to screen pixel coordinates
        dotted_x, dotted_y = self.glsurface.LatLonTopixelCoords(dotted_coords[::2], dotted_coords[1::2])
        dashed_x, dashed_y = self.glsurface.LatLonTopixelCoords(dashed_coords[::2], dashed_coords[1::2])

        # Determine angle between start and end of the line segments and length
        dotted_angle = np.arctan2(dotted_y[1::2]-dotted_y[::2], dotted_x[1::2]-dotted_x[::2])
        dotted_length = np.sqrt((dotted_x[1::2]-dotted_x[::2])*(dotted_x[1::2]-dotted_x[::2]) +
                                (dotted_y[1::2]-dotted_y[::2])*(dotted_y[1::2]-dotted_y[::2]))

        dashed_angle = np.arctan2(dashed_y[1::2]-dashed_y[::2], dashed_x[1::2]-dashed_x[::2])
        dashed_length = np.sqrt((dashed_x[1::2]-dashed_x[::2])*(dashed_x[1::2]-dashed_x[::2]) +
                                (dashed_y[1::2]-dashed_y[::2])*(dashed_y[1::2]-dashed_y[::2]))

    def line_interval(self, lat, lon, interval):
        """
        Function: Devide a line in segments
        Args:
            lat:        latitudes of lines [array]
            lon:        longitudes of lines [array]
            interval:   segment interval [float]
        Returns:
            lat:        latitudes of line segments [array]
            lon:        longitudes of line segments [array]

        Created by: Bob van Dillen
        Date: 18-2-2022
        """

        # Convert to screen pixel coordinates
        x, y = self.glsurface.LatLonTopixelCoords(lat, lon)

        angle = np.arctan2(y[1::2]-y[::2], x[1::2]-x[::2])
        # Reshape for processing
        angle = angle.reshape(len(angle), 1)
        length = np.sqrt((x[1::2]-x[::2])*(x[1::2]-x[::2]) + (y[1::2]-y[::2])*(y[1::2]-y[::2]))

        # Determine angle and distance between line start and end point
        # angle, dist = geo.kwikqdrdist_matrix(lat[::2], lon[::2], lat[1::2], lon[1::2])

        # Determine number of segments (including empty segments (line-empty-line-...))
        n_segments = length//interval

        # Determine amount of line segments (make number of segments odd)
        if (n_segments % 2) == 0:
            n_lines = n_segments - 1
        else:
            n_lines = n_segments
        # Reshape for processing
        n_lines = n_lines.reshape(len(n_lines), 1)

        # Create matrix for line segment coordinates
        '''
        Example:
        Start            Matrix        Angles
        [[x1 x2 x3]] * ( [[1 2 0]  * cos([[angle1 angle2 angle3]]) )
                          [1 2 3]
                          [1 0 0]]
        
        line 1 has 2 line segments
        line 2 has 3 line segments
        line 3 has 1 line segment
        '''
        n_matrix = np.arange(np.max(n_lines)+1)
        n_matrix = np.broadcast_to(n_matrix, (len(n_lines), np.max(n_lines)))
        n_matrix = n_matrix*(n_matrix <= n_lines)

        # x =









    def actdata_changed(self, nodeid, nodedata, changed_elems):
        ''' Update buffers when a different node is selected, or when
            the data of the current node is updated. '''
        # Shape data change
        if 'SHAPE' in changed_elems:
            # Make Current
            if nodedata.polys or nodedata.points:
                self.glsurface.makeCurrent()

            # Polys
            if nodedata.polys:
                contours, fills, colors = zip(*nodedata.polys.values())
                # Create contour buffer with color
                self.allpolys.update(vertex=np.concatenate(contours),
                                     color=np.concatenate(colors))

                # Create fill buffer
                self.allpfill.update(vertex=np.concatenate(fills))
            else:
                self.allpolys.set_vertex_count(0)
                self.allpfill.set_vertex_count(0)

            # Points
            if nodedata.points:
                contours, fills, colors = zip(*nodedata.points.values())
                # Update positions
                contours = np.concatenate(contours)
                self.pointslat.update(np.array(contours[::2], dtype=np.float32))
                self.pointslon.update(np.array(contours[1::2], dtype=np.float32))
                # Update colors
                self.allpoints.update(color=np.concatenate(colors))

        # ATCMODE data change
        if 'ATCMODE' in changed_elems:
            self.allpfill.set_attribs(color=np.append(palette.polys, 50))
            self.polyprev.set_attribs(color=palette.previewpoly)

