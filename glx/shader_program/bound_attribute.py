import ctypes
from itertools import count

import numpy as np

from ..gl_importer import OpenGL, gl

__all__ = []


class Indexer:

    def __init__(self, shape, strides):
        self.shape = shape
        self.strides = strides

    def __repr__(self):
        return "Indexer(max_index={}, indexed_advance={})".format(
            self.max_index,
            self.indexed_advance)

    def get_offset(self, index):
        return int(np.dot(index, self.strides))


class BoundAttribute:

    """
    A BufferBoundAttribute knows how to bind a single attribute in a shader.
    """

    def __init__(self, attribute, program, buffer_dtype):
        """
        Let the shape of the buffer_dtype have n dimensions.  Then,
        m = n - is_vector - (array_size is not None) ≥ 0.  Iff m > 0, this is
        an indexed attribute.
        * indexed attributes need to be bound at draw time, e.g.,
          vertex_array.attributes[attrib_name].bind(index).
        * program is an instance of ShaderProgram.
        * non-indexed attributes are bound now, which associates them
          with the vertex array (so binding the vertex array)
          automatically binds them.

        The constructor does not make any OpenGL calls.

        Parameters:
        * attribute: An Attribute object.
        * buffer_dtype:  The type of the numpy array that represents the
          buffer.

        Members:
        * attribute_location:  The location of the attribute in the program
          returned by glGetAttribLocation
        * stride:
          The stride between each vector item in bytes.
        * offset:
          The offset into the buffer of the first vector item in bytes.
        * integral:
          Whether the data in the buffer is integral or floating point.
        * shape:
          The the number of components in each vector item.  1 <= shape <= 4
        * gl_type:
          The GL type, e.g., GL_FLOAT or GL_INT
        * indexer:
          An instance of Indexer that translates from a sub-array index into
          the numpy array to a byte offset.  It also knows the maximum
          sub-array index for the purpose of assertions.  A sub-array is the
          leftover dimensions in the numpy array that are bound at call time.
        """
        self.attribute_name = attribute.name
        self.attribute_location = \
            program.attribute_name_to_location(attribute.name)
        self.stride = buffer_dtype.itemsize

        # Calculate offset and sub_dtype.
        self.offset = 0
        sub_dtype = buffer_dtype
        for lookup in attribute.lookup_sequence:
            sub_dtype, offset_delta = sub_dtype.fields[lookup]
            self.offset += offset_delta

        # Calculate shape and indexer.
        shape = sub_dtype.shape
        strides = np.zeros((), dtype=sub_dtype).strides
        if attribute.is_vector:
            if attribute.is_packed_array:
                raise ValueError
            if not (1 <= shape[-1] <= 4):
                raise ValueError
            self.vector_size = shape[-1]
            # The last entry of shape and stride have to do with this vector,
            # which has now been consumed.
            shape = shape[:-1]
            strides = strides[:-1]
        else:
            self.vector_size = 1

        if attribute.array_size is None:
            self.array_size = 1
            self.array_stride = 0
            self.packed_array_size = 1
        elif attribute.array_size <= shape[-1]:
            self.array_size = attribute.array_size
            self.array_stride = strides[-1]
            self.packed_array_size = ((self.array_size + 3) // 4
                                      if attribute.is_packed_array
                                      else self.array_size)
            if attribute.is_packed_array:
                self.array_stride *= 4
                self.vector_size = 4
            # The last entry of shape and stride have to do with this vector,
            # which has now been consumed.
            shape = shape[:-1]
            strides = strides[:-1]
        else:
            raise ValueError(
                f'Attribute array is supposed to have size '
                f'{attribute.array_size}, '
                f'but the buffer has dimensions {shape}')

        if shape:  # Any leftover dimensions must be indexed at call time.
            self.indexer = Indexer(shape, strides)
        else:
            self.indexer = None

        # Calculate gl_type and integral.
        self.gl_type = OpenGL.arrays.numpymodule.ARRAY_TO_GL_TYPE_MAPPING[
            sub_dtype.base]
        self.integral = np.issubdtype(sub_dtype, np.integer)
#       if self.attribute_name == 'data':
#           print(self.vector_size, self.array_size,
#                 self.packed_array_size,
#                 self.array_stride, sub_dtype,
#                 buffer_dtype)

    def enable_attributes(self):
        for i in range(self.packed_array_size):
            gl.glEnableVertexAttribArray(self.attribute_location + i)

    def bind(self, index=None):
        """
        index is the index into the dimensions (that are not consumed by
        is_vertex or array_index) of the vertex buffer (a numpy array).  For
        example, if the we have an exposed trait called "firing" on a cluster
        of size n, then index is a number in range(n).  If index is None, that
        means the exposed trait is a scalar.

        bind's job is to specify the location and data format of the array of
        vertex attributes.
        """
        offset = self.offset
        if index is not None:
            try:
                offset += self.indexer.get_offset(index)
            except ValueError:
                raise IndexError(
                    f"Bad index {index} on attribute '{self.attribute_name}'.")
        for attrib_index, this_offset in zip(range(self.packed_array_size),
                                             count(offset, self.array_stride)):
            pointer = ctypes.c_void_p(this_offset)
            this_attrib_location = self.attribute_location + attrib_index
            if self.integral:
                gl.glVertexAttribIPointer(this_attrib_location,
                                          self.vector_size,
                                          self.gl_type,
                                          self.stride,
                                          pointer)
            else:
                gl.glVertexAttribPointer(this_attrib_location,
                                         self.vector_size,
                                         self.gl_type,
                                         gl.GL_FALSE,
                                         self.stride,
                                         pointer)

    def __repr__(self):
        return ("BufferBoundAttribute("
                + ", ".join("{}={}".format(x, getattr(self, x))
                            for x in ['integral',
                                      'attribute_location',
                                      'shape',
                                      'gl_type',
                                      'stride',
                                      'offset',
                                      'indexer']) + ")")
