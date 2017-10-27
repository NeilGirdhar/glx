import numpy as np
from pkg_resources import resource_filename

from ..shader_program import Attribute, BufferDescription, ShaderProgram
from .gl_importer import gl

__all__ = ['BasicShaderProgram']


class BasicShaderProgram(ShaderProgram):

    """
    The BasicShaderProgram draws pairs of (x, y) points, as for example
    triangle strips or lines.
    """

    def __init__(self, uniforms={}):
        super().__init__(
            vertex=[resource_filename('glx', 'glsl_shaders/basic.vert')],
            fragment=[resource_filename('glx', 'glsl_shaders/basic.frag')])

        with self.bind_context(uniforms):
            # Create one buffer.
            self.buffer, = gl.glGenBuffers(1)

            # Create one vertex array and describe it.
            # The array is fed using a numpy array of shape (n, 2), which
            # describes n (x, y) pairs.
            self.vertex_array, = self.create_vertex_arrays(
                [BufferDescription(
                    self.buffer,
                    np.dtype(('f', (2,))),
                    [Attribute('vertex', [], is_vector=True)])])
