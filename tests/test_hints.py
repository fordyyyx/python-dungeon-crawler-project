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
    assert set(HINTS) == {"combat", "passive_regen", "passive_regen_full", "guarded_exit", "forge", "forge_shortcut", "practice_chamber", "skill_points", "autosave", "evasive", "room_interactions", "workshop"}

def test_hints_all_have_non_empty_text():
    assert all(text.strip() for text in HINTS.values())

def test_passive_regen_hint_matches_the_real_regen_cap():
    """The hint text hard-codes 'three quarters' - this fails if Normal's regen cap changes without the wording being updated."""
    from dungeon_crawler.difficulty import DIFFICULTIES
    assert DIFFICULTIES["normal"].regen_cap == 0.75
    assert "three quarters of your maximum on Normal" in HINTS["passive_regen"]

def test_passive_regen_hint_matches_hards_regen_cap():
    """The same hint hard-codes 'half on Hard'."""
    from dungeon_crawler.difficulty import DIFFICULTIES
    assert DIFFICULTIES["hard"].regen_cap == 0.5
    assert "half on Hard" in HINTS["passive_regen"]

def test_passive_regen_hints_cover_every_difficulty():
    """Every setting with a cap must be named in the capped hint - a new capped setting needs adding to its wording. The rest regenerate
    to full and get the other hint (see main()'s movement branch)."""
    from dungeon_crawler.difficulty import DIFFICULTIES
    for setting in DIFFICULTIES.values():
        if setting.regen_cap < 1:
            assert f"on {setting.label}" in HINTS["passive_regen"], setting.label
    assert "all the way back to full" in HINTS["passive_regen_full"]

def test_evasive_hint_points_at_ranged_attacks_and_spells():
    """The hint must name the counters that actually bypass melee dodge - see take_damage()'s melee flag."""
    assert "Ranged" in HINTS["evasive"]
    assert "spells" in HINTS["evasive"]

def test_combat_hint_does_not_claim_light_attacks_never_miss():
    """Regression: the hint said "'attack light' never misses", untrue since armour weight added a miss chance to every attack."""
    assert "never misses" not in HINTS["combat"]
    assert "'stats'" in HINTS["combat"]

def test_workshop_hint_names_the_upgrade_command_and_what_limits_it():
    assert "'upgrade'" in HINTS["workshop"]
    assert "intellect" in HINTS["workshop"]
