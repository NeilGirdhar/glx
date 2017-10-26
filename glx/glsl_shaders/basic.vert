#version 330

uniform vec4 color;
uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

in vec2 vertex;

void main()
{
    gl_Position = projection * view * model * vec4(vertex, 0.0, 1.0);
}
