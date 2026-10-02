"""The game loop and top-level command routing."""

from dungeon_crawler.characters import Player
from dungeon_crawler.world import Room
from dungeon_crawler.content import build_world, HADES_SPARED, HADES_DEFEATED, TYPHON_DEFEATED, HARDCORE
from dungeon_crawler.combat import handle_combat_command, resolve_attack_and_check_defeat, handle_target_command
from dungeon_crawler import dev_tools
from dungeon_crawler.exploration import pick_up, trade_with_ally, is_exit_locked, display_local_exits, display_map, find_floor_for_room, handle_examine, recruit_companion, dismiss_companion, repair_item, get_exit_guardian, check_equippable, take_all, take_all_from_ally, get_uncleared_rooms, start_duel, talk_to, get_rival_lines, get_enemy_ancestry_lines, get_advice, is_exit_concealed, get_story_gate
from dungeon_crawler.character_creation import choose_ancestry, choose_secondary_ancestry, create_player, choose_title_screen_action, choose_profile, choose_slot, choose_occupied_slot, confirm
from dungeon_crawler import save_system
from dungeon_crawler.hints import show_hint
from dungeon_crawler.exchange import list_offers, make_exchange, sell_item
from dungeon_crawler.exceptions import ActionRefused, SaveFileError
from dungeon_crawler.dialogue import continue_dialogue
from dungeon_crawler.upgrades import upgrade_item, list_upgrades
from dungeon_crawler.trophies import place_trophies, describe_plinths

REST_MANA_AMOUNT = 10
PASSIVE_REGEN_PER_MOVE = 1
PASSIVE_REGEN_CAP_FRACTION = 0.75
ENDING_SHOWN = "ending_shown"
TRUE_ENDING_SHOWN = "true_ending_shown"
RESERVED_COMMAND_WORDS: frozenset[str] = frozenset({
    "north", "south", "east", "west", "up", "down", "ascend", "descend",
    "look", "examine", "map", "fullmap", "world", "inventory", "stats", "skills", "learn", "advice", "offers", "exchange", "sell",
    "take", "drop", "use", "equip", "unequip", "talk", "trade", "recruit", "dismiss", "challenge", "say", "place",
    "attack", "cast", "target", "flee", "rest", "wait", "repair", "dummy", 'upgrade',
    "save", "load", "quit", "exit", "controls", "uncleared", "toggle", "dev", "developer",
})
"""The first word of every global command. Room interactions are checked before global commands so a room verb starting with one of these would
silently override it."""


def print_room(room: Room, player: Player):
    """Display a room's name, description, the Trophy Room's plinths (describe_plinths()), any room interactions currently available, contents,
    and occupants on entry. Same-named enemies
    are grouped onto one line ("Head of Scylla x6"), and each enemy is introduced with its own article (see Enemy.with_article()).
    Ally dialogue - or, with no ally present, a companion's - fires automatically here if player.auto_talk is enabled, and the room's exits
    are listed if player.auto_map is. A companion who still requires a duel is announced as present, not as recruitable. An invulnerable
    enemy is shown by its description alone - no "blocks your path", no armour - and never triggers the combat hint."""
    print(f"{room.name}: {room.description}")

    if room.is_trophy_room:
        print(describe_plinths(room))

    verbs = room.available_interactions(player)
    if verbs:
        print(f"(You could: {', '.join(verbs)})")

    if room.items:
        print(f"You see: {', '.join(item.display_name for item in room.items)}")

    if room.enemies:
        groups: dict[str, list] = {}
        for enemy in room.enemies:
            groups.setdefault(enemy.name, []).append(enemy)
        for name, group in groups.items():
            first = group[0]
            if first.invulnerable:
                print(first.description)
                continue
            count = len(group)
            if first.has_been_fled_from:
                if count == 1:
                    print(f"{first.with_article(definite=True)} is still here - it hasn't forgotten you either.")
                else:
                    print(f"{name} x{count} are still here - they haven't forgotten you either.")
            elif count == 1:
                print(f"{first.with_article()} blocks your path! {first.description} [Armour {first.armour}]")
            else:
                print(f"{name} x{count} block your path! {first.description} [Armour {first.armour}]")
        for line in get_enemy_ancestry_lines(room, player) + get_rival_lines(room, player):
            print(f"\n{line}")

    if room.allies:
        ally = room.allies[0]
        print(f"{ally.name} is here. {ally.description}")
        if player.auto_talk:
            print("\n" + talk_to(room.allies[0], player, room))

    if room.companions:
        companion = room.companions[0]
        if companion.can_be_recruited(player):
            print(f"{companion.name} could be recruited here. {companion.description}")
        else:
            print(f"{companion.name} is here. {companion.description}")
        if player.auto_talk and not room.allies:
            print("\n" + talk_to(room.companions[0], player, room))

    if player.auto_map:
        print("\nExits:\n" + display_local_exits(room, player))

    room_hints = []
    if any(enemy.is_alive() and not enemy.respawns and not enemy.invulnerable for enemy in room.enemies):
        room_hints.append(show_hint(player, "combat"))
    if room.is_forge:
        room_hints.append(show_hint(player, "forge"))
    if room.is_practice_chamber:
        room_hints.append(show_hint(player, "practice_chamber"))
    if room.is_workshop:
        room_hints.append(show_hint(player, "workshop"))
    if any(enemy.is_alive() and enemy.melee_dodge_chance > 0 for enemy in room.enemies):
        room_hints.append(show_hint(player, "evasive"))
    if room.available_interactions(player):
        room_hints.append(show_hint(player, "room_interactions"))
    for hint in room_hints:
        if hint:
            print(f"\n{hint}")

def get_controls_text() -> str:
    """Return the full player-facing command list, unchanged regardless of whether the player is currently
    locked in combat. Mirrors the README's Controls section - keep both in sync when commands change."""
    return (
        "look - display room name and description\n"
        "examine - look closer at your surroundings; may reveal hidden passages\n"
        "examine <item> - view an item's description\n"
        "north / east / south / west / descend / ascend - move in that direction\n"
        "map - show the exits available from your current room\n"
        "fullmap / world - show every reachable room on the current floor\n"
        "toggle auto map - map displays automatically on room entry\n"
        "uncleared - display visited rooms that are not yet cleared and reachable rooms not yet discovered\n"
        "talk - talk to an ally or companion in the room\n"
        "say <number> - answer in a conversation, choosing one of the numbered options\n"
        "toggle auto talk - allies speak automatically on room entry\n"
        "attack / attack light / attack heavy / attack ranged - attack an enemy in the room (locks you into combat); heavy hits harder but can miss, ranged needs an equipped ranged weapon\n"
        "target <name> - set your attack target; add a number if enemies share a name (e.g. target harpies 2)\n"
        "cast <spell> - cast a known spell (mid-combat only); costs mana and may set a one-turn cooldown\n"
        "flee - disengages from combat (mid-combat only)\n"
        "take <item> - pick up an item from the room\n"
        "take all - pick up all items from the room\n"
        "use <item> / equip <item> - use or equip an item from your inventory\n"
        "unequip <item> - unequip an item\n"
        "drop <item> - drop an item into the room (quest items can't be dropped)\n"
        "take <item> from <ally> - take an item from an ally's inventory\n"
        "take all from <ally> - take all items from an ally's inventory\n"
        "trade - trade required items with an ally for their reward\n"
        "recruit <name> - recruit a companion who joins your team in combat (requires specific items)\n"
        "challenge <name> - duel a companion who won't join until you've beaten them; losing isn't a death, and your HP is restored afterwards\n"
        "repair <item> - repair an item to full durability (requires gold)\n"
        "upgrade / upgrade <item> - improve a weapon or armour piece at a workshop (requires gold; your intellect limits how far); bare 'upgrade' lists what you could improve\n"
        "place <trophy> / place all - set a trophy you've won on its plinth, where there's somewhere worthy of it\n"
        "dismiss - release your current companion, who returns home\n"
        "advice - ask your companion what they make of the room (only some companions give advice; also works mid-combat)\n"
        "offers - list what the merchant in this room will exchange, and for how much\n"
        "exchange <number> - accept one of the merchant's offers, paying its gold (and handing over its item, if it asks for one)\n"
        "sell <item> - sell an item to someone who buys them, for half its value (quest items and equipped gear can't be sold)\n"
        "dummy set <stat> <value> - customise the practice dummy's stats (Practice Chamber only)\n"
        "skills - view your skill tree progress and available points\n"
        "learn <path> - spend a skill point (attack, defence, or abilities)\n"
        "rest / wait - recover mana outside of combat\n"
        "save / save <profile> <slot> - save your progress outside of combat; bare 'save' targets your active slot, 'save <profile> <slot>' targets a specific one (confirms first if it's already occupied)\n"
        "load <profile> <slot> - load a different save outside of combat; always confirms, since it discards any unsaved progress\n"
        "inventory - display carried items\n"
        "stats - display your core stats and ancestry\n"
        "controls - show this list\n"
        "quit / exit - quit the game"
    )

def ending_text(player: Player) -> str:
    """The ending, shown once when Hades falls. Differs slightly depending on whether he was spared."""
    if HADES_SPARED in player.story_flags:
        body = (
            "Hades doesn't go back to his throne. He stands beside you instead, looking out over a hall he hasn't truly seen in an age. Across the "
            "Underworld, the dead begin to move again - slowly, then with purpose - towards judgement at last.\n\n"
            "\"Far above, they'll call this a victory,\" he says quietly. \"Let them.\" He turns towards the dark stair. \"Whenever you're "
            "ready. He won't wait for long.\""
        )
    else:
        body = (
            "The throne of bone stands empty. Across the Underworld, the dead begin to move again - slowly, then with purpose - towards "
            "judgement at last. Far above, the gods will call it a victory.\n\n"
            "Below, something vast turns over in the dark, and doesn't go back to sleep."
        )
    return (
        "\n\n========================\n\n"
        f"{body}\n\n"
        "The story is over. The Underworld isn't finished with you yet.\n\n"
        "========================\n"
    )

def choose_after_ending() -> str:
    """Ask the player what to do after the ending - 'title' or 'continue'."""
    print("1. Return to the title screen\n2. Continue exploring\n")
    while True:
        choice = input("> ").strip()
        if choice == "1":
            return "title"
        if choice == "2":
            return "continue"
        print("Choose 1 or 2.")

def true_ending_text(player: Player) -> str:
    """The true ending, shown once when Typhon falls. Points the player towards Zeus and the Trophy Room without naming what waits there."""
    if HADES_SPARED in player.story_flags:
        opening = (
            "Typhon falls - not all at once, but the way a mountain falls, slowly, and then completely. Hades stands at the edge of the chasm "
            "a long time before he speaks. \"It's done,\" he says at last. \"For good, this time. Go home. I'll take it from here.\""
        )
    else:
        opening = (
            "Typhon falls - not all at once, but the way a mountain falls, slowly, and then completely. The chasm is quiet for the first time "
            "in an age. Whatever Hades spent himself holding back, you've finished."
        )
    return (
        "\n\n========================\n\n"
        f"{opening}\n\n"
        "Far above, on Olympus, a god who once fought Typhon himself - and only barely won - has been watching. He keeps a room for trophies "
        "like the one that just fell to the floor, and he'll want to see this one.\n\n"
        "This is the true ending.\n\n"
        "========================\n"
    )

ENDINGS = [
    (HADES_DEFEATED, ENDING_SHOWN, ending_text),
    (TYPHON_DEFEATED, TRUE_ENDING_SHOWN, true_ending_text)
]
"""(flag that triggers it, flag recording it's been shown, text). Checked after every command - see main()."""

def main() -> None:
    """Run the game from name entry through to the player quitting or dying: developer-mode activation, ancestry
    selection, world construction, then the read-command/dispatch loop. Top-level command routing only - each
    branch calls straight into combat.py/exploration.py/dev_tools.py/characters.py for the actual behaviour."""
    while True:
        active_profile: int | None = None
        active_slot: int | None = None

        while True:
            action = choose_title_screen_action()

            if action == "quit":
                return

            if action == "delete":
                profile_num = choose_profile()
                slot_num = choose_occupied_slot(profile_num)
                if slot_num is not None and confirm(f"Delete profile {profile_num}, slot {slot_num}?"):
                    save_system.delete_save(profile_num, slot_num)
                    print("Deleted.")
                continue

            if action == "load":
                profile_num = choose_profile()
                slot_num = choose_occupied_slot(profile_num)
                if slot_num is None:
                    continue
                dungeon, _, all_floors = build_world()
                try:
                    player, current_room = save_system.load_game(profile_num, slot_num, dungeon)
                except SaveFileError as error:
                    print(error)
                    continue
                active_profile, active_slot = profile_num, slot_num
                break

            profile_num = choose_profile()
            slot_num = choose_slot(profile_num)
            if save_system.slot_exists(profile_num, slot_num):
                if not confirm(f"Profile {profile_num}, slot {slot_num} already has a save. Overwrite it?"):
                    continue
            active_profile, active_slot = profile_num, slot_num

            print("What is your name, hero?")
            name = input("> ").strip() or "Hero"

            starting_floor_key = "floor_0"
            dev_mode_requested = name.lower() == "developer mode"
            if dev_mode_requested:
                print("[DEV] Developer mode activated.")
                name = "Dev"

            ancestry_key = choose_ancestry()
            secondary_ancestry_key = choose_secondary_ancestry(ancestry_key)
            player = create_player(name, ancestry_key, secondary_ancestry_key)
            player.dev_mode = dev_mode_requested

            dungeon, current_room, all_floors = build_world()

            if player.dev_mode:
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
            break

        while True:
            return_to_title = False
            starting_floor = find_floor_for_room(current_room, all_floors)
            if starting_floor is not None:
                player.visited_floors.add(starting_floor)
                player.visited_rooms.add(current_room.name)
            print_room(current_room, player)
            print("\nNot sure where to start? Try talking to whoever is in the room with you.")

            quit_requested = False
            while player.is_alive():
                if player.skill_tree.skill_points > 0:
                    skill_hint = show_hint(player, "skill_points")
                    if skill_hint:
                        print(skill_hint)
                if not player.in_combat and player.companion is not None:
                    player.companion.loyalty_ready = player.has_loyalty_token()
                command = input("> ").strip().lower()
                print("\n\n")

                if command in ("quit", "exit"):
                    quit_requested = True
                    break

                elif command in current_room.interactions and not player.in_combat:
                    interaction = current_room.interactions[command]
                    if interaction.is_available(player, current_room):
                        print(interaction.handler(player, current_room))
                    else:
                        print(interaction.unavailable_message)

                elif command == "save" and not player.in_combat:
                    if active_profile is None:
                        print("No active save slot - use 'save <profile> <slot>' first.")
                    else:
                        save_system.save_game(active_profile, active_slot, player, current_room, dungeon)
                        print(f"Saved to profile {active_profile}, slot {active_slot}")

                elif command.startswith("save ") and not player.in_combat:
                    parts = command.removeprefix("save ").split()
                    if len(parts) != 2 or not all(p.isdigit() for p in parts):
                        print("Usage: save <profile> <slot>")
                    else:
                        profile_num, slot_num = int(parts[0]), int(parts[1])
                        if HARDCORE in player.story_flags and (profile_num, slot_num) != (active_profile, active_slot):
                            print(
                                f"A hardcore run can only be saved to its own slot - profile {active_profile}, slot {active_slot}. "
                                "Use 'save' on its own."
                            )
                        else:
                            proceed = True
                            if save_system.slot_exists(profile_num, slot_num):
                                proceed = confirm(f"Profile {profile_num}, slot {slot_num} already has a save. Overwrite it?")
                            if proceed:
                                save_system.save_game(profile_num, slot_num, player, current_room, dungeon)
                                active_profile, active_slot = profile_num, slot_num
                                print(f"Saved to profile {profile_num}, slot {slot_num}.")

                elif command.startswith("load ") and not player.in_combat:
                    parts = command.removeprefix("load ").split()
                    if len(parts) != 2 or not all(p.isdigit() for p in parts):
                        print("Usage: load <profile> <slot>")
                    else:
                        profile_num, slot_num = int(parts[0]), int(parts[1])
                        if not save_system.slot_exists(profile_num, slot_num):
                            print(f"There's no save in profile {profile_num}, slot {slot_num}.")
                        elif confirm("Loading will discard any unsaved progress since your last save. Continue?"):
                            # load_game() patches a *fresh* world - reusing the live one would keep state the save never had
                            fresh_dungeon, _, fresh_floors = build_world()
                            try:
                                loaded_player, loaded_room = save_system.load_game(profile_num, slot_num, fresh_dungeon)
                            except SaveFileError as error:
                                print(error)
                            else:
                                dungeon, all_floors = fresh_dungeon, fresh_floors
                                player, current_room = loaded_player, loaded_room
                                active_profile, active_slot = profile_num, slot_num
                                print_room(current_room, player)

                elif command.startswith("challenge ") and not player.in_combat:
                    print(start_duel(command.removeprefix("challenge ").strip(), current_room, player))

                elif command == "controls":
                    print(get_controls_text())

                elif command == "developer mode":
                    player.dev_mode = not player.dev_mode

                # checked ahead of the in_combat branch below (not nested inside the exploration-only path) so dev commands
                # always work regardless of combat state - this was a real bug once, see CLAUDE.md
                elif command.startswith("dev ") and player.dev_mode:
                    message, new_room = dev_tools.handle_dev_command(command.removeprefix("dev ").strip(), player, current_room, dungeon)
                    print(message)
                    if new_room is not None:
                        current_room.on_leave()
                        current_room = new_room
                        print_room(current_room, player)

                elif command.startswith("target "):
                    print(handle_target_command(command, current_room.enemies, player))

                elif command.startswith("dummy set "):
                    parts = command.removeprefix("dummy set ").split(" ", 1)
                    if len(parts) != 2:
                        print("[Practice] Usage: dummy set <stat> <value>")
                    else:
                        dummy = next((enemy for enemy in current_room.enemies if enemy.respawns), None)
                        if dummy is None:
                            print("There's no practice dummy here.")
                        else:
                            print(dev_tools.handle_dummy_set(parts[0], parts[1], dummy))

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
                        print(f"{item.display_name}: {item.description}")
                    else:
                        print("You don't see that here.")

                elif command == "toggle auto talk":
                    player.auto_talk = not player.auto_talk
                    status = "on" if player.auto_talk else "off"
                    print(f"Auto-talk is now {status}.")

                elif command == "toggle auto map":
                    player.auto_map = not player.auto_map
                    status = "on" if player.auto_map else "off"
                    print(f"Auto-map is now {status}.")

                elif command == "take all":
                    print(take_all(current_room, player))

                elif command.startswith("take all from "):
                    ally_name = command.removeprefix("take all from ").strip()
                    ally = next((a for a in current_room.allies if a.name.lower() == ally_name.lower()), None)
                    if ally is not None:
                        print(take_all_from_ally(ally, player))
                    else:
                        print("There is no one here by that name.")

                elif command.startswith("take ") and " from " not in command:
                    item_name = command.removeprefix("take ").strip()
                    print(pick_up(current_room, item_name, player))

                elif command == "map":
                    print(display_local_exits(current_room, player))

                elif command in ("fullmap", "world"):
                    print(display_map(current_room, player))

                elif command in current_room.exits and not is_exit_concealed(current_room, command, player):
                    guardian = get_exit_guardian(current_room, command)
                    if command in current_room.fast_travel_locks:
                        print("You haven't opened this shortcut yet - reach it from the other side first.")
                    elif is_exit_locked(current_room, command, player):
                        required = current_room.locked_exits[command]
                        print(f"That way is locked. You need the {required} first.")
                    elif guardian is not None:
                        print(f"{guardian.name} bars the way - you'll have to deal with it first.")
                        guard_hint = show_hint(player, "guarded_exit")
                        if guard_hint:
                            print(guard_hint)
                    elif (gate := get_story_gate(current_room, command, player)) is not None:
                        print(gate.blocked_message)
                    else:
                        current_room.unlock_exit(command)
                        if command in current_room.exit_activations:
                            unlock_room, unlock_direction = current_room.exit_activations[command]
                            if unlock_direction in unlock_room.fast_travel_locks:
                                unlock_room.fast_travel_locks.discard(unlock_direction)
                                print("The path back opens behind you.")
                                shortcut_hint = show_hint(player, "forge_shortcut")
                                if shortcut_hint:
                                    print(shortcut_hint)
                        current_room.on_leave()
                        current_room = current_room.exits[command]
                        player.visited_rooms.add(current_room.name)
                        regen_cap = int(player.max_hp * PASSIVE_REGEN_CAP_FRACTION)
                        if player.hp < regen_cap:
                            player.hp = min(player.max_hp, player.hp + PASSIVE_REGEN_PER_MOVE)
                            print(f"You catch your breath as you move on. (+{PASSIVE_REGEN_PER_MOVE} HP)")
                            regen_hint = show_hint(player, "passive_regen")
                            if regen_hint:
                                print(regen_hint)
                        found_floor = find_floor_for_room(current_room, all_floors)
                        if found_floor is not None:
                            current_floor_rooms = all_floors[found_floor]
                            if found_floor not in player.visited_floors:
                                player.visited_floors.add(found_floor)
                                if active_profile is not None:
                                    save_system.save_game(active_profile, active_slot, player, current_room, dungeon)
                                    print("(autosaved)")
                                    autosave_hint = show_hint(player, "autosave")
                                    if autosave_hint:
                                        print(autosave_hint)
                        print_room(current_room, player)

                elif command == "look":
                    print_room(current_room, player)

                elif command == "offers":
                    print(list_offers(current_room, player))

                elif command == "exchange" or command.startswith("exchange "):
                    print(make_exchange(command.removeprefix("exchange").strip(), current_room, player))

                elif (command == "sell" or command.startswith("sell ")) and not player.in_combat:
                    print(sell_item(command.removeprefix("sell").strip(), current_room, player))

                elif (command == "upgrade" or command.startswith("upgrade ")) and not player.in_combat:
                    item_name = command.removeprefix("upgrade").strip()
                    print(upgrade_item(item_name, current_room, player) if item_name else list_upgrades(current_room, player))

                elif (command == "place" or command.startswith("place ")) and not player.in_combat:
                    item_name = command.removeprefix("place").strip()
                    print(place_trophies(item_name, current_room, player) if item_name else "Place what? Say 'place' followed by a trophy, or 'place all'.")

                elif command == "uncleared":
                    print(get_uncleared_rooms(all_floors, player))

                elif command == "attack":
                    attackable = [e for e in current_room.enemies if not e.invulnerable]
                    if attackable:
                        enemy = next((e for e in attackable if e is player.current_target), attackable[0])
                        player.in_combat = True
                        player.current_target = enemy
                        print(resolve_attack_and_check_defeat(player, enemy, player.team, current_room.enemies, current_room))
                    elif current_room.enemies:
                        print(current_room.enemies[0].invulnerable_message)
                    else:
                        print("There's nothing here to attack.")

                elif command.startswith("use "):
                    item_name = command.removeprefix("use ").strip()
                    try:
                        print(player.inventory.use_item(item_name, player))
                    except ActionRefused as e:
                        print(e)

                elif command.startswith("equip "):
                    item_name = command.removeprefix("equip ").strip()
                    error = check_equippable(item_name, player)
                    if error is not None:
                        print(error)
                    else:
                        print(player.inventory.use_item(item_name, player))

                elif command.startswith("unequip "):
                    item_name = command.removeprefix("unequip ").strip()
                    try:
                        print(player.inventory.unequip_item(item_name, player))
                    except ActionRefused as e:
                        print(e)

                elif command.startswith("drop "):
                    item_name = command.removeprefix("drop ").strip()
                    try:
                        item = player.inventory.drop_item(item_name)
                        current_room.add_item(item)
                        print(f"You drop {item.with_article(definite=True)}.")
                    except ActionRefused as e:
                        print(e)

                elif command == "stats":
                    print(player.get_stats())

                elif command == "advice":
                    print(get_advice(current_room, player))

                elif command == "inventory":
                    print(player.get_inventory_display())

                elif command == "talk":
                    if current_room.allies:
                        print(talk_to(current_room.allies[0], player, current_room))
                    elif current_room.companions:
                        print(talk_to(current_room.companions[0], player, current_room))
                    else:
                        print("There's no one here to talk to.")

                elif command == "say" or command.startswith("say "):
                    print(continue_dialogue(command.removeprefix("say").strip(), current_room, player))

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
                    except ActionRefused as e:
                        print(e)
                else:
                    print("Nothing happens.")

                outcome = None
                for trigger, shown, text in ENDINGS:
                    if trigger in player.story_flags and shown not in player.story_flags:
                        player.story_flags.add(shown)
                        print(text(player))
                        if active_profile is not None:
                            save_system.save_game(active_profile, active_slot, player, current_room, dungeon)
                            print("(autosaved)")
                        outcome = choose_after_ending()
                        break
                if outcome == "title":
                    return_to_title = True
                    break

            if return_to_title:
                break

            if quit_requested:
                return

            if HARDCORE in player.story_flags:
                if active_profile is not None:
                    save_system.delete_save(active_profile, active_slot)
                print(
                    "\nYou have died.\n\n"
                    "Somewhere far above a chained god closes his eyes. There are no second chances this time.\n"
                    "(Hardcore: this save has been deleted.)"
                )
                break

            if active_profile is not None and confirm("You have died. Reload your last save?"):
                fresh_dungeon, _, fresh_floors = build_world()
                try:
                    player, current_room = save_system.load_game(active_profile, active_slot, fresh_dungeon)
                except SaveFileError as error:
                    print(error)
                else:
                    dungeon, all_floors = fresh_dungeon, fresh_floors
                    continue

            print("\nYou have died.")
            break

if __name__ == "__main__":
    main()