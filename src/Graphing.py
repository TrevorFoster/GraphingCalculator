#!/usr/bin/python
import sys
import re, MathCalc, copy, pygame, sys

def frange(start, stop, step):
    vals = []
    i = start
    while i <= stop:
        vals.append(i)
        i += step
    return vals

def formatExpression(func):
    global dependentVar

    # Attempts to format multiplication in the expression properly
    # so that it may be successfully evaluated
    def fixMultiplication(func):
        result = re.sub(r"(\b[0-9]+(?:\.[0-9]+)?) *(?=[A-Za-z]+)", lambda match: match.group() + "*", func)

        return re.sub(r"\) *[\w(]", lambda match: "%s*%s"  % (match.group()[0], match.group()[1:]), result)

    # Attempts to format exponents in the expression properly
    # so that it may be successfully evaluated
    def fixExponents(func):
        return re.sub(r"\^+", "**", func)

    # Removes dependant variable from expression if it contains
    # a dependant variable
    def removeDependant(func):
        if func.count("=") == 1:
            parts = func.split("=")

            return parts[1].strip()
        return func

    func = func.strip()
    return removeDependant(fixExponents(fixMultiplication(func)))

def validateFunction(func):
    # Finds total number of unmatched brackets in the expression
    # if negative there are closing brackets missing opening brackets
    # if positive there are opening brackets missing a closing brace
    def matchBrackets(func):
        return func.count("(") - func.count(")")

    # Attempts to find function calls missing opening brace
    def findWithoutOpening(func):
        result = ""
        last = 0
        for op in re.finditer(FUNCREGEX, func):
            i = op.span()[1]

            while i < len(func) and func[i].isspace(): i += 1

            if func[i] != "(":
                result += func[last: i] + "("
                last = i
            else:
                result += func[last: op.span()[1]]
                last = op.span()[1]
        result += func[last:]

        return result

    dif = matchBrackets(findWithoutOpening(func))
    bracks = matchBrackets(func)
    if bracks != 0:
        print "Invalid expression %d unmatched brackets." % bracks
        return False
    elif dif != 0:
        print "Invalid expression %d unmatched brackets." % dif
        return False
    return True

# Graphs the function for the domain passed to the function
# Centers the coordinates around center point
def trace(func, domain, center, zoom):
    graph = []

    for x in domain:
        x /= zoom[0]
        y = MathCalc.readEquation(func, (independentVar, x))
        if y != None:
            graph.append((x * zoom[0] + center[0], -(y * zoom[1]) + center[1]))

    return graph

def drawGraph(coords):
    pygame.draw.lines(screen, [60, 60, 150], False, coords, 3)

def drawAxes(center):
    global WINDW, WINDH

    center = (float(center[0]), float(center[1]))
    pygame.draw.line(screen, [0, 0, 0], [0, center[1]], [WINDW, center[1]], 3)
    pygame.draw.line(screen, [0, 0, 0], [center[0], 0], [center[0], WINDH], 3)    

def drawText(graph):
    dim = [xrange(80), xrange(24)]

    realGraph = map(lambda p: [int(p[0] / zoom[0]),
                               int(p[1] / zoom[1])], graph
                )
    result = "\n".join(
        map(lambda row: "".join(row),
             [map(lambda x: "*" if [x, y] in realGraph else " ", dim[0]) for y in dim[1]])
    

    print result

def fixScale(func):
    global zoom, camView

    zoom[1] = zoom[0]
    needsUpdate = True

def chooseDomain(lower, upper, func):
    global zoom, camView

    boundLength = abs(upper - lower)

    zoom[0] = float(WINDW) / boundLength
    camView = (lower * zoom[0] + WINDW / 2, camView[1])

    needsUpdate = True

def chooseRange(lower, upper, func):
    global zoom, camView

    boundLength = abs(upper - lower)

    zoom[1] = float(WINDH) / boundLength
    camView = (camView[0], -(upper * zoom[1] - WINDH / 2))

    needsUpdate = True

def updateGraph(func):
    global viewGraph, axisView, zoom
    step = float(WINDW) / sigPoints
    domain = frange((-(WINDW / 2.0) + camView[0]), (WINDW / 2.0 + camView[0]), step)

    coords = trace(func, domain, axisCenter, zoom)

    # Translate the graph and axis into view
    viewGraph = translate(camView, *coords)
    axisView = translate(camView, axisCenter)

    needsUpdate = True

# -----------------------------------------------------
# translate:
# params: tuple translation - A vector to translate a vector
# or set of vectors with
# list args         - A list of vectors to be
# translated
#
# return: The array of coordinates translated by the translation
# vector as two tuples
#
# desc: Translates a vector or set of vectors by a translation
# vector
# -------------------------------------------------------
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

def findIndependent(func):
    varsFound = list(set(filter(lambda word: not word in funcList, re.findall("[A-Za-z]\w*", func))))

    if len(varsFound) == 1:
        setIndependant(varsFound[0])
   
def setIndependant(newVar):
    global independentVar

    independentVar = newVar

def setDependant(newVar):
    global dependentVar

    dependentVar = newVar

def changeFunction(newFunc):
    global origFunc, func, needsUpdate

    formatted = formatExpression(newFunc)
    if validateFunction(formatted):
        origFunc = newFunc
        if len(origFunc) == 0:
            origFunc = " "
        func = formatted
        findIndependent(func)
        
        needsUpdate = True
        return font.render(dependentVar + " = " + origFunc, 1, [0, 0, 0])

    return None

def updateXBounds():
    global boundsX

    boundsX = [(-(WINDW / 2.0) + camView[0]) / zoom[0], (WINDW / 2.0 + camView[0]) / zoom[0]]
    for callback in domChangedCallbacks:
        callback(boundsX)

def updateYBounds():
    global boundsY

    boundsY = [(-(WINDH / 2.0) - camView[1]) / zoom[1], (WINDH / 2.0 - camView[1]) / zoom[1]]
    for callback in rngChangedCallbacks:
        callback(boundsY)

def subscribeDomain(callback):
    global domChangedCallbacks

    domChangedCallbacks.append(callback)

def subscribeRange(callback):
    global rngChangedCallbacks

    rngChangedCallbacks.append(callback)

def subAvailable():
    try:
        domChangedCallbacks
    except NameError:
        return False
    else:
        try:
            rngChangedCallbacks
        except NameError:
            return False
        else:
            return True

def run(function = None):
    global WINDW, WINDH, sigPoints, camView, axisCenter, axisView, zoom,\
       screen, viewGraph, func, origFunc, dependentVar, independentVar, FUNCREGEX, funcList,\
       domChangedCallbacks, rngChangedCallbacks, boundsX, boundsY, needsUpdate, font, ZOOMCONST, QUICKZOOMCONST

    WINDW, WINDH = 800, 600
    sigPoints = 300
    ZOOMCONST = 1.08
    QUICKZOOMCONST = 1.01
    zoom = [20, 20]
    camView = (0, 0)
    axisCenter = (WINDW / 2, WINDH / 2)
    viewGraph = []
    axisView = []
    domChangedCallbacks, rngChangedCallbacks = [] , []
    dependentVar, independentVar = "y", "x"
    boundsX = [-10, 10]
    funcList = ["acos", "asin", "atan", "atan2", "ceil", "cos", "cosh",
                   "degrees", "exp", "fabs", "floor", "fmod", "frexp",
                   "hypot", "ldexp", "log", "log10", "modf", "pow",
                   "radians", "sin", "sinh", "sqrt", "tan", "tanh"]

    FUNCREGEX = r"|".join(funcList)

    origFunc = ""

    if function != None:
        origFunc = function[:]
    elif len(sys.argv) > 1:
        origFunc = sys.argv[1]

    needsUpdate = True
    updateBounds = False

    upHeld = False
    downHeld = False
    # Initialize mouse stuff
    leftDown = False
    moved = False
    prevMousePos = None

    pygame.init()
    pygame.font.init()
    pygame.display.init()
    font = pygame.font.SysFont("Courier", 32)
    axesFont = pygame.font.SysFont("Courier", 20)
    screen = pygame.display.set_mode([WINDW, WINDH], pygame.RESIZABLE)

    eqSurf = changeFunction(origFunc)
    chooseDomain(-10, 10, func)
    fixScale(func)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                # store the window's new size
                WINDW, WINDH = event.size

                # re center the axis
                axisCenter = (WINDW / 2, WINDH / 2)
                screen = pygame.display.set_mode([WINDW, WINDH], pygame.RESIZABLE | pygame.DOUBLEBUF)

                updateGraph(func)

            if event.type == pygame.QUIT:
                # exit the game loop
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    drawText(viewGraph)

                if event.key == pygame.K_UP:
                    upHeld = True
                if event.key == pygame.K_DOWN:
                    downHeld = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    upHeld = False
                if event.key == pygame.K_DOWN:
                    downHeld = False

            if event.type == pygame.MOUSEMOTION:
                moved = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    leftDown = True

                # Mouse wheel rolled up
                if event.button == 4:
                    zoomIn(ZOOMCONST)
                    # Update the graph with the new scale
                    needsUpdate = True
                    updateBounds = True

                # Mouse wheel rolled down
                elif event.button == 5:
                    zoomOut(ZOOMCONST)
                    # Update the graph with the new scale
                    needsUpdate = True
                    updateBounds = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    leftDown = False
                    prevMousePos = None

        if upHeld:
            zoomIn(QUICKZOOMCONST)
            needsUpdate = True      # Update the graph with the new scale
            updateBounds = True

        if downHeld:
            zoomOut(QUICKZOOMCONST)
            needsUpdate = True      # Update the graph with the new scale
            updateBounds = True

        if moved and leftDown:
            mPos = pygame.mouse.get_pos()
            if prevMousePos:
                newX = camView[0] + prevMousePos[0] - mPos[0]
                newY = camView[1] + prevMousePos[1] - mPos[1]
                camView = (newX, newY)
                needsUpdate = True
                updateBounds = True

            prevMousePos = mPos
            moved = False

        if updateBounds:
            updateXBounds()
            updateYBounds()
            updateBounds = False

        if needsUpdate:
            updateGraph(func, )
            
            screen.fill([255, 255, 255])

            if eqSurf != None:
                screen.blit(eqSurf, (0, 0))

            drawAxes(axisView)
            if len(viewGraph) >= 2:
                drawGraph(viewGraph)

            pygame.display.update()  # update the screen surface
            needsUpdate = False

    pygame.quit()  # free pygame's resources

if __name__ == "__main__":
    run()
