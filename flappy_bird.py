
from turtle import back
import glfw
import sys
from OpenGL.GL import *
from grafica.scene_graph import drawSceneGraphNode
import grafica.text_renderer as tx
from modelo import *
from controlador import Controller

if __name__ == '__main__':

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, 'Plaffy Burd', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTextureTransformShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Telling OpenGL to use our shader program
    #glUseProgram(pipeline.shaderProgram)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # HACEMOS LOS OBJETOS
    background = Background(pipeline)
    bird = Birdie(pipeline)
    pipes = PipeCreator()
    ground = Ground(pipeline)
    victory = sys.argv[1]
    score = Scoreboard(textPipeline, bird)
    defeatscreen = DefeatScreen(pipeline)
    victoryscreen = VictoryScreen(pipeline)

    controlador.set_model(bird)
    controlador.set_pipes(pipes)

    t0 = 0
    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input

        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        glUseProgram(pipeline.shaderProgram)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        pipes.create_pipe(pipeline)  # Aleatorio
        pipes.update(0.6 * dt)  
        bird.update(0.1*dt)
        background.update(0.5*dt)
        score.update(pipes, bird)
        
        # Reconocer la logica
        bird.collide(pipes)  
        bird.hasWon(victory, pipes)

        # DIBUJAR LOS MODELOS

        background.draw(pipeline)        
        bird.draw(pipeline)
        pipes.draw(pipeline)
        ground.draw(pipeline)
        defeatscreen.draw(pipeline, bird)
        victoryscreen.draw(pipeline, bird)

        glUseProgram(textPipeline.shaderProgram)

        score.draw(textPipeline)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()
