class Room:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.exits: dict[str, "Room"] = {}
        self.items: list = []
        self.enemies: list = []

    def connect(self, direction: str, other_room: "Room") -> None:
        self.exits[direction] = other_room

    def get_exit(self, direction: str) -> "Room | None":
        return self.exits.get(direction)

    def __repr__(self) -> str:
        return f"Room({self.name!r})"

class Map:
    def __init__(self):
        self.rooms: dict[str, Room] = {}

    def add_room(self, room: Room) -> None:
        self.rooms[room.name] = room

    def get_room(self, name: str) -> "Room | None":
        return self.rooms.get(name)

    def __len__(self) -> int:
        return len(self.rooms)
