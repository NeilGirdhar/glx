from contextlib import contextmanager

from glx import gl as gl

from .bound_attribute import BoundAttribute

__all__ = []


class VertexArray:

    """
    A VertexArray manages an OpenGL vertex array, which is a collection of
    bindings for the varying variables in a ShaderProgram.  Instances of
    BoundAttribute are created to do the individual binding.
    """

    def __init__(self, program, buffer_description):
        """
        * program is a ShaderProgram object.
        * buffer_description is a BufferDescription object.

        Creating this object will enable the specified attributes, which
        associates them with the bound buffer.
        """
        # The GL vertex array index.
        self.vertex_array = gl.glGenVertexArrays(1)
        # A map from attribute name to an instance of BoundAttribute.
        self.attributes = {}

        with self.bind_context():
            # Bind buffer for attribute name.
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER,
                            buffer_description.buffer_index)

            for attribute in buffer_description.attributes:
                bound_attribute = BoundAttribute(
                    attribute,
                    program,
                    buffer_description.buffer_dtype)
                bound_attribute.enable_attributes()
                if not bound_attribute.indexer:
                    bound_attribute.bind()
                self.attributes[attribute.name] = bound_attribute

            # Finished describing buffers.
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def delete(self):
        assert self.vertex_array is not None
        gl.glDeleteVertexArrays(1, [self.vertex_array])
        self.vertex_array = None

    @contextmanager
    def bind_context(self):
        if self.vertex_array is None:
            yield
        else:
            gl.glBindVertexArray(self.vertex_array)
            try:
                yield
            finally:
                gl.glBindVertexArray(0)
