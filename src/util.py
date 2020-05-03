def loadFile(name):
    with open(name, 'r', encoding='utf-8-sig') as file:
        lines = filter(None, (line.rstrip() for line in file))
        return list(lines)