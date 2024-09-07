from collections import deque
from random import randint, shuffle
from charMap import getMaps
from platform import system
CHINASTART = 19968
TEST_ADDR = "Backend\\levels\\chinese-words.txt"
TEST_ADDR_MAC = "Backend/levels/chinese-words.txt"


def loadLevelMCQ(address):
    wordMap = {} # index -> (chinese, pinyin, english)
    charMap, choiceMap = getMaps()
    charCount = len(charMap)

    print("opening file...")
    with open(address, 'r', encoding = 'utf-8') as file:
        lines = file.readlines()
    file.close()

    print("reading file...")
    for index, line in enumerate(lines):
        currLine = line.split(" ")
        first = ord(currLine[0][:1])
        if first < CHINASTART:
            continue
        characters = 0
        chineseWord = ""
        pinyin = ""
        english = ""
        pointer = 0
        while pointer < len(currLine):
            section = currLine[pointer]
            if pointer == 0:
                characters += len(section)
                chineseWord = section
                for c in section:
                    if c not in charMap:
                        charCount += 1
                        charMap[c] = charCount
                        choiceMap[charCount] = c

            elif characters > 0:
                pinyin += section
                characters -= 1
            else:
                english = "".join(currLine[pointer:])[:-1]
            pointer += 1
        
        wordMap[index] = [chineseWord, pinyin, english]

    return[wordMap, charMap, choiceMap]


def playMCQ(times, misses, correct, level):

    wordMap, charMap, choiceMap = level
    charCount = len(charMap)
    if times == 0:
        print("Summary:")
        print("Missed: ", misses)
        print("Correct: ", correct)
        return [misses, correct]
    
    num = randint(1, len(wordMap))
    correctAnswer, pinyin, english = wordMap[num]
    correctQueue = deque()
    choices = [] # holds ids of choices
    for c in correctAnswer:
        correctQueue.append(charMap[c]) #ids of correct answer
        choices.append(charMap[c]) #ids

    n = 9 - len(correctAnswer)
    while n > 0: # may be duplicates will fix later
        newChoice = randint(1, charCount)
        if newChoice not in choices:
            choices.append(newChoice)
            n -= 1
    reveal = ["_" for _ in range(len(correctAnswer))] 
    currReveal = 0
    shuffle(choices)
    while correctQueue:
        print(pinyin, english)
        print(reveal)
        
        chars = [choiceMap[i] for i in choices] #indexes characters
        
        print(chars)
        print("enter answer 1 to ",len(choices))

        #print(choiceMap[correctQueue[0]]) # prints answer for debugging
        answer = 0
        while answer not in range(1, len(choices)+1): # not input protected
            answer = int(input())
        answer -= 1
        
        if correctQueue[0] == charMap[chars[answer]]: #id to id
            reveal[currReveal] = choiceMap[correctQueue.popleft()]
            currReveal += 1
            correct+= 1
            choices.pop(answer)
        else:
            print("wrong")
            misses += 1
            if charMap[chars[answer]] in correctQueue:
                continue
            choices.pop(answer)
            
        
        
    return playMCQ(times - 1, misses, correct, level)

def runGame(times):
    match system():
        case "Windows":
            playMCQ(times, 0, 0, loadLevelMCQ(TEST_ADDR))

        case "Darwin":
            print("on mac")
            playMCQ(times, 0, 0, loadLevelMCQ(TEST_ADDR_MAC))



        

       




        
