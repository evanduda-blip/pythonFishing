

class player:
    
    def __init__(self):
        self.row = 1
        self.col = 1
        self.bobberCol = 0
        self.bobberDirection = 1
        self.inventory = []
        self.inPond = False
        self.money = 0.0
        rods = [
                {
                    "name":"Training Rod",
                    "strength": 1.0,
                    "valueMultiplier": 1.0
                }
            ]
        self.fishingRod = rods[0]
        self.fishingJournal = {}
        
    def changeMap(self, newMap):
        self.currentMap = newMap