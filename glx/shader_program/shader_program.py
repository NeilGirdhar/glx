from contextlib import contextmanager

from ..gl_importer import OpenGL, gl
from ..wrappers import glGetActiveAttrib
from .shader import Shader
from .uniform_description import UniformDescription
from .vertex_array import VertexArray

__all__ = ['ShaderProgram']


class ShaderProgram:

    """
    A ShaderProgram manages an entire pipeline: vertex shader, possible
    geometry shader, and fragment shader.  Calling bind_context binds the
    entire pipeline, and possible some uniform variables.   Its
    create_vertex_arrays method creates a list of VertexArray objects, which
    allows binding of varying variables.
    """

    def __init__(self, vertex=[], geometry=[], fragment=[],
                 context_kwargs=None):
        """
        * vertex, geometry and fragment are lists of filenames of included
          shaders.
        * context_kwargs are passed to the mako runtime context.
        """
        # pylint: disable=assignment-from-no-return
        self.program_index = gl.glCreateProgram()
        assert self.program_index > 0
        self.shaders = {(filename, type_): Shader(filename,
                                                  type_,
                                                  context_kwargs)
                        for filenames, type_ in [
                            (vertex, gl.GL_VERTEX_SHADER),
                            (geometry, gl.GL_GEOMETRY_SHADER),
                            (fragment, gl.GL_FRAGMENT_SHADER)]
                        for filename in filenames}
        for shader in self.shaders.values():
            gl.glAttachShader(self.program_index,
                              shader.shader_index)
        gl.glLinkProgram(self.program_index)
        value = gl.glGetProgramiv(self.program_index, gl.GL_LINK_STATUS)
        if value != 1:
            log = gl.glGetProgramInfoLog(self.program_index).decode('latin')
            raise Exception("""
                            Couldn't link program.
                            Shader program info log:
                            """ + log)

        self.create_uniform_binders()

    @contextmanager
    def bind_context(self, uniforms=None):
        if uniforms is None:
            uniforms = {}

        try:
            gl.glUseProgram(self.program_index)
        except OpenGL.error.GLError:
            log = gl.glGetProgramInfoLog(self.program_index).decode('latin')
            raise Exception("""
                            Couldn't use program.
                            Shader program info log:
                            """ + log)
        try:
            for name, value in uniforms.items():
                getattr(self, name)(value)
            yield self
        finally:
            gl.glUseProgram(0)

    def delete_program(self):
        gl.glDeleteProgam(self.program_index)
        self.program_index = 0

    def create_uniform_binders(self):
        for shader in self.shaders.values():
            if shader.type_ != gl.GL_VERTEX_SHADER:
                continue
            for u in UniformDescription.parse_shader_text(shader.shader_text):
                if hasattr(self, u.name):
                    raise ValueError(
                        f"Multiple uniforms with the same name: {u.name}")
                setattr(self, u.name, u.create_method(self.program_index))

    def attribute_name_to_location(self, attribute_name):
        attribute_location = gl.glGetAttribLocation(
            self.program_index, attribute_name)
        if attribute_location == -1:
            count = gl.glGetProgramiv(self.program_index,
                                      gl.GL_ACTIVE_ATTRIBUTES)[0]
            print("Active Attributes:")
            for i in range(count):
                name, _, _ = glGetActiveAttrib(self.program_index, i)
                print(" ", name)
            raise ValueError(
                f'Attribute "{attribute_name}" not found in program.')
        return attribute_location

    def create_vertex_arrays(self, buffer_descriptions):
        """
        * buffer_descriptions is a reiterable of BufferDescription.
        """
        return [VertexArray(self, buffer_description)
                for buffer_description in buffer_descriptions]
