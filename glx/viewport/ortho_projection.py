import numpy as np
from rectangle import Rect

from ..transformations import clip_matrix

__all__ = ['OrthoProjection']


class OrthoProjection:
    """
    A projection coverts between two spaces:
    * widget (determined externally by the widget_rect)
    * gl (the gl coördinates, which range from -1 to 1 on each axis)
    """

    def __init__(self, widget_rect=Rect(sizes=[1, 1])):
        """
        widget_rect
        * shape: (2,)
        * in screen coordinates
        """
        self.widget_rect = widget_rect

    # Matrix properties:
    @property
    def widget_to_gl(self):
        """
        This is the projection matrix.
        """
        wr = self.widget_rect
        return (np.diag([1, -1, 1, 1])
                @ clip_matrix(wr.mins[0], wr.maxes[0],
                              wr.mins[1], wr.maxes[1],
                              -1.0, 1.0))

    @property
    def gl_to_widget(self):
        """
        This is the inverse projection matrix.
        """
        return np.linalg.inv(self.widget_to_gl)

    def __repr__(self):
        return f"{type(self).__name__}(widget_rect={self.widget_rect})"
