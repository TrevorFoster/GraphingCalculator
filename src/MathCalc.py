#!/usr/bin/python
from __future__ import division
import math
from math import acos, asin, atan, atan2, ceil, cos, cosh,\
    degrees, e, exp, fabs, floor, fmod, frexp,\
    hypot, ldexp, log, log10, modf, pi, pow,\
    radians, sin, sinh, sqrt, tan, tanh

def readEquation(func, var=None):
    e = math.e
    safe = {"abs": abs, "acos": acos, "asin": asin, "atan": atan, "atan2": atan2, "ceil": ceil, "cos": cos,
            "cosh": cosh, "degrees": degrees, "e": e, "exp": exp, "fabs": fabs, "floor": floor,
            "fmod": fmod, "frexp": frexp, "hypot": hypot, "ldexp": ldexp, "log": log, "log10": log10,
            "min": min, "max": max, "modf": modf, "pi": pi, "pow": pow, "radians": radians, "sin": sin,
            "sinh": sinh, "sqrt": sqrt, "tan": tan, "tanh": tanh}

    if var != None:
        safe[var[0]] = var[1]

    try:
        y = eval(func, {"__builtins__": None}, safe)
        return y
    except Exception as e:
        return None


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