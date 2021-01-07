import re
import sys
import argparse
from collections import OrderedDict 

class EqvTable:
    def __init__(self):
        self.table = OrderedDict()
        self.matchPattern = re.compile("^\.eqv (\w+) (.*)\n")
        self._replacePattern = None

    def add(self, name, value):
        self.table[name] = value
        self._replacePattern = None

    def match(self, line):
        match = self.matchPattern.fullmatch(line)
        if not match: return False
        self.add(*match.groups())
        return True

    def getReplacePattern(self):
        if self._replacePattern: return self._replacePattern
        self._replacePattern = re.compile(r"\b({})\b".format("|".join(self.table.keys())))
        return self._replacePattern

    def replace(self, line):
        if len(self.table) == 0: return line
        return self.getReplacePattern().sub(lambda m: self.table[m.group(0)], line)


class Macro:
    def __init__(self, name, parameters, lines):
        self.name = name
        self.parameters = parameters
        self.lines = lines
        self.replacePattern = self.getReplacePattern()

    def getReplacePattern(self):
        return re.compile(r"\b({})\b".format("|".join(self.parameters)))

    def evaluate(self, arguments):
        if len(arguments) == 0: return self.lines
        outputLines = []
        for line in self.lines:
            outputLines.append(self.replacePattern.sub(
                lambda m: arguments[self.parameters.index(m.group(0))], line))
        return outputLines


class MacroTable:
    def __init__(self):
        self.table = OrderedDict()
        self.matchPattern = re.compile("\.macro (\w+)\s*\(?((?:%\w+[,\s]*)*)\)?\s*\n")
        self._replacePattern = None

    def add(self, name, parameters, lines):
        self.table[name] = Macro(name, parameters, lines)
        self._replacePattern = None

    def match(self, line, inputFile, eqvTable):
        match = self.matchPattern.fullmatch(line)
        if not match: return False
        name = match.group(1)
        parameters = match.group(2).replace(",", " ").split()
        lines = []
        while True:
            line = next(inputFile)
            if line.startswith(".end_macro"): break
            line = eqvTable.replace(line)
            lines.extend(self.replace(line))
        self.add(name, parameters, lines)
        return True

    def getReplacePattern(self):
        if self._replacePattern: return self._replacePattern
        regex = r"\s*\b({})\b".format("|".join(self.table.keys()))
        regex += "\s*\(?((?:[\w$]+[,\s]*)*)\)?\s*\n"
        self._replacePattern = re.compile(regex)
        return self._replacePattern

    def replace(self, line):
        if len(self.table) == 0: return [line]
        match = self.getReplacePattern().fullmatch(line)
        if not match: return [line]
        name = match.group(1)
        arguments = match.group(2).replace(",", " ").split()
        return self.table[name].evaluate(arguments)


def preprocess(inputFile):
    outputLines = []
    eqvTable = EqvTable()
    macroTable = MacroTable()
    for line in inputFile:
        if eqvTable.match(line): continue
        if macroTable.match(line, inputFile, eqvTable): continue
        line = eqvTable.replace(line)
        outputLines.extend(macroTable.replace(line))
    return outputLines

def main():
    argumentParser = argparse.ArgumentParser()

    argumentParser.add_argument("-i", "--input", nargs = "?", type = argparse.FileType(),
            default = sys.stdin, const = sys.stdin,
            help = "The input file. Standard input if not specified.")

    argumentParser.add_argument("-o", "--output", nargs = "?", type = argparse.FileType("w"),
            default = sys.stdout, const = sys.stdout,
            help = "The output file. Standard output if not specified.")

    arguments = argumentParser.parse_args()

    lines = preprocess(arguments.input)

    arguments.output.write("".join(lines))

if __name__ == "__main__":
    main()
