import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es

from OpenGL.GL import glClearColor, GL_STATIC_DRAW
import random
from typing import List


def create_gpu(shape, pipeline):
    gpu = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu


class Birdie(object):

    def __init__(self, pipeline):
        # Figuras básicas
        gpu_body_quad = create_gpu(bs.createColorQuad(1, 0.8, 0.8), pipeline)  # rosado
        gpu_leg_quad = create_gpu(bs.createColorQuad(1, 0.5, 1), pipeline)  # rosado fuerte
        gpu_eye_quad = create_gpu(bs.createColorQuad(1, 1, 1), pipeline)  # blanco

        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        body.childs += [gpu_body_quad]

        # Creamos las piernas
        leg = sg.SceneGraphNode('leg')  # pierna generica
        leg.transform = tr.scale(0.25, 0.25, 1)
        leg.childs += [gpu_leg_quad]

        # Izquierda
        leg_izq = sg.SceneGraphNode('legLeft')
        leg_izq.transform = tr.translate(-0.5, -0.5, 0)  # tr.matmul([])..
        leg_izq.childs += [leg]

        leg_der = sg.SceneGraphNode('legRight')
        leg_der.transform = tr.translate(0.5, -.5, 0)
        leg_der.childs += [leg]

        # Ojitos
        eye = sg.SceneGraphNode('eye')
        eye.transform = tr.scale(0.25, 0.25, 1)
        eye.childs += [gpu_eye_quad]

        eye_izq = sg.SceneGraphNode('eyeLeft')
        eye_izq.transform = tr.translate(-0.3, 0.5, 0)
        eye_izq.childs += [eye]

        eye_der = sg.SceneGraphNode('eyeRight')
        eye_der.transform = tr.translate(0.3, 0.5, 0)
        eye_der.childs += [eye]

        # Ensamblamos el mono
        mono = sg.SceneGraphNode('bird')
        mono.transform = tr.matmul([tr.scale(0.2, 0.2, 0), tr.translate(-3.0, 0, 0)])
        mono.childs += [body, leg_izq, leg_der, eye_izq, eye_der]

        transform_mono = sg.SceneGraphNode('birdTR')
        transform_mono.childs += [mono]

        self.model = transform_mono
        self.pos = 0  # -1, 0, 1
        self.y = 0  # Variable que indica la posicion visual de chansey (-0.7, 0.7)
        self.puntaje = 0
        self.alive = True

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def modifymodel(self):
        # Transforma la geometria del modelo segun las variables internas
        # Podria ser una funcion hiper gigante
        self.model.transform = tr.translate(0, self.y, 0)

    def update(self, dt):
        """
        Modifica x tal que satisfaga las constantes internas del modelo.
        x-->f(dt,self.pos)
        dt: incrementar/decrementar la variable (+sumo, -resto) *2dt, 3dt....
        self.pos ---> -1 ---> x->0.7
        self.pos ---> 0 ----> x =0
        self.pos ---> 1---->x = 0.7
        """
        gravity = 0.5
        dt *= 10
        if self.pos == 1:
            self.y += dt  # no lineal, cos(...)
        elif self.pos == 0:
            self.y -= gravity*(dt)
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
            if (-0.45 >= e.pos_x >= -0.9 and self.pos == e.pos_y) or (self.y < -0.75):
                print('Juego terminado. Puntuacion final: ' + str(self.puntaje))
                """
                En este caso, podríamos hacer alguna pestaña de alerta al usuario,
                cambiar el fondo por alguna textura, o algo así, en este caso lo que hicimos fue
                cambiar el color del fondo de la app por uno rojo.
                """
                pipes.die()  # Básicamente cambia el color del fondo, pero podría ser algo más elaborado, obviamente
                self.alive = False
            elif e.pos_x < -1.1 and e.pos_y != self.pos:
                self.puntaje += 1
                print('Puntuacion actual:' + str(self.puntaje))
                deleted_pipes.append(e)
        pipes.delete(deleted_pipes)

class Ground(object):

    def __init__(self, pipeline):
        gpu_ground = create_gpu(bs.createColorQuad(0.4, 0.5, 0), pipeline)

        ground = sg.SceneGraphNode('ground')
        ground.transform = tr.scale(1, 1, 0)
        ground.childs += [gpu_ground]

        ground_tr = sg.SceneGraphNode('groundTR')
        ground_tr.childs += [ground]

        self.pos_y = -1
        self.pos_x = 0
        self.model = ground

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, self.pos_y, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")


class Pipe(object):

    def __init__(self, pipeline):
        gpu_pipe = create_gpu(bs.createColorQuad(0.780, 0, 0.223), pipeline)

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

    def die(self):  # DARK SOULS
        glClearColor(1, 0, 0, 1.0)  # Cambiamos a rojo
        self.on = False  # Dejamos de generar huevos, si es True es porque el jugador ya perdió

    def create_pipe(self, pipeline):
        if len(self.pipes) >= 2 or not self.on:  # No puede haber un máximo de 10 huevos en pantalla
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
