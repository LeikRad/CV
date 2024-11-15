import random

from panda3d.core import loadPrcFile
from panda3d.core import *
loadPrcFile("config.prc")
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import os, sys
import math

class MyGame(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # Get the location of the 'py' file I'm running:
        self.mydir = os.path.abspath(sys.path[0])
        # convert to panda's specific notation
        self.mydir = Filename.fromOsSpecific(self.mydir).getFullpath()


# create an object for the game and run it
game = MyGame()
game.run()