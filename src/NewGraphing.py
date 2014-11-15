import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], os.pardir)) + "/lib")
try:
	import pyglet
except ImportError:
	print "Pyglet was not found."
	print "Please run the makefile to compile pyglet."
	print "Usage: make"
	sys.exit(0)

import re, MathCalc, GraphUtils
from pyglet.window import key, mouse
from pyglet.gl import *

# Graphs the function for the domain passed to the function
# Centers the coordinates around center point
def trace(func, domain, center, zoom):
	global camView
	graph = []

	for x in domain:
		x /= zoom[0]
		y = MathCalc.readEquation(func, (independentVar, x))
		if y != None:
			graph += (x * zoom[0] + center[0] - camView[0],
				constants.WINDH - (-(y * zoom[1]) + center[1]) + camView[1])

	return graph

def drawGraph(coords):
	print len(coords)
	pyglet.graphics.draw(len(coords) / 2, pyglet.gl.GL_LINE_STRIP,
		('v2f', coords),
		('c4f', ((1, .25, .25, 0) * (len(coords) / 2)))
	)
	

def drawAxes(center):
	center = (float(center[0]), constants.WINDH - float(center[1]))
	pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
		('v2f', (0, center[1], constants.WINDW, center[1])),
		('c4f', (0, 0, 0, 0, 0, 0, 0, 0))
	)
	

	pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
		('v2f', (center[0], constants.WINDH, center[0], 0)),
		('c4f', (0, 0, 0, 0, 0, 0, 0, 0))
	)
	

def drawText(graph):
	dim = [xrange(80), xrange(24)]

	realGraph = map(lambda p: [int(p[0] / zoom[0]),
							   int(p[1] / zoom[1])], graph)
				
	result = "\n".join(
		map(lambda row: "".join(row),
			 [map(lambda x: "*" if [x, y] in realGraph else " ", dim[0]) for y in dim[1]])
		)

	print result

def fixScale(func):
	global zoom, camView

	zoom[1] = zoom[0]
	update.needsUpdate = True

def chooseDomain(lower, upper, func):
	global zoom, camView

	boundLength = abs(upper - lower)

	zoom[0] = float(constants.WINDW) / boundLength
	camView = (lower * zoom[0] + constants.WINDW / 2, camView[1])

	update.needsUpdate = True

def chooseRange(lower, upper, func):
	global zoom, camView

	boundLength = abs(upper - lower)

	zoom[1] = float(constants.WINDH) / boundLength
	camView = (camView[0], -(upper * zoom[1] - constants.WINDH / 2))

	update.needsUpdate = True

def updateGraph(func):
	global viewGraph, axisView, zoom, camView, axisCenter

	step = float(constants.WINDW) / (constants.SIGPOINTS / 2.0)

	domain = GraphUtils.frange((-(constants.WINDW / 2.0) + camView[0]) - 1,
			(constants.WINDW / 2.0 + camView[0]) + 1, step)

	viewGraph = trace(func, domain, axisCenter, zoom)

	# Translate the graph and axis into view
	#viewGraph = translate(camView, coords)
	axisView = translate(camView, axisCenter)

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

def changeFunction(newFunc):
    global origFunc, func, needsUpdate, independentVar

    formatted = GraphUtils.formatExpression(newFunc)
    if GraphUtils.validateFunction(formatted):
        origFunc = newFunc
        if len(origFunc) == 0:
            origFunc = " "
        func = formatted
        independant = GraphUtils.findIndependent(func)
        if independant != None:
        	independentVar = independant

        needsUpdate = True

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

def update(dt, func):
	if update.upHeld:
		zoomIn(constants.QUICKZOOMCONST)
		update.needsUpdate = True      # Update the graph with the new scale
	if update.downHeld:
		zoomOut(constants.QUICKZOOMCONST)
		update.needsUpdate = True      # Update the graph with the new scale

	if update.needsUpdate:
		updateGraph(func)
		update.needsUpdate = False

def constants():
	constants.WINDW = 800
	constants.WINDH = 600
	constants.SIGPOINTS = 300
	constants.ZOOMCONST = 1.08
	constants.QUICKZOOMCONST = 1.01

def run(function=None):
	global zoom, camView, dependentVar, independentVar, axisView, viewGraph
	constants()        # define necessary constants
	zoom = [20, 20]
	camView = (0, 0)
	axisCenter = (constants.WINDW / 2, constants.WINDH / 2)
	viewGraph = []
	axisView = axisCenter
	domChangedCallbacks, rngChangedCallbacks = [] , []
	dependentVar, independentVar = "y", "x"
	boundsX = [-10, 10]

	origFunc = ""

	if function != None:
		origFunc = function[:]
	elif len(sys.argv) > 1:
		origFunc = sys.argv[1]

	changeFunction(origFunc)

	update.needsUpdate = True
	updateBounds = False

	update.upHeld = False
	update.downHeld = False

	chooseDomain(-10, 10, func)
	fixScale(func)

	update.needsUpdate = True

	window = pyglet.window.Window(resizable=True, width=constants.WINDW, height=constants.WINDH)
	pyglet.clock.schedule(update, func)

	@window.event
	def on_key_press(symbol, modifiers):
		if symbol == key.UP:
			update.upHeld = True
		if symbol == key.DOWN:
			update.downHeld = True

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

		drawAxes(axisView)

		glEnable(GL_LINE_SMOOTH)
		glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
		glLineWidth(3.0)

		drawGraph(viewGraph)

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