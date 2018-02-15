import re
import datetime

class PalParser(object):
    def __init__(self):
        # The label and branch dictionaries are separated to compare and determine valid labels at end
        # Otherwise, tracking these errors would be very difficult
        self.labelDictionary = {}
        self.branchDictionary = {}
        self.variableList = []
        self.lineCount = 1
        self.errorDictionary = {
            "ill-formed label": 0,
            "invalid opcode": 0,
            "too many operands": 0,
            "too few operands": 0,
            "ill-formed operands": 0,
            "wrong operand type": 0,
            "label problems": 0,
            "variable problems": 0
        }
        self.startToken = 0
        self.endToken = 0
        self.defToken = 0
        self.registers = ["R0", "R1", "R2", "R3", "R4", "R4", "R5", "R6", "R7"]
        self.now = datetime.datetime.now()

    def main(self, inputFileName):
        outputFileName = inputFileName.split(".")[0] + ".log"
        with open(outputFileName, "w") as logFile:
            with open(inputFileName, "r") as inputFile:
                self.printHeader(logFile, inputFileName, outputFileName)
                for line in inputFile:
                    lineData = line.split(";")[0].split("\n")[0]
                    if lineData.strip(" "):
                        logFile.write(str(self.lineCount) + ". " + lineData + "\n")
                        self.analyzeLine(lineData.replace(",", " "), logFile)
                        self.lineCount += 1
            self.printLabelData(logFile)
            self.printEndSummary(logFile)
        if inputFile.closed == False:
            inputFile.close()
        if logFile.closed == False:
            logFile.close()

    def analyzeLine(self, line, logFile):
        #Lambda form from example by Ron Kalian
        lineItems = list(filter(lambda item: item != "", line.split(" ")))
        errorMessage = ""
        if lineItems == "":
            return
        elif self.endToken > 0:
            errorMessage = "invalid opcode -- opcode cannot be present after END"
            self.errorDictionary["invalid opcode"] += 1
        elif self.startToken == 0 and not lineItems[0] == "SRT":
            errorMessage = "invalid opcode -- expected SRT"
            self.errorDictionary["invalid opcode"] += 1
        elif self.startToken == 1 and lineItems[0] == "SRT":
            errorMessage = "invalid opcode -- SRT should only occur at the start of a program"
            self.errorDictionary["invalid opcode"] += 1
        elif self.startToken == 0 and lineItems[0] == "SRT":
            self.startToken += 1
            if len(lineItems) > 1:
                errorMessage = "too many operands -- SRT should be on it's own line"
                self.errorDictionary["too many operands"] += 1
        elif self.defToken == 0 and lineItems[0] == "DEF":
            errorMessage = self.variableAddressCheck(lineItems)
        elif lineItems[0] == "END":
            self.endToken += 1
        else:
            self.defToken = 1
            if ":" in lineItems[0]:
                errorMessage = self.validLabelCheck(lineItems[0].strip(":"), "first")
                if errorMessage == "":
                    del lineItems[0]
                    errorMessage = self.opCodeCheck(lineItems)
            else:
                errorMessage = self.opCodeCheck(lineItems)
        if not (errorMessage == ""):
            logFile.write("****error: " + errorMessage + "\n")

    def printHeader(self, logFile, inputFile, outputFile):
        logFile.write("Parse of PAL Program by Parser.py\n")
        logFile.write("INPUT: " + inputFile + "\n")
        logFile.write("OUTPUT: " + outputFile + "\n")
        logFile.write("PROCESS DATE: " + str(self.now.month) + "/" + str(self.now.day) + "/" + str(self.now.year) + "\n")
        logFile.write("NAME: " + "Peter Nielson\n")
        logFile.write("CS 3210\n\n\n\n")
        logFile.write("PAL Program Listing\n")
        logFile.write("-------------------\n\n")

    def printEndSummary(self, logFile):
        logFile.write("\n\n\nSummary ----------\n\n")
        logFile.write("\n")
        logFile.write("total lines   =  " + str(self.lineCount - 1) + "\n")
        logFile.write("total errors  =  " + str(self.totalErrorCount()) + "\n")
        self.errorCounts(logFile)
        logFile.write("\n\n")
        if self.totalErrorCount() == 0:
            logFile.write("This PAL program is valid\n")
        else:
            logFile.write("This PAL program is not valid\n")

    def totalErrorCount(self):
        totalCount = 0
        for key in self.errorDictionary:
            totalCount += self.errorDictionary[key]
        return totalCount

    def errorCounts(self, logFile):
        for key in self.errorDictionary:
            if not self.errorDictionary[key] == 0:
                logFile.write("  " + str(self.errorDictionary[key]) + "   " + key + "\n")

    def printLabelData(self, logFile):
        logFile.write("\n\nLabels:\n")
        keys = []
        if self.labelDictionary or self.branchDictionary:
            for key in self.branchDictionary:
                for item in self.labelDictionary:
                    if item == key and self.labelDictionary[key] == 0:
                        logFile.write(key + " is branched to " + str(self.branchDictionary[key]))
                        logFile.write(" times and is valid\n")
                        keys.append(key)
                    elif item == key and not self.labelDictionary[key] == 0:
                        logFile.write(key + " is branched to " + str(self.branchDictionary[key]))
                        logFile.write(" times and is invalid\n")
                        keys.append(key)
            for key in keys:
                del self.labelDictionary[key]
                del self.branchDictionary[key]
            # There are separate checks here to see if there are any invalid branches that were not caught earlier
            if self.branchDictionary:
                for key in self.branchDictionary:
                    logFile.write(key + " is branched to " + str(self.branchDictionary[key]))
                    logFile.write(" times and is invalid\n")
                    logFile.write("***error: " + self.labelProblemsMessage(key, " branches to a nonexistent label\n"))
            if self.labelDictionary:
                for key in self.labelDictionary:
                    logFile.write(key + " is branched to " + str(self.labelDictionary[key]) + " times and valid\n")
                    logFile.write("***error: " + self.labelProblemsMessage(key, " is never branched to"))
        else:
            logFile.write("There are no labels in this program\n")


########################################################################################################################

    def variableAddressCheck(self, line):
        operandCount = 0
        errorMessage = ""
        for i in range(len(line)):
            if i == 1:
                errorMessage = self.validVariableCheck(line[i])
            elif i == 2:
                errorMessage =  self.validOctalCheck(line[i])
            elif i > 2:
                errorMessage = self.tooManyOperandsMessage(line[0], 2)
            if not errorMessage == "":
                return errorMessage
            operandCount += 1
        if operandCount < 3:
            errorMessage = self.tooFewOperandsMessage(line[0], 2)
        return errorMessage

    def validVariableCheck(self, variable):
        if re.match(r'^[A-Z]{1,5}$', variable) and self.defToken == 0:
            self.variableList.append(variable)
            return ""
        elif re.match(r'^[A-Z]{1,5}$', variable) and self.defToken == 1:
            for i in self.variableList:
                if i == variable:
                    return ""  # variable was found
            return self.variableProblemsMessage(variable)
        return self.illFormedOperandMessage(variable, "variable syntax; must be A-Z and between 1 and 5 characters")

    def validOctalCheck(self, num):
        if not re.match(r'^[0-7]{1,}$', num):
            return self.illFormedOperandMessage(num, "value for octal")
        return ""

    def validLabelCheck(self, label, type):
        errorMessage = ""
        if re.match(r'^[A-Z]{1,5}$', label):
            if label in self.labelDictionary == True and type == "first":
                print "a"
                errorMessage = self.labelProblemsMessage(label, "cannot branch to two locations")
            elif label not in self.labelDictionary and type == "first":
                self.labelDictionary[label] = 0
            elif type == "branch":
                if label not in self.branchDictionary:
                    self.branchDictionary[label] = 1
                else:
                    self.branchDictionary[label] += 1
        else:
            errorMessage = self.illFormedLabelMessage(label)
        return errorMessage

    def opCodeCheck(self, lineItems):
        if lineItems[0] == "DEF":
            self.errorDictionary["invalid opcode"] += 1
            return "invalid opcode -- all DEF opcodes must appear after start and before other opcodes"
        elif lineItems[0] == "ADD":
            return self.threeSourceCheck(lineItems)
        elif lineItems[0] == "SUB":
            return self.threeSourceCheck(lineItems)
        elif lineItems[0] == "MUL":
            return self.threeSourceCheck(lineItems)
        elif lineItems[0] == "DIV":
            return self.threeSourceCheck(lineItems)
        elif lineItems[0] == "INC":
            return self.oneSourceCheck(lineItems)
        elif lineItems[0] == "DEC":
            return self.oneSourceCheck(lineItems)
        elif lineItems[0] == "COPY":
            return self.twoSourceCheck(lineItems)
        elif lineItems[0] == "MOVE":
            return self.valueSourceCheck(lineItems)
        elif lineItems[0] == "BGT":
            return self.twoSourceLabelCheck(lineItems)
        elif lineItems[0] == "BEQ":
            return self.twoSourceLabelCheck(lineItems)
        elif lineItems[0] == "BR":
            return self.oneLabelCheck(lineItems)
        else:
            return self.invalidOpCodeMessage(lineItems[0])

    def validRegisterCheck(self, reg):
        for i in self.registers:
            if i == reg:
                return ""
        return self.illFormedOperandMessage(reg, "register number")

    def typeCheckSource(self, item):
        if re.match(r'^[A-Z]{1,5}$', item):
            return self.validVariableCheck(item)
        elif re.match(r'^[0-9]{1,}$', item):
            return self.wrongOperandTypeMessage(item, "variable or register", "number")
        else:
            return self.validRegisterCheck(item)

    def typeCheckValue(self, item):
        if re.match(r'^[0-9]{1,}', item):
            return self.validOctalCheck(item)
        else:
            return self.wrongOperandTypeMessage(item, "number", "variable or register")

    def typeCheckLabel(self, item):
        if re.match(r'^[A-Z]{1,5}$', item):
            return self.validLabelCheck(item, "branch")
        elif re.match(r'^[0-9]{1,}$', item):
            return self.wrongOperandTypeMessage(item, "label", "number")
        else:
            return self.wrongOperandTypeMessage(item, "label", "variable or register")

########################################################################################################################

    def threeSourceCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i == 3:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i > 3:
                return self.tooManyOperandsMessage(lineItems[0], 3)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 4:
            return self.tooFewOperandsMessage(lineItems[0], 3)
        return errorMessage

    def oneSourceCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i > 1:
                return self.tooManyOperandsMessage(lineItems[0], 1)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 2:
            return self.tooFewOperandsMessage(lineItems[0], 1)
        return errorMessage

    def twoSourceCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i > 2:
                return self.tooManyOperandsMessage(lineItems[0], 2)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 3:
            return self.tooFewOperandsMessage(lineItems[0], 2)
        return errorMessage

    def valueSourceCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckValue(lineItems[i])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i > 2:
                return self.tooManyOperandsMessage(lineItems[i], 2)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 3:
            return self.tooFewOperandsMessage(lineItems[0], 2)
        return errorMessage

    def twoSourceLabelCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i])
            elif i == 3:
                errorMessage = self.typeCheckLabel(lineItems[i])
            elif i > 3:
                return self.tooManyOperandsMessage(lineItems[0], 3)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 4:
            return self.tooFewOperandsMessage(lineItems[0], 3)
        return errorMessage

    def oneLabelCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckLabel(lineItems[i])
            elif i > 1:
                return self.tooManyOperandsMessage(lineItems[0], 1)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 2:
            return self.tooFewOperandsMessage(lineItems[0], 1)
        return errorMessage

########################################################################################################################

    def tooManyOperandsMessage(self, item, num):
        self.errorDictionary["too many operands"] += 1
        return "too many operands -- expected " + str(num) + " operands for " + item

    def tooFewOperandsMessage(self, item, num):
        self.errorDictionary["too few operands"] += 1
        return "too few operands -- expected " + str(num) + " operands for " + item

    def illFormedOperandMessage(self, item, type):
        self.errorDictionary["ill-formed operands"] += 1
        return "ill-formed operands -- " + item + " is an invalid " + type

    def variableProblemsMessage(self, item):
        self.errorDictionary["variable problems"] += 1
        return "variable problems -- " + item + " was not initialized"

    def labelProblemsMessage(self, item, type):
        self.errorDictionary["label problems"] += 1
        return "label problems -- label " + item + " " + type

    def illFormedLabelMessage(self, item):
        self.errorDictionary["ill-formed label"] += 1
        return "ill formed label -- " + item + " does not follow label syntax"

    def wrongOperandTypeMessage(self, item, expected, present):
        self.errorDictionary["wrong operand type"] += 1
        return "wrong operand type -- " + present + " where " + expected + " expected at " + item

    def invalidOpCodeMessage(self, item):
        self.errorDictionary["invalid opcode"] += 1
        return "invalid opcode -- " + item + " is not a valid opcode"



parser = PalParser()
parser.main("input.pal")