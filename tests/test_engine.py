from dungeon_crawler.characters import Player, Enemy, Ally
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
    assert "Hero equips Wooden Sword (+1 ATK)." in captured.out
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