from dungeon_crawler.characters import Player, Ally, Companion
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, QuestItem, Weapon
from dungeon_crawler.exploration import pick_up, is_exit_locked, trade_with_ally, recruit_companion, dismiss_companion, display_map, find_floor_for_room, display_local_exits, handle_examine

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
