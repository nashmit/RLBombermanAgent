
def isCointAt(mylist, x, y):
    for (i, j) in mylist:
        if (i, j) == (x, y):
            return 1
    return 0

def isBombAt(mylist, x, y):
    for (i, j) in mylist:
        if(i, j) == (x, y):
            return True
    return False