import numpy as np
from rectangle import Rect

from glx import BoundedOrthoView, OrthoProjection, Viewport


class Geometry:
    """
    A Geometry manages all of the viewports and measurement-related variables
    for a widget.
    """
    DEFAULT_ZOOM = [100.0, 100.0]
    LAYOUT_BORDER = 0
    ZOOM_RANGE = [[0.1, 10.0], [2000.0, 400.0]]

    def __init__(self):
        ortho_view = BoundedOrthoView(
            scene_rect=Rect(),
            border=self.LAYOUT_BORDER,
            zoom=np.array(self.DEFAULT_ZOOM),
            scroll=np.zeros(2, dtype='i'),
            zoom_range=self.ZOOM_RANGE,
            widget_size=np.zeros(2, dtype='i'))

        # Create the viewport.
        self.viewport = Viewport(
            projection=OrthoProjection(),
            view=ortho_view)

    # Properties --------------------------------------------------------------
    @property
    def scene_visible_rect(self):
        return self.viewport.scene_visible_rect()

    @property
    def projection_matrix(self):
        return self.viewport.projection.widget_to_gl.astype('f')

    @property
    def view_matrix(self):
        return self.viewport.view.scene_to_widget.astype('f')

    # Setters -----------------------------------------------------------------
    def set_device_pixel_ratio(self, device_pixel_ratio):
        self.viewport.view.device_pixel_ratio = device_pixel_ratio

    def set_widget_size(self, widget_size):
        """
        widget_size is a tuple (width, height) in screen pixels.

        This will change the projection matrix.
        """
        v = self.viewport
        v.projection.widget_rect = Rect(
            mins=[0, 0],
            maxes=[widget_size[0], widget_size[1]])
        v.view.widget_size = v.projection.widget_rect.sizes

    def set_scene_rect(self, new_scene_rect):
        v = self.viewport
        if v.view.scene_rect:
            # If the scene_rect is not empty, hold its center.
            v.view.hold_and_set_scene_rect(v.projection.widget_rect.center,
                                           new_scene_rect)
        else:
            v.view.scene_rect = new_scene_rect

    # Attribute setters -------------------------------------------------------
    def apply_projection_matrix(self, shader_programs):
        projection_matrix = self.projection_matrix
        for shader_program in shader_programs:
            with shader_program.bind_context(
                    uniforms={'projection': projection_matrix}):
                pass

    def apply_view_matrix(self, shader_programs):
        view_matrix = self.view_matrix
        for shader_program in shader_programs:
            with shader_program.bind_context(
                    uniforms={'view': view_matrix}):
                pass
