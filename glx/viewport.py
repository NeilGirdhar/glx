from rectangle import Rect

from .transformations import four_components

__all__ = ['Viewport']


class Viewport:
    """
    A Viewport maps “points” in the unit square to widget or scene
    coördinates.  To do that it needs a projection, which maps between
    OpenGL and widget coördinates; and a view, which maps between widget
    and scene coördinates.

    A viewport has an optional location, which is a subregion of the unit
    square to which the viewport corresponds.
    """

    def __init__(self, projection, view, location=Rect(sizes=[1, 1])):
        self.projection = projection
        self.view = view
        self.location = location

    # New methods -------------------------------------------------------------
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

    def scene_visible_rect(self):
        """
        The widget rectangle mapped to scene space.
        """
        return self.projection.widget_rect.transformed(
            self.view.widget_to_scene).rectified()

    # Static methods ----------------------------------------------------------
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

    # Magic methods -----------------------------------------------------------
    def __repr__(self):
        return (f"{type(self).__name__}(location={self.location}, "
                f"projection={self.projection}, "
                f"view={self.view})")
