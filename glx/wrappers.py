import OpenGL.GL as gl

__all__ = ['glGetActiveAttrib']


def glGetActiveAttrib(program, index):
    """Wrap PyOpenGL glGetActiveAttrib as for glGetActiveUniform
    """
    buffer_size, = gl.glGetProgramiv(program,
                                     gl.GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
    length = gl.GLsizei()
    size = gl.GLint()
    type_ = gl.GLenum()
    name = bytes(buffer_size)

    gl.glGetActiveAttrib(program, index, buffer_size,
                         length, size, type_, name)
    return name.decode().rstrip('\x00'), size.value, type_.value
