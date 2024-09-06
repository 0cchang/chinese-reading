from random import randint, shuffle

CHINASTART = 19968
TEST_ADDR = "Backend\levels\chinese-words.txt"



def readLevel(address):
    wordMap = {} # index -> (chinese, pinyin, english)
    charMap = {} # character -> id
    choiceMap = {} # id -> character
    charCount = 0

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

    return[wordMap, charMap, choiceMap, charCount]


def playGame(times, misses, correct, level):

    wordMap, charMap, choiceMap, charCount = level
    if times == 0:
        return [misses, correct]
    
    num = randint(1, len(wordMap))
    correctAnswer, pinyin, english = wordMap[num]
    correctQueue = []
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
        answer = int(input()) # not input protected
        answer -= 1
        
        if correctQueue[0] == charMap[chars[answer]]: #id to id
            reveal[currReveal] = choiceMap[correctQueue.pop(0)]
            currReveal += 1
            correct+= 1
            choices.pop(answer)
        else:
            print("wrong")
            misses += 1
            if charMap[chars[answer]] in correctQueue:
                continue
            choices.pop(answer)
            
        
        
    return playGame(times - 1, misses, correct, level)

score = playGame(5, 0, 0, readLevel(TEST_ADDR))
print("Summary:", score)

        

       




        
