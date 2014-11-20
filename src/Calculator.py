#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Tkinter import *
import ttk, os, MathCalc, subprocess, Graphing, GraphUtils, CLineReadFile
from platform import system

def createGraphThread():
    global graphThread, first, fList

    funcArg = [element[6].get() for element in fList]
    funcArg = GraphUtils.replaceCalls(funcArg)
    funcArg = [GraphUtils.formatExpression(f) for f in funcArg]
    funcArg = [GraphUtils.nestFunctions(e[1], funcArg[:e[0]] + funcArg[e[0] + 1:]) for e in enumerate(funcArg)]
    
    graphThread = subprocess.Popen(["python-32", sys.path[1] + "/Graphing.py", str(len(funcArg))] + funcArg + ["%s,%s" % (lowerX.get(), upperX.get()), "%s,%s" % (lowerY.get(), upperY.get())])
    
def startGraphing():
    if graphThread != None:
        if not graphThread.poll():
            createGraphThread()
    else:
        createGraphThread()
    
def equationChanged(stuff, var, resultString, resultLabel, num):
    global fList

    def updateResults(rng):
        replaced = GraphUtils.replaceCalls(map(lambda frame: frame[6].get(), fList[rng[0]: rng[1]]))
        for i in range(len(replaced)):
            replaced[i] = GraphUtils.nestFunctions(replaced[i], replaced[:i] + replaced[i + 1:])
        for i in range(len(replaced)):
            frame = fList[i + rng[0]]
            eq = replaced[i]
            eq = GraphUtils.formatExpression(eq)
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

def buttonClicked(button):
    global lastSelected

    if lastSelected != None:
        if button in "+-*/":
            lastSelected.insert(INSERT, " %c " % button)
        else:
            lastSelected.insert(INSERT, button)
        lastSelected.focus_set()

def addFunction(func):
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
        removeFunc(fN)

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

    removeButton = ttk.Button(single, width=2, text="X", command=lambda: removeFunc(fNum - 1))
    removeButton.grid(row=fNum, column=2, pady=2)

    resultLabel.grid_forget()

    single.pack()

    fEntry.focus_set()
    lastSelected = fEntry

    fList.append((fLabel, fEntry, removeButton, resultLabel, single, num, eqString, resultString))

def removeFunc(fN):
    global fList, lastSelected

    if fN >= len(fList):
        return
    elif fN == 0:
        # Clear first entry
        fList[fN][6].set("")
        return

    # Remove all function widgets
    widgets = fList.pop(fN)
    for i in range(5):
        widgets[i].destroy()
    del widgets

    for i in range(len(fList)):
        fList[i][1].bind("<BackSpace>", lambda event, new=i: backSpaceEntry(event, new))
        fList[i][2].configure(command=lambda new=i: removeFunc(new))
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
    global root, domainSet, floatPattern, graphThread, equation, resultBox, \
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

    s = ttk.Style()

    if system() == "Windows":
        s.theme_use('xpnative')
    elif system() == "Darwin":
        s.theme_use('aqua')
    else:
        s.theme_use('default')

    floatPattern = r"(\-|\+)?[0-9]+(\.[0-9]*)?"

    lastSelected = None
    vcmd = (root.register(validateInput), '%d', '%S')
    fList = []

    eqFont = ("Cambria", 12)
    graphThread = None

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

    #equation = ttk.Entry(topFrame, font=eqFont, textvariable=text)
    #equation.pack(side=LEFT, padx=4, pady=6, fill=X, expand=True)

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
    tabs.add(miscFrame, text="Misc")

    tabs.pack(side=RIGHT, fill=Y, expand=True)
    midFrame.pack(fill=BOTH, expand=True)

    xLow, xHigh = StringVar(), StringVar()
    yLow, yHigh = StringVar(), StringVar()

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

    restrictionFrame.pack(fill=BOTH, expand=True)

    mainFrame.pack(side=LEFT)
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

