"""
Visual Computing 2024/2025
Hands On 03 - 3D Transformations and Projections
v 2.2
Samuel Silva, 2024
"""

import math
import random

import OpenGL.raw.GLU
import pygame as pg
import numpy as np
import sys
from numpy import array
from pygame.fastevent import wait
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import shaders
from OpenGL.arrays import vbo
import glm
from timeit import default_timer as timer

class VCHelper:
    """ This class provides some helper functions for the Visual Computing class """

    def __init__(self):
        self.vao = None
        self.windowSize = (0, 0)
        self.shader = None
        self.vao_triangle = None
        self.triangle_vbo = None
        self.square_vbo = None
        self.tri_top_x = -0.5
        self.clock = pg.time.Clock()


        # game variables

        self.number_of_hits = 0


        # initial values for matrices and relevant positions/orientations
        self.projMatrix = glm.ortho(-1, 1.0, -1.0, 1.0, -1.0, 1.0)

        self.modelMatrix = np.identity(4, np.float32)
        self.viewMatrix = np.identity(4, np.float32)

        # game area limits
        self.min_x = self.min_y = self.min_z = -5.0
        self.max_x = self.max_y = self.max_z = 5.0

        # triangle properties
        self.tx = self.ty = self.tz = 3.0
        self.angle = 0.0
        self.sx = self.sy = self.sz = 0.2

        # square properties
        self.tolerance = 0.1
        self.s_tx = 0  # random.uniform(self.min_x, self.max_x)
        self.s_ty = 0  # random.uniform(self.min_y, self.max_y)
        self.s_tz = 0.0
        self.s_angle = 0.0
        self.s_sx = self.s_sy = self.s_sz = 0.2
        self.s_anim_scale = 0.005

        # this pushes the "world back 5 units in Z, moving it away from the camera
        self.globalTz = -5

        # camera parameters (not applied, in this hands-on)
        self.cam_position = np.array([0, 0, 0], 'f')
        self.cam_target = np.array([0, 0, -1], 'f')
        self.cam_direction = np.array([0, 0, -1], 'f')

        # perspective projection parameters
        self.fovy = 45
        self.nearPlane = 1.5
        self.farPlane = 25

        self.number_of_cubes = 5
        self.rx = self.min_x + (self.max_x - self.min_x) * np.random.rand(1, self.number_of_cubes)
        self.ry = self.min_y + (self.max_y - self.min_y) * np.random.rand(1, self.number_of_cubes)
        self.rang = 1.2 * np.random.rand(1, self.number_of_cubes)

        # game events
        self.collision = False

    def initalizeGLWindow(self, width, height):
        """ This method initialized the OpenGL window and context recurring to pygame
            all parameters regarding OpenGL states are set here"""
        pg.init()

        # this may be needed for Metal (apple silicon)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        self.windowSize = (width, height)
        pg.display.set_mode(self.windowSize, DOUBLEBUF | OPENGL | RESIZABLE)

        #glEnable(GL_DEPTH_TEST)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    def initShaders(self):
        """ This method contains the definition and compilation instructions for the
            vertex and fragment shaders """

        vertex_shader = shaders.compileShader("""#version 330
            layout (location = 0) in vec3 position;
            layout (location = 1) in vec3 color;

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            out vec3 vColor;

            void main() {
            gl_Position =  projection * view * model * vec4(position, 1.0);
            vColor = vec3(color);

            }""", GL_VERTEX_SHADER)

        result = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
        if not (result):
            raise RuntimeError(glGetShaderInfoLog(vertex_shader))

        # FRAGMENT_SHADER = shaders.compileShader("""#version 120
        #    varying vec3 pos;
        #    void main() {
        #    gl_FragColor = vec4( 1, 1, 0, 1 );
        #     }""", GL_FRAGMENT_SHADER)

        fragment_shader = shaders.compileShader("""#version 330
            in vec3 vColor;
            out vec4 out_color;
            void main() {
                out_color = vec4(vColor,1); 
    }""", GL_FRAGMENT_SHADER)

        # just compile the shader program including the two configured shaders
        self.shader = shaders.compileProgram(vertex_shader, fragment_shader)

        result = glGetProgramiv(self.shader, GL_LINK_STATUS)

        if not result:
            raise RuntimeError(glGetProgramInfoLog(self.shader))

        glUseProgram(self.shader)

        self.compute_proj_view_matrix()

    def initVertexBuffer(self):
        """ This method  initializes the vertex buffer objects (VBOs) containing the
            vertex data for the different geometries to be drawn """
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertices for the triangle
        # note that they are given in counter-clockwise order
        self.triangle_vertices = array([
                [0, 1, 0, 1, 1, 1],
                [1, -1, 0, 0, 1, 1],
                [-1, -1, 0, 1, 1, 0]  # ,
                # [2, -1, 0, 1, 0, 0],
                # [4, -1, 0, 0, 1, 0],
                # [4, 1, 0, 0, 0, 1],
                # [2, -1, 0, 1, 0, 0],
                # [4, 1, 0, 0, 0, 1],
                # [2, 1, 0, 0, 1, 1],
            ], 'f')

        self.triangle_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.triangle_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.triangle_vertices.size, self.triangle_vertices, GL_STATIC_DRAW)

        # and now the vertices for the... cube
        self.square_vertices = array([
                [-1, -1, 1, 1, 0, 0],
                [1, -1, 1, 1, 0, 0],
                [1, 1, 1, 1, 0, 0],

                [1, 1, 1, 1, 0, 0],
                [-1, 1, 1, 1, 0, 0],
                [-1, -1, 1, 1, 0, 0],  # front face

                [-1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 0],
                [1, 1, -1, 1, 1, 0],

                [1, 1, -1, 1, 1, 0],
                [-1, 1, -1, 1, 1, 0],
                [-1, 1, 1, 1, 1, 0],  # top face

                [-1, -1, -1, 1, 0, 1],
                [1, -1, -1, 1, 0, 1],
                [1, -1, 1, 1, 0, 1],

                [1, -1, 1, 1, 0, 1],
                [-1, -1, 1, 1, 0, 1],
                [-1, -1, -1, 1, 0, 1],  # bottom face

                [-1, 1, 1, 0, 0, 1],
                [-1, -1, -1, 0, 0, 1],
                [-1, -1, 1, 0, 0, 1],

                [-1, 1, 1, 0, 0, 1],
                [-1, 1, -1, 0, 0, 1],
                [-1, -1, -1, 0, 0, 1],  #

                [1, 1, -1, 0, 1, 0],
                [1, -1, 1, 0, 1, 0],
                [1, -1, -1, 0, 1, 0],

                [1, 1, -1, 0, 1, 0],
                [1, 1, 1, 0, 1, 0],
                [1, -1, 1, 0, 1, 0],  # right face

                [-1, 1, -1, 0, 1, 1],
                [1, -1, -1, 0, 1, 1],
                [-1, -1, -1, 0, 1, 1],

                [-1, 1, -1, 0, 1, 1],
                [1, 1, -1, 0, 1, 1],
                [1, -1, -1, 0, 1, 1],  # back face
            ], 'f')

        self.square_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.square_vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.square_vertices.size, self.square_vertices, GL_STATIC_DRAW)

    def draw_cube(self):
        """ This method contains the instructions that need to be issued to draw the cube:
            bind to the specific vbo; tell where the attributes are (location) and how
            they are passed; enable those attributes; and draw the geometry."""
        glBindBuffer(GL_ARRAY_BUFFER, self.square_vbo)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, None)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLES, 0, 36)

    def draw_triangle(self):
        """ This method contains the instructions that need to be issued to draw the triangle:
            bind to the specific vbo; tell where the attributes are (location) and how
            they are passed; enable those attributes; and draw the geometry."""

        glBindBuffer(GL_ARRAY_BUFFER, self.triangle_vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, None)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLES, 0, 3)

    def render(self):
        """ just render the scene """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.compute_proj_view_matrix()

        try:

            try:
                # we need to define which shader we are using; we only have one,
                # but we could have a different shader for each object
                glUseProgram(self.shader)

                # draw triangle

                self.compute_model_matrix(self.tx, self.ty, self.tz, self.sx, 0.0, 0.0, self.angle)
                self.draw_triangle()

                # draw cube
                self.compute_model_matrix(self.s_tx, self.s_ty, self.s_tz, self.s_sx, 0.2 * self.s_angle,
                                          1.7 * self.s_angle, 0.2 * self.s_angle)

                self.draw_cube()

            finally:
                pass
            #    glDisableClientState(GL_VERTEX_ARRAY)
            #    glDisableClientState(GL_COLOR_ARRAY)
        finally:
            pass

        pg.display.flip()

    def compute_proj_view_matrix(self):
        """ compute the projection and view matrices """

        # just ensure that a compute shader has been selected
        glUseProgram(self.shader)

        self.projMatrix = glm.ortho(self.min_x, self.max_x, self.min_y, self.max_y, -1, 15.0)

        projLoc = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(projLoc, 1, GL_TRUE, np.array(self.projMatrix, dtype=np.float32))

        self.viewMatrix = np.identity(4, np.float32)
        self.viewMatrix = glm.translate(self.viewMatrix, glm.vec3(0, 0, 0))

        viewLoc = glGetUniformLocation(self.shader, "view")
        glUniformMatrix4fv(viewLoc, 1, GL_TRUE, np.array(self.viewMatrix, dtype=np.float32))

    def compute_model_matrix(self, tx, ty, tz, s, angle_x, angle_y, angle_z):
        """ Compute a model matrix based on the given parameters and send it to the shaders. """

        self.modelMatrix = np.identity(4, np.float32)
        # self.modelMatrix = glm.scale(self.modelMatrix, s, s, s)
        # self.modelMatrix = glm.rotate(self.modelMatrix, angle_z, 0, 0, 1.0)
        # self.modelMatrix = glm.rotate(self.modelMatrix, angle_y, 0, 1.0, 0)
        # self.modelMatrix = glm.rotate(self.modelMatrix, angle_x, 1.0, 0, 0)
        # self.modelMatrix = glm.translate(self.modelMatrix, tx, ty, self.globalTz + tz)

        self.modelMatrix = glm.translate(self.modelMatrix, glm.vec3(tx, ty, self.globalTz + tz))
        self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(angle_x), glm.vec3(1.0, 0, 0))
        self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(angle_y), glm.vec3(0, 1.0, 0))
        self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(angle_z), glm.vec3(0, 0, 1.0))
        self.modelMatrix = glm.scale(self.modelMatrix, glm.vec3(s, s, s))

        modelLoc = glGetUniformLocation(self.shader, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, np.array(self.modelMatrix, dtype=np.float32))

    def normalize(self, v):
        """ Normalized vector v, i.e., make it have a length of 1.0 """
        squaresSum = v[0] * v[0] + v[1] * v[1] + v[2] * v[2]

        norm = np.sqrt(squaresSum)

        vn = v

        if norm > 0:
            vn[0] /= norm
            vn[1] /= norm
            vn[2] /= norm

        return vn

    def process_events(self, pg):
        """ Process all events caught by pygame"""

        # events first
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        # continuously pressed keys
        keys = pg.key.get_pressed()

        # keys controlling the ship
        if keys[pg.K_UP]:
            self.ty += 0.05
            if self.ty > self.max_y:
                self.ty = self.min_y
            self.angle = 0
        if keys[pg.K_DOWN]:
            self.ty -= 0.05
            if self.ty < self.min_y:
                self.ty = self.max_y
            self.angle = -180
        if keys[pg.K_LEFT]:
            self.tx -= 0.05
            if self.tx < self.min_x:
                self.tx = self.max_x
            self.angle = 90
        if keys[pg.K_RIGHT]:
            self.tx += 0.05
            if self.tx > self.max_x:
                self.tx = self.min_x
            self.angle = -90

        if keys[pg.K_a]:
            self.fovy += 1
            self.compute_proj_view_matrix()
        if keys[pg.K_z] and self.fovy > 10:
            self.fovy -= 1
            self.compute_proj_view_matrix()

        # these are for proper orientation of the triangle tip when moving diagonally
        if keys[pg.K_UP] and keys[pg.K_LEFT]:
            self.angle = 45
        if keys[pg.K_DOWN] and keys[pg.K_LEFT]:
            self.angle = 135
        if keys[pg.K_UP] and keys[pg.K_RIGHT]:
            self.angle = -45
        if keys[pg.K_DOWN] and keys[pg.K_RIGHT]:
            self.angle = -135

    def check_collisions(self):
        """ When a collision happens, i.e., the triangle is in the close vicinity of the square, a new square is
            generated. """
        #boundary = 0.3
        #if (self.s_tx - boundary) < self.tx < (self.s_tx + boundary) and \
        #        (self.s_ty - boundary) < self.ty < (self.s_ty + boundary):
        #    self.collision = True;
        #    self.number_of_hits += 1
        #    self.s_tx = random.uniform(self.min_x, self.max_x)
        #    self.s_ty = random.uniform(self.min_y, self.max_y)

    def animate(self):
        """ This just performs a very simple animation of the cube by changing the scale"""
        
        # a line to get you started... but with just this one, we have a problem of unlimited square growth
        #self.s_sx += self.s_anim_scale



#####################################################################
# MAIN stuff


# create an object of out helper class, where all code is encapsulated
mygl = VCHelper()

# initialize the OpenGL window and context
# it uses pygame, inside
mygl.initalizeGLWindow(800, 800)

# initialize the vertex buffers. For the most recent versions of OpenGL
# it is not possible to initialize the shaders without having some VAO
mygl.initVertexBuffer()

# compile and initialize the shaders
mygl.initShaders()

start_time = timer()
while True:
    # this line below just measures the time since it was last called.
    # the parameter for tick is the desired frame rate
    # if the time taken to render a frame (i.e., execute the while
    # one time), is less than the intended frame rate, this line will
    # delay the execution to match it. It ensures that the code runs
    # at the same speed in every machine
    dt = mygl.clock.tick(60)

    mygl.process_events(pg)  # checking for any pressed keys or events

    mygl.check_collisions()  # did the triangle collide with the square?

    mygl.animate()  # change parameters to animate objects

    mygl.render()  # render scene

    # after 10 hits, it shows how much time was taken to do it and resets counters
    if mygl.number_of_hits == 10:
        stop_time = timer()
        res = stop_time-start_time
        print(f"10 hits in {res:10.2f} seconds.")
        start_time = timer()
        mygl.number_of_hits = 0

