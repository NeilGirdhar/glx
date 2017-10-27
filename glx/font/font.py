import string
from contextlib import contextmanager

import freetype as ft
import numpy as np
from pkg_resources import resource_filename

from ..shader_program import ShaderProgram
from .atlas import Atlas
from .code_lookup import CodeLookup


class Font:
    ATLAS_TEXTURE_UNIT = 0
    CODE_TEXTURE_UNIT = 1
    DEFAULT_CHARACTERS = (string.ascii_letters
                          + string.digits
                          + string.punctuation
                          + ' ')
    FT_OPTIONS = (ft.FT_LOAD_RENDER |
                  ft.FT_LOAD_FORCE_AUTOHINT)
    # ft.FT_LOAD_TARGET_LCD

    def __init__(self, filename, size):
        """
        Create all textures for latin characters and store them on the card.
        Set uniforms for the textures.
        """
        self.shader_program = ShaderProgram(
            vertex=[resource_filename('glx', 'glsl_shaders/text.vert')],
            geometry=[resource_filename('glx', 'glsl_shaders/text.geom')],
            fragment=[resource_filename('glx', 'glsl_shaders/text.frag')])
        self.char_to_index = {}
        self.chars = []
        self.atlas = Atlas(self, 256, self.ATLAS_TEXTURE_UNIT)
        self.code_lookup = CodeLookup(self, len(self.DEFAULT_CHARACTERS),
                                      self.CODE_TEXTURE_UNIT)

        self.face = ft.Face(filename)
        self.face.set_char_size(size * 64)

        for c in self.DEFAULT_CHARACTERS:
            self.add_char(c)

        with self.shader_program.bind_context():
            self.shader_program.font_atlas(np.int32(self.atlas.texture_unit))
            self.shader_program.code_to_texture(np.int32(
                self.code_lookup.texture_unit))
            self.shader_program.gamma(np.float32(2.2))

    def add_char(self, c, register=True):
        self.face.load_char(c, self.FT_OPTIONS)

        glyph = self.face.glyph
        bitmap = glyph.bitmap

        uvs = self.atlas.add_char(bitmap)
        self.code_lookup.add_char(uvs)

        if register:
            self.char_to_index[c] = len(self.chars)
            self.chars.append(c)
            # self.display()

    def get_char(self, c):
        if c not in self.char_to_index:
            self.add_char(c)
        return self.char_to_index[c]

    def sort_chars(self):
        def sort_key(c):
            index = self.char_to_index[c]
            uvs = self.code_lookup.data[index]
            return uvs[1] - uvs[3]
        self.chars.sort(key=sort_key, reverse=False)
        self.char_to_index = {c: i
                              for i, c in enumerate(self.chars)}

    def repopulate(self):
        self.sort_chars()
        self.atlas.clear()
        self.code_lookup.clear()
        for c in self.chars:
            self.add_char(c, register=False)

    @contextmanager
    def draw_context(self, *args, **kwargs):
        if self.atlas.needs_update:
            self.atlas.update_texture()
        if self.code_lookup.needs_update:
            self.code_lookup.update_texture()
        with self.shader_program.bind_context(*args, **kwargs):
            with self.atlas.draw_context(), self.code_lookup.draw_context():
                yield

    def display(self):
        if self.atlas.lines:
            line = self.atlas.lines[-1]
            last_line_usage = line.x * line.height / self.atlas.size
        else:
            last_line_usage = 0
        for line in self.atlas.lines:
            print(line.height / self.atlas.size)
        print(self.atlas.size,
              (self.atlas.y + last_line_usage) / self.atlas.size)
        for c, d in zip(self.chars,
                        self.code_lookup.data[: self.code_lookup.used]):
            print(c, d)
        print('-')
        print()
