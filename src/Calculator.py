#!/usr/bin/python
# -*- coding: UTF-8 -*-
from Tkinter import *
import ttk, os, MathCalc, subprocess, Graphing, GraphUtils, CLineReadFile, UnitTests
from platform import system

# Start the graphing process  
def createGraphProcess(functions, domain, gRange):
    # Format the expressions so they are ready to be graphed
    funcArg = [GraphUtils.formatExpression(f) for f in functions]
    funcArg = GraphUtils.replaceCalls(funcArg)
    funcArg = [GraphUtils.nestFunctions(e[1], funcArg[:e[0]] + funcArg[e[0] + 1:]) for e in enumerate(funcArg)]

    # Open the graphing subprocess
    return subprocess.Popen(["python", sys.path[1] + "/Graphing.py", str(len(funcArg))] + funcArg + [domain,gRange])

# Manage the graphing process creation
def startGraphing():
    global graphProcess, fList

    funcArg = [element[6].get() for element in fList]
    domain, gRange = "%s,%s" % (lowerX.get(), upperX.get()), "%s,%s" % (lowerY.get(), upperY.get())

    if graphProcess != None:
        if graphProcess.poll() == None:
            # Terminate previous graphing process
            graphProcess.terminate()
            graphProcess = createGraphProcess(funcArg, domain, gRange)
        else:
            graphProcess = createGraphProcess(funcArg, domain, gRange)
    else:
        graphProcess = createGraphProcess(funcArg, domain, gRange)

# Callback for when a entry box has been changed   
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

            # Calculate the result of the entered equation
            result = MathCalc.readEquation(GraphUtils.removeDependant(eq))
            resultType = type(result)
            types = [int, long, float]

            # Display the result of calculation below the text box
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

# Add num that was clicked to last selected entry
def numPadClicked(button):
    global lastSelected

    if lastSelected != None:
        if button in "+-*/":
            lastSelected.insert(INSERT, " %c " % button)
        else:
            lastSelected.insert(INSERT, button)
        lastSelected.focus_set()

# Add correct function to last selected entry
def funcClicked(func):
    global lastSelected

    if lastSelected != None:
        if func not in ("pi", "e"):
            lastSelected.insert(INSERT, func + "()")
            lastSelected.icursor(lastSelected.index(INSERT) - 1)
        else:
            lastSelected.insert(INSERT, func)
            lastSelected.icursor(lastSelected.index(INSERT))
        
        lastSelected.focus_set()

# Update the last selected entry when one is clicked
def entryClicked(event):
    global lastSelected
    lastSelected = event.widget

# Event handler for backspace in function entry
def backSpaceEntry(event, fN):
    if len(event.widget.get()) == 0:
        removeFuncEntry(fN)

def addToFuncList(*args):
    global fList, funcFrame, lastSelected

    fNum = len(fList) + 1
    num = StringVar()
    
    single = ttk.Frame(funcFrame)

    # Create leading label
    fLabel = ttk.Label(single, textvariable=num)
    fLabel.grid(row=fNum, column=0, pady=2, sticky=W)
    num.set("%d." % (fNum))
    
    resultString = StringVar()
    resultLabel = Label(single, textvariable=resultString)

    # Create function entry text box
    eqString = StringVar()
    eqString.trace("w", lambda *args: equationChanged(args, eqString, resultString, resultLabel, num))
    fEntry = ttk.Entry(single, width=20, font=eqFont, textvariable=eqString)
    fEntry.grid(row=fNum, column=1, pady=2)

    fEntry.bind("<ButtonRelease-1>", entryClicked)
    fEntry.bind("<Return>", addToFuncList)
    fEntry.bind("<BackSpace>", lambda event: backSpaceEntry(event, fNum - 1))

    # Create the remove text box button
    removeButton = ttk.Button(single, width=2, text="⨉", command=lambda: removeFuncEntry(fNum - 1))
    removeButton.grid(row=fNum, column=2, pady=2)

    resultLabel.grid_forget()

    single.pack()

    fEntry.focus_set()
    lastSelected = fEntry

    # Add the new function entry to fList
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

# Event handler to evaluate new input to domain
# and range entry boxes.
def validateInput(action, text):
    if action == "0" or text in "0123456789.+-" or re.match(floatPattern, text):
        return True
    return False

def doGUI():
    global root, domainSet, floatPattern, graphProcess, equation, resultBox, \
        lowerX, upperX, lowerY, upperY, fList, funcFrame, eqFont, lastSelected

    buttons = [["7", "8", "9", "÷"],
               ["4", "5", "6", "⨯"],
               ["1", "2", "3", "-"],
               ["0", ".", "=", "+"]]

    # Characters that are added instead of face char
    charMap = [["7", "8", "9", "/"],
               ["4", "5", "6", "*"],
               ["1", "2", "3", "-"],
               ["0", ".", "=", "+"]]

    # Faces for trig buttons
    trig = [["sin", "arcsin", "sinh"],
            ["cos", "arccos", "cosh"],
            ["tan", "arctan", "tanh"],
            ["pi"]]

    # Faces for misc buttons
    funcs = [["ln", "log", "log10"],
             ["sqrt", "ceil", "floor"],
             ["abs", "min", "max"],
             ["e"]]

    root = Tk()
    root.minsize(720, 350)
    root.wm_title("Graphing Calculator")

    # Pattern to match floats
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
                command=lambda r=i, c=j: numPadClicked(charMap[r][c])
            ).grid(row=i, column=j, padx=2, pady=2)
    buttonFrame.pack(padx=4, pady=8)

    rightFrame = ttk.Frame(mainFrame)
    # Setting up notebook containing available functions
    tabs = ttk.Notebook(rightFrame)

    # Tab for trig functions
    trigFrame = ttk.Frame(tabs)
    # Tab for misc functions
    miscFrame = ttk.Frame(tabs)

    # Layout for trig tab
    for i in xrange(len(trig)):
        for j in xrange(len(trig[i])):
            ttk.Button(
                trigFrame, width=6, text=trig[i][j],
                command=lambda r=i, c=j: funcClicked(trig[r][c])
            ).grid(row=i, column=j, padx=2, pady=2)
    trigFrame.pack()

    # Layout for misc tab
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

    # Give some initial values to domain and range
    xLow.set("-10")
    xHigh.set("10")
    yLow.set("-7.5")
    yHigh.set("7.5")

    restrictionFrame = ttk.Frame(rightFrame, borderwidth=4, relief=GROOVE)

    # Layout for domain entry
    domLabel = ttk.Label(restrictionFrame, text="Domain")
    domFrame = ttk.Frame(restrictionFrame, borderwidth=4, relief=GROOVE)
    lowerX = ttk.Entry(domFrame, width=8, textvariable=xLow, validate="key", validatecommand=vcmd)
    domNotation = ttk.Label(domFrame, text="≤ x ≤")
    upperX = ttk.Entry(domFrame, width=8, textvariable=xHigh, validate="key", validatecommand=vcmd)

    # Layout for range entry
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

# Display interactable text interface
def textInterface():
    # Get user input for expression
    def inputExpression():
        while 1:
            while 1:
                print "\nPlease enter expression to evaluate [OR] q to return to the main menu"
                expression = raw_input(">> ").strip()
                if not expression:
                    continue
                break

            if expression.lower() == "q":
                return None

            formatted = GraphUtils.formatExpression(expression)
            if not GraphUtils.validateFunction(formatted):
                print "The expression entered has unmatched brackets.\nPlease try again.\n"
                continue
            return expression

    # Menu options
    options = ["Evaluate an expression", "Set domain and range", "View a function in text",
                "View a function in the graph window", "Perform calculations from a text file",
                "Exit the program"]
    
    domain, rnge = [-10, 10], [-7.5, 7.5]
    
    # Pattern to match floats
    floatPattern = r"(\-|\+)?[0-9]+(\.[0-9]*)?"

    currentDom, currentRange = "%s,%s" % (str(domain[0]), str(domain[1])), "%s,%s" % (str(rnge[0]), str(rnge[1]))
    graphProcess = None
    running = True
    while running:
        # Display options to the user
        print "What would you like to do?"
        for i, option in enumerate(options):
            print "  %d. %s" % (i + 1, option)

        choice = raw_input(">> ").strip()
        if choice == "1":
            expression = inputExpression()
            if expression == None:
                continue
            formatted = GraphUtils.formatExpression(expression)
            result = MathCalc.readEquation(formatted)
            if result == None:
                print "\nSorry the expression was not evaluated successfully.\n"
            else:
                print "\nResult: %s\n" % str(result)

        elif choice == "2":
            # Display the current domain and range to user
            print "\nCurrent domain and range:"
            print "%s <= x <= %s  %s <= y <= %s\n" % (str(domain[0]), str(domain[1]), str(rnge[0]), str(rnge[1]))

            # Domain entry
            while 1:
                print "Please input the domain [OR] nothing to not alter it"
                print "Format: 'lowerX,upperX'"
                inp = raw_input(">> ").strip()
                if not inp: break

                # Match the user entered domain
                match = re.search(r"(%s) *\, *(%s)" % (floatPattern, floatPattern), inp)
                if match == None:
                    print "Invalid input please try again.\n"
                    continue

                domain = map(lambda s: float(s.strip()), match.group().split(","))
                currentDom = "%s,%s" % (str(domain[0]), str(domain[1]))
                break
            print

            # Range entry
            while 1:
                print "Please input the range [OR] nothing to not alter it"
                print "Format: 'lowerY,upperY'"
                inp = raw_input(">> ").strip()
                if not inp: break

                # Match the user entered range
                match = re.search(r"(%s) *\, *(%s)" % (floatPattern, floatPattern), inp)
                if match == None:
                    print "Invalid input please try again.\n"
                    continue
                    
                rnge = map(lambda s: float(s.strip()), match.group().split(","))
                currentRange = "%s,%s" % (str(rnge[0]), str(rnge[1]))
                break
            print

        elif choice == "3":
            expression = inputExpression()
            if not expression:
                continue
            
            # Format the entered expression and draw the text graph
            expression = GraphUtils.formatExpression(expression)
            Graphing.commandLineDraw(expression, domain, rnge)

        elif choice == "4":
            expression = inputExpression()
            if expression == None:
                continue

            if graphProcess != None:
                if graphProcess.poll() == None:
                    # Terminate previous graphing process
                    graphProcess.terminate()
                    graphProcess = createGraphProcess([expression], currentDom, currentRange)
                else:
                    graphProcess = createGraphProcess([expression], currentDom, currentRange)
            else:
                graphProcess = createGraphProcess([expression], currentDom, currentRange)
            print
        elif choice == "5":
            print
            while 1:
                print "Please input the path to the file [OR] q to return to the main menu"
                inp = raw_input(">> ")
                if inp.lower() == "q":
                    break
                try:
                    fileContents = CLineReadFile.readFile(inp)
                except:
                    print "Sorry", inp, "cannot be found or opened.\n"
                    continue
                expressions = CLineReadFile.parseContents(fileContents)
                results = CLineReadFile.evalExpressions(expressions)

                # Display results
                print "============Results============"
                CLineReadFile.printResults(results)
                break
            print

        elif choice == "6":
            print "Goodbye!"
            running = False

if __name__ == "__main__":
    args = len(sys.argv)
    if args > 1:
        option = sys.argv[1].lower()
        if option == "cmd":                     # Start text interface
            textInterface()
        elif args == 3 and option == "file":    # Evaluate expressions in file
            try:
                fileContents = CLineReadFile.readFile(sys.argv[2])
            except:
                print "File not found."
                sys.exit(0)
            expressions = CLineReadFile.parseContents(fileContents)
            results = CLineReadFile.evalExpressions(expressions)
            CLineReadFile.printResults(results)
    else:                                       # Start graphical user interface
        doGUI()

    # Run unit tests
    assert UnitTests.unitTest()
