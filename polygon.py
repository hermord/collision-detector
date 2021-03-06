from helpers import getRandomColor
import constants as const
import geometry

import pyglet.gl as gl
from pyglet.graphics import draw
from shape import Shape

class Polygon(Shape, geometry.Polygon):
    # The respresentation of a polygon is a list of dots (vertices)
    def __init__(self, dots):
        # Calculate bounds as minimum/maximum values of x and y for all dots
        max_x = max(x for x, y in dots)
        min_x = min(x for x, y in dots)
        max_y = max(y for x, y in dots)
        min_y = min(y for x, y in dots)

        # This will be the bounding box.
        Shape.__init__(self, geometry.Point(min_x, min_y), max_x-min_x, max_y-min_y)

        geometry.Polygon.__init__(self, dots)

        self.gl_vertices = self.get_gl_vertices()

        self.color=getRandomColor()


    def render(self):
        self.set_colliding_flag()

        self.gl_vertices = self.get_gl_vertices()

        # Without this, number of points in polygon is undefined to pyglet.
        gl.glEnable(gl.GL_PRIMITIVE_RESTART)
        gl.glPrimitiveRestartIndex(-1)

        gl.glEnable(gl.GL_LINE_SMOOTH)

        vertices = round(len(self.gl_vertices)/2)

        gl.glColor4f(*self.color)
        draw(vertices, gl.GL_POLYGON, ('v2f', self.gl_vertices))

        if(self.colliding):
            gl.glLineWidth(const.BORDER_WIDTH)
            gl.glColor4f(*const.COLOR_COLLIDING[self.colliding])
            draw(vertices-1, gl.GL_LINE_LOOP, ('v2f', self.gl_vertices[:-2]))  # Exclude last vertex (the primitive restart)

        gl.glDisable(gl.GL_LINE_SMOOTH)

    def updateBounds(self):
        # Find maxima of x and y coordinates
        max_x = max(x for x, y in self.dots)
        min_x = min(x for x, y in self.dots)
        max_y = max(y for x, y in self.dots)
        min_y = min(y for x, y in self.dots)
        self.bounds.x, self.bounds.y = min_x, min_y
        self.bounds.width = max_x-min_x
        self.bounds.height = max_y-min_y


    def collidingWith(self, item):
        # First, check if bounding rects collide. If not, there is no collision.
        if(not geometry.check_collide_rectangles(self.bounds, item.bounds)):
            return const.COLLISION_NONE

        # Item is a polygon
        if(type(self) is type(item)):
            # If both are rectangles, use rectangle-specific algo
            if(hasattr(self, 'rectangle') and hasattr(item, 'rectangle')):
                # Rectangle collision is equivalent to bounds collision, and we've already checked that
                return True
            else:
                return const.COLLISION_SAT if\
                    geometry.check_collide_polygons(self.dots, item.dots, self.normals, item.normals) else const.COLLISION_NONE
        # Item is a circle
        elif(issubclass(type(item), geometry.Circle)):
            return const.COLLISION_SAT if geometry.check_collide_polygon_circle(self.dots, item, self.normals) else const.COLLISION_NONE
        else:
            raise TypeError("Only shapes can be checked for collisions")
