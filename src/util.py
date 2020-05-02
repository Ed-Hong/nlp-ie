def loadFile(name):
    with open(name, 'r') as file:
        lines = filter(None, (line.rstrip() for line in file))
        return list(lines)