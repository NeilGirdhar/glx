__all__ = ['Attribute']


class Attribute:

    def __init__(self,
                 name,
                 lookup_sequence,
                 *,
                 is_vector=False,
                 is_packed_array=False,
                 array_size=None):
        """
        * name is the name of the input attribute in the GLSL vertex
          shader code.  It is mainly used for error-reporting.
        * lookup_sequence is an iterable of names or indices, which constitute
          a path in the numpy array's dtype that locates the data in the numpy
          array.  Names are used to index into records, and indices are used
          to lookup into arrays.
        * is_vector is a Boolean that says whether this attribute is a vector,
          e.g., vec4.  Vector attributes have between 2 and 4 components.  The
          final dimension of the numpy array's shape must match the vector
          length.
        * is_packed_array is a Boolean that indicates that the data is packed
          as vectors of length 4, which means that the array_size times 4 is
          greater than or equal to the final dimension of the numpy array's
          shape.
        * array_size: an integer representing the size of the array
          attribute, e.g., float data[7].  For now, these must be bound to
          contiguous entries in the buffer numpy array.  Otherwise
          array_size is None to indicate a scalar.
        """
        self.name = name
        self.lookup_sequence = lookup_sequence
        self.is_vector = is_vector
        self.array_size = array_size
        self.is_packed_array = is_packed_array
        if is_vector and is_packed_array:
            raise ValueError

    def __repr__(self):
        return (f"{type(self).__qualname__}("
                f"{self.name}, {self.lookup_sequence}, "
                f"is_vector={self.is_vector}, "
                f"is_packed_array={self.is_packed_array}, "
                f"array_size={self.array_size})")
