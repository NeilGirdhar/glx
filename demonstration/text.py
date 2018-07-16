import sys

import moderngl
import numpy as np
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from rectangle import Rect

from geometry import Geometry
from glx import DisplayList, Font, gl, translation_matrix

background = np.array([0.0, 0.16862745098039217, 0.21176470588235294, 1.0])
off_white = np.array([0.9333, 0.9098, 0.8353, 1.0])


class QModernGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()

        self.context = None
        self.screen = None

    def initializeGL(self):
        super().initializeGL()
        self.context = moderngl.create_context()


class MyWidget(QModernGLWidget):

    def __init__(self):
        self.geometry = Geometry()
        super().__init__()
        self.geometry.set_device_pixel_ratio(self.devicePixelRatio())
        self.text_location = None

        new_scene_rect = Rect([0.0, 0.0],
                              [10.0, 1.0])
        self.geometry.set_scene_rect(new_scene_rect)

    def initializeGL(self):
        super().initializeGL()

        # Set up font.
        self.font = Font('/Library/Fonts/Arial Unicode.ttf', 24)
        with self.font.shader_program.bind_context():
            self.font.shader_program.color(off_white)

        self.text_display_list = DisplayList(self.font)
        self.text_display_list.set_text("Hello world!")

        widget_rect = self.size()
        width = widget_rect.width()
        height = widget_rect.height()
        self.do_resize(width, height)

    def resizeGL(self, width, height):
        super().resizeGL(width, height)
        self.do_resize(width, height)

    def do_resize(self, width, height):
        self.geometry.set_widget_size([width, height])
        self.geometry.apply_projection_matrix([self.font.shader_program])
        self.text_location = np.array(
            [(0.9 * self.geometry.scene_visible_rect.mins[0]
              + 0.1 * self.geometry.scene_visible_rect.maxes[0]),
             0.1,
             0,
             1])

    def paintGL(self):
        framebuffer = self.defaultFramebufferObject()
        mgl_framebuffer = self.context.detect_framebuffer(
            self.defaultFramebufferObject())

        # Clear the buffer.
        mgl_framebuffer.clear(*background)

        with self.context.scope(
                framebuffer=mgl_framebuffer,
                enable_only=moderngl.BLEND):
            pass

            # Set up blending.
            gl.glBlendEquationi(framebuffer, gl.GL_FUNC_ADD)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            gl.glEnable(gl.GL_BLEND)

            # Get matrices.
            view_matrix = self.geometry.view_matrix
            model_matrix = translation_matrix([0.0, 0.0, 0.0]).astype('f')

            # Paint the text.
            with self.font.draw_context():
                location = view_matrix.dot(model_matrix.dot(
                    self.text_location))
                self.text_display_list.draw(location)


if __name__ == '__main__':
    gl_format = QSurfaceFormat()
    gl_format.setVersion(4, 1)
    gl_format.setAlphaBufferSize(0)
    gl_format.setDepthBufferSize(0)
    gl_format.setProfile(QSurfaceFormat.CoreProfile)
    gl_format.setSamples(8)
    gl_format.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
    gl_format.setSwapInterval(0)
    QSurfaceFormat.setDefaultFormat(gl_format)

    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())
