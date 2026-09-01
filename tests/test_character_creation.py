from dungeon_crawler.character_creation import choose_ancestry, create_player

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
