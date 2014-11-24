#!/usr/bin/python
import re
from MathCalc import funcList

def frange(start, stop, step):
    vals = []
    i = start
    while i <= stop:
        vals.append(i)
        i += step
    return vals

def formatExpression(func):
    # Attempts to format multiplication in the expression properly
    # so that it may be successfully evaluated
    def fixMultiplication(func):
        result = re.sub(r"(\b(?:\-|\+)?[0-9]+(?:\.[0-9]+)?) *([A-Za-z]+)", lambda match: "%s*%s" % (match.group(1), match.group(2)), func)
        result = re.sub(r"(\)) *([\w(])", lambda match: "%s*%s" % (match.group(1), match.group(2)), result)
        result = re.sub(r"(\b(?:\-|\+)?[0-9]+(?:\.[0-9]+)?)(\()",
                    lambda match: ("%s%s" if match.group(1) in funcList else "%s*%s") % (match.group(1), match.group(2)), result)

        fixed, last = "", 0
        for match in re.finditer(r"(%s)\b" % FUNCREGEX, result):
            i = match.start()
            while i > 0 and result[i].isalnum():
                i -= 1
            if not result[i].isalnum(): i += 1

            if match.start() - i > 0:
                fixed += result[last:i] + result[i:match.start()] + "*" + result[match.start():match.end()]
            else:
                fixed += result[last:match.end()]
            last = match.end()

        fixed += result[last:]

        return fixed

    # Attempts to format exponents in the expression properly
    # so that it may be successfully evaluated
    def replaceExp(func):
        return re.sub(r"\^+", "**", func)

    # Attempts to find function calls missing opening brace
    def fixOpening(func):
        result = ""
        last = 0
        for op in re.finditer(FUNCREGEX, func):
            i = op.span()[1]

            while i < len(func) and func[i].isspace(): i += 1

            if i >= len(func): break;
            if func[i] != "(":
                result += func[last: i] + "("
                last = i
            else:
                result += func[last: op.span()[1]]
                last = op.span()[1]
        result += func[last:]

        return result if validateFunction(result) else func

    # Strip whitespace from expression
    func = func.strip()

    return replaceExp(
                fixMultiplication(
                    fixOpening(func)
                    )
                )

def nestFunctions(func, other):
    formatted = formatExpression(func)
    independant = findIndependent(removeDependant(formatted))

    result = formatted
    if independant != None:
        for i in range(len(other)):
            otherFormatted = formatExpression(other[i])
            dependant = findDependant(otherFormatted)
            if dependant not in "xXyY" and dependant in independant:
                result = re.sub(r"\b%s\b" % independant, 
                    lambda match: removeDependant(nestFunctions(other[i], other[:i] + other[i + 1:])), result)
    return result

def defineFunctions(functions):
    anyDefined = False
    for f in functions:
        if f.count("=") != 1:
            continue

        dependant = findDependant(f)
        
        if dependant == "y": continue
        match = re.search(r"([A-Za-z]\w*) *\((.+)\)", dependant)
        if match == None: continue

        if match and match.group(1) and match.group(1) not in funcList or\
            (match.group(1) in funcList and match.group(1) in userFuncMapings):
            anyDefined = True
            userFuncMapings[match.group(1)] = (map(lambda arg: arg.strip(), match.group(2).split(",")), f)

        if match.group(1) not in funcList:
            funcList.append(match.group(1))
            FUNCREGEX = r"(?i)(%s)" % "|".join(funcList)
    return anyDefined

def getArgs(f, start):
    i = start
    while i < len(f) and f[i] != "(": i += 1
    argStart = i
    open = 1
    i += 1
    while i < len(f) and open != 0:
        if f[i] == "(": open += 1
        elif f[i] == ")": open -= 1
        i += 1

    return (argStart, i)

def replaceCalls(functions):
    if len(userFuncMapings) == 0: 
        return functions

    # Subs parameters into called function
    def callIt(match, f):
        if match and match.group(1) in userFuncMapings:
            beingCalled = userFuncMapings[match.group(1)]
            argPos = getArgs(f, match.start())

            args = map(lambda arg: arg.strip(), f[argPos[0] + 1: argPos[1] - 1].split(","))
            if len(args) == len(beingCalled[0]):
                subbed = re.sub(r"(%s)" % "|".join(beingCalled[0]), 
                    lambda match: "("+args[beingCalled[0].index(match.group(1))]+")", removeDependant(beingCalled[1]))

                return (subbed, argPos)
            else:
                return None
        return (match.group(), [0, 0])

    def replaceCall(function):
        woDep = removeDependant(function)

        if re.search(mapRegex, woDep) == None:
            return function

        match = list(re.finditer(mapRegex, woDep))[-1]
        called = callIt(match, woDep)

        if called == None:
            return function

        sub, argPos = called
        result = woDep[0: match.start()] + sub + woDep[argPos[1]:]

        if function.count("=") == 1:
            prevSub = findDependant(function) + "=" + result
        else:
            prevSub = "y=" + result

        return replaceCall(prevSub)

    results = []
    mapRegex = r"(%s)" % "|".join(userFuncMapings.keys())

    for f in functions:
        results.append(replaceCall(f))

    return results

def findIndependent(func):
    varsFound = list(set(filter(lambda word: not word in funcList, re.findall("[A-Za-z]\w*", func))))

    if len(varsFound) > 0:
        return varsFound
    else:
        return None

def findDependant(func):
    if func.count("=") == 1:
        parts = func.split("=")

        return parts[0].strip()
    return "y"

# Removes dependant variable from expression if it contains
# a dependant variable
def removeDependant(func):
    if func.count("=") == 1:
        parts = func.split("=")

        return parts[1].strip()
    return func

def validateFunction(func):
    # Finds total number of unmatched brackets in the expression
    # if negative there are closing brackets missing opening brackets
    # if positive there are opening brackets missing a closing brace
    def matchBrackets(func):
        return func.count("(") - func.count(")")

    bracks = matchBrackets(func)
    if bracks != 0:
        return False
    return True

FUNCREGEX = r"(?i)(%s)" % "|".join(funcList)
userFuncMapings = {}

