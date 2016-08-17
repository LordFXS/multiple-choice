import math
import re
import platform
import os
import sys
import hashlib
import subprocess

newline = "\n"
folder = "\\"
statisticsList = []
maxScores = []
fractions = []

# Change newline char depending on system
if "Windows" in platform.system():
    newline = "\n"
    folder = "\\"
if "Darwin" in platform.system():
    newline = "\n"
    folder = "/"
if "Linux" in platform.system():
    newline = "\n"
    folder = "/"

    
def findOptions(inputFilename):
    # Check correct input type
    if not type(inputFilename) is str:
        raise TypeError("findOptions() expected a string, but got a %s" % type(inputFilename))
    f = open(inputFilename, "r")
    l = f.readline()
    res = []

    # Read contents of file:
    while not "\\end{document}" in l:
        if "\\begin{question}" in l:
            res.append(handleQuestion(f))
        l = f.readline()
    return res


def handleQuestion(fil):
    # Check the correct type of inputs
    if not type(fil) is file:
        raise TypeError("handleQuestion() expected a file, but got a %s" % (type(fil)))
    l = fil.readline()
    letters = []
    keys = []
    weight = 1
    stem = ""
    options = []
    
    # Read until the question is done
    while not "\\end{question}" in l:
        # Remember the stem
        if "\\stem{" in l:
            stem = l
        # Remember the stem if it is an environment
        if "\\begin{stem}" in l:
            stem = l
            while not "\\end{stem}" in l:
                l = fil.readline()
                stem = stem + l
        # Handle the weight if one exists
        if "\\weight" in l:
            tmp = l.split("{")
            tmp2 = tmp[1].split("}")
            weight = int(tmp2[0])
        # Handle each option
        if "\\option" in l:
            tmp = l.split("[",1)
            tmp2 = tmp[1].split("]",1)
            letters.append(tmp2[0])
            options.append(tmp[0] + tmp2[1])
        # Handle each key
        if "\\key" in l:
            tmp = l.split("[",1)
            tmp2 = tmp[1].split("]",1)
            letters.append(tmp2[0])
            keys.append(tmp2[0])
            options.append(tmp[0] + tmp2[1])
        # Handle environment style option
        if "\\begin{option}" in l:
            tmp = l.split("[",1)
            print tmp
            tmp2 = tmp[1].split("]",1)
            letters.append(tmp2[0])
            tmp3 = tmp[0] + tmp2[1]
            while not "\\end{option}" in l:
                l = fil.readline()
                tmp3 += l
            options.append(tmp3)
        # Handle environment style key
        if "\\begin{key}" in l:
            tmp = l.split("[",1)
            tmp2 = tmp[1].split("]",1)
            letters.append(tmp2[0])
            keys.append(tmp2[0])
            tmp3 = tmp[0] + tmp2[1]
            while not "\\end{key}" in l:
                l = fil.readline()
                tmp3 += l
            options.append(tmp3)
        l = fil.readline()
    # Construct the list of resulst and return it
    return [weight, keys, letters, [stem, options]]

def correct(test, answer, numQuestion):
    # Check correct input type
    if not type(test) is list or not type(answer) is list or not type(numQuestion) is int:
        raise TypeError("correct() expected two lists and a int, but got a %s, a %s, and a %s" % (type(test), type(answer), type(numQuestion)))
    weight = test[0]
    keys = test[1]
    letters = test[2]
    stem = test[3][0]
    options = test[3][1]
    keyChosen = False

    # If the there are more answers then possible throw an error
    if len(answer) > len(letters):
        raise StandardError("correct(): in question %s, there is %s options, but %s has been written" % ( numQuestion, str(len(letters)), str(len(answer))))

    # Calculate the number given to the bottom part of the fraction
    weigtedFractionPart = 0
    global fractions
    if len(fractions) == numQuestion:
        fractionPart = math.log(len(letters))
        weigtedFractionPart = weight * fractionPart
        fractions.append(weigtedFractionPart)
    else:
        weigtedFractionPart = fractions[numQuestion]

    # Special case no answer selected so the list of answers is ["-"]
    if len(answer) == 1 and answer[0] == "-":
        return [0, weigtedFractionPart, keyChosen, weight]

    # Check that no incorrect letter was writen in the answer list
    for letter in answer:
        if letter not in letters:
            raise StandardError("correct(): in question %s, %s is not a valid option" % ( numQuestion, letter))

    # If no or all options is marked return 0
    if len(answer) == len(letters):
        return [0, weigtedFractionPart, keyChosen, weight]

    # Check how many keys were marked
    markedKeys = 0
    counted = False
    for letter in answer:
        if letter in keys:
            markedKeys += 1
        index = letters.index(letter)
        global statisticsList
        for statElm in statisticsList:
            if statElm[0] in stem:
                print "match!"
                optIndex = statElm[1].index(options[index])
                statElm[2][optIndex] = statElm[2][optIndex] + 1
                if counted:
                    statElm[2].append(-1)
                counted = True
                break                

    # Calculate score 
    weightedScore = 0
    if markedKeys > 0:
        tmp = math.log(float(len(letters))/float(len(answer)))
        unweightedScore = tmp #* markedKeys
        weightedScore = weight * unweightedScore
        keyChosen = True
    else :
        tmp = -( float(len(answer)) / (float(len(letters)) - float(len(answer))))
        tmp2 = math.log(float(len(letters))/float(len(answer)))
        unweightedScore = tmp * tmp2
        weightedScore = weight * unweightedScore

    return [weightedScore, weigtedFractionPart, keyChosen, weight]


def correct_v1(test, answer, numQuestion):
    # Check correct input type
    if not type(test) is list or not type(answer) is list or not type(numQuestion) is int:
        raise TypeError("correct() expected two lists and a int, but got a %s, a %s, and a %s" % (type(test), type(answer), type(numQuestion)))
    weight = test[0]
    keys = test[1]
    letters = test[2]
    stem = test[3][0]
    options = test[3][1]
    keyChosen = False

    # If the there are more answers then possible throw an error
    if len(answer) > len(letters):
        raise StandardError("correct(): in question %s, there is %s options, but %s has been written" % ( numQuestion, str(len(letters)), str(len(answer))))

    # Calculate maximum score for this question if doesn't already exists
    maxScore = 0
    global maxScores
    if len(maxScores) == numQuestion:
        maxScore = weight * math.log(float(len(letters))/float(len(keys)))
        maxScores.append(maxScore)
    else:
        maxScore = maxScores[numQuestion]

    # Special case no answer selected so the list of answers is ["-"]
    if len(answer) == 1 and answer[0] == "-":
        return [0, maxScore, keyChosen, weight]
    
    # Check that no incorrect letter was writen in the answer list
    for letter in answer:
        if letter not in letters:
            raise StandardError("correct(): in question %s, %s is not a valid option" % ( numQuestion, letter))

    # If no or all options is marked return 0
    if len(answer) == len(letters):
        return [0, maxScore, keyChosen, weight]

    # Check how many keys were marked
    markedKeys = 0
    counted = False
    for letter in answer:
        if letter in keys:
            markedKeys += 1
        index = letters.index(letter)
        global statisticsList
        for statElm in statisticsList:
            if statElm[0] == stem:
                optIndex = statElm[1].index(options[index])
                statElm[2][optIndex] = statElm[2][optIndex] + 1
                if counted:
                    statElm[2].append(-1)
                counted = True
                break                

    # Calculate score 
    weightedScore = 0
    if markedKeys > 0:
        tmp = math.log(float(len(letters))/float(len(answer)))
        unweightedScore = tmp / len(keys) * markedKeys
        weightedScore = weight * unweightedScore
        keyChosen = True
    else :
        tmp = -( float(len(answer)) / (float(len(letters)) - float(len(answer))))
        tmp2 = math.log(float(len(letters))/float(len(answer)))
        unweightedScore = tmp * tmp2
        weightedScore = weight * unweightedScore

    return [weightedScore, maxScore, keyChosen, weight]


def checkSum(fil):
    # Check correct input type
    if not type(fil) is str:
        raise TypeError("checkSum() expected a string, but got a %s" % (type(fil)))
    blocksize = 65536 # To cut large files into blocks
    tmp = fil.split(".")
    filename = tmp[0] + ".sha256"
    # If the hash files doesn't exists
    if not os.path.exists(filename):
        raise IOError("Checksum file not found, %s" % filename)
    hashfile = open(filename, "rb")
    hasher = hashlib.sha256()
    res = True
    # Read a block from the file that is being checked
    # hash the block
    # compare it to the next line in the checksum file
    with open(fil, "rb") as checkFil:
        buff = checkFil.read(blocksize)
        while len(buff) > 0:
            hasher.update(buff)
            line = hashfile.readline()
            hashVal = hasher.hexdigest() + newline
            res = res and hashVal == line
            buff = checkFil.read(blocksize)
    return res

def generateListForStatistics(fil):
    # Check correct input type
    if not type(fil) is str:
        raise TypeError("generateDictionaries() expected a string, but got a %s" % (type(fil)))
    global statisticsList
    statisticsList = []
    # Search for questions and hand of responsebility when one is found
    with open(fil, "r") as f:
        l = f.readline()
        while not "\\end{test}" in l:
            if "\\begin{question}" in l:
                statisticsList.append(makeQuestionList(f))
            l = f.readline()
        f.close()


def makeQuestionList(f):
    # Check correct input type
    if not type(f) is file:
        raise TypeError("makeQuestionList() expected a file, but got a %s" % (type(f)))
    res = []
    options = []
    counters = []
    l = f.readline()
    # Make each question into a list consisting of the stem, the options, and a numerical value for each option
    while not "\\end{question}" in l:
        if "\\stem{" in l:
            res.append(l)
        if "\\option{" in l or "\\key{" in l:
            options.append(l)
            counters.append(0)
        if "\\begin{stem}" in l:
            tmp = l
            while not "\\end{stem}" in l:
                l = f.readline()
                tmp = tmp + l
            res.append(tmp)
        if "\\begin{option}" in l or "\\begin{key}" in l:
            tmp = l
            while (not "\\end{option}" in l) and (not "\\end{key}" in l):
                l = f.readline()
                tmp = tmp + l
            options.append(tmp)
            counters.append(0)
        l = f.readline()
    res.append(options)
    res.append(counters)
    return res


def correctTest(inputFilename, answers):
    # Check correct input type
    if not type(inputFilename) is str or not type(answers) is list:
        raise TypeError("correctTest() expected a string and a lists, but got a %s and a %s" % (type(inputFilename), type(answers)))
    results = []
    marks = 0.0
    fraction = 0.0
    numCorrect = 0
    numQuestions = 0

    print inputFilename + newline
    
    # Check hash checksum for file
    if not checkSum(inputFilename):
        raise AssertionError("There is something wrong %s does not match its checksum file" % (inputFilename))
    
    # Find the number of options, keys, and weight for each question
    fromTest = findOptions(inputFilename)

    # Check that the number of answers and questions match
    if len(fromTest) > len(answers):
        raise StandardError("correctTest(): missing answers for %s questions" % str(len(fromTest)-len(answers)))
    if len(fromTest) < len(answers):
        raise StandardError("correctTest(): too many answers")

    # Score the test
    for i in range(0,len(answers)):
        results.append(correct(fromTest[i],answers[i], i))
    for res in results:
        marks += res[0]
        fraction += res[1]
        if res[2]:
            numCorrect += res[3]
        numQuestions += res[3]
    return [marks / fraction * 100, numCorrect, numQuestions]


def destructAnswerFile(answerFile):
    # Check correct input type
    if not type(answerFile) is str:
        raise TypeError("destructAnswerFile() expected a string, but got a %s" % (type(answerFile)))
    f = open(answerFile, "r")
    studentNumber = 0
    testNumber = 0
    answersList = []
    res = []
    # Go through each line of the answer file
    for line in f:
        # Match empty line or line of whitespace and skip the iteration
        if re.match("\s+", line):
            continue
        # Split the line on a single whitespace char and save the parts
        tmp = line.rstrip().split(" ", 2)
        studentNumber = int(tmp[0])
        testNumber = int(tmp[1])
        # Split the answers base on numerical chars
        answersList = re.split("[0-9]+",tmp[2])
        # Remove the empty string that is in the start of the list
        answersList.pop(0)
        # Convert the strings of answers to lists contaning the chars
        # Example "AB" becomes ["A", "B"]
        for i in range(0,len(answersList)):
            answersList[i] = list(answersList[i])
        res.append([studentNumber, testNumber, answersList])
    return res

def correctMultipleTests(orgfilePath, answersFilename, scoreFilename, filePath, texFilename):
    # Check correct input type
    if not type(texFilename) is str or not type(answersFilename) is str or not type(scoreFilename) or not type(filePath) is str or not type(orgfilePath) is str:
        raise TypeError("correctMultipleTests() expected five strings, but got a %s, a %s, a %s, a %s, and a %s" % (type(texFilename), type(answersFilename), type(scoreFilename), type(filePath), type(orgfilePath)))
    scoreFile = open(scoreFilename, "w")
    texFilePath = filePath + folder + "TeX"
    
    # Destruct the answer file
    answers = destructAnswerFile(answersFilename)

    # Generate the list need for the statistics document
    originalFile = filePath + folder + "original.tex"
    generateListForStatistics(originalFile)

    i = 0
    # For each answer check them against the .tex file that generated the test
    for answer in answers:
        res = correctTest(texFilePath + folder + texFilename + str(answer[1]) + ".tex", answer[2])
        score = str(round(res[0], 2))
        if score < 0:
            score = 0
        numCorrect = res[1]
        numQuestions = res[2]
        scoreFile.write("Student number: " + str(answer[0]) + " correctly answered " + str(numCorrect) + " out of " + str(numQuestions) + ", which calculates to a score of: " + score  + "%" + newline)
        i += 1
        print str(i) + " test(s) corrected so far"
    scoreFile.close()

    # Generate the total scoring file
    totalScoreFile = open(filePath + folder + "TotalScore.tex", "w")
    org = open(originalFile, "r")
    orgLine = org.readline()
    while not "\\end{document}" in orgLine:
        if "\\begin{question}" in orgLine:
            writeQuestion(totalScoreFile, i)
            while not "\\end{question}" in orgLine:
                orgLine = org.readline()
        elif "\\begin{test}" in orgLine:
            totalScoreFile.write(orgLine)
            totalScoreFile.write("\\renewcommand{\\numberOfCandidates}{" + str(i) + "}" + newline)
            totalScoreFile.write("\\renewcommand{\\showKeys}{" + str(1) + "}" + newline)
        else:
            totalScoreFile.write(orgLine)
        
        orgLine = org.readline()
    totalScoreFile.write(orgLine)
    totalScoreFile.close()
    org.close()

    loc = os.getcwd() + folder + filePath + folder
    os.chdir(orgfilePath)
    #subprocess.call(["pdflatex", "-output-directory=" + loc, "TotalScore.tex"], stdout=subprocess.PIPE)
    subprocess.call(["pdflatex", "-output-directory=" + loc, "TotalScore.tex"])

def writeQuestion(fil, total):
    elm = statisticsList.pop(0)
    testHandedIns = 0
    totalAnswers = 0
    for num in elm[2]:
        testHandedIns += num
        if num > 0:
            totalAnswers += num
    fil.write("\\begin{question}[" + str(testHandedIns) + "]" + newline)
    fil.write(elm[0])
    fil.write("\\begin{options}" + newline)
    for j in range(0,len(elm[1])):
        option = elm[1][j]
        if "\\begin{key}" in option or "\\begin{option}" in option:
            tmp = option.split("}",1)
            tmp[0] = tmp[0] + "}[" + str(elm[2][j]) + "/" + str(totalAnswers) + "]"
            option = "".join(tmp)
        else:
            tmp = option.split("{",1)
            tmp[0] = tmp[0] + "[" + str(elm[2][j]) + "/" + str(totalAnswers) + "]{"
            option = "".join(tmp)
        if "\\key" in option:
            option = option + "\\hfill" + str(round(float(elm[2][j]) / float(total) * 100.0, 2)) + "\%"
        if "\\begin{key}" in option:
            tmp = option.split("\\end{key}",1)
            option = tmp[0] + "\\hfill" + str(round(float(elm[2][j]) / float(total) * 100.0, 2)) + "\%" + newline + "\\end{key}"
        fil.write(option)
        j += 1
    fil.write("\\end{options}" + newline)
    fil.write("\\end{question}" + newline)




    
if len(sys.argv) is 1:
    pass
elif len(sys.argv) is 2:
    correctMultipleTests(sys.argv[1], "answers.txt", "Scores.txt", "generated_tests", "test")
elif len(sys.argv) is 3:
    correctMultipleTests(sys.argv[1], sys.argv[2], "Scores.txt", "generated_tests", "test")
elif len(sys.argv) is 4:
    correctMultipleTests(sys.argv[1], sys.argv[2], sys.argv[3], "generated_tests", "test")
elif len(sys.argv) is 5:
    correctMultipleTests(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], "test")
else:
    correctMultipleTests(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
