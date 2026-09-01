from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world, ANCESTRIES
from dungeon_crawler.combat import handle_combat_command, resolve_attack_and_check_defeat
from dungeon_crawler import dev_tools

def pick_up(room: Room, item_name: str, player: Player) -> str:
    for item in room.items:
        if item.name.lower() == item_name.lower():
            player.inventory.add(item)
            room.remove_item(item)
            return f"You take the {item.name}. {item.description}"
    return "That's not here."

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
        dev_tools.DEV_MODE = True
        print("[DEV] Developer mode activated.")
        name = "Dev"

    ancestry_key = choose_ancestry()
    player = create_player(name, ancestry_key)

    dungeon, current_room, all_floors = build_world()

    if dev_tools.DEV_MODE:
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
            dev_tools.DEV_MODE = not dev_tools.DEV_MODE

        elif command.startswith("dev ") and dev_tools.DEV_MODE:
            message, new_room = dev_tools.handle_dev_command(command.removeprefix("dev ").strip(), player, current_room, dungeon)
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
            print(player.get_skills_display())

        elif command.startswith("learn "):
            path_name = command.removeprefix("learn ").strip()
            try:
                print(player.skill_tree.invest(path_name, player))
            except ValueError as e:
                print(e)
        

        else:
            print("Nothing happens.")

if __name__ == "__main__":
    main()