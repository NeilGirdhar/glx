from rectangle import Rect

from .transformations import four_components

__all__ = ['Viewport']


class Viewport:

    def __init__(self,
                 location=Rect(sizes=[1, 1]),
                 projection=None,
                 view=None):
        """
        A Viewport maps converts “points” in the unit square to widget or scene
        coördinates.  To do that it needs a projection, which maps between
        OpenGL and widget coördinates; and a view, which maps between widget
        and scene coördinates.

        A viewport has an optional location, which is a subregion of the unit
        square to which the viewport corresponds.
        """
        self.location = location
        self.projection = projection
        self.view = view

    def point_to_gl(self, point):
        retval = (((point[:2] - self.location.mins) * 2 / self.location.sizes)
                  - 1)
        retval[1] *= -1
        retval[self.location.sizes == 0.0] = 0.5
        return four_components(retval)

    def point_to_widget(self, point):
        return self.projection.gl_to_widget.dot(self.point_to_gl(point))

    def point_to_scene(self, point):
        return self.view.widget_to_scene.dot(self.point_to_widget(point))

    @staticmethod
    def viewports_point_to_scene(viewports, point):
        """
        Given an iterable of viewports, finds the one containing
        the point, and returns a pair:
        * viewport, and
        * scene coördinates of the point in the viewport.
        Otherwise return None.
        """
        for viewport in viewports:
            if point[:2] in viewport.location:
                return viewport, viewport.point_to_scene(point)
        return None, None

    def __repr__(self):
        return (f"{type(self).__name__}(location={self.location}, "
                f"projection={self.projection}, "
                f"view={self.view})")
