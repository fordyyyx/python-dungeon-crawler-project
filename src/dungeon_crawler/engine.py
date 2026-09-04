"""The game loop and top-level command routing."""

from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room, Map
from dungeon_crawler.content import build_world
from dungeon_crawler.combat import handle_combat_command, resolve_attack_and_check_defeat, handle_target_command
from dungeon_crawler import dev_tools
from dungeon_crawler.exploration import pick_up, trade_with_ally, is_exit_locked, display_local_exits, display_map, find_floor_for_room, handle_examine, recruit_companion, dismiss_companion, repair_item
from dungeon_crawler.character_creation import choose_ancestry, create_player

REST_MANA_AMOUNT = 10


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

    if room.companions:
        companion = room.companions[0]
        print(f"{companion.name} could be recruited here. {companion.description}")


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
        "target <name> - set your attack target; add a number if enemies share a name (e.g. target harpies 2)\n"
        "cast <spell> - cast a known spell (mid-combat only); costs mana and may set a one-turn cooldown\n"
        "flee - disengages from combat (mid-combat only)\n"
        "take <item> - pick up an item from the room\n"
        "use <item> - use or equip an item from your inventory\n"
        "unequip <item> - unequip an item\n"
        "drop <item> - drop an item into the room (quest items can't be dropped)\n"
        "take <item> from <ally> - take an item from an ally's inventory\n"
        "trade - trade required items with an ally for their reward\n"
        "recruit <name> - recruit a companion who joins your team in combat (requires specific items)\n"
        "repair <item> - repair an item to full durability (requires gold)\n"
        "dismiss - release your current companion, who returns home\n"
        "skills - view your skill tree progress and available points\n"
        "learn <path> - spend a skill point (attack, defence, or abilities)\n"
        "rest / wait - recover mana outside of combat\n"
        "inventory - display carried items\n"
        "stats - display your core stats and ancestry\n"
        "controls - show this list\n"
        "quit / exit - quit the game" 
    )


def main() -> None:
    """Run the game from name entry through to the player quitting or dying: developer-mode activation, ancestry
    selection, world construction, then the read-command/dispatch loop. Top-level command routing only - each
    branch calls straight into combat.py/exploration.py/dev_tools.py/characters.py for the actual behaviour."""
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

        # checked ahead of the in_combat branch below (not nested inside the exploration-only path) so dev commands
        # always work regardless of combat state - this was a real bug once, see CLAUDE.md
        elif command.startswith("dev ") and dev_tools.DEV_MODE:
            message, new_room = dev_tools.handle_dev_command(command.removeprefix("dev ").strip(), player, current_room, dungeon)
            print(message)
            if new_room is not None:
                current_room = new_room
                print_room(current_room, player)

        elif command.startswith("target "):
            print(handle_target_command(command, current_room.enemies, player))

        elif player.in_combat:
            if player.current_target is not None:
                print(handle_combat_command(command, player, player.current_target, player.team, current_room.enemies, current_room))
            else:
                # defensive fallback - in_combat and current_target should always be set/cleared together;
                # this only fires if that invariant is ever broken elsewhere
                player.in_combat = False
                print("You are no longer in combat.")

        elif command == "examine":
            print(handle_examine(current_room, player))

        elif command in ("rest", "wait"):
            restored = min(REST_MANA_AMOUNT, player.max_mana - player.mana)
            player.mana += restored
            print(f"{player.name} rests and recovers {restored} mana.")

        elif command.startswith("repair "):
            item_name = command.removeprefix("repair ").strip()
            print(repair_item(item_name, player, current_room))

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
                if player.current_target is not None:
                    enemy = player.current_target
                else:
                    enemy = current_room.enemies[0]
                player.in_combat = True
                player.current_target = enemy
                print(resolve_attack_and_check_defeat(player, enemy, player.team, current_room.enemies, current_room))
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

        elif command.startswith("recruit "):
            name = command.removeprefix("recruit ").strip()
            print(recruit_companion(name, current_room, player))

        elif command == "dismiss":
            print(dismiss_companion(player))

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