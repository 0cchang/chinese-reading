from random import randint, shuffle
import redis
import json

# Configure Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

CHINASTART = 19968
TEST_ADDR = "Backend/levels/chinese-words.txt"

def loadLevelMCQ(address):
    # Fetch charMap and choiceMap from Redis
    charMap_json = redis_client.hgetall('character_to_id')  # Use HGETALL for hash
    choiceMap_json = redis_client.hgetall('id_to_character')  # Use HGETALL for hash
    
    if not charMap_json or not choiceMap_json:
        raise Exception("character_to_id or id_to_character not found in Redis")

    charMap = charMap_json
    choiceMap = choiceMap_json
    charCount = len(charMap)

    print("Opening file...")
    wordMap = {}  # index -> (chinese, pinyin, english)
    
    try:
        with open(address, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise Exception(f"File not found: {address}")
    except IOError as e:
        raise Exception(f"Error reading file: {e}")
    
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
                        charMap[c] = str(charCount)
                        choiceMap[str(charCount)] = c
            elif characters > 0:
                pinyin += section
                characters -= 1
            else:
                english = " ".join(currLine[pointer:]).strip()
            pointer += 1
        
        wordMap[str(index)] = [chineseWord, pinyin, english]

    return [wordMap, charMap, choiceMap]

def playMCQ(pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level):
    
    wordMap, charMap, choiceMap = level
    charCount = len(charMap)

    num = str(randint(0, len(wordMap) - 1))
    correctAnswer, pinyin, english = wordMap[num]

    choices = [charMap.get(c, -1) for c in correctAnswer]
    correctQueue = choices.copy()
    
    # Add random choices
    while len(choices) < 9:
        newChoice = str(randint(1, charCount))
        if newChoice not in choices:
            choices.append(newChoice)
    
    reveal = ["_" for _ in range(len(correctAnswer))]
    currReveal = 0
    shuffle(choices)
    dispChoices = [choiceMap.get(str(i), '') for i in choices]
    print(correctQueue, choices)
    return pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level
