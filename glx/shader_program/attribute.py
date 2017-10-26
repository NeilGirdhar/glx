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
        * lookup_sequence is an iterable of names, which constitute a path in
          the numpy array's dtype that locates the data in the numpy array.
        * is_vector is a Boolean that says whether this attribute is a vector,
          e.g., vec4.  Vector attributes have between 2 and 4 components.  The
          final dimension of the numpy array's shape must match the vector
          lenth.
        * array_size: an integer representing the size of the array
          attribute, e.g., float data[7].  For now, these must be bound to
          contiguous entries in the buffer numpy array.  Otherwise
          array_size is None to indicate a scalar.
        * is_packed_array is a Boolean that indicates that the array is stored
          as vec4 and possibly one final scalar or vector element for excess
          elements named "extra_" + name.
        """
        self.name = name
        self.is_vector = is_vector
        self.array_size = array_size
        self.is_packed_array = is_packed_array
        self.lookup_sequence = lookup_sequence
