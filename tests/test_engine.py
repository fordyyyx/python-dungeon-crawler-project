from dungeon_crawler.characters import Player, Enemy, Ally, Companion
from dungeon_crawler.world import Room
from dungeon_crawler.items import Weapon
from dungeon_crawler.engine import print_room, get_controls_text, main

def test_print_room_prints_name_and_description(capsys):
    room = Room("Armoury", "A dusty room full of old weapons.")
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "Armoury: A dusty room full of old weapons." in captured.out

def test_print_room_with_items_prints_item_names(capsys):
    room = Room("Armoury")
    room.add_item(Weapon(name="Bronze Xiphos", description="", damage=3))
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "You see: Bronze Xiphos" in captured.out

def test_print_room_with_no_items_does_not_print_you_see(capsys):
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "You see" not in captured.out

def test_print_room_with_enemy_prints_enemy_description(capsys):
    room = Room("Armoury")
    room.add_enemy(Enemy(name="Goblin", hp=10, description="A snarling goblin."))
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "A Goblin blocks your path! A snarling goblin." in captured.out

def test_print_room_with_no_enemies_does_not_print_blocks_your_path(capsys):
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "blocks your path" not in captured.out

def test_print_room_with_previously_fled_enemy_prints_re_encounter_message(capsys):
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=10, description="A snarling goblin.")
    enemy.has_been_fled_from = True
    room.add_enemy(enemy)
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "The Goblin is still here - it hasn't forgotten you either." in captured.out

def test_print_room_with_previously_fled_enemy_does_not_print_blocks_your_path(capsys):
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=10, description="A snarling goblin.")
    enemy.has_been_fled_from = True
    room.add_enemy(enemy)
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "blocks your path" not in captured.out

def test_print_room_with_ally_prints_ally_description(capsys):
    room = Room("Armoury")
    room.add_ally(Ally(name="Chiron", description="A wise centaur."))
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "Chiron is here. A wise centaur." in captured.out

def test_print_room_with_no_allies_does_not_print_is_here(capsys):
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "is here" not in captured.out

def test_print_room_with_auto_talk_off_does_not_print_ally_talk(capsys):
    room = Room("Armoury")
    room.add_ally(Ally(name="Chiron", description="A wise centaur.", hint="Beware the minotaur."))
    player = Player(name="hero", hp=100)
    player.auto_talk = False

    print_room(room, player)

    captured = capsys.readouterr()
    assert "Beware the minotaur." not in captured.out

def test_print_room_with_auto_talk_on_prints_ally_talk(capsys):
    room = Room("Armoury")
    room.add_ally(Ally(name="Chiron", description="A wise centaur.", hint="Beware the minotaur."))
    player = Player(name="hero", hp=100)
    player.auto_talk = True

    print_room(room, player)

    captured = capsys.readouterr()
    assert "Beware the minotaur." in captured.out

def test_print_room_with_auto_talk_on_and_no_allies_does_not_call_talk(capsys):
    room = Room("Armoury")
    player = Player(name="hero", hp=100)
    player.auto_talk = True

    print_room(room, player)

    captured = capsys.readouterr()
    assert "is here" not in captured.out

def test_print_room_with_companion_prints_recruit_message(capsys):
    room = Room("Camp")
    room.add_companion(Companion(name="Imp", hp=10, home_room=room, description="A loyal imp."))
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "Imp could be recruited here. A loyal imp." in captured.out

def test_print_room_with_no_companions_does_not_print_recruit_message(capsys):
    room = Room("Camp")
    player = Player(name="hero", hp=100)

    print_room(room, player)

    captured = capsys.readouterr()
    assert "could be recruited" not in captured.out

def test_get_controls_text_lists_movement_and_combat_commands():
    text = get_controls_text()

    assert "attack / attack light / attack heavy / attack ranged - attack an enemy in the room (locks you into combat); heavy hits harder but can miss, ranged needs an equipped ranged weapon" in text
    assert "flee - disengages from combat (mid-combat only)" in text
    assert "north / east / south / west / descend / ascend - move in that direction" in text

def test_get_controls_text_lists_inventory_and_ally_commands():
    text = get_controls_text()

    assert "take <item> - pick up an item from the room" in text
    assert "trade - trade required items with an ally for their reward" in text
    assert "inventory - display carried items" in text

def test_get_controls_text_lists_quit_command():
    text = get_controls_text()

    assert "quit / exit - quit the game" in text

def test_get_controls_text_lists_target_command():
    text = get_controls_text()

    assert "target <name> - set your attack target; add a number if enemies share a name (e.g. target harpies 2)" in text

def test_get_controls_text_lists_recruit_and_dismiss_commands():
    text = get_controls_text()

    assert "recruit <name> - recruit a companion who joins your team in combat (requires specific items)" in text
    assert "dismiss - release your current companion, who returns home" in text

def test_get_controls_text_lists_dummy_set_command():
    text = get_controls_text()

    assert "dummy set <stat> <value> - customise the practice dummy's stats (Practice Chamber only)" in text

def test_get_controls_text_lists_cast_command():
    text = get_controls_text()

    assert "cast <spell> - cast a known spell (mid-combat only); costs mana and may set a one-turn cooldown" in text

def test_get_controls_text_lists_rest_and_wait_command():
    text = get_controls_text()

    assert "rest / wait - recover mana outside of combat" in text

def test_get_controls_text_lists_save_and_load_commands():
    text = get_controls_text()

    assert "save / save <profile> <slot>" in text
    assert "load <profile> <slot>" in text

def test_get_controls_text_lists_attack_type_variants():
    text = get_controls_text()

    assert "attack light" in text
    assert "attack heavy" in text
    assert "attack ranged" in text
    assert "heavy hits harder but can miss" in text
    assert "ranged needs an equipped ranged weapon" in text

def test_get_controls_text_lists_examine_commands():
    text = get_controls_text()

    assert "examine - look closer at your surroundings; may reveal hidden passages" in text
    assert "examine <item> - view an item's description" in text

def test_get_controls_text_lists_repair_command():
    text = get_controls_text()

    assert "repair <item> - repair an item to full durability (requires gold)" in text

def test_main_happy_path_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough of the full routing chain: title screen, name/ancestry prompts, movement,
    take, use, and quit."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",  # title screen: New Game, profile 1, slot 1
        "Hero",
        "basic",
        "ares",
        "north",
        "take wooden sword",
        "use wooden sword",
        "south",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Chamber of Chiron (North)" in captured.out
    assert "You take the Wooden Sword." in captured.out
    assert "Hero equips Wooden Sword (melee, +1 DMG)." in captured.out
    assert "Hero has died" not in captured.out

def test_main_dev_command_routing_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough covering dev-mode activation via the 'developer mode' name, the floor-select
    prompt it unlocks, and dispatch of a dev command - all routed before the in_combat check."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set hp 999",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "[DEV] Developer mode activated." in captured.out
    assert "[DEV] hp set to 999." in captured.out

def test_main_combat_routing_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough covering both combat-entry paths: the 'attack' elif branch starts combat,
    then the earlier player.in_combat elif branch takes over for the follow-up 'attack'."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev spawn training dummy",
        "attack",
        "attack",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "[DEV] Spawned Training Dummy." in captured.out
    assert "Training Dummy has been defeated." in captured.out
    assert "It dropped: Dummy Head" in captured.out

def test_main_target_command_redirects_pre_combat_attack_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough covering the 'target <name>' command: with two different enemies in the room,
    targeting the second by name before the first 'attack' must redirect that first attack to it, rather
    than defaulting to whichever enemy is first in the room."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev spawn training dummy",
        "dev spawn skeleton warrior",
        "target skeleton warrior",
        "attack",
        "attack",
        "attack",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "You focus on the Skeleton Warrior." in captured.out
    assert "Skeleton Warrior has been defeated." in captured.out
    assert "It dropped: Small Healing Potion" in captured.out
    assert "Training Dummy has been defeated." not in captured.out

def test_main_recruit_and_dismiss_routing_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough confirming 'recruit <name>' and 'dismiss' route to their handlers, via the
    no-companion-present/no-companion-to-dismiss error paths - no room in the built world has a recruitable
    Companion yet, and there's no dev-spawn support for them either, so a successful recruit isn't
    reachable through main() at all right now."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "Hero",
        "basic",
        "ares",
        "recruit nobody",
        "dismiss",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "There's no one named 'nobody' here to recruit." in captured.out
    assert "You don't have a companion to dismiss." in captured.out

def test_main_repair_command_routing_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough confirming 'repair <item>' routes to repair_item() - both away from the Forge
    (blocked) and at the Forge with an already-full-durability item (no repair needed). Wearing an item
    down below full durability requires real combat exchanges, better left to manual playtesting than
    scripted here."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "repair bronze breastplate",
        "dev teleport forge of prometheus",
        "dev add bronze breastplate",
        "use bronze breastplate",
        "repair bronze breastplate",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "There's nowhere to repair armour here." in captured.out
    assert "Bronze Breastplate doesn't need repairing." in captured.out

def test_main_rest_and_wait_restore_mana_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough confirming both 'rest' and 'wait' route to the same mana-recovery branch, and
    that recovery caps at max_mana rather than overfilling."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set mana 5",
        "rest",
        "wait",
        "dev set mana 18",
        "rest",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Dev rests and recovers 10 mana." in captured.out # 5 -> 15
    assert "Dev rests and recovers 5 mana." in captured.out # 15 -> 20 (wait, same branch)
    assert "Dev rests and recovers 2 mana." in captured.out # 18 -> 20, capped rather than overfilling

def test_main_dummy_set_routing_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough confirming 'dummy set <stat> <value>' routes to handle_dummy_set() once a
    practice dummy is present, and reports the room-lookup/usage errors that live only in main()'s own
    routing (not handle_dummy_set() itself) when it isn't."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dummy set atk 50",
        "dev teleport practice chamber",
        "dummy set atk",
        "dummy set atk 50",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "There's no practice dummy here." in captured.out
    assert "[Practice] Usage: dummy set <stat> <value>" in captured.out
    assert "[Practice] atk set to 50." in captured.out

def test_main_player_death_ends_game_loop_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough covering the tail end of main(): the while loop exits once the player dies,
    and the game-over message prints afterwards."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set hp 1",
        "dev spawn skeleton warrior",
        "attack",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Dev has fallen. Game Over." in captured.out
    assert "Dev has died. Game over." not in captured.out

# ---- title screen: New Game / Load Game / Delete Save / Quit, plus save/load/autosave routing ----

def test_main_quit_from_title_screen_does_nothing(monkeypatch, capsys, tmp_path):
    """Choosing Quit at the very first prompt exits before any world/player is ever built."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    monkeypatch.setattr("builtins.input", lambda prompt="": "4")

    main()

    captured = capsys.readouterr()
    assert "hero" not in captured.out.lower()

def test_main_new_game_prompts_overwrite_confirmation_for_occupied_slot(monkeypatch, tmp_path):
    """Picking a slot that already has a save under it must ask before overwriting - declining returns to
    the title screen instead of silently starting a new game over it."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    from dungeon_crawler import save_system
    from dungeon_crawler.characters import Player
    from dungeon_crawler.world import Room, Map
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_system.save_game(1, 1, Player(name="Old Hero", hp=50), room, dungeon)

    responses = iter([
        "1", "1", "1",  # New Game, profile 1, slot 1 (occupied)
        "no",           # decline the overwrite
        "4",            # Quit
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    assert save_system.slot_summary(1, 1) == "Old Hero - LVL 1  - Chamber"

def test_main_save_command_writes_to_active_slot(monkeypatch, capsys, tmp_path):
    """The bare 'save' command persists to whichever profile/slot was chosen at the title screen."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "Hero", "basic", "ares",
        "save",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Saved to profile 1, slot 1" in captured.out
    from dungeon_crawler import save_system
    assert save_system.slot_exists(1, 1) is True

def test_main_load_game_from_title_screen_restores_saved_player(monkeypatch, capsys, tmp_path):
    """Loading via the title screen's own 'Load Game' action (not the mid-game 'load <profile> <slot>'
    command) reconstructs the saved player and drops straight into the game loop without asking for a
    name or ancestry."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    from dungeon_crawler import save_system
    from dungeon_crawler.content import build_world
    dungeon, current_room, _ = build_world()
    from dungeon_crawler.character_creation import create_player
    saved_player = create_player("Saved Hero", "basic", "ares")
    save_system.save_game(1, 1, saved_player, current_room, dungeon)

    responses = iter([
        "2", "1", "1",  # Load Game, profile 1, slot 1
        "stats",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "What is your name, hero?" not in captured.out
    assert "Saved Hero (" in captured.out  # from the 'stats' command, confirming the reload actually happened

def test_main_load_game_with_no_saves_returns_to_title_screen(monkeypatch, capsys, tmp_path):
    """Picking Load Game with an empty profile must not crash (regression test for the bug where
    choose_slot() was used instead of choose_occupied_slot(), letting an empty slot reach
    save_system.load_game() and raise an uncaught FileNotFoundError - see CLAUDE.md)."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "2", "1",  # Load Game, profile 1 (no saves)
        "4",       # back at the title screen - Quit
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()  # must not raise

    captured = capsys.readouterr()
    assert "Profile 1 has no saves." in captured.out

def test_main_delete_save_removes_slot_after_confirmation(monkeypatch, capsys, tmp_path):
    """The title screen's 'Delete Save' action removes the chosen slot once confirmed, then returns to
    the title screen rather than starting a game."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    from dungeon_crawler import save_system
    from dungeon_crawler.characters import Player
    from dungeon_crawler.world import Room, Map
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_system.save_game(1, 1, Player(name="Hero", hp=50), room, dungeon)

    responses = iter([
        "3", "1", "1",  # Delete Save, profile 1, slot 1
        "yes",          # confirm
        "4",            # Quit
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Deleted." in captured.out
    assert save_system.slot_exists(1, 1) is False

def test_main_autosaves_on_first_crossing_into_a_new_floor(monkeypatch, capsys, tmp_path):
    """Crossing into a floor not yet in player.visited_floors triggers an autosave and prints '(autosaved)'."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev add charon's coin",    # unlocks the 'descend' exit to floor 1, from the starting room itself
        "descend",                  # floor_0 -> floor_1: first-ever crossing, autosaves
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "(autosaved)" in captured.out
    from dungeon_crawler import save_system
    assert save_system.slot_exists(1, 1) is True