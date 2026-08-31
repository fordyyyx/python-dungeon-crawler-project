from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.items import Weapon, Item
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world, ANCESTRIES
from dungeon_crawler.content import create_wooden_sword, create_wooden_shield, create_dummy_head, create_mentors_token, create_charons_coin, create_bronze_xiphos, create_aegis_fragment, create_ambrosia, create_bronze_breastplate, create_small_healing_potion, create_cyclops_eye, create_spear_of_ares, create_centaurs_broken_bow, create_breastplate_of_athena, create_hermes_favour
from dungeon_crawler.content import create_training_dummy, create_skeleton_warrior, create_minotaur, create_hades
from dungeon_crawler.content import create_chiron, create_mentor, create_wounded_soldier, create_charon, create_athena, create_ares, create_hermes, create_prometheus
from collections.abc import Callable
import random

DEV_MODE = False

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
    "skillpoints": "skillpoints",
}

def handle_dev_set(stat_name: str, value_str: str, player: Player) -> str:
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
 
def find_item_by_name(name: str) -> Item | None:
    factory = ITEM_REGISTRY.get(name.lower())
    return factory() if factory else None

def find_enemy_by_name(name: str) -> Enemy | None:
    factory = ENEMY_REGISTRY.get(name.lower())
    return factory() if factory else None

def find_ally_by_name(name: str) -> Ally | None:
    factory = ALLY_REGISTRY.get(name.lower())
    return factory() if factory else None

def handle_dev_kill(player: Player, room: Room) -> str:
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

def find_room_by_name_ci(dungeon: Map, name: str) -> "Room | None":
    target = name.lower()
    for room_name, room_obj in dungeon.rooms.items():
        if room_name.lower() == target:
            return room_obj
    return None

def handle_dev_remove(character_name: str, room: Room) -> str:
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
    enemy_count = len(room.enemies)
    ally_count = len(room.allies)
    for enemy in list(room.enemies):
        room.remove_enemy(enemy)
    for ally in list(room.allies):
        room.remove_ally(ally)
    return f"[DEV] Cleared room: removed {enemy_count} enemies and {ally_count} allies."


def handle_dev_command(command: str, player: Player, room: Room, dungeon: Map) -> tuple[str, "Room | None"]:
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

def pick_up(room: Room, item_name: str, player: Player) -> str:
    for item in room.items:
        if item.name.lower() == item_name.lower():
            player.inventory.add(item)
            room.remove_item(item)
            return f"You take the {item.name}. {item.description}"
    return "That's not here."

def resolve_combat_round(player: Player, enemy: Enemy):
    messages = [player.attack(enemy)]

    if not enemy.is_alive():
        messages.append(f"{player.name}: {player.hp}/{player.max_hp} HP")
        return "\n".join(messages)

    messages.append(enemy.attack(player))
    messages.append(format_hp_line(player, enemy))

    return "\n".join(messages)

def handle_enemy_defeat(room: Room, enemy: Enemy, player: Player) -> str:
    """Remove the defeated enemy, drop loot (or trigger a phase transition), and grant XP/gold. Assembles one combined message, does not print."""
    if enemy.next_phase_factory is not None:
        next_phase = enemy.next_phase_factory()
        room.remove_enemy(enemy)
        room.add_enemy(next_phase)
        player.in_combat = True
        player.current_target = next_phase
        return f"{enemy.name} falls, but something rises to take its place - {next_phase.name}."

    room.remove_enemy(enemy)
    messages = [f"{enemy.name} has been defeated."]

    if enemy.loot:
        for item in enemy.loot:
            room.add_item(item)
        messages.append(f"It dropped: {', '.join(item.name for item in enemy.loot)}")

    if enemy.gold_reward > 0:
        player.gold += enemy.gold_reward
        messages.append(f"{player.name} picked up {enemy.gold_reward} gold.")

    if enemy.experience_reward > 0:
        messages.append(player.gain_experience(enemy.experience_reward))

    return "\n".join(messages)

def is_exit_locked(room: Room, direction: str, player: Player) -> bool:
    if direction not in room.locked_exits:
        return False
    required_item_name = room.locked_exits[direction]
    return required_item_name not in [item.name for item in player.inventory.items]

def trade_with_ally(ally: Ally, player: Player):
    if not ally.required_items or ally.reward is None:
        return f"{ally.name} has nothing to trade."

    player_item_names = [item.name for item in player.inventory.items]
    missing = [name for name in ally.required_items if name not in player_item_names]

    if missing:
        return f"{ally.name} shakes their head. \"You're still missing: {', '.join(missing)}.\""

    equipped_items = [
        item for item in player.inventory.items
        if item.name in ally.required_items and item.equipped
    ]

    if equipped_items:
        equipped_names = ", ".join(item.name for item in equipped_items)
        return f"{ally.name} shakes their head. \"You'll need to unequip: {equipped_names}.\""

    for name in ally.required_items:
        item = next(item for item in player.inventory.items if item.name == name)
        player.inventory.remove(item)

    player.inventory.add(ally.reward)
    ally.trade_completed = True
    result = f"{ally.name} nods, accepting each item in turn. \"You've done well.\" They hand you the {ally.reward.name}."
    if ally.post_trade_message:
        result += f"\n\n{ally.post_trade_message}"
    return result

def print_room(room: Room, player: Player):
    """Display a room's name, description, contents, and occupants on entry.
    Ally dialogue fires automatically here if player.auto_talk is enabled."""
    print(f"{room.name}: {room.description}")

    if room.items:
        print(f"You see: {', '.join(item.name for item in room.items)}")

    if room.enemies:
        enemy = room.enemies[0]
        if enemy.has_been_fled_from:
            print(f"The {enemy.name} is still here - it hasn't forgotten you either.")
        else:
            print(f"A {enemy.name} blocks your path! {enemy.description}")

    if room.allies:
        ally = room.allies[0]
        print(f"{ally.name} is here. {ally.description}")
        if player.auto_talk:
            print("\n" + ally.talk(player))

def display_map(current_room: Room, player: Player) -> str:
    visited: set[str] = set()
    lines = []

    def explore(room: Room) -> None:
        if room.name in visited:
            return
        visited.add(room.name)
        lines.append(f"\n{room.name}")

        unlocked_targets = []
        for direction, target in room.exits.items():
            if is_exit_locked(room, direction, player):
                lines.append(f"  {direction} -> Locked Door")
            else:
                lines.append(f"  {direction} -> {target.name}")
                unlocked_targets.append(target)

        for target in unlocked_targets:
            explore(target)

    explore(current_room)
    return "\n".join(lines)

def find_floor_for_room(room: Room, all_floors: dict[str, dict[str, Room]]) -> str | None:
    for floor_name, rooms in all_floors.items():
        if room.name in rooms:
            return floor_name
    return None

def display_local_exits(room: Room, player: Player) -> str:
    if not room.exits:
        return "There are no exits from this room."
    lines = []
    for direction, target in room.exits.items():
        if is_exit_locked(room, direction, player):
            lines.append(f"{direction} -> Locked Door")
        else:
            lines.append(f"{direction} -> {target.name}")
    return "\n".join(lines)

def choose_ancestry() -> str:
    print("\nBefore your descent begins, tell me - whose blood runs in you?\n")
    for key, data in ANCESTRIES.items():
        print(f"    {key} - {data['label']} (ATK {data['attack']} / DEF {data['armour']} / HP {data['hp']})")

    while True:
        choice = input("\n> ").strip().lower()
        if choice in ANCESTRIES:
            return choice
        print("That name means nothing to me. Choose from the list above.")

def create_player(name: str, ancestry_key: str) -> Player:
    data = ANCESTRIES[ancestry_key]
    player = Player(
        name=name,
        hp=data['hp'],
        attack_damage=data["attack"],
        armour=data["armour"],
        ancestry_label=data["label"]
    )
    player.intellect = data["intellect"]
    if data["bonus_skill_point"]:
        player.skill_tree.skill_points += 1
    return player

def handle_combat_command(command: str, player: Player, enemy: Enemy, room: Room) -> str:
    if command == "attack":
        return resolve_attack_and_check_defeat(player, enemy, room)

    if command == "flee":
        result = flee_combat(player, enemy)
        player.in_combat = False
        player.current_target = None
        return result

    if command.startswith("use "):
        item_name = command.removeprefix("use ").strip()
        try:
            result = player.inventory.use_item(item_name, player)
        except ValueError as e:
            return str(e)

        if enemy.is_alive():
            enemy_message = enemy.attack(player)
            result += f"\n{enemy_message}"
            result += "\n" + format_hp_line(player, enemy)
            if not player.is_alive():
                player.in_combat = False
                player.current_target = None
        return result

    if command == "stats":
        return player.get_stats()

    if command == "skills":
        return display_skills(player)

    if command.startswith("learn "):
        path_name = command.removeprefix("learn ").strip()
        try:
            return player.skill_tree.invest(path_name, player)
        except ValueError as e:
            return str(e)

    if command == "inventory":
        return player.get_inventory_display()

    return "You can't do that mid-combat. Try 'attack', 'flee', 'use <item>', 'stats', 'skills', or 'inventory'." 

def flee_combat(player: Player, enemy: Enemy) -> str:
    """Attempt to disengage from combat. Always succeeds, but a healthier enemy has a higher chance
    of landing a free hit as the player disengages."""
    chance_of_free_hit = enemy.hp / enemy.max_hp
    enemy.has_been_fled_from = True
    if random.random() < chance_of_free_hit:
        damage_dealt, death_message = player.take_damage(enemy.attack_damage, attacker=enemy)
        message = f"You disengage, but the {enemy.name} gets a hit in as you go - {damage_dealt} damage."
        if death_message:
            message += f"\n{death_message}"
        return message
    return f"You disengage cleanly, leaving the {enemy.name} behind."

def format_hp_line(player: Player, enemy: Enemy) -> str:
    return f"{player.name}: {player.hp}/{player.max_hp} HP  |  {enemy.name}: {enemy.hp}/{enemy.max_hp} HP"

def display_skills(player: Player) -> str:
    lines = []
    for path_name, path in player.skill_tree.paths.items():
        next_skill = path.next_skill
        if next_skill is not None:
            lines.append(f"{path.name}: next unlock is {next_skill.name} - {next_skill.description}")
        else:
            lines.append(f"{path.name}: fully unlocked")
    lines.append(f"Skill Points available: {player.skill_tree.skill_points}")
    return "\n".join(lines)

def resolve_attack_and_check_defeat(player: Player, enemy: Enemy, room: Room) -> str:
    result = resolve_combat_round(player, enemy)
    if not enemy.is_alive():
        player.in_combat = False
        player.current_target = None
        handle_enemy_defeat(room, enemy, player)
    return result

def get_controls_text() -> str:
    """Return the full player-facing command list, unchanged regardless of whether the player is currently
    locked in combat. Mirrors the README's Controls section - keep both in sync when commands change."""
    return (
        "look - display room name and description\n"
        "north / east / south / west / descend / ascend - move in that direction\n"
        "map - show the exits available from your current room\n"
        "fullmap / world - show every reachable room on the current floor\n"
        "talk - talk to an ally in the room\n"
        "toggle auto talk - allies speak automatically on room entry\n"
        "attack - attack an enemy in the room (locks you into combat)\n"
        "flee - disengages from combat (mid-combat only)\n"
        "take <item> - pick up an item from the room\n"
        "use <item> - use or equip an item from your inventory\n"
        "unequip <item> - unequip an item\n"
        "drop <item> - drop an item into the room (quest items can't be dropped)\n"
        "take <item> from <ally> - take an item from an ally's inventory\n"
        "trade - trade required items with an ally for their reward\n"
        "skills - view your skill tree progress and available points\n"
        "learn <path> - spend a skill point (attack, defence, or abilities)\n"
        "inventory - display carried items\n"
        "stats - display your core stats and ancestry\n"
        "controls - show this list\n"
        "quit / exit - quit the game" 
    )

def handle_examine(room: Room, player: Player) -> str:
    """Show a room's extra flavour text and reveal any hidden exits ot has."""
    messages = []
    if room.examine_text:
        if room.required_intellect <= player.intellect:
            messages.append(room.examine_text)
        else:
            messages.append("There's something here, but you can't quite make sense of it.")
    else:
        messages.append("You look closer, but find nothing you hadn't already noticed.")

    revealed = room.reveal_hidden_exits()
    if revealed:
        messages.append(f"Your search reveals a hidden passage: {', '.join(revealed)}.")

    return "\n".join(messages)



def main() -> None:
    global DEV_MODE
    print("What is your name, hero?")
    name = input("> ").strip() or "Hero"

    starting_floor_key = "floor_0"
    if name.lower() == "developer mode":
        DEV_MODE = True
        print("[DEV] Developer mode activated.")
        name = "Dev"

    ancestry_key = choose_ancestry()
    player = create_player(name, ancestry_key)

    dungeon, current_room, all_floors = build_world()

    if DEV_MODE:
        print("\n[DEV] Which floor should you start on?")
        for floor_key in all_floors:
            print(f"  {floor_key}")
        while True:
            choice = input("> ").strip().lower()
            if choice in all_floors:
                starting_floor_key = choice
                break
            print("[DEV] Unknown floor. Try again.")

    current_floor_rooms = all_floors[starting_floor_key]
    if starting_floor_key != "floor_0":
        current_room = next(iter(current_floor_rooms.values()))

    print_room(current_room, player)
    print("\nNot sure where to start? Try talking to whoever is in the room with you.")

    while player.is_alive():
        command = input("> ").strip().lower()
        print("\n\n")

        if command in ("quit", "exit"):
            break

        elif command == "controls":
            print(get_controls_text())

        elif command == "developer mode":
            DEV_MODE = not DEV_MODE

        elif command.startswith("dev ") and DEV_MODE:
            message, new_room = handle_dev_command(command.removeprefix("dev ").strip(), player, current_room, dungeon)
            print(message)
            if new_room is not None:
                current_room = new_room
                print_room(current_room, player)

        elif player.in_combat:
            if player.current_target is not None:
                print(handle_combat_command(command, player, player.current_target, current_room))
            else:
                player.in_combat = False
                print("You are no longer in combat.")

        elif command == "examine":
            print(handle_examine(current_room, player))

        elif command.startswith("examine "):
            item_name = command.removeprefix("examine ").strip()
            item = next((i for i in current_room.items if i.name.lower() == item_name.lower()), None)
            if item is None:
                item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
            if item is not None:
                print(f"{item.name}: {item.description}")
            else:
                print("You don't see that here.")


        elif command == "toggle auto talk":
            player.auto_talk = not player.auto_talk
            status = "on" if player.auto_talk else "off"
            print(f"Auto-talk is now {status}.")

        elif command.startswith("take ") and " from " not in command:
            item_name = command.removeprefix("take ").strip()
            print(pick_up(current_room, item_name, player))

        elif command == "map":
            print(display_local_exits(current_room, player))

        elif command in ("fullmap", "world"):
            print(display_map(current_room, player))

        elif command in current_room.exits:
            if is_exit_locked(current_room, command, player):
                required = current_room.locked_exits[command]
                print(f"That way is locked. You need the {required} first.")
            else:
                current_room = current_room.exits[command]
                found_floor = find_floor_for_room(current_room, all_floors)
                if found_floor is not None:
                    current_floor_rooms = all_floors[found_floor]
                print_room(current_room, player)

        elif command == "look":
            print_room(current_room, player)

        elif command == "attack":
            if current_room.enemies:
                enemy = current_room.enemies[0]
                player.in_combat = True
                player.current_target = enemy
                print(resolve_attack_and_check_defeat(player, enemy, current_room))
            else:
                print("There's nothing here to attack.")

        elif command.startswith("use "):
            item_name = command.removeprefix("use ").strip()
            try:
                print(player.inventory.use_item(item_name, player))
            except ValueError as e:
                print(e)

        elif command.startswith("unequip "):
            item_name = command.removeprefix("unequip ").strip()
            try:
                print(player.inventory.unequip_item(item_name, player))
            except ValueError as e:
                print(e)

        elif command.startswith("drop "):
            item_name = command.removeprefix("drop ").strip()
            try:
                item = player.inventory.drop_item(item_name)
                current_room.add_item(item)
                print(f"You drop the {item.name}")
            except ValueError as e:
                print(e)

        elif command == "stats":
            print(player.get_stats())

        elif command == "inventory":
            print(player.get_inventory_display())

        elif command == "talk":
            if current_room.allies:
                ally = current_room.allies[0]
                print(ally.talk(player))
            else:
                print("There's no one here to talk to.")

        elif command.startswith("take ") and " from " in command:
            parts = command.removeprefix("take ").split(" from ")
            if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                print("Try: take <item> from <ally>")
            else:
                item_name, ally_name = parts
                ally = next((a for a in current_room.allies if a.name.lower() == ally_name.strip().lower()), None)
                if ally is not None:
                    print(ally.give_item(item_name.strip(), player))
                else:
                    print("There is no one here by that name.")

        elif command == "trade":
            if current_room.allies:
                ally = current_room.allies[0]
                print(trade_with_ally(ally, player))
            else:
                print("There is no one here to trade with.")

        elif command == "skills":
            print(display_skills(player))

        elif command.startswith("learn "):
            path_name = command.removeprefix("learn ").strip()
            try:
                print(player.skill_tree.invest(path_name, player))
            except ValueError as e:
                print(e)
        

        else:
            print("Nothing happens.")

    if not player.is_alive():
        print(f"\n{player.name} has died. Game over.")

if __name__ == "__main__":
    main()