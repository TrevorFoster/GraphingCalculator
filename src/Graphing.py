#!/usr/bin/python
import sys
from CLineReadFile import relativePath
sys.path.insert(0, relativePath(sys.path[0], 1, "/lib"))
try:
    import pyglet
except ImportError:
    print "Installing Pyglet... Please wait a moment..."
    from subprocess import call

    call(["make", "-C", relativePath(sys.path[0], 1, "")])
    del call
    
    try:
        import pyglet
    except ImportError:
        print "Pyglet not found."
        sys.exit(0)

import re, random, MathCalc, GraphUtils
from pyglet.window import key, mouse
from pyglet.gl import *

# Graphs the function for the domain passed to the function
# Centers the coordinates around center point
def traceDomain(func, domain, center, zoom):
    global camView
    graph = []

    ind = GraphUtils.findIndependent(func)
    if ind != None:
        ind = ind[0]
    for x in domain:
        x /= zoom[0]
        y = MathCalc.readEquation(func, (ind, x))
        if y != None:
            graph += (x * zoom[0] + center[0] - camView[0],
                constants.WINDH - (-(y * zoom[1]) + center[1]) + camView[1])

    return graph

def traceRange(func, grange, center, zoom):
    global camView
    graph = []

    ind = GraphUtils.findIndependent(func)
    if ind != None:
        ind = ind[0]
    for y in grange:
        y /= zoom[1]
        x = MathCalc.readEquation(func, (ind, y))
        if x != None:
            graph += (x * zoom[0] + center[0] - camView[0],
                constants.WINDH - (-(y * zoom[1]) + center[1]) + camView[1])

    return graph

# Draws 
def drawGraph(coords, colour):
    pyglet.graphics.draw(len(coords) / 2, pyglet.gl.GL_LINE_STRIP,
        ('v2f', coords),
        ('c4f', colour * (len(coords) / 2))
    )
    
# Draws both the x and y axes centered around center
def drawAxes(center):
    # Offset center y by OpenGL draw origin
    center = (float(center[0]), constants.WINDH - float(center[1]))

    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
        ('v2f', (0, center[1], constants.WINDW, center[1])),
        ('c4f', (0.196078431, 0.196078431, 0.196078431, 0, 0.196078431, 0.196078431, 0.196078431, 0))
    )
    

    pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
        ('v2f', (center[0], constants.WINDH, center[0], 0)),
        ('c4f', (0.196078431, 0.196078431, 0.196078431, 0, 0.196078431, 0.196078431, 0.196078431, 0))
    )
    

def drawText(graph):
    dim = [xrange(60), xrange(18)]

    realGraph = map(lambda p: [int(p[0] / zoom[0]), int(p[1] / zoom[1])], (zip(graph[0::2], graph[1::2])))

    result = "\n".join(
        map(lambda row: "".join(row),
             [map(lambda x: "*" if [x, y] in realGraph else " ", dim[0]) for y in dim[1]])
        )

    print result

def fixScale():
    global zoom, camView

    zoom[1] = zoom[0]
    update.needsUpdate = True

def chooseDomain(lower, upper):
    global zoom, camView

    boundLength = abs(upper - lower)

    zoom[0] = float(constants.WINDW) / boundLength
    camView = (lower * zoom[0] + constants.WINDW / 2.0, camView[1])

    update.needsUpdate = True

def chooseRange(lower, upper):
    global zoom, camView

    boundLength = abs(upper - lower)

    zoom[1] = float(constants.WINDH) / boundLength
    camView = (camView[0], -(upper * zoom[1] - constants.WINDH / 2.0))

    update.needsUpdate = True

def graphDomain(func):
    global camView, zoom, axisCenter

    step = float(constants.WINDW) / (constants.SIGPOINTS / 2.0)

    domain = GraphUtils.frange((-(constants.WINDW / 2.0) + camView[0]) - 1,
            (constants.WINDW / 2.0 + camView[0]) + 1, step)

    viewGraph = traceDomain(GraphUtils.removeDependant(func), domain, axisCenter, zoom)
    return viewGraph

def graphRange(func):
    global camView, zoom, axisCenter

    step = float(constants.WINDH) / (constants.SIGPOINTS / 2.0)
    grange = GraphUtils.frange((-(constants.WINDH / 2.0) - camView[1]) - 1,
            (constants.WINDH / 2.0 - camView[1]) + 1, step)

    viewGraph = traceRange(GraphUtils.removeDependant(func), grange, axisCenter, zoom)
    return viewGraph

def updateGraph(func):
    global axisView, zoom, camView, axisCenter

    dependant = GraphUtils.findDependant(func)
    if dependant in "yY":
        viewGraph = graphDomain(func)
    elif dependant in "xX":
        viewGraph = graphRange(func)
    else:
        independant = GraphUtils.findIndependent(func)

        if "y" in independant or "Y" in independant:
            viewGraph = graphRange(func)
        elif "x" in independant or "X" in independant:
            viewGraph = graphDomain(func)
        else:
            viewGraph = graphDomain(func)

    # Translate the graph and axis into view
    axisView = translate(camView, axisCenter)

    return viewGraph

def translate(translation, *args):
    translated = []
    transX, transY = translation
    for p in args:
        translated.append([p[0] - transX, p[1] - transY])

    if len(translated) == 1:
        return translated[0]
    else:
        return translated


def zoomIn(zoomSpeed):
    global zoom, camView

    # Scale the function up in x and y direction
    zoom[0] *= zoomSpeed
    zoom[1] *= zoomSpeed
    # Center the camera while zooming
    camView = (camView[0] * zoomSpeed, camView[1] * zoomSpeed)


def zoomOut(zoomSpeed):
    global zoom, camView

    # Scale the function up in x and y direction
    zoom[0] /= zoomSpeed
    zoom[1] /= zoomSpeed
    # Center the camera while zooming
    camView = (camView[0] / zoomSpeed, camView[1] / zoomSpeed)

def addFunction(newFunc):
    global functions, independant, colours

    formatted = GraphUtils.formatExpression(newFunc)
    if GraphUtils.validateFunction(formatted):
        origFunc = newFunc
        if len(origFunc) == 0:
            origFunc = " "
        func = formatted
        independant = GraphUtils.findIndependent(func)

        functions.append(func)
        for i in range(len(functions)):
            functions[i] = GraphUtils.nestFunctions(functions[i], functions[:i] + functions[i + 1:])

        graphs.append([])
        colours.append(chooseColour())

        update.needsUpdate = True

def chooseColour():
    global lastColour

    if lastColour == -1:
        lastColour = random.randint(0, len(constants.PRECOLOURS) - 1)

    lastColour += 1
    if lastColour >= len(constants.PRECOLOURS):
        lastColour = 0
    return constants.PRECOLOURS[lastColour]

def update(dt):
    global functions

    if update.upHeld:
        zoomIn(constants.QUICKZOOMCONST)
        update.needsUpdate = True      # Update the graph with the new scale
    if update.downHeld:
        zoomOut(constants.QUICKZOOMCONST)
        update.needsUpdate = True      # Update the graph with the new scale

    if update.needsUpdate:
        for i in range(len(graphs)):
            graphs[i] = updateGraph(functions[i])
        update.needsUpdate = False

def constants():
    constants.WINDW = 800
    constants.WINDH = 600
    constants.SIGPOINTS = 600
    constants.ZOOMCONST = 1.08
    constants.QUICKZOOMCONST = 1.01
    def toOpenGL(colour):
        return map(lambda component: component / 255., colour)

    constants.PRECOLOURS = map(lambda colour: toOpenGL(colour), [
        [79, 129, 189, 0], [128, 100, 162, 0], [247, 150, 70, 0], [0, 0, 0, 0],
        [155, 200, 89, 0]
    ])

def run():
    global zoom, camView, dependentVar, independentVar, axisView, functions, graphs, colours, lastColour
    constants()        # define necessary constants
    zoom = [20, 20]
    camView = (0, 0)
    axisCenter = (constants.WINDW / 2, constants.WINDH / 2)
    axisView = axisCenter

    independentVar, dependentVar = "x", "y"
    boundsX = [-10, 10]
    boundsY = [-7.5, 7.5]
    functions = []
    graphs = []
    colours = []
    lastColour = -1
    origFunc = ""
    if len(sys.argv) > 1:
        print sys.argv
        funcs = int(sys.argv[1])
        for i in range(2, 2 + funcs):
            addFunction(sys.argv[i])
        if len(sys.argv) > 2 + funcs:
            boundsX = map(lambda i: float(i), sys.argv[2 + funcs].split(","))
        if len(sys.argv) > 3 + funcs:
            print sys.argv[3]
            boundsY = map(lambda i: float(i), sys.argv[3 + funcs].split(","))

    update.needsUpdate = True
    updateBounds = False

    update.upHeld = False
    update.downHeld = False

    chooseDomain(boundsX[0], boundsX[1])
    chooseRange(boundsY[0], boundsY[1])

    update.needsUpdate = True

    window = pyglet.window.Window(resizable=True, caption="Graph Window", width=constants.WINDW, height=constants.WINDH)
    pyglet.clock.schedule(update)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == key.UP:
            update.upHeld = True
        if symbol == key.DOWN:
            update.downHeld = True
        if symbol == key.RETURN:
            drawText(viewGraph)

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol == key.UP:
            update.upHeld = False
        if symbol == key.DOWN:
            update.downHeld = False

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        global camView
        if mouse.LEFT & buttons:
            newX = camView[0] - dx
            newY = camView[1] + dy
            camView = (newX, newY)
            update.needsUpdate = True

    @window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        if scroll_y > 0:
            zoomIn(constants.ZOOMCONST)
        else:
            zoomOut(constants.ZOOMCONST)

        # Update the graph with the new scale
        update.needsUpdate = True

    @window.event
    def on_draw():
        glClearColor(1, 1, 1, 1)
        window.clear()

        glLineWidth(2.5)
        glEnable(GL_LINE_SMOOTH)

        drawAxes(axisView)

        glLineWidth(3.0)

        for i in range(len(graphs)):
            drawGraph(graphs[i], colours[i])

        glFlush()

    @window.event
    def on_resize(width, height):
        global axisCenter
    
        # store the window's new size
        constants.WINDW, constants.WINDH = width, height

        # re center the axis
        axisCenter = (width / 2.0, height / 2.0)
    
        update.needsUpdate = True

    pyglet.app.run()

if __name__ == "__main__":
    run()