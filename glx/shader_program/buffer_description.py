import numpy as np

__all__ = ['BufferDescription']


class BufferDescription:

    def __init__(self, buffer_index, buffer_dtype, attributes):
        """
        * buffer_index is a buffer object index (as returned by glGenBuffers).
        * buffer_dtype is the dtype of the numpy array that will be loaded
          into the buffer.
        * attributes is a reiterable of BoundAttribute objects.
        """
        if not isinstance(buffer_index, np.uint32):
            raise TypeError
        if not isinstance(buffer_dtype, np.dtype):
            raise TypeError

        self.buffer_index = buffer_index
        self.buffer_dtype = buffer_dtype
        self.attributes = attributes
