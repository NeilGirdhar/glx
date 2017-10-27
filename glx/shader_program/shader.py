from io import StringIO

from mako.runtime import Context
from mako.template import Template

from glx import gl as gl

__all__ = ['Shader']


class Shader:
    EXTENSION = {
        gl.GL_VERTEX_SHADER: 'vert',
        gl.GL_GEOMETRY_SHADER: 'geom',
        gl.GL_FRAGMENT_SHADER: 'frag',
        gl.GL_COMPUTE_SHADER: 'comp'}

    def __init__(self, filename, type_, context_kwargs=None):
        self.type_ = type_

        template = Template(filename=filename)
        buffer = StringIO()
        context = Context(buffer, **(context_kwargs
                                     if context_kwargs is not None
                                     else {}))
        try:
            template.render_context(context)
        except:
            from mako import exceptions
            print(exceptions.text_error_template().render())
        shader_text = buffer.getvalue()

        # pylint: disable=assignment-from-no-return
        self.shader_index = gl.glCreateShader(type_)
        assert self.shader_index

        gl.glShaderSource(self.shader_index, shader_text)
        gl.glCompileShader(self.shader_index)
        result = gl.glGetShaderiv(self.shader_index, gl.GL_COMPILE_STATUS)
        if result != 1:
            log = gl.glGetShaderInfoLog(self.shader_index).decode('latin')
            print(shader_text)
            raise Exception("""
                            Couldn't compile shader.
                            Shader compilation log:
                            """ + log)
        self.shader_text = shader_text

    def delete_shader(self):
        gl.glDeleteShader(self.shader_index)
        self.shader_index = 0
