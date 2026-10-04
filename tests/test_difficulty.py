from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room, Map
from dungeon_crawler.difficulty import (
    Difficulty, DIFFICULTIES, DEFAULT_DIFFICULTY, NG_PLUS_MULTIPLIER_PER_CYCLE,
    get_difficulty, enemy_multipliers, scale_enemy, scale_rooms, scale_for, scale_world, ensure_world_scaled,
)

def make_enemy(hp: int = 100, attack_damage: int = 10, **kwargs) -> Enemy:
    return Enemy(name="Goblin", hp=hp, attack_damage=attack_damage, **kwargs)

# ---- the settings ----

def test_difficulties_are_story_easy_normal_and_hard_in_that_order():
    assert list(DIFFICULTIES) == ["story", "easy", "normal", "hard"]

def test_difficulties_labels():
    assert [setting.label for setting in DIFFICULTIES.values()] == ["Story", "Easy", "Normal", "Hard"]

def test_difficulties_all_have_a_description():
    assert all(setting.description.strip() for setting in DIFFICULTIES.values())

def test_story_halves_enemies_and_regenerates_two_a_move_to_full():
    story = DIFFICULTIES["story"]
    assert (story.hp_multiplier, story.attack_multiplier, story.regen_cap, story.regen_per_move) == (0.5, 0.5, 1.0, 2)

def test_easy_weakens_enemies_and_regenerates_to_full():
    easy = DIFFICULTIES["easy"]
    assert (easy.hp_multiplier, easy.attack_multiplier, easy.regen_cap, easy.regen_per_move) == (0.75, 0.8, 1.0, 1)

def test_normal_leaves_enemies_alone_and_regenerates_to_three_quarters():
    """Normal is the baseline every balance pass tuned - it must never scale anything."""
    normal = DIFFICULTIES["normal"]
    assert (normal.hp_multiplier, normal.attack_multiplier, normal.regen_cap, normal.regen_per_move) == (1.0, 1.0, 0.75, 1)

def test_hard_strengthens_enemies_and_regenerates_to_half():
    hard = DIFFICULTIES["hard"]
    assert (hard.hp_multiplier, hard.attack_multiplier, hard.regen_cap, hard.regen_per_move) == (1.3, 1.2, 0.5, 1)

def test_difficulties_get_harder_in_order():
    settings = list(DIFFICULTIES.values())
    for easier, harder in zip(settings, settings[1:]):
        assert easier.hp_multiplier < harder.hp_multiplier
        assert easier.attack_multiplier < harder.attack_multiplier
        assert easier.regen_cap >= harder.regen_cap

def test_default_difficulty_is_normal():
    assert DEFAULT_DIFFICULTY == "normal"
    assert DEFAULT_DIFFICULTY in DIFFICULTIES

def test_a_difficulty_cannot_be_changed_once_made():
    """The dataclass is frozen - a setting is shared by every run that uses it."""
    try:
        DIFFICULTIES["normal"].hp_multiplier = 2.0
        assert False, "Expected an AttributeError but none was raised"
    except AttributeError:
        pass

# ---- get_difficulty ----

def test_get_difficulty_returns_the_setting_for_a_key():
    assert get_difficulty("hard") is DIFFICULTIES["hard"]

def test_get_difficulty_returns_a_difficulty():
    assert isinstance(get_difficulty("story"), Difficulty)

def test_get_difficulty_unknown_key_raises_key_error():
    try:
        get_difficulty("impossible")
        assert False, "Expected a KeyError but none was raised"
    except KeyError:
        pass

# ---- enemy_multipliers ----

def test_enemy_multipliers_on_normal_with_no_cycles_are_one():
    assert enemy_multipliers("normal", 0) == (1.0, 1.0)

def test_enemy_multipliers_are_the_settings_own_with_no_cycles():
    assert enemy_multipliers("hard", 0) == (1.3, 1.2)
    assert enemy_multipliers("story", 0) == (0.5, 0.5)

def test_ng_plus_adds_a_quarter_per_cycle():
    assert NG_PLUS_MULTIPLIER_PER_CYCLE == 0.25
    assert enemy_multipliers("normal", 1) == (1.25, 1.25)
    assert enemy_multipliers("normal", 2) == (1.5, 1.5)

def test_ng_plus_cycles_add_rather_than_compound():
    """Four cycles is +100%, not 1.25 to the fourth power."""
    assert enemy_multipliers("normal", 4) == (2.0, 2.0)

def test_ng_plus_multiplies_on_top_of_the_setting():
    hp_multiplier, attack_multiplier = enemy_multipliers("hard", 1)
    assert abs(hp_multiplier - 1.625) < 1e-9
    assert abs(attack_multiplier - 1.5) < 1e-9

# ---- scale_enemy ----

def test_scale_enemy_on_hard_raises_max_hp_and_attack():
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "hard", 0)
    assert enemy.max_hp == 130
    assert enemy.attack_damage == 12

def test_scale_enemy_on_story_halves_max_hp_and_attack():
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "story", 0)
    assert enemy.max_hp == 50
    assert enemy.attack_damage == 5

def test_scale_enemy_on_easy_scales_hp_and_attack_separately():
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "easy", 0)
    assert enemy.max_hp == 75
    assert enemy.attack_damage == 8

def test_scale_enemy_on_normal_changes_nothing():
    enemy = make_enemy(hp=37, attack_damage=9)
    scale_enemy(enemy, "normal", 0)
    assert (enemy.hp, enemy.max_hp, enemy.attack_damage) == (37, 37, 9)

def test_scale_enemy_applies_the_ng_plus_cycle():
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "normal", 2)
    assert enemy.max_hp == 150
    assert enemy.attack_damage == 15

def test_scale_enemy_keeps_a_full_health_enemy_full():
    enemy = make_enemy(hp=100)
    scale_enemy(enemy, "hard", 0)
    assert enemy.hp == enemy.max_hp == 130

def test_scale_enemy_keeps_a_wounded_enemys_share_of_its_hp():
    enemy = make_enemy(hp=100)
    enemy.hp = 50
    scale_enemy(enemy, "hard", 0)
    assert enemy.hp == 65

def test_scale_enemy_never_kills_a_living_enemy():
    """1 of 100 HP is half a point of 50 - it must stay alive on 1, not round down to 0."""
    enemy = make_enemy(hp=100)
    enemy.hp = 1
    scale_enemy(enemy, "story", 0)
    assert enemy.hp == 1

def test_scale_enemy_leaves_a_dead_enemy_dead():
    enemy = make_enemy(hp=100)
    enemy.hp = 0
    scale_enemy(enemy, "hard", 0)
    assert enemy.hp == 0
    assert enemy.max_hp == 130

def test_scale_enemy_max_hp_never_drops_below_one():
    enemy = make_enemy(hp=1, attack_damage=0)
    scale_enemy(enemy, "story", 0)
    assert enemy.max_hp == 1
    assert enemy.hp == 1

def test_scale_enemy_an_enemy_with_no_attack_stays_harmless():
    enemy = make_enemy(hp=10, attack_damage=0)
    scale_enemy(enemy, "hard", 3)
    assert enemy.attack_damage == 0

def test_scale_enemy_with_keep_hp_keeps_current_hp_exactly():
    """Loading a save: HP was saved already scaled, so it must not be scaled a second time."""
    enemy = make_enemy(hp=100)
    enemy.hp = 90
    scale_enemy(enemy, "hard", 0, keep_hp=True)
    assert enemy.hp == 90
    assert enemy.max_hp == 130

def test_scale_enemy_with_keep_hp_caps_current_hp_at_the_new_maximum():
    enemy = make_enemy(hp=100)
    scale_enemy(enemy, "story", 0, keep_hp=True)
    assert enemy.hp == 50

def test_scale_enemy_twice_gives_the_same_result_as_once():
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "hard", 0)
    scale_enemy(enemy, "hard", 0)
    assert (enemy.hp, enemy.max_hp, enemy.attack_damage) == (130, 130, 12)

def test_scale_enemy_to_a_new_setting_never_compounds():
    """Hard then Story is plain Story - scaling always starts from the unscaled values."""
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "hard", 0)
    scale_enemy(enemy, "story", 0)
    assert (enemy.hp, enemy.max_hp, enemy.attack_damage) == (50, 50, 5)

def test_scale_enemy_back_to_normal_restores_the_unscaled_values():
    enemy = make_enemy(hp=37, attack_damage=9)
    scale_enemy(enemy, "hard", 2)
    scale_enemy(enemy, "normal", 0)
    assert (enemy.hp, enemy.max_hp, enemy.attack_damage) == (37, 37, 9)

def test_scale_enemy_leaves_the_unscaled_values_alone():
    enemy = make_enemy(hp=100, attack_damage=10)
    scale_enemy(enemy, "hard", 1)
    assert (enemy.unscaled_max_hp, enemy.unscaled_attack) == (100, 10)

def test_scale_enemy_undoes_a_stat_set_by_hand():
    """What 'dev set' does - the next rescale works from the factory's values, not the hand-set ones."""
    enemy = make_enemy(hp=100, attack_damage=10)
    enemy.attack_damage = 99
    enemy.max_hp = 500
    scale_enemy(enemy, "normal", 0)
    assert (enemy.max_hp, enemy.attack_damage) == (100, 10)

def test_scale_enemy_never_scales_a_respawning_enemy():
    """The Practice Chamber's dummy is the player's own sandbox, set with 'dummy set'."""
    dummy = make_enemy(hp=100, attack_damage=10, respawns=True)
    scale_enemy(dummy, "hard", 3)
    assert (dummy.hp, dummy.max_hp, dummy.attack_damage) == (100, 100, 10)

def test_scale_enemy_leaves_armour_and_the_other_combat_numbers_alone():
    enemy = make_enemy(hp=100, attack_damage=10, armour=4, brace_amount=3, heal_amount=6, armour_pierce=2)
    scale_enemy(enemy, "hard", 1)
    assert (enemy.armour, enemy.brace_amount, enemy.heal_amount, enemy.armour_pierce) == (4, 3, 6, 2)

def test_scale_enemy_leaves_rewards_alone():
    """Gold and XP are the same on every setting, so the economy needs no retuning."""
    enemy = make_enemy(hp=100, attack_damage=10, experience_reward=40, gold_reward=25)
    scale_enemy(enemy, "story", 0)
    assert (enemy.experience_reward, enemy.gold_reward) == (40, 25)

# ---- scale_rooms ----

def test_scale_rooms_scales_every_enemy_in_every_room():
    first, second = Room("Hall"), Room("Cellar")
    enemies = [make_enemy(), make_enemy(), make_enemy()]
    first.add_enemy(enemies[0])
    first.add_enemy(enemies[1])
    second.add_enemy(enemies[2])
    scale_rooms([first, second], "hard", 0)
    assert [enemy.max_hp for enemy in enemies] == [130, 130, 130]

def test_scale_rooms_accepts_a_generator_of_rooms():
    """main() passes a generator over every floor's rooms."""
    room = Room("Hall")
    enemy = make_enemy()
    room.add_enemy(enemy)
    scale_rooms((r for r in [room]), "story", 0)
    assert enemy.max_hp == 50

def test_scale_rooms_passes_keep_hp_on():
    room = Room("Hall")
    enemy = make_enemy()
    enemy.hp = 40
    room.add_enemy(enemy)
    scale_rooms([room], "hard", 0, keep_hp=True)
    assert enemy.hp == 40

def test_scale_rooms_with_an_empty_room_does_nothing():
    scale_rooms([Room("Hall")], "hard", 0)

# ---- scale_for ----

def test_scale_for_uses_the_players_difficulty():
    player = Player(name="Hero", hp=20)
    player.difficulty = "hard"
    enemy = make_enemy()
    scale_for(enemy, player)
    assert enemy.max_hp == 130

def test_scale_for_uses_the_players_ng_plus_cycle():
    player = Player(name="Hero", hp=20)
    player.ng_plus_cycle = 2
    enemy = make_enemy()
    scale_for(enemy, player)
    assert (enemy.max_hp, enemy.attack_damage) == (150, 15)

def test_scale_for_a_new_player_changes_nothing():
    """A fresh Player is on Normal with no cycles - so every test that builds one sees unscaled enemies."""
    enemy = make_enemy(hp=37, attack_damage=9)
    scale_for(enemy, Player(name="Hero", hp=20))
    assert (enemy.hp, enemy.max_hp, enemy.attack_damage) == (37, 37, 9)

# ---- scale_world ----

def make_world():
    """A two-room world with one enemy in each."""
    world = Map()
    hall, cellar = Room("Hall"), Room("Cellar")
    world.add_room(hall)
    world.add_room(cellar)
    goblin, rat = make_enemy(hp=100, attack_damage=10), make_enemy(hp=20, attack_damage=10)
    hall.add_enemy(goblin)
    cellar.add_enemy(rat)
    return world, goblin, rat

def test_scale_world_scales_every_enemy_in_every_room():
    world, goblin, rat = make_world()
    scale_world(world, "hard", 0)
    assert (goblin.max_hp, goblin.attack_damage) == (130, 12)
    assert (rat.max_hp, rat.attack_damage) == (26, 12)

def test_scale_world_records_what_the_world_was_scaled_for():
    world, _, _ = make_world()
    scale_world(world, "easy", 2)
    assert world.scaled_for == ("easy", 2)

def test_scale_world_passes_keep_hp_on():
    world, goblin, _ = make_world()
    goblin.hp = 40
    scale_world(world, "hard", 0, keep_hp=True)
    assert goblin.hp == 40

def test_scale_world_with_no_rooms_still_records_the_setting():
    world = Map()
    scale_world(world, "story", 0)
    assert world.scaled_for == ("story", 0)

# ---- ensure_world_scaled ----

def test_ensure_world_scaled_scales_a_world_that_has_never_been_scaled():
    world, goblin, _ = make_world()
    player = Player(name="Hero", hp=20)
    player.difficulty = "hard"
    ensure_world_scaled(world, player)
    assert goblin.max_hp == 130
    assert world.scaled_for == ("hard", 0)

def test_ensure_world_scaled_does_nothing_when_the_setting_has_not_changed():
    """It runs before every command - it must not touch a world already scaled for this run. A stat set by hand is the proof: a rescale
    would undo it."""
    world, goblin, _ = make_world()
    player = Player(name="Hero", hp=20)
    player.difficulty = "hard"
    ensure_world_scaled(world, player)
    goblin.attack_damage = 99
    goblin.hp = 7
    ensure_world_scaled(world, player)
    assert (goblin.attack_damage, goblin.hp) == (99, 7)

def test_ensure_world_scaled_rescales_when_the_difficulty_changes():
    """What happens when Prometheus raises a run to Hard, or after 'dev difficulty'."""
    world, goblin, rat = make_world()
    player = Player(name="Hero", hp=20)
    ensure_world_scaled(world, player)
    player.difficulty = "hard"
    ensure_world_scaled(world, player)
    assert (goblin.max_hp, rat.max_hp) == (130, 26)
    assert world.scaled_for == ("hard", 0)

def test_ensure_world_scaled_rescales_when_the_ng_plus_cycle_changes():
    world, goblin, _ = make_world()
    player = Player(name="Hero", hp=20)
    ensure_world_scaled(world, player)
    player.ng_plus_cycle = 1
    ensure_world_scaled(world, player)
    assert (goblin.max_hp, goblin.attack_damage) == (125, 12)
    assert world.scaled_for == ("normal", 1)

def test_ensure_world_scaled_keeps_a_wounded_enemys_share_of_its_hp():
    world, goblin, _ = make_world()
    player = Player(name="Hero", hp=20)
    ensure_world_scaled(world, player)
    goblin.hp = 50
    player.difficulty = "hard"
    ensure_world_scaled(world, player)
    assert goblin.hp == 65

def test_ensure_world_scaled_changing_setting_twice_does_not_compound():
    world, goblin, _ = make_world()
    player = Player(name="Hero", hp=20)
    for difficulty in ("hard", "story", "normal"):
        player.difficulty = difficulty
        ensure_world_scaled(world, player)
    assert (goblin.hp, goblin.max_hp, goblin.attack_damage) == (100, 100, 10)
