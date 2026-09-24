"""Save/load system - profile and slot management, JSON persistence for Player state and a full per-room snapshot of the world. See roadmap.md's
Save/load system item for the full design.

Scope note: this module owns serialisation/deserialisation and file I/O only. The title screen and every save/load prompt live in
character_creation.py; main()'s save/load/autosave commands and the active-slot session state live in engine.py.

Every room currently gets a full snapshot, not just changed ones - the "only serialise changed rooms" optimisation from roadmap.md
needs real change-tracking (a Room.touched flag or similar) to do properly, which is out of scope for this pass. JSON size for a text-game map
is trivial, so this is a safe simplification, not a shortcut that needs revisiting urgently."""

import json
import os

from dungeon_crawler.characters import Player
from dungeon_crawler.world import Map, Room
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.items import Armour
from dungeon_crawler.dev_tools import find_item_by_name, find_spell_by_name, find_companion_by_name, find_enemy_by_name, ENEMY_REGISTRY
from dungeon_crawler.character_creation import ANCESTRIES

PROFILE_LIMIT = 3
SAVE_SLOTS_PER_PROFILE = 5
SAVES_DIR = "saves"

ABILITY_FLAG_NAMES = [
    "has_double_strike", "has_last_stand", "has_thorns", "has_reckless_strength", "has_measured_casting", "has_swift_feet",
    "has_unyielding_tide", "has_berserking", "has_silver_tongue", "can_ranged_without_weapon", "has_petrifying_gaze", "has_bull_rush",
    "has_iron_hide",
]
"""The 13 boolean ability flags (3 skill-tree + 10 secondary-ancestry, see characters.py) that need saving directly by name - the fourth
skill-tree ability, dodge_chance, is numeric, handled as its own field instead."""


def slot_path(profile_num: int, slot_num: int) -> str:
    """Path to a given profile/slot's save file e.g. saves/profile_1/slot_3.json, Does not create anything - see ensure_profile_dir()."""
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
    or None if the slot is empty. Reads the raw JSON directly - does not reconstruct a Player."""
    if not slot_exists(profile_num, slot_num):
        return None
    with open(slot_path(profile_num, slot_num), "r") as f:
        data = json.load(f)
    p = data["player"]
    return f"{p['name']} - LVL {p['level']} {p['ancestry_label']} - {p['current_room']}"


def serialise_player(player: Player, current_room) -> dict:
    """Snapshot Player's full state - not a delta, since there's only ever one Player and no baseline to diff against."""
    return {
        "name": player.name,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "attack_damage": player.attack_damage,
        "base_armour": player.base_armour,
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
        "companion": serialise_companion(player.companion) if player.companion is not None else None,
        "dev_mode": player.dev_mode,
        "auto_map": player.auto_map,
        "visited_rooms": sorted(player.visited_rooms),
        "seen_hints": sorted(player.seen_hints),
        "ancestry_key": player.ancestry_key,
        "secondary_ancestry_key": player.secondary_ancestry_key,
        "seen_lines": sorted(player.seen_lines),
    }

def _ancestry_key_for_label(label: str, field: str = "label") -> str | None:
    """The ANCESTRIES key whose `field` matches label, or None - recovers keys for saves made before they were stored. The secondary lookup
    passes field="secondary_ability_label", since that's what secondary_ancestry_label holds."""
    return next((key for key, data in ANCESTRIES.items() if data[field] == label), None)

def player_from_save_data(data: dict, world: Map) -> tuple[Player, Room]:
    """Reconstruct a Player from a save's 'player' section - bypasses ancestry selection entirely since every stat is already known.
    Items/spells/companion are rebuilt via their registries (dev_tools.py, per this module's registry convention - anything that needs
    to survive a save must be registered there)."""
    player = Player(
        name=data["name"],
        hp=data["hp"],
        attack_damage=data["attack_damage"],
        armour=0,
        ancestry_label=data["ancestry_label"],
    )
    if "base_armour" in data:
        player.base_armour = data["base_armour"]
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
    player.ancestry_key = data.get("ancestry_key") or _ancestry_key_for_label(data["ancestry_label"])
    player.secondary_ancestry_key = data.get("secondary_ancestry_key") or _ancestry_key_for_label(data["secondary_ancestry_label"], "secondary_ability_label")
    player.seen_lines = set(data.get("seen_lines", []))

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

    if "base_armour" not in data:
        # an older save stored total armour, worn pieces included - set it only now the gear is back on, so the armour setter can take
        # the worn pieces' defence back out and leave just the base
        player.armour = data["armour"]

    if data["companion"] is not None:
        home_room = world.get_room(data["companion"].get("home_room", ""))
        player.companion = companion_from_save_data(data["companion"], home_room)

    player.dev_mode = data["dev_mode"]
    player.auto_map = data.get("auto_map", False)
    player.visited_rooms = set(data.get("visited_rooms", []))
    player.seen_hints = set(data.get("seen_hints", []))

    current_room = world.get_room(data["current_room"])
    if current_room is None:
        room_name = data["current_room"]
        raise ValueError(f"Save references unknown room '{room_name}' - save file may be corrupted.")
    return player, current_room

def serialise_companion(companion) -> dict:
    """A companion's saved state - level and XP rather than stats (stats are recalculated on load by restore_level()), plus whether their duel is
    won and which room is home."""
    return {
        "name": companion.name,
        "hp": companion.hp,
        "level": companion.level,
        "experience": companion.experience,
        "duel_won": companion.duel_won,
        "home_room": companion.home_room.name,
        "active_effects": [{"name": e.name, "amount": e.amount, "duration": e.duration} for e in companion.active_effects],
    }

def companion_from_save_data(data: dict, home_room: "Room | None"):
    """Rebuild a companion from its saved state via COMPANION_REGISTRY, or None if it isn't registered. home_room re-links the real room from the
    loaded world - the registry factory only has a detached placeholder. Older saves only had name, hp, and active_effects, so every other field
    falls back to a fresh companion's value."""
    companion = find_companion_by_name(data["name"])
    if companion is None:
        return None
    companion.restore_level(data.get("level", 1), data.get("experience", 0))
    companion.hp = min(data["hp"], companion.max_hp)
    companion.duel_won = data.get("duel_won", False)
    if home_room is not None:
        companion.home_room = home_room
    companion.active_effects = [StatusEffect(e["name"], e["amount"], e["duration"]) for e in data.get("active_effects", [])]
    return companion


def serialise_room(room) -> dict:
    """Full snapshot of one room's current state - see module docstring re: why every room is snapshotted not just changed ones.
    locked_exits is saved as the directions still locked: walking through a locked exit unlocks it for good (Room.unlock_exit()), so a
    fresh build_world() alone would re-lock doors the player has already opened. unlocked_extras/locked_exits_removed are older,
    always-empty placeholders, kept only so existing saves keep the same shape. A wave add's wave_gate_factory can't be saved
    as a function, so it's stored as the name of the phase it would spawn, and re-linked through ENEMY_REGISTRY by apply_room_data().
    Every companion still in the room is saved via serialise_companion(), so a won duel - or a recruited companion's absence - survives."""
    return {
        "enemies": [
            {
            "name": e.name,
            "hp": e.hp,
            "has_been_fled_from": e.has_been_fled_from,
            "wave_gate": e.wave_gate_factory().name if e.wave_gate_factory is not None else None
            }
            for e in room.enemies if e.is_alive()],
        "items": [
            {"name": item.name, "durability": getattr(item, "durability", None)} for item in room.items
        ],
        "unlocked_extras": [d for d in list(room.locked_exits) if False],
        "locked_exits_removed": [],
        "allies_traded": [ally.name for ally in room.allies if getattr(ally, "trade_completed", False)],
        "fast_travel_locks": sorted(room.fast_travel_locks),
        "locked_exits": sorted(room.locked_exits),
        "companions": [serialise_companion(companion) for companion in room.companions],
    }

def apply_room_data(room, data: dict) -> None:
    """Patch a freshly-built room to match its saved snapshot: restore the room's living enemies, replace the item list, mark completed
    trades, restore fast_travel_locks, unlock any locked exit the save no longer lists as locked, and replace the room's companions with
    the saved ones (the last three only when the save has them - an older save without "locked_exits" or "companions" leaves what
    build_world() made in place).

    Enemies: each saved enemy first claims an unclaimed same-named enemy already in the fresh room (in order, so two same-named enemies
    each get their own saved HP), keeping the exact instance build_world() made - which matters for any enemy ENEMY_REGISTRY doesn't
    know. A saved enemy the fresh room doesn't have (a wave add or a later boss phase spawned mid-fight) is
    rebuilt from ENEMY_REGISTRY instead, and silently skipped if the registry doesn't know it either. Fresh enemies nobody claimed were
    defeated before the save, so they're removed. A saved wave_gate is re-linked to its ENEMY_REGISTRY factory - one shared function
    object, so reloaded siblings still pass handle_enemy_defeat()'s identity check."""
    unclaimed = list(room.enemies)
    for enemy_data in data["enemies"]:
        enemy = next((e for e in unclaimed if e.name == enemy_data["name"]), None)
        if enemy is not None:
            unclaimed.remove(enemy)
        else:
            enemy = find_enemy_by_name(enemy_data["name"])
            if enemy is None:
                continue
            room.add_enemy(enemy)
        enemy.hp = enemy_data["hp"]
        enemy.has_been_fled_from = enemy_data["has_been_fled_from"]
        gate_name = enemy_data.get("wave_gate")
        if gate_name is not None:
            enemy.wave_gate_factory = ENEMY_REGISTRY.get(gate_name.lower())
    for enemy in unclaimed:
        room.remove_enemy(enemy)

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

    if "fast_travel_locks" in data:
        room.fast_travel_locks = set(data["fast_travel_locks"])

    if "locked_exits" in data:
        still_locked = set(data["locked_exits"])
        for direction in list(room.locked_exits):
            if direction not in still_locked:
                room.unlock_exit(direction)

    if "companions" in data:
        for companion in list(room.companions):
            room.remove_companion(companion)
        for companion_data in data["companions"]:
            companion = companion_from_save_data(companion_data, room)
            if companion is not None:
                room.add_companion(companion)

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