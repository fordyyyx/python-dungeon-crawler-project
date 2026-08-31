class Room:
    def __init__(self, name: str, description: str = "", examine_text: str = ""):
        self.name = name
        self.description = description
        self.examine_text = examine_text
        """Extra flavour/hint text shown only via the 'examine' command, distinct from the description shown automatically on room entry."""
        self.exits: dict[str, "Room"] = {}
        self.hidden_exits: dict[str, "Room"] = {}
        """Exits that dont appear in .exits (and therefore not in map/fullmap) until revealed via reveal_hidden_exits()."""
        self.locked_exits: dict[str, str] = {}
        self._items: list = []
        self._enemies: list = []
        self._allies: list = []

    def connect(self, direction: str, other_room: "Room") -> None:
        self.exits[direction] = other_room

    def get_exit(self, direction: str) -> "Room | None":
        return self.exits.get(direction)

    def lock_exit(self, direction: str, required_item_name: str) -> None:
        self.locked_exits[direction] = required_item_name

    def add_item(self, item):
        self._items.append(item)

    def remove_item(self, item):
        self._items.remove(item)

    def add_enemy(self, enemy):
        self._enemies.append(enemy)

    def remove_enemy(self, enemy):
        self._enemies.remove(enemy)

    def add_ally(self, ally):
        self._allies.append(ally)

    def remove_ally(self, ally):
        self._allies.remove(ally)

    def add_hidden_exit(self, direction: str, room: "Room") -> None:
        """Add an exit that remains invisible until reveal_hidden_exits() is called."""
        self.hidden_exits[direction] = room

    def reveal_hidden_exits(self) -> list[str]:
        """Promote every hidden exit into the normal exits dict. Returns the list of directions revealed, empty if there was nothing to
        reveal - the caller uses this to decide whether to print a discovery message."""
        revealed = list(self.hidden_exits.keys())
        for direction, room in self.hidden_exits.items():
            self.exits[direction] = room
        self.hidden_exits.clear()
        return revealed

    @property
    def items(self) -> list:
        return list(self._items)

    @property
    def enemies(self) -> list:
        return list(self._enemies)

    @property
    def allies(self) -> list:
        return list(self._allies)

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
