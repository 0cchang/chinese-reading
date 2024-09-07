from charMap import getMaps

CHINASTART = 19968

def loadLevelRead(address):
    clickToChar = {} #(x, y) -> charId
    print("opening file...")
    with open(address, 'r', encoding = 'utf-8') as file:
        lines = file.readlines()
    file.close()

    for index, line in enumerate(lines):
        currLine = line.split(" ")
        first = ord(currLine[0][:1])
        if first < CHINASTART:
            continue
            