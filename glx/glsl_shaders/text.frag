#version 330

uniform sampler2D font_atlas;
uniform vec4 color;
uniform float gamma;

in vec2 g_uv;

layout (location = 0) out vec4 fragment_color;

void main()
{
    float a = texture(font_atlas, g_uv).r;
    fragment_color.rgb = color.rgb;
    fragment_color.a = color.a * pow(a, 1.0 / gamma);
}
