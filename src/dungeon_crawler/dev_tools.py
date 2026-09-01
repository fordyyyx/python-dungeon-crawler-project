"""The entire developer command toolkit - isolated from real gameplay logic. DEV_MODE gates all of it; toggled via
the 'developer mode' command in main()."""

from typing import Callable
from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.items import Item
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import create_wooden_sword, create_wooden_shield, create_dummy_head, create_mentors_token, create_charons_coin, create_bronze_xiphos, create_aegis_fragment, create_ambrosia, create_bronze_breastplate, create_small_healing_potion, create_cyclops_eye, create_spear_of_ares, create_centaurs_broken_bow, create_breastplate_of_athena, create_hermes_favour
from dungeon_crawler.content import create_training_dummy, create_skeleton_warrior, create_minotaur, create_hades
from dungeon_crawler.content import create_chiron, create_mentor, create_wounded_soldier, create_charon, create_athena, create_ares, create_hermes, create_prometheus
from dungeon_crawler.combat import handle_enemy_defeat

DEV_MODE = False

# Every new create_*() item/enemy/ally function in content.py needs a matching line in the relevant
# registry below (mirrored across all three) - otherwise dev add/spawn can't find it. See CLAUDE.md.
ITEM_REGISTRY: dict[str, Callable[[], Item]] = {
    "wooden sword": create_wooden_sword,
    "wooden shield": create_wooden_shield,
    "dummy head": create_dummy_head,
    "mentor's token": create_mentors_token,
    "charon's coin": create_charons_coin,
    "bronze xiphos": create_bronze_xiphos,
    "shield of aegis (fragment)": create_aegis_fragment,
    "vial of ambrosia": create_ambrosia,
    "bronze breastplate": create_bronze_breastplate,
    "small healing potion": create_small_healing_potion,
    "cyclops eye": create_cyclops_eye,
    "spear of ares": create_spear_of_ares,
    "centaur's broken bow": create_centaurs_broken_bow,
    "breastplate of athena": create_breastplate_of_athena,
    "favour of hermes": create_hermes_favour,
}

ENEMY_REGISTRY: dict[str, Callable[[], Enemy]] = {
    "training dummy": create_training_dummy,
    "skeleton warrior": create_skeleton_warrior,
    "minotaur": create_minotaur,
    "hades": create_hades,
}

ALLY_REGISTRY: dict[str, Callable[[], Ally]] = {
    "chiron": create_chiron,
    "mentor": create_mentor,
    "wounded soldier": create_wounded_soldier,
    "charon": create_charon,
    "athena": create_athena,
    "ares": create_ares,
    "hermes": create_hermes,
    "prometheus": create_prometheus,

}

STAT_ALIASES = {
    "atk": "attack_damage",
    "def": "armour",
    "hp": "hp",
    "maxhp": "max_hp",
}

def find_item_by_name(name: str) -> Item | None:
    """Look up name (case-insensitive) in ITEM_REGISTRY and build a fresh instance, or None if no match."""
    factory = ITEM_REGISTRY.get(name.lower())
    return factory() if factory else None

def find_enemy_by_name(name: str) -> Enemy | None:
    """Look up name (case-insensitive) in ENEMY_REGISTRY and build a fresh instance, or None if no match."""
    factory = ENEMY_REGISTRY.get(name.lower())
    return factory() if factory else None

def find_ally_by_name(name: str) -> Ally | None:
    """Look up name (case-insensitive) in ALLY_REGISTRY and build a fresh instance, or None if no match."""
    factory = ALLY_REGISTRY.get(name.lower())
    return factory() if factory else None

def find_room_by_name_ci(dungeon: Map, name: str) -> "Room | None":
    """Case-insensitive room lookup by name across the whole dungeon, or None if no match."""
    target = name.lower()
    for room_name, room_obj in dungeon.rooms.items():
        if room_name.lower() == target:
            return room_obj
    return None


def handle_dev_set(stat_name: str, value_str: str, player: Player) -> str:
    """Set any real Player attribute by name via setattr (STAT_ALIASES resolves shorthand like 'atk'/'def' first) - a single
    generic command rather than one branch per stat, so a new stat works automatically the moment it exists on Player. Also
    keeps hp/max_hp consistent with each other when one is set past the other. 'skillpoints' is special-cased since it lives
    on player.skill_tree, not directly on player."""
    stat_name = stat_name.strip().lower()
    try:
        value = int(value_str.strip())
    except ValueError:
        return f"[DEV] Invalid value '{value_str.strip()}'."

    if stat_name == "skillpoints":
        player.skill_tree.skill_points = value
        return f"[DEV] Skill points set to {value}."

    attr_name = STAT_ALIASES.get(stat_name, stat_name)
    if not hasattr(player, attr_name):
        return f"[DEV] Unknown stat '{stat_name}'."

    setattr(player, attr_name, value)

    if attr_name == "hp" and value > player.max_hp:
        player.max_hp = value
    if attr_name == "max_hp" and player.hp > value:
        player.hp = value

    return f"[DEV] {stat_name} set to {value}."

def handle_dev_kill(player: Player, room: Room) -> str:
    """Instantly defeat the player's current combat target if it's in this room, otherwise the room's first enemy. Reuses
    handle_enemy_defeat() for the actual removal/loot/reward handling rather than reimplementing it."""
    if player.current_target is not None and player.current_target in room.enemies:
        enemy = player.current_target
    elif room.enemies:
        enemy = room.enemies[0]
    else:
        return "[DEV] No enemy here to kill."

    enemy.hp = 0
    handle_enemy_defeat(room, enemy, player)
    player.in_combat = False
    player.current_target = None

    loot_text = f" Dropped: {', '.join(item.name for item in enemy.loot)}." if enemy.loot else ""
    return f"[DEV] Killed {enemy.name}.{loot_text}"

def handle_dev_remove(character_name: str, room: Room) -> str:
    """Remove a single matching enemy or ally from room by name (first match only). Does not call handle_enemy_defeat() -
    no loot, XP, or gold; a dev removal is not a kill. See also handle_dev_remove_all() and handle_dev_clear_room()
    for the other two removal scopes - each is a distinct, deliberate scope, not interchangeable."""
    character_name = character_name.strip().lower()
    for enemy in room.enemies:
        if enemy.name.lower() == character_name:
            room.remove_enemy(enemy)
            return f"[DEV] Removed {enemy.name}."
    for ally in room.allies:
        if ally.name.lower() == character_name:
            room.remove_ally(ally)
            return f"[DEV] Removed {ally.name}."
    return f"[DEV] No character named '{character_name}' found here."

def handle_dev_remove_all(character_name: str, room: Room) -> str:
    """Remove every enemy/ally in room matching character_name. Does not call handle_enemy_defeat() - no loot, XP, or gold;
    a dev removal is not a kill. See also handle_dev_remove() (single instance) and handle_dev_clear_room() (everything)."""
    character_name = character_name.strip().lower()
    removed = 0
    for enemy in list(room.enemies):
        if enemy.name.lower() == character_name:
            room.remove_enemy(enemy)
            removed += 1
    for ally in list(room.allies):
        if ally.name.lower() == character_name:
            room.remove_ally(ally)
            removed += 1
    if removed == 0:
        return f"[DEV] No character named '{character_name}' found here."
    return f"[DEV] Removed {removed} instance(s) of '{character_name}'."

def handle_dev_clear_room(room: Room) -> str:
    """Remove every enemy and ally in room, regardless of name. Does not call handle_enemy_defeat() - no loot, XP, or gold;
    a dev removal is not a kill. See also handle_dev_remove() (single instance) and handle_dev_remove_all() (all of one name)."""
    enemy_count = len(room.enemies)
    ally_count = len(room.allies)
    for enemy in list(room.enemies):
        room.remove_enemy(enemy)
    for ally in list(room.allies):
        room.remove_ally(ally)
    return f"[DEV] Cleared room: removed {enemy_count} enemies and {ally_count} allies."

def handle_dev_command(command: str, player: Player, room: Room, dungeon: Map) -> tuple[str, "Room | None"]:
    """Dispatch a 'dev ...' command (with the 'dev ' prefix already stripped) to the matching handle_dev_*() function.
    Always returns (message, new_room) - new_room is only ever non-None for 'dev teleport', letting main() reassign
    current_room; every other branch must still return None as the second element, not a bare string. This shape
    matters because a bare string return here was a real bug once (see CLAUDE.md) - a stale call site hadn't been
    updated after this function's return type changed, so main() printed the raw tuple instead of the message."""
    if command.startswith("set "):
        parts = command.removeprefix("set ").split(" ", 1)
        if len(parts) != 2:
            return "[DEV] Usage: dev set <stat> <value>", None
        return handle_dev_set(parts[0], parts[1], player), None

    if command.startswith("add "):
        item_name = command.removeprefix("add ").strip()
        item = find_item_by_name(item_name)
        if item is None:
            return f"[DEV] No known item named '{item_name}'.", None
        player.inventory.add(item)
        return f"[DEV] Added {item.name} to inventory.", None

    if command.startswith("spawn "):
        character_name = command.removeprefix("spawn ").strip()
        enemy = find_enemy_by_name(character_name)
        if enemy is not None:
            room.add_enemy(enemy)
            return f"[DEV] Spawned {enemy.name}.", None
        ally = find_ally_by_name(character_name)
        if ally is not None:
            room.add_ally(ally)
            return f"[DEV] Spawned {ally.name}.", None
        return f"[DEV] No known character names {character_name}.", None

    if command.startswith("remove all "):
        return handle_dev_remove_all(command.removeprefix("remove all "), room), None

    if command.startswith("remove "):
        return handle_dev_remove(command.removeprefix("remove "), room), None

    if command == "clear room":
        return handle_dev_clear_room(room), None

    if command == "kill":
        return handle_dev_kill(player, room), None

    if command.startswith("teleport "):
        room_name = command.removeprefix("teleport ").strip()
        target_room = find_room_by_name_ci(dungeon, room_name)
        if target_room == None:
            return f"[DEV] No room named '{room_name}'.", None
        player.in_combat = False
        player.current_target = None
        return f"[DEV] Teleported to {target_room.name}.", target_room

    if command.startswith("learn "):
        path_name = command.removeprefix("learn ").strip()
        # grant a point up front so invest() only fails on a bad path name, not on missing points
        # (dev learn should work regardless of the player's real point balance) - refunded below if it fails
        player.skill_tree.skill_points += 1
        try:
            return "[DEV] " + player.skill_tree.invest(path_name, player), None
        except ValueError as e:
            player.skill_tree.skill_points -= 1
            return f"[DEV] {e}", None

    if command == "unlock all":
        cleared = list(room.locked_exits.keys())
        room.locked_exits.clear()
        if not cleared:
            return "[DEV] No locked exits in this room.", None
        return f"[DEV] Unlocked: {', '.join(cleared)}.", None

    if command.startswith("unlock "):
        direction = command.removeprefix("unlock ").strip()
        if direction in room.locked_exits:
            del room.locked_exits[direction]
            return f"[DEV] Unlocked exit: {direction}.", None
        return f"[DEV] {direction} is not a locked exit here.", None

    if command == "help":
        return (
            "[DEV] Commands: dev add <item>, dev set hp <n>, "
            "dev unlock <direction>, dev unlock all, dev skillpoints"
        ), None
        
    return f"[DEV] Unrecognised dev command: {command}. Try 'dev help'.", None