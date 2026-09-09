from dungeon_crawler.character_creation import (
    choose_ancestry, choose_secondary_ancestry, create_player,
    choose_title_screen_action, choose_profile, choose_slot, choose_occupied_slot, confirm,
)
from dungeon_crawler import save_system
from dungeon_crawler.characters import Player
from dungeon_crawler.world import Room, Map

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

def test_choose_secondary_ancestry_returns_chosen_key_when_valid(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "ares")
    assert choose_secondary_ancestry("basic") == "ares"

def test_choose_secondary_ancestry_is_case_insensitive(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "ARES")
    assert choose_secondary_ancestry("basic") == "ares"

def test_choose_secondary_ancestry_strips_whitespace_from_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "  ares  ")
    assert choose_secondary_ancestry("basic") == "ares"

def test_choose_secondary_ancestry_reprompts_on_invalid_choice_before_accepting_valid_one(monkeypatch):
    responses = iter(["nonsense", "ares"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_secondary_ancestry("basic") == "ares"

def test_choose_secondary_ancestry_prints_error_message_for_invalid_choice(monkeypatch, capsys):
    responses = iter(["nonsense", "ares"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    choose_secondary_ancestry("basic")
    captured = capsys.readouterr()
    assert "That name means nothing to me. Choose from the list above." in captured.out

def test_choose_secondary_ancestry_rejects_choice_matching_primary_and_reprompts(monkeypatch):
    responses = iter(["ares", "basic"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_secondary_ancestry("ares") == "basic"

def test_choose_secondary_ancestry_prints_message_when_choice_matches_primary(monkeypatch, capsys):
    responses = iter(["ares", "basic"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    choose_secondary_ancestry("ares")
    captured = capsys.readouterr()
    assert "You've already claimed that blood - choose a different one, or 'basic' for none." in captured.out

def test_choose_secondary_ancestry_excludes_primary_ancestry_from_printed_options(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt="": "ares")
    choose_secondary_ancestry("basic")
    captured = capsys.readouterr()
    assert "basic - No secondary gift" not in captured.out

def test_choose_secondary_ancestry_prints_each_non_primary_ancestry_option(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt="": "ares")
    choose_secondary_ancestry("basic")
    captured = capsys.readouterr()
    assert "ares - Reckless Strength - heavy attacks never miss" in captured.out
    assert "cyclops - Iron Hide - reduces every hit taken by 1" in captured.out

def test_create_player_sets_name():
    player = create_player("Hero", "basic", "basic")
    assert player.name == "Hero"

def test_create_player_sets_stats_from_ancestry():
    player = create_player("Hero", "basic", "basic")
    assert player.hp == 20
    assert player.attack_damage == 3
    assert player.armour == 1

def test_create_player_sets_ancestry_label():
    player = create_player("Hero", "basic", "basic")
    assert player.ancestry_label == "No lineage"

def test_create_player_with_bonus_skill_point_ancestry_grants_skill_point():
    player = create_player("Hero", "odysseus", "basic")
    assert player.skill_tree.skill_points == 1

def test_create_player_without_bonus_skill_point_ancestry_grants_no_skill_point():
    player = create_player("Hero", "basic", "basic")
    assert player.skill_tree.skill_points == 0

def test_create_player_sets_intellect_from_ancestry():
    player = create_player("Hero", "athena", "basic")
    assert player.intellect == 5

def test_create_player_with_different_secondary_key_applies_secondary_effect():
    player = create_player("Hero", "basic", "ares")
    assert player.has_reckless_strength is True

def test_create_player_with_different_secondary_key_sets_secondary_ancestry_label():
    player = create_player("Hero", "basic", "ares")
    assert player.secondary_ancestry_label == "Reckless Strength - heavy attacks never miss"

def test_create_player_with_basic_secondary_key_applies_no_effect():
    player = create_player("Hero", "athena", "basic")
    assert player.has_reckless_strength is False
    assert player.has_measured_casting is False

def test_create_player_with_basic_secondary_key_does_not_set_secondary_ancestry_label():
    player = create_player("Hero", "athena", "basic")
    assert player.secondary_ancestry_label == ""

def test_create_player_with_secondary_key_matching_primary_applies_no_effect():
    """Same figure can't be picked as both - selecting ares/ares must not grant the ares secondary ability."""
    player = create_player("Hero", "ares", "ares")
    assert player.has_reckless_strength is False

def test_create_player_with_secondary_key_matching_primary_does_not_set_secondary_ancestry_label():
    player = create_player("Hero", "ares", "ares")
    assert player.secondary_ancestry_label == ""

# ---- choose_title_screen_action ----

def test_choose_title_screen_action_returns_new_for_choice_one(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "1")
    assert choose_title_screen_action() == "new"

def test_choose_title_screen_action_returns_load_for_choice_two(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "2")
    assert choose_title_screen_action() == "load"

def test_choose_title_screen_action_returns_delete_for_choice_three(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "3")
    assert choose_title_screen_action() == "delete"

def test_choose_title_screen_action_returns_quit_for_choice_four(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "4")
    assert choose_title_screen_action() == "quit"

def test_choose_title_screen_action_reprompts_on_invalid_choice_before_accepting_valid_one(monkeypatch):
    responses = iter(["nonsense", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_title_screen_action() == "new"

def test_choose_title_screen_action_prints_error_message_for_invalid_choice(monkeypatch, capsys):
    responses = iter(["nonsense", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    choose_title_screen_action()
    captured = capsys.readouterr()
    assert "Choose 1, 2, 3, or 4." in captured.out

# ---- choose_profile ----

def test_choose_profile_returns_chosen_number_when_valid(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "2")
    assert choose_profile() == 2

def test_choose_profile_accepts_lower_boundary(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "1")
    assert choose_profile() == 1

def test_choose_profile_accepts_upper_boundary(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": str(save_system.PROFILE_LIMIT))
    assert choose_profile() == save_system.PROFILE_LIMIT

def test_choose_profile_reprompts_on_non_digit_input(monkeypatch):
    responses = iter(["nonsense", "1"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_profile() == 1

def test_choose_profile_reprompts_on_out_of_range_number(monkeypatch):
    responses = iter([str(save_system.PROFILE_LIMIT + 1), "1"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_profile() == 1

# ---- choose_slot ----

def test_choose_slot_returns_chosen_number_when_valid(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda prompt="": "3")
    assert choose_slot(1) == 3

def test_choose_slot_reprompts_on_out_of_range_number(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    responses = iter([str(save_system.SAVE_SLOTS_PER_PROFILE + 1), "1"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_slot(1) == 1

def test_choose_slot_prints_empty_for_unoccupied_slot(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda prompt="": "1")
    choose_slot(1)
    captured = capsys.readouterr()
    assert "1. empty" in captured.out

def test_choose_slot_prints_summary_for_occupied_slot(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_system.save_game(1, 2, Player(name="Hero", hp=50), room, dungeon)
    monkeypatch.setattr("builtins.input", lambda prompt="": "2")
    choose_slot(1)
    captured = capsys.readouterr()
    assert "2. Hero - LVL 1  - Chamber" in captured.out

# ---- choose_occupied_slot ----

def test_choose_occupied_slot_returns_none_when_profile_has_no_saves(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    assert choose_occupied_slot(1) is None

def test_choose_occupied_slot_prints_message_when_profile_has_no_saves(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    choose_occupied_slot(1)
    captured = capsys.readouterr()
    assert "Profile 1 has no saves." in captured.out

def test_choose_occupied_slot_returns_chosen_occupied_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_system.save_game(1, 2, Player(name="Hero", hp=50), room, dungeon)
    monkeypatch.setattr("builtins.input", lambda prompt="": "2")
    assert choose_occupied_slot(1) == 2

def test_choose_occupied_slot_reprompts_on_unoccupied_slot_choice(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_system.save_game(1, 2, Player(name="Hero", hp=50), room, dungeon)
    responses = iter(["1", "2"])  # slot 1 is empty, slot 2 is occupied
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert choose_occupied_slot(1) == 2

# ---- confirm ----

def test_confirm_returns_true_for_yes(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "yes")
    assert confirm("Overwrite?") is True

def test_confirm_returns_true_for_y(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "y")
    assert confirm("Overwrite?") is True

def test_confirm_returns_false_for_no(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "no")
    assert confirm("Overwrite?") is False

def test_confirm_returns_false_for_n(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "n")
    assert confirm("Overwrite?") is False

def test_confirm_is_case_insensitive(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda prompt="": "YES")
    assert confirm("Overwrite?") is True

def test_confirm_reprompts_on_unrecognised_answer_before_accepting_valid_one(monkeypatch):
    responses = iter(["maybe", "yes"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    assert confirm("Overwrite?") is True

def test_confirm_prints_error_message_for_unrecognised_answer(monkeypatch, capsys):
    responses = iter(["maybe", "yes"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    confirm("Overwrite?")
    captured = capsys.readouterr()
    assert "Please answer yes or no." in captured.out
