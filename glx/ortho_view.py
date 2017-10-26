import numpy as np

from .transformations import translation_matrix

__all__ = ['OrthoView']


class OrthoView:

    def __init__(self, zoom=np.ones(2), scroll=np.zeros(2, dtype='i')):
        """
        zoom
        * shape: (2,)
        * Conversion from scene space to screen space.
        scroll
        * shape: (2,)
        * Conversion from screen space to widget space.
        * Bottom-right is positive.

        There are three spaces:
        * scene
        * screen (the scene space zoomed)
        * widget (the screen space translated)
        * scaled_widget (device_pixel_ratio times smaller than widget)
        """
        super().__init__()
        # These variables do the transformation between spaces.
        self.zoom_ = np.ones(2) * zoom
        self.scroll_ = np.array(scroll, dtype='i')
        self.device_pixel_ratio = 1.0
        assert self.scroll.shape == (2,)

    # Settable vector properties ----------------------------------------------
    @property
    def zoom(self):
        return self.zoom_

    @zoom.setter
    def zoom(self, new_zoom):
        self.zoom_ = new_zoom

    @property
    def scroll(self):
        return self.scroll_

    @scroll.setter
    def scroll(self, new_scroll):
        self.scroll_ = new_scroll

    # Vector properties -------------------------------------------------------
    @property
    def flipped_zoom(self):
        return np.array([self.zoom_[0], -self.zoom_[1]])

    # Matrix properties -------------------------------------------------------
    @property
    def scene_to_screen(self):
        return np.diag([self.zoom[0], -self.zoom[1], 1.0, 1.0])

    @property
    def widget_to_screen(self):
        return translation_matrix([self.scroll_[0],
                                   self.scroll_[1],
                                   0.0])

    @property
    def widget_to_scene(self):
        """
        The inverse view matrix.
        """
        return self.screen_to_scene.dot(self.widget_to_screen)

    @property
    def screen_to_scene(self):
        return np.diag([1 / self.zoom[0], -1 / self.zoom[1], 1.0, 1.0])

    @property
    def screen_to_widget(self):
        return np.linalg.inv(self.widget_to_screen)

    @property
    def scene_to_widget(self):
        """
        This is the view matrix.
        """
        return self.screen_to_widget.dot(self.scene_to_screen)

    @property
    def scaled_widget_to_scene(self):
        return self.widget_to_scene.dot(self.scaled_widget_to_widget)

    @property
    def scaled_widget_to_screen(self):
        return self.widget_to_screen.dot(self.scaled_widget_to_widget)

    @property
    def scaled_widget_to_widget(self):
        return np.diag([self.device_pixel_ratio, self.device_pixel_ratio,
                        1.0, 1.0])
