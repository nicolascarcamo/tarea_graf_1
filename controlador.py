"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

from modelo import Birdie, PipeCreator
import glfw
import sys
from typing import Union


class Controller(object):
    model: Union['Birdie', None]  # Con esto queremos decir que el tipo de modelo es 'Chansey' (nuestra clase) ó None
    pipes: Union['PipeCreator', None]

    def __init__(self):
        self.model = None
        self.pipes = None

    def set_model(self, m):
        self.model = m

    def set_pipes(self, e):
        self.pipes = e

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        elif key == glfw.KEY_UP and action == glfw.PRESS:
            # print('Move left')
            self.model.move_up()

        elif  key == glfw.KEY_UP and action == glfw.RELEASE:
            self.model.move_center()

        # Raton toca la pantalla....
        else:
            print('Unknown key')
