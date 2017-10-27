import numpy as np

from glx import gl

from ..shader_program import Attribute, BufferDescription, ShaderProgram
from pkg_resources import resource_filename

__all__ = ['BasicShaderProgram']


class BasicShaderProgram(ShaderProgram):

    """
    The BasicShaderProgram draws pairs of (x, y) points, as for example
    triangle strips or lines.
    """

    def __init__(self, uniforms={}):
        super().__init__(vertex=['glx/glsl_shaders/basic'],
                         fragment=['glx/glsl_shaders/basic'])

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
