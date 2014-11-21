#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Tkinter import *
import ttk, os, MathCalc, subprocess, Graphing, GraphUtils, CLineReadFile, UnitTests
from platform import system

def createGraphProcess():
    global graphProcess, fList

    # Format the expressions so they are ready to be graphed
    funcArg = [element[6].get() for element in fList]
    funcArg = [GraphUtils.formatExpression(f) for f in funcArg]
    funcArg = GraphUtils.replaceCalls(funcArg)
    funcArg = [GraphUtils.nestFunctions(e[1], funcArg[:e[0]] + funcArg[e[0] + 1:]) for e in enumerate(funcArg)]

    # Open the graphing subprocess
    graphProcess = subprocess.Popen(["python", sys.path[1] + "/Graphing.py", str(len(funcArg))] + funcArg + ["%s,%s" % (lowerX.get(), upperX.get()), "%s,%s" % (lowerY.get(), upperY.get())])
    
def startGraphing():
    if graphProcess != None:
        if graphProcess.poll() == None:
            # Terminate previous graphing process
            graphProcess.terminate()
            createGraphProcess()
        else:
            createGraphProcess()
    else:
        createGraphProcess()
    
def equationChanged(stuff, var, resultString, resultLabel, num):
    global fList

    def updateResults(rng):
        formatted = map(lambda frame: GraphUtils.formatExpression(frame[6].get()), fList[rng[0]: rng[1]])
        replaced = GraphUtils.replaceCalls(formatted)
        for i in range(len(replaced)):
            replaced[i] = GraphUtils.nestFunctions(replaced[i], replaced[:i] + replaced[i + 1:])
        for i in range(len(replaced)):
            frame = fList[i + rng[0]]
            eq = replaced[i]

            result = MathCalc.readEquation(GraphUtils.removeDependant(eq))
            resultType = type(result)
            types = [int, long, float]

            if resultType in types:
                frame[7].set("= " + str(result))
                frame[3].grid(columnspan=1000)
            else:
                frame[3].grid_forget()

    if GraphUtils.defineFunctions([var.get()] + map(lambda frame: frame[6].get(), fList)):
        updateResults([0, len(fList)])
    else:
        index = int(num.get()[:-1]) - 1
        updateResults([index, index + 1])

def numPadClicked(button):
    global lastSelected

    if lastSelected != None:
        if button in "+-*/":
            lastSelected.insert(INSERT, " %c " % button)
        else:
            lastSelected.insert(INSERT, button)
        lastSelected.focus_set()

def funcClicked(func):
    global lastSelected

    if lastSelected != None:
        lastSelected.insert(INSERT, func + "()")
        lastSelected.icursor(lastSelected.index(INSERT) - 1)
        lastSelected.focus_set()

def entryClicked(event):
    global lastSelected
    lastSelected = event.widget

def backSpaceEntry(event, fN):
    if len(event.widget.get()) == 0:
        removeFuncEntry(fN)

def addToFuncList(*args):
    global fList, funcFrame, lastSelected

    fNum = len(fList) + 1
    num = StringVar()
    
    single = ttk.Frame(funcFrame)
    fLabel = ttk.Label(single, textvariable=num)
    fLabel.grid(row=fNum, column=0, pady=2, sticky=W)
    num.set("%d." % (fNum))
    
    resultString = StringVar()
    resultLabel = Label(single, textvariable=resultString)

    eqString = StringVar()
    eqString.trace("w", lambda *args: equationChanged(args, eqString, resultString, resultLabel, num))
    fEntry = ttk.Entry(single, width=20, font=eqFont, textvariable=eqString)
    fEntry.grid(row=fNum, column=1, pady=2)

    fEntry.bind("<ButtonRelease-1>", entryClicked)
    fEntry.bind("<Return>", addToFuncList)
    fEntry.bind("<BackSpace>", lambda event: backSpaceEntry(event, fNum - 1))

    removeButton = ttk.Button(single, width=2, text="X", command=lambda: removeFuncEntry(fNum - 1))
    removeButton.grid(row=fNum, column=2, pady=2)

    resultLabel.grid_forget()

    single.pack()

    fEntry.focus_set()
    lastSelected = fEntry

    fList.append((fLabel, fEntry, removeButton, resultLabel, single, num, eqString, resultString))

def removeFuncEntry(fN):
    global fList, lastSelected

    if fN >= len(fList):
        return
    elif fN == 0:
        if fN + 1 < len(fList):
            fList[fN][6].set(fList[fN + 1][6].get())
            fN += 1
        else:
            fList[fN][6].set("")
            return

    # Remove all function widgets
    widgets = fList.pop(fN)
    for i in range(5):
        widgets[i].destroy()
    del widgets

    for i in range(len(fList)):
        fList[i][1].bind("<BackSpace>", lambda event, new=i: backSpaceEntry(event, new))
        fList[i][2].configure(command=lambda new=i: removeFuncEntry(new))
        fList[i][5].set("%d." % (i + 1))

    fList[fN - 1][1].focus_set()
    lastSelected = fList[fN - 1][1]

def validateInput(action, text):
    if action == "0" or text in "0123456789.+-" or re.match(floatPattern, text):
        return True
    return False

#def testValidateInput():  **Testing function for the validateInput method, not quite sure where re or floatPattern are defined so i left them out** 
#   action = "1"
#   text = "1"
#   boo = True
#   boo = validateInput(action, text)
#   print boo

def doGUI():
    global root, domainSet, floatPattern, graphProcess, equation, resultBox, \
        lowerX, upperX, lowerY, upperY, fList, funcFrame, eqFont, lastSelected

    buttons = [["7", "8", "9", "/"],
               ["4", "5", "6", "*"],
               ["1", "2", "3", "-"],
               ["0", ".", "=", "+"]]

    trig = [["sin", "arcsin", "sinh"],
            ["cos", "arccos", "cosh"],
            ["tan", "arctan", "tanh"]]

    funcs = [["ln", "log", "log10"],
             ["sqrt", "ceil", "floor"],
             ["abs", "min", "max"]]

    root = Tk()
    root.minsize(720, 350)
    root.wm_title("Graphing Calculator")

    # 
    floatPattern = r"(\-|\+)?[0-9]+(\.[0-9]*)?"

    s = ttk.Style()

    # Choose best theme for os being used
    if system() == "Windows":
        s.theme_use('xpnative')
    elif system() == "Darwin":
        s.theme_use('aqua')
    else:
        s.theme_use('default')

    lastSelected = None
    vcmd = (root.register(validateInput), '%d', '%S')
    fList = []

    eqFont = ("Cambria", 12)
    graphProcess = None

    leftPane = PanedWindow(root)
    leftPane.pack(fill=BOTH, expand=1)

    innerPane = PanedWindow(leftPane, orient=VERTICAL)
    innerPane.pack(fill=BOTH, expand=1)
    leftPane.add(innerPane)

    listControl = ttk.Frame(innerPane, borderwidth=4, relief=SUNKEN)
    add = ttk.Button(listControl, width=3, text="+", command=addToFuncList)
    add.pack(side=LEFT)
    graph = ttk.Button(listControl, width=5, text="Graph", command=startGraphing)
    graph.pack(side=RIGHT, padx=4, pady=2)
    listControl.pack()

    innerPane.add(listControl)

    funcFrame = ttk.Frame(innerPane)
    funcFrame.pack()
    addToFuncList()

    innerPane.add(funcFrame)

    mainFrame = ttk.Frame(leftPane, borderwidth=4, relief=SUNKEN)

    text = StringVar()
    text.trace("w", equationChanged)

    # Creating grid of digit/arithmetic operator buttons
    buttonFrame = ttk.Frame(mainFrame)
    for i in xrange(len(buttons)):
        for j in xrange(len(buttons[i])):
            ttk.Button(
                buttonFrame, width=6, text=buttons[i][j],
                command=lambda r=i, c=j: numPadClicked(buttons[r][c])
            ).grid(row=i, column=j, padx=2, pady=2)
    buttonFrame.pack(padx=4, pady=8)

    rightFrame = ttk.Frame(mainFrame)
    # Setting up notebook containing available functions
    tabs = ttk.Notebook(rightFrame)

    # Tab for trig functions
    trigFrame = ttk.Frame(tabs)
    # Tab for misc functions
    miscFrame = ttk.Frame(tabs)

    for i in xrange(len(trig)):
        for j in xrange(len(trig[i])):
            ttk.Button(
                trigFrame, width=6, text=trig[i][j],
                command=lambda r=i, c=j: funcClicked(trig[r][c])
            ).grid(row=i, column=j, padx=2, pady=2)
    trigFrame.pack()

    for i in xrange(len(funcs)):
        for j in xrange(len(funcs[i])):
            ttk.Button(
                miscFrame, width=6, text=funcs[i][j],
                command=lambda r=i, c=j: funcClicked(funcs[r][c])
            ).grid(row=i, column=j, padx=2, pady=2)
    miscFrame.pack()

    tabs.add(trigFrame, text="Trig")
    tabs.add(miscFrame, text="Misc")

    tabs.pack(side=LEFT, fill=Y, expand=1)

    xLow, xHigh = StringVar(), StringVar()
    yLow, yHigh = StringVar(), StringVar()

    xLow.set("-10")
    xHigh.set("10")
    yLow.set("-7.5")
    yHigh.set("7.5")

    restrictionFrame = ttk.Frame(rightFrame, borderwidth=4, relief=GROOVE)

    domLabel = ttk.Label(restrictionFrame, text="Domain")
    domFrame = ttk.Frame(restrictionFrame, borderwidth=4, relief=GROOVE)
    lowerX = ttk.Entry(domFrame, width=8, textvariable=xLow, validate="key", validatecommand=vcmd)
    domNotation = ttk.Label(domFrame, text="≤ x ≤")
    upperX = ttk.Entry(domFrame, width=8, textvariable=xHigh, validate="key", validatecommand=vcmd)

    rangeLabel = ttk.Label(restrictionFrame, text="Range")
    rngFrame = ttk.Frame(restrictionFrame, borderwidth=4, relief=GROOVE)
    lowerY = ttk.Entry(rngFrame, width=8, textvariable=yLow, validate="key", validatecommand=vcmd)
    rngNotation = ttk.Label(rngFrame, text="≤ y ≤")
    upperY = ttk.Entry(rngFrame, width=8, textvariable=yHigh, validate="key", validatecommand=vcmd)

    domLabel.pack()
    lowerX.pack(side=LEFT)
    domNotation.pack(side=LEFT)
    upperX.pack(side=LEFT)
    domFrame.pack(fill=Y)

    rangeLabel.pack()
    lowerY.pack(side=LEFT)
    rngNotation.pack(side=LEFT)
    upperY.pack(side=LEFT)
    rngFrame.pack(fill=Y)

    restrictionFrame.pack(side=RIGHT, fill=BOTH, expand=1)

    rightFrame.pack(fill=BOTH, expand=1)

    mainFrame.pack()
    leftPane.add(mainFrame)

    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            fileContents = CLineReadFile.readFile(sys.argv[1])
        except:
            print "File not found."
            sys.exit(0)
        expressions = CLineReadFile.parseContents(fileContents)
        results = CLineReadFile.evalExpressions(expressions)
        CLineReadFile.printResults(results)

    else: 
        doGUI()

    assert UnitTests.unitTest()
