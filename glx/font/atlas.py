from contextlib import contextmanager

import numpy as np

from glx import gl as gl


class Atlas:

    class OverfullError(BaseException):
        pass

    class Line:

        def __init__(self, y):
            """
            (x, y) is the top-left corner.
            """
            self.y = y
            self.x = 0
            self.height = 0

    def __init__(self, font, size, texture_unit, guard=1):
        self.creation_id = 0
        self.clear()
        self.resize(size)
        self.texture_unit = texture_unit
        self.font = font
        self.guard = guard

        with self.font.shader_program.bind_context():
            # Create sampler.
            self.sampler_object, = gl.glGenSamplers(1)

            # Create texture.
            self.texture, = gl.glGenTextures(1)

            # Bind sampler to texture unit, and set parameters.
            gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
            gl.glBindSampler(self.texture_unit, self.sampler_object)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_WRAP_S,
                                   gl.GL_CLAMP_TO_EDGE)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_WRAP_T,
                                   gl.GL_CLAMP_TO_EDGE)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_MAG_FILTER,
                                   gl.GL_LINEAR)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_MIN_FILTER,
                                   gl.GL_LINEAR)
            gl.glBindSampler(self.texture_unit, 0)

            # Set uniform with texture unit.
            self.font.shader_program.font_atlas(np.int32(self.texture_unit))

    def resize(self, size):
        self.creation_id += 1
        self.needs_update = True
        self.texture_array = np.empty((size, size), dtype=np.ubyte)

    def clear(self):
        self.needs_update = True
        self.lines = []
        self.y = 0  # rows used

    @property
    def size(self):
        return self.texture_array.shape[0]

    def new_line(self):
        if self.lines:
            self.y += self.lines[-1].height + self.guard
        line = Atlas.Line(self.y)
        self.lines.append(line)
        return line

    def add_char(self, bitmap):
        while True:
            try:
                if bitmap.width > self.size:
                    raise Atlas.OverfullError
                for line in self.lines:
                    if (bitmap.width + line.x <= self.size
                            and (bitmap.rows <= line.height
                                 or line is self.lines[-1])):
                        break
                else:
                    line = self.new_line()
                    if self.y + bitmap.rows > self.size:
                        raise Atlas.OverfullError

                # Copy bitmap into texture_array.
                self.texture_array[line.y: line.y + bitmap.rows,
                                   line.x: line.x + bitmap.width].flat = \
                    bitmap.buffer
                self.needs_update = True

                line.height = max(bitmap.rows, line.height)
                bottom_left = [line.x, line.y + bitmap.rows]
                top_right = [line.x + bitmap.width, line.y]
                line.x += bitmap.width + self.guard
                return np.array(bottom_left + top_right) / self.size
            except Atlas.OverfullError:
                self.resize(self.size * 2)
                self.font.repopulate()

    def update_texture(self):
        # Bind texture to texture unit, set paramters and upload texture.
        # ActiveTexture must precede TexParameter, BindTexture,
        # and TexImage.
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D,
                        0,
                        gl.GL_R8,
                        self.texture_array.shape[1],
                        self.texture_array.shape[0],
                        0,
                        gl.GL_RED,
                        gl.GL_UNSIGNED_BYTE,
                        self.texture_array)
        self.needs_update = False

    @contextmanager
    def draw_context(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glBindSampler(self.texture_unit, self.sampler_object)
        yield
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glBindSampler(self.texture_unit, 0)
