import json

class Room:
    """Create an object which represents a room."""

    def __init__(self, number: int, name: str, description: str, lit: bool,
                 locked: bool, exits: dict[str, int]) -> None:
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
    -----------

    mapfile : str
    The file to load the map data from.#

    Returns:
    -------

    tuple
        Contains two lists: rooms and metadata.
        rooms: list[Room] - contains the map data.
        metadata: dict[str, str] - contains the entrance room number."""
    with open(mapfile, 'r') as f:
        data = json.load(f)

    valid_data_versions = [1]
    rooms = []
    metadata = {"entrance_room": data['entrance_room']}
    
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
    game_map, metadata = get_map_data("map.json")
    print(game_map)
    leave = False
    current_room = 0
    while not leave:
        if game_map[current_room].lit == False:
            print("This is a dark room, you can't see anything.")
        else:
            print(game_map[current_room].name)
            print(game_map[current_room].description)
        new_room_number = int(input("Go to a room number: "))
        try:
            new_room = game_map[new_room_number]
        except IndexError:
            print("There is no room with that number!")
            continue
        if new_room.locked == True:
            print("This room is locked. You can't go in there!")
        else:
            current_room = new_room_number

if __name__ == "__main__":
    main()
