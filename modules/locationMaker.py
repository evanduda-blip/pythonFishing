import random

def checkList2D(array, row, col):
    return 0 <= row < len(array) and 0 <= col < len(array[row])

class newLocation:    
    
    def newLocationBlank (self, x, y):
        blankMap = []
        countx = 0

        while countx < x:
            blankMap.append([])
            county = 0
            while county < y:
                blankMap[countx].append(0)
                county += 1
            countx += 1

        self.area = blankMap
        return blankMap

    def newLocationWater (self, x, y):
        blankMap = self.newLocationBlank(x, y)
        startWater = random.randint(0, (x * y) - 1)
        width = random.randint(1, 4)

        startRow, startCol = divmod(startWater, y)

        for row in range(x):
            for col in range(y):
                distance = abs(row - startRow) + abs(col - startCol)
                if distance <= width:
                    if checkList2D(blankMap, row, col):
                        blankMap[row][col] = "w"

        self.area = blankMap
        return blankMap

    def newPond (self, x, y, layers=3):
        if layers < 1:
            raise ValueError("layers must be at least 1")

        blankMap = []
        for currentRow in range(x):
            layer = currentRow * layers // x + 1
            blankMap.append([str(layer) for _ in range(y)])
        self.area = blankMap
        return blankMap

    def addShop (self):
        for row in range(1, 4):
            for col in range(1, 4):
                self.area[row][col] = "S"

    def addLocalPond (self):
        pond = [
            "000ww0000",
            "00wwwww00",
            "0wwwwwww0",
            "wwwwwwwww",
            "wwwwwwwww",
            "wwwwwwwww",
            "0wwwwwww0",
            "00wwwww00",
            "000ww0000",
        ]
        startRow = 8
        startCol = 8

        for row, pondRow in enumerate(pond):
            for col, tile in enumerate(pondRow):
                if tile == "w":
                    self.area[startRow + row][startCol + col] = tile

    def addHouse (self):
        for row in range (1,3):
            for col in range(17,19):
                self.area[row][col] = "H"

    #Pick the top left corner
    #person parameter is a npc class
    def addNPC (self, row, col):
        self.area[row][col] = "N"

    def returnArea (self):
        return self.area