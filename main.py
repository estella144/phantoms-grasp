import json

VERSION = "0.2.0.dev1"

class Item:
    """
    Create an object which represents an item.

    Attributes:
        name: str - The name of the item.
        description: str - A brief description of the item.
        location: int - The location of the item as a map index.
        -1 indicates it is in the player's inventory.
        is_held: bool - Whether the item is held by the player or not.
    """

    def __init__(
            self, name: str, description: str, location: int,
            is_held: bool) -> None:
        self.description = description
        self.location = location
        self.is_held = is_held

class Key(Item):
    """
    Create an object which represents a key.

    Attributes:
        rooms: list[rooms] - A list of rooms the key can unlock as map indices.
    """

    def __init__(
            self, name: str, description: str, location: int,
            is_held: bool, rooms = list[int]) -> None:
        Item.__init__(self, name, description, location, is_held)
        self.rooms = rooms

class Room:
    """
    Create an object which represents a room.

    Attributes:
        number: int - The unique identifier of the room.
        name: str - The name of the room.
        description: str - A brief description of the room.
        is_lit: bool - Whether the room is lit or not.
        is_locked: bool - Whether the room is locked or not.
        exits (dict[str, int]): A dictionary mapping directions to room numbers.
    """

    def __init__(
            self, number: int, name: str, description: str, is_lit: bool,
            is_locked: bool, exits: dict[str, int]) -> None:
        self.number = number
        self.name = name
        self.description = description
        self.lit = lit
        self.locked = locked
        self.exits = exits

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

    valid_data_versions = [1]
    rooms = []
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
            lit=room_data['lit'],
            locked=room_data['locked'],
            exits=room_data['exits']
        )
        rooms.append(room)
    
    return rooms, metadata

def main() -> None:
    """Main game loop."""
    print()
    
    game_map, metadata = get_map_data("map.json")
    leave = False
    current_room = metadata['spawn_room']
    entrance_room = metadata['entrance_room']
    
    while not leave:
        if game_map[current_room].lit == False:
            print("This is a dark room, you can't see anything.")
        else:
            print(game_map[current_room].name)
            print(game_map[current_room].description)

        if current_room == 0:
            choice = input("You have reached the entrance. Do you want to leave? [Y/N, default: N] ").upper()
            if choice == "Y":
                leave = True
                break

        try:
            new_room_number = int(input("Go to a room number: "))
            if new_room_number < 0:
                print("That's not a positive whole number!")
                continue
        except ValueError:
            print("That's not a positive whole number!")
            continue
        
        try:
            new_room = game_map[new_room_number]
        except IndexError:
            print("There is no room with that number!")
            continue
        
        if new_room.locked == True:
            print("This room is locked. You can't go in there!")
            continue
        current_room = new_room_number

    print("The door opens, revealing the night sky outside.")
    print("You have escaped.")
    input("Press [Enter] to exit and quit")

if __name__ == "__main__":
    main()
