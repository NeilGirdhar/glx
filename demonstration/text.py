import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from glx import DisplayList, Font

# A list of fonts can be found like this:
# matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
font = '/Library/Fonts/Arial Unicode.ttf'
font_size = 20

# The display() method does all the work; it has to call the appropriate
# OpenGL functions to actually display something.
def display():
    # Clear the color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

#   with self.font.draw_context():
#       vertex_offset = view_matrix.dot(model.dot(self.geo.text_location))
#       text_display_list.draw(
#           np.array([0.5, 0.5, 0.0, 1.0], dtype=np.float32))
    # ... render stuff in here ...
    # It will go to an off-screen frame buffer.

    # Copy the off-screen buffer to the screen.
    glutSwapBuffers()

glutInit(sys.argv)

# Create a double-buffer RGBA window.   (Single-buffering is possible.
# So is creating an index-mode window.)
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
#glutInitContextVersion(4, 1)
glutInitContextFlags(GLUT_CORE_PROFILE | GLUT_DEBUG)

font = Font('/Library/Fonts/Arial Unicode.ttf', 20)
with font.shader_program.bind_context():
    font.color(np.array([0.9, 0.9, 1.0, 0.0], dtype=np.float32))

text_display_list = DisplayList(font)
text_display_list.set_text("hello world")


# Create a window, setting its title
glutCreateWindow('interactive')

# Set the display callback.  You can set other callbacks for keyboard and
# mouse events.
glutDisplayFunc(display)

# Run the GLUT main loop until the user closes the window.
glutMainLoop()
