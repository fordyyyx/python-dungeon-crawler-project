from dungeon_crawler.characters import Character
from dungeon_crawler.status_effects import StatusEffect

def test_status_effect_initialises_with_correct_attributes():
    effect = StatusEffect("Poison", -3, 4)
    assert effect.name == "Poison"
    assert effect.amount == -3
    assert effect.duration == 4

def test_status_effect_tick_with_negative_amount_deals_damage():
    character = Character(name="Hero", hp=20, attack_damage=5)
    effect = StatusEffect("Poison", -3, 4)
    effect.tick(character)
    assert character.hp == 17

def test_status_effect_tick_with_negative_amount_returns_damage_message():
    character = Character(name="Hero", hp=20, attack_damage=5)
    effect = StatusEffect("Poison", -3, 4)
    message = effect.tick(character)
    assert message == "Hero takes 3 damage from Poison."

def test_status_effect_tick_damage_cannot_exceed_current_hp():
    character = Character(name="Hero", hp=2, attack_damage=5)
    effect = StatusEffect("Poison", -10, 3)
    effect.tick(character)
    assert character.hp == 0

def test_status_effect_tick_with_positive_amount_heals():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.hp = 5
    effect = StatusEffect("Regen", 3, 4)
    effect.tick(character)
    assert character.hp == 8

def test_status_effect_tick_with_positive_amount_returns_heal_message():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.hp = 5
    effect = StatusEffect("Regen", 3, 4)
    message = effect.tick(character)
    assert message == "Hero recovers 3 HP from Regen."

def test_status_effect_tick_heal_does_not_exceed_max_hp():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.hp = 9
    effect = StatusEffect("Regen", 5, 4)
    effect.tick(character)
    assert character.hp == 10

def test_status_effect_tick_with_zero_amount_changes_no_hp_and_returns_nothing():
    """A zero-amount effect (e.g. Blinded) neither damages nor heals, and stays quiet - it used to print 'recovers 0 HP' every round."""
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.hp = 5
    effect = StatusEffect("Blinded", 0, 2)
    message = effect.tick(character)
    assert character.hp == 5
    assert message == ""

def test_status_effect_tick_with_zero_amount_still_counts_down():
    effect = StatusEffect("Blinded", 0, 2)
    effect.tick(Character(name="Hero", hp=10, attack_damage=5))
    assert effect.duration == 1

def test_status_effect_miss_chance_defaults_to_zero():
    assert StatusEffect("Poison", -3, 4).miss_chance == 0.0

def test_status_effect_stores_miss_chance():
    assert StatusEffect("Blinded", 0, 2, miss_chance=0.3).miss_chance == 0.3

def test_status_effect_tick_decrements_duration():
    character = Character(name="Hero", hp=20, attack_damage=5)
    effect = StatusEffect("Poison", -3, 4)
    effect.tick(character)
    assert effect.duration == 3

def test_status_effect_counts_down_on_attack_for_a_pure_miss_chance_effect():
    assert StatusEffect("Blinded", 0, 2, miss_chance=0.3).counts_down_on_attack is True

def test_status_effect_does_not_count_down_on_attack_without_a_miss_chance():
    assert StatusEffect("Neutral", 0, 2).counts_down_on_attack is False

def test_status_effect_does_not_count_down_on_attack_when_it_also_changes_hp():
    """A damaging effect still lasts a number of turns, even if it also adds a miss chance."""
    assert StatusEffect("Smoke", -1, 2, miss_chance=0.3).counts_down_on_attack is False

def test_status_effect_tick_leaves_an_attack_counted_effect_alone():
    character = Character(name="Hero", hp=10, attack_damage=5)
    effect = StatusEffect("Blinded", 0, 2, miss_chance=0.3)
    assert effect.tick(character) == ""
    assert effect.duration == 2
    assert character.hp == 10
