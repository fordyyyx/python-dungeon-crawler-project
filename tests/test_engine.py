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

    assert "attack - attack an enemy in the room (locks you into combat)" in text
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

def test_get_controls_text_lists_cast_command():
    text = get_controls_text()

    assert "cast <spell> - cast a known spell (mid-combat only); costs mana and may set a one-turn cooldown" in text

def test_get_controls_text_lists_rest_and_wait_command():
    text = get_controls_text()

    assert "rest / wait - recover mana outside of combat" in text

def test_get_controls_text_lists_repair_command():
    text = get_controls_text()

    assert "repair <item> - repair an item to full durability (requires gold)" in text

def test_main_happy_path_smoke_test(monkeypatch, capsys):
    """Scripted playthrough of the full routing chain: name/ancestry prompts, movement, take, use, and quit."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "Hero",
        "basic",
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

def test_main_dev_command_routing_smoke_test(monkeypatch, capsys):
    """Scripted playthrough covering dev-mode activation via the 'developer mode' name, the floor-select
    prompt it unlocks, and dispatch of a dev command - all routed before the in_combat check."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "developer mode",
        "basic",
        "floor_0",
        "dev set hp 999",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "[DEV] Developer mode activated." in captured.out
    assert "[DEV] hp set to 999." in captured.out

def test_main_combat_routing_smoke_test(monkeypatch, capsys):
    """Scripted playthrough covering both combat-entry paths: the 'attack' elif branch starts combat,
    then the earlier player.in_combat elif branch takes over for the follow-up 'attack'."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "developer mode",
        "basic",
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

def test_main_target_command_redirects_pre_combat_attack_smoke_test(monkeypatch, capsys):
    """Scripted playthrough covering the 'target <name>' command: with two different enemies in the room,
    targeting the second by name before the first 'attack' must redirect that first attack to it, rather
    than defaulting to whichever enemy is first in the room."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "developer mode",
        "basic",
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

def test_main_recruit_and_dismiss_routing_smoke_test(monkeypatch, capsys):
    """Scripted playthrough confirming 'recruit <name>' and 'dismiss' route to their handlers, via the
    no-companion-present/no-companion-to-dismiss error paths - no room in the built world has a recruitable
    Companion yet, and there's no dev-spawn support for them either, so a successful recruit isn't
    reachable through main() at all right now."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "Hero",
        "basic",
        "recruit nobody",
        "dismiss",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "There's no one named 'nobody' here to recruit." in captured.out
    assert "You don't have a companion to dismiss." in captured.out

def test_main_repair_command_routing_smoke_test(monkeypatch, capsys):
    """Scripted playthrough confirming 'repair <item>' routes to repair_item() - both away from the Forge
    (blocked) and at the Forge with an already-full-durability item (no repair needed). Wearing an item
    down below full durability requires real combat exchanges, better left to manual playtesting than
    scripted here."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "developer mode",
        "basic",
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

def test_main_rest_and_wait_restore_mana_smoke_test(monkeypatch, capsys):
    """Scripted playthrough confirming both 'rest' and 'wait' route to the same mana-recovery branch, and
    that recovery caps at max_mana rather than overfilling."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "developer mode",
        "basic",
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

def test_main_player_death_ends_game_loop_smoke_test(monkeypatch, capsys):
    """Scripted playthrough covering the tail end of main(): the while loop exits once the player dies,
    and the game-over message prints afterwards."""
    monkeypatch.setattr("dungeon_crawler.dev_tools.DEV_MODE", False)
    responses = iter([
        "developer mode",
        "basic",
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