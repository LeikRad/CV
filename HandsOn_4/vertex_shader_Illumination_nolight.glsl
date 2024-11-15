/*
Visual Computing 2021/2022
--------------------------

Vertex shader *simulating* no illumination.
It uses the ambient properties of the material as a unique color for the object.

Samuel Silva, Nov. 2021
*/
#version 330

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 normal;

out vec4 vColor;
out vec3 vNormal;


uniform vec4 lightPosition;
uniform vec3 viewerPosition;

// Model view and projection matrices

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


uniform vec4 lightColor;

// these are properties of the OBJECT
struct Material {
    vec4 ambient;
    vec4 diffuse;
    vec4 specular;
    float shininess;
};

uniform Material material;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0);
    vColor = material.specular;
}