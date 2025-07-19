
from OpenGL.GL import *
import pygame as pg
from pygame.locals import *

pg.init()
window_size = (640, 480)
pg.display.set_mode(window_size, DOUBLEBUF | OPENGL | RESIZABLE)

glClearColor(0.0, 1.0, 0.0, 1.0)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()

    glClear(GL_COLOR_BUFFER_BIT)
    pg.display.flip()
