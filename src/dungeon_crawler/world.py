"""World classes - Room (a single location with exits, items, enemies, and allies) and Map (the collection of all rooms, keyed by name)."""

class Room:
    """A single location in the world - holds its own items/enemies/allies, and its exits (including locked and hidden ones) to other rooms."""

    def __init__(self, name: str, description: str = "", examine_text: str = "", required_intellect = 0, is_forge: bool = False):
        """Build an empty room; items/enemies/allies/exits are all populated afterwards via add_*()/connect()/lock_exit() calls."""
        self.name = name
        self.description = description
        self.examine_text = examine_text
        """Extra flavour/hint text shown only via the 'examine' command, distinct from the description shown automatically on room entry."""
        self.required_intellect = required_intellect
        self.exits: dict[str, "Room"] = {}
        self.hidden_exits: dict[str, "Room"] = {}
        """Exits that dont appear in .exits (and therefore not in map/fullmap) until revealed via reveal_hidden_exits()."""
        self.locked_exits: dict[str, str] = {}
        self._items: list = []
        self._enemies: list = []
        self._allies: list = []
        self._companions: list = []
        self.is_forge = is_forge

    def connect(self, direction: str, other_room: "Room") -> None:
        """Add a normal (unlocked, visible) exit from this room to other_room."""
        self.exits[direction] = other_room

    def get_exit(self, direction: str) -> "Room | None":
        """The room in that direction, or None if there's no exit there."""
        return self.exits.get(direction)

    def lock_exit(self, direction: str, required_item_name: str) -> None:
        """Require required_item_name to pass through this exit - see is_exit_locked() in exploration.py, which checks this."""
        self.locked_exits[direction] = required_item_name

    def add_item(self, item):
        """Add item to this room."""
        self._items.append(item)

    def remove_item(self, item):
        """Remove item from this room."""
        self._items.remove(item)

    def add_enemy(self, enemy):
        """Add enemy to this room."""
        self._enemies.append(enemy)

    def remove_enemy(self, enemy):
        """Remove enemy from this room."""
        self._enemies.remove(enemy)

    def add_ally(self, ally):
        """Add ally to this room."""
        self._allies.append(ally)

    def remove_ally(self, ally):
        """Remove ally from this room."""
        self._allies.remove(ally)

    def add_companion(self, companion):
        """Add companion to this room - where a dismissed Companion reappears, see dismiss_companion() in exploration.py."""
        self._companions.append(companion)

    def remove_companion(self, companion):
        """Remove companion from this room."""
        self._companions.remove(companion)

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
        """A copy of this room's items, safe to iterate without exposing the private list."""
        return list(self._items)

    @property
    def enemies(self) -> list:
        """A copy of this room's enemies, safe to iterate without exposing the private list."""
        return list(self._enemies)

    @property
    def allies(self) -> list:
        """A copy of this room's allies, safe to iterate without exposing the private list."""
        return list(self._allies)

    @property
    def companions(self) -> list:
        """A copy of this room's recruitable companions, safe to iterate without exposing the private list."""
        return list(self._companions)

    def __repr__(self) -> str:
        """Debug representation showing the room's name."""
        return f"Room({self.name!r})"

class Map:
    """The full set of rooms in the world (or a floor), keyed by room name."""

    def __init__(self):
        """Start with an empty room collection."""
        self.rooms: dict[str, Room] = {}

    def add_room(self, room: Room) -> None:
        """Add room to the map, keyed by its name."""
        self.rooms[room.name] = room

    def get_room(self, name: str) -> "Room | None":
        """The room with that name, or None if it isn't on the map."""
        return self.rooms.get(name)

    def __len__(self) -> int:
        """Number of rooms currently on the map."""
        return len(self.rooms)
