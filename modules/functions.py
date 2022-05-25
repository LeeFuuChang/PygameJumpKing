def dist(x1, y1, x2, y2):
    return ( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) )**(1/2)

def mapNumber(n, a1, b1, a2, b2):
    r = ((n-a1)*((b2-a2) / (b1-a1))) + a2
    return r

def numberInRange(a, b1, b2):
    return (
        b1 <= a and a <= b2
    ) or (
        b2 <= a and a <= b1
    )