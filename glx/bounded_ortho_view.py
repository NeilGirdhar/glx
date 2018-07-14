from contextlib import contextmanager

import numpy as np
from rectangle import Rect

from .ortho_view import OrthoView

__all__ = ['BoundedOrthoView']


class BoundedOrthoView(OrthoView):
    """
    Like an OrthoView, BoundedOrthoView converts between four spaces:
    * scene
    * screen (the scene space zoomed)
    * widget (the screen space translated)
    * scaled_widget (device_pixel_ratio times smaller than widget)
    It also keeps track of
    * the size of the widget in screen space,
    * the represented area in scene space,
    * a range of valid zoom levels, and
    * a border.
    """

    def __init__(self,
                 zoom,
                 scroll,
                 scene_rect,
                 border,
                 zoom_range,
                 widget_size):
        # pylint: disable=too-many-arguments
        """
        * zoom
          * shape: (2,)
          * Conversion from scene space to screen space.
        * scroll
          * shape: (2,)
          * Conversion from screen space to widget space.
          * Bottom-right is positive.
        * scene_rect
          * Rect of shape: (2,)
          * The rectangle of the scene that is represented.
          * in scene space
        * border
          * float
          * The border in pixels (screen space).
        * zoom_range
          * shape: (2,)
          * The minimum and maximum zoom for both axes.
          * Limits the zoom whenever it's set.
        * widget_size
          * shape: (2,)
          * The size of the widget in screen space.
          * Limits the scroll whenever it's set.
        """
        super().__init__(zoom=zoom, scroll=scroll)
        self.scene_rect_ = scene_rect
        self.border = border
        self.zoom_range = zoom_range
        self.widget_size_ = widget_size

    # Settable vector properties ----------------------------------------------
    @OrthoView.zoom.setter
    def zoom(self, new_zoom):
        if not isinstance(new_zoom, np.ndarray):
            raise TypeError
        # Clip the new_zoom to zoom_range
        OrthoView.zoom.fset(self, np.clip(new_zoom, *self.zoom_range))

    @OrthoView.scroll.setter
    def scroll(self, new_scroll):
        OrthoView.scroll.fset(self, self.scroll_range_rect.clamped(new_scroll))

    @property
    def scene_rect(self):
        return self.scene_rect_

    @scene_rect.setter
    def scene_rect(self, new_scene_rect):
        self.scene_rect_ = new_scene_rect

    # Vector properties -------------------------------------------------------
    @property
    def widget_size(self):
        return self.widget_size_

    @widget_size.setter
    def widget_size(self, new_widget_size):
        self.widget_size_ = new_widget_size
        self.scroll = self.scroll  # Clamp the scroll.
        self.widget_resized_signal.emit(new_widget_size)

    # Rectangle properties ----------------------------------------------------
    @property
    def screen_rect(self):
        return (self.scene_rect * self.flipped_zoom).rectified().bordered(
            self.border)

    @property
    def scroll_range_rect(self):
        return Rect(self.screen_rect.mins,
                    self.screen_rect.maxes - self.widget_size)

    def scene_visible_rect(self, widget_rect):
        """
        The scene visible rect is a rectangle in scene space that surrounds
        what you can see in gl space given a projection matrix.
        The projection matrix maps widget space to gl space.
        """
        return widget_rect.transformed(self.widget_to_scene).rectified()

    # Value updaters ----------------------------------------------------------
    def hold_and_set_scene_rect(self,
                                widget_hold_point,
                                scene_rect):
        with self.hold_position(widget_hold_point):
            self.scene_rect = scene_rect

    @contextmanager
    def hold_position(self, widget_hold_point):
        def scene_hold_point(widget_hold_point):
            if widget_hold_point is None:
                return np.zeros(4)
            return self.widget_to_scene.dot(widget_hold_point)
        shp = scene_hold_point(widget_hold_point)
        yield
        delta_shp = (shp - scene_hold_point(widget_hold_point))[:2]
        self.scroll += (delta_shp * self.flipped_zoom).astype(np.int32)

    def __repr__(self):
        return (f"{type(self).__name__}("
                f"zoom={self.zoom}, "
                f"scroll={self.scroll}, "
                f"scene_rect={self.scene_rect}, "
                f"border={self.border}, "
                f"zoom_range={self.zoom_range}, "
                f"widget_size={self.widget_size}"
                ")")
