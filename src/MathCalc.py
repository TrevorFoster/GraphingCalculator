#!/usr/bin/python
from __future__ import division
import math

from math import acos, asin, atan, atan2, ceil, cos, cosh,\
    degrees, e, exp, fabs, floor, fmod, frexp,\
    hypot, ldexp, log, log10, modf, pi, pow,\
    radians, sin, sinh, sqrt, tan, tanh

def readEquation(func, var=None):
    if var != None:
        bindings[var[0]] = var[1]

    try:
        y = eval(func, {"__builtins__": None}, bindings)
        if var != None: 
            del bindings[var[0]]
        return y
    except Exception as e:
        if var != None:
            del bindings[var[0]]
        return None

contents = ""
try:
    import sys
    from CLineReadFile import relativePath
    with open(relativePath(sys.path[0], 1, "/res/FunctionList.dat"), "r") as fileHandle:
        contents = fileHandle.read()
except Exception:
    print "File not found"

bindings = dict([(b[0], locals().get(b[1], None)) \
    for b in sorted(map(lambda line: line.split(":"), contents.split("\n")), key=lambda b: b[0])])

def testReadEquation():
    if readEquation("7+3") != 10:
        print "** testSafeEval failed **"
        return False
    else:
        return True

def testReadEquation2():
    if readEquation("8(+") != None:
        print "** testReadEquation2 failed **"
        return False
    else:
        return True

assert testReadEquation()
assert testReadEquation2()