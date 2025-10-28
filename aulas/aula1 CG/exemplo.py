from OpenGL.GL import *
from OpenGL.GLUT import *

def display():
    # Limpa todos os pixels da tela
    glClear(GL_COLOR_BUFFER_BIT)

    # Desenha um polígono branco (retângulo)
    glBegin(GL_POLYGON)
    glColor3f(0.0, 0.0,0.0) 
    glVertex3f(0.25, 0.25, 0.00)

    glColor3f(1.0, 0.0, 0.0) 
    glVertex3f(0.75, 0.25, 0.00)

    glColor3f(0.0, 1.0, 0.0) 
    glVertex3f(0.75, 0.75, 0.00)

    glColor3f(0.0, 0.0, 1.0) 
    glVertex3f(0.25, 0.75, 0.00)
    glEnd()

    # Troca buffers - double-buffering
    glutSwapBuffers()

def reshape (width, height):
    size = width if width < height else height
    glViewport(0, 0, size, size)

def init():
    # Define a cor de fundo preta
    glClearColor(0.0,0.0,0.0, 1.0)

    # Inicializa as matrizes do OpenGL
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(250, 250)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Hello world!")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)

    glutMainLoop()

if __name__ == "__main__":
    main()