from rectangle import Rect

from ..transformations import four_components

__all__ = ['Viewport']


class Viewport:
    """
    A Viewport contains
    * a projection, which maps between OpenGL and widget coördinates, and
    * a view, which maps between widget and scene coördinates.

    Theoretically viewports should also have a location within the widget.
    """

    def __init__(self, projection, view):
        self.projection = projection
        self.view = view

    # New methods -------------------------------------------------------------
    def scene_visible_rect(self):
        """
        The widget rectangle mapped to scene space.
        """
        return self.projection.widget_rect.transformed(
            self.view.widget_to_scene).rectified()

    # Magic methods -----------------------------------------------------------
    def __repr__(self):
        return (f"{type(self).__name__}("
                f"projection={self.projection}, "
                f"view={self.view})")
