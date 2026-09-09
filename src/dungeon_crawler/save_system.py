"""Save/load system - profile and slot management, JSON persistence for Player state and per-room deltas. See roadmap.md's
Save/load system item for the full design.

Scope note: this module owns serialisation/deserialisation and file I/O only. The title screen, main()'s save/load/autosave
commands, and the active-slot session stats are deliberately not built here - see roadmap.md.

Every room currently gets a full snapshot, not just changed ones - the "only serialise changed rooms" optimisation from roadmap.md
needs real change-tracking (a Room.touched flag or similar) to do properly, which is out of scope for this pass. JSON size for a text-game map
is trivial, so this is a safe simplification, not a shortcut that needs revisiting urgently."""

import json
import os

from dungeon_crawler.characters import Player
from dungeon_crawler.world import Map, Room
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.items import Armour
from dungeon_crawler.dev_tools import find_item_by_name, find_spell_by_name, find_companion_by_name

PROFILE_LIMIT = 3
SAVE_SLOTS_PER_PROFILE = 5
SAVES_DIR = "saves"

ABILITY_FLAG_NAMES = [
    "has_double_strike", "has_last_stand", "has_thorns", "has_reckless_strength", "has_measured_casting", "has_swift_feet",
    "has_unyielding_tide", "has_berserking", "has_silver_tongue", "can_ranged_without_weapon", "has_petrifying_gaze", "has_bull_rush",
    "has_iron_hide",
]
"""The 13 boolean ability flags (4 skill-tree + 9 secondary-ancestry... actually 10, see characters.py) that need saving directly by name
- dodge_chance is numeric, handled as its own field instead."""


def slot_path(profile_num: int, slot_num: int) -> str:
    """Path to a given profile/slots's save file e.g. saves/profile_1/slot_3.json, Does not create anything - see ensure_profile_dir()."""
    return os.path.join(SAVES_DIR, f"profile_{profile_num}", f"slot_{slot_num}.json")

def ensure_profile_dir(profile_num: int) -> str:
    """Create profile_num's save directory if it doesn't already exist (saves/profile_N/), returning its path. Safe to call every time a save
    happens - exist_ok=True means an existing directory is left untouched."""
    path = os.path.join(SAVES_DIR, f"profile_{profile_num}")
    os.makedirs(path, exist_ok=True)
    return path

def slot_exists(profile_num: int, slot_num : int) -> bool:
    """Whether profile_num/slot_num already has a save file."""
    return os.path.isfile(slot_path(profile_num, slot_num))

def slot_summary(profile_num: int, slot_num: int) -> str | None:
    """A one-line summary of profile_num/slot_num's save (name, level, ancestry, current room) for a slot-picker UI to show at a glance,
    or None is the slot is empty. Reads the raw JSON directly - does not reconstruct a Player."""
    if not slot_exists(profile_num, slot_num):
        return None
    with open(slot_path(profile_num, slot_num), "r") as f:
        data = json.load(f)
    p = data["player"]
    return f"{p['name']} - LVL {p['level']} {p['ancestry_label']} - {p['current_room']}"


def serialise_player(player: Player, current_room) -> dict:
    """Snapshot Player's full state - not a delta, since there's only ever once Player and no baseline to diff against."""
    return {
        "name": player.name,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "attack_damage": player.attack_damage,
        "armour": player.armour,
        "intellect": player.intellect,
        "level": player.level,
        "experience": player.experience,
        "experience_to_next_level": player.experience_to_next_level,
        "gold": player.gold,
        "mana": player.mana,
        "ancestry_label": player.ancestry_label,
        "secondary_ancestry_label": player.secondary_ancestry_label,
        "current_room": current_room.name,
        "visited_floors": sorted(player.visited_floors),
        "dodge_chance": player.dodge_chance,
        "ability_flags": {flag: getattr(player, flag) for flag in ABILITY_FLAG_NAMES},
        "skill_tree": {name: path.unlocked_count for name, path in player.skill_tree.paths.items()},
        "skill_points": player.skill_tree.skill_points,
        "known_spells": [spell.name for spell in player.known_spells],
        "spell_cooldowns": dict(player.spell_cooldowns),
        "active_effects": [{"name": e.name, "amount": e.amount, "duration": e.duration} for e in player.active_effects],
        "inventory": [
            {"name": item.name, "equipped": item.equipped, "durability": getattr(item, "durability", None)} for item in player.inventory.items
        ],
        "companion": (
            {"name": player.companion.name, "hp": player.companion.hp,
             "active_effects": [{"name": e.name, "amount": e.amount, "duration": e.duration} for e in player.companion.active_effects]}
            if player.companion is not None else None
        ),
    }

def player_from_save_data(data: dict, world: Map) -> tuple[Player, Room]:
    """Reconstruct a Player from a save's 'player' section - bypasses ancestry selection entirely since every stat is already knwon.
    Items/spells/companion are rebuilt via their registries (dev_tools.py, per this module's registry convention - anythin that needs
    to survive a save must be registered there."""
    player = Player(
        name=data["name"],
        hp=data["hp"],
        attack_damage=data["attack_damage"],
        armour=data["armour"],
        ancestry_label=data["ancestry_label"],
    )
    player.max_hp = data["max_hp"]
    player.intellect = data["intellect"]
    player.level = data["level"]
    player.experience = data["experience"]
    player.experience_to_next_level = data["experience_to_next_level"]
    player.gold = data["gold"]
    player.mana = data["mana"]
    player.secondary_ancestry_label = data["secondary_ancestry_label"]
    player.visited_floors = set(data["visited_floors"])
    player.dodge_chance = data["dodge_chance"]

    for flag, value in data["ability_flags"].items():
        setattr(player, flag, value)

    for path_name, unlocked_count in data["skill_tree"].items():
        if path_name in player.skill_tree.paths:
            player.skill_tree.paths[path_name].unlocked_count = unlocked_count
    player.skill_tree.skill_points = data["skill_points"]

    player.known_spells = [s for s in (find_spell_by_name(n) for n in data["known_spells"]) if s is not None]
    player.spell_cooldowns = dict(data["spell_cooldowns"])
    player.active_effects = [StatusEffect(e["name"], e["amount"], e["duration"]) for e in data["active_effects"]]

    for item_data in data["inventory"]:
        item = find_item_by_name(item_data["name"])
        if item is None:
            continue
        if item_data["durability"] is not None and isinstance(item, Armour):
            item.durability = item_data["durability"]
        player.inventory.add(item)
        if item_data["equipped"]:
            item.use(player)

    if data["companion"] is not None:
        companion = find_companion_by_name(data["companion"]["name"])
        if companion is not None:
            companion.hp = data["companion"]["hp"]
            companion.active_effects = [StatusEffect(e["name"], e["amount"], e["duration"]) for e in data["companion"]["active_effects"]]
            player.companion = companion

    current_room = world.get_room(data["current_room"])
    if current_room is None:
        room_name = data["current_room"]
        raise ValueError(f"Save references unknown room '{room_name}' - save file may be corrupted.")
    return player, current_room


def serialise_room(room) -> dict:
    """Full snapshot of one room's current state - see module docstring re: why every room is snapshotted not just changed ones.
    locked_exits is deliberately never serialised - it's static, set once at world-build time and only ever mutated by dev unlock/dev
    unlock all (out of scope for a production save). is_exit_locked() checks the player's current inventory live, every time, not a 
    persisted flag - so a fresh build_world() always reproduces identical locked_exits."""
    return {
        "enemies": [{"name": e.name, "hp": e.hp, "has_been_fled_from": e.has_been_fled_from} for e in room.enemies if e.is_alive()],
        "items": [
            {"name": item.name, "durability": getattr(item, "durability", None)} for item in room.items
        ],
        "unlocked_extras": [d for d in list(room.locked_exits) if False], 
        "locked_exits_removed": [],
        "allies_traded": [ally.name for ally in room.allies if getattr(ally, "trade_completed", False)],
    }

def apply_room_data(room, data: dict) -> None:
    """Patch a freshly-built room to match its saved deltas: remove enemies not listed, restore HP/fled-status on survivors replace
    the item list, mark completed trades."""
    saved_enemies = {e["name"]: e for e in data["enemies"]}
    for enemy in list(room.enemies):
        saved = saved_enemies.get(enemy.name)
        if saved is None:
            room.remove_enemy(enemy)
        else:
            enemy.hp = saved["hp"]
            enemy.has_been_fled_from = saved["has_been_fled_from"]

    for item in list(room.items):
        room.remove_item(item)
    for item_data in data["items"]:
        item = find_item_by_name(item_data["name"])
        if item is None:
            continue
        if item_data["durability"] is not None and isinstance(item, Armour):
            item.durability = item_data["durability"]
        room.add_item(item)

    for ally in room.allies:
        if ally.name in data["allies_traded"]:
            ally.trade_completed = True

def serialise_world(world: Map) -> dict:
    """Snapshot every room in world."""
    return {name: serialise_room(room) for name, room in world.rooms.items()}

def apply_world_data(world: Map, data: dict) -> None:
    """Patch every room in a freshly-built world against its saved snapshot."""
    for room_name, room_data in data.items():
        room = world.get_room(room_name)
        if room is not None:
            apply_room_data(room, room_data)


def save_game(profile_num: int, slot_num: int, player: Player, current_room, world: Map) -> None:
    """Write a full save to profile_num/slot_num, overwriting anything already there. No confirmation logic here - that's
    main()'s job (its title-screen New Game flow and the 'save <profile> <slot>' command both confirm before overwriting
    an occupied slot; this function itself always overwrites unconditionally)."""
    ensure_profile_dir(profile_num)
    data = {"player": serialise_player(player, current_room), "world": serialise_world(world)}
    with open(slot_path(profile_num, slot_num), "w") as f:
        json.dump(data, f, indent=2)

def load_game(profile_num: int, slot_num: int, world: Map) -> tuple[Player, Room]:
    """Reconstruct a Player from profile_num/slot_num, patching world (already built fresh via build_world()) to match. Raises FileNotFoundError
    if the slot is empty - the caller is responsible for checking slot_exists() first and showing a friendly message instead of letting this
    propagate."""
    with open(slot_path(profile_num, slot_num), "r") as f:
        data = json.load(f)
    apply_world_data(world, data["world"])
    return player_from_save_data(data["player"], world)

def delete_save(profile_num: int, slot_num: int) -> bool:
    """Delete one save slot. Returns False if there was nothing to delete."""
    if not slot_exists(profile_num, slot_num):
        return False
    os.remove(slot_path(profile_num, slot_num))
    return True

def delete_profile(profile_num: int) -> bool:
    """Delete every slot in a profile. Returns False if the profile directory doesn't exist."""
    path = os.path.join(SAVES_DIR, f"profile_{profile_num}")
    if not os.path.isdir(path):
        return False
    for slot_num in range(1, SAVE_SLOTS_PER_PROFILE + 1):
        if slot_exists(profile_num, slot_num):
            os.remove(slot_path(profile_num, slot_num))
    return True