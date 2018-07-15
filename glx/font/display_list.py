import freetype as ft
import numpy as np

from ..gl_importer import gl as gl
from ..shader_program import Attribute, BufferDescription

__all__ = ['DisplayList']


class DisplayList:
    RECORD_TYPE = np.dtype([('vertex', '<f4', 2),
                            ('code', '<i4')])

    def __init__(self, font):
        self.font = font
        self.buffer, = gl.glGenBuffers(1)
        self.vertex_array, = font.shader_program.create_vertex_arrays(
            [BufferDescription(
                self.buffer,
                self.RECORD_TYPE,
                [Attribute('vertex', ['vertex'], is_vector=True),
                 Attribute('code', ['code'])])])
        self.array = None
        self.text = None
        self.characters = {}

    def delete(self):
        # Work around the fact that glGenBuffers returns a result that
        # glDeleteBuffers can't handle.
        gl.glDeleteBuffers(1, int(self.buffer))
        self.vertex_array.delete()

    def set_text(self, text):
        """
        Fill the buffer and vertex array.
        Possibly render additional glyphs into the texture.
        """
        if not isinstance(text, str):
            raise TypeError("text argument must be a string — not {}".format(
                type(text)))
        if (text == self.text
                and self.atlas_creation_id == self.font.atlas.creation_id):
            return
        self.text = text
        self.regenerate()

    def regenerate(self):
        face = self.font.face
        options = self.font.FT_OPTIONS

        self.atlas_creation_id = self.font.atlas.creation_id
        self.array = np.empty(len(self.text), self.RECORD_TYPE)
        vertex = np.zeros(2, dtype='f')
        last_char_index = 0

        for i, c in enumerate(self.text):
            this_vertex = self.array[i: i + 1]

            # Set code.
            this_vertex['code'] = self.font.get_char(c)

            # get_char might have caused creation_id to change.
            if self.atlas_creation_id != self.font.atlas.creation_id:
                self.regenerate()
                return

            # Set vertex.
            face.load_char(c, options)
            glyph = face.glyph

            this_char_index = face.get_char_index(c)
            assert this_char_index > 0

            kerning = face.get_kerning(last_char_index, this_char_index,
                                       ft.FT_KERNING_DEFAULT)

            advance = glyph.linearHoriAdvance / 65536
#           print("==========")
#           print(glyph.format)
#           print(c)
#           print("glyph", glyph.bitmap.rows)
#           for x in ['linearHoriAdvance', 'linearVertAdvance',
#                     'bitmap_left', 'bitmap_top']:
#               print(x, getattr(glyph, x))
#           print("glyph metrics")
#           for x in ['horiAdvance', 'horiBearingX', 'horiBearingY',
#                     'vertAdvance', 'vertBearingX', 'vertBearingY', 'width']:
#               print(x, getattr(glyph.metrics, x))
            bottom_left = np.array(
                (glyph.bitmap_left + kerning.x / 64,
                 -glyph.bitmap_top + glyph.bitmap.rows + kerning.y / 64),
                dtype='f')

            this_vertex['vertex'] = vertex + bottom_left
            vertex[0] += advance

            last_char_index = this_char_index

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer)
        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        self.array.nbytes,
                        self.array,
                        gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def draw(self, widget_point):
        """
        Before drawing, be sure to set the uniforms:
        * projection
        * color
        * gamma
        * scale
        """
        if self.atlas_creation_id != self.font.atlas.creation_id:
            self.regenerate()
        with self.vertex_array.bind_context():
            self.font.shader_program.vertex_offset(widget_point)
            gl.glDrawArrays(gl.GL_POINTS, 0, len(self.text))
