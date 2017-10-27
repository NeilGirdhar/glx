import re

import numpy as np

from ..gl_importer import gl

__all__ = ['UniformDescription']


class UniformDescription:

    def __init__(self, name, array_length, is_matrix, method_name, dtype):
        self.name = name
        self.array_length = array_length
        self.is_matrix = is_matrix
        self.method_name = method_name
        self.dtype = dtype

    # New methods -------------------------------------------------------------
    def create_method(self, program_index):
        index = gl.glGetUniformLocation(program_index, self.name)
        method = getattr(gl, 'gl' + self.method_name)

        def internal_create_method(index, method, array_length):
            # pylint: disable=cell-var-from-loop
            if self.is_matrix:
                def h(ref):
                    # assert ref.dtype == h.description.dtype
                    method(index, array_length, gl.GL_TRUE, ref)
            elif self.array_length is not None:
                def h(ref):
                    # assert ref.dtype == h.description.dtype
                    method(index, array_length, ref)
            else:
                def h(value):
                    # assert value.dtype == h.description.dtype
                    method(index, value)
            h.description = self
            return h
        return internal_create_method(index, method, self.array_length)

    @classmethod
    def parse_shader_text(cls, shader_text):
        """
        Parses the shader text and returns an iterable of UniformDescription
        objects.
        """
        for type_, name, array in re.findall(
                r'^uniform (\w*|unsigned int) (\w*)(?:\[(\d*)\]|);',
                shader_text,
                re.MULTILINE):

            array_length = int(array) if array else None

            u = (cls.parse_vector(name, type_, array_length)
                 or cls.parse_matrix(name, type_, array_length)
                 or cls.parse_scalar(name, type_, array_length))
            if u is None:
                raise ValueError(f"Type {type_} not understood")
            yield u

    @classmethod
    def parse_vector(cls, name, type_, array_length):
        """
        Returns a UniformDescription given parsed values:
        * name, a string,
        * type_, a string such as bvec4, and
        * array_length, an integer or None.
        """
        # Check if type_ is a vector.
        m = re.match('(i|u|d|b|)vec(.)', type_)
        if not m:
            return None
        type_code, shape = m.groups()
        base_type = cls._translate_type_code(type_code)
        return UniformDescription(name,
                                  array_length or 1,
                                  False,
                                  f'Uniform{shape}{base_type}v',
                                  cls._dtype_of_base_type(base_type))

    @classmethod
    def parse_matrix(cls, name, type_, array_length):
        """
        Returns a UniformDescription given parsed values:
        * name, a string,
        * type_, a string such as bvec4, and
        * array_length, an integer or None.
        """
        m = re.match('(d|)mat(.*)$', type_)
        if not m:
            return None
        type_code, shape = m.groups()
        base_type = cls._translate_type_code(type_code)
        return UniformDescription(name,
                                  array_length or 1,
                                  True,
                                  f'UniformMatrix{shape}{base_type}v',
                                  cls._dtype_of_base_type(base_type))

    @classmethod
    def parse_scalar(cls, name, type_, array_length):
        """
        Returns a UniformDescription given parsed values:
        * name, a string,
        * type_, a string such as bvec4, and
        * array_length, an integer or None.
        """
        if any(type_.startswith(x + 'sampler')
               for x in ['', 'i', 'u']):
            type_code = 'i'
        else:
            try:
                type_code = {'bool': 'b',
                             'int': 'i',
                             'uint': 'ui',
                             'unsigned int': 'ui',
                             'float': 'f',
                             'double': 'd'}[type_]
            except KeyError:
                return None
        base_type = cls._translate_type_code(type_code)
        return UniformDescription(
            name,
            array_length,
            False,
            f'Uniform1{base_type}{"v" if array_length else ""}',
            cls._dtype_of_base_type(base_type))

    # Private methods ---------------------------------------------------------
    @classmethod
    def _translate_type_code(cls, type_code):
        return {'': 'f',
                'b': 'ui',
                'u': 'ui'}.get(type_code, type_code)

    @classmethod
    def _dtype_of_base_type(cls, base_type):
        return {'i': np.int32,
                'ui': np.uint32,
                'f': np.float32,
                'd': np.float64}[base_type]
