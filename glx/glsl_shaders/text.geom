#version 330

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform sampler2D font_atlas;
uniform mat4 projection;

in vec4 v_uv[];

out vec2 g_uv;

void main()
{
    vec4 pos = gl_in[0].gl_Position;
    vec4 uv = v_uv[0];
    vec2 size = vec2(textureSize(font_atlas, 0)) * (uv.zw - uv.xy);
    vec2 pos_opposite = pos.xy + (mat2(projection) * size);

    gl_Position = vec4(pos.xy, 0, 1);
    g_uv = uv.xy;
    EmitVertex();

    gl_Position = vec4(pos.x, pos_opposite.y, 0, 1);
    g_uv = uv.xw;
    EmitVertex();

    gl_Position = vec4(pos_opposite.x, pos.y, 0, 1);
    g_uv = uv.zy;
    EmitVertex();

    gl_Position = vec4(pos_opposite.xy, 0, 1);
    g_uv = uv.zw;
    EmitVertex();

    EndPrimitive();
}
