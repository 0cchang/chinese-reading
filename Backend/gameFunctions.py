from random import randint, shuffle
from charMap import getMaps

CHINASTART = 19968
TEST_ADDR = "Backend/levels/chinese-words.txt"

def loadLevelMCQ(address):
    wordMap = {}  # index -> (chinese, pinyin, english)
    charMap, choiceMap = getMaps()
    charCount = len(charMap)

    print("Opening file...")
    with open(address, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    print("Reading file...")
    for index, line in enumerate(lines):
        currLine = line.split()
        if not currLine:
            continue
        
        first = ord(currLine[0][0])
        if first < CHINASTART:
            continue
        
        characters = 0
        chineseWord, pinyin, english = "", "", ""
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
                english = " ".join(currLine[pointer:]).strip()
            pointer += 1
        
        wordMap[index] = [chineseWord, pinyin, english]

    return [wordMap, charMap, choiceMap]

def playMCQ(pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level):
    wordMap, charMap, choiceMap = level
    charCount = len(charMap)

    if not correctQueue or not choices:  # Load next question or reset
        num = randint(0, len(wordMap) - 1)
        correctAnswer, pinyin, english = wordMap[num]

        choices = [charMap[c] for c in correctAnswer]
        correctQueue = choices.copy()
        
        # Add random choices
        while len(choices) < 9:
            newChoice = randint(1, charCount)
            if newChoice not in choices:
                choices.append(newChoice)
        
        reveal = ["_" for _ in range(len(correctAnswer))]
        currReveal = 0
        shuffle(choices)
        dispChoices = [choiceMap[i] for i in choices]
        
    return pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level
