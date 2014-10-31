from Tkinter import *
import ttk
import threading
import Graphing

def createGraphThread():
    global graphThread

    graphThread = threading.Thread(target=Graphing.run)
    graphThread.daemon = True
    graphThread.start()

def startGraphing():
    if graphThread != None:
        if not graphThread.isAlive():
            createGraphThread()
    else:
        createGraphThread()

    if equation.get():
        Graphing.changeFunction(equation.get())

def equationChanged(*args):
    if graphThread != None:
        Graphing.changeFunction(equation.get())

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

buttons = [["7", "8", "9", "/"],
           ["4", "5", "6", "*"],
           ["1", "2", "3", "-"],
           ["0", ".", "C", "+"]]

trig = [["sin", "arcsin", "sinh"],
        ["cos", "arccos", "cosh"],
        ["tan", "arctan", "tanh"]]

funcs = [["ln", "log", "log10"],
         ["sqrt"]]

root = Tk()
root.minsize(600, 400)
ttk.Style().theme_use('vista')

eqFont = ("Cambria", 14)
graphThread = None

#root.bind("<Key>", lambda e: equation.focus_set())

mainFrame = ttk.Frame(root)
topFrame = ttk.Frame(mainFrame)

text = StringVar()
text.trace("w", equationChanged)

equation = ttk.Entry(topFrame, font=eqFont, textvariable=text)
equation.pack(side=LEFT, padx=4, pady=6, fill=X, expand=True)

graph = ttk.Button(topFrame, width=5, text="Graph", command=startGraphing)
graph.pack(side=RIGHT, padx=4, pady=2)

topFrame.pack(fill=X)

midFrame = ttk.Frame(mainFrame, borderwidth=4, relief=SUNKEN)

buttonFrame = ttk.Frame(midFrame)
for i in xrange(len(buttons)):
    for j in xrange(len(buttons[i])):
        ttk.Button(
            buttonFrame, width=6, text=buttons[i][j],
            command=lambda r=i, c=j: buttonClicked(buttons[r][c])
        ).grid(row=i, column=j, padx=2, pady=2)
buttonFrame.grid(row=1, column=0, padx=4)

tabs = ttk.Notebook(midFrame)

trigFrame = ttk.Frame(tabs)
funcFrame = ttk.Frame(tabs)

for i in xrange(len(trig)):
    for j in xrange(len(trig[i])):
        ttk.Button(
            trigFrame, width=6, text=trig[i][j],
            command=lambda r=i, c=j: addFunction(trig[r][c])
        ).grid(row=i, column=j)
trigFrame.pack()

for i in xrange(len(funcs)):
    for j in xrange(len(funcs[i])):
        ttk.Button(
            funcFrame, width=6, text=funcs[i][j],
            command=lambda r=i, c=j: addFunction(funcs[r][c])
        ).grid(row=i, column=j)
funcFrame.pack()

tabs.add(trigFrame, text="Trig")
tabs.add(funcFrame, text="Funcs")

tabs.grid(row=1, column=1)

midFrame.pack()

mainFrame.pack()

root.mainloop()
