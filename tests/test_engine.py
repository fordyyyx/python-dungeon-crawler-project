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

def test_print_room_with_auto_map_on_lists_exits(capsys):
    room = Room("Styx Crossing", "Black water.")
    room.connect("east", Room("Fields of Asphodel"))
    player = Player(name="Hero", hp=20)
    player.auto_map = True
    print_room(room, player)
    captured = capsys.readouterr()
    assert "Exits:\neast -> Fields of Asphodel" in captured.out

def test_print_room_with_auto_map_off_does_not_list_exits(capsys):
    room = Room("Styx Crossing", "Black water.")
    room.connect("east", Room("Fields of Asphodel"))
    player = Player(name="Hero", hp=20)
    print_room(room, player)
    captured = capsys.readouterr()
    assert "Exits:" not in captured.out

def test_get_controls_text_lists_new_take_all_and_equip_commands():
    text = get_controls_text()
    assert "take all - " in text
    assert "take all from <ally> - " in text
    assert "use <item> / equip <item> - " in text

def test_get_controls_text_lists_auto_map_and_uncleared_commands():
    text = get_controls_text()
    assert "toggle auto map - " in text
    assert "uncleared - " in text

def test_print_room_with_living_enemy_shows_combat_hint_once(capsys):
    room = Room("Fields of Asphodel", "Grey grass.")
    room.add_enemy(Enemy(name="Shade", hp=7))
    player = Player(name="Hero", hp=20)

    print_room(room, player)
    print_room(room, player)

    captured = capsys.readouterr()
    assert captured.out.count("[Hint] There's something here that wants a fight.") == 1
    assert "combat" in player.seen_hints

def test_print_room_with_only_a_respawning_enemy_shows_no_combat_hint(capsys):
    room = Room("Practice Chamber", "Straw everywhere.")
    room.add_enemy(Enemy(name="Practice Enemy", hp=20, respawns=True))
    player = Player(name="Hero", hp=20)
    print_room(room, player)
    assert "combat" not in player.seen_hints

def test_print_room_with_only_a_dead_enemy_shows_no_combat_hint(capsys):
    room = Room("Fields of Asphodel", "Grey grass.")
    shade = Enemy(name="Shade", hp=7)
    shade.hp = 0
    room.add_enemy(shade)
    player = Player(name="Hero", hp=20)
    print_room(room, player)
    assert "combat" not in player.seen_hints

def test_print_room_in_a_forge_shows_forge_hint(capsys):
    room = Room("Forge of Prometheus", "Hot.", is_forge=True)
    player = Player(name="Hero", hp=20)
    print_room(room, player)
    captured = capsys.readouterr()
    assert "[Hint] This is the forge." in captured.out

def test_print_room_in_the_practice_chamber_shows_practice_hint(capsys):
    room = Room("Practice Chamber", "Straw everywhere.", is_practice_chamber=True)
    player = Player(name="Hero", hp=20)
    print_room(room, player)
    captured = capsys.readouterr()
    assert "[Hint] The dummy here never stays down" in captured.out

def test_print_room_does_not_repeat_a_hint_already_seen(capsys):
    room = Room("Forge of Prometheus", "Hot.", is_forge=True)
    player = Player(name="Hero", hp=20)
    player.seen_hints.add("forge")
    print_room(room, player)
    captured = capsys.readouterr()
    assert "[Hint]" not in captured.out

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

def test_main_developer_mode_toggle_command_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough confirming the mid-game 'developer mode' command toggles player.dev_mode -
    a dev command is blocked for a normal (non-'developer mode'-name) player, works once toggled on,
    then is blocked again once toggled back off."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "Hero",
        "basic",
        "ares",
        "dev set hp 999",  # blocked - dev_mode starts False for a normal player
        "developer mode",  # toggles dev_mode on
        "dev set hp 999",  # now works
        "developer mode",  # toggles dev_mode back off
        "dev set hp 999",  # blocked again
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert captured.out.count("[DEV] hp set to 999.") == 1

def test_main_combat_routing_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough covering both combat-entry paths: the 'attack' elif branch starts combat,
    then the earlier player.in_combat elif branch takes over for the follow-up 'attack'."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
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

def test_main_multi_stage_boss_wave_and_phase_transition_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough of the full multi-stage boss mechanic through main(): defeating Test Boss
    spawns its two-add wave (next_wave_factories) instead of transitioning immediately; defeating the
    first add alone must not trigger the phase transition (a living sibling still blocks it via
    wave_gate_factory); defeating the second (last) add triggers the deferred transition to Test Boss
    (Phase 2); and defeating that phase ends combat normally, with its own gold/XP reward."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev spawn test boss",
        "attack",  # kills Test Boss -> spawns the two-add wave
        "attack",  # kills the first add -> sibling still alive, no transition yet
        "attack",  # kills the second (last) add -> transition to Test Boss (Phase 2)
        "attack",  # kills Test Boss (Phase 2) -> normal defeat, ends combat
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Test Boss falls, but conjures 2 lesser foes to bar your path!" in captured.out
    assert captured.out.count("something greater emerges") == 1
    assert "something greater emerges: Test Boss (Phase 2)." in captured.out
    assert "Test Boss (Phase 2) has been defeated." in captured.out
    assert "Dev picked up 5 gold." in captured.out
    assert "Dev gains 5 experience." in captured.out

def test_main_target_command_redirects_pre_combat_attack_smoke_test(monkeypatch, capsys, tmp_path):
    """Scripted playthrough covering the 'target <name>' command: with two different enemies in the room,
    targeting the second by name before the first 'attack' must redirect that first attack to it, rather
    than defaulting to whichever enemy is first in the room."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
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
    """Scripted playthrough covering the tail end of main(): the inner while loop exits once the player
    dies, the reload prompt fires (an active profile/slot is always set by this point), and declining it
    prints the game-over message and ends main() entirely."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set hp 1",
        "dev spawn skeleton warrior",
        "attack",
        "no",  # decline "Reload your last save?"
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Dev has fallen. Game Over." in captured.out
    assert "Dev has died. Game over." not in captured.out
    assert "You have died." in captured.out

def test_main_player_death_accepting_reload_restores_the_save_and_continues_playing(monkeypatch, capsys, tmp_path):
    """Accepting the 'Reload your last save?' prompt loads the active slot (saved at full HP before the
    fatal fight) and drops back into the game loop instead of ending main() - the outer while loop runs a
    second iteration rather than falling through to the 'You have died.' message."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "save",  # snapshot the player alive, at full HP, before the fight
        "dev set hp 1",
        "dev spawn skeleton warrior",
        "attack",
        "yes",  # accept "Reload your last save?"
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Dev has fallen. Game Over." in captured.out
    assert "You have died." not in captured.out
    assert captured.out.count("Not sure where to start? Try talking to whoever is in the room with you.") == 2

def test_main_quit_after_death_reload_confirmation_is_not_conflated_with_dying_again(monkeypatch, capsys, tmp_path):
    """Real bug found and fixed: the inner while loop used to exit for both 'quit' and actual death with
    no way to tell them apart, so quitting normally (with an active save) falsely triggered the death
    reload prompt. Now a plain 'quit' from a live player returns immediately, without ever printing the
    death or reload-prompt text - regression test for that fix."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "Hero",
        "basic",
        "ares",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "You have died" not in captured.out
    assert "Reload your last save?" not in captured.out

# ---- title screen: New Game / Load Game / Delete Save / Quit, plus save/load/autosave routing ----

def test_main_quit_from_title_screen_does_nothing(monkeypatch, capsys, tmp_path):
    """Choosing Quit at the very first prompt exits before any world/player is ever built."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda prompt="": "4")

    main()

    captured = capsys.readouterr()
    assert "hero" not in captured.out.lower()

def test_main_new_game_prompts_overwrite_confirmation_for_occupied_slot(monkeypatch, tmp_path):
    """Picking a slot that already has a save under it must ask before overwriting - declining returns to
    the title screen instead of silently starting a new game over it."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
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

def test_main_moving_below_regen_cap_grants_passive_regen(monkeypatch, capsys, tmp_path):
    """Crossing into another room while below PASSIVE_REGEN_CAP_FRACTION of max_hp restores PASSIVE_REGEN_PER_MOVE HP and
    prints a message - exploration-only (movement is never reachable mid-combat)."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set hp 5",
        "north",
        "stats",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "You catch your breath as you move on. (+1 HP)" in captured.out
    assert "6 HP" in captured.out

def test_main_moving_above_regen_cap_but_below_full_hp_grants_no_regen(monkeypatch, capsys, tmp_path):
    """Regen is capped at PASSIVE_REGEN_CAP_FRACTION of max_hp (15 for a 20 HP basic player) - pacing between rooms can no longer heal to full."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set hp 17",
        "north",
        "stats",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "You catch your breath" not in captured.out
    assert "17 HP" in captured.out

def test_main_passive_regen_stops_once_hp_reaches_the_cap(monkeypatch, capsys, tmp_path):
    """From 14 HP, the first move regenerates to 15 (the cap for a 20 HP player); the second move grants nothing more."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev set hp 14",
        "north",
        "south",
        "stats",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert captured.out.count("You catch your breath as you move on.") == 1
    assert "15 HP" in captured.out

def test_main_moving_at_full_hp_does_not_print_passive_regen_message(monkeypatch, capsys, tmp_path):
    """No regen message (or HP change) when the player is already at max_hp when they move."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "north",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "You catch your breath" not in captured.out

def test_main_forge_reciprocal_exit_blocked_until_activated_from_the_other_side(monkeypatch, capsys, tmp_path):
    """The Forge of Prometheus's reciprocal fast-travel exits (back to Prayer Room/Stony Lair/Maze of Pillars)
    stay locked until the corresponding one-way 'forge' exit has been used from that room first."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev teleport forge of prometheus",
        "prayer room",
        "look",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "You haven't opened this shortcut yet - reach it from the other side first." in captured.out
    assert "Three faint doorways" in captured.out.split("You haven't opened")[-1]

def test_main_using_forge_shortcut_unlocks_the_reciprocal_exit(monkeypatch, capsys, tmp_path):
    """Using Prayer Room's one-way 'forge' exit unlocks the Forge of Prometheus's reciprocal 'prayer room' exit,
    which then works immediately."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1",
        "developer mode",
        "basic",
        "ares",
        "floor_0",
        "dev teleport prayer room",
        "forge",
        "prayer room",
        "look",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "The path back opens behind you." in captured.out
    assert "You haven't opened this shortcut yet" not in captured.out
    assert "Faded murals" in captured.out.split("The path back opens behind you.")[-1]
def test_main_guarded_exit_blocks_movement_while_the_guardian_lives(monkeypatch, capsys, tmp_path):
    """The Labyrinth of the Minotaur's south exit is guarded - walking past a living Minotaur is refused."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport labyrinth of the minotaur",
        "south",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Minotaur bars the way - you'll have to deal with it first." in captured.out
    assert "Mossy Grove:" not in captured.out

def test_main_guarded_exit_opens_once_the_room_is_cleared(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport labyrinth of the minotaur",
        "dev clear room",
        "south",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "bars the way" not in captured.out
    assert "Mossy Grove:" in captured.out

def test_main_guarded_exit_does_not_block_unguarded_exits_in_the_same_room(monkeypatch, capsys, tmp_path):
    """Only south is guarded - the player can still reach Stony Lair to the west with the Minotaur alive."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport labyrinth of the minotaur",
        "west",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "bars the way" not in captured.out
    assert "Stony Lair:" in captured.out

def test_main_take_mid_combat_picks_up_loot_dropped_by_a_defeated_enemy(monkeypatch, capsys, tmp_path):
    """Loot drops onto the room floor; with a second enemy still alive, combat stays locked - 'take' must still
    work so a multi-enemy fight's drops (e.g. the Gorgons' potions during the Medusa chain) are usable mid-fight."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport dev test room",
        "dev spawn training dummy",
        "dev spawn training dummy",
        "attack",
        "attack",
        "take dummy head",
        "look",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    before_take, after_take = captured.out.split("You take the Dummy Head.")
    assert "You can't do that mid-combat" not in before_take
    # 'look' is refused only while combat is still locked - proving the take above happened mid-fight
    assert "You can't do that mid-combat" in after_take

def test_main_take_all_from_ally_then_equip_gears_up_from_the_wounded_soldier(monkeypatch, capsys, tmp_path):
    """Smoke test: 'take all from <ally>' collects every gift in one command, and 'equip' then equips one of them."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_1",
        "take all from wounded soldier",
        "equip bronze xiphos",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Wounded Soldier gives you: Bronze Xiphos, Bronze Breastplate, Small Healing Potion." in captured.out
    assert "Dev equips Bronze Xiphos (melee, +3 DMG)." in captured.out

def test_main_uncleared_reports_only_visited_rooms_with_something_left(monkeypatch, capsys, tmp_path):
    """Walk past the Shade in Fields of Asphodel without fighting it - 'uncleared' then reports it, hints at Styx
    Crossing's hidden exit without naming the direction, and lists the Library of Athena (one open step below Styx
    Crossing) as undiscovered - while the hidden Sunken Vault is never named."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_1",
        "descend",
        "east",
        "west",
        "uncleared",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    report = captured.out.split("Floor 1:")[-1]
    assert "    Fields of Asphodel - enemies remain" in report
    assert "    Styx Crossing - something here is worth a closer look" in report
    assert "Floor 2:\n    Library of Athena - undiscovered" in report
    assert "Sunken Vault" not in report

def test_main_toggle_auto_map_lists_exits_on_entering_the_next_room(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_1",
        "toggle auto map",
        "descend",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "Auto-map is now on." in captured.out
    after_move = captured.out.split("Auto-map is now on.")[-1]
    assert "Exits:" in after_move
    assert "east -> Fields of Asphodel" in after_move

def test_main_guarded_exit_hint_shows_once_however_many_times_the_exit_is_blocked(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport labyrinth of the minotaur",
        "south",
        "south",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert captured.out.count("Minotaur bars the way") == 2
    assert captured.out.count("[Hint] Some ways forward are guarded") == 1

def test_main_skill_point_hint_shows_once_when_a_point_is_available(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev set skillpoints 1",
        "look",
        "look",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert captured.out.count("[Hint] You have a skill point to spend.") == 1

def test_main_opening_a_forge_shortcut_shows_the_shortcut_hint(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport prayer room",
        "forge",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    after_unlock = captured.out.split("The path back opens behind you.")[-1]
    assert "[Hint] You've opened a shortcut to the Forge of Prometheus." in after_unlock

def test_main_killing_the_last_enemy_with_a_spell_ends_combat(monkeypatch, capsys, tmp_path):
    """Smoke test for the cast-branch defeat fix: a spell kill must end combat, so an exploration-only command
    like 'look' works straight afterwards instead of being refused as mid-combat."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport dev test room",
        "dev spawn training dummy",
        "dev grant spell prayer bolt",
        "attack",
        "cast prayer bolt",
        "look",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    after_cast = captured.out.split("Prayer Bolt")[-1]
    assert "You can't do that mid-combat" not in after_cast
    assert "You see: Dummy Head" in after_cast

def test_main_fleeing_mid_boss_wave_then_saving_and_reloading_keeps_the_wave_and_the_guard(monkeypatch, capsys, tmp_path):
    """Smoke test for the save/load fix: fell Medusa's first phase (spawning the Gorgons), flee, save, reload - the Gorgons must
    still be there guarding 'descend', rather than the Lair reloading empty and letting the boss be skipped."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_0",
        "dev teleport lair of medusa",
        "dev set hp 100",
        "dev set attack_damage 100",
        "attack",
        "flee",
        "save",
        "load 1 1",
        "yes",
        "descend",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    assert "conjures 2 lesser foes" in captured.out
    after_reload = captured.out.split("conjures 2 lesser foes")[-1]
    assert "Gorgon bars the way - you'll have to deal with it first." in after_reload

def test_main_mid_game_load_rebuilds_the_world_instead_of_patching_the_live_one(monkeypatch, capsys, tmp_path):
    """Regression: 'load <profile> <slot>' used to patch the already-played world rather than a fresh build_world(), so state the
    save never had leaked through - here, a hidden exit revealed after saving stayed revealed after loading."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([
        "1", "1", "1", "developer mode", "basic", "ares", "floor_1",
        "descend",
        "save",
        "examine",
        "load 1 1",
        "yes",
        "down",
        "quit",
    ])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))

    main()

    captured = capsys.readouterr()
    after_reload = captured.out.split("Loading will discard")[-1]
    assert "Nothing happens." in after_reload
    assert "Sunken Vault:" not in after_reload
