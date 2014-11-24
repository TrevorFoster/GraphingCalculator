#!/usr/bin/python
from GraphUtils import*
from MathCalc import*
from CLineReadFile import*
import sys

#=============GraphUtils tests=============
def testFixMultipication():
    result = fixMultiplication("3(15)")
    shouldBe = "3*(15)"
    if result != shouldBe:
        print "fixMultiplication failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

def testFixOpening():
    result = fixOpening("sinx)cosx)")
    shouldBe = "sin(x)cos(x)"

    if result != shouldBe:
        print "testFixOpening failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

def testReplaceExp():
    result = replaceExp("5^3")
    shouldBe = "5**3"
    if  result != shouldBe:
        print "testReplaceExp failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

def testFormatExpression():
    result = formatExpression("y = x^2sinx)cosx)tanx)x^4")
    shouldBe = "y = x**2*sin(x)*cos(x)*tan(x)*x**4"

    if result != shouldBe:
        print "testFormatExpression failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

def testFindIndependent():
   result = findIndependent("sin(x) + cos(x)")
   shouldBe = "x"
   if  result != shouldBe:
       print "testFindIndependent failed: returned", result, "instead of the correct format of", shouldBe
       return False
   return True

def testRemoveDependant():
    result = removeDependant("y = exp(x)")
    shouldBe = "exp(x)"

    if result != shouldBe:
        print "testRemoveDependant failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True

def testValidateFunction():
    result = validateFunction("((2+3)-(3*4)")
    shouldBe = False
    if  result != shouldBe:
        print "testValidateFunction failed: returned", result, "instead of the correct format of", shouldBe
        return False
    return True
#=============End GraphUtils tests=============

#=============CLineReadFile tests=============
def testParseContents():
    if parseContents("8+7\n3*6\n\n4*2\n") != ["8+7", "3*6", "4*2"]:
        print "** testParseContents failed **"
        return False
    else:
        return True
    
def testEvalExpressions():
    if evalExpressions(["8+7", "3*6"]) != ["15", "18"]:
        print "** testEvalExpressions failed **"
        return False
    else:
        return True

def readFileTest():
    if readFile(relativePath(sys.path[0], 1, "/res/testFile.txt")) != "2+4\n2*sin(pi/2)\n1+1":
        print "**readFile failed**"
        return False
    else:
        return True
#=============End CLineReadFile tests=============

#=============MathCalc tests=============
def testReadEquation():
    equations = [("7+3",), ("8*2",), ("sqrt(100)",), ("sin(x)", ("x", 1.5707963267948966))]
    expected  = [10, 16, 10, 1]
    tests = zip(equations, expected)

    passed = True
    for test, shouldBe in tests:
        result = readEquation(*test)
        if result != shouldBe:
            print "** testReadEquation failed **", test, "should have been:",shouldBe
            passed = False
    return passed
#=============End MathCalc tests=============

def unitTest():
    tests = [testParseContents, testEvalExpressions, testFormatExpression,\
        testRemoveDependant, testValidateFunction, testReadEquation, testParseContents,\
        testEvalExpressions, readFileTest]

    totalTests, passedTests, failedTests = len(tests), 0, 0
    for test in tests:
        if test(): passedTests += 1
        else: failedTests += 1

    print "Tests run: " + str(totalTests)
    print "Tests succeeded: " + str(passedTests)
    print "Tests failed: " + str(failedTests)

    return passedTests == totalTests
