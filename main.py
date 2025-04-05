import json
import platform

INVENTORY_LIMIT = 2
VERSION = "0.2.1"
VALID_DIRECTIONS = ['north', 'east', 'south', 'west', 'up', 'down']

class Item:
    """
    Create an object which represents an item.

    Attributes:
        name: str
            The name of the item.
        description: str
            A brief description of the item.
        location: int
            The location of the item as a map index.
            999 indicates it is in the player's inventory.
        is_held: bool
            Whether the item is held by the player or not.
        provides_light: bool
            Whether the item lights up rooms.
    """

    def __init__(
            self, name: str, description: str, location: int,
            is_held: bool, provides_light: bool
        ) -> None:
        self.name = name
        self.description = description
        self.location = location
        self.is_held = is_held
        self.provides_light = provides_light

class Key(Item):
    """
    Create an object which represents a key.

    Attributes:
        rooms: list[rooms] - A list of rooms the key can unlock as map indices.
    """

    def __init__(
            self, name: str, description: str, location: int,
            is_held: bool, provides_light: bool,
            rooms_unlocked = list[int]
        ) -> None:
        Item.__init__(
            self,
            name,
            description,
            location,
            is_held,
            provides_light
        )
        self.rooms_unlocked = rooms_unlocked
        

class Room:
    """
    Create an object which represents a room.

    Attributes:
        number: int - The unique identifier of the room.
        name: str - The name of the room.
        description: str - A brief description of the room.
        is_lit: bool - Whether the room is lit or not.
        is_locked: bool - Whether the room is locked or not.
        exits (dict[str, int])
            A dictionary mapping directions to room numbers.
    """

    def __init__(
            self, number: int, name: str, description: str,
            is_lit: bool, is_locked: bool, exits: dict[str, int]
        ) -> None:
        self.number = number
        self.name = name
        self.description = description
        self.is_lit = is_lit
        self.is_locked = is_locked
        self.exits = exits

def show_help() -> None:
    """Shows help message, including version and system information."""
    print(f"Version: {VERSION}")
    print(f"OS: {platform.system()} {platform.release()} " +
          f"{platform.version()}")
    print(f"Python: {platform.python_version()} " +
          f"({platform.python_branch()}:" +
          f"{platform.python_revision()})")

    print()
    print("look - shows room name and description.")
    print("go <direction: str> - travels in the specified direction.")
    print("pickup <item: str> - picks up the item.")
    print("drop <item: str> - drops the item.")
    print("inventory - shows inventory.")
    print("leave - leaves house (only works at entrance).")
    print("help - show this help message.")

def check_key(room_number: int, items: list[Item]) -> bool:
    for item in items:
        if (isinstance(item, Key) and item.location == 999):
            if room_number in item.rooms_unlocked:
                return True
    return False

def format_passages(exits: dict[str, int]) -> str:
    if not exits:
        return "There are no visible exits from the room."

    directions = []
    for direction in exits:
        directions.append(direction)
    
    if len(directions) == 1:
        return f"There is a passage out of the room going {directions[0]}."
    elif len(directions) == 2:
        return f"There are passages out of the room going {directions[0]} and {directions[1]}."
    else:
        all_but_last = ", ".join(directions[:-1])
        return f"There are passages out of the room going {all_but_last} and {directions[-1]}."

def get_new_room_number(
        game_map: dict, current_room_num: int,
        direction: str
    ) -> int:
    
    direction = direction.lower()

    if direction not in VALID_DIRECTIONS:
        print(f"'{direction}' is not a valid direction.")
        return -1

    current_room = game_map[current_room_num]

    if direction in current_room.exits:
        return current_room.exits[direction]
    else:
        print(f"You can't go {direction} from here.")
        return -1

    
def create_item(location: int, item_data: dict) -> Item:
    if item_data["type"] == "Item":
        return Item(
            name=item_data["name"],
            description=item_data["description"],
            location=location,
            is_held=item_data["is_held"],
            provides_light=item_data["provides_light"]
        )
    elif item_data["type"] == "Key":
        return Key(
            name=item_data["name"],
            description=item_data["description"],
            location=location,
            is_held=item_data["is_held"],
            provides_light=item_data["provides_light"],
            rooms_unlocked=item_data.get("rooms_unlocked", [])
        )
    else:
        raise ValueError(f"Unknown item type: {item_data['type']}")

def get_map_data(mapfile: str) -> tuple:
    """
    Loads map data from a JSON file.

    Parameters:
    mapfile: str
    The file to load the map data from.

    Returns:
    tuple
        Contains two lists: rooms and metadata.
        rooms: list[Room] - contains the map data.
        metadata: dict[str, str] - contains the entrance room number.
    """
    with open(mapfile, 'r') as f:
        data = json.load(f)

    valid_data_versions = [2]
    rooms = []
    items = []
    metadata = {"data_version": data['data_version'],
                "entrance_room": data['entrance_room'],
                "spawn_room": data['spawn_room']}

    if metadata['data_version'] not in valid_data_versions:
        print("Error: Incompatible map data.")
        input("Press [Enter] to quit")
        quit()

    for room_data in data['room_data']:
        room = Room(
            number=room_data['number'],
            name=room_data['name'],
            description=room_data['description'],
            is_lit=room_data['lit'],
            is_locked=room_data['locked'],
            exits=room_data['exits']
        )
        rooms.append(room)

        for item_data in room_data.get("items", []):
            item = create_item(room_data['number'], item_data)
            items.append(item)
    
    return rooms, items, metadata

def main() -> None:
    print()

    game_map, items, metadata = get_map_data("map.json")
    leave = False
    current_room = metadata['spawn_room']
    entrance_room = metadata['entrance_room']
    items_held = 0

    def describe_room():
        player_light = any(item.provides_light
                           and item.location == 999 for item in items)
        if not game_map[current_room].is_lit and not player_light:
            print("This is a dark room. You can't see anything.")
        else:
            print(game_map[current_room].name)
            print(game_map[current_room].description)

            for item in items:
                if item.location == current_room:
                    print(f"There is a {item.name} here.")

            print(format_passages(game_map[current_room].exits))

    def show_inventory():
        is_carrying_nothing = True
        print("You are carrying:")
        for item in items:
            if item.location == 999:
                print(f"- {item.name}")
                is_carrying_nothing = False
        if is_carrying_nothing:
            print("Nothing")
        print()

    describe_room()

    while not leave:
        command = input("> ").strip().lower().split()

        if not command:
            print("Enter 'help' for help.")
            continue

        if command[0] == "look":
            describe_room()

        elif command[0] == "inventory":
            show_inventory()

        elif command[0] == "pickup":
            if len(command) < 2:
                print("Pickup what?")
                continue
            item_name = " ".join(command[1:])
            for item in items:
                if (item.location == current_room
                    and item.name.lower() == item_name):
                    if items_held < INVENTORY_LIMIT:
                        item.location = 999
                        items_held += 1
                        print(f"You picked up the {item.name}.")
                    else:
                        print("You're carrying too much.")
                    break
            else:
                print("No such item here.")

        elif command[0] == "drop":
            if len(command) < 2:
                print("Drop what?")
                continue
            item_name = " ".join(command[1:])
            for item in items:
                if (item.location == 999
                    and item.name.lower() == item_name):
                    item.location = current_room
                    items_held -= 1
                    print(f"You dropped the {item.name}.")
                    break
            else:
                print("You're not carrying that.")

        elif command[0] == "go":
            if len(command) < 2:
                print("Go where?")
                continue
            direction = command[1]
            new_room_number = get_new_room_number(game_map, current_room, direction)

            if new_room_number == -1:
                continue

            if (game_map[new_room_number].is_locked
                and not check_key(new_room_number, items)):
                print("This room is locked. You need a key.")
                continue

            current_room = new_room_number
            describe_room()

            if current_room == entrance_room:
                print("You have reached the entrance. Type 'leave' to exit.")

        elif command[0] == "leave":
            if current_room == entrance_room:
                leave = True
                break
            else:
                print("You can't leave from here.")

        elif command[0] == "help":
            show_help()

        else:
            print("Unknown command. Enter 'help' for commands.")

    print("The door opens, revealing the night sky outside.")
    print("You have escaped.")
    input("Press [Enter] to exit and quit")

if __name__ == "__main__":
    main()
