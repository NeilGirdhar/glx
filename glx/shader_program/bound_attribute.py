import ctypes
from itertools import count

import numpy as np

from ..gl_importer import OpenGL, gl

__all__ = []


class Indexer:

    def __init__(self, shape, strides):
        """
        Members
        * shape:
          The shapes of the indexed dimensions.
        * strides:
          The strides in bytes of the indexed dimensions.
        """
        self.shape = shape
        self.strides = strides

    def __repr__(self):
        return "Indexer(shape={}, strides={})".format(
            self.shape,
            self.strides)

    def get_offset(self, index):
        return int(np.dot(index, self.strides))


class BoundAttribute:

    """
    A BoundAttribute knows how to bind a single attribute in a shader.
    """

    def __init__(self, attribute, program, buffer_dtype):
        """
        The constructor accepts:
        * attribute: An Attribute object that describes the location of some
          data within a numpy array.
        * program: An instance of ShaderProgram.
        * buffer_dtype:  The type of the numpy array that represents the
          buffer.

        The constructor calculates the parameters of the OpenGL calls (e.g.,
        glVertexAttribPointer) that will need to be made when the
        BoundAttribute is bound.

        The constructor sets members relating to calling OpenGL functions:
        * attribute_location:  The location of the attribute in the program
          returned by glGetAttribLocation.
        * stride:
          The byte offset between consecutive “vertex attributes”.
        * offset:
          The offset in bytes into the buffer of the first “vertex attribute”.
        * integral:
          Whether the data in the buffer is integral or floating point.
        * gl_type:
          The GL type, e.g., GL_FLOAT or GL_INT
        * vector_size:
          The number of components per “vertex attribute”. Must be 1, 2, 3,
          or 4.
        * array_size:
          The number of OpenGL attributes represented by this BoundAttribute
          object.
        * array_stride:
          The stride in bytes between each component of the array.

        The constructor also sets members relating to indexing:
        * indexer:
          An instance of Indexer that translates from a sub-array index into
          the numpy array to a byte offset.  It also knows the maximum
          sub-array index for the purpose of assertions.  A sub-array is the
          leftover dimensions in the numpy array that are bound at call time.

        Let the shape of the buffer_dtype have n dimensions.  Then,
        m = n - is_vector - (array_size is not None) ≥ 0.  Iff m > 0, this is
        an indexed attribute.
        * indexed attributes need to be bound at draw time, e.g.,
          vertex_array.attributes[attrib_name].bind(index).
        * non-indexed attributes can be bound once to associate them with the
          vertex array (so binding the vertex array) automatically binds them.
        """
        self.attribute_name = attribute.name
        self.attribute_location = \
            program.attribute_name_to_location(attribute.name)
        self.stride = buffer_dtype.itemsize

        # Calculate offset and sub_dtype.
        self.offset = 0
        sub_dtype = buffer_dtype
        for lookup in attribute.lookup_sequence:
            if sub_dtype.fields is None:
                if not isinstance(lookup, int):
                    raise TypeError
                strides = np.zeros((), dtype=sub_dtype).strides
                if lookup > sub_dtype.shape[0]:
                    raise ValueError
                offset_delta = lookup * strides[0]
                sub_dtype = np.dtype((sub_dtype.base, sub_dtype.shape[1:]))
            else:
                if not isinstance(lookup, str):
                    raise TypeError
                sub_dtype, offset_delta = sub_dtype.fields[lookup]

            self.offset += offset_delta

        # Calculate shape and indexer.
        shape = sub_dtype.shape
        strides = np.zeros((), dtype=sub_dtype).strides

        def consume_last_dimension():
            nonlocal shape
            nonlocal strides
            # The last entry of shape and stride have to do with this
            # vector, which has now been consumed.
            shape = shape[:-1]
            strides = strides[:-1]

        if attribute.is_packed_array:
            if attribute.is_vector:
                raise ValueError
            if shape[-1] <= (attribute.array_size - 1) * 4:
                raise ValueError(
                    "The attribute's array_size is unnecessarily large given "
                    "the Numpy array shape's final component "
                    f"{shape[-1]}.")
            if attribute.array_size is None:
                raise ValueError(
                    "The array_size of a packed array is not specified")

            self.vector_size = 4
            self.array_size = attribute.array_size
            self.array_stride = strides[-1] * 4
            consume_last_dimension()
        else:
            if attribute.is_vector:
                if not (1 <= shape[-1] <= 4):
                    raise ValueError

                self.vector_size = shape[-1]
                consume_last_dimension()
            else:
                self.vector_size = 1

            if attribute.array_size is None:
                self.array_size = 1
                self.array_stride = 0
            else:
                if attribute.array_size != shape[-1]:
                    raise ValueError(
                        f'Attribute array is supposed to have size '
                        f'{attribute.array_size}, '
                        f'but the buffer has dimensions {shape}')
                self.array_size = attribute.array_size
                consume_last_dimension()

        if shape:  # Any leftover dimensions must be indexed at call time.
            self.indexer = Indexer(shape, strides)
        else:
            self.indexer = None

        # Calculate gl_type and integral.
        self.gl_type = OpenGL.arrays.numpymodule.ARRAY_TO_GL_TYPE_MAPPING[
            sub_dtype.base]
        self.integral = np.issubdtype(sub_dtype, np.integer)

    def enable_attributes(self):
        for i in range(self.array_size):
            gl.glEnableVertexAttribArray(self.attribute_location + i)

    def bind(self, index=None):
        """
        bind makes the OpenGL calls to specify the location and data format of
        the array of vertex attributes.
        * index is the index into the dimensions (that are not consumed by
          is_vertex or array_index) of the vertex buffer (a numpy array).
        """
        offset = self.offset
        if index is not None:
            try:
                offset += self.indexer.get_offset(index)
            except ValueError as e:
                raise IndexError(
                    f"Bad index {index} on attribute '{self.attribute_name}' "
                    f"that wants {len(self.indexer.strides)} components.") \
                    from e
        for attrib_index, this_offset in zip(
                range(self.array_size),
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

    def __str__(self):
        return ("BoundAttribute("
                + ", ".join("{}={}".format(x, getattr(self, x))
                            for x in ['attribute_location',
                                      'stride',
                                      'offset',
                                      'integral',
                                      'gl_type',
                                      'vector_size',
                                      'array_size',
                                      'array_stride',
                                      'indexer']) + ")")
