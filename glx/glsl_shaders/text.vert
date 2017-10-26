#version 330

uniform sampler2D font_atlas;
uniform sampler1D code_to_texture;
uniform mat4 projection;
uniform vec2 vertex_offset;  // in view space.
uniform vec4 color;
uniform float gamma;

//  vertex in view space of each character adjusted for kerning, etc.
in vec2 vertex;
in int code;

out vec4 v_uv;

void main()
{
    v_uv = texelFetch(
            code_to_texture,
            code,
            0);
    gl_Position = projection * vec4(vertex_offset + vertex, 0.0, 1.0);
}
