import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import os.path
from grafica.gpu_shape import GPUShape
from OpenGL.GL import *

from OpenGL.GL import glClearColor, GL_STATIC_DRAW
import random
from typing import List


def create_gpu(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu

def create_gpu_bird(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    spritesDirectory = os.path.join(thisFolderPath, "Sprites")
    spritePath = os.path.join(spritesDirectory, "pidgey_sprite.png")
    gpu.texture = es.textureSimpleSetup(
    spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpu

def create_gpu_ground(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    spritesDirectory = os.path.join(thisFolderPath, "Sprites")
    spritePath = os.path.join(spritesDirectory, "pidgey_sprite.png")
    gpu.texture = es.textureSimpleSetup(
    spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpu

def create_gpu_pipe(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    spritesDirectory = os.path.join(thisFolderPath, "Sprites")
    spritePath = os.path.join(spritesDirectory, "pipe_sprite.png")
    gpu.texture = es.textureSimpleSetup(
    spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpu

class Birdie(object):

    def __init__(self, pipeline):
        # Figuras básicas
        gpu_body_quad = create_gpu_bird(bs.createTextureQuad(1, 1), pipeline)  # rosado

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        body.childs += [gpu_body_quad]

        # Ensamblamos el mono
        mono = sg.SceneGraphNode('bird')
        mono.transform = tr.matmul([tr.scale(0.2, 0.2, 0), tr.translate(-3.0, 0, 0)])
        mono.childs += [body]

        transform_mono = sg.SceneGraphNode('birdTR')
        transform_mono.childs += [mono]

        self.model = transform_mono
        self.pos = 0  
        self.y = 0  # Variable que indica la posicion visual del pajaro
        self.puntaje = 0
        self.alive = True


    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def modifymodel(self):
        # Transforma la geometria del modelo segun las variables internas
        # Podria ser una funcion hiper gigante
        self.model.transform = tr.translate(0, self.y, 0)
        

    def update(self, dt):

        gravity = 0.5
        dt *= 10
        if self.pos == 1 and self.y <= 0.85:
            self.y += dt  # no lineal, cos(...)
        elif self.pos == 0 and self.y >= -0.75:
            self.y -= gravity*(dt)
        elif self.pos == 1 and self.y >= 0.85:
            self.y += 0
        elif self.pos == 0 and self.y <= -0.75:
            self.y -= 0

        # modificar de manera constante al modelo
        # aqui deberia llamar a tr.translate
        self.modifymodel()

    def move_up(self):
        if not self.alive:
            return
        self.pos = 1

    def move_center(self):
        if not self.alive:
            return
        self.pos = 0

    def collide(self, pipes: 'PipeCreator'):
        if not pipes.on:  # Si el jugador perdió, no detecta colisiones
            return



        deleted_pipes = []
        for e in pipes.pipes:
            if (-0.45 >= e.pos_x >= -0.9) and ((e.pos_y - 0.75) <= self.y <= (e.pos_y + 0.75)):
                print('Juego terminado. Puntuacion final: ' + str(self.puntaje))

                pipes.die()  # Básicamente cambia el color del fondo, pero podría ser algo más elaborado, obviamente
                self.alive = False
            elif self.y <= -0.75: #Choca contra el suelo
                pipes.die()
                self.alive = False

            elif e.pos_x < -1.1: #Logro pasar un obstaculo de manera exitosa
                self.puntaje += 1
                print('Puntuacion actual:' + str(self.puntaje))
                deleted_pipes.append(e)
        pipes.delete(deleted_pipes)

    def hasWon(self, victoryPoints): #Revisa si logro obtener el puntaje
        if int(victoryPoints) == self.puntaje:
            self.win()
            self.alive = False
    
    def win(self):
        glClearColor(0, 1, 0, 1.0)  # Cambiamos a verde pq gano :D

      
class Ground(object):

    def __init__(self, pipeline):
        gpu_ground = create_gpu_ground(bs.createTextureQuad(1, 1), pipeline)

        ground = sg.SceneGraphNode('ground')
        ground.transform = tr.scale(9999, 0.25, 1)
        ground.childs += [gpu_ground]

        ground_tr = sg.SceneGraphNode('groundTR')
        ground_tr.childs += [ground]

        self.model = ground_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(0, -1, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class Pipe(object):

    def __init__(self, pipeline):
        gpu_pipe = create_gpu_pipe(bs.createTextureQuad(1, 1), pipeline)

        pipe = sg.SceneGraphNode('pipe')
        pipe.transform = tr.scale(0.1, 0.75, 1)
        pipe.childs += [gpu_pipe]

        pipe_tr = sg.SceneGraphNode('pipeTR')
        pipe_tr.childs += [pipe]

        self.pos_y = random.choice([-1, 1])  # LOGICA
        self.pos_x = 1
        self.model = pipe_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, 0.7 * self.pos_y, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def update(self, dt):
        self.pos_x -= dt


class PipeCreator(object):
    pipes: List['Pipe']

    def __init__(self):
        self.pipes = []
        self.on = True

    def die(self):
        glClearColor(1, 0, 0, 1.0)  # Cambiamos a rojo
        self.on = False  # Dejamos de generar pipes, si es True es porque el jugador ya perdió

    def create_pipe(self, pipeline):
        if len(self.pipes) >= 3 or not self.on:  # No puede haber un máximo de 3 pipes en pantalla
            return
        if random.random() < 0.01:
            self.pipes.append(Pipe(pipeline))

    def draw(self, pipeline):
        for k in self.pipes:
            k.draw(pipeline)

    def update(self, dt):
        for k in self.pipes:
            k.update(dt)

    def delete(self, d):
        if len(d) == 0:
            return
        remain_pipes = []
        for k in self.pipes:  # Recorro todos los huevos
            if k not in d:  # Si no se elimina, lo añado a la lista de huevos que quedan
                remain_pipes.append(k)
        self.pipes = remain_pipes  # Actualizo la lista
