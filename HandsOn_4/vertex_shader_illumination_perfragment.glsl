/*
Visual Computing 2021/2022
--------------------------

Vertex shader supporting per-fragment shading.
The shader just passes the position and normal in world coordinates. These wiil be interpolated by OpenGL
when passed to the fragment shader.

Samuel Silva, Nov. 2021
*/
#version 330

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 normal;

out vec3 vNormal;
out vec3 fragPos;

// Model view and projection matrices

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


void main()
{
    fragPos = vec3(model *  vec4(position, 1.0));
    vNormal = mat3(transpose(inverse(model))) * normal;

    gl_Position = projection * view * vec4(fragPos, 1.0);
}

