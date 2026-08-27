from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.items import Weapon, Item
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world
from dungeon_crawler.content import create_wooden_sword, create_wooden_shield, create_dummy_head, create_mentors_token, create_charons_coin, create_bronze_xiphos, create_aegis_fragment, create_ambrosia, create_bronze_breastplate, create_small_healing_potion, create_cyclops_eye, create_spear_of_ares, create_centaurs_broken_bow, create_breastplate_of_athena, create_hermes_favour
from collections.abc import Callable


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

def find_item_by_name(name: str) -> Item | None:
    factory = ITEM_REGISTRY.get(name.lower())
    return factory() if factory else None

def handle_dev_command(command: str, player: Player, room: Room) -> str:
    if command.startswith("add "):
        item_name = command.removeprefix("add ").strip()
        item = find_item_by_name(item_name)
        if item is None:
            return f"[DEV] No known item named '{item_name}'."
        player.inventory.add(item)
        return f"[DEV] Added {item.name} to inventory."

    if command.startswith("set hp "):
        try:
            value = int(command.removeprefix("set hp ").strip())
        except ValueError:
            return "[DEV] Invalid HP value."
        player.hp = value
        return f"[DEV] HP set to {value}."

    if command == "unlock all":
        cleared = list(room.locked_exits.keys())
        room.locked_exits.clear()
        if not cleared:
            return "[DEV] No locked exits in this room."
        return f"[DEV] Unlocked: {', '.join(cleared)}."

    if command.startswith("unlock "):
        direction = command.removeprefix("unlock ").strip()
        if direction in room.locked_exits:
            del room.locked_exits[direction]
            return f"[DEV] Unlocked exit: {direction}."
        return f"[DEV] {direction} is not a locked exit here."

    if command == "skillpoints":
        player.skill_tree.skill_points += 1
        return f"[DEV] Skill points: {player.skill_tree.skill_points}."

    if command == "help":
        return (
            "[DEV] Commands: dev add <item>, dev set hp <n>, "
            "dev unlock <direction>, dev unlock all, dev skillpoints"
        )

    return f"[DEV] Unrecognised dev command: {command}. Try 'dev help'."

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
    messages.append(f"{player.name}: {player.hp}/{player.max_hp} HP  |  {enemy.name}: {enemy.hp}/{enemy.max_hp} HP")

    return "\n".join(messages)

def handle_enemy_defeat(room: Room, enemy: Enemy) -> None:
    room.remove_enemy(enemy)
    for item in enemy.loot:
        room.add_item(item)

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
    result = f"{ally.name} nods, accepting each item in turn. \"You've done well.\" They hand you the {ally.reward.name}."
    if ally.post_trade_message:
        result += f"\n\n{ally.post_trade_message}"
    return result

def print_room(room: Room):
    print(f"{room.name}: {room.description}")
    if room.items:
        print(f"You see: {', '.join(item.name for item in room.items)}")
    if room.enemies:
        enemy = room.enemies[0]
        print(f"A {enemy.name} blocks your path! {enemy.description}")
    if room.allies:
        ally = room.allies[0]
        print(f"{ally.name} is here. {ally.description}")

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

def main() -> None:
    dungeon, current_room, all_floors = build_world()
    current_floor_rooms = all_floors["floor_0"]
    player = Player(name="Hero", hp=20, attack_damage=3)

    print_room(current_room)
    print("\nNot sure where to start? Try talking to whoever is in the room with you.")

    while player.is_alive():
        command = input("> ").strip().lower()
        print("\n\n")

        if command.startswith("take ") and " from " not in command:
            item_name = command.removeprefix("take ").strip()
            print(pick_up(current_room, item_name, player))

        elif command in ("quit", "exit"):
            break

        elif command.startswith("dev ") and DEV_MODE:
            print(handle_dev_command(command.removeprefix("dev ").strip(), player, current_room))

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
                print_room(current_room)

        elif command == "look":
            print_room(current_room)

        elif command == "attack":
            if current_room.enemies:
                enemy = current_room.enemies[0]
                print(resolve_combat_round(player, enemy))
                if not enemy.is_alive():
                    handle_enemy_defeat(current_room, enemy)
                    if enemy.name == "Hades":
                        print(f"\n{player.name} has defeated Hades. You win!")
                        break
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
            for path_name, path in player.skill_tree.paths.items():
                next_skill = path.next_skill
                if next_skill is not None:
                    print(f"{path.name}: next unlock is {next_skill.name} - {next_skill.description}")
                else:
                    print(f"{path.name}: fully unlocked")
            print(f"Skill Points available: {player.skill_tree.skill_points}")

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