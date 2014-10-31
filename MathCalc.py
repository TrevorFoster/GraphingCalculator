from __future__ import division
import math
from math import acos, asin, atan, atan2, ceil, cos, cosh,\
    degrees, e, exp, fabs, floor, fmod, frexp,\
    hypot, ldexp, log, log10, modf, pi, pow,\
    radians, sin, sinh, sqrt, tan, tanh

def safeEval(func, x=None):
    e = math.e
    safe = {"acos": acos, "asin": asin, "atan": atan, "atan2": atan2, "ceil": ceil, "cos": cos,
            "cosh": cosh, "degrees": degrees, "e": e, "exp": exp, "fabs": fabs, "floor": floor,
            "fmod": fmod, "frexp": frexp, "hypot": hypot, "ldexp": ldexp, "log": log, "log10": log10,
            "modf": modf, "pi": pi, "pow": pow, "radians": radians, "sin": sin, "sinh": sinh,
            "sqrt": sqrt, "tan": tan, "tanh": tanh}

    if x != None:
        safe["x"] = x

    try:
        y = eval(func, {"__builtins__": None}, safe)
        return y
    except Exception as e:
        return None
