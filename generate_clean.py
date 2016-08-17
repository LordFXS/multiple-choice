#imports
import platform
import random
import copy
import sys
import os
import time
import subprocess
import hashlib

# Record the start time
start_time = time.time()

# Default values
seed = 0000
random.seed(seed)
newline = "\n"
folder = "\\"

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


# Change the seed value
def setSeed(num):
    if type(num) is int:
        global seed
        seed = num
        random.seed(seed)
    else:
        raise TypeError("The seed must be set to a integer, it was %s" % type(num))


# Get the value of seed
def getSeed():
    global seed
    return seed


# Takes a list and swaps all the elements on even indexes
def swapEven(lst):
    # Check correct type of input
    if not type(lst) is list:
        raise TypeError("swapEven() expected a list, but got a %s" % type(lst))
    even = []
    odd = []
    res = []

    # Destruct list and reverse the list of even elements
    for i in range(0,len(lst)):
        if i % 2 is 0:
            even.append(lst[i])
        else:
            odd.append(lst[i])
    even.reverse()

    # Reconstruct the list with the reversed even elements
    for i in range(0,len(lst)):
        if i % 2 is 0:
            res.append(even.pop(0))
        else:
            res.append(odd.pop(0))
    return res


# Takes a list and swaps all the elements on odd indexes
def swapOdd(lst):
    # Check correct type of input
    if not type(lst) is list:
        raise TypeError("swapOdd() expected a list, but got a %s" % type(lst))
    odd = []
    even = []
    res = []

    # Destruct the list and reverse the list of elements that had an odd index
    for i in range(0,len(lst)):
        if i % 2 is 1:
            odd.append(lst[i])
        else:
            even.append(lst[i])
    odd.reverse()

    # Reconstruct the list with the now reversed odd elements
    for i in range(0,len(lst)):
        if i % 2 is 1:
            res.append(odd.pop(0))
        else:
            res.append(even.pop(0))
    return res


# Destructs a test
def destructTest(f):
    # Check if type of the input is correct
    if not type(f) is file:
        raise TypeError("destructTest() expected a file, but got a %s" % type(f))
    l = f.readline()
    groups = []
    tmp = ""

    # Read until \end{test} is meet and split the groups to create the list of groups
    while not "\\end{test}" in l:
        if "\\begin{questionGroup}" in l:
            groups.append(destructGroup(f, l))
        l = f.readline()
    return groups


# Destruct the textuel group into a list representing the group
def destructGroup(f, prev):
    # Check types of the input
    if not type(f) is file or not type(prev) is str:
        raise TypeError("destructGroup() expected a file and a string, but got a %s and a %s" % (type(f), type(prev)))
    l = f.readline()
    group = [prev]
    tmp = ""

    # Read until \end{questionGroup} is meet, and split the group into parts
    while not "\\end{questionGroup}" in l:

        # Make the groupHeading into its own part
        if "\\groupHeading{" in l:
            group.append(l)

        # Make the whole groupText into one part
        elif "\\begin{groupText}" in l:
            while not "\\end{groupText}" in l:
                tmp += l
                l = f.readline()
            tmp += l
            group.append(tmp)
            tmp = ""

        # Make each question into its own part
        elif "\\begin{question}" in l:
            group.append(destructQuestion(f, l))
        l = f.readline()
    group.append(l)
    return group


# Destruct a textuel question and create a list of its parts
def destructQuestion(f, prev):
    # Check correct types for input
    if not type(f) is file or not type(prev) is str:
        raise TypeError("destructQuestion() expected a file and a string, but got a %s %s" % (type(f), type(prev)))
    l = f.readline()
    question = [prev]
    tmp = ""
    stem = ""
    weight = ""

    # Read until \end{question} is meet and split the question into parts
    while not "\\end{question}" in l:

        # Save the stem
        if "\\stem" in l:
            stem = l

        # Save the stem if it is an environment
        if "\\begin{stem}" in l:
            stem += l
            while not "\\end{stem}" in l:
                l = f.readline()
                stem += l
                
        # Make the list of options into a part
        elif "\\begin{options}" in l:
            question.append(destructOptions(f, l))

        # If there is a weight save it
        elif "\weight" in l:
            weight = l
        l = f.readline()
    # Insert the stem
    question.insert(1,stem)
    # If there was a weight insert it
    if not weight == "":
        question.insert(3,weight)
    question.append(l)
    return question


# Destruct a textuel list of options and create a list of the elements
def destructOptions(f, prev):
    # Check the correct type of inputs
    if not type(f) is file or not type(prev) is str:
        raise TypeError("destructOptions() expected a file and a string, but got a %s, and a %s" % (type(f), type(prev)))
    l = f.readline()
    options = [prev]
    tmp = ""

    # Read until \end{options} is meet and split the options into elements
    while not "\\end{options}" in l:

        # Create option/key element and assign random letter
        if "\\option" in l or "\\key" in l:
            if not getSeed() == 0:
                ls = l.split("{")
                for x in range(1,len(ls)):
                    ls[x] = "{" + ls[x]
                ls.insert(1, "[" + generateLetter() + "]")
                options.append("".join(ls))
            else: # If seed == 0 do not add random letters
                options.append(l)

        # Create option/key element and assign random letter if the option/key is an environment
        if "\\begin{key}" in l or "\\begin{option}" in l:
            opt = l
            # If the seed is not 0, assign random letter
            if not getSeed() == 0: 
                opt = opt.rstrip() + "[" + generateLetter() + "]" + newline
            while (not "\\end{key}" in l) and (not "\\end{option}" in l):
                l = f.readline()
                opt = opt + l
            options.append(opt)
                
        l = f.readline()
    options.append(l)

    # Reset the random letter generator, so all letters are available again
    resetLetters()
    return options


# Swap function, which decides based on the seed which swap to use
def swap(lst):
    # Check the correct input type
    if not type(lst) is list:
        raise TypeError("swap() expected a list, but got a %s" % type(lst))
    global seed

    # If seed is 0 do nothing
    if not seed is 0:
        res = []

        # If seed % 4 is 0 swap the even indexed elements
        if seed % 4 is 0:   
            res = swapEven(lst)

        # If seed % 4 is 1 swap the odd indexed elements
        elif seed % 4 is 1:
            res = swapOdd(lst)

        # If seed % 4 is 2 reverse the list
        elif seed % 4 is 2:
            res = lst
            res.reverse()

        # If seed % 4 is 3 do not change the list
        elif seed % 4 is 3:
            res = lst
        #seed += 1
        return res
    else:
        return lst


# Permute a test
def permuteTest(test):
    # Check correct input type
    if not type(test) is list:
        raise TypeError("permuteTest() expected a list, but got a %s" % type(test))
    res = []
    tmp = []
    tmp2 = []
    tmp = permute(test, 0, False) #permute the groups
    for elm in tmp:
        if not type(elm[2]) is list:
            tmp2.append(permute(elm, 3, True)) #permute the questions, when the group have a groupText
        else:
            tmp2.append(permute(elm, 2, True)) #permute the questions, when the group doesn't have a groupText   
    for i in range(0,len(tmp2)):
        group = tmp2[i]
        for j in range(3, len(group) - 1):
            question = group[j]
            options = question[2] # Structure of question will be [start, stem, [options], weight?, end]
            question[2] = permute(options, 1, True) # Permute the options of the test
            tmp2[i][j] = question
            j += 1
        i += 1
    res = tmp2
    return res


# Permute a list
def permute(lst, offset, saveLast):
    # Check if input has the correct types
    if not type(lst) is list or not type(offset) is int or not type(saveLast) is bool:
        raise TypeError("permute() expected a list, an integer, and a bool  but got a %s, an %s, and a %s" % (type(lst), type(offset), type(saveLast)))
    res = []

    # Save offset many first elements of the list
    for x in range(0,offset):
        res.append(lst.pop(0))

    # Save last element of saveLast is true
    if saveLast:
        tmp = lst.pop(len(lst) - 1)

    # Swap the remaning list and add them to the result
    swlst = swap(lst)
    for elm in swlst:
        res.append(elm)

    # If the last element was taken out put it back in
    if saveLast:
        res.append(tmp)
    return res


# Read an input file, destruct it, permute it, and write the result to the output file
def readWriteTestFile(inputFile, outputFile):
    # Check correct input types
    if not type(inputFile) is str or not type(outputFile) is str:
        raise TypeError("readWriteTestFile() expected two strings, but got a %s and a %s" % (type(inputFile), type(outputFile)))
    f = open(inputFile, "r")
    o = open(outputFile, "w")
    l = f.readline()
    global newline

    # Read and then write the contents of the input file
    while not "\\end{document}" in l:

        # If a test starts the destruct it, permute it, and write the result to the output file
        if "\\begin{test}" in l:
            o.write(l)
            test = destructTest(f)
            permuted = permuteTest(test)
            writeTest(permuted, o)
            o.write("\\end{test}" + newline)
        elif "\\testNumber" in l:
            o.write(handleTestNumber(l))
        else:
            o.write(l)
        l = f.readline()
    o.write(l)
    o.close()

                
def handleTestNumber(line):
    # Check the types of the input
    if not type(line) is str:
        raise TypeError("handleTestNumber() expected a string but got a %s" % type(line))
    # Find an instance of \testNumber and exchange it with the seed value.
    if "\\testNumber" in line:
        parts = line.split("\\testNumber", 1)
        newPart = str(getSeed())
        while len(newPart) < 4:
            newPart = "0" + newPart
        parts.insert(1, newPart)
        meh = "".join(parts)
        # Call recursivly
        return handleTestNumber(meh)
    else:
        return line
    

# Write the list representing a test to the output file
def writeTest(lst, out):
    # Check the types of the input
    if not type(lst) is list or not type(out) is file:
        raise TypeError("writeTest() expected a list and a file, but got a %s and a" % (type(lst), type(out)))
    # Destruct the list
    for elm in lst:
        # If the element of the list is a list make a recursive call
        if isinstance(elm, list):
            writeTest(elm, out)
        # Else just write the element to the file
        elif type(elm) is str:
            out.write(elm)


def hashFile(outFile):
    # Check correct types of input
    if not type(outFile) is str:
        raise TypeError("hashFile() expected a string, but got a %s" % type(outFile))
    blocksize = 65536 # To cut large files into blocks
    tmp = outFile.split(".")
    global newline
    # If the hash files doesn't exists
    if not os.path.exists(tmp[0] + ".sha256"):
        hashfile = open(tmp[0] + ".sha256", "wb")
        hasher = hashlib.sha256()
        # loop read block size, hash the value and put the value intp the new hashfile
        with open(outFile, "rb") as fil:
            buff = fil.read(blocksize)
            while len(buff) > 0:
                hasher.update(buff)
                hashfile.write(hasher.hexdigest() + newline)
                buff = fil.read(blocksize)

            
# Generate multiple tests based on an input file
def generateMultipleTests(inputfile, num, outfilename):
    # Check correct types of input
    if type(num) is int and type(inputfile) is str and type(outfilename) is str:
        # Setup paths
        oldPath = os.getcwd() + folder
        texFolder = oldPath + "generated_tests" + folder + "TeX" + folder
        pdfFolder = oldPath + "generated_tests" + folder + "pdf" + folder

        # Check if destination folders exists, if not create them
        if not os.path.exists(oldPath + "generated_tests" + folder):
            os.makedirs(oldPath + "generated_tests" + folder)
        if not os.path.exists(texFolder):
            os.makedirs(texFolder)
        if not os.path.exists(pdfFolder):
            os.makedirs(pdfFolder)

        # Set new path
        os.chdir(os.path.dirname(os.path.abspath(inputfile)))

        # Generate for the original non shuffled file
        orgFile = oldPath + "generated_tests" + folder + "original.tex"
        if not os.path.exists(orgFile):
            readWriteTestFile(oldPath + inputfile, orgFile)
            hashFile(orgFile)
            #subprocess.call(["pdflatex", "-output-directory=" + oldPath + "generated_tests" + folder, orgFile], stdout=subprocess.PIPE)
            subprocess.call(["pdflatex", "-output-directory=" + oldPath + "generated_tests" + folder, orgFile])
        
        # Loop that generates .tex files and then compiles them with pdflatex
        for x in range(0, num + 1):
            setSeed(x)
            outFile = texFolder + outfilename + str(x) + ".tex"
            # If the file does not already exists create it
            if not os.path.exists(outFile):
                # Generate file
                readWriteTestFile(oldPath + inputfile, outFile)
                # Compile the file
                #subprocess.call(["pdflatex", "-output-directory=" + pdfFolder, outFile], stdout=subprocess.PIPE)
                subprocess.call(["pdflatex", "-output-directory=" + pdfFolder, outFile])
            # Hash the file
            hashFile(outFile)
            print "created test number " + str(x) + " with the name " + outFile
            x += 1
        os.chdir(oldPath)
    else:
        # Raise error if the inputs had a wrong type
        raise TypeError("generateMultipleTests() expected the name of the4 input file of type string, the number of tests to generate of type int, and the base name of the outputfiles of type string. Instead it got %s, %s, and %s." % (type(inputfile), type(num), type(outfilename)))
    


# Random letter
fullLetters = ["A","B","D","E","F","G","H","J","K","L","M","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
letters = copy.deepcopy(fullLetters)

def resetLetters():
    global letters
    letters = copy.deepcopy(fullLetters)

def generateLetter():
    return letters.pop(random.randint(0,len(letters) - 1))


if len(sys.argv) is 1:
    pass
elif len(sys.argv) is 2:
    generateMultipleTests(sys.argv[1], 1, "test")
elif len(sys.argv) is 3:
    generateMultipleTests(sys.argv[1], int(sys.argv[2]), "test")
else:
    generateMultipleTests(sys.argv[1], int(sys.argv[2]), sys.argv[3])

    

print("--- The run took %s seconds ---" % (time.time() - start_time))
