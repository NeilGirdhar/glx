from contextlib import contextmanager

import numpy as np

from ..gl_importer import gl as gl
from ..tools import next_power_of_two

__all__ = ['CodeLookup']


class CodeLookup:

    def __init__(self, font, size, texture_unit):
        self.clear()
        self.resize(size)
        self.texture_unit = texture_unit
        self.font = font

        with self.font.shader_program.bind_context():
            # Create sampler.
            self.sampler_object, = gl.glGenSamplers(1)

            # Create texture.
            self.texture, = gl.glGenTextures(1)

            # Bind sampler to texture unit, and set parameters.
            gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
            gl.glBindSampler(self.texture_unit, self.sampler_object)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glSamplerParameteri(self.sampler_object,
                                   gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)

            # Set uniform with texture unit.
            self.font.shader_program.code_to_texture(
                np.int32(self.texture_unit))

    def resize(self, size):
        self.data = np.empty((next_power_of_two(size), 4), dtype='f')
        self.needs_update = True

    def clear(self):
        self.used = 0
        self.needs_update = True

    @property
    def size(self):
        return self.data.shape[0]

    def add_char(self, uvs):
        if self.used == self.size:
            old_data = self.data
            old_size = self.size
            self.resize(2 * self.size)
            self.data[0: old_size] = old_data
        self.data[self.used] = uvs
        self.used += 1
        self.needs_update = True

    def update_texture(self):
        # Bind texture to texture unit, set paramters and upload texture.
        # ActiveTexture must precede TexParameter, BindTexture,
        # and TexImage.
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_1D, self.texture)
        gl.glTexImage1D(gl.GL_TEXTURE_1D,
                        0,
                        gl.GL_RGBA32F,
                        self.data.shape[0],
                        0,  # border
                        gl.GL_RGBA,
                        gl.GL_FLOAT,
                        self.data)
        self.needs_update = False

    @contextmanager
    def draw_context(self):
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_1D, self.texture)
        gl.glBindSampler(self.texture_unit, self.sampler_object)
        yield
        gl.glActiveTexture(gl.GL_TEXTURE0 + self.texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glBindSampler(self.texture_unit, 0)
