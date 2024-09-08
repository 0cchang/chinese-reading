from random import randint, shuffle
import redis
import json

# Configure Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

CHINASTART = 19968
TEST_ADDR = "Backend/levels/chinese-words.txt"

def loadLevelMCQ(address):
    
    
    # Fetch charMap and choiceMap from Redis
    charMap_json = redis_client.hgetall('character_to_id')  # Use HGETALL for hash
    choiceMap_json = redis_client.hgetall('id_to_character')  # Use HGETALL for hash
    
    if not charMap_json or not choiceMap_json:
        raise Exception("character_to_id or id_to_character not found in Redis")

    # Convert from bytes to strings
    charMap = {k.decode('utf-8'): v.decode('utf-8') for k, v in charMap_json.items()}
    choiceMap = {k.decode('utf-8'): v.decode('utf-8') for k, v in choiceMap_json.items()}
    charCount = len(charMap)

    print("Opening file...")
    with open(address, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    wordMap = {}  # index -> (chinese, pinyin, english)
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

    if not correctQueue or not choices:  # Load next question or reset
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
        
    return pinyin, english, reveal, currReveal, correctQueue, choices, dispChoices, level
