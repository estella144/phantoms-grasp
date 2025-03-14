import json

INVENTORY_LIMIT = 2
VERSION = "0.2.0.dev4"

class Item:
    """
    Create an object which represents an item.

    Attributes:
        name: str - The name of the item.
        description: str - A brief description of the item.
        location: int - The location of the item as a map index.
        999 indicates it is in the player's inventory.
        is_held: bool - Whether the item is held by the player or not.
        provides_light: bool - Whether the item lights up rooms.
    """

    def __init__(
            self, name: str, description: str, location: int,
            is_held: bool, provides_light: bool) -> None:
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
            rooms_unlocked = list[int]) -> None:
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

def check_key(room_number: int, items: list[Item]):
    for item in items:
        if (isinstance(item, Key) and item["location"] == 999):
            if room_number in item["unlocks"]:
                return True
    return False

def get_new_room_number(map_length: int) -> int:
    """
    Requests a room number (map index) and validates it.
    Returns the desired room number if it is valid, and -1 otherwise.
    """

    try:
        new_room_number = int(input("Go to a room number: "))
        if new_room_number < 0:
            print("That's not a positive whole number!")
            return -1
    except ValueError:
        print("That's not a positive whole number!")
        return -1
    
    if new_room_number >= map_length:
        print("There is no room with that number!")
        return -1
    
    return new_room_number
    
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

        print(room_data.get("items", []))
        for item_data in room_data.get("items", []):
            item = create_item(room_data['number'], item_data)
            items.append(item)
    
    return rooms, items, metadata

def main() -> None:
    """Main game loop."""
    print()
    
    game_map, items, metadata = get_map_data("map.json")
    leave = False
    current_room = metadata['spawn_room']
    entrance_room = metadata['entrance_room']
    items_held = 0
    
    while not leave:

        print(items)
        player_light = False
        for item in items:
            if (item.provides_light == True
                and item.location == 999):
                player_light = True
        
        if (game_map[current_room].is_lit == False
            and player_light == False):
            print("This is a dark room, you can't see anything.")
        else:
            print(game_map[current_room].name)
            print(game_map[current_room].description)
            for item in items:
                if item.location == current_room:
                    print(f"There is a {item.name} in the room.")
                    pick_up = input("Pick up the item? [Y/N]").lower()
                    if pick_up == "y":
                        items[items.index(item)].location = 999
                        items_held += 1

        if current_room == 0:
            choice = input("You have reached the entrance.",
                           "Do you want to leave?",
                           "[Y/N, default: N] ").upper()
            if choice == "Y":
                leave = True
                break
        
        new_room_number = get_new_room_number(len(game_map))
        
        if new_room_number != -1:
            # -1 indicates an invalid input
            if (game_map[new_room_number].is_locked == True
                and check_key(new_room_number, items) == False):
                print("This room is locked. Find a key to unlock it.")
                continue
            current_room = new_room_number

    print("The door opens, revealing the night sky outside.")
    print("You have escaped.")
    input("Press [Enter] to exit and quit")

if __name__ == "__main__":
    main()
