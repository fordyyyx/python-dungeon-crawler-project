from dungeon_crawler.characters import Character
from dungeon_crawler.spells import Spell

def test_spell_initialises_with_correct_attributes():
    spell = Spell(name="Firebolt", description="A bolt of fire.", mana_cost=5, damage=10)
    assert spell.name == "Firebolt"
    assert spell.description == "A bolt of fire."
    assert spell.mana_cost == 5
    assert spell.damage == 10

def test_spell_initialises_with_default_damage_heal_and_effect():
    spell = Spell(name="Mystery", description="", mana_cost=5)
    assert spell.damage == 0
    assert spell.heal_amount == 0
    assert spell.effect_name is None
    assert spell.effect_amount == 0
    assert spell.effect_duration == 0

def test_spell_cast_pure_heal_heals_caster():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    caster.hp = 10
    spell = Spell(name="Mend", description="", mana_cost=5, heal_amount=8)
    spell.cast(caster, None)
    assert caster.hp == 18

def test_spell_cast_pure_heal_does_not_exceed_max_hp():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    caster.hp = 15
    spell = Spell(name="Mend", description="", mana_cost=5, heal_amount=8)
    spell.cast(caster, None)
    assert caster.hp == 20

def test_spell_cast_pure_heal_returns_message():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    caster.hp = 10
    spell = Spell(name="Mend", description="", mana_cost=5, heal_amount=8)
    message = spell.cast(caster, None)
    assert message == "Hero recovers 8 HP."

def test_spell_cast_damage_deals_damage_to_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    spell.cast(caster, target)
    assert target.hp == 10

def test_spell_cast_damage_returns_message():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    message = spell.cast(caster, target)
    assert message == "Hero casts Firebolt at Goblin for 10 damage."

def test_spell_cast_damage_with_no_target_raises_error():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)

    try:
        spell.cast(caster, None)
        assert False, "Expected a ValueError but none was raised"
    except ValueError as e:
        assert str(e) == "You need a target for Firebolt - try 'target <enemy>' first."

def test_spell_cast_damage_appends_death_message_when_target_dies():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=5, attack_damage=0)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    message = spell.cast(caster, target)
    assert "Goblin has died." in message

def test_spell_cast_with_positive_effect_amount_applies_to_caster():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Regenerate", description="", mana_cost=5, effect_name="Regen", effect_amount=3, effect_duration=4)
    spell.cast(caster, None)
    assert len(caster.active_effects) == 1
    assert caster.active_effects[0].name == "Regen"

def test_spell_cast_with_negative_effect_amount_applies_to_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    spell = Spell(name="Blight", description="", mana_cost=5, effect_name="Poison", effect_amount=-3, effect_duration=4)

    spell.cast(caster, target)

    assert len(target.active_effects) == 1
    assert caster.active_effects == []

def test_spell_cast_with_negative_effect_amount_and_no_target_raises_error():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Blight", description="", mana_cost=5, effect_name="Poison", effect_amount=-3, effect_duration=4)

    try:
        spell.cast(caster, None)
        assert False, "Expected a ValueError but none was raised"
    except ValueError as e:
        assert str(e) == "You need a target for Blight - try 'target <enemy>' first."

def test_spell_cast_builds_a_fresh_effect_object_each_cast():
    """Each cast() must build its own StatusEffect - reusing the same spell on two characters must not
    secretly share one mutable effect object."""
    spell = Spell(name="Regenerate", description="", mana_cost=5, effect_name="Regen", effect_amount=3, effect_duration=4)
    hero = Character(name="Hero", hp=20, attack_damage=5)
    ally = Character(name="Ally", hp=20, attack_damage=5)
    spell.cast(hero, None)
    spell.cast(ally, None)
    assert hero.active_effects[0] is not ally.active_effects[0]

def test_spell_would_fail_returns_none_when_damage_spell_has_a_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    assert spell.would_fail(caster, target) is None

def test_spell_would_fail_returns_message_when_damage_spell_has_no_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    assert spell.would_fail(caster, None) == "You need a target for Firebolt - try 'target <enemy>' first."

def test_spell_would_fail_returns_message_when_damage_spell_target_is_dead():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    target.hp = 0
    spell = Spell(name="Firebolt", description="", mana_cost=5, damage=10)
    assert spell.would_fail(caster, target) == "You need a target for Firebolt - try 'target <enemy>' first."

def test_spell_would_fail_returns_none_for_pure_heal_regardless_of_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Mend", description="", mana_cost=5, heal_amount=8)
    assert spell.would_fail(caster, None) is None

def test_spell_would_fail_returns_none_when_offensive_effect_has_a_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    spell = Spell(name="Blight", description="", mana_cost=5, effect_name="Poison", effect_amount=-3, effect_duration=4)
    assert spell.would_fail(caster, target) is None

def test_spell_would_fail_returns_message_when_offensive_effect_has_no_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Blight", description="", mana_cost=5, effect_name="Poison", effect_amount=-3, effect_duration=4)
    assert spell.would_fail(caster, None) == "You need a target for Blight - try 'target <enemy>' first."

def test_spell_would_fail_returns_none_for_self_effect_regardless_of_target():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    spell = Spell(name="Regenerate", description="", mana_cost=5, effect_name="Regen", effect_amount=3, effect_duration=4)
    assert spell.would_fail(caster, None) is None

def test_spell_cast_combining_damage_and_offensive_effect():
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=0)
    spell = Spell(name="Venom Bolt", description="", mana_cost=5, damage=5, effect_name="Poison", effect_amount=-2, effect_duration=3)

    message = spell.cast(caster, target)

    assert target.hp == 15
    assert len(target.active_effects) == 1
    assert "casts Venom Bolt at Goblin for 5 damage." in message
    assert "afflicted with Poison" in message

def test_spell_cast_lethal_damage_skips_offensive_effect_on_dead_target():
    """Regression test for the fix: would_fail() only checks aliveness before the cast starts, so it can't catch
    this cast's own damage killing the target. cast() must skip the effect itself rather than applying poison
    to an already-dead target."""
    caster = Character(name="Hero", hp=20, attack_damage=5)
    target = Character(name="Goblin", hp=5, attack_damage=0)
    spell = Spell(name="Venom Bolt", description="", mana_cost=5, damage=5, effect_name="Poison", effect_amount=-2, effect_duration=3)

    message = spell.cast(caster, target)

    assert target.active_effects == []
    assert "afflicted with Poison" not in message
    assert "Goblin has died." in message

def test_spell_cast_self_effect_still_applies_when_damage_kills_target():
    """The is_alive() guard must only ever affect the offensive-recipient branch (recipient is target) - a
    self-targeted effect (recipient is caster) must still apply even when this same cast's damage kills target."""
    caster = Character(name="Hero", hp=15, attack_damage=5)
    target = Character(name="Goblin", hp=5, attack_damage=0)
    spell = Spell(name="Draining Bolt", description="", mana_cost=5, damage=5, effect_name="Regen", effect_amount=3, effect_duration=3)

    spell.cast(caster, target)

    assert len(caster.active_effects) == 1
    assert caster.active_effects[0].name == "Regen"
