/*
Visual Computing 2021/2022
--------------------------

Simple fragment shader receiving a color for the fragment

Samuel Silva, Nov. 2021
*/
#version 330

in vec4 vColor;
out vec4 out_color;

void main()
{

    out_color = vColor;

    return;

}