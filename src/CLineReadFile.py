#!/usr/bin/python

def relativePath(curr, up, new):
    from os import path, pardir
    return path.abspath(path.join(curr, (pardir + "/") * up)) + new

def readFile(fileName):
    # Open and read file contents
    with open(fileName, "r") as fileHandle:
        contents = fileHandle.read()

    # Return file's contents
    return contents

def parseContents(fileContents):
    from GraphUtils import formatExpression

    parsed = map(lambda line: formatExpression(line),
        filter(lambda line: line, fileContents.splitlines())
        )
    return parsed

def evalExpressions(expressions):
    from MathCalc import readEquation

    # Evaluate each expression in expressions
    results = map(lambda result: "Expression invalid." if result == None else str(result),
        map(lambda exp: readEquation(exp), expressions)
    )

    # Return results
    return results

def printResults(results):
    for result in results:
        print str(result)
        
