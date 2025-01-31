import sys
import os
from speechEditorUI import SpeechEditorUI
from PyQt5 import QtCore, QtGui, QtWidgets
import socket
from resources import IP, PORT, substitutions, digits


class SpeechEditor():
    ###################################################################################
    # __init__: 
    # inputs:
    # outputs:
    def __init__(self):
        
        self.digits = digits
        self.substitutions = substitutions

        self.fileName = ''              # file object
        self.fileLines = []             # list of file lines
        self.currentLine = ''           # list containing words/punctuation of current line
        self.wordList = []              # list of detected words that have not yet been confirmed
        self.lineHistory = []           # history of the line currently being edited
        self.fileHistory = []           # history of the file currently being edited
        self.fileHistoryIndex = 0       # index to keep track of which file we are working on
        self.lineHistoryIndex = 0       # index to track the line history we are working on
        self.wordIndex = 0              # index to track the word the curser is currently at (in the current line)
        self.charIndex = 0              # word to track the chracter we are currently editing in the line
        self.currentLineNum = 0         # Line number we are editing
        self.mode = "stop"              # mode for tracking key word handling
        self.rawCommand = ""
        
        # socket for message passing
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind( (IP, PORT) )

    # action keywords: if lineHistory is not empty, then move to the previous line index

    def undo(self):
        print("undo")
        self.currentLineNum -= 1
        self.currentLine = self.lineHistory[self.currentLineNum]

    def erase(self):
        self.currentLine = ""
        print("erase")

    def delete(self):
        index = self.wordIndex - 1
        self.wordList.remove(index)
        self.currentLine = ' '.join(self.wordList)      # TODO: check hpw to join
        print("delete")

    
    def back(self):
        print("back")

    def forward(self):
        print("forward")

    def underscore(self):
        print("Underscore")
        
    def getText(self):
        while True:
            self.listen()
            numWords = len(self.wordList)
            print(f"from getText: wordList: {self.wordList}")

            wordIndex = 0
            while wordIndex < numWords:
                word = self.wordList[wordIndex]

                # ignore all 
                if word == "confirm":
                    self.wordList.pop(wordIndex)
                    self.currentLine += " ".join(self.wordList)
                    print(f"Current line: {self.currentLine}")
                    return
                elif word == "escape":
                    self.wordList.pop(wordIndex)                        # rmove the word escape and keep the literal by incrementing the list index
                else:
                    self.wordList[wordIndex] = self.substitute(word)    # check for substitutions 
                #TODO: Else: action words. 
                #TODO: Edit the current Line object while the for loop is processing.
                wordIndex += 1
            self.currentLine += " ".join(self.wordList)
            print(f"Current line: {self.currentLine}")


    ###################################################################################
    # getFile: 
    # inputs:
    # outputs:
    def getFile(self, fileOption):
        self.currentLine = ''
        self.currentLineNum = 'F'
        if fileOption == "create":
            self.mode = "createFile"
            self.getText()
            self.fileName = self.currentLine
            self.file = open(self.fileName, 'w')
            self.file.close()
            
            """
            Insert error handling for files that already exist
            """

        elif fileOption == "edit":
            self.mode = "editFile"
            self.fileName = self.getText()

            """
            Insert error handling for files that don't exist
            """

        self.currentLine = ""
        self.currentLineNum = 0
        self.mode = "start"

    ###################################################################################
    # substitute:   Check the two raw substitution dictionaries taken from resources.py.
    #               replace any match with its substitution.
    # inputs:       word.
    # outputs:      substitution word.
    def substitute(self, word):
        if word in self.substitutions:
            return self.substitutions[word]
        if word in self.digits:
            return self.digits[word]
        return word


    ###################################################################################
    # firstLineHandler: Create a file with the file name and append the new line into
    #               the fileLines list. Write the new line to the file.
    def firstLineHandler(self):
        self.currentLineNum = 0                 # reset the line number
        self.currentLine = ''                   # reset the line content
        self.currentLine = self.getText()       # get our text string
        self.fileLines.append(self.currentLine) # append to our file lines list
        with open(self.fileName, "w") as f:     # write one line to the file
            f.writelines(self.fileLines)
        return
    
    ###################################################################################
    # lastLineHandler: For evey line in between the last line of the file and the line
    #               in which we are inserting new text, insert a new line character.
    #               Reset the line objects and trackers. Read the line form input. Write
    #               all ines back to file.
    def lastLineHandler(self, totalLines, insertionLine):
        self.currentLineNum = insertionLine
        self.currentLine = ""
        self.getText()
        for i in range(totalLines, insertionLine):
            self.fileLines.append("\n")
        self.fileLines.append(self.currentLine)
        with open(self.fileName, "w") as f:
            f.writelines(self.fileLines)
        return
    
    ###################################################################################
    # middleLineHandler: Edit a currently existing line. Place the current line into
    #               the self.currentLine object so that it displays and edits properly.
    #               call the getText object to edit (not replace) the currentLine obj.
    #               write all the lines back to the file.
    def middleLineHandler(self, insertionLine):
        self.currentLine = self.fileLines[insertionLine]
        self.currentLineNum = insertionLine
        self.getText()
        self.fileLines[insertionLine] = self.currentLine
        with open(self.fileName, "w") as f:
            f.writelines(self.fileLines)
        return
    

    ###################################################################################
    # getFileLines: Open the file and test how many lines exist. Give the user an error
    #               message when the file does not exist. 
    # output:       Return the length of the file Lines
    def getFileLines(self):
        try:
            with open(self.fileName, "r") as f:
                self.fileLines = f.readlines()
        except:
            # TODO: error handle when file doesn't exist
            return 0
        return len(self.fileLines)
    
    ###################################################################################
    # getIntfromWords:  General handler for translating words & their homophones into
    #           an int object. Note that built in functions may not handle homophones.
    def getIntfromWords(self, wordNum):
        sub = self.substitute(wordNum)
        try:    # try to convert the word number into a digit. 
            insertionLine = int(sub)
            return insertionLine
        except: # if fails, then command was an error
            return

    ###################################################################################
    # getLine:  Translate the line number from word format (including homophones) into
    #           an int object. Rely on different handlers to place the new or edited 
    #           line into the first line of a file, replace a current line, or append
    #           a new line any position below the last line.
    def getLine(self, wordNum):
        self.mode = "line"
        insertionLine = self.getIntfromWords(wordNum)
        totalLines = self.getFileLines()

        if (insertionLine == 0 and totalLines == 0):
            self.firstLineHandler()
        elif (insertionLine >= totalLines):
            self.lastLineHandler(totalLines, insertionLine)
        elif ( (insertionLine < totalLines) and (totalLines != 0) ):
            self.middleLineHandler(insertionLine)

    

    ###################################################################################
    # terminal: execute the command from the audio. Because we call getText, "CONFIRM"
    #           is necessary to finish reading from the input.
    def terminal(self):
        self.getText()
        print(f"current line: {self.currentLine}")
        os.system(self.currentLine)

    ###################################################################################
    # process:  check for key words from the START state. only 4 key words.
    #           each key word comes witha handler. "file" and "line" require one more
    #           word for correct syntax. Do not process command unless the second word
    #           is present.
    def process(self, numWords):
        word0 = self.wordList.pop(0)
        if word0 == "stop":                                 # stop the program
            sys.exit(0)
        elif word0 == "terminal":                           # edit and run a terminal command
            print(f"terminal")
            self.terminal()
        elif numWords > 1:                                  # file/line edit require one more argument
            word1 = self.wordList.pop(0)
            if word0 == "file":                             # edit or create a file
                print(f"file: {word1}")
                self.getFile(word1)
            elif (word0 == "line" and self.fileName != ''): # edit or create a line
                print(f"line: {word1}")
                self.getLine(word1)

    ###################################################################################
    # start:    block the process while waiting for input from audio process. save the
    #           raw text into rawCommand to visualize our model. Parse the words for 
    #           substitution and processing.
    def listen(self):
        data, addr = self.sock.recvfrom(1024)
        print(data)
        self.rawCommand = data.decode('utf-8')
        self.wordList = self.rawCommand.split()
        return

    ###################################################################################
    # start:    Inifinite socket polling. Once a packet is recieved, iterate through
    #           each word of the recieved packet. Process command. Only accept raw text.
    #           only key words in this phase. no "CONFRIM" is needed (only in getText).
    def start(self):
        while (True):
            self.listen()
            print(self.wordList)
            while True:
                numWords = len(self.wordList)
                if numWords <= 0:
                    break
                self.process(numWords)



if __name__ == "__main__":
    editor = SpeechEditor()
    editor.start()