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

def test_status_effect_tick_with_zero_amount_takes_the_heal_branch():
    """amount < 0 is the only damage condition - a zero-amount effect goes through the heal path
    (healing 0), not the damage path."""
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.hp = 5
    effect = StatusEffect("Neutral", 0, 2)
    message = effect.tick(character)
    assert character.hp == 5
    assert message == "Hero recovers 0 HP from Neutral."

def test_status_effect_tick_decrements_duration():
    character = Character(name="Hero", hp=20, attack_damage=5)
    effect = StatusEffect("Poison", -3, 4)
    effect.tick(character)
    assert effect.duration == 3
