import re
from MathCalc import bindings

def frange(start, stop, step):
	vals = []
	i = start
	while i <= stop:
		vals.append(i)
		i += step
	return vals

def formatExpression(func):
	global dependentVar

	# Attempts to format multiplication in the expression properly
	# so that it may be successfully evaluated
	def fixMultiplication(func):
		result = re.sub(r"(\b[0-9]+(?:\.[0-9]+)?) *([A-Za-z]+)", lambda match: "%s*%s" % (match.group(1), match.group(2)), func)
		result = re.sub(r"\) *[\w(]", lambda match: "%s*%s"  % (match.group()[0], match.group()[1:]), result)
		result = re.sub(r"([A-Za-z]+)(%s)" % FUNCREGEX, lambda match: "%s*%s" % (match.group(1), match.group(2)), result)
		print result
		return result

	# Attempts to format exponents in the expression properly
	# so that it may be successfully evaluated
	def replaceExp(func):
		return re.sub(r"\^+", "**", func)

	# Removes dependant variable from expression if it contains
	# a dependant variable
	def removeDependant(func):
		if func.count("=") == 1:
			parts = func.split("=")

			return parts[1].strip()
		return func

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

	func = func.strip()

	return fixOpening(
		removeDependant(
			replaceExp(
					fixMultiplication(func)
				)
			)
		)

def findIndependent(func):
	varsFound = list(set(filter(lambda word: not word in funcList, re.findall("[A-Za-z]\w*", func))))

	if len(varsFound) == 1:
		return varsFound[0]
	else:
		return None

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

funcList = sorted(bindings.keys())
FUNCREGEX = r"(?i)%s" % "|".join(funcList)
