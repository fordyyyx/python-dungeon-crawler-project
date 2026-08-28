from dungeon_crawler.characters import Player, Enemy, Ally
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, Consumable, QuestItem, Weapon
from dungeon_crawler.engine import pick_up, resolve_combat_round, handle_enemy_defeat, is_exit_locked, trade_with_ally, print_room, display_map, find_floor_for_room, display_local_exits, find_item_by_name, handle_dev_command, create_player, handle_combat_command, flee_combat, display_skills

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

    print_room(room)

    captured = capsys.readouterr()
    assert "Armoury: A dusty room full of old weapons." in captured.out

def test_print_room_with_items_prints_item_names(capsys):
    room = Room("Armoury")
    room.add_item(Weapon(name="Bronze Xiphos", description="", damage=3))

    print_room(room)

    captured = capsys.readouterr()
    assert "You see: Bronze Xiphos" in captured.out

def test_print_room_with_no_items_does_not_print_you_see(capsys):
    room = Room("Armoury")

    print_room(room)

    captured = capsys.readouterr()
    assert "You see" not in captured.out

def test_print_room_with_enemy_prints_enemy_description(capsys):
    room = Room("Armoury")
    room.add_enemy(Enemy(name="Goblin", hp=10, description="A snarling goblin."))

    print_room(room)

    captured = capsys.readouterr()
    assert "A Goblin blocks your path! A snarling goblin." in captured.out

def test_print_room_with_no_enemies_does_not_print_blocks_your_path(capsys):
    room = Room("Armoury")

    print_room(room)

    captured = capsys.readouterr()
    assert "blocks your path" not in captured.out

def test_print_room_with_ally_prints_ally_description(capsys):
    room = Room("Armoury")
    room.add_ally(Ally(name="Chiron", description="A wise centaur."))

    print_room(room)

    captured = capsys.readouterr()
    assert "Chiron is here. A wise centaur." in captured.out

def test_print_room_with_no_allies_does_not_print_is_here(capsys):
    room = Room("Armoury")

    print_room(room)

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
    handle_dev_command("add wooden sword", player, room)
    item_names = [item.name for item in player.inventory.items]
    assert "Wooden Sword" in item_names

def test_handle_dev_command_add_known_item_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("add wooden sword", player, room)
    assert message == "[DEV] Added Wooden Sword to inventory."

def test_handle_dev_command_add_unknown_item_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("add nonexistent thing", player, room)
    assert message == "[DEV] No known item named 'nonexistent thing'."

def test_handle_dev_command_add_unknown_item_does_not_add_to_inventory():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("add nonexistent thing", player, room)
    assert len(player.inventory) == 0

def test_handle_dev_command_set_hp_updates_player_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set hp 50", player, room)
    assert player.hp == 50

def test_handle_dev_command_set_hp_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("set hp 50", player, room)
    assert message == "[DEV] HP set to 50 (max HP: 100)"

def test_handle_dev_command_set_hp_with_invalid_value_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("set hp abc", player, room)
    assert message == "[DEV] Invalid HP value."

def test_handle_dev_command_set_hp_with_invalid_value_does_not_change_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set hp abc", player, room)
    assert player.hp == 100

def test_handle_dev_command_set_hp_above_max_hp_raises_max_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set hp 150", player, room)
    assert player.max_hp == 150

def test_handle_dev_command_set_hp_above_max_hp_returns_updated_max_hp_in_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("set hp 150", player, room)
    assert message == "[DEV] HP set to 150 (max HP: 150)"

def test_handle_dev_command_set_hp_below_max_hp_does_not_change_max_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set hp 50", player, room)
    assert player.max_hp == 100

def test_handle_dev_command_set_maxhp_updates_max_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set maxhp 150", player, room)
    assert player.max_hp == 150

def test_handle_dev_command_set_maxhp_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("set maxhp 150", player, room)
    assert message == "[DEV] Max HP set to 150"

def test_handle_dev_command_set_maxhp_with_invalid_value_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("set maxhp abc", player, room)
    assert message == "[DEV] Invalid max HP value."

def test_handle_dev_command_set_maxhp_with_invalid_value_does_not_change_max_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set maxhp abc", player, room)
    assert player.max_hp == 100

def test_handle_dev_command_set_maxhp_below_current_hp_clamps_hp_down():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set maxhp 50", player, room)
    assert player.hp == 50

def test_handle_dev_command_set_maxhp_above_current_hp_does_not_change_hp():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("set maxhp 150", player, room)
    assert player.hp == 100

def test_handle_dev_command_unlock_all_clears_locked_exits():
    room = Room("A")
    room.lock_exit("north", "Key")
    room.lock_exit("east", "Shield")
    player = Player(name="hero", hp=100)
    handle_dev_command("unlock all", player, room)
    assert room.locked_exits == {}

def test_handle_dev_command_unlock_all_returns_message_listing_unlocked_directions():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    message = handle_dev_command("unlock all", player, room)
    assert message == "[DEV] Unlocked: north."

def test_handle_dev_command_unlock_all_with_no_locked_exits_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=100)
    message = handle_dev_command("unlock all", player, room)
    assert message == "[DEV] No locked exits in this room."

def test_handle_dev_command_unlock_direction_removes_lock():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    handle_dev_command("unlock north", player, room)
    assert "north" not in room.locked_exits

def test_handle_dev_command_unlock_direction_returns_confirmation_message():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    message = handle_dev_command("unlock north", player, room)
    assert message == "[DEV] Unlocked exit: north."

def test_handle_dev_command_unlock_direction_not_locked_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=100)
    message = handle_dev_command("unlock north", player, room)
    assert message == "[DEV] north is not a locked exit here."

def test_handle_dev_command_skillpoints_increments_skill_points():
    player = Player(name="hero", hp=100)
    room = Room("A")
    handle_dev_command("skillpoints", player, room)
    assert player.skill_tree.skill_points == 1

def test_handle_dev_command_skillpoints_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("skillpoints", player, room)
    assert message == "[DEV] Skill points: 1."

def test_handle_dev_command_help_returns_help_text():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("help", player, room)
    assert message == (
        "[DEV] Commands: dev add <item>, dev set hp <n>, "
        "dev unlock <direction>, dev unlock all, dev skillpoints"
    )

def test_handle_dev_command_unrecognised_command_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    message = handle_dev_command("frobnicate", player, room)
    assert message == "[DEV] Unrecognised dev command: frobnicate. Try 'dev help'."

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

    assert message == "No item named' nonexistent' in inventory."

def test_handle_combat_command_use_item_triggers_enemy_counterattack_when_enemy_alive():
    player = Player(name="Hero", hp=50, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=5)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, room)

    assert message == "Hero uses Potion, healing 5 HP.\nGoblin attacks Hero for 5 damage."
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