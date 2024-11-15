"""
Visual Computing 2024/2025
Lighting using OpengGL

Samuel Silva, Oct. 2024
"""

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

import pywavefront as wf

import glm

from dataclasses import dataclass


class GeometricObject:
    """
    A simple class to manage objects. In enables loading from OBJ files, creating the vertex buffer and rendering
    """

    def __init__(self, modelpath: str = ''):
        self.vao = None
        self.vbo = None
        self.vertices = None
        self.faces = None
        self.model = None
        self.ebo = None

        self.default_geometry = True

        self.modelMatrix = np.identity(4, 'f')

        self.changed = True

        # if no geometry file is given to the constructor, then use a default geometry (cube)
        if modelpath == '':
            self.init_cube()
        else:
            self.load_model(modelpath)
            self.default_geometry = False

        # material properties of the object
        self.material_ambient = np.array([0.6, 0.6, 0, 1.0], 'f')
        self.material_specular = np.array([1.0, 1.0, 1.0, 1.0], 'f')
        self.material_diffuse = np.array([1.0, 1.0, 0, 1.0], 'f')
        self.material_shininess = 32

        self.object_position = np.array([0.0, 0.0, 0.0], 'f')
        self.object_scaling = [1, 1, 1]
        self.object_rotation = [0, 0, 0]

        self.computeshader = None

    def set_material_byname(self, material: str):
        """ Some pre-defined material properties """

        if material.upper() == '' or material.upper() == 'BRASS':
            self.material_ambient = np.array([0.329412, 0.223529, 0.027451, 1.0], 'f')
            self.material_diffuse = np.array([0.780392, 0.568627, 0.113725, 1.0], 'f')
            self.material_specular = np.array([0.992157, 0.941176, 0.807843, 1.0], 'f')
            self.material_shininess = 27.8974

        if material.upper() == 'RED_PLASTIC':
            self.material_ambient = np.array([0.0, 0.0, 0.0, 1.0], 'f')
            self.material_diffuse = np.array([0.5, 0.0, 0.0, 1.0], 'f')
            self.material_specular = np.array([0.7, 0.6, 0.6, 1.0], 'f')
            self.material_shininess = 32

        if material.upper() == 'OBSIDIAN':
            self.material_ambient = np.array([0.05375, 0.05, 0.06625, 1.0], 'f')
            self.material_diffuse = np.array([0.18275, 0.17, 0.22525, 1.0], 'f')
            self.material_specular = np.array([0.332741, 0.328634, 0.346435, 1.0], 'f')
            self.material_shininess = 38.4

        if material.upper() == 'GOLD':
            self.material_ambient = np.array([0.24725, 0.1995, 0.0745, 1.0], 'f')
            self.material_diffuse = np.array([0.75164, 0.60648, 0.22648, 1.0], 'f')
            self.material_specular = np.array([0.628281, 0.555802, 0.366065, 1.0], 'f')
            self.material_shininess = 51.2

        if material.upper() == 'EMERALD':
            self.material_ambient = np.array([0.0215, 0.1745, 0.0215, 0.55], 'f')
            self.material_diffuse = np.array([0.07568, 0.61424, 0.07568, 0.55], 'f')
            self.material_specular = np.array([0.633, 0.727811, 0.633, 0.55], 'f')
            self.material_shininess = 0.6 * 128

        if material.upper() == 'CHROME':
            self.material_ambient = np.array([0.25, 0.25, 0.25, 1.0], 'f')
            self.material_diffuse = np.array([0.4, 0.4, 0.4, 1.0], 'f')
            self.material_specular = np.array([0.774597, 0.774597, 0.774597, 1.0], 'f')
            self.material_shininess = 0.6 * 128

    def set_rotation(self, vRotation):
        self.object_rotation = np.array(vRotation, 'f')

    def set_translation(self, vTranslation):
        self.object_position = np.array(vTranslation, 'f')

    def set_scale(self, vScale):
        self.object_scaling = vScale

    def set_material(self, ambient, specular, diffuse, shininess):
        self.material_specular = specular
        self.material_ambient = ambient
        self.material_diffuse = diffuse
        self.material_shininess = shininess

    def init_cube(self):
        self.geometry = array([
            [-1, -1, 1, 1, 0, 0, 0, 0, 1],
            [1, -1, 1, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 0, 0, 0, 1],

            [1, 1, 1, 1, 0, 0, 0, 0, 1],
            [-1, 1, 1, 1, 0, 0, 0, 0, 1],
            [-1, -1, 1, 1, 0, 0, 0, 0, 1],  # front face

            [-1, 1, 1, 1, 1, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 0, 0, 1, 0],
            [1, 1, -1, 1, 1, 0, 0, 1, 0],

            [1, 1, -1, 1, 1, 0, 0, 1, 0],
            [-1, 1, -1, 1, 1, 0, 0, 1, 0],
            [-1, 1, 1, 1, 1, 0, 0, 1, 0],  # top face

            [-1, -1, -1, 1, 0, 1, 0, -1, 0],
            [1, -1, -1, 1, 0, 1, 0, -1, 0],
            [1, -1, 1, 1, 0, 1, 0, -1, 0],

            [1, -1, 1, 1, 0, 1, 0, -1, 0],
            [-1, -1, 1, 1, 0, 1, 0, -1, 0],
            [-1, -1, -1, 1, 0, 1, 0, -1, 0],  # bottom face

            [-1, 1, 1, 0, 0, 1, -1, 0, 0],
            [-1, -1, -1, 0, 0, 1, -1, 0, 0],
            [-1, -1, 1, 0, 0, 1, -1, 0, 0],

            [-1, 1, 1, 0, 0, 1, -1, 0, 0],
            [-1, 1, -1, 0, 0, 1, -1, 0, 0],
            [-1, -1, -1, 0, 0, 1, -1, 0, 0],  # left face

            [1, 1, -1, 0, 1, 0, 1, 0, 0],
            [1, -1, 1, 0, 1, 0, 1, 0, 0],
            [1, -1, -1, 0, 1, 0, 1, 0, 0],

            [1, 1, -1, 0, 1, 0, 1, 0, 0],
            [1, 1, 1, 0, 1, 0, 1, 0, 0],
            [1, -1, 1, 0, 1, 0, 1, 0, 0],  # right face

            [-1, 1, -1, 0, 1, 1, 0, 0, -1],
            [1, -1, -1, 0, 1, 1, 0, 0, -1],
            [-1, -1, -1, 0, 1, 1, 0, 0, -1],

            [-1, 1, -1, 0, 1, 1, 0, 0, -1],
            [1, 1, -1, 0, 1, 1, 0, 0, -1],
            [1, -1, -1, 0, 1, 1, 0, 0, -1]  # back face
        ], 'f')

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.geometry.size, self.geometry, GL_STATIC_DRAW)

    def load_model(self, path):
        """ loads a model from a .OBJ file --- only simple format supported... """

        model = wf.Wavefront(path, create_materials=True, collect_faces=True)
        print("Format:", model.mesh_list[0].materials[0].vertex_format)
        # print (teapot.mesh_list[0].materials[0].vertices)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        self.vertices = np.array(model.mesh_list[0].materials[0].vertices, 'f')
        print(self.vertices.size)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.vertices.size, self.vertices, GL_STATIC_DRAW)

        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        self.faces = np.array(model.mesh_list[0].faces, dtype=np.int32)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * self.faces.size, self.faces, GL_STATIC_DRAW)

        self.changed = True

    def render(self, shader):
        """ deal with composing the model matrix for this object and send it to the GPU and issue the code for rendering
        """

        glUseProgram(shader)

        # if something changed (affecting the model matrix or material properties recompute
        # otherwise, spare the computations
        if self.changed:
            self.modelMatrix = np.identity(4, np.float32)

            self.modelMatrix = glm.translate(self.modelMatrix, glm.vec3(self.object_position[0],
                                             self.object_position[1],
                                             self.object_position[2]))
            self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(self.object_rotation[0]), glm.vec3(1.0, 0, 0))
            self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(self.object_rotation[1]), glm.vec3(0, 1.0, 0))
            self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(self.object_rotation[2]), glm.vec3(0, 0, 1.0))
            self.modelMatrix = glm.scale(self.modelMatrix, glm.vec3(self.object_scaling[0],
                                         self.object_scaling[1],
                                         self.object_scaling[2]))
            self.changed = False

        modelLoc = glGetUniformLocation(shader, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, np.array(self.modelMatrix, dtype=np.float32))

        # need to pass the material properties of this object to the shader
        glUniform4fv(glGetUniformLocation(shader, "material.ambient"), 1, self.material_ambient)
        glUniform4fv(glGetUniformLocation(shader, "material.diffuse"), 1, self.material_diffuse)
        glUniform4fv(glGetUniformLocation(shader, "material.specular"), 1, self.material_specular)
        glUniform1f(glGetUniformLocation(shader, "material.shininess"), self.material_shininess)

        # if no model is given, then use default geometry (cube)
        if self.default_geometry:
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(0))  # vertices
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(6 * 4))  # normals
            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(2)
            glDrawArrays(GL_TRIANGLES, 0, 36)

        else:

            # Deal with the geometry and rendering
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(5 * 4))  # vertices
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(2 * 4))  # normals

            # glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(6 * 4))
            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(2)

            glDrawArrays(GL_TRIANGLES, 0, self.vertices.size)
            # glDrawElements(GL_TRIANGLES, self.obj_nFaceIndices, GL_UNSIGNED_INT, ctypes.c_void_p(0))


class LightSource:
    def __init__(self):

        # light properties; default is a point light (w = 1.0)
        self.position = np.array([0.0, 0.0, 10.0, 1.0], 'f')
        self.color = np.array([1.0, 1.0, 1.0], 'f')
        self.ambient = np.array([0.3, 0.3, 0.3], 'f')

        self.vbo = None
        self.lamp_geometry = None
        self.object_color = np.array([1.0, 1.0, 1.0, 1.0], 'f')
        self.object_scaling = [.3, .3, .3]
        self.object_rotation = [0, 0, 0]

        self.modelMatrix = np.identity(4, 'f')

        # initialize lamp to default geometry (for rendering, if required)
        self.set_lamp_geometry()
        self.set_lamp_shaders()

    def set_lamp_shaders(self):
        """ These shaders are JUST for rendering the lamp geometry!! We do not want to lamp's representation to be
        illuminated... """

        VERTEX_SHADER = shaders.compileShader("""#version 330
            layout (location = 0) in vec3 position;

            uniform vec3 lampColor;
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;
                        
            out vec3 vColor;

            void main() {
            gl_Position =  projection * view * model * vec4(position, 1.0);
            vColor = vec3(lampColor);

            }""", GL_VERTEX_SHADER)

        result = glGetShaderiv(VERTEX_SHADER, GL_COMPILE_STATUS)
        if not (result):
            raise RuntimeError(glGetShaderInfoLog(VERTEX_SHADER))

        # FRAGMENT_SHADER = shaders.compileShader("""#version 120
        #    varying vec3 pos;
        #    void main() {
        #    gl_FragColor = vec4( 1, 1, 0, 1 );
        #     }""", GL_FRAGMENT_SHADER)

        FRAGMENT_SHADER = shaders.compileShader("""#version 330
            in vec3 vColor;
            out vec4 out_color;
            void main() {
                out_color = vec4(vColor,1); 
    }""", GL_FRAGMENT_SHADER)

        # just compile the shader program including the two configured shaders
        self.lamp_geometry_shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        result = glGetProgramiv(self.lamp_geometry_shader, GL_LINK_STATUS)

        if not (result):
            raise RuntimeError(glGetProgramInfoLog(self.lamp_geometry_shader))

    def set_lamp_geometry(self):
        """ This defines a geometry for representing the light's position in the world """
        self.lamp_geometry = array([
            [-1, -1, 1, 1, 0, 0, 0, 0, 1],
            [1, -1, 1, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 0, 0, 0, 1],

            [1, 1, 1, 1, 0, 0, 0, 0, 1],
            [-1, 1, 1, 1, 0, 0, 0, 0, 1],
            [-1, -1, 1, 1, 0, 0, 0, 0, 1],  # front face

            [-1, 1, 1, 1, 1, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 0, 0, 1, 0],
            [1, 1, -1, 1, 1, 0, 0, 1, 0],

            [1, 1, -1, 1, 1, 0, 0, 1, 0],
            [-1, 1, -1, 1, 1, 0, 0, 1, 0],
            [-1, 1, 1, 1, 1, 0, 0, 1, 0],  # top face

            [-1, -1, -1, 1, 0, 1, 0, -1, 0],
            [1, -1, -1, 1, 0, 1, 0, -1, 0],
            [1, -1, 1, 1, 0, 1, 0, -1, 0],

            [1, -1, 1, 1, 0, 1, 0, -1, 0],
            [-1, -1, 1, 1, 0, 1, 0, -1, 0],
            [-1, -1, -1, 1, 0, 1, 0, -1, 0],  # bottom face

            [-1, 1, 1, 0, 0, 1, -1, 0, 0],
            [-1, -1, -1, 0, 0, 1, -1, 0, 0],
            [-1, -1, 1, 0, 0, 1, -1, 0, 0],

            [-1, 1, 1, 0, 0, 1, -1, 0, 0],
            [-1, 1, -1, 0, 0, 1, -1, 0, 0],
            [-1, -1, -1, 0, 0, 1, -1, 0, 0],  # left face

            [1, 1, -1, 0, 1, 0, 1, 0, 0],
            [1, -1, 1, 0, 1, 0, 1, 0, 0],
            [1, -1, -1, 0, 1, 0, 1, 0, 0],

            [1, 1, -1, 0, 1, 0, 1, 0, 0],
            [1, 1, 1, 0, 1, 0, 1, 0, 0],
            [1, -1, 1, 0, 1, 0, 1, 0, 0],  # right face

            [-1, 1, -1, 0, 1, 1, 0, 0, -1],
            [1, -1, -1, 0, 1, 1, 0, 0, -1],
            [-1, -1, -1, 0, 1, 1, 0, 0, -1],

            [-1, 1, -1, 0, 1, 1, 0, 0, -1],
            [1, 1, -1, 0, 1, 1, 0, 0, -1],
            [1, -1, -1, 0, 1, 1, 0, 0, -1]  # back face
        ], 'f')

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 4 * self.lamp_geometry.size, self.lamp_geometry, GL_STATIC_DRAW)

    def enable(self, shader):
        """ Deal with sending relevant information about this light to the shader """
        glUseProgram(shader)

        # Position of the Light Source and its color to shader
        glUniform4fv(glGetUniformLocation(shader, "lightPosition"), 1,
                     self.position)

        glUniform4fv(glGetUniformLocation(shader, "lightColor"), 1,
                     self.color)

    def render(self, shader):
        """ render the lamp on the scene, if needed """

        glUseProgram(self.lamp_geometry_shader)

        self.modelMatrix = np.identity(4, 'f')

        
       

        self.modelMatrix = glm.translate(self.modelMatrix, glm.vec3(self.position[0],
                                         self.position[1],
                                         self.position[2]))
        self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(self.object_rotation[0]), glm.vec3(1.0, 0, 0))    
        self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(self.object_rotation[1]), glm.vec3(0, 1.0, 0))
        self.modelMatrix = glm.rotate(self.modelMatrix, glm.radians(self.object_rotation[2]), glm.vec3(0, 0, 1.0))
        self.modelMatrix = glm.scale(self.modelMatrix, glm.vec3(self.object_scaling[0],
                                     self.object_scaling[1],
                                     self.object_scaling[2]))


        modelLoc = glGetUniformLocation(self.lamp_geometry_shader, "model")
        glUniformMatrix4fv(modelLoc, 1, GL_TRUE, np.array(self.modelMatrix, dtype=np.float32))

        # also send the light color
        glUniform3fv(glGetUniformLocation(self.lamp_geometry_shader, "lampColor"), 1,
                     self.object_color)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * 4, None)
        glEnableVertexAttribArray(0)

        glDrawArrays(GL_TRIANGLES, 0, 36)

        glUseProgram(0)


class VCHelper:
    """ This class provides some helper functions for the Visual Computing class """

    def __init__(self):
        self.windowSize = (0, 0)
        self.shader = None
        self.vao_triangle = None
        self.clock = pg.time.Clock()

        self.geometricObjects = []
        self.lightSources = []

        @dataclass
        class CameraInfo:
            pos_viewer = np.array([0.0, 0.0, 0.0, 0.0], 'f')

        self.camera = CameraInfo()

        # initial values for matrices and relevant positions/orientations
        self.projMatrix = glm.ortho(-1, 1.0, -1.0, 1.0, -1.0, 1.0)
        self.modelMatrix_triangle = np.identity(4, np.float32)
        self.viewMatrix = np.identity(4, np.float32)

        # view volume limits
        self.min_x = self.min_y = self.min_z = -20.0
        self.max_x = self.max_y = self.max_z = 20.0
        self.min_z = -30
        self.max_z = 30

        # square properties
        self.tolerance = 0.1
        self.s_tx = 0  # random.uniform(self.min_x, self.max_x)
        self.s_ty = 0  # random.uniform(self.min_y, self.max_y)
        self.s_tz = 0.0
        self.s_angle = 0.0
        self.s_sx = self.s_sy = self.s_sz = 5
        self.s_anim_scale = 0.001

        self.globalTz = -40;

        # camera parameters
        self.cam_position = np.array([0, 0, 0], 'f')
        self.cam_target = np.array([0, 0, -1], 'f')
        self.cam_direction = np.array([0, 0, -1], 'f')

        # perspective projection parameters
        self.fovy = 45
        self.nearPlane = 2
        self.farPlane = 50

    def add_geometric_object(self, path: str = '', position=None, rotation=None, scale=None, material: str = ''):
        self.geometricObjects.append(GeometricObject(path))

        if position is None:
            position = np.array([0.0, 0.0, 0.0], 'f')

        if scale is None:
            scaleV = np.array([1.0, 1.0, 1.0], 'f')
        else:
            scaleV = np.array([scale, scale, scale], 'f')

        if rotation is None:
            rotation = np.array([0.0, 0.0, 0.0], 'f')

        # very naive way to do it... it applies the translation last, so that one can rotate and scale assuming that the
        # model is placed at the origin.

        self.geometricObjects[-1].set_rotation(rotation)
        self.geometricObjects[-1].set_scale(scaleV)
        self.geometricObjects[-1].set_translation(position)
        self.geometricObjects[-1].set_material_byname(material)

    def add_lightsource(self):
        self.lightSources.append(LightSource())
        self.lightSources[-1].enable(self.shader)

    def initalizeGLWindow(self, width, height):
        """ This function initialized the OpenGL window and context recurring to pygame
            all parameters regarding OpenGL states are set here"""
        pg.init()

        # this may be needed for Metal (apple silicon)
        # pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        # pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        # pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        self.windowSize = (width, height)
        pg.display.set_mode(self.windowSize, DOUBLEBUF | OPENGL | RESIZABLE | BLEND_ALPHA_SDL2)

        glEnable(GL_DEPTH_TEST)

        glEnable(GL_CULL_FACE)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def initShaders(self, vs_file: str, fs_file: str):
        """ init shaders from files on disk """

        # get vertex shader code from file
        vertex_shader_file = open(vs_file, "r")
        vertex_shader_code = vertex_shader_file.read()
        vertex_shader_file.close()

        VERTEX_SHADER = shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER)

        result = glGetShaderiv(VERTEX_SHADER, GL_COMPILE_STATUS)

        if not (result):
            raise RuntimeError(glGetShaderInfoLog(VERTEX_SHADER))

        # get fragment shader code from file
        fragment_shader_file = open(fs_file)
        fragment_shader_code = fragment_shader_file.read()
        fragment_shader_file.close()

        FRAGMENT_SHADER = shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)

        # just compile the shader program including the two configured shaders
        shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        result = glGetProgramiv(shader, GL_LINK_STATUS)

        if not (result):
            raise RuntimeError(glGetProgramInfoLog(self.shader))

        return shader

    def initShaders_Illumination_PerFragment_Halfway(self):
        """ load shaders to implerment per-fragment shader """

        self.shader = self.initShaders("vertex_shader_illumination_perfragment.glsl",
                                       "fragment_shader_illumination_perfragment_halfway.glsl")

        glUseProgram(self.shader)

        self.compute_proj_view_matrix()

    def initShaders_Illumination_PerFragment(self):
        """ load shaders to implerment per-fragment shader """

        self.shader = self.initShaders("vertex_shader_illumination_perfragment.glsl",
                                       "fragment_shader_illumination_perfragment.glsl")

        glUseProgram(self.shader)

        self.compute_proj_view_matrix()

    def initShaders_Illumination_PerVertex(self):
        """ load shaders to implerment per-vertex shader """

        self.shader = self.initShaders("vertex_shader_Illumination_pervertex.glsl",
                                       "fragment_shader_illumination_pervertex.glsl")

        glUseProgram(self.shader)
        self.compute_proj_view_matrix()

    def initShaders_Illumination_PerTriangle(self):
        """ load shaders to implement flat shading """

        self.shader = self.initShaders("vertex_shader_Illumination_pertriangle.glsl",
                                       "fragment_shader_illumination_pertriangle.glsl")

        glUseProgram(self.shader)
        self.compute_proj_view_matrix()

    def initShaders_No_Illumination(self):
        """ load shaders to implement flat shading """

        self.shader = self.initShaders("vertex_shader_Illumination_nolight.glsl",
                                       "fragment_shader_illumination_nolight.glsl")

        glUseProgram(self.shader)
        self.compute_proj_view_matrix()

    def set_geometry_buffers(self):
        """ Generate all the vertex buffers and assign the data to them.
            This is the place to add the objects to the rendered scene.
        """

        # Some objects to add later...

        # self.add_geometric_object('skull.obj', [0, 0, -8], [-90.0, 0, 0], .25, 'chrome')
        # self.add_geometric_object('skull.obj', [8, 0, 0], [-90.0, 0, 0], .25, 'gold')
        # self.add_geometric_object('skull.obj', [-8, 0, 0], [-90.0, 0, 0], .25, 'obsidian')
        # self.add_geometric_object('skull.obj', [0, -8, 0], [-90.0, 0, 0], .25, 'red_plastic')
        # self.add_geometric_object('skull.obj', [0, 8, 0], [-90.0, 0, 0], .25, 'emerald')

        self.add_geometric_object('sphere.obj', [0, 0, 0], [0.0, 0, 0], 6, 'emerald')

        self.add_geometric_object('', [0, 0, -30], [-90.0, 0, 0], 20, 'brass')

    def set_lighting(self):
        """ add and confiture lighting """

        # just add a single light
        # note: the shaders are not prepared for multiple lights!
        self.add_lightsource()

    def render(self):
        """ Render the scene... Runs every frame! """
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.compute_proj_view_matrix()

        try:

            try:

                glUseProgram(self.shader)

                # sending order to render all objects
                for obj in self.geometricObjects:
                    obj.render(self.shader)

                # render the light source position in the scene (white cube)
                self.lightSources[0].render(self.shader)

            finally:
                pass

        finally:
            glUseProgram(0)

        pg.display.flip()

    def compute_proj_view_matrix(self):
        """ compute the projection and view matrices """

        # just ensure that a compute shader has been selected
        glUseProgram(self.shader)

        # self.projMatrix = glm.ortho(self.min_x, self.max_x, self.min_y, self.max_y, self.min_z, self.max_z)
        self.projMatrix = glm.perspective(self.fovy, self.windowSize[0] / self.windowSize[1], self.nearPlane,
                                          self.farPlane)

        projLoc = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(projLoc, 1, GL_TRUE, np.array(self.projMatrix, dtype=np.float32))

        self.viewMatrix = np.identity(4, np.float32)
        self.viewMatrix = glm.translate(self.viewMatrix, glm.vec3(0, 0, self.globalTz))

        viewLoc = glGetUniformLocation(self.shader, "view")
        glUniformMatrix4fv(viewLoc, 1, GL_TRUE, np.array(self.viewMatrix, dtype=np.float32))

        glUniform3fv(glGetUniformLocation(self.shader, "viewerPosition"), 1,
                     self.camera.pos_viewer)

        # lights have individual shaders for rendering the lamp position
        # they need the proj and view transformations too
        for l in self.lightSources:
            glUseProgram(l.lamp_geometry_shader)
            projLoc = glGetUniformLocation(l.lamp_geometry_shader, "projection")
            glUniformMatrix4fv(projLoc, 1, GL_TRUE, np.array(self.projMatrix, dtype=np.float32))
            viewLoc = glGetUniformLocation(l.lamp_geometry_shader, "view")
            glUniformMatrix4fv(viewLoc, 1, GL_TRUE, np.array(self.viewMatrix, dtype=np.float32))

    def process_events(self, pg):
        """ Process all events caught by pygame"""

        # events first
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        # continuously pressed keys
        keys = pg.key.get_pressed()

        # change the fov in the perspective projection
        if keys[pg.K_a]:
            self.fovy += 1
            self.compute_proj_view_matrix()
        if keys[pg.K_z] and self.fovy > 10:
            self.fovy -= 1
            self.compute_proj_view_matrix()

        # if keys[pg.K_b]:
        #     self.geometricObjects[0].object_position += [0.01, 0, 0]
        #     self.geometricObjects[0].changed = True
        # if keys[pg.K_v]:
        #     self.geometricObjects[0].object_position -= [0.01, 0, 0]
        #     self.geometricObjects[0].changed = True

        # change light type
        if keys[pg.K_i]:
            self.lightSources[0].position[3] = 0.0  # directional light
            mygl.lightSources[0].enable(self.shader)
        if keys[pg.K_o]:
            self.lightSources[0].position[3] = 1.0  # point light
            mygl.lightSources[0].enable(self.shader)

        ########################
        # moving the point light
        advance = .1
        if keys[pg.K_UP]:
            self.lightSources[0].position += [0.0, advance, 0.0, 0.0]
            mygl.lightSources[0].enable(self.shader)
        if keys[pg.K_DOWN]:
            self.lightSources[0].position -= [0.0, advance, 0.0, 0.0]
            mygl.lightSources[0].enable(self.shader)
        if keys[pg.K_LEFT]:
            self.lightSources[0].position -= [advance, 0.0, 0.0, 0.0]
            mygl.lightSources[0].enable(self.shader)
        if keys[pg.K_RIGHT]:
            self.lightSources[0].position += [advance, 0.0, 0.0, 0.0]
            mygl.lightSources[0].enable(self.shader)
        if keys[pg.K_w]:
            self.lightSources[0].position -= [0.0, 0.0, advance, 0.0]
            mygl.lightSources[0].enable(self.shader)
        if keys[pg.K_s]:
            self.lightSources[0].position += [0.0, 0.0, advance, 0.0]
            mygl.lightSources[0].enable(self.shader)

        delta_clipPlane = .1
        # keys for changing projection parameters
        if keys[pg.K_PLUS] or keys[pg.K_KP_PLUS]:
            self.max_y += delta_clipPlane
            self.max_x = self.max_y
            self.min_x -= delta_clipPlane
            self.min_y = self.min_x
            self.compute_proj_view_matrix()
            print(self.min_x, ', ', self.max_x)

        if keys[pg.K_MINUS] or keys[pg.K_KP_MINUS]:
            if not (self.max_y + delta_clipPlane < 0):
                self.max_y -= delta_clipPlane
                self.max_x = self.max_y
                self.min_x += delta_clipPlane
                self.min_y = self.min_x
                self.compute_proj_view_matrix()

        ##############################
        # change type of illumination

        if keys[pg.K_1]:
            mygl.initShaders_No_Illumination()
            mygl.lightSources[0].enable(self.shader)
            print("per-nothing")

        if keys[pg.K_2]:
            mygl.initShaders_Illumination_PerTriangle()
            mygl.lightSources[0].enable(self.shader)
            print("per-triangle")

        if keys[pg.K_3]:
            mygl.initShaders_Illumination_PerVertex()
            mygl.lightSources[0].enable(self.shader)
            print("per-vertex")

        if keys[pg.K_4]:
            mygl.initShaders_Illumination_PerFragment()
            mygl.lightSources[0].enable(self.shader)
            print("per-fragment")

        if keys[pg.K_5]:
            mygl.initShaders_Illumination_PerFragment_Halfway()
            mygl.lightSources[0].enable(self.shader)
            print("per-fragment")

    def check_collisions(self):
        pass

    def animate(self):
        # self.cam_position[2] -= .01

        self.s_sx += self.s_anim_scale
        self.s_sy = self.s_sx
        self.s_sz = self.s_sx

        if self.s_sx > 0.25 or self.s_sx < 0.15:
            self.s_anim_scale *= -1

        #self.s_angle += 1

        self.globalTz += .005

        # self.lightSources[0].position = [8*math.sin(math.pi * self.s_angle/180), 0, self.lightSources[0].position[2] -.0005, 0]
        # mygl.lightSources[0].enable(self.shader)
        # print(self.globalTz)


#####################################################################
# MAIN stuff

# create an object of out helper class, where all code is encapsulated
mygl = VCHelper()

# initialize the OpenGL window and context
# it uses pygame, inside
mygl.initalizeGLWindow(800, 800)

# initialize the vertex buffers. For the most recent versions of OpenGL
# it is not possible to initialise the shaders without having some VAO
mygl.set_geometry_buffers()

# compile and initialize the compute shader
mygl.initShaders_No_Illumination()

mygl.set_lighting()

# soundtrack = pg.mixer.Sound("soundtrack.mp3")
# soundtrack.play()

print("""Supported Command:
      ---------------------
      ARROW KEYS: move light in XX and YY
      W and S: move light front and back
      1: no shading
      2: flat shading
      3: per-vertex shading (Gouraud)
      4: per-fragment shading (Phong)
      5: per-fragment shading (Blinn-Phong)""")


while True:
    # this line below just measures the time since it was last called.
    # the parameter for tick is the desired frame rate
    # if the time taken to render a frame (i.e., execute the while
    # one time, is less than the intended frame rate, this line will
    # delay the execution to match it. It ensures that the code runs
    # at the same speed in every machine
    dt = mygl.clock.tick(60)

    # print(f"fps:  {1000 / dt:3.0f}")

    mygl.process_events(pg)  # checking for any pressed keys or events

    mygl.animate()

    mygl.check_collisions()

    mygl.render()
