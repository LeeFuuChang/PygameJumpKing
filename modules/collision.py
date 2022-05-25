def CheckLinesCollision(a1, b1, a2, b2):
    uA = ((b2[0] - a2[0]) * (a1[1] - a2[1]) - (b2[1] - a2[1]) * (a1[0] - a2[0])) / ((b2[1] - a2[1]) * (b1[0] - a1[0]) - (b2[0] - a2[0]) * (b1[1] - a1[1]))
    uB = ((b1[0] - a1[0]) * (a1[1] - a2[1]) - (b1[1] - a1[1]) * (a1[0] - a2[0])) / ((b2[1] - a2[1]) * (b1[0] - a1[0]) - (b2[0] - a2[0]) * (b1[1] - a1[1]))
    if(uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1):
        intersectionX = a1[0] + (uA * (b1[0] - a1[0]))
        intersectionY = a1[1] + (uA * (b1[1] - a1[1]))
        return [True, intersectionX, intersectionY]
    return [False, 0, 0]