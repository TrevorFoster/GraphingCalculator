#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Tkinter import *
import ttk, os, threading, MathCalc, subprocess, NewGraphing, GraphUtils

def createGraphThread():
	global graphThread, first
	graphThread = subprocess.Popen(["python-32", sys.path[1] + "/NewGraphing.py", equation.get()])
	# graphThread = threading.Thread(target=NewGraphing.run)
	# graphThread.daemon = True
	# graphThread.start()
	
def startGraphing():
	if graphThread != None:
		if not graphThread.poll():
			createGraphThread()
	else:
		createGraphThread()
	
def equationChanged(*args):
	eq = GraphUtils.formatExpression(equation.get())
	result = MathCalc.readEquation(eq)
	resultType = type(result)

	if resultType is float or resultType is int:
		resultBox.delete(0, END)
		resultBox.insert(END, "= " + str(result))
		resultBox.pack()
	else:
		resultBox.pack_forget()

	# if graphThread != None and graphThread.isAlive():
	# 	lock.acquire()
	# 	NewGraphing.changeFunction(eq)
	# 	lock.release()

def buttonClicked(button):
	if button == "C":
		clearEquation()
	else:
		if button in "+-*/":
			equation.insert(INSERT, " %c " % button)
		else:
			equation.insert(INSERT, button)
	equation.focus_set()

def clearEquation():
	equation.delete(0, END)
	equation.focus_set()

def addFunction(func):
	equation.insert(INSERT, func + "()")
	equation.icursor(equation.index(INSERT) - 1)
	equation.focus_set()

def setDomain(domain):
	global domainSet

	lowerX.delete(0, END)
	upperX.delete(0, END)
	lowerX.insert(0, str(domain[0]))
	upperX.insert(0, str(domain[1]))
	domainSet = True

def setRange(rangee):
	lowerY.delete(0, END)
	upperY.delete(0, END)
	lowerY.insert(0, str(rangee[0]))
	upperY.insert(0, str(rangee[1]))
	rangeSet = True

def domainChanged(*args):
	global domainSet

	if graphThread != None and not domainSet:
		lock.acquire()
		lowX = lowerX.get()
		upX = upperX.get()
		lock.release()
		if re.match(floatPattern, lowX) and re.match(floatPattern, upX):
			NewGraphing.chooseDomain(float(lowX), float(upX), Graphing.func)
	domainSet = False

def rangeChanged(*args):
	global rangeSet

	if graphThread != None and not rangeSet:
		lock.acquire()
		lowY = lowerY.get()
		upY = upperY.get()
		
		if re.match(floatPattern, lowY) and re.match(floatPattern, upY):
			NewGraphing.chooseRange(float(lowY), float(upY), Graphing.func)
		lock.release()
	rangeSet = False

def validateInput(action, text):
	if action == "0" or text in "0123456789.+-" or re.match(floatPattern, text):
		return True
	return False

def doGUI():
	global domainSet, floatPattern, graphThread, equation, resultBox, lowerX, upperX, lowerY, upperY, lock

	lock = threading.Lock()

	buttons = [["7", "8", "9", "/"],
			   ["4", "5", "6", "*"],
			   ["1", "2", "3", "-"],
			   ["0", ".", "C", "+"]]

	trig = [["sin", "arcsin", "sinh"],
			["cos", "arccos", "cosh"],
			["tan", "arctan", "tanh"]]

	funcs = [["ln", "log", "log10"],
			 ["sqrt", "ceil", "floor"],
			 ["abs", "min", "max"]]

	root = Tk()
	root.minsize(600, 350)
	s = ttk.Style()
	print s.theme_names()
	s.theme_use('aqua')

	floatPattern = r"(\-|\+)?[0-9]+(\.[0-9]*)?"
	first = True
	domainSet = False
	rangeSet = False
	vcmd = (root.register(validateInput), '%d', '%S')

	eqFont = ("Cambria", 14)
	graphThread = None

	mainFrame = ttk.Frame(root, borderwidth=4, relief=SUNKEN)
	topFrame = ttk.Frame(mainFrame)

	text = StringVar()
	text.trace("w", equationChanged)

	equation = ttk.Entry(topFrame, font=eqFont, textvariable=text)
	equation.pack(side=LEFT, padx=4, pady=6, fill=X, expand=True)

	graph = ttk.Button(topFrame, width=5, text="Graph", command=startGraphing)
	graph.pack(side=RIGHT, padx=4, pady=2)

	topFrame.pack(fill=X)

	resultFrame = ttk.Frame(mainFrame)

	resultBox = ttk.Entry(resultFrame)
	resultBox.pack_forget()

	resultFrame.pack()

	midFrame = ttk.Frame(mainFrame)

	# Creating grid of digit/arithmetic operator buttons
	buttonFrame = ttk.Frame(midFrame)
	for i in xrange(len(buttons)):
		for j in xrange(len(buttons[i])):
			ttk.Button(
				buttonFrame, width=6, text=buttons[i][j],
				command=lambda r=i, c=j: buttonClicked(buttons[r][c])
			).grid(row=i, column=j, padx=2, pady=2)
	buttonFrame.pack(side=LEFT, padx=4)

	# Setting up notebook containing available functions
	tabs = ttk.Notebook(midFrame)

	# Tab for trig functions
	trigFrame = ttk.Frame(tabs)
	# Tab for misc functions
	miscFrame = ttk.Frame(tabs)

	for i in xrange(len(trig)):
		for j in xrange(len(trig[i])):
			ttk.Button(
				trigFrame, width=6, text=trig[i][j],
				command=lambda r=i, c=j: addFunction(trig[r][c])
			).grid(row=i, column=j, padx=2, pady=2)
	trigFrame.pack()

	for i in xrange(len(funcs)):
		for j in xrange(len(funcs[i])):
			ttk.Button(
				miscFrame, width=6, text=funcs[i][j],
				command=lambda r=i, c=j: addFunction(funcs[r][c])
			).grid(row=i, column=j, padx=2, pady=2)
	miscFrame.pack()

	tabs.add(trigFrame, text="Trig")
	tabs.add(miscFrame, text="Funcs")

	tabs.pack(side=RIGHT)
	midFrame.pack()

	xLow = StringVar()
	xLow.trace("w", domainChanged)
	xHigh = StringVar()
	xHigh.trace("w", domainChanged)

	yLow = StringVar()
	yLow.trace("w", rangeChanged)
	yHigh = StringVar()
	yHigh.trace("w", rangeChanged)

	xLow.set("-10")
	xHigh.set("10")
	yLow.set("-7.5")
	yHigh.set("7.5")

	restrictionFrame = ttk.Frame(mainFrame)

	lowerX = ttk.Entry(restrictionFrame, width=8, textvariable=xLow, validate="key", validatecommand=vcmd)
	domNotation = ttk.Label(restrictionFrame, text="≤ x ≤")
	upperX = ttk.Entry(restrictionFrame, width=8, textvariable=xHigh, validate="key", validatecommand=vcmd)

	lowerY = ttk.Entry(restrictionFrame, width=8, textvariable=yLow, validate="key", validatecommand=vcmd)
	rngNotation = ttk.Label(restrictionFrame, text="≤ y ≤")
	upperY = ttk.Entry(restrictionFrame, width=8, textvariable=yHigh, validate="key", validatecommand=vcmd)

	lowerX.grid(row=0, column=1)
	domNotation.grid(row=0, column=2)
	upperX.grid(row=0, column=3)

	lowerY.grid(row=1, column=1)
	rngNotation.grid(row=1, column=2)
	upperY.grid(row=1, column=3)

	restrictionFrame.pack(fill=X, expand=True)
	mainFrame.pack()

	root.mainloop()

if __name__ == "__main__":
	if len(sys.argv) > 1:
		try:
			fileContents = CLineReadFile.readFile(sys.argv[1])
			expressions = CLineReadFile.parseContents(fileContents)
			results = CLineReadFile.evalExpressions(expressions)
			CLineReadFile.printResults(results)
		except (Exception):
			print "File not found"
	else: 
		doGUI()

