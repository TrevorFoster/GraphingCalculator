import pygame, re, sys, MathCalc

def frange(start, stop, step):
    vals = []
    i = start
    while i <= stop:
        vals.append(i)
        i += step
    return vals

def formatFunction(func):
    def fixMultiplication(func):
        result = re.sub(r"(\b[0-9]+(?:\.[0-9]+)?) *(?=[A-Za-z]+)", lambda match: match.group() + "*", func)
        return re.sub(r"\) *[\w(]", lambda match: match.group()[0] + "*" + match.group()[1:], result)

    def fixExponents(func):
        return re.sub(r"\^", "**", func)

    return fixExponents(fixMultiplication(func))

def validateFunction(func):
    def matchBrackets(func):
        openBrackets = 0
        for c in func:
            if c == "(":
                openBrackets += 1
            if c == ")":
                openBrackets -= 1
        return openBrackets

    def findWithout(func):
        aliases = ["acos", "asin", "atan", "atan2", "ceil", "cos", "cosh",
                   "degrees", "exp", "fabs", "floor", "fmod", "frexp",
                   "hypot", "ldexp", "log", "log10", "modf", "pow",
                   "radians", "sin", "sinh", "sqrt", "tan", "tanh"]

        regex = r"|".join(aliases)
        result = ""
        last = 0
        for op in re.finditer(regex, func):
            i = op.span()[1]
            if i >= len(func) - 1:
                invalid = True
            else:
                invalid = False
                while i < len(func):
                    if func[i] == "(":
                        break
                    elif func[i] == " ":
                        i += 1

                    else:
                        invalid = True
                        break
                    if i == len(func) - 1:
                        invalid = True
                        break

            if invalid:
                print func[last:i]
                result += func[last: i] + "("
                last = i
            else:
                result += func[last: op.span()[1]]
                last = op.span()[1]
        result += func[last:]

        return result

    dif = matchBrackets(findWithout(func))
    bracks = matchBrackets(func)
    if bracks != 0:
        print "Invalid expression %d unmatched brackets." % bracks
        return False
    elif dif != 0:
        print "Invalid expression %d unmatched brackets." % dif
        return False
    return True

def trace(func, domain, center):
    graph = []

    for x in domain:
        x /= zoomX
        y = MathCalc.safeEval(func, x)
        if y != None:
            graph.append((x * zoomX + center[0], -(y * zoomY) + center[1]))

    return graph


def drawGraph(coords):
    pygame.draw.lines(screen, [60, 60, 150], False, coords, 3)
    #pygame.draw.aalines(screen, [60, 60, 150], False, translate((0, 3), *viewGraph), True)
    #pygame.draw.aalines(screen, [60, 60, 150], False, translate((0, -2), *viewGraph), True)


def drawAxes(center):
    center = (float(center[0]), float(center[1]))
    pygame.draw.line(screen, [0, 0, 0], [0, center[1]], [WINDW, center[1]], 3)
    pygame.draw.line(screen, [0, 0, 0], [center[0], 0], [center[0], WINDH], 3)

##    width = abs(bounds[1] - bounds[0])
##    c = 0
##
# for i in xrange(0, len(coords), 50):
##        label = axesFont.render(str(coords[i][0] / zoomX), 1, [100, 100, 100])
##        screen.blit(label, (coords[i][0] - camView[0], center[1]))


def drawText(graph):
    dim = [xrange(80), xrange(24)]

    realGraph = map(lambda p: [int(p[0] / zoomX),
                               int(p[1] / zoomY)], graph)
    result = ""
    for y in dim[1]:
        for x in dim[0]:
            if [x, y] in realGraph:
                result += "*"
            else:
                result += " "
        result += "\n"

    print result

def fixScale(func):
    global zoomX, zoomY, camView

    zoomY = zoomX

    updateGraph(func)

def chooseRange(lower, upper, func):
    global zoomX, zoomY, camView

    boundLength = abs(upper - lower)

    zoomY = float(WINDH) / boundLength
    camView = (camView[0], lower * zoomY + (-WINDH if lower >= 0 else WINDH) / 2)

    updateGraph(func)

def chooseDomain(lower, upper, func):
    global zoomX, zoomY, camView

    boundLength = abs(upper - lower)

    zoomX = float(WINDW) / boundLength
    camView = (lower * zoomX + WINDW / 2, camView[1])

    updateGraph(func)


def updateGraph(func):
    global viewGraph, axisView, bounds
    step = float(WINDW) / sigPoints
    domain = frange((-(WINDW / 2.0) + camView[0]), (WINDW / 2.0 + camView[0]), step)

    bounds = [min(domain) / zoomX, max(domain) / zoomX]
    coords = trace(func, domain, axisCenter)

    # Translate the graph and axis into view
    viewGraph = translate(camView, *coords)
    axisView = translate(camView, axisCenter)

# -----------------------------------------------------
# translate:
# params: tuple translation - A vector to translate a vector
# or set of vectors with
# list args         - A list of vectors to be
# translated
##
# return: The array of coordinates translated by the translation
# vector as two tuples
##
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
    global zoomX, zoomY, camView

    # Scale the function up in x and y direction
    zoomX *= zoomSpeed
    zoomY *= zoomSpeed
    # Center the camera while zooming
    camView = (camView[0] * zoomSpeed, camView[1] * zoomSpeed)


def zoomOut(zoomSpeed):
    global zoomX, zoomY, camView

    # Scale the function up in x and y direction
    zoomX /= zoomSpeed
    zoomY /= zoomSpeed
    # Center the camera while zooming
    camView = (camView[0] / zoomSpeed, camView[1] / zoomSpeed)


def changeFunction(newFunc):
    global origFunc, func

    formatted = formatFunction(newFunc)
    if validateFunction(formatted):
        origFunc = newFunc
        func = formatted
        updateGraph(func)
        fixScale(func)

def run():
    global WINDW, WINDH, sigPoints, camView, zoomX, zoomY, axisCenter, axisView, screen, viewGraph, func, origFunc
    WINDW, WINDH = 800, 600
    sigPoints = 500
    ZOOMCONST = 1.08
    QUICKZOOMCONST = 1.01
    zoomX, zoomY = 20, 20
    camView = (0, 0)

    origFunc = ""
    if len(sys.argv) > 1:
        origFunc = sys.argv[1]

    func = formatFunction(origFunc)
    valid = validateFunction(func)

    if not valid:
        sys.exit(1)

    axisCenter = (WINDW / 2, WINDH / 2)

    viewGraph = []
    axisView = []

    updateGraph(func)
    chooseDomain(-10, 10, func)
    chooseRange(-1, 1, func)

    # Initialize mouse stuff
    leftDown = False
    moved = False
    prevMousePos = None

    upHeld = False
    downHeld = False

    needsUpdate = False

    screen = None

    running = True
    last = False
    pygame.init()
    font = pygame.font.SysFont("Courier", 32)
    axesFont = pygame.font.SysFont("Courier", 20)
    screen = pygame.display.set_mode([WINDW, WINDH], pygame.RESIZABLE)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                # store the window's new size
                WINDW, WINDH = event.size

                # re center the axis
                axisCenter = (WINDW / 2, WINDH / 2)
                screen = pygame.display.set_mode([WINDW, WINDH], pygame.RESIZABLE)

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

                # Mouse wheel rolled down
                elif event.button == 5:
                    zoomOut(ZOOMCONST)
                    # Update the graph with the new scale
                    needsUpdate = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    leftDown = False
                    prevMousePos = None

        if upHeld:
            zoomIn(QUICKZOOMCONST)
            # Update the graph with the new scale
            needsUpdate = True

        if downHeld:
            zoomOut(QUICKZOOMCONST)
            # Update the graph with the new scale
            needsUpdate = True

        if moved and leftDown:
            mPos = pygame.mouse.get_pos()
            if prevMousePos:
                newX = camView[0] + prevMousePos[0] - mPos[0]
                newY = camView[1] + prevMousePos[1] - mPos[1]
                camView = (newX, newY)
                needsUpdate = True

            prevMousePos = mPos
            moved = False

        if needsUpdate:
            updateGraph(func)
            needsUpdate = False

        screen.fill([255, 255, 255])

        eq = font.render("f(x) = " + origFunc, 1, [0, 0, 0])
        screen.blit(eq, (0, 0))

        drawAxes(axisView)
        if len(viewGraph) >= 2:
            drawGraph(viewGraph)

        pygame.display.flip()  # update the screen surface

    pygame.quit()  # free pygame's resources

if __name__ == "__main__":
    run()
