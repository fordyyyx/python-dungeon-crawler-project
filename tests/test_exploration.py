from dungeon_crawler.characters import Player, Ally, Companion, Enemy
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, QuestItem, Weapon, Consumable
from dungeon_crawler.exploration import start_duel, pick_up, is_exit_locked, trade_with_ally, recruit_companion, dismiss_companion, repair_item, display_map, find_floor_for_room, display_local_exits, handle_examine, get_exit_guardian, take_all, take_all_from_ally, check_equippable, get_uncleared_reasons, get_uncleared_rooms, has_unfinished_trade, get_undiscovered_rooms

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

def test_trade_with_ally_with_silver_tongue_does_not_remove_required_items():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    player.has_silver_tongue = True
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    trade_with_ally(ally, player)

    assert sword in player.inventory.items

def test_trade_with_ally_with_silver_tongue_still_adds_reward():
    coin = QuestItem(name="Charon's Coin", description="")
    ally = Ally(name="Chiron", required_items=["Wooden Sword"], reward=coin)
    player = Player(name="hero", hp=100)
    player.has_silver_tongue = True
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    trade_with_ally(ally, player)

    assert coin in player.inventory.items

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

def test_recruit_companion_returns_error_when_player_already_has_companion():
    room = Room("Camp")
    home = Room("Camp")
    existing = Companion(name="Imp", hp=10, home_room=home)
    harpy = Companion(name="Harpy", hp=10, home_room=room)
    room.add_companion(harpy)
    player = Player(name="hero", hp=100)
    player.companion = existing

    message = recruit_companion("harpy", room, player)

    assert message == "You already have a companion, Imp. Dismiss them first."

def test_recruit_companion_does_not_replace_existing_companion():
    room = Room("Camp")
    home = Room("Camp")
    existing = Companion(name="Imp", hp=10, home_room=home)
    harpy = Companion(name="Harpy", hp=10, home_room=room)
    room.add_companion(harpy)
    player = Player(name="hero", hp=100)
    player.companion = existing

    recruit_companion("harpy", room, player)

    assert player.companion is existing

def test_recruit_companion_returns_not_here_message_when_no_matching_companion():
    room = Room("Camp")
    player = Player(name="hero", hp=100)

    message = recruit_companion("harpy", room, player)

    assert message == "There's no one named 'harpy' here to recruit."

def test_recruit_companion_matches_name_case_insensitively():
    room = Room("Camp")
    companion = Companion(name="Harpy", hp=10, home_room=room)
    room.add_companion(companion)
    player = Player(name="hero", hp=100)

    recruit_companion("HARPY", room, player)

    assert player.companion is companion

def test_recruit_companion_returns_missing_items_message_when_player_lacks_required_items():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Bronze Xiphos", "Wooden Shield"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)

    message = recruit_companion("imp", room, player)

    assert message == "Imp shakes their head. \"You're still missing: Bronze Xiphos, Wooden Shield.\""

def test_recruit_companion_does_not_set_player_companion_when_items_missing():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Bronze Xiphos"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)

    recruit_companion("imp", room, player)

    assert player.companion is None

def test_recruit_companion_returns_unequip_message_when_required_item_is_equipped():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Wooden Sword"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)

    message = recruit_companion("imp", room, player)

    assert message == "Imp shakes their head. \"You'll need to unequip: Wooden Sword.\""

def test_recruit_companion_does_not_remove_equipped_item_when_blocked():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Wooden Sword"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    player.inventory.use_item("Wooden Sword", player)

    recruit_companion("imp", room, player)

    assert sword in player.inventory.items

def test_recruit_companion_removes_required_items_from_inventory_on_success():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Wooden Sword"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    recruit_companion("imp", room, player)

    assert sword not in player.inventory.items

def test_recruit_companion_sets_player_companion_on_success():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Wooden Sword"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    recruit_companion("imp", room, player)

    assert player.companion is companion

def test_recruit_companion_removes_companion_from_room_on_success():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Wooden Sword"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    recruit_companion("imp", room, player)

    assert companion not in room.companions

def test_recruit_companion_returns_confirmation_message_on_success():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room, required_items=["Wooden Sword"])
    room.add_companion(companion)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)

    message = recruit_companion("imp", room, player)

    assert message == "Imp joins you."

def test_recruit_companion_with_no_required_items_succeeds_without_any_items():
    room = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=room) # required_items defaults to []
    room.add_companion(companion)
    player = Player(name="hero", hp=100)

    message = recruit_companion("imp", room, player)

    assert player.companion is companion
    assert message == "Imp joins you."

def test_dismiss_companion_returns_message_when_player_has_no_companion():
    player = Player(name="hero", hp=100)

    message = dismiss_companion(player)

    assert message == "You don't have a companion to dismiss."

def test_dismiss_companion_restores_full_hp():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 3
    player = Player(name="hero", hp=100)
    player.companion = companion

    dismiss_companion(player)

    assert companion.hp == 10

def test_dismiss_companion_restores_full_hp_when_downed():
    """Dismissing a downed companion is itself a way to recover them, distinct from using a Reviver."""
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    player = Player(name="hero", hp=100)
    player.companion = companion

    dismiss_companion(player)

    assert companion.hp == 10

def test_dismiss_companion_adds_companion_back_to_home_room():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    player = Player(name="hero", hp=100)
    player.companion = companion

    dismiss_companion(player)

    assert companion in home.companions

def test_dismiss_companion_clears_player_companion():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    player = Player(name="hero", hp=100)
    player.companion = companion

    dismiss_companion(player)

    assert player.companion is None

def test_dismiss_companion_returns_confirmation_message():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    player = Player(name="hero", hp=100)
    player.companion = companion

    message = dismiss_companion(player)

    assert message == "Imp returns to Camp."

def test_repair_item_outside_forge_returns_message():
    room = Room("Armoury")
    player = Player(name="hero", hp=100)

    message = repair_item("shield", player, room)

    assert message == "There's nowhere to repair armour here."

def test_repair_item_with_no_matching_item_returns_message():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)

    message = repair_item("shield", player, room)

    assert message == "You don't have any armour named 'shield'."

def test_repair_item_with_non_armour_item_returns_message():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Sword", description="", damage=3)
    player.inventory.add(sword)

    message = repair_item("sword", player, room)

    assert message == "You don't have any armour named 'sword'."

def test_repair_item_with_full_durability_returns_no_repair_needed_message():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    player.inventory.add(armour)

    message = repair_item("shield", player, room)

    assert message == "Shield doesn't need repairing."

def test_repair_item_with_insufficient_gold_returns_message():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 5
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2 # missing 3, costs 6 at REPAIR_COST_PER_POINT=2
    player.inventory.add(armour)

    message = repair_item("shield", player, room)

    assert message == "Repairing Shield costs 6 gold - you only have 5."

def test_repair_item_with_insufficient_gold_does_not_change_durability():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 5
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2
    player.inventory.add(armour)

    repair_item("shield", player, room)

    assert armour.durability == 2

def test_repair_item_with_insufficient_gold_does_not_change_gold():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 5
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2
    player.inventory.add(armour)

    repair_item("shield", player, room)

    assert player.gold == 5

def test_repair_item_deducts_cost_scaled_by_missing_durability():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2 # missing 3, costs 6
    player.inventory.add(armour)

    repair_item("shield", player, room)

    assert player.gold == 94

def test_repair_item_restores_full_durability():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2
    player.inventory.add(armour)

    repair_item("shield", player, room)

    assert armour.durability == 5

def test_repair_item_returns_confirmation_message():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2
    player.inventory.add(armour)

    message = repair_item("shield", player, room)

    assert message == "Shield is fully repaired for 6 gold."

def test_repair_item_matches_name_case_insensitively():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 2
    player.inventory.add(armour)

    message = repair_item("SHIELD", player, room)

    assert message == "Shield is fully repaired for 6 gold."

def test_repair_item_when_broken_restores_defence_to_player_armour():
    """A broken piece's defence stops counting; repairing it makes it count again - Character.armour is calculated from worn, unbroken pieces."""
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    player.inventory.add(armour)
    armour.use(player)
    armour.durability = 0

    repair_item("shield", player, room)

    assert player.armour == 3

def test_repair_item_when_not_broken_does_not_add_defence_a_second_time():
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    player.inventory.add(armour)
    armour.use(player) # player.armour = 3
    armour.durability = 3 # merely worn, never dropped to 0

    repair_item("shield", player, room)

    assert player.armour == 3

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

def test_display_map_explores_past_locked_exit_when_player_has_required_item():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    room_a.lock_exit("north", "Key")
    player = Player(name="hero", hp=10)
    key = Weapon(name="Key", description="", damage=0)
    player.inventory.add(key)
    assert display_map(room_a, player) == "\nA\n  north -> B\n\nB"

def test_display_map_lists_multiple_branches_from_same_room():
    room_a = Room("A")
    room_b = Room("B")
    room_c = Room("C")
    room_a.connect("north", room_b)
    room_a.connect("east", room_c)
    player = Player(name="hero", hp=10)
    assert display_map(room_a, player) == "\nA\n  north -> B\n  east -> C\n\nB\n\nC"

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

def test_display_local_exits_shows_destination_when_player_has_required_item():
    room_a = Room("A")
    room_b = Room("B")
    room_a.connect("north", room_b)
    room_a.lock_exit("north", "Key")
    player = Player(name="hero", hp=10)
    key = Weapon(name="Key", description="", damage=0)
    player.inventory.add(key)
    assert display_local_exits(room_a, player) == "north -> B"

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

def test_handle_examine_with_insufficient_intellect_does_not_reveal_hidden_exits():
    """Revised design: required_intellect now gates the hidden-exit reveal too, not just the flavour text -
    see CLAUDE.md's revised Intellect hard rule (reachability, not permanent inaccessibility, is the guardrail)."""
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.", required_intellect=3)
    vault = Room("Sunken Vault")
    room.add_hidden_exit("down", vault)
    player = Player(name="Hero", hp=50)
    player.intellect = 0
    handle_examine(room, player)
    assert room.get_exit("down") is None

def test_handle_examine_with_sufficient_intellect_reveals_hidden_exits():
    room = Room("Styx Crossing", examine_text="The stonework here looks subtly disturbed.", required_intellect=3)
    vault = Room("Sunken Vault")
    room.add_hidden_exit("down", vault)
    player = Player(name="Hero", hp=50)
    player.intellect = 3
    handle_examine(room, player)
    assert room.get_exit("down") is vault

def test_get_exit_guardian_returns_none_when_exit_is_not_guarded():
    room = Room("Labyrinth")
    room.connect("south", Room("Grove"))
    room.add_enemy(Enemy(name="Minotaur", hp=25))
    assert get_exit_guardian(room, "south") is None

def test_get_exit_guardian_returns_living_enemy_on_guarded_exit():
    room = Room("Labyrinth")
    room.connect("south", Room("Grove"))
    room.guard_exit("south")
    minotaur = Enemy(name="Minotaur", hp=25)
    room.add_enemy(minotaur)
    assert get_exit_guardian(room, "south") is minotaur

def test_get_exit_guardian_returns_none_when_guarded_room_has_no_enemies():
    room = Room("Labyrinth")
    room.connect("south", Room("Grove"))
    room.guard_exit("south")
    assert get_exit_guardian(room, "south") is None

def test_get_exit_guardian_ignores_dead_enemies():
    room = Room("Labyrinth")
    room.connect("south", Room("Grove"))
    room.guard_exit("south")
    minotaur = Enemy(name="Minotaur", hp=25)
    minotaur.hp = 0
    room.add_enemy(minotaur)
    assert get_exit_guardian(room, "south") is None

def test_get_exit_guardian_skips_a_dead_enemy_to_find_a_living_one():
    room = Room("Lair")
    room.connect("descend", Room("Camp"))
    room.guard_exit("descend")
    dead_gorgon = Enemy(name="Gorgon", hp=12)
    dead_gorgon.hp = 0
    living_gorgon = Enemy(name="Gorgon", hp=12)
    room.add_enemy(dead_gorgon)
    room.add_enemy(living_gorgon)
    assert get_exit_guardian(room, "descend") is living_gorgon

def test_get_exit_guardian_ignores_respawning_enemies():
    room = Room("Practice Chamber")
    room.connect("west", Room("Forge"))
    room.guard_exit("west")
    room.add_enemy(Enemy(name="Practice Enemy", hp=20, respawns=True))
    assert get_exit_guardian(room, "west") is None

def test_take_all_moves_every_room_item_into_inventory():
    room = Room("Vault")
    player = Player(name="Hero", hp=20)
    potion = Consumable(name="Small Healing Potion", heal_amount=5)
    bone = QuestItem(name="Skeleton Bone", description="")
    room.add_item(potion)
    room.add_item(bone)

    take_all(room, player)

    assert potion in player.inventory.items
    assert bone in player.inventory.items
    assert room.items == []

def test_take_all_returns_one_line_summary():
    room = Room("Vault")
    player = Player(name="Hero", hp=20)
    room.add_item(Consumable(name="Small Healing Potion", heal_amount=5))
    room.add_item(QuestItem(name="Skeleton Bone", description=""))

    message = take_all(room, player)

    assert message == "You take: Small Healing Potion, Skeleton Bone."

def test_take_all_in_empty_room_returns_nothing_to_take_message():
    room = Room("Vault")
    player = Player(name="Hero", hp=20)
    assert take_all(room, player) == "There's nothing here to take."

def test_take_all_from_ally_moves_every_item_into_inventory():
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    potion = Consumable(name="Small Healing Potion", heal_amount=5)
    ally = Ally(name="Wounded Soldier", items=[sword, potion])
    player = Player(name="Hero", hp=20)

    take_all_from_ally(ally, player)

    assert sword in player.inventory.items
    assert potion in player.inventory.items
    assert ally.inventory.items == []

def test_take_all_from_ally_returns_one_line_summary():
    ally = Ally(name="Wounded Soldier", items=[Weapon(name="Bronze Xiphos", description="", damage=3)])
    player = Player(name="Hero", hp=20)
    assert take_all_from_ally(ally, player) == "Wounded Soldier gives you: Bronze Xiphos."

def test_take_all_from_ally_with_nothing_left_returns_message():
    ally = Ally(name="Wounded Soldier")
    player = Player(name="Hero", hp=20)
    assert take_all_from_ally(ally, player) == "Wounded Soldier has nothing left to give."

def test_check_equippable_returns_none_for_unequipped_weapon():
    player = Player(name="Hero", hp=20)
    player.inventory.add(Weapon(name="Labrys", description="", damage=5))
    assert check_equippable("labrys", player) is None

def test_check_equippable_returns_none_for_unequipped_armour():
    player = Player(name="Hero", hp=20)
    player.inventory.add(Armour(name="Weathered Helm", description="", defence=1, slot="helmet"))
    assert check_equippable("Weathered Helm", player) is None

def test_check_equippable_returns_error_for_missing_item():
    player = Player(name="Hero", hp=20)
    assert check_equippable("Labrys", player) == "No item named 'Labrys' in inventory."

def test_check_equippable_returns_error_for_non_equippable_item():
    player = Player(name="Hero", hp=20)
    player.inventory.add(Consumable(name="Small Healing Potion", heal_amount=5))
    assert check_equippable("small healing potion", player) == "You can't equip the Small Healing Potion."

def test_check_equippable_returns_error_for_already_equipped_item():
    player = Player(name="Hero", hp=20)
    labrys = Weapon(name="Labrys", description="", damage=5)
    player.inventory.add(labrys)
    labrys.use(player)
    assert check_equippable("labrys", player) == "Labrys is already equipped."

def test_get_uncleared_reasons_returns_empty_list_for_cleared_room():
    room = Room("Grove")
    assert get_uncleared_reasons(room) == []

def test_get_uncleared_reasons_reports_living_enemies():
    room = Room("Grove")
    room.add_enemy(Enemy(name="Satyr", hp=15))
    assert get_uncleared_reasons(room) == ["enemies remain"]

def test_get_uncleared_reasons_ignores_dead_and_respawning_enemies():
    room = Room("Practice Chamber")
    dead = Enemy(name="Satyr", hp=15)
    dead.hp = 0
    room.add_enemy(dead)
    room.add_enemy(Enemy(name="Practice Enemy", hp=20, respawns=True))
    assert get_uncleared_reasons(room) == []

def test_get_uncleared_reasons_hints_at_hidden_exit_without_naming_direction():
    room = Room("Styx Crossing")
    room.add_hidden_exit("down", Room("Sunken Vault"))
    reasons = get_uncleared_reasons(room)
    assert reasons == ["something here is worth a closer look"]
    assert "down" not in reasons[0]

def test_get_uncleared_rooms_lists_only_visited_uncleared_rooms_grouped_by_floor():
    grove = Room("Mossy Grove")
    grove.add_enemy(Enemy(name="Satyr", hp=15))
    unvisited = Room("Sandy Expanse")
    unvisited.add_enemy(Enemy(name="Ember Wraith", hp=19))
    cleared = Room("Stony Lair")
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Mossy Grove", "Stony Lair"}
    floors = {"floor_4": {"Mossy Grove": grove, "Sandy Expanse": unvisited, "Stony Lair": cleared}}

    result = get_uncleared_rooms(floors, player)

    assert result == "Floor 4:\n    Mossy Grove - enemies remain"

def test_get_uncleared_rooms_never_reveals_unvisited_rooms():
    unvisited = Room("Sandy Expanse")
    unvisited.add_enemy(Enemy(name="Ember Wraith", hp=19))
    player = Player(name="Hero", hp=20)
    floors = {"floor_4": {"Sandy Expanse": unvisited}}

    result = get_uncleared_rooms(floors, player)

    assert "Sandy Expanse" not in result

def test_get_uncleared_rooms_with_everything_cleared_returns_all_clear_message():
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Stony Lair"}
    floors = {"floor_4": {"Stony Lair": Room("Stony Lair")}}
    assert get_uncleared_rooms(floors, player) == "Every room you've visited has been cleared."

def test_get_uncleared_rooms_joins_multiple_reasons_for_one_room():
    room = Room("Styx Crossing")
    room.add_enemy(Enemy(name="Shade", hp=7))
    room.add_hidden_exit("down", Room("Sunken Vault"))
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}
    floors = {"floor_1": {"Styx Crossing": room}}

    result = get_uncleared_rooms(floors, player)

    assert result == "Floor 1:\n    Styx Crossing - enemies remain, something here is worth a closer look"

# ---- has_unfinished_trade ----

def test_has_unfinished_trade_is_true_for_an_open_trade():
    ally = Ally(name="Hermes", required_items=["Skeleton Bone"], reward=QuestItem(name="Favour", description=""))
    assert has_unfinished_trade(ally) is True

def test_has_unfinished_trade_is_false_once_the_trade_is_completed():
    ally = Ally(name="Hermes", required_items=["Skeleton Bone"], reward=QuestItem(name="Favour", description=""))
    ally.trade_completed = True
    assert has_unfinished_trade(ally) is False

def test_has_unfinished_trade_is_false_for_an_ally_with_no_required_items():
    """e.g. the Mentor - hands out an item, but has nothing to trade for."""
    ally = Ally(name="Mentor", reward=QuestItem(name="Mentor's Token", description=""))
    assert has_unfinished_trade(ally) is False

def test_has_unfinished_trade_is_false_for_an_ally_with_no_reward():
    """e.g. Prometheus - no reward, so nothing to trade."""
    ally = Ally(name="Prometheus", required_items=["Ember"])
    assert has_unfinished_trade(ally) is False

# ---- get_uncleared_reasons: items and trades ----

def test_get_uncleared_reasons_reports_items_left_behind():
    room = Room("Sunken Vault")
    room.add_item(Consumable(name="Small Healing Potion", heal_amount=5))
    assert get_uncleared_reasons(room) == ["items left behind"]

def test_get_uncleared_reasons_reports_an_unfinished_trade():
    room = Room("Hall of Hermes")
    room.add_ally(Ally(name="Hermes", required_items=["Skeleton Bone"], reward=QuestItem(name="Favour", description="")))
    assert get_uncleared_reasons(room) == ["an unfinished trade"]

def test_get_uncleared_reasons_does_not_report_a_completed_trade():
    room = Room("Hall of Hermes")
    ally = Ally(name="Hermes", required_items=["Skeleton Bone"], reward=QuestItem(name="Favour", description=""))
    ally.trade_completed = True
    room.add_ally(ally)
    assert get_uncleared_reasons(room) == []

def test_get_uncleared_reasons_does_not_report_an_ally_with_nothing_to_trade():
    room = Room("Forge of Prometheus")
    room.add_ally(Ally(name="Prometheus"))
    assert get_uncleared_reasons(room) == []

def test_get_uncleared_reasons_lists_every_reason_in_order():
    room = Room("Busy Room")
    room.add_enemy(Enemy(name="Shade", hp=7))
    room.add_item(Consumable(name="Small Healing Potion", heal_amount=5))
    room.add_ally(Ally(name="Hermes", required_items=["Skeleton Bone"], reward=QuestItem(name="Favour", description="")))
    room.add_hidden_exit("down", Room("Vault"))
    assert get_uncleared_reasons(room) == ["enemies remain", "items left behind", "an unfinished trade", "something here is worth a closer look"]

# ---- get_undiscovered_rooms ----

def _one_floor(*rooms):
    return {"floor_1": {room.name: room for room in rooms}}

def test_get_undiscovered_rooms_includes_unvisited_room_through_an_open_exit():
    styx = Room("Styx Crossing")
    fields = Room("Fields of Asphodel")
    styx.connect("east", fields)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}
    assert get_undiscovered_rooms(_one_floor(styx, fields), player) == {"Fields of Asphodel"}

def test_get_undiscovered_rooms_excludes_already_visited_rooms():
    styx = Room("Styx Crossing")
    fields = Room("Fields of Asphodel")
    styx.connect("east", fields)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing", "Fields of Asphodel"}
    assert get_undiscovered_rooms(_one_floor(styx, fields), player) == set()

def test_get_undiscovered_rooms_only_looks_one_step_from_a_visited_room():
    """Following exits further would name rooms the player has never seen or been shown."""
    a, b, c = Room("A"), Room("B"), Room("C")
    a.connect("east", b)
    b.connect("east", c)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"A"}
    assert get_undiscovered_rooms(_one_floor(a, b, c), player) == {"B"}

def test_get_undiscovered_rooms_skips_an_item_locked_exit_without_the_item():
    chamber = Room("Chamber of Chiron")
    east = Room("Chamber of Chiron (East)")
    chamber.connect("east", east)
    chamber.lock_exit("east", "Wooden Sword")
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Chamber of Chiron"}
    assert get_undiscovered_rooms(_one_floor(chamber, east), player) == set()

def test_get_undiscovered_rooms_follows_an_item_locked_exit_once_the_item_is_held():
    chamber = Room("Chamber of Chiron")
    east = Room("Chamber of Chiron (East)")
    chamber.connect("east", east)
    chamber.lock_exit("east", "Wooden Sword")
    player = Player(name="Hero", hp=20)
    player.inventory.add(Weapon(name="Wooden Sword", description="", damage=1))
    player.visited_rooms = {"Chamber of Chiron"}
    assert get_undiscovered_rooms(_one_floor(chamber, east), player) == {"Chamber of Chiron (East)"}

def test_get_undiscovered_rooms_skips_an_exit_guarded_by_a_living_enemy():
    labyrinth = Room("Labyrinth of the Minotaur")
    grove = Room("Mossy Grove")
    labyrinth.connect("south", grove)
    labyrinth.guard_exit("south")
    labyrinth.add_enemy(Enemy(name="Minotaur", hp=25))
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Labyrinth of the Minotaur"}
    assert get_undiscovered_rooms(_one_floor(labyrinth, grove), player) == set()

def test_get_undiscovered_rooms_follows_a_guarded_exit_once_its_guardian_is_dead():
    labyrinth = Room("Labyrinth of the Minotaur")
    grove = Room("Mossy Grove")
    labyrinth.connect("south", grove)
    labyrinth.guard_exit("south")
    minotaur = Enemy(name="Minotaur", hp=25)
    minotaur.hp = 0
    labyrinth.add_enemy(minotaur)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Labyrinth of the Minotaur"}
    assert get_undiscovered_rooms(_one_floor(labyrinth, grove), player) == {"Mossy Grove"}

def test_get_undiscovered_rooms_skips_a_fast_travel_locked_exit():
    forge = Room("Forge of Prometheus")
    prayer = Room("Prayer Room")
    forge.connect("prayer room", prayer)
    forge.lock_fast_travel_exit("prayer room")
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Forge of Prometheus"}
    assert get_undiscovered_rooms(_one_floor(forge, prayer), player) == set()

def test_get_undiscovered_rooms_never_follows_a_hidden_exit():
    styx = Room("Styx Crossing")
    vault = Room("Sunken Vault")
    styx.add_hidden_exit("down", vault)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}
    assert get_undiscovered_rooms(_one_floor(styx, vault), player) == set()

def test_get_undiscovered_rooms_follows_a_hidden_exit_once_revealed():
    styx = Room("Styx Crossing")
    vault = Room("Sunken Vault")
    styx.add_hidden_exit("down", vault)
    styx.reveal_hidden_exits()
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}
    assert get_undiscovered_rooms(_one_floor(styx, vault), player) == {"Sunken Vault"}

def test_get_undiscovered_rooms_ignores_a_visited_room_not_in_any_floor():
    """e.g. the dev test room - not part of all_floors, so it's skipped rather than raising."""
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Dev Test Room"}
    assert get_undiscovered_rooms(_one_floor(Room("A")), player) == set()

# ---- get_uncleared_rooms: undiscovered entries ----

def test_get_uncleared_rooms_lists_an_undiscovered_neighbour():
    styx = Room("Styx Crossing")
    fields = Room("Fields of Asphodel")
    styx.connect("east", fields)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}

    result = get_uncleared_rooms(_one_floor(styx, fields), player)

    assert result == "Floor 1:\n    Fields of Asphodel - undiscovered"

def test_get_uncleared_rooms_groups_an_undiscovered_room_under_its_own_floor():
    styx = Room("Styx Crossing")
    library = Room("Library of Athena")
    styx.connect("descend", library)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}
    floors = {"floor_1": {"Styx Crossing": styx}, "floor_2": {"Library of Athena": library}}

    result = get_uncleared_rooms(floors, player)

    assert result == "Floor 2:\n    Library of Athena - undiscovered"

def test_get_uncleared_rooms_lists_visited_and_undiscovered_rooms_together_in_floor_order():
    styx = Room("Styx Crossing")
    styx.add_enemy(Enemy(name="Shade", hp=7))
    fields = Room("Fields of Asphodel")
    styx.connect("east", fields)
    player = Player(name="Hero", hp=20)
    player.visited_rooms = {"Styx Crossing"}

    result = get_uncleared_rooms(_one_floor(styx, fields), player)

    assert result == "Floor 1:\n    Styx Crossing - enemies remain\n    Fields of Asphodel - undiscovered"

def test_repair_item_on_an_unequipped_broken_piece_does_not_change_armour():
    """Regression: repairing a broken piece used to add its defence to player.armour even when it wasn't being worn."""
    room = Room("Forge", is_forge=True)
    player = Player(name="hero", hp=100, armour=1)
    player.gold = 100
    armour = Armour(name="Shield", description="", defence=3, max_durability=5)
    armour.durability = 0
    player.inventory.add(armour)

    repair_item("shield", player, room)

    assert player.armour == 1

def _duellist() -> Enemy:
    """Test helper - a stand-in duel_enemy_factory."""
    return Enemy(name="Imp", hp=30, description="It squares up.")

def _camp_with_duelling_companion():
    """Test helper - a room holding a companion who has to be duelled first."""
    room = Room("Camp")
    companion = Companion(name="Imp", hp=20, home_room=room, duel_enemy_factory=_duellist)
    room.add_companion(companion)
    return room, companion

# ---- recruit_companion and duels ----

def test_recruit_companion_refuses_a_companion_who_must_be_duelled_first():
    room, companion = _camp_with_duelling_companion()
    player = Player(name="Hero", hp=20)
    message = recruit_companion("imp", room, player)
    assert player.companion is None
    assert message == "Imp won't follow anyone who hasn't beaten them. Try 'challenge imp'."

def test_recruit_companion_succeeds_once_the_duel_is_won():
    room, companion = _camp_with_duelling_companion()
    companion.duel_won = True
    player = Player(name="Hero", hp=20)
    recruit_companion("imp", room, player)
    assert player.companion is companion

# ---- start_duel ----

def test_start_duel_with_no_matching_companion_returns_message():
    room = Room("Camp")
    player = Player(name="Hero", hp=20)
    assert start_duel("imp", room, player) == "There's no one named 'imp' here to challenge."

def test_start_duel_with_a_companion_who_does_not_duel_returns_message():
    room = Room("Camp")
    room.add_companion(Companion(name="Imp", hp=20, home_room=room))
    player = Player(name="Hero", hp=20)
    assert start_duel("imp", room, player) == "Imp has no interest in fighting you."
    assert player.in_combat is False

def test_start_duel_after_the_duel_is_won_returns_message():
    room, companion = _camp_with_duelling_companion()
    companion.duel_won = True
    player = Player(name="Hero", hp=20)
    assert start_duel("imp", room, player) == "Imp has already measured you - there's nothing left to prove."
    assert room.enemies == []

def test_start_duel_swaps_the_companion_for_its_combat_form():
    room, companion = _camp_with_duelling_companion()
    player = Player(name="Hero", hp=20)
    start_duel("imp", room, player)
    assert companion not in room.companions
    assert len(room.enemies) == 1
    assert room.enemies[0].duel_companion is companion

def test_start_duel_records_the_players_hp_to_restore_afterwards():
    room, _ = _camp_with_duelling_companion()
    player = Player(name="Hero", hp=20)
    player.hp = 13
    start_duel("imp", room, player)
    assert room.enemies[0].duel_return_hp == 13

def test_start_duel_puts_the_player_into_combat_with_the_opponent():
    room, _ = _camp_with_duelling_companion()
    player = Player(name="Hero", hp=20)
    message = start_duel("imp", room, player)
    assert player.in_combat is True
    assert player.current_target is room.enemies[0]
    assert message == "Imp accepts. The duel begins.\nIt squares up."

def test_start_duel_matches_the_name_case_insensitively():
    room, companion = _camp_with_duelling_companion()
    player = Player(name="Hero", hp=20)
    start_duel("IMP", room, player)
    assert companion not in room.companions

# ---- guarded and sealed exits in exit listings ----

def test_display_local_exits_names_the_guardian_of_a_guarded_exit():
    room = Room("Labyrinth")
    room.connect("south", Room("Grove"))
    room.guard_exit("south")
    room.add_enemy(Enemy(name="Minotaur", hp=20))
    assert display_local_exits(room, Player(name="Hero", hp=20)) == "south -> Grove (guarded by Minotaur)"

def test_display_local_exits_drops_the_guard_label_once_the_guardian_is_gone():
    room = Room("Labyrinth")
    room.connect("south", Room("Grove"))
    room.guard_exit("south")
    assert display_local_exits(room, Player(name="Hero", hp=20)) == "south -> Grove"

def test_display_local_exits_shows_an_unopened_shortcut_as_sealed():
    room = Room("Forge")
    room.connect("prayer room", Room("Prayer Room"))
    room.lock_fast_travel_exit("prayer room")
    assert display_local_exits(room, Player(name="Hero", hp=20)) == "prayer room -> Sealed Shortcut"

def test_display_map_names_the_guardian_and_does_not_map_past_it():
    labyrinth = Room("Labyrinth")
    grove = Room("Grove")
    beyond = Room("Beyond")
    labyrinth.connect("south", grove)
    grove.connect("south", beyond)
    labyrinth.guard_exit("south")
    labyrinth.add_enemy(Enemy(name="Minotaur", hp=20))
    output = display_map(labyrinth, Player(name="Hero", hp=20))
    assert "south -> Grove (guarded by Minotaur)" in output
    assert "Beyond" not in output

def test_display_map_shows_an_unopened_shortcut_as_sealed_and_does_not_map_past_it():
    forge = Room("Forge")
    prayer_room = Room("Prayer Room")
    prayer_room.connect("west", Room("Cave"))
    forge.connect("prayer room", prayer_room)
    forge.lock_fast_travel_exit("prayer room")
    output = display_map(forge, Player(name="Hero", hp=20))
    assert "prayer room -> Sealed Shortcut" in output
    assert "Cave" not in output
