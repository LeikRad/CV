import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
import pygame as pg
from pygame.locals import *
from numpy import array
from OpenGL.arrays import vbo

class VCHelper:
    """ This class provides some helper functions for the Visual Computing class """

    def __init__(self):
        self.windowsize = (0, 0)
        self.shader = None
        self.vao_triangle = None
        self.vbo_triangle = None

    #########################
    def init_shaders(self):
        """This function defines the vertex and fragment shaders and compiles them"""

        # compiling a vertex shader
        vertex_shader = shaders.compileShader("""#version 330
             layout (location = 0) in vec3 position;

             void main() {
                gl_Position =  vec4(position, 1.0);
             }""", GL_VERTEX_SHADER)

        # checking if vertex shader compilation went OK
        result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
        if not result:
            raise RuntimeError(glGetShaderInfoLog(vertex_shader))

        # compiling a fragment shader
        fragment_shader = shaders.compileShader("""#version 330
             out vec4 out_color;
             void main() {
                 out_color = vec4(1.0f, 0.5f, 0.2f, 1.0f); 
             }""", GL_FRAGMENT_SHADER)

        # checking if fragment shader compilation went OK
        result = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
        if not result:
            raise RuntimeError(glGetShaderInfoLog(fragment_shader))

        # Compile a program with both shaders
        self.shader = shaders.compileProgram(vertex_shader, fragment_shader)

        # Check if the shader program was linked OK
        result = glGetProgramiv(self.shader, GL_LINK_STATUS)
        if not result:
            raise RuntimeError(glGetProgramInfoLog(self.shader))

    def init_vertex_buffers(self):
        """Define the geometry and copy it to a vertex buffer object"""
        self.triangle_vertices = None

    #########################
    def init_window(self, w, h):
        """This function initializes a pygame window to serve as OpenGL context"""
        pg.init()

        self.windowsize = (w, h)

        pg.display.set_mode(self.windowsize, DOUBLEBUF | OPENGL | RESIZABLE)
        pg.display.set_caption("Visual Computing")

        glClearColor(0.0, 0.0, 0.2, 1.0)

    #########################
    def render(self):
        """This function will deal with rendering objects to the scene"""

        # clear the buffer
        glClear(GL_COLOR_BUFFER_BIT)

        # Some code will be added here...

        # flip the buffer and show what I just composed
        pg.display.flip()


# create an object of type CVHelper, the Visual Computing helper class
cv = VCHelper()

# initialize a window
cv.init_window(640, 480)

# initialize the vertex buffers here


# enter the loop for rendering and processing events
while True:

    # process events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                quit()

    # render the scene
    cv.render()
