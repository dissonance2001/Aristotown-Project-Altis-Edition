import math

def getLevelExp(experience):
    return int(math.ceil((math.sqrt(10000 + (80 * (experience + 1))) - 100) / 40))

def getExpLevel(level):
    return 20 * level * (level + 5)
