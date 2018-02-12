import re

class PalParser(object):
    def __init__(self):
        self.labelDictionary = {}
        self.variableList = []
        self.lineCount = 1
        self.illFormedLabel = 0
        self.variableProblems = 0
        self.invalidOpcode = 0
        self.tooManyOperands = 0
        self.tooFewOperands = 0
        self.illFormedOperands = 0
        self.wrongOperandType = 0
        self.labelProblems = 0
        self.startToken = 0
        self.defToken = 0
        self.registers = ["R0", "R1", "R2", "R3", "R4", "R4", "R5", "R6", "R7"]

    def main(self, inputFileName):
        outputFileName = inputFileName.split(".")[0] + ".log"
        with open(outputFileName, "w") as logFile:
            with open(inputFileName, "r") as inputFile:
                for line in inputFile:
                    lineData = line.split(";")[0].split("\n")[0]
                    if lineData.strip(" "):
                        logFile.write(str(self.lineCount) + ". " + lineData + "\n")
                        self.analyzeLine(lineData, logFile)
                        self.lineCount += 1
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
        elif self.startToken == 0 and not lineItems[0] == "SRT":
            errorMessage = "invalid opcode -- expected SRT"
            self.invalidOpcode += 1
        elif self.startToken == 1 and lineItems[0] == "SRT":
            errorMessage = "invalid opcode -- SRT should only occur at the start of a program"
            self.invalidOpcode += 1
        elif self.startToken == 0 and lineItems[0] == "SRT":
            self.startToken += 1
            if len(lineItems) > 1:
                errorMessage = "too many operands -- SRT should be on it's own line"
                self.tooManyOperands += 1
        elif self.defToken == 0 and lineItems[0] == "DEF":
            errorMessage = self.variableAddressCheck(lineItems)
        else:
            self.defToken = 1
            if ":" in lineItems[0]:
                errorMessage = self.validLabelCheck(lineItems[0].strip(":"))
                if errorMessage == "":
                    del lineItems[0]
                    errorMessage = self.opCodeCheck(lineItems)
            else:
                errorMessage = self.opCodeCheck(lineItems)
        if not (errorMessage == ""):
            logFile.write("****error: " + errorMessage + "\n")

########################################################################################################################

    def variableAddressCheck(self, line):
        operandCount = 0
        errorMessage = ""
        for i in range(len(line)):
            if i == 1:
                errorMessage = self.validVariableCheck(line[i].strip(","))
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
        elif re.match(r'^[A-Z]{1,5}$', variable) and defToken == 1:
            for i in self.variableList:
                if i == variable:
                    return ""  # variable was found
            return self.variableProblemsMessage(variable)
        return self.illFormedOperandMessage(variable, "variable syntax; must be A-Z and between 1 and 5 characters")

    def validOctalCheck(self, num):
        if not re.match(r'^[0-7]{1,}$', num):
            return self.illFormedOperandMessage(num, "value for octal")
        return ""

    def validLabelCheck(self, label):
        if re.match(r'^[A-Z]{1,5}$', label):
            if label in self.labelDictionary == True:
                if self.labelDictionary[label] >= 1:
                    self.labelDictionary[label] += 1
                    return self.labelProblemsMessage(label, "appears too many times in the code")
                else:
                    self.labelDictionary[label] += 1
            else:
                self.labelDictionary[label] = 0
                return ""
        return self.illFormedLabelMessage(label)

    def opCodeCheck(self, lineItems):
        if lineItems[0] == "DEF":
            self.invalidOpcode += 1
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
        return ""

    def validRegisterCheck(self, reg):
        for i in self.registers:
            if i == reg:
                return ""
        return self.illFormedOperandMessage(reg, "register number")

    def typeCheckSource(self, item):
        if re.match(r'^[A-Z]{1,5}$', item):
            return self.validLabelCheck(item)
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
            return self.validLabelCheck(item)
        elif re.match(r'^[0-9]{1,}$', item):
            return self.wrongOperandTypeMessage(item, "label", "number")
        else:
            return self.wrongOperandTypeMessage(item, "label", "variable or register")

########################################################################################################################
    # Change splits to strips if syntax doesn't require a space (R1,R2,R3)
    def threeSourceCheck(self, lineItems):
        countToken = 0
        errorMessage = ""
        for i in range(len(lineItems)):
            if i == 1:
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
            elif i == 3:
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
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
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
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
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
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
                errorMessage = self.typeCheckValue(lineItems[i].split(",")[0])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
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
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
            elif i == 2:
                errorMessage = self.typeCheckSource(lineItems[i].split(",")[0])
            elif i == 3:
                errorMessage = self.typeCheckLabel(lineItems[i].split(",")[0])
            elif i > 3:
                return self.tooManyOperandsMessage(lineItems[0], 3)
            if errorMessage:
                return errorMessage
            countToken += 1
        if countToken < 4:
            return self.tooFewOperandsMessage(lineItems[0], 3)
        return errorMessage

########################################################################################################################

    def tooManyOperandsMessage(self, item, num):
        self.tooManyOperands += 1
        return "too many operands -- expected " + str(num) + " operands for " + item

    def tooFewOperandsMessage(self, item, num):
        self.tooFewOperands += 1
        return "too few operands -- expected " + str(num) + " operands for " + item

    def illFormedOperandMessage(self, item, type):
        self.illFormedOperands += 1
        return "ill-formed operands -- " + item + " is an invalid " + type

    def variableProblemsMessage(self, item):
        self.variableProblems += 1
        return "variable problems -- " + item + " was not initialized"

    def labelProblemsMessage(self, item, type):
        self.labelProblems += 1
        return "label problems -- label " + item + " " + type

    def illFormedLabelMessage(self, item):
        self.illFormedLabel += 1
        return "ill formed label -- " + item + " does not follow label syntax"

    def wrongOperandTypeMessage(self, item, expected, present):
        self.wrongOperandType += 1
        return "wrong operand type -- " + present + " where " + expected + " expected at " + item





parser = PalParser()
parser.main("input.pal")