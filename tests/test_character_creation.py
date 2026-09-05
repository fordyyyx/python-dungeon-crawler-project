from dungeon_crawler.character_creation import choose_ancestry, choose_secondary_ancestry, create_player

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
