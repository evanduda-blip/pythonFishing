import msvcrt
import time
from colorama import Fore, Style, init
import random
import pygame
import os
import json
import threading
import sys
from pathlib import Path


def _get_project_directories():
    script_dir = Path(__file__).resolve().parent
    project_dirs = [script_dir]
    markers = ("gameData.json", "modules", "assets", "data", "audio")

    for directory in script_dir.parents:
        has_module_files = (directory / "player.py").is_file() and (
            directory / "locationMaker.py"
        ).is_file()
        if has_module_files or any((directory / marker).exists() for marker in markers):
            project_dirs.append(directory)

    return project_dirs


def _add_module_search_path():
    for project_dir in _get_project_directories():
        for module_dir in (
            project_dir,
            project_dir / "modules",
            project_dir / "src",
            project_dir / "src" / "modules",
        ):
            if all(
                (module_dir / module_name).is_file()
                for module_name in ("locationMaker.py", "player.py")
            ):
                module_path = str(module_dir)
                if module_path not in sys.path:
                    sys.path.insert(0, module_path)
                return

    raise ModuleNotFoundError(
        "Could not find locationMaker.py and player.py. Keep them together "
        "or place both in a modules/ folder."
    )


_add_module_search_path()
import locationMaker
import player

init(autoreset=True)
pygame.mixer.init()

def get_save_game_path(filename="user_data.json"):
    app_data_dir = os.getenv("APPDATA")
    if not app_data_dir:
        app_data_dir = os.path.expanduser("~")

    game_folder = os.path.join(app_data_dir, "MyAwesomePythonGame")

    if not os.path.exists(game_folder):
        os.makedirs(game_folder)
    return os.path.join(game_folder, filename)

def load_game_data():
    path = get_save_game_path()

    if not os.path.exists(path):
        changePlayerMap(data["hub"])
        person.fishingJournal = populateJournal()
        return
    with open(path, "r") as file:
        changePlayerMap(data["hub"])
        oldData = json.load(file)
        person.changeMap(oldData["location"])
        person.row = oldData["player"]["position"]["row"]
        person.col = oldData["player"]["position"]["col"]
        person.money = oldData["player"]["money"]
        person.fishingJournal = oldData["player"]["journal"]
        person.fishingRod = oldData["player"]["fishingRod"]
        person.inventory = oldData["player"]["inventory"]

def save_game_data():
    data = {
    "location": person.currentMap,
    "player": {
        "position": {
            "row": person.row,
            "col": person.col
        },
        "money": person.money,
        "fishingRod": person.fishingRod,
        "inventory":person.inventory,
        "journal":person.fishingJournal
    }
    }
    path = get_save_game_path()
    with open(path, "w") as file:
        json.dump(data, file, indent=4)

def get_asset_path(relative_path):
    """Find an asset beside the script or in a standard resource folder."""
    asset_path = Path(relative_path)
    if getattr(sys, 'frozen', False):
        search_dirs = [Path(sys._MEIPASS)]
    else:
        search_dirs = _get_project_directories()

    if asset_path.is_absolute():
        if asset_path.is_file():
            return str(asset_path)
        raise FileNotFoundError(f"Asset not found: {asset_path}")

    resource_folders = ("assets", "data", "audio")
    for directory in search_dirs:
        candidates = [directory / asset_path]
        candidates.extend(
            directory / folder / asset_path for folder in resource_folders
        )
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)

    if asset_path.parent == Path("."):
        matches = []
        for directory in search_dirs:
            for folder in resource_folders:
                resource_dir = directory / folder
                if resource_dir.is_dir():
                    matches.extend(
                        path
                        for path in resource_dir.rglob(asset_path.name)
                        if path.is_file()
                    )

        matches = list(dict.fromkeys(matches))
        if len(matches) == 1:
            return str(matches[0])
        if len(matches) > 1:
            raise ValueError(
                f"Asset name is ambiguous; provide its folder: {relative_path}"
            )

    searched_locations = ", ".join(str(directory) for directory in search_dirs)
    raise FileNotFoundError(
        f"Asset not found: {relative_path}. Searched: {searched_locations} "
        "and their assets/, data/, and audio/ folders."
    )


global data
with open(get_asset_path("gameData.json"), "r") as file:
    data = json.load(file)

colors = {
    "0": Style.NORMAL + Fore.GREEN,
    "1": Style.BRIGHT + Fore.CYAN,
    "2": Style.NORMAL + Fore.CYAN,
    "3": Style.BRIGHT + Fore.BLUE,
    "4": Style.NORMAL + Fore.BLUE,
    "5": Style.DIM + Fore.BLUE,
    "P": Style.NORMAL + Fore.RED,
    "w": Style.NORMAL + Fore.BLUE,
    "B": Style.NORMAL + Fore.GREEN,
    "*": Style.NORMAL + Fore.YELLOW,
    "|": Style.NORMAL + Fore.WHITE,
    "S": Style.DIM + Fore.RED,
    "H": Fore.YELLOW
}

def playSoundEffect(sound):
    pygame.mixer.music.set_volume(0.25)
    sound.play()

    def restoreMusicVolume():
        while pygame.mixer.get_busy():
            time.sleep(0.01)
        pygame.mixer.music.set_volume(1.0)

    threading.Thread(target=restoreMusicVolume, daemon=True).start()


def randomCenterWeighted(firstValue, secondValue):
    minValue = min(firstValue, secondValue)
    maxValue = max(firstValue, secondValue)
    center = (minValue + maxValue) / 2
    return random.triangular(minValue, maxValue, center)


def getLineSnapChance(depth):
    pondMap = person.currentMap["pond"]["map"]
    rodStrength = float(person.fishingRod.get("strength", 1.0))
    currentDepth = int(pondMap[depth][0])

    if rodStrength >= currentDepth:
        return 0

    breakChance = 0
    for row in pondMap[:depth + 1]:
        if int(row[0]) > rodStrength:
            breakChance += 0.1

    return breakChance


def checkList2D (array, row, col):
    if 0 <= row < len(array):
        if 0 <= col < len(array[row]):
            return True
    return False

def checkSurrounding (array, row, col, item):
    if checkList2D(array, row + 1, col) and array[row + 1][col] == item:
        return True
    if checkList2D(array, row - 1, col) and array[row - 1][col] == item:
        return True
    if checkList2D(array, row, col - 1) and array[row][col - 1] == item:
        return True 
    if checkList2D(array, row, col + 1) and array[row][col + 1] == item:
        return True
    return False

def getCurrentPosition(board, item):
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == item:
                return row, col
    return None

def updateBoard (currentBoard, line_positions=None):
    line_positions = line_positions or {}
    for i, item in enumerate(currentBoard):
        row = ""
        for j, item2 in enumerate(item):
            cell = item2
            if i == person.row and j == person.col and not person.inPond:
                cell = "P"
            if person.inPond and i == 0 and j == person.bobberCol:
                cell = "B"
            if (i, j) in line_positions:
                cell = "|"
            if (person.inPond and i > 0 and person.currentMap["pond"]["prizes"][i][j] != "0" and (i, j) not in line_positions):
                cell = "*"

            if cell == "S":
                color = Style.DIM + Fore.RED
            else:
                color = colors.get(str(cell), Style.NORMAL + Fore.GREEN)

            row += color + str(cell) + " " + Style.RESET_ALL
        print(row)

    if not person.inPond:
        stringToPrint = "Current Rod: " + person.fishingRod["name"] + "\n"
        for i, item in enumerate(person.inventory):
            weightText = " | " + str(item["weight"]) + " lbs" if "weight" in item else ""
            stringToPrint += str(i + 1) + ". " + item["name"] + weightText + "\n"
        stringToPrint += "Current Money: $" + str(person.money)
        print_in_box(stringToPrint)

def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')

def moveNorth (board):
    if checkList2D(board, person.row - 1, person.col) and board[person.row - 1][person.col] != "w":
        person.row -= 1
        
def moveSouth (board):
    if checkList2D(board, person.row + 1, person.col) and board[person.row + 1][person.col] != "w":
        person.row += 1

def moveWest (board):
    if (checkList2D(board, person.row, person.col - 1) and board[person.row][person.col - 1] != "w"):
        person.col -= 1

def moveEast (board):
    if (checkList2D(board, person.row, person.col + 1) and board[person.row][person.col + 1] != "w"):
        person.col += 1

def changePlayerMap (map):
    if map["map"] == "hub":
        hub = locationMaker.newLocation()
        hub.newLocationBlank(20,20)
        hub.addLocalPond()
        hub.addShop()
        hub.addHouse()
        map["map"] = hub.returnArea()

    if "pond" in map and isinstance(map["pond"]["map"], dict):
        pondConfig = map["pond"]["map"]
        pond = locationMaker.newLocation().newPond(
            pondConfig["row"],
            pondConfig["col"],
            pondConfig["depth"]
        )
        map["pond"]["map"] = pond

    person.changeMap(map)


def main():
    clearConsole()
    
    global person
    load_game_data()
    
    updateBoard(person.currentMap["map"])
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'w':
                moveNorth(person.currentMap["map"])
            elif key == b's':
                moveSouth(person.currentMap["map"])
            elif key == b'd':
                moveEast(person.currentMap["map"])
            elif key == b'a':
                moveWest(person.currentMap["map"])
            elif key == b'q':
                pygame.mixer.music.stop()
                save_game_data()
                break
            elif key == b' ':
                if checkSurrounding(person.currentMap["map"], person.row, person.col, "w"):
                    fishingMinigame()
                    
                if checkSurrounding(person.currentMap["map"], person.row, person.col, "S"):
                    shop()

                if checkSurrounding(person.currentMap["map"], person.row, person.col, "H"):
                    printJournal()

            clearConsole()
            updateBoard(person.currentMap["map"])

def hookAnimation (targetRow):
    board = person.currentMap["pond"]["map"] if person.inPond else person.currentMap["map"]
    prizes = person.currentMap["pond"]["prizes"]
    for row in range(1, targetRow):
        line_positions = {(r, person.bobberCol): "|" for r in range(1, row + 1)}
        snapChance = getLineSnapChance(row)
        connectedToPrize = (
            checkList2D(prizes, row + 1, person.bobberCol)
            and prizes[row + 1][person.bobberCol] != "0"
        )
        if not connectedToPrize and random.random() < snapChance:
            clearConsole()
            updateBoard(board, line_positions)
            print("Your line snapped!")
            time.sleep(1.5)
            person.inPond = False
            return False
        clearConsole()
        updateBoard(board, line_positions)
        time.sleep(.25)
    return True

def dropHook():
    targetRow = None
    for row in range(1, len(person.currentMap["pond"]["prizes"])):
        if person.currentMap["pond"]["prizes"][row][person.bobberCol] != "0":
            targetRow = row
            break

    if targetRow is not None:
        if not hookAnimation(targetRow):
            return

        prize = person.currentMap["pond"]["prizes"][targetRow][person.bobberCol]
        if isinstance(prize, dict):
            print("You got a: " + prize["name"])
            caughtPrize = prize.copy()                
            caughtPrize["value"] = round(caughtPrize["value"] * person.fishingRod.get("valueMultiplier", 1.0), 2)
            if "minWeight" in caughtPrize and "maxWeight" in caughtPrize:
                caughtPrize["weight"] = round(randomCenterWeighted(caughtPrize["minWeight"], caughtPrize["maxWeight"]), 2)
                del caughtPrize["minWeight"]
                del caughtPrize["maxWeight"]
            person.inventory.append(caughtPrize)
            if caughtPrize["type"] == "fish" or caughtPrize["type"] == "Legendary Fish":
                if not person.fishingJournal[findValue(person.fishingJournal, "name", caughtPrize["name"])]["discovered"]:
                    
                    if caughtPrize["type"] == "Legendary Fish":
                        playSoundEffect(legendaryFish)
                    else:
                        playSoundEffect(newItem)
                else:
                    playSoundEffect(normalItem)
                person.fishingJournal[findValue(person.fishingJournal, "name", caughtPrize["name"])]["discovered"] = True
                if person.fishingJournal[findValue(person.fishingJournal, "name", caughtPrize["name"])]["largest"] < caughtPrize["weight"]:
                    person.fishingJournal[findValue(person.fishingJournal, "name", caughtPrize["name"])]["largest"] = caughtPrize["weight"]
        else:
            print("You got a prize!")
        time.sleep(2)
        person.inPond = False
        return
    else:
        print("No prize under the bobber.")
        time.sleep(1)
        person.inPond = False
        return

def print_in_box(text):
    lines = text.split('\n')
    max_len = max(len(line) for line in lines)
    
    border = "+" + "-" * (max_len + 2) + "+"
    
    print(border)
    for line in lines:
        print(f"| {line.ljust(max_len)} |")
    print(border)

def createPrizes(array):
    array["prizes"] = [["0" for _ in range(len(array["map"][0]))] for _ in range(len(array["map"]))]
    for col in range(len(array["map"][0])):
        if random.randint(1, 2) == 1:
            prizeRows = range(1, len(array["map"]))
            rowWeights = range(len(array["map"]) - 1, 0, -1)
            prizeRow = random.choices(prizeRows, weights=rowWeights, k=1)[0]
            prizeTier = int(array["map"][prizeRow][col])
            prizePool = person.currentMap["pond"]["possiblePrizes"].get(str(prizeTier), [])
            if prizePool:
                prize = prizePool[random.randint(0, len(prizePool) - 1)]
                array["prizes"][prizeRow][col] = prize

def fishingMinigame():
    clearConsole()
    person.inPond = True
    createPrizes(person.currentMap["pond"])
    updateBoard(person.currentMap["pond"]["map"])

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'q':
                break
            if key == b' ':
                dropHook()
                break

        if 0 <= person.bobberDirection + person.bobberCol < len(person.currentMap["pond"]["map"][0]):
            person.bobberCol += person.bobberDirection
        else:
            person.bobberDirection *= -1
        time.sleep(0.25)
        clearConsole()
        updateBoard(person.currentMap["pond"]["map"])

def shop():
    clearConsole()
    print(person.currentMap["shop"]["image"])
    print(person.currentMap["shop"]["greeting"])
    currentSelection = 0
    printListSelection(currentSelection)
    
    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
    
            if key == b"w":
                if currentSelection - 1 != -1:
                    currentSelection -= 1
                    printListSelection(currentSelection)
            if key == b's':
                if currentSelection + 1 != len(person.currentMap["shop"]["options"]):
                    currentSelection += 1
                    printListSelection(currentSelection)
            if key == b' ':
                break

    if currentSelection == 0:
        clearConsole()
        if "rods" in person.currentMap["shop"]["inventory"]:
            if len(person.currentMap["shop"]["inventory"]["rods"]["stock"]) > 0:
                print("Which rod would you like to buy? (You have $" + str(person.money) + ")")
                for i, item in enumerate(person.currentMap["shop"]["inventory"]["rods"]["stock"]):
                    print(str(i + 1) + ": " + item["name"] + " | Cost: $" + str(item["cost"]) + " (Strength: " + str(item["strength"]) + ", Value Mulitpler: " + str(item["valueMultiplier"]) + ")")
                userSelection = int(input("Enter the number you want to purchase: ")) - 1
                if person.money > person.currentMap["shop"]["inventory"]["rods"]["stock"][userSelection]["cost"]:
                    person.money -= person.currentMap["shop"]["inventory"]["rods"]["stock"][userSelection]["cost"]
                    person.fishingRod = person.currentMap["shop"]["inventory"]["rods"]["stock"][userSelection]
                else:
                    print("You have no money to spend")
    elif currentSelection == 1:
        currentSelectedItems = ["- "] * len(person.inventory)
        currentSelectionSell = 0
        updateSellList(currentSelectionSell, currentSelectedItems)
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()

                if key == b'w':
                    if currentSelectionSell - 1 != -1:
                        currentSelectionSell -= 1
                        updateSellList(currentSelectionSell, currentSelectedItems)
                if key == b's':
                    if currentSelectionSell + 1 != len(person.inventory):
                        currentSelectionSell += 1
                        updateSellList(currentSelectionSell, currentSelectedItems)
                if key == b' ':
                    currentSelectedItems[currentSelectionSell] = "* "
                    updateSellList(currentSelectionSell, currentSelectedItems)
                if key == b'e':
                    remaining_items = []
                    for item, selection in zip(person.inventory, currentSelectedItems):
                        if selection == "* ":
                            person.money += item["value"]
                        else:
                            remaining_items.append(item)

                    person.inventory = remaining_items
                    break

def updateSellList(currentPosition, selectedItems):
    clearConsole()
    print("Here are you items you can sell: ")
    for i, (item, selection) in enumerate(zip(person.inventory, selectedItems)):
        if i == currentPosition:
            print("> " + item["name"])
        else:
            print(selection + item["name"])
    
def printListSelection (index):
    clearConsole()
    print(person.currentMap["shop"]["image"])
    print(person.currentMap["shop"]["greeting"])
    for i, item in enumerate(person.currentMap["shop"]["options"]):
        if index == i:
            print("> " + item)
        else:
            print("- " + item)

def printJournal():
    clearConsole()
    lines = []
    lines.append("Your Fishing Log: ")
    for entry in person.fishingJournal:
        textToPrint = entry["id"] + ": "
        if entry["discovered"]:
            textToPrint += entry["name"]
            if entry["type"] == "Legendary Fish":
                textToPrint += " (Legendary)"
            textToPrint += " | "
            textToPrint += str(entry["largest"]) + " lbs"
        else:
            textToPrint += "????"
        lines.append(textToPrint)

    print_in_box("\n".join(lines) if lines else "No fish in the journal.")

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b' ':
                break
    
#Requires a list of objects
def findValue (list, key, valueToFind):
    for i,object in enumerate(list):
        if object[key] == valueToFind:
            return i

def populateJournal():
    journal = []
    count = 0
    for location in data.values():
        for prize_list in location["pond"]["possiblePrizes"].values():
            for item in prize_list:
                if item["type"] == "fish" or item["type"] == "Legendary Fish":
                    count += 1
                    journal.append({
                        "id": f"{count:03}",
                        "name": item["name"],
                        "discovered": False,
                        "largest": 0,
                        "type": item["type"]
                    })
    return journal

if __name__ == "__main__":
    global person
    person = player.player()
    pygame.mixer.music.load(get_asset_path("02. Overworld of Hyrule.mp3"))
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play(-1)
    normalItem = pygame.mixer.Sound(get_asset_path("04. Small Item Get.mp3"))
    legendaryFish = pygame.mixer.Sound(get_asset_path("07. Collect Item.mp3"))
    newItem = pygame.mixer.Sound(get_asset_path("06. Secret.mp3"))
    main()


"""
{

    "id":"001",
    "name":"Sunfish",
    "type":"Normal",
    "Largest":11

}

"""