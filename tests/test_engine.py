from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Armour, Consumable, QuestItem, Weapon
from dungeon_crawler.engine import pick_up, is_exit_locked, trade_with_ally, print_room, display_map, find_floor_for_room, display_local_exits, choose_ancestry, create_player, get_controls_text, handle_examine

def test_pick_up_adds_item_to_inventory():
    room = Room("Armoury")
    sword = Weapon("Bronze Xiphos", "", damage=3)
    room.add_item(sword)
    player = Player(name="hero", hp=100)

    pick_up(room, "bronze xiphos", player)

    assert sword in player.inventory.items

def test_pick_up_removes_item_from_room():
    room = Room("Armoury")
    sword = Weapon("Bronze Xiphos", "", damage=3)
    room.add_item(sword)
    player = Player(name="hero", hp=100)
    assert sword in room.items
    
    pick_up(room, "bronze xiphos", player)
    assert sword not in room.items

def test_pick_up_returns_message_with_description(capsys):
    room = Room("Armoury")
    sword = Weapon("Bronze xiphos", "", damage=3)
    room.add_item(sword)
    player = Player(name="hero", hp=100)

    print(pick_up(room, "bronze xiphos", player))
    captured = capsys.readouterr()
    assert "You take the Bronze xiphos." in captured.out


def test_pick_up_returns_not_here_message_when_item_missing(capsys):
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    print(pick_up(room, "bronze xiphos", player))
    captured = capsys.readouterr()
    assert "That's not here." in captured.out

def test_pick_up_is_case_insensitive():
    room = Room("Library of Athena")
    shield = Armour(name="Shield of Aegis (fragment)", defence=2, description="...")
    room.add_item(shield)
    player = Player(name="hero", hp=100)

    result = pick_up(room, "shield of aegis (fragment)", player)

    assert shield in player.inventory.items

def test_is_exit_locked_returns_false_when_direction_not_locked():
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    assert is_exit_locked(room, "north", player) is False

def test_is_exit_locked_returns_true_when_player_missing_required_item():
    room = Room("Armoury")
    room.lock_exit("north", "Bronze Key")
    player = Player(name="hero", hp=100)

    assert is_exit_locked(room, "north", player) is True

def test_is_exit_locked_returns_false_when_player_has_required_item():
    room = Room("Armoury")
    room.lock_exit("north", "Bronze Key")
    key = Weapon(name="Bronze Key", description="", damage=0)
    player = Player(name="hero", hp=100)
    player.inventory.add(key)

    assert is_exit_locked(room, "north", player) is False

def test_trade_with_ally_returns_missing_message_when_player_lacks_required_items():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword", "Wooden Shield"], reward=coin)
    player = Player(name="hero", hp=100)

    message = trade_with_ally(ally, player)

    assert message == "Chiron shakes their head. \"You're still missing: Wooden Sword, Wooden Shield.\""

def test_trade_with_ally_does_not_add_reward_when_items_missing():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)

    trade_with_ally(ally, player)

    assert coin not in player.inventory.items

def test_trade_with_ally_removes_required_items_from_player_inventory_when_complete():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    trade_with_ally(ally, player)

    assert sword not in player.inventory.items

def test_trade_with_ally_adds_reward_to_player_inventory_when_complete():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    trade_with_ally(ally, player)

    assert coin in player.inventory.items

def test_trade_with_ally_returns_confirmation_message_when_complete():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    message = trade_with_ally(ally, player)

    assert message == "Chiron nods, accepting each item in turn. \"You've done well.\" They hand you the Charon's Coin."

def test_trade_with_ally_marks_trade_completed_on_success():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    trade_with_ally(ally, player)

    assert ally.trade_completed is True

def test_trade_with_ally_does_not_mark_trade_completed_when_items_missing():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)

    trade_with_ally(ally, player)

    assert ally.trade_completed is False

def test_trade_with_ally_returns_unequip_message_when_required_item_is_equipped():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)

    message = trade_with_ally(ally, player)

    assert message == "Chiron shakes their head. \"You'll need to unequip: Wooden Sword.\""

def test_trade_with_ally_does_not_add_reward_when_required_item_is_equipped():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)

    trade_with_ally(ally, player)

    assert coin not in player.inventory.items

def test_trade_with_ally_does_not_remove_equipped_item_when_blocked():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)

    trade_with_ally(ally, player)

    assert sword in player.inventory.items

def test_trade_with_ally_returns_nothing_to_trade_message_when_ally_has_no_required_items():
    ally = Ally(name="Hermes")
    player = Player(name="hero", hp=100)

    message = trade_with_ally(ally, player)

    assert message == "Hermes has nothing to trade."

def test_trade_with_ally_returns_nothing_to_trade_message_when_ally_has_no_reward():
    ally = Ally(name="Prometheus", required_items=["Fire"])
    player = Player(name="hero", hp=100)

    message = trade_with_ally(ally, player)

    assert message == "Prometheus has nothing to trade."

def test_trade_with_ally_appends_post_trade_message_when_set():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin, post_trade_message="Safe travels, hero.")
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    message = trade_with_ally(ally, player)

    assert message == "Chiron nods, accepting each item in turn. \"You've done well.\" They hand you the Charon's Coin.\n\nSafe travels, hero."

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

def test_find_floor_for_room_returns_floor_name_when_room_present():
    room_a = Room("A")
    all_floors = {"floor_0": {"A": room_a}}
    assert find_floor_for_room(room_a, all_floors) == "floor_0"

def test_find_floor_for_room_returns_none_when_room_not_present():
    room_a = Room("A")
    all_floors = {"floor_0": {}}
    assert find_floor_for_room(room_a, all_floors) is None

def test_find_floor_for_room_finds_room_in_second_floor():
    room_a = Room("A")
    room_b = Room("B")
    all_floors = {"floor_0": {"A": room_a}, "floor_1": {"B": room_b}}
    assert find_floor_for_room(room_b, all_floors) == "floor_1"

def test_display_map_single_room_with_no_exits():
    room = Room("A")
    player = Player(name="hero", hp=10)
    assert display_map(room, player) == "\nA"

def test_display_map_lists_unlocked_exit():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    player = Player(name="hero", hp=10)
    assert display_map(room_a, player) == "\nA\n  north -> B\n\nB"

def test_display_map_shows_locked_door_for_locked_exit():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    room_a.lock_exit("north", "Key")
    player = Player(name="hero", hp=10)
    assert display_map(room_a, player) == "\nA\n  north -> Locked Door"

def test_display_map_does_not_explore_beyond_locked_exit():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    room_a.lock_exit("north", "Key")
    player = Player(name="hero", hp=10)
    assert "B" not in display_map(room_a, player)

def test_display_map_does_not_revisit_room_in_cycle():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    room_b.connect("south", room_a)
    player = Player(name="hero", hp=10)
    assert display_map(room_a, player) == "\nA\n  north -> B\n\nB\n  south -> A"

def test_display_local_exits_with_no_exits_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=10)
    assert display_local_exits(room, player) == "There are no exits from this room."

def test_display_local_exits_lists_unlocked_exit():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    player = Player(name="hero", hp=10)
    assert display_local_exits(room_a, player) == "north -> B"

def test_display_local_exits_shows_locked_door_for_locked_exit():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    room_a.lock_exit("north", "Key")
    player = Player(name="hero", hp=10)
    assert display_local_exits(room_a, player) == "north -> Locked Door"

def test_display_local_exits_lists_multiple_exits():
    room_a = Room("A")
    room_b = Room("B")
    room_c = Room("C")
    room_a.connect("north", room_b)
    room_a.connect("east", room_c)
    player = Player(name="hero", hp=10)
    assert display_local_exits(room_a, player) == "north -> B\neast -> C"

def test_display_local_exits_does_not_recurse_into_connected_rooms():
    room_a = Room("A")
    room_b = Room("B")
    room_c = Room("C")
    room_a.connect("north", room_b)
    room_b.connect("east", room_c)
    player = Player(name="hero", hp=10)
    assert display_local_exits(room_a, player) == "north -> B"

def test_choose_ancestry_returns_chosen_key_when_valid(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "basic")
    assert choose_ancestry() == "basic"

def test_choose_ancestry_is_case_insensitive(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "BASIC")
    assert choose_ancestry() == "basic"

def test_choose_ancestry_strips_whitespace_from_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "  basic  ")
    assert choose_ancestry() == "basic"

def test_choose_ancestry_reprompts_on_invalid_choice_before_accepting_valid_one(monkeypatch):
    responses = iter(["nonsense", "basic"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_ancestry() == "basic"

def test_choose_ancestry_prints_error_message_for_invalid_choice(monkeypatch, capsys):
    responses = iter(["nonsense", "basic"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    choose_ancestry()
    captured = capsys.readouterr()
    assert "That name means nothing to me. Choose from the list above." in captured.out

def test_choose_ancestry_prints_each_ancestry_option(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt="": "basic")
    choose_ancestry()
    captured = capsys.readouterr()
    assert "basic - No lineage (ATK 3 / DEF 1 / HP 20)" in captured.out
    assert "odysseus - Descendant of Odysseus (ATK 3 / DEF 1 / HP 20)" in captured.out

def test_create_player_sets_name():
    player = create_player("Hero", "basic")
    assert player.name == "Hero"

def test_create_player_sets_stats_from_ancestry():
    player = create_player("Hero", "basic")
    assert player.hp == 20
    assert player.attack_damage == 3
    assert player.armour == 1

def test_create_player_sets_ancestry_label():
    player = create_player("Hero", "basic")
    assert player.ancestry_label == "No lineage"

def test_create_player_with_bonus_skill_point_ancestry_grants_skill_point():
    player = create_player("Hero", "odysseus")
    assert player.skill_tree.skill_points == 1

def test_create_player_without_bonus_skill_point_ancestry_grants_no_skill_point():
    player = create_player("Hero", "basic")
    assert player.skill_tree.skill_points == 0

def test_create_player_sets_intellect_from_ancestry():
    player = create_player("Hero", "athena")
    assert player.intellect == 5

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

def test_handle_examine_with_examine_text_returns_examine_text():
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.")
    player = Player(name="Hero", hp=50)
    message = handle_examine(room, player)
    assert "The stonework here looks subtly disturbed." in message

def test_handle_examine_without_examine_text_returns_default_message():
    room = Room("A")
    player = Player(name="Hero", hp=50)
    message = handle_examine(room, player)
    assert message == "You look closer, but find nothing you hadn't already noticed."

def test_handle_examine_reveals_hidden_exit_in_room_exits():
    room = Room("Styx Crossing")
    vault = Room("Sunken Vault")
    room.add_hidden_exit("down", vault)
    player = Player(name="Hero", hp=50)
    handle_examine(room, player)
    assert room.get_exit("down") is vault

def test_handle_examine_appends_message_naming_revealed_direction():
    room = Room("Styx Crossing")
    vault = Room("Sunken Vault")
    room.add_hidden_exit("down", vault)
    player = Player(name="Hero", hp=50)
    message = handle_examine(room, player)
    assert "Your search reveals a hidden passage: down." in message

def test_handle_examine_with_no_hidden_exits_does_not_mention_hidden_passage():
    room = Room("A")
    player = Player(name="Hero", hp=50)
    message = handle_examine(room, player)
    assert "hidden passage" not in message

def test_handle_examine_reveals_multiple_hidden_exits_lists_all_directions():
    room = Room("A")
    b = Room("B")
    c = Room("C")
    room.add_hidden_exit("down", b)
    room.add_hidden_exit("up", c)
    player = Player(name="Hero", hp=50)
    message = handle_examine(room, player)
    assert "Your search reveals a hidden passage: down, up." in message

def test_handle_examine_with_sufficient_intellect_returns_examine_text():
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.", required_intellect=3)
    player = Player(name="Hero", hp=50)
    player.intellect = 3
    message = handle_examine(room, player)
    assert "The stonework here looks subtly disturbed." in message

def test_handle_examine_with_insufficient_intellect_returns_cant_make_sense_message():
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.", required_intellect=3)
    player = Player(name="Hero", hp=50)
    player.intellect = 2
    message = handle_examine(room, player)
    assert "There's something here, but you can't quite make sense of it." in message

def test_handle_examine_with_insufficient_intellect_does_not_reveal_examine_text():
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.", required_intellect=3)
    player = Player(name="Hero", hp=50)
    player.intellect = 2
    message = handle_examine(room, player)
    assert "The stonework here looks subtly disturbed." not in message

def test_handle_examine_with_insufficient_intellect_still_reveals_hidden_exits():
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.", required_intellect=3)
    vault = Room("Sunken Vault")
    room.add_hidden_exit("down", vault)
    player = Player(name="Hero", hp=50)
    player.intellect = 0
    handle_examine(room, player)
    assert room.get_exit("down") is vault