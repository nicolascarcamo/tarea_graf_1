import grafica.transformations as tr
import grafica.text_renderer as tx
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

def create_gpu_background(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    spritesDirectory = os.path.join(thisFolderPath, "Sprites")
    spritePath = os.path.join(spritesDirectory, "forest_background.png")
    gpu.texture = es.textureSimpleSetup(
    spritePath, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
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
    spritePath = os.path.join(spritesDirectory, "groundBlockSprite.png")
    gpu.texture = es.textureSimpleSetup(
    spritePath, GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
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

class Background(object):
    def __init__(self, pipeline):
        backgroundShape = bs.createTextureQuad(1, 1)
        #bs.scaleVertices(backgroundShape, 100, [10, 10, 1])
        gpu_background = create_gpu_background(backgroundShape, pipeline)
        
        background = sg.SceneGraphNode('background')
        background.transform = tr.scale(2, 2, 1)
        background.childs += [gpu_background]

        background_tr = sg.SceneGraphNode('backgroundTR')
        background_tr.childs += [background]

        self.model = background_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(0, 0, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class Scoreboard(object):
    def __init__(self, textPipeline):
        textBitsTexture = tx.generateTextBitsTexture()
        gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
        headerText = "Puntuacion: "
        headerCharSize = 0.1
        headerCenterX = headerCharSize * len(headerText) / 2
        headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
        self.gpuHeader = es.GPUShape().initBuffers()
        textPipeline.setupVAO(self.gpuHeader)
        self.gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
        self.gpuHeader.texture = gpuText3DTexture
        self.headerTransform = tr.matmul([
            tr.translate(-0.25, 0.9, 0),
            #tr.rotationZ(np.pi / 2),
        ])

    def draw(self, textPipeline):
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1, 1, 1, 0)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0, 0, 0, 1)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, self.headerTransform)
        textPipeline.drawCall(self.gpuHeader)



class Birdie(object):

    def __init__(self, pipeline):
        # Figuras básicas
        gpu_body_quad = create_gpu_bird(bs.createTextureQuad(1, 1), pipeline)

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
        if self.pos == 1 and self.y <= 0.9:
            self.y += dt  # no lineal, cos(...)
        elif self.pos == 0 and self.y >= -0.75:
            self.y -= gravity*(dt)
        elif self.pos == 1 and self.y >= 0.9:
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
        gpu_ground = create_gpu_ground(bs.createTextureQuad(45, 8), pipeline)

        ground = sg.SceneGraphNode('ground')
        ground.transform = tr.scale(2, 0.3, 1)
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
