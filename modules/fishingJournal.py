import msvcrt

class fishingJournal:
    def __init__(self):
        self.journal = []

    def newJournal(self, data):
        count = 0
        for location in data.values():
            for prize_list in location["pond"]["possiblePrizes"].values():
                for item in prize_list:
                    if item["type"] == "fish" or item["type"] == "Legendary Fish":
                        count += 1
                        self.journal.append({
                            "id": f"{count:03}",
                            "name": item["name"],
                            "discovered": False,
                            "largest": 0,
                            "type": item["type"],
                            "amountCaught": 0
                        })

    def loadSavedJournal (self, json):
        self.journal = json["player"]["journal"]

    def updateFish (self, id, largest=None):
        self.journal[int(id) - 1]["discovered"] = True
        if largest:
            self.journal[int(id) - 1]["largest"] = largest

    def returnFishInformation (self, id=None, name=None):
        if id is not None:
            return self[int(id) - 1]
        if name is not None:
            for item in self.journal:
                if item["name"] == name:
                    return item
            return None

    def toString (self):
        lines = []
        lines.append("Your Fishing Log: ")
        for entry in self.journal:
            textToPrint = entry["id"] + ": "
            if entry["discovered"]:
                textToPrint += entry["name"]
                if entry["type"] == "Legendary Fish":
                    textToPrint += " (Legendary)"
                textToPrint += " | "
                textToPrint += str(entry["largest"]) + " lbs"
                textToPrint += " (" + str(entry["amountCaught"]) + " caught)"
            else:
                textToPrint += "????"
            lines.append(textToPrint)
        
        return("\n".join(lines) if lines else "No fish in the journal.")

    def returnFullList (self):
        return self.journal