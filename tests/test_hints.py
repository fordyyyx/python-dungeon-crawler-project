from dungeon_crawler.characters import Player
from dungeon_crawler.hints import HINTS, show_hint

def test_show_hint_returns_prefixed_hint_text_the_first_time():
    player = Player(name="Hero", hp=20)
    assert show_hint(player, "forge") == f"[Hint] {HINTS['forge']}"

def test_show_hint_marks_the_key_as_seen():
    player = Player(name="Hero", hp=20)
    show_hint(player, "forge")
    assert "forge" in player.seen_hints

def test_show_hint_returns_empty_string_once_already_seen():
    player = Player(name="Hero", hp=20)
    show_hint(player, "forge")
    assert show_hint(player, "forge") == ""

def test_show_hint_respects_hints_seen_before_this_session():
    """seen_hints is restored from the save file, so a hint seen before a reload must stay silent afterwards."""
    player = Player(name="Hero", hp=20)
    player.seen_hints = {"autosave"}
    assert show_hint(player, "autosave") == ""

def test_show_hint_tracks_each_key_independently():
    player = Player(name="Hero", hp=20)
    show_hint(player, "forge")
    assert show_hint(player, "combat") == f"[Hint] {HINTS['combat']}"

def test_show_hint_is_tracked_per_player():
    first = Player(name="Hero", hp=20)
    second = Player(name="Other", hp=20)
    show_hint(first, "forge")
    assert show_hint(second, "forge") == f"[Hint] {HINTS['forge']}"

def test_show_hint_with_unknown_key_raises_key_error():
    player = Player(name="Hero", hp=20)
    try:
        show_hint(player, "not a real hint")
        assert False, "Expected a KeyError but none was raised"
    except KeyError:
        pass

def test_hints_defines_every_key_the_game_triggers():
    """Every show_hint() call site in engine.py uses one of these keys - a missing one would raise KeyError mid-game."""
    assert set(HINTS) == {"combat", "passive_regen", "guarded_exit", "forge", "forge_shortcut", "practice_chamber", "skill_points", "autosave", "evasive"}

def test_hints_all_have_non_empty_text():
    assert all(text.strip() for text in HINTS.values())

def test_passive_regen_hint_matches_the_real_regen_cap():
    """The hint text hard-codes 'three quarters' - this fails if PASSIVE_REGEN_CAP_FRACTION changes without the wording being updated."""
    from dungeon_crawler.engine import PASSIVE_REGEN_CAP_FRACTION
    assert PASSIVE_REGEN_CAP_FRACTION == 0.75
    assert "three quarters" in HINTS["passive_regen"]

def test_evasive_hint_points_at_ranged_attacks_and_spells():
    """The hint must name the counters that actually bypass melee dodge - see take_damage()'s melee flag."""
    assert "Ranged" in HINTS["evasive"]
    assert "spells" in HINTS["evasive"]
