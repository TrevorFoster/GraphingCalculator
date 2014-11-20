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
        result = re.sub(r"(\b[0-9]+(?:\.[0-9]+)?) *([A-Za-z]+)", lambda match: "%s*%s" % (match.group(1), match.group(2)), func)
        result = re.sub(r"(\) *)([\w(])", lambda match: "%s*%s" % (match.group(1), match.group(2)), result)
        result = re.sub(r"((?:\b[0-9]+(?:\.[0-9]+)?)|(?:[A-Za-z]\w*))(\()",
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
        
    def testFixMultipication():
        result = fixMultiplication("3(15)")
        shouldBe = "3*(15)"
        if result != shouldBe:
            print "fixMultiplication failed: returned", result, "instead of the correct format of", shouldBe
            return False
        return True

    # Attempts to format exponents in the expression properly
    # so that it may be successfully evaluated
    def replaceExp(func):
        return re.sub(r"\^+", "**", func)
    
    def testReplaceExp():
        result = replaceExp("5^3")
        shouldBe = "5**3"
        if  result != shouldBe:
            print "testReplaceExp failed: returned", result, "instead of the correct format of", shouldBe
            return False
        return True

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

    def testFixOpening():
        result = fixOpening("sinx)cosx)")
        shouldBe = "sin(x)cos(x)"

        if result != shouldBe:
            print "testFixOpening failed: returned", result, "instead of the correct format of", shouldBe
            return False
        return True

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
    for f in functions:
        dependant = findDependant(f)
        match = re.search(r"([A-Za-z]\w*) *\((.+)\)", dependant)
        if match and match.group(1) not in funcList:
            userFuncMapings[match.group(1)] = (map(lambda arg: arg.strip(), match.group(2).split(",")), f)
            funcList.append(match.group(1))

def getArgs(f, start):
    i = start
    while i < len(f) and f[i] != "(": i += 1
    argStart = i
    open = 1
    i += 1
    while i < len(f) and open != 0:
        if f[i] == "(":
            open += 1
        elif f[i] == ")":
            open -= 1
        i += 1

    return (argStart, i)

def replaceCalls(functions):
    def callIt(match, f):
        if match and match.group(1) in userFuncMapings:
            beingCalled = userFuncMapings[match.group(1)]
            argPos = getArgs(f, match.start())
            args = map(lambda arg: arg.strip(), f[argPos[0] + 1: argPos[1] - 1].split(","))
            if len(args) == len(beingCalled[0]):
                subbed = re.sub(r"(%s)" % "|".join(beingCalled[0]), 
                    lambda match: args[beingCalled[0].index(match.group(1))], removeDependant(beingCalled[1]))

                return subbed
        return match.group()

    for f in functions:
        print removeDependant(f)
        result = re.sub(r"(%s)" % "|".join(userFuncMapings.keys()), lambda match, i=f: callIt(match, f), removeDependant(f))
        print result


def testFormatExpression():
    result = formatExpression("y = x^2sinx)cosx)tanx)x^4")
    shouldBe = "x**2*sin(x)*cos(x)*tan(x)*x**4"

    if result != shouldBe:
        print "testFormatExpression failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

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

def testRemoveDependant():
    result = removeDependant("y = exp(x)")
    shouldBe = "exp(x)"

    if result != shouldBe:
        print "testRemoveDependant failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

#def testFindIndependent():
#    result = findIndependent("sin(x) + cos(x)")
#    shouldBe = "x"
#    if  result != shouldBe:
#        print "testFindIndependent failed: returned", result, "instead of the correct format of", shouldBe
#        return False
#    return True

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

def testValidateFunction():
    result = validateFunction("((2+3)-(3*4)")
    shouldBe = False
    if  result != shouldBe:
        print "testValidateFunction failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

FUNCREGEX = r"(?i)(%s)" % "|".join(funcList)
userFuncMapings = {}
defineFunctions(["a(x1, x2) = 3sin(x1) + 2cos(x2)"])
replaceCalls(["a(sin(x), cos(x)) - a(2, 4)"])
