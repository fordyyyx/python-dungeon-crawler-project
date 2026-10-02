"""World classes - Room (a single location with exits, items, enemies, and allies) and Map (the collection of all rooms, keyed by name)."""
from dataclasses import dataclass
from typing import Callable

class Room:
    """A single location in the world - holds its own items/enemies/allies, and its exits (including locked and hidden ones) to other rooms."""

    def __init__(self, name: str, description: str = "", examine_text: str = "", required_intellect = 0, is_forge: bool = False, is_practice_chamber: bool = False):
        """Build an empty room; items/enemies/allies/exits are all populated afterwards via add_*()/connect()/lock_exit() calls."""
        self.name = name
        self.description = description
        self.examine_text = examine_text
        """Extra flavour/hint text shown only via the 'examine' command, distinct from the description shown automatically on room entry."""
        self.required_intellect = required_intellect
        self.exits: dict[str, "Room"] = {}
        self.hidden_exits: dict[str, "Room"] = {}
        """Exits that don't appear in .exits (and therefore not in map/fullmap) until revealed via reveal_hidden_exit() - by examining the
        room, or by loading a save made after it was examined."""
        self.locked_exits: dict[str, str] = {}
        """direction -> the item needed to pass through it (see is_exit_locked(), exploration.py). The lock is removed for good via
        unlock_exit() the first time the player walks through, so it mutates during play and is part of save data - see save_system.py."""
        self.fast_travel_locks: set[str] = set()
        """Directions on THIS room that can't be used yet - separate from locked_exits (item-gated); these are gated by having used the paired
        exit from the other side at least once (see exit_activations, register_fast_travel_activation()). Like locked_exits, this mutates
        during play, so it's part of save data - see save_system.py."""
        self.exit_activations: dict[str, tuple["Room", str]] = {}
        """direction (on this room) -> (room, direction) to unlock the moment THIS exit is successfully used. Set once at world-build time, never
        mutated during play - same category as the exits themselves: static, not saved."""
        self.guarded_exits: set[str] = set()
        """Directions that can't be used while any living, non-respawning enemy remains in this room - see get_exit_guardian() (exploration.py).
        Static (set at world-build time, never mutated during play), so not saved; the live 'is it still guarded' state
        comes from room.enemies, which already is."""
        self._items: list = []
        self._enemies: list = []
        self._allies: list = []
        self._companions: list = []
        self.is_forge = is_forge
        self.is_practice_chamber = is_practice_chamber
        self.interactions: dict[str, RoomInteraction] = {}
        """Room-specific verbs -> RoomInteraction. Set at world-build time and never saved - like exits. Checked before global commands in main(),
        so a verb must never clash with a core command."""
        self.flags: set[str] = set()
        """Permanent changes an interaction has made to this room (e.g. 'sirens_bargain_taken', 'chest_opened'). Saved, like fast_travel_locks."""
        self.cleared_story_flag: str | None = None
        """A story flag (player.story_flags) to set the first time this room has no living, non-respawning enemies left - e.g. the Throne
        Room's 'suitors_cleared', which makes Odysseus recruitable. Checked after every defeat, so kill order never matters. Set at world-build
        time and never saved; the flag it sets lives on the player, which is."""
        self.cleared_message: str = ""
        """Shown once, when cleared_story_flag is first set."""
        self.transient_state: dict = {}
        """Scratch state for the current visit only - e.g. how far through a puzzle the player is, or where they are in a conversation. Never saved, and cleared by on_leave() whenever the player
        leaves the room - walking out or by dev teleport - so a half-finished puzzle always starts again from scratch."""
        self.advice: str = ""
        """An optional line an advice-giving companion adds in this room, for things get_advice() can't work out from the enemies - a puzzle, a
        trap, a bargain. Set at world-build time; never saved."""
        self.concealed_until: str | None = None
        """A story flag the player must have before this room exists as far as they can tell. Until then, exits leading here are hidden from
        every exit list and map, can't be used ('descend' behaves as though there's nothing there), and nothing - uncleared, the Oracle,
        Tiresias - mentions it. Set at world-build time and never saved; the flag lives on the player, which is. Tartarus uses it to keep the
        real finale secret until Hades falls."""
        self.story_gates: dict[str, StoryGate] = {}
        """direction -> StoryGate. A fourth kind of blocked exit, alongside locked_exits (items), guarded_exits (enemies) and
        fast_travel_locks (shortcuts): shut until the player has made some story decision."""

    def connect(self, direction: str, other_room: "Room") -> None:
        """Add a normal (unlocked, visible) exit from this room to other_room."""
        self.exits[direction] = other_room

    def get_exit(self, direction: str) -> "Room | None":
        """The room in that direction, or None if there's no exit there."""
        return self.exits.get(direction)

    def lock_exit(self, direction: str, required_item_name: str) -> None:
        """Require required_item_name to pass through this exit - see is_exit_locked() in exploration.py, which checks this."""
        self.locked_exits[direction] = required_item_name

    def unlock_exit(self, direction: str) -> None:
        """Permanently remove the item lock on 'direction' - called when the player first walks through it, so a door never re-locks just
        because its key item was later dropped (dropping a key behind its own door used to softlock the game). No-op if the exit isn't locked."""
        self.locked_exits.pop(direction, None)

    def lock_fast_travel_exit(self, direction: str) -> None:
        """Mark 'direction' as locked until the paired exit elsewhere is used - see fast_travel_locks."""
        self.fast_travel_locks.add(direction)

    def register_fast_travel_activation(self, direction: str, unlocks_room: "Room", unlocks_direction: str) -> None:
        """The moment 'direction' on THIS room is successfully used, unlock 'unlocks_direction' on 'unlocks_room'."""
        self.exit_activations[direction] = (unlocks_room, unlocks_direction)

    def guard_exit(self, direction: str) -> None:
        """Block 'direction' until every living, non-respawning enemy in this room is defeated."""
        self.guarded_exits.add(direction)

    def gate_exit(self, direction: str, required_flags: tuple[str, ...], blocked_message: str, map_label: str) -> None:
        """Shut 'direction' until the player has any one of required_flags."""
        self.story_gates[direction] = StoryGate(required_flags, blocked_message, map_label)

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
        """Add an exit that remains invisible until reveal_hidden_exit() is called for its direction."""
        self.hidden_exits[direction] = room

    def reveal_hidden_exit(self, direction: str) -> None:
        """Move a hidden exit into this room's normal exits - the one place that happens, used by examining a room and by loading a save.
        Does nothing if there's no hidden exit in that direction."""
        target = self.hidden_exits.pop(direction, None)
        if target is not None:
            self.exits[direction] = target

    def add_interaction(self, verb: str, handler: Callable[...,str], is_available: Callable[..., bool] | None = None, unavailable_message: str = "Nothing happens.") -> None:
        """Register a verb that only works in this room."""
        self.interactions[verb] = RoomInteraction(
            handler=handler,
            is_available=is_available or (lambda player, room: True),
            unavailable_message=unavailable_message,
        )

    def available_interactions(self, player) -> list[str]:
        """The verbs that currently do something here, in the order they were added."""
        return [verb for verb, interaction in self.interactions.items() if interaction.is_available(player, self)]

    def on_leave(self) -> None:
        """Called whenever the player leaves this room, by any route - walking out or dev teleport. Clears transient_state, so per-visit state
        like a half-finished puzzle always starts fresh on the next visit."""
        self.transient_state.clear()

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

@dataclass
class RoomInteraction:
    """A verb that only works in one room - see Room.add_interaction(). handler performs it and returns the message to show; is_available decides
    whether it currently does anything (an unavailable verb isn't listed in the room, and does nothing if typed). Both receive (player, room).
    Handlers live in each floor's content file, the same data-driven pattern as Enemy.defeat_effect."""

    handler: Callable[..., str]
    is_available: Callable[..., bool] = lambda player, room: True
    unavailable_message: str = "Nothing happens."

@dataclass
class StoryGate:
    """An exit that stays shut until the player has any one of required_flags (see Player.story_flags). blocked_message is shown when they
    try it; map_label appears beside the exit in exit lists and maps. Set at world-build time and never saved - the flags it checks live on
    the player, which are."""

    required_flags: tuple[str, ...]
    blocked_message: str
    map_label: str
