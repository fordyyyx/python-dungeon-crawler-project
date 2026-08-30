from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Armour, Consumable, QuestItem, Weapon
from dungeon_crawler.engine import pick_up, resolve_combat_round, handle_enemy_defeat, is_exit_locked, trade_with_ally, print_room, display_map, find_floor_for_room, display_local_exits, find_item_by_name, handle_dev_command, create_player, handle_combat_command, flee_combat, display_skills, resolve_attack_and_check_defeat, handle_dev_set, find_enemy_by_name, find_ally_by_name, handle_dev_kill, find_room_by_name_ci, handle_dev_remove, handle_dev_remove_all, handle_dev_clear_room, format_hp_line

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

def test_resolve_combat_round_reduces_enemy_hp():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert enemy.hp == 10

def test_resolve_combat_round_reduces_player_hp_when_enemy_survives():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert player.hp == 95

def test_resolve_combat_round_returns_both_attack_messages_when_both_survive():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert "Hero attacks Goblin" in result
    assert "Goblin attacks Hero" in result

def test_resolve_combat_round_enemy_defeated_does_not_counter_attack():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert player.hp == 100

def test_resolve_combat_round_returns_fallen_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert "Goblin has been defeated." in result

def test_resolve_combat_round_returns_fallen_message_when_player_defeated():
    player = Player(name="Hero", hp=5, attack_damage=1)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=20)

    result = resolve_combat_round(player, enemy)

    assert "Hero has fallen." in result

def test_resolve_combat_round_returns_full_message_when_both_survive():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert result == "Hero attacks Goblin for 10 damage.\nGoblin attacks Hero for 5 damage.\nHero: 95/100 HP  |  Goblin: 10/20 HP"

def test_resolve_combat_round_returns_full_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert result == "Hero attacks Goblin for 20 damage.\nGoblin has been defeated.\nHero: 100/100 HP"

def test_handle_enemy_defeat_removes_enemy_from_room():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert enemy not in room.enemies

def test_handle_enemy_defeat_adds_loot_to_room():
    room = Room("Armoury")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert sword in room.items

def test_handle_enemy_defeat_with_no_loot_adds_nothing_to_room():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert room.items == []

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

def test_find_item_by_name_returns_item_for_known_name():
    item = find_item_by_name("wooden sword")
    assert item is not None
    assert item.name == "Wooden Sword"

def test_find_item_by_name_is_case_insensitive():
    item = find_item_by_name("WOODEN SWORD")
    assert item is not None
    assert item.name == "Wooden Sword"

def test_find_item_by_name_returns_none_for_unknown_name():
    item = find_item_by_name("nonexistent item")
    assert item is None

def test_find_item_by_name_returns_new_instance_each_call():
    item1 = find_item_by_name("wooden sword")
    item2 = find_item_by_name("wooden sword")
    assert item1 is not item2

def test_handle_dev_command_add_known_item_adds_to_inventory():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    handle_dev_command("add wooden sword", player, room, dungeon)
    item_names = [item.name for item in player.inventory.items]
    assert "Wooden Sword" in item_names

def test_handle_dev_command_add_known_item_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("add wooden sword", player, room, dungeon)
    assert message == "[DEV] Added Wooden Sword to inventory."
    assert new_room is None

def test_handle_dev_command_add_unknown_item_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("add nonexistent thing", player, room, dungeon)
    assert message == "[DEV] No known item named 'nonexistent thing'."

def test_handle_dev_command_add_unknown_item_does_not_add_to_inventory():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    handle_dev_command("add nonexistent thing", player, room, dungeon)
    assert len(player.inventory) == 0

def test_handle_dev_command_set_dispatches_to_handle_dev_set():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("set atk 50", player, room, dungeon)
    assert player.attack_damage == 50
    assert message == "[DEV] atk set to 50."
    assert new_room is None

def test_handle_dev_command_set_with_missing_value_returns_usage_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("set atk", player, room, dungeon)
    assert message == "[DEV] Usage: dev set <stat> <value>"

def test_handle_dev_command_unlock_all_clears_locked_exits():
    room = Room("A")
    room.lock_exit("north", "Key")
    room.lock_exit("east", "Shield")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    handle_dev_command("unlock all", player, room, dungeon)
    assert room.locked_exits == {}

def test_handle_dev_command_unlock_all_returns_message_listing_unlocked_directions():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock all", player, room, dungeon)
    assert message == "[DEV] Unlocked: north."

def test_handle_dev_command_unlock_all_with_no_locked_exits_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock all", player, room, dungeon)
    assert message == "[DEV] No locked exits in this room."

def test_handle_dev_command_unlock_direction_removes_lock():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    handle_dev_command("unlock north", player, room, dungeon)
    assert "north" not in room.locked_exits

def test_handle_dev_command_unlock_direction_returns_confirmation_message():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock north", player, room, dungeon)
    assert message == "[DEV] Unlocked exit: north."

def test_handle_dev_command_unlock_direction_not_locked_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock north", player, room, dungeon)
    assert message == "[DEV] north is not a locked exit here."

def test_handle_dev_command_help_returns_help_text():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("help", player, room, dungeon)
    assert message == (
        "[DEV] Commands: dev add <item>, dev set hp <n>, "
        "dev unlock <direction>, dev unlock all, dev skillpoints"
    )

def test_handle_dev_command_unrecognised_command_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("frobnicate", player, room, dungeon)
    assert message == "[DEV] Unrecognised dev command: frobnicate. Try 'dev help'."

def test_handle_dev_command_spawn_enemy_adds_to_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn minotaur", player, room, dungeon)
    assert message == "[DEV] Spawned Minotaur."
    enemy_names = [enemy.name for enemy in room.enemies]
    assert "Minotaur" in enemy_names

def test_handle_dev_command_spawn_ally_adds_to_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn chiron", player, room, dungeon)
    assert message == "[DEV] Spawned Chiron."
    ally_names = [ally.name for ally in room.allies]
    assert "Chiron" in ally_names

def test_handle_dev_command_spawn_unknown_name_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn nonexistent", player, room, dungeon)
    assert message == "[DEV] No known character names nonexistent."

def test_handle_dev_command_remove_removes_named_enemy():
    player = Player(name="hero", hp=100)
    room = Room("A")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)
    dungeon = Map()
    message, new_room = handle_dev_command("remove goblin", player, room, dungeon)
    assert message == "[DEV] Removed Goblin."
    assert enemy not in room.enemies

def test_handle_dev_command_remove_all_removes_every_matching_enemy():
    player = Player(name="hero", hp=100)
    room = Room("A")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    dungeon = Map()
    message, new_room = handle_dev_command("remove all goblin", player, room, dungeon)
    assert message == "[DEV] Removed 2 instance(s) of 'goblin'."
    assert room.enemies == []

def test_handle_dev_command_clear_room_removes_all_enemies_and_allies():
    player = Player(name="hero", hp=100)
    room = Room("A")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_ally(Ally(name="Chiron"))
    dungeon = Map()
    message, new_room = handle_dev_command("clear room", player, room, dungeon)
    assert message == "[DEV] Cleared room: removed 1 enemies and 1 allies."
    assert room.enemies == []
    assert room.allies == []

def test_handle_dev_command_kill_defeats_first_enemy_in_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)
    dungeon = Map()
    message, new_room = handle_dev_command("kill", player, room, dungeon)
    assert message == "[DEV] Killed Goblin."
    assert enemy not in room.enemies

def test_handle_dev_command_kill_with_no_enemy_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("kill", player, room, dungeon)
    assert message == "[DEV] No enemy here to kill."

def test_handle_dev_command_teleport_to_known_room_returns_target_room():
    player = Player(name="hero", hp=100)
    room = Room("Start")
    target = Room("Alpha")
    dungeon = Map()
    dungeon.add_room(target)
    message, new_room = handle_dev_command("teleport Alpha", player, room, dungeon)
    assert message == "[DEV] Teleported to Alpha."
    assert new_room is target

def test_handle_dev_command_teleport_to_unknown_room_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("Start")
    dungeon = Map()
    message, new_room = handle_dev_command("teleport Nowhere", player, room, dungeon)
    assert message == "[DEV] No room named 'Nowhere'."
    assert new_room is None

def test_handle_dev_command_teleport_clears_combat_state():
    player = Player(name="hero", hp=100)
    player.in_combat = True
    player.current_target = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Start")
    target = Room("Alpha")
    dungeon = Map()
    dungeon.add_room(target)
    handle_dev_command("teleport Alpha", player, room, dungeon)
    assert player.in_combat is False
    assert player.current_target is None

def test_handle_dev_command_learn_invests_a_free_skill_point():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("learn defence", player, room, dungeon)
    assert message == "[DEV] hero gains +2 armour from Hardened Skin."
    assert player.armour == 2
    assert player.skill_tree.skill_points == 0

def test_handle_dev_command_learn_with_invalid_path_refunds_the_free_skill_point():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    handle_dev_command("learn nonexistent", player, room, dungeon)
    assert player.skill_tree.skill_points == 0

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

def test_flee_combat_clean_escape_when_enemy_at_zero_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0

    message = flee_combat(player, enemy)

    assert message == "You disengage cleanly, leaving the Goblin behind."

def test_flee_combat_clean_escape_does_not_damage_player():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0

    flee_combat(player, enemy)

    assert player.hp == 50

def test_flee_combat_gets_hit_when_enemy_at_full_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    message = flee_combat(player, enemy)

    assert message == "You disengage, but the Goblin gets a hit in as you go - 5 damage."
    assert player.hp == 45

def test_flee_combat_hit_can_defeat_player():
    player = Player(name="Hero", hp=5, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=20)

    message = flee_combat(player, enemy)

    assert message == "You disengage, but the Goblin gets a hit in as you go - 20 damage.\nHero has fallen. Game Over."
    assert player.hp == 0

def test_display_skills_shows_next_skill_for_each_path():
    player = Player(name="Hero", hp=50, attack_damage=10)
    result = display_skills(player)
    assert "Attack: next unlock is Iron Grip - Steadier strikes." in result
    assert "Defence: next unlock is Hardened Skin - Blows land softer." in result
    assert "Abilities: next unlock is Twin Strike - A second blow follows the first, fast and true." in result

def test_display_skills_shows_fully_unlocked_when_path_exhausted():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 3
    player.skill_tree.invest("attack", player)
    player.skill_tree.invest("attack", player)
    player.skill_tree.invest("attack", player)
    result = display_skills(player)
    assert "Attack: fully unlocked" in result

def test_display_skills_shows_available_skill_points():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 2
    result = display_skills(player)
    assert "Skill Points available: 2" in result

def test_handle_combat_command_attack_reduces_enemy_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    handle_combat_command("attack", player, enemy, room)

    assert enemy.hp == 10

def test_handle_combat_command_attack_returns_combat_round_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("attack", player, enemy, room)

    assert "Hero attacks Goblin for 10 damage." in message

def test_handle_combat_command_attack_when_enemy_defeated_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_combat_command("attack", player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_combat_command_attack_when_enemy_defeated_removes_enemy_from_room():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_combat_command("attack", player, enemy, room)

    assert enemy not in room.enemies

def test_handle_combat_command_attack_when_enemy_survives_does_not_clear_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=5)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("attack", player, enemy, room)

    assert player.in_combat is True
    assert player.current_target is enemy

def test_handle_combat_command_flee_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("flee", player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_combat_command_flee_returns_flee_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("flee", player, enemy, room)

    assert message == "You disengage cleanly, leaving the Goblin behind."

def test_handle_combat_command_use_item_heals_player():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    handle_combat_command("use potion", player, enemy, room)

    assert player.hp == 40

def test_handle_combat_command_use_item_returns_use_message_when_enemy_not_alive():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, room)

    assert message == "Hero uses Potion, healing 10 HP."

def test_handle_combat_command_use_item_with_invalid_name_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("use nonexistent", player, enemy, room)

    assert message == "No item named 'nonexistent' in inventory."

def test_handle_combat_command_use_item_with_invalid_name_does_not_trigger_enemy_counterattack():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use nonexistent", player, enemy, room)

    assert message == "No item named 'nonexistent' in inventory."
    assert player.hp == 50

def test_handle_combat_command_use_item_triggers_enemy_counterattack_when_enemy_alive():
    player = Player(name="Hero", hp=50, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=5)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, room)

    assert message == "Hero uses Potion, healing 5 HP.\nGoblin attacks Hero for 5 damage.\nHero: 45/50 HP  |  Goblin: 20/20 HP"
    assert player.hp == 45

def test_handle_combat_command_use_item_enemy_counterattack_can_defeat_player_clears_combat_state():
    player = Player(name="Hero", hp=5, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=1)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=20)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("use potion", player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None
    assert player.hp == 0

def test_handle_combat_command_stats_returns_player_stats():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("stats", player, enemy, room)

    assert message.startswith("Hero ():")

def test_handle_combat_command_skills_returns_skills_display():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("skills", player, enemy, room)

    assert "Skill Points available: 0" in message

def test_handle_combat_command_learn_invests_skill():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 1
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("learn defence", player, enemy, room)

    assert player.armour == 2
    assert message == "Hero gains +2 armour from Hardened Skin."

def test_handle_combat_command_learn_with_no_skill_points_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("learn defence", player, enemy, room)

    assert message == "No skill points available"

def test_handle_combat_command_inventory_returns_inventory_display():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("inventory", player, enemy, room)

    assert message == "Your inventory is empty."

def test_handle_combat_command_unrecognised_command_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("dance", player, enemy, room)

    assert message == "You can't do that mid-combat. Try 'attack', 'flee', 'use <item>', 'stats', 'skills', or 'inventory'."

def test_resolve_attack_and_check_defeat_reduces_enemy_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    resolve_attack_and_check_defeat(player, enemy, room)

    assert enemy.hp == 10

def test_resolve_attack_and_check_defeat_returns_combat_round_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = resolve_attack_and_check_defeat(player, enemy, room)

    assert "Hero attacks Goblin for 10 damage." in message

def test_resolve_attack_and_check_defeat_when_enemy_defeated_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_resolve_attack_and_check_defeat_when_enemy_defeated_removes_enemy_from_room():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, room)

    assert enemy not in room.enemies

def test_resolve_attack_and_check_defeat_when_enemy_survives_does_not_clear_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=5)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    resolve_attack_and_check_defeat(player, enemy, room)

    assert player.in_combat is True
    assert player.current_target is enemy

def test_handle_dev_set_updates_aliased_stat():
    player = Player(name="hero", hp=100, attack_damage=10)
    handle_dev_set("atk", "50", player)
    assert player.attack_damage == 50

def test_handle_dev_set_returns_confirmation_message():
    player = Player(name="hero", hp=100, attack_damage=10)
    message = handle_dev_set("atk", "50", player)
    assert message == "[DEV] atk set to 50."

def test_handle_dev_set_skillpoints_sets_exact_value():
    player = Player(name="hero", hp=100)
    player.skill_tree.skill_points = 5
    handle_dev_set("skillpoints", "3", player)
    assert player.skill_tree.skill_points == 3

def test_handle_dev_set_returns_skillpoints_message():
    player = Player(name="hero", hp=100)
    message = handle_dev_set("skillpoints", "3", player)
    assert message == "[DEV] Skill points set to 3."

def test_handle_dev_set_unknown_stat_returns_error_message():
    player = Player(name="hero", hp=100)
    message = handle_dev_set("nonsense", "5", player)
    assert message == "[DEV] Unknown stat 'nonsense'."

def test_handle_dev_set_invalid_value_returns_error_message():
    player = Player(name="hero", hp=100)
    message = handle_dev_set("atk", "abc", player)
    assert message == "[DEV] Invalid value 'abc'."

def test_handle_dev_set_hp_above_max_hp_raises_max_hp():
    player = Player(name="hero", hp=100)
    handle_dev_set("hp", "150", player)
    assert player.max_hp == 150

def test_handle_dev_set_hp_below_max_hp_does_not_change_max_hp():
    player = Player(name="hero", hp=100)
    handle_dev_set("hp", "50", player)
    assert player.max_hp == 100

def test_handle_dev_set_maxhp_below_current_hp_clamps_hp_down():
    player = Player(name="hero", hp=100)
    handle_dev_set("maxhp", "50", player)
    assert player.hp == 50

def test_handle_dev_set_maxhp_above_current_hp_does_not_change_hp():
    player = Player(name="hero", hp=100)
    handle_dev_set("maxhp", "150", player)
    assert player.hp == 100

def test_find_enemy_by_name_returns_enemy_for_known_name():
    enemy = find_enemy_by_name("minotaur")
    assert enemy is not None
    assert enemy.name == "Minotaur"

def test_find_enemy_by_name_is_case_insensitive():
    enemy = find_enemy_by_name("MINOTAUR")
    assert enemy is not None
    assert enemy.name == "Minotaur"

def test_find_enemy_by_name_returns_none_for_unknown_name():
    enemy = find_enemy_by_name("nonexistent")
    assert enemy is None

def test_find_enemy_by_name_returns_new_instance_each_call():
    enemy1 = find_enemy_by_name("minotaur")
    enemy2 = find_enemy_by_name("minotaur")
    assert enemy1 is not enemy2

def test_find_ally_by_name_returns_ally_for_known_name():
    ally = find_ally_by_name("chiron")
    assert ally is not None
    assert ally.name == "Chiron"

def test_find_ally_by_name_is_case_insensitive():
    ally = find_ally_by_name("CHIRON")
    assert ally is not None
    assert ally.name == "Chiron"

def test_find_ally_by_name_returns_none_for_unknown_name():
    ally = find_ally_by_name("nonexistent")
    assert ally is None

def test_find_ally_by_name_returns_new_instance_each_call():
    ally1 = find_ally_by_name("chiron")
    ally2 = find_ally_by_name("chiron")
    assert ally1 is not ally2

def test_handle_dev_kill_prefers_players_current_target():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    other_enemy = Enemy(name="Other", hp=10, attack_damage=5)
    target_enemy = Enemy(name="Target", hp=10, attack_damage=5)
    room.add_enemy(other_enemy)
    room.add_enemy(target_enemy)
    player.current_target = target_enemy

    message = handle_dev_kill(player, room)

    assert message == "[DEV] Killed Target."
    assert target_enemy not in room.enemies
    assert other_enemy in room.enemies

def test_handle_dev_kill_falls_back_to_first_enemy_in_room():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)

    message = handle_dev_kill(player, room)

    assert message == "[DEV] Killed Goblin."

def test_handle_dev_kill_with_no_enemies_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_kill(player, room)

    assert message == "[DEV] No enemy here to kill."

def test_handle_dev_kill_includes_loot_in_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)

    message = handle_dev_kill(player, room)

    assert message == "[DEV] Killed Goblin. Dropped: Bronze Xiphos."

def test_handle_dev_kill_with_no_loot_does_not_include_dropped_text():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)

    message = handle_dev_kill(player, room)

    assert "Dropped" not in message

def test_handle_dev_kill_clears_combat_state():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)
    player.in_combat = True
    player.current_target = enemy

    handle_dev_kill(player, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_dev_kill_moves_loot_into_room():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)

    handle_dev_kill(player, room)

    assert sword in room.items

def test_find_room_by_name_ci_returns_room_for_known_name():
    dungeon = Map()
    room = Room("Alpha")
    dungeon.add_room(room)
    found = find_room_by_name_ci(dungeon, "Alpha")
    assert found is room

def test_find_room_by_name_ci_is_case_insensitive():
    dungeon = Map()
    room = Room("Alpha")
    dungeon.add_room(room)
    found = find_room_by_name_ci(dungeon, "ALPHA")
    assert found is room

def test_find_room_by_name_ci_returns_none_for_unknown_name():
    dungeon = Map()
    found = find_room_by_name_ci(dungeon, "Nowhere")
    assert found is None

def test_handle_dev_remove_removes_enemy_from_room():
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)

    message = handle_dev_remove("goblin", room)

    assert message == "[DEV] Removed Goblin."
    assert enemy not in room.enemies

def test_handle_dev_remove_removes_ally_from_room():
    room = Room("Arena")
    ally = Ally(name="Chiron")
    room.add_ally(ally)

    message = handle_dev_remove("chiron", room)

    assert message == "[DEV] Removed Chiron."
    assert ally not in room.allies

def test_handle_dev_remove_not_found_returns_message():
    room = Room("Arena")

    message = handle_dev_remove("nonexistent", room)

    assert message == "[DEV] No character named 'nonexistent' found here."

def test_handle_dev_remove_all_removes_every_matching_enemy():
    room = Room("Arena")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_enemy(Enemy(name="Other", hp=10, attack_damage=5))

    message = handle_dev_remove_all("goblin", room)

    assert message == "[DEV] Removed 2 instance(s) of 'goblin'."
    remaining_names = [enemy.name for enemy in room.enemies]
    assert remaining_names == ["Other"]

def test_handle_dev_remove_all_removes_matching_allies():
    room = Room("Arena")
    room.add_ally(Ally(name="Chiron"))
    room.add_ally(Ally(name="Chiron"))

    message = handle_dev_remove_all("chiron", room)

    assert message == "[DEV] Removed 2 instance(s) of 'chiron'."
    assert room.allies == []

def test_handle_dev_remove_all_not_found_returns_message():
    room = Room("Arena")

    message = handle_dev_remove_all("nonexistent", room)

    assert message == "[DEV] No character named 'nonexistent' found here."

def test_handle_dev_clear_room_removes_all_enemies_and_allies():
    room = Room("Arena")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_ally(Ally(name="Chiron"))

    message = handle_dev_clear_room(room)

    assert message == "[DEV] Cleared room: removed 1 enemies and 1 allies."
    assert room.enemies == []
    assert room.allies == []

def test_handle_dev_clear_room_with_empty_room_returns_zero_counts():
    room = Room("Arena")

    message = handle_dev_clear_room(room)

    assert message == "[DEV] Cleared room: removed 0 enemies and 0 allies."

def test_format_hp_line_returns_expected_format():
    player = Player(name="Hero", hp=95, attack_damage=10)
    player.max_hp = 100
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    enemy.max_hp = 20

    line = format_hp_line(player, enemy)

    assert line == "Hero: 95/100 HP  |  Goblin: 10/20 HP"