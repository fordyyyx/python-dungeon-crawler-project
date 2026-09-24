from dungeon_crawler.characters import HP_PER_LEVEL, COMPANION_HP_PER_LEVEL, COMPANION_ATTACK_PER_LEVEL, STARTING_EXPERIENCE_TO_NEXT_LEVEL, WEAPON_LIFESTEAL_CAP, HEAVY_ATTACK_MISS_CHANCE, BLADE_HEAVY_MISS_MODIFIER, ARMOUR_WEIGHT_MISS_PENALTY, WEAPON_POISON_AMOUNT, WEAPON_POISON_DURATION, Character, Player, Enemy, Ally, Companion, Skill, AttackBoostSkill, DefenceBoostSkill, DoubleStrikeSkill, LastStandSkill, ThornsSkill, DodgeSkill, SkillPath, SkillTree
from dungeon_crawler.items import Weapon, Armour, Inventory, QuestItem
from dungeon_crawler.world import Room
from dungeon_crawler.status_effects import StatusEffect

def test_character_initialises_with_correct_stats():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.hp == 30
    assert character.attack_damage == 5

def test_character_initialises_with_default_armour_of_zero():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.armour == 0

def test_take_damage_reduces_hp():
    character = Character(name="Hero", hp=100, attack_damage=10)
    character.take_damage(30)
    assert character.hp == 70

def test_take_damage_cannot_go_below_zero():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.take_damage(50)
    assert character.hp == 0

def test_take_damage_applies_armour_reduction():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=3)
    character.take_damage(5)
    assert character.hp == 28

def test_take_damage_with_armour_exceeding_damage_still_deals_minimum_damage():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=10)
    character.take_damage(4)
    assert character.hp == 29

def test_take_damage_of_zero_deals_no_damage_despite_minimum_damage():
    """MINIMUM_DAMAGE only applies when amount > 0 - a 0-attack enemy (e.g. the Training Dummy) stays harmless."""
    character = Character(name="Hero", hp=30, attack_damage=5)
    damage_dealt, message = character.take_damage(0)
    assert damage_dealt == 0
    assert character.hp == 30

def test_take_damage_with_ignore_armour_skips_armour_reduction():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=5)
    damage_dealt, message = character.take_damage(10, ignore_armour=True)
    assert damage_dealt == 10

def test_take_damage_with_ignore_armour_still_applies_pending_damage_reduction():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=5)
    character.pending_damage_reduction = 4
    damage_dealt, message = character.take_damage(10, ignore_armour=True)
    assert damage_dealt == 6

def test_take_damage_with_ignore_armour_still_applies_iron_hide():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=5)
    character.has_iron_hide = True
    damage_dealt, message = character.take_damage(10, ignore_armour=True)
    assert damage_dealt == 9

def test_take_damage_with_iron_hide_reduces_damage_by_one():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_iron_hide = True
    damage_dealt, message = character.take_damage(10)
    assert damage_dealt == 9

def test_take_damage_with_iron_hide_still_deals_minimum_damage():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=10)
    character.has_iron_hide = True
    damage_dealt, message = character.take_damage(4)  # fully blocked by armour, then iron hide - minimum damage still applies
    assert damage_dealt == 1

def test_take_damage_kills_character():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.take_damage(10)
    assert character.is_alive() is False

def test_is_alive_true_when_hp_above_zero():
    character = Character(name="Hero", hp=10, attack_damage=5)
    assert character.is_alive() == True

def test_is_alive_false_when_hp_zero():
    character = Character(name="Hero", hp=0, attack_damage=5)
    assert character.is_alive() == False

def test_character_on_death_returns_default_message():
    character = Character(name="Hero", hp=0, attack_damage=5)
    message = character.on_death()
    assert "Hero has died" in message

def test_take_damage_lethal_damage_returns_death_message():
    character = Character(name="Hero", hp=10, attack_damage=5)
    damage_dealt, message = character.take_damage(10)
    assert "Hero has died" in message

def test_take_damage_non_lethal_damage_returns_empty_string():
    character = Character(name="Hero", hp=10, attack_damage=5)
    damage_dealt, message = character.take_damage(5)
    assert message == ""

def test_take_damage_returns_damage_dealt():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=3)
    damage_dealt, message = character.take_damage(10)
    assert damage_dealt == 7

def test_take_damage_with_last_stand_survives_lethal_hit_at_one_hp():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_last_stand = True
    damage_dealt, message = character.take_damage(50)
    assert character.hp == 1

def test_take_damage_with_last_stand_returns_refuses_to_fall_message():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_last_stand = True
    damage_dealt, message = character.take_damage(50)
    assert message == "Hero refuses to fall, clinging to life at 1 HP."

def test_take_damage_with_last_stand_does_not_trigger_when_already_at_one_hp():
    character = Character(name="Hero", hp=1, attack_damage=5)
    character.has_last_stand = True
    damage_dealt, message = character.take_damage(10)
    assert character.hp == 0
    assert character.is_alive() is False

def test_take_damage_with_last_stand_does_not_affect_non_lethal_hit():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_last_stand = True
    damage_dealt, message = character.take_damage(10)
    assert character.hp == 20
    assert message == ""

def test_take_damage_with_thorns_deals_counter_damage_to_attacker():
    target = Character(name="Goblin", hp=30, attack_damage=5)
    target.has_thorns = True
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    target.take_damage(10, attacker=attacker)
    assert attacker.hp == 48

def test_take_damage_with_thorns_counter_damage_message():
    target = Character(name="Goblin", hp=30, attack_damage=5)
    target.has_thorns = True
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    damage_dealt, message = target.take_damage(10, attacker=attacker)
    assert message == "Hero takes 2 damage from the counter-strike."

def test_take_damage_with_thorns_counter_damage_minimum_is_one():
    target = Character(name="Goblin", hp=30, attack_damage=5)
    target.has_thorns = True
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    target.take_damage(2, attacker=attacker)
    assert attacker.hp == 49

def test_take_damage_with_thorns_does_nothing_without_attacker():
    target = Character(name="Goblin", hp=30, attack_damage=5)
    target.has_thorns = True
    damage_dealt, message = target.take_damage(10)
    assert message == ""

def test_take_damage_with_thorns_triggers_on_a_minimum_damage_hit():
    """Armour can no longer fully block a landed hit, so thorns always has at least 1 damage to reflect."""
    target = Character(name="Goblin", hp=30, attack_damage=5, armour=10)
    target.has_thorns = True
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    target.take_damage(4, attacker=attacker)
    assert attacker.hp == 49

def test_take_damage_with_thorns_counter_damage_cannot_go_below_zero():
    attacker = Character(name="Hero", hp=1, attack_damage=10)
    target = Character(name="Goblin", hp=30, attack_damage=5)
    target.has_thorns = True
    target.take_damage(10, attacker=attacker)
    assert attacker.hp == 0

def test_take_damage_with_thorns_includes_counter_message_with_death_message():
    target = Character(name="Goblin", hp=5, attack_damage=5)
    target.has_thorns = True
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    damage_dealt, message = target.take_damage(10, attacker=attacker)
    assert message == "Hero takes 2 damage from the counter-strike.\nGoblin has died."

def test_take_damage_with_zero_dodge_chance_never_dodges():
    """random.random() always returns a value in [0.0, 1.0), so 'random.random() < 0.0' is deterministically
    false - no monkeypatch needed to prove the default (dodge_chance=0.0) never dodges."""
    character = Character(name="Hero", hp=30, attack_damage=5)
    damage_dealt, message = character.take_damage(10)
    assert damage_dealt == 10
    assert "dodges" not in message

def test_take_damage_with_dodge_forced_to_succeed_deals_no_damage(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.dodge_chance = 0.5
    damage_dealt, message = character.take_damage(50)
    assert damage_dealt == 0
    assert character.hp == 30

def test_take_damage_with_dodge_forced_to_succeed_returns_dodge_message(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.dodge_chance = 0.5
    damage_dealt, message = character.take_damage(50)
    assert message == "Hero dodges the attack!"

def test_take_damage_with_dodge_forced_to_fail_deals_normal_damage(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.99)
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.dodge_chance = 0.5
    damage_dealt, message = character.take_damage(10)
    assert damage_dealt == 10
    assert character.hp == 20

def test_take_damage_with_dodge_does_not_consume_pending_damage_reduction(monkeypatch):
    """Dodge returns before the brace-consumption line runs - a successful dodge leaves an unused brace
    intact for the next hit, rather than wasting it on a hit that never landed."""
    monkeypatch.setattr("random.random", lambda: 0.0)
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.dodge_chance = 0.5
    character.pending_damage_reduction = 4
    character.take_damage(10)
    assert character.pending_damage_reduction == 4

def test_take_damage_with_dodge_prevents_thorns_counter_attack(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.dodge_chance = 0.5
    character.has_thorns = True
    attacker = Character(name="Goblin", hp=10, attack_damage=5)
    character.take_damage(10, attacker=attacker)
    assert attacker.hp == 10

def test_take_damage_reduces_equipped_body_armour_durability_by_one():
    character = Character(name="Hero", hp=100, attack_damage=5)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=5)
    armour.use(character)
    character.take_damage(10)
    assert armour.durability == 4

def test_take_damage_reduces_helmet_and_body_durability_independently():
    character = Character(name="Hero", hp=100, attack_damage=5)
    helmet = Armour(name="Helm", description="", defence=2, slot="helmet", max_durability=3)
    body = Armour(name="Plate", description="", defence=4, slot="body", max_durability=3)
    helmet.use(character)
    body.use(character)
    character.take_damage(5)
    assert helmet.durability == 2
    assert body.durability == 2

def test_take_damage_degrades_durability_even_when_damage_is_fully_blocked():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=0)
    armour = Armour(name="Shield", description="", defence=100, slot="body", max_durability=5)
    armour.use(character) # blocks any realistic hit entirely
    character.take_damage(5)
    assert armour.durability == 4

def test_take_damage_backs_out_defence_when_armour_breaks():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=0)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=1)
    armour.use(character) # character.armour == 3
    character.take_damage(1)
    assert armour.durability == 0
    assert character.armour == 0

def test_take_damage_already_broken_armour_does_not_reduce_defence_again():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=0)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=1)
    armour.use(character)
    character.take_damage(1) # breaks it, armour drops from 3 to 0
    character.take_damage(1) # already broken - nothing left to back out
    assert armour.durability == 0
    assert character.armour == 0

def test_take_damage_with_unyielding_tide_does_not_back_out_defence_when_armour_breaks():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=0)
    character.has_unyielding_tide = True
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=1)
    armour.use(character) # character.armour == 3
    character.take_damage(1)
    assert armour.durability == 0
    assert character.armour == 3

def test_take_damage_with_unyielding_tide_still_degrades_durability():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=0)
    character.has_unyielding_tide = True
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=5)
    armour.use(character)
    character.take_damage(1)
    assert armour.durability == 4

def test_take_damage_armour_still_reduces_damage_on_the_hit_that_breaks_it():
    """Durability degrades after reduced (this hit's damage) is already calculated - the piece's defence
    still protects the hit that breaks it, only future hits lose the benefit."""
    character = Character(name="Hero", hp=100, attack_damage=5, armour=0)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=1)
    armour.use(character)

    damage_dealt_first, _ = character.take_damage(10) # still protected by the armour that breaks this hit
    damage_dealt_second, _ = character.take_damage(10) # armour's defence is gone now

    assert damage_dealt_first == 7
    assert damage_dealt_second == 10

def test_take_damage_with_dodge_does_not_degrade_armour_durability(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    character = Character(name="Hero", hp=100, attack_damage=5)
    character.dodge_chance = 0.5
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=5)
    armour.use(character)
    character.take_damage(10)
    assert armour.durability == 5

def test_take_damage_with_pending_damage_reduction_reduces_incoming_damage():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.pending_damage_reduction = 4
    character.take_damage(10)
    assert character.hp == 24 # 10 - 4 brace

def test_take_damage_with_pending_damage_reduction_is_consumed_after_one_hit():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.pending_damage_reduction = 4
    character.take_damage(10)
    assert character.pending_damage_reduction == 0

def test_take_damage_with_pending_damage_reduction_does_not_carry_over_to_next_hit():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.pending_damage_reduction = 4
    character.take_damage(10) # consumes the brace: 30 - 6 = 24
    character.take_damage(10) # full damage this time: 24 - 10 = 14
    assert character.hp == 14

def test_take_damage_with_pending_damage_reduction_exceeding_damage_still_deals_minimum_damage():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.pending_damage_reduction = 20
    character.take_damage(10)
    assert character.hp == 29

def test_take_damage_with_pending_damage_reduction_is_still_consumed_when_it_fully_blocks_the_hit():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.pending_damage_reduction = 20
    character.take_damage(10)
    assert character.pending_damage_reduction == 0

def test_take_damage_with_pending_damage_reduction_applies_before_armour():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=3)
    character.pending_damage_reduction = 4
    damage_dealt, message = character.take_damage(10)
    assert damage_dealt == 3 # 10 - 4 brace = 6, then - 3 armour = 3

def test_take_damage_with_pending_damage_reduction_exceeding_damage_still_triggers_thorns():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_thorns = True
    character.pending_damage_reduction = 20
    attacker = Character(name="Goblin", hp=10, attack_damage=5)
    character.take_damage(10, attacker=attacker)
    assert attacker.hp == 9 # the minimum 1 damage got through, so thorns reflects its minimum 1

def test_character_initialises_with_no_active_effects():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.active_effects == []

def test_apply_status_effect_adds_new_effect():
    character = Character(name="Hero", hp=30, attack_damage=5)
    effect = StatusEffect("Poison", -3, 4)
    character.apply_status_effect(effect)
    assert effect in character.active_effects

def test_apply_status_effect_returns_afflicted_message():
    character = Character(name="Hero", hp=30, attack_damage=5)
    effect = StatusEffect("Poison", -3, 4)
    message = character.apply_status_effect(effect)
    assert message == "Hero is afflicted with Poison."

def test_apply_status_effect_with_existing_same_name_prolongs_duration():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 4))
    character.apply_status_effect(StatusEffect("Poison", -3, 2))
    assert len(character.active_effects) == 1
    assert character.active_effects[0].duration == 6

def test_apply_status_effect_with_existing_same_name_returns_prolonged_message():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 4))
    message = character.apply_status_effect(StatusEffect("Poison", -3, 2))
    assert message == "Hero's Poison is prolonged."

def test_apply_status_effect_reapplication_does_not_change_amount():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 4))
    character.apply_status_effect(StatusEffect("Poison", -5, 2))
    assert character.active_effects[0].amount == -3

def test_apply_status_effect_different_names_both_stay_active():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 4))
    character.apply_status_effect(StatusEffect("Regen", 2, 3))
    assert len(character.active_effects) == 2

def test_tick_status_effects_returns_empty_list_when_no_active_effects():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.tick_status_effects() == []

def test_tick_status_effects_applies_each_active_effect():
    character = Character(name="Hero", hp=20, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 4))
    character.tick_status_effects()
    assert character.hp == 17

def test_tick_status_effects_removes_effect_when_duration_expires():
    character = Character(name="Hero", hp=20, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 1))
    character.tick_status_effects()
    assert character.active_effects == []

def test_tick_status_effects_keeps_effect_when_duration_remains():
    character = Character(name="Hero", hp=20, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 2))
    character.tick_status_effects()
    assert len(character.active_effects) == 1
    assert character.active_effects[0].duration == 1

def test_tick_status_effects_stops_ticking_further_effects_once_character_dies():
    """Same 'stop once dead' precedent as resolve_combat_round() - a tick that kills the character must
    not let a later effect in the list also tick this round."""
    character = Character(name="Hero", hp=5, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -10, 3))
    character.apply_status_effect(StatusEffect("Fire", -3, 3))

    messages = character.tick_status_effects()

    assert character.hp == 0
    assert not any("Fire" in message for message in messages)

def test_tick_status_effects_appends_death_message_when_a_tick_kills_the_character():
    character = Character(name="Hero", hp=5, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -10, 3))
    messages = character.tick_status_effects()
    assert messages[-1] == "Hero has died."

def test_tick_status_effects_does_not_append_death_message_when_character_survives():
    character = Character(name="Hero", hp=20, attack_damage=5)
    character.apply_status_effect(StatusEffect("Poison", -3, 2))
    messages = character.tick_status_effects()
    assert len(messages) == 1

def test_attack_reduces_target_hp():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    attacker.attack(target)
    assert target.hp == 10

def test_attack_returns_message_naming_attacker_and_target():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 10 damage."

def test_attack_appends_death_message_when_target_dies():
    attacker = Character(name="Hero", hp=30, attack_damage=100)
    target = Character(name="Goblin", hp=20, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 100 damage.\nGoblin has died."

def test_attack_message_shows_armour_reduced_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=20, attack_damage=5, armour=4)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 6 damage. (4 deflected by armour)"

def test_attack_message_shows_minimum_damage_when_armour_exceeds_attack():
    attacker = Character(name="Hero", hp=30, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=5, armour=10)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 1 damage. (4 deflected by armour)"

def test_attack_with_double_strike_deals_second_hit():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    assert target.hp == 85

def test_attack_with_double_strike_message_includes_second_strike():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target)
    assert "Hero strikes again for 5 damage." in message

def test_attack_with_double_strike_skips_second_hit_when_target_dies_from_first():
    attacker = Character(name="Hero", hp=30, attack_damage=100)
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=20, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 100 damage.\nGoblin has died."

def test_attack_with_double_strike_second_hit_can_finish_off_target():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=12, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 10 damage.\nHero strikes again for 5 damage.\nGoblin has died."
    assert target.is_alive() is False

def test_attack_triggers_thorns_counter_attack_on_attacker():
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    target = Character(name="Goblin", hp=30, attack_damage=5)
    target.has_thorns = True
    message = attacker.attack(target)
    assert attacker.hp == 48
    assert "Hero takes 2 damage from the counter-strike." in message

def test_attack_with_berserking_at_or_below_half_hp_adds_bonus_damage():
    attacker = Character(name="Hero", hp=20, attack_damage=10)
    attacker.hp = 10  # exactly half of max_hp
    attacker.has_berserking = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target)
    assert target.hp == 88  # 100 - (10 + 2)

def test_attack_with_berserking_above_half_hp_adds_no_bonus_damage():
    attacker = Character(name="Hero", hp=20, attack_damage=10)
    attacker.hp = 15  # above half of max_hp
    attacker.has_berserking = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target)
    assert target.hp == 90  # 100 - 10, no bonus

def test_attack_with_bull_rush_against_full_hp_target_adds_bonus_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_bull_rush = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target)
    assert target.hp == 87  # 100 - (10 + 3)

def test_attack_with_bull_rush_against_damaged_target_adds_no_bonus_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_bull_rush = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    target.hp = 50
    attacker.attack(target)
    assert target.hp == 40  # 50 - 10, no bonus

def test_attack_with_lifesteal_heals_attacker_for_half_of_damage_dealt():
    attacker = Character(name="Lamia", hp=30, attack_damage=10)
    attacker.has_lifesteal = True
    attacker.hp = 10
    target = Character(name="Hero", hp=100, attack_damage=0)
    attacker.attack(target)
    assert attacker.hp == 15  # 10 + (10 // 2)

def test_attack_with_lifesteal_uses_damage_actually_dealt_after_armour():
    attacker = Character(name="Lamia", hp=30, attack_damage=10)
    attacker.has_lifesteal = True
    attacker.hp = 10
    target = Character(name="Hero", hp=100, attack_damage=0, armour=4)
    attacker.attack(target)
    assert attacker.hp == 13  # 6 damage dealt after armour, so 10 + 3

def test_attack_with_lifesteal_does_not_heal_above_max_hp():
    attacker = Character(name="Lamia", hp=30, attack_damage=10)
    attacker.has_lifesteal = True
    attacker.hp = 28
    target = Character(name="Hero", hp=100, attack_damage=0)
    attacker.attack(target)
    assert attacker.hp == 30

def test_attack_with_lifesteal_does_not_heal_when_no_damage_is_dealt():
    attacker = Character(name="Lamia", hp=30, attack_damage=3)
    attacker.has_lifesteal = True
    attacker.hp = 10
    target = Character(name="Hero", hp=100, attack_damage=0, armour=5)
    attacker.attack(target)
    assert attacker.hp == 10

def test_attack_without_lifesteal_does_not_heal_attacker():
    attacker = Character(name="Lamia", hp=30, attack_damage=10)
    attacker.hp = 10
    target = Character(name="Hero", hp=100, attack_damage=0)
    attacker.attack(target)
    assert attacker.hp == 10

def test_attack_with_lifesteal_message_mentions_hp_drained():
    attacker = Character(name="Lamia", hp=30, attack_damage=10)
    attacker.has_lifesteal = True
    attacker.hp = 10
    target = Character(name="Hero", hp=100, attack_damage=0)
    message = attacker.attack(target)
    assert "drains 5 HP" in message

def test_attack_with_lifesteal_at_full_hp_has_no_drain_message():
    attacker = Character(name="Lamia", hp=30, attack_damage=10)
    attacker.has_lifesteal = True
    target = Character(name="Hero", hp=100, attack_damage=0)
    message = attacker.attack(target)
    assert "drains" not in message

def test_attack_petrifying_gaze_forced_success_poisons_surviving_target(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)  # below the 0.15 threshold
    attacker = Character(name="Hero", hp=30, attack_damage=5)
    attacker.has_petrifying_gaze = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target)
    assert len(target.active_effects) == 1
    assert target.active_effects[0].name == "Poison"

def test_attack_petrifying_gaze_forced_failure_does_not_poison_target(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.2)  # above the 0.15 threshold
    attacker = Character(name="Hero", hp=30, attack_damage=5)
    attacker.has_petrifying_gaze = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target)
    assert target.active_effects == []

def test_attack_petrifying_gaze_does_not_apply_to_a_target_killed_by_the_hit(monkeypatch):
    """The death_message branch returns early, before the petrifying gaze check - a killed target
    must never be poisoned, even when the roll would otherwise succeed."""
    monkeypatch.setattr("random.random", lambda: 0.0)  # would trigger the gaze if the code ever reached it
    attacker = Character(name="Hero", hp=30, attack_damage=100)
    attacker.has_petrifying_gaze = True
    target = Character(name="Goblin", hp=10, attack_damage=0)
    message = attacker.attack(target)
    assert target.active_effects == []
    assert "afflicted with Poison" not in message

def test_player_initialises_with_inventory():
    player = Player(name="Hero", hp=10)
    assert isinstance(player.inventory, Inventory)
    assert len(player.inventory) == 0

def test_player_initialises_with_correct_stats():
    player = Player(name="Hero", hp=50, attack_damage=7, armour=2)
    assert player.name == "Hero"
    assert player.hp == 50
    assert player.attack_damage == 7
    assert player.armour == 2

def test_player_initialises_at_level_one_with_no_experience():
    player = Player(name="Hero", hp=10)
    assert player.level == 1
    assert player.experience == 0

def test_player_initialises_with_default_experience_to_next_level():
    player = Player(name="Hero", hp=10)
    assert player.experience_to_next_level == 50

def test_player_initialises_with_no_gold():
    player = Player(name="Hero", hp=10)
    assert player.gold == 0

def test_player_initialises_with_no_intellect():
    player = Player(name="Hero", hp=10)
    assert player.intellect == 0

def test_gain_experience_increases_experience():
    player = Player(name="Hero", hp=10)
    player.gain_experience(10)
    assert player.experience == 10

def test_gain_experience_returns_message_when_below_threshold():
    player = Player(name="Hero", hp=10)
    message = player.gain_experience(10)
    assert message == "Hero gains 10 experience."

def test_gain_experience_below_threshold_does_not_level_up():
    player = Player(name="Hero", hp=10)
    player.gain_experience(10)
    assert player.level == 1

def test_gain_experience_at_threshold_levels_up():
    player = Player(name="Hero", hp=10)
    player.gain_experience(50)
    assert player.level == 2

def test_gain_experience_at_threshold_returns_combined_message():
    player = Player(name="Hero", hp=10)
    message = player.gain_experience(50)
    assert message == "Hero gains 50 experience.\nHero reaches level 2! +2 max HP, and a skill point is available."

def test_gain_experience_over_threshold_carries_remainder_forward():
    player = Player(name="Hero", hp=10)
    player.gain_experience(70)
    assert player.experience == 20

def test_gain_experience_with_excess_experience_only_levels_up_once():
    player = Player(name="Hero", hp=10)
    player.gain_experience(200)
    assert player.level == 2

def test_level_up_increments_level():
    player = Player(name="Hero", hp=10)
    player.level_up()
    assert player.level == 2

def test_level_up_subtracts_threshold_from_experience():
    player = Player(name="Hero", hp=10)
    player.experience = 60
    player.level_up()
    assert player.experience == 10

def test_level_up_grants_a_skill_point():
    player = Player(name="Hero", hp=10)
    player.level_up()
    assert player.skill_tree.skill_points == 1

def test_level_up_scales_experience_threshold():
    player = Player(name="Hero", hp=10)
    player.level_up()
    assert player.experience_to_next_level == 75

def test_level_up_returns_level_up_message():
    player = Player(name="Hero", hp=10)
    message = player.level_up()
    assert message == "Hero reaches level 2! +2 max HP, and a skill point is available."

def test_level_up_increases_intellect():
    player = Player(name="Hero", hp=10)
    player.level_up()
    assert player.intellect == 1


def test_player_initialises_with_default_attack_damage():
    player = Player(name="Hero", hp=10)
    assert player.attack_damage == 5

def test_player_on_death_returns_game_over_message():
    player = Player(name="Hero", hp=10)
    message = player.on_death()
    assert message == "Hero has fallen. Game Over."

def test_player_initialises_with_no_companion_by_default():
    player = Player(name="Hero", hp=10)
    assert player.companion is None

def test_player_team_returns_just_self_when_no_companion():
    player = Player(name="Hero", hp=10)
    assert len(player.team) == 1
    assert player.team[0] is player

def test_player_team_includes_companion_when_alive():
    player = Player(name="Hero", hp=10)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    player.companion = companion
    assert companion in player.team
    assert len(player.team) == 2

def test_player_team_lists_self_before_companion():
    player = Player(name="Hero", hp=10)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    player.companion = companion
    assert player.team[0] is player
    assert player.team[1] is companion

def test_player_team_excludes_downed_companion():
    player = Player(name="Hero", hp=10)
    home = Room("Camp")
    companion = Companion(name="Imp", hp=10, home_room=home)
    companion.hp = 0
    player.companion = companion
    assert companion not in player.team
    assert len(player.team) == 1

def test_player_initialises_with_no_known_spells():
    player = Player(name="Hero", hp=10)
    assert player.known_spells == []

def test_player_initialises_with_mana():
    player = Player(name="Hero", hp=10)
    assert player.mana == 20

def test_player_initialises_with_max_mana():
    player = Player(name="Hero", hp=10)
    assert player.max_mana == 20

def test_player_initialises_with_no_spell_cooldowns():
    player = Player(name="Hero", hp=10)
    assert player.spell_cooldowns == {}

def test_tick_spell_cooldowns_with_no_cooldowns_does_nothing():
    player = Player(name="Hero", hp=10)
    player.tick_spell_cooldowns()
    assert player.spell_cooldowns == {}

def test_tick_spell_cooldowns_removes_cooldown_that_reaches_zero():
    player = Player(name="Hero", hp=10)
    player.spell_cooldowns["Firebolt"] = 1
    player.tick_spell_cooldowns()
    assert "Firebolt" not in player.spell_cooldowns

def test_tick_spell_cooldowns_decrements_cooldown_above_one():
    player = Player(name="Hero", hp=10)
    player.spell_cooldowns["Firebolt"] = 3
    player.tick_spell_cooldowns()
    assert player.spell_cooldowns["Firebolt"] == 2

def test_tick_spell_cooldowns_handles_each_spell_independently():
    player = Player(name="Hero", hp=10)
    player.spell_cooldowns["Firebolt"] = 1
    player.spell_cooldowns["Mend"] = 3
    player.tick_spell_cooldowns()
    assert "Firebolt" not in player.spell_cooldowns
    assert player.spell_cooldowns["Mend"] == 2

def test_enemy_initialises_with_correct_stats():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, armour=1)
    assert enemy.name == "Goblin"
    assert enemy.hp == 15
    assert enemy.attack_damage == 4
    assert enemy.armour == 1

def test_enemy_initialises_with_empty_loot_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.loot == []

def test_enemy_initialises_with_description():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, description="A grumbling goblin, unhappy to be disturbed.")
    assert enemy.description == "A grumbling goblin, unhappy to be disturbed."

def test_enemy_on_death_returns_defeated_message():
    enemy = Enemy(name="Hades", hp=60, attack_damage=20)
    message = enemy.on_death()
    assert "Hades has been defeated." in message

def test_enemy_on_death_drops_loot():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    damage_dealt, message = enemy.take_damage(10)
    assert "Iron Sword" in message

def test_enemy_on_death_with_no_loot_does_not_include_drop_message():
    enemy = Enemy("Hades", hp=60, attack_damage=20)
    message = enemy.on_death()
    assert "dropped" not in message.lower()

def test_player_get_stats(capsys):
    player = Player(name="hero", hp=100)
    print(player.get_stats())
    captured = capsys.readouterr()
    assert "hero ():" in captured.out

def test_get_stats_includes_intellect_line():
    player = Player(name="hero", hp=100)
    player.intellect = 3
    stats = player.get_stats()
    assert "3 INT" in stats

def test_player_get_stats_has_no_leading_whitespace():
    player = Player(name="hero", hp=100)
    stats = player.get_stats()
    assert stats.startswith("hero ():")

def test_player_initialises_with_empty_ancestry_label_by_default():
    player = Player(name="hero", hp=100)
    assert player.ancestry_label == ""

def test_player_initialises_with_ancestry_label():
    player = Player(name="hero", hp=100, ancestry_label="Descendant of Zeus")
    assert player.ancestry_label == "Descendant of Zeus"

def test_player_initialises_with_auto_talk_false():
    player = Player(name="hero", hp=100)
    assert player.auto_talk is False

def test_player_initialises_with_empty_secondary_ancestry_label_by_default():
    player = Player(name="hero", hp=100)
    assert player.secondary_ancestry_label == ""

def test_player_initialises_with_empty_visited_floors_by_default():
    player = Player(name="hero", hp=100)
    assert player.visited_floors == set()

def test_player_initialises_with_dev_mode_false_by_default():
    player = Player(name="hero", hp=100)
    assert player.dev_mode is False

def test_get_stats_header_line_includes_ancestry_label_when_set():
    player = Player(name="hero", hp=100, ancestry_label="Descendant of Zeus")
    stats = player.get_stats()
    assert stats.startswith("hero (Descendant of Zeus):")

def test_get_stats_does_not_include_secondary_gift_line_by_default():
    player = Player(name="hero", hp=100)
    stats = player.get_stats()
    assert "Secondary gift" not in stats

def test_get_stats_includes_secondary_gift_line_when_set():
    player = Player(name="hero", hp=100)
    player.secondary_ancestry_label = "Reckless Strength - heavy attacks never miss"
    stats = player.get_stats()
    assert "Secondary gift: Reckless Strength - heavy attacks never miss" in stats

def test_get_stats_does_not_include_unlocked_skills_section_by_default():
    player = Player(name="hero", hp=100)
    stats = player.get_stats()
    assert "Unlocked Skills" not in stats

def test_get_stats_includes_unlocked_skills_section_when_skill_unlocked():
    player = Player(name="hero", hp=100)
    player.skill_tree.skill_points = 1
    player.skill_tree.invest("defence", player)
    stats = player.get_stats()
    assert "Unlocked Skills:" in stats
    assert "  - Hardened Skin" in stats

def test_get_stats_has_no_weapon_summary_when_nothing_equipped():
    player = Player(name="hero", hp=100, attack_damage=10)
    stats = player.get_stats()
    assert "10 ATK\n" in stats

def test_get_stats_includes_melee_weapon_bonus_in_atk_line():
    player = Player(name="hero", hp=100, attack_damage=10)
    sword = Weapon(name="Sword", description="", damage=5)
    sword.use(player)
    stats = player.get_stats()
    assert "10 ATK (+5 melee)" in stats

def test_get_stats_includes_ranged_weapon_bonus_in_atk_line():
    player = Player(name="hero", hp=100, attack_damage=10)
    bow = Weapon(name="Bow", description="", damage=4, slot="ranged")
    bow.use(player)
    stats = player.get_stats()
    assert "10 ATK (+4 ranged)" in stats

def test_get_stats_includes_both_weapon_bonuses_when_both_equipped():
    player = Player(name="hero", hp=100, attack_damage=10)
    sword = Weapon(name="Sword", description="", damage=5)
    bow = Weapon(name="Bow", description="", damage=4, slot="ranged")
    sword.use(player)
    bow.use(player)
    stats = player.get_stats()
    assert "10 ATK (+5 melee, +4 ranged)" in stats

def test_get_stats_unlocked_skills_section_lists_skills_from_multiple_paths():
    player = Player(name="hero", hp=100)
    player.skill_tree.skill_points = 2
    player.skill_tree.invest("defence", player)
    player.skill_tree.invest("attack", player)
    stats = player.get_stats()
    assert "  - Hardened Skin" in stats
    assert "  - Iron Grip" in stats

def test_ally_initialises_with_empty_inventory():
    ally = Ally(name="Chiron")
    assert isinstance(ally.inventory, Inventory)
    assert len(ally.inventory) == 0

def test_ally_initialises_with_description():
    ally = Ally(name="Chiron", description="Half man, half horse, entirely patient.")
    assert ally.description == "Half man, half horse, entirely patient."

def test_ally_talk_returns_hint_when_set():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron", hint="Beware the minotaur.")
    assert ally.talk(player) == "Beware the minotaur."

def test_ally_talk_returns_default_message_when_no_hint():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron")
    assert ally.talk(player) == "Chiron has nothing to say."

def test_ally_initialises_with_items_adds_them_to_inventory():
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally = Ally(name="Chiron", items=[sword])
    assert sword in ally.inventory.items

def test_ally_initialises_with_default_required_items_as_empty_list():
    ally = Ally(name="Chiron")
    assert ally.required_items == []

def test_ally_initialises_with_no_reward_by_default():
    ally = Ally(name="Chiron")
    assert ally.reward is None

def test_ally_initialises_with_reward():
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally = Ally(name="Chiron", reward=sword)
    assert ally.reward is sword

def test_ally_initialises_with_empty_post_trade_message_by_default():
    ally = Ally(name="Chiron")
    assert ally.post_trade_message == ""

def test_ally_initialises_with_post_trade_message():
    ally = Ally(name="Chiron", post_trade_message="Safe travels, hero.")
    assert ally.post_trade_message == "Safe travels, hero."

def test_ally_initialises_with_trade_completed_false():
    ally = Ally(name="Chiron")
    assert ally.trade_completed is False

def test_ally_talk_returns_hint_complete_when_trade_completed_even_if_missing_required_items():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron", hint="Learn to move first.", hint_complete="Well done.", required_items=["Wooden Sword"])
    ally.trade_completed = True
    assert ally.talk(player) == "Well done."

def test_ally_talk_falls_back_to_hint_when_trade_completed_but_no_hint_complete_set():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron", hint="Learn to move first.", required_items=["Wooden Sword"])
    ally.trade_completed = True
    assert ally.talk(player) == "Learn to move first."

def test_ally_talk_returns_hint_when_player_missing_required_items():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Chiron", hint="Learn to move first.", hint_complete="Well done.", required_items=["Wooden Sword"])
    assert ally.talk(player) == "Learn to move first."

def test_ally_talk_returns_hint_complete_when_player_has_required_items():
    player = Player(name="hero", hp=10)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    ally = Ally(name="Chiron", hint="Learn to move first.", hint_complete="Well done.", required_items=["Wooden Sword"])
    assert ally.talk(player) == "Well done."

def test_ally_talk_falls_back_to_hint_when_required_items_met_but_no_hint_complete_set():
    player = Player(name="hero", hp=10)
    sword = Weapon(name="Wooden Sword", description="", damage=1)
    player.inventory.add(sword)
    ally = Ally(name="Chiron", hint="Learn to move first.", required_items=["Wooden Sword"])
    assert ally.talk(player) == "Learn to move first."

def test_ally_give_item_adds_item_to_player_inventory():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    ally.give_item("Bronze Xiphos", player)
    assert sword in player.inventory.items

def test_ally_give_item_removes_item_from_ally_inventory():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    ally.give_item("Bronze Xiphos", player)
    assert sword not in ally.inventory.items

def test_ally_give_item_returns_confirmation_message():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    message = ally.give_item("Bronze Xiphos", player)
    assert message == "Chiron gives you the Bronze Xiphos."

def test_ally_give_item_returns_message_when_item_not_found():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    message = ally.give_item("Bronze Xiphos", player)
    assert message == "Chiron does not have that item."

def test_ally_give_item_matches_item_name_case_insensitively():
    ally = Ally(name="Chiron")
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    ally.inventory.add(sword)
    ally.give_item("bronze xiphos", player)
    assert sword in player.inventory.items

def test_companion_initialises_with_correct_stats():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, attack_damage=4)
    assert companion.hp == 15
    assert companion.attack_damage == 4

def test_companion_initialises_with_home_room():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.home_room is home

def test_companion_initialises_with_default_armour_zero():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.armour == 0

def test_companion_initialises_with_default_description_empty():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.description == ""

def test_companion_initialises_with_description():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, description="A loyal imp.")
    assert companion.description == "A loyal imp."

def test_companion_initialises_with_empty_required_items_by_default():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.required_items == []

def test_companion_initialises_with_required_items():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, required_items=["Bronze Xiphos"])
    assert companion.required_items == ["Bronze Xiphos"]

def test_companion_initialises_with_default_aggression_weight():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.aggression_weight == 1.0

def test_companion_initialises_with_default_caution_weight():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.caution_weight == 1.0

def test_companion_initialises_with_default_randomness_weight():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.randomness_weight == 0.3

def test_companion_initialises_with_custom_aggression_weight():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, aggression_weight=2.5)
    assert companion.aggression_weight == 2.5

def test_companion_initialises_with_custom_caution_weight():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, caution_weight=1.8)
    assert companion.caution_weight == 1.8

def test_companion_initialises_with_custom_randomness_weight():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, randomness_weight=0.6)
    assert companion.randomness_weight == 0.6

def test_companion_initialises_with_no_brace_amount_by_default():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.brace_amount == 0

def test_companion_initialises_with_custom_brace_amount():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, brace_amount=3)
    assert companion.brace_amount == 3

def test_companion_initialises_with_no_heal_amount_by_default():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    assert companion.heal_amount == 0

def test_companion_initialises_with_custom_heal_amount():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home, heal_amount=5)
    assert companion.heal_amount == 5

def test_companion_on_death_returns_downed_message():
    home = Room("Camp")
    companion = Companion(name="Imp", hp=15, home_room=home)
    message = companion.on_death()
    assert message == "Imp is downed and can no longer fight - a Reviver can bring them back."

def test_character_initialises_with_max_hp_equal_to_hp():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.max_hp == 30

def test_enemy_on_death_drops_multiple_loot_items_lists_all_names():
    sword = Weapon(name="Iron Sword", description="", damage=5)
    shield = Weapon(name="Bronze Shield", description="", damage=0)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword, shield])
    message = enemy.on_death()
    assert "Iron Sword, Bronze Shield" in message

def test_ally_initialises_with_empty_description_by_default():
    ally = Ally(name="Chiron")
    assert ally.description == ""

def test_character_initialises_with_no_equipped_melee_weapon():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_melee_weapon is None

def test_character_initialises_with_no_equipped_ranged_weapon():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_ranged_weapon is None

def test_character_initialises_with_no_equipped_helmet():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_helmet is None

def test_character_initialises_with_no_equipped_body_armour():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_body is None

def test_character_initialises_with_has_double_strike_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_double_strike is False

def test_character_initialises_with_has_last_stand_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_last_stand is False

def test_character_initialises_with_has_thorns_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_thorns is False

def test_character_initialises_with_in_combat_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.in_combat is False

def test_character_initialises_with_no_current_target():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.current_target is None

def test_character_initialises_with_no_pending_damage_reduction():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.pending_damage_reduction == 0

def test_character_initialises_with_zero_dodge_chance():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.dodge_chance == 0.0

def test_character_initialises_with_has_reckless_strength_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_reckless_strength is False

def test_character_initialises_with_has_measured_casting_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_measured_casting is False

def test_character_initialises_with_has_swift_feet_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_swift_feet is False

def test_character_initialises_with_has_unyielding_tide_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_unyielding_tide is False

def test_character_initialises_with_has_berserking_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_berserking is False

def test_character_initialises_with_has_silver_tongue_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_silver_tongue is False

def test_character_initialises_with_can_ranged_without_weapon_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.can_ranged_without_weapon is False

def test_character_initialises_with_has_petrifying_gaze_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_petrifying_gaze is False

def test_character_initialises_with_has_bull_rush_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_bull_rush is False

def test_character_initialises_with_has_lifesteal_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_lifesteal is False

def test_character_initialises_with_has_iron_hide_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.has_iron_hide is False

def test_character_initialises_with_turn_started_false():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.turn_started is False

def test_attack_light_includes_equipped_melee_weapon_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    sword = Weapon(name="Sword", description="", damage=5)
    sword.use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="light")
    assert target.hp == 85

def test_attack_light_ignores_equipped_ranged_weapon():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    bow = Weapon(name="Bow", description="", damage=4, slot="ranged")
    bow.use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="light")
    assert target.hp == 90

def test_attack_ranged_includes_equipped_ranged_weapon_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    bow = Weapon(name="Bow", description="", damage=4, slot="ranged")
    bow.use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="ranged")
    assert target.hp == 86

def test_attack_ranged_ignores_equipped_melee_weapon():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    sword = Weapon(name="Sword", description="", damage=5)
    sword.use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="ranged")
    assert target.hp == 90

def test_attack_ranged_with_no_ranged_weapon_deals_base_damage_only():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="ranged")
    assert target.hp == 90

def test_attack_heavy_forced_hit_multiplies_damage(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy")
    assert target.hp == 82  # 100 - round(10 * 1.75) = 100 - 18

def test_attack_heavy_forced_hit_includes_equipped_melee_weapon_damage(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    sword = Weapon(name="Sword", description="", damage=6)
    sword.use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy")
    assert target.hp == 72  # 100 - round(16 * 1.75) = 100 - 28

def test_attack_heavy_forced_miss_deals_no_damage(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy")
    assert target.hp == 100

def test_attack_heavy_forced_miss_returns_miss_message(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.0)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero swings a heavy blow at Goblin - but misses!"

def test_attack_heavy_roll_below_miss_chance_misses(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.35)  # below HEAVY_ATTACK_MISS_CHANCE (0.4)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero swings a heavy blow at Goblin - but misses!"

def test_attack_heavy_with_reckless_strength_hits_on_a_roll_that_would_normally_miss(monkeypatch):
    """Reckless Strength halves the heavy miss chance (0.4 -> 0.2 unarmed, see get_miss_chance()) - a 0.3 roll misses
    for everyone else but lands for a Reckless attacker."""
    monkeypatch.setattr("random.random", lambda: 0.3)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_reckless_strength = True
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero attacks Goblin for 18 damage."

def test_attack_heavy_with_reckless_strength_can_still_miss(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)  # below even the halved miss chance
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_reckless_strength = True
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero swings a heavy blow at Goblin - but misses!"

def test_attack_heavy_with_bull_rush_adds_bonus_after_the_multiplier(monkeypatch):
    """Bull Rush's +3 is added to the incoming hit after the heavy multiplier, so it isn't scaled by it."""
    monkeypatch.setattr("random.random", lambda: 0.9)  # avoids the heavy miss roll
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_bull_rush = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target, attack_type="heavy")
    assert target.hp == 79  # 100 - (round(10 * 1.75) + 3)

def test_attack_with_bull_rush_does_not_boost_double_strike_second_hit():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_bull_rush = True
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=100, attack_damage=0)
    attacker.attack(target)
    assert target.hp == 82  # 100 - (10 + 3) - (10 // 2)

def test_attack_with_double_strike_second_hit_ignores_armour():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=100, attack_damage=5, armour=4)
    message = attacker.attack(target)
    assert target.hp == 89  # 100 - (10 - 4) - (10 // 2), armour skipped on the second hit
    assert "Hero strikes again for 5 damage." in message

def test_attack_heavy_forced_hit_returns_message_naming_attacker_and_target(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero attacks Goblin for 18 damage."

def test_attack_heavy_with_double_strike_second_hit_uses_unmultiplied_base_damage(monkeypatch):
    """The second Double Strike hit always uses base_damage // 2 (attack_damage + weapon bonus),
    computed before the heavy multiplier is applied to the first hit - only the first hit is boosted."""
    monkeypatch.setattr("random.random", lambda: 0.9)  # avoids the heavy miss roll
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    attacker.has_double_strike = True
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert target.hp == 77  # 100 - round(10 * 1.75) - (10 // 2) = 100 - 18 - 5
    assert "Hero strikes again for 5 damage." in message

def test_get_inventory_display_returns_empty_message_when_no_items():
    player = Player(name="hero", hp=100)
    assert player.get_inventory_display() == "Your inventory is empty."

def test_get_inventory_display_lists_single_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    assert player.get_inventory_display() == "Bronze Xiphos - blade, 3 DMG"

def test_get_inventory_display_shows_count_for_duplicate_items():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    assert player.get_inventory_display() == "Bronze Xiphos x2 - blade, 3 DMG"

def test_get_inventory_display_lists_multiple_items_on_separate_lines():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Weapon(name="Shield", description="", damage=1))
    assert player.get_inventory_display() == "Bronze Xiphos - blade, 3 DMG\nShield - blade, 1 DMG"

def test_get_inventory_display_marks_equipped_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    sword.use(player)
    assert player.get_inventory_display() == "Bronze Xiphos (equipped) - blade, 3 DMG"

def test_get_inventory_display_marks_duplicate_group_equipped_if_any_instance_equipped():
    player = Player(name="hero", hp=100)
    equipped_sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    spare_sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(equipped_sword)
    player.inventory.add(spare_sword)
    equipped_sword.use(player)
    assert player.get_inventory_display() == "Bronze Xiphos x2 (equipped) - blade, 3 DMG"

def test_get_inventory_display_lists_quest_item_in_separate_section():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    assert player.get_inventory_display() == "Bronze Xiphos - blade, 3 DMG\n\nQuest Items: Dummy Head"

def test_get_inventory_display_with_only_quest_items():
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    assert player.get_inventory_display() == "\nQuest Items: Dummy Head"

def test_get_inventory_display_lists_multiple_quest_items_together():
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    player.inventory.add(QuestItem(name="Mentor's Token", description=""))
    assert player.get_inventory_display() == "\nQuest Items: Dummy Head, Mentor's Token"

def test_get_inventory_display_with_gold_and_no_items_is_not_empty_message():
    player = Player(name="hero", hp=100)
    player.gold = 10
    assert player.get_inventory_display() != "Your inventory is empty."

def test_get_inventory_display_with_only_gold_shows_gold_line():
    player = Player(name="hero", hp=100)
    player.gold = 10
    assert player.get_inventory_display() == "\nGold: 10"

def test_get_inventory_display_appends_gold_line_after_items():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.gold = 5
    assert player.get_inventory_display() == "Bronze Xiphos - blade, 3 DMG\n\nGold: 5"

def test_player_initialises_with_skill_tree():
    player = Player(name="hero", hp=100)
    assert isinstance(player.skill_tree, SkillTree)


def test_display_skills_shows_next_skill_for_each_path():
    player = Player(name="Hero", hp=50, attack_damage=10)
    result = player.get_skills_display()
    assert "Attack: next unlock is Iron Grip - Steadier strikes." in result
    assert "Defence: next unlock is Hardened Skin - Blows land softer." in result
    assert "Abilities: next unlock is Twin Strike - A second blow follows the first, fast and true." in result

def test_display_skills_shows_fully_unlocked_when_path_exhausted():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 5
    for _ in range(5):
        player.skill_tree.invest("attack", player)
    result = player.get_skills_display()
    assert "Attack: fully unlocked" in result

def test_display_skills_shows_available_skill_points():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 2
    result = player.get_skills_display()
    assert "Skill Points available: 2" in result

def test_skill_apply_raises_not_implemented_error():
    skill = Skill(name="Mystery Skill", description="")
    character = Character(name="Hero", hp=100, attack_damage=10)

    try:
        skill.apply(character)
        assert False, "Expected a NotImplementedError but none was raised"
    except NotImplementedError:
        pass

def test_attack_boost_skill_initialises_with_correct_bonus():
    skill = AttackBoostSkill(name="Iron Grip", description="Steadier strikes.", bonus=2)
    assert skill.name == "Iron Grip"
    assert skill.description == "Steadier strikes."
    assert skill.bonus == 2

def test_attack_boost_skill_apply_increases_attack_damage():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = AttackBoostSkill(name="Iron Grip", description="", bonus=3)
    skill.apply(character)
    assert character.attack_damage == 13

def test_attack_boost_skill_apply_returns_message():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = AttackBoostSkill(name="Iron Grip", description="", bonus=3)
    message = skill.apply(character)
    assert message == "Hero gains +3 attack from Iron Grip."

def test_defence_boost_skill_initialises_with_correct_bonus():
    skill = DefenceBoostSkill(name="Hardened Skin", description="Blows land softer.", bonus=2)
    assert skill.name == "Hardened Skin"
    assert skill.description == "Blows land softer."
    assert skill.bonus == 2

def test_defence_boost_skill_apply_increases_armour():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = DefenceBoostSkill(name="Hardened Skin", description="", bonus=3)
    skill.apply(character)
    assert character.armour == 3

def test_defence_boost_skill_apply_returns_message():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = DefenceBoostSkill(name="Hardened Skin", description="", bonus=3)
    message = skill.apply(character)
    assert message == "Hero gains +3 armour from Hardened Skin."

def test_skill_path_initialises_with_zero_unlocked_count():
    path = SkillPath(name="Defence", skills=[DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)])
    assert path.unlocked_count == 0

def test_skill_path_next_skill_returns_first_skill_when_none_unlocked():
    skill = DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)
    path = SkillPath(name="Defence", skills=[skill])
    assert path.next_skill is skill

def test_skill_path_unlock_next_increments_unlocked_count():
    path = SkillPath(name="Defence", skills=[DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)])
    character = Character(name="Hero", hp=100, attack_damage=10)
    path.unlock_next(character)
    assert path.unlocked_count == 1

def test_skill_path_unlock_next_applies_skill_to_character():
    path = SkillPath(name="Defence", skills=[DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)])
    character = Character(name="Hero", hp=100, attack_damage=10)
    path.unlock_next(character)
    assert character.armour == 2

def test_skill_path_unlock_next_returns_skills_apply_message():
    path = SkillPath(name="Defence", skills=[DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)])
    character = Character(name="Hero", hp=100, attack_damage=10)
    message = path.unlock_next(character)
    assert message == "Hero gains +2 armour from Hardened Skin."

def test_skill_path_unlock_next_raises_error_when_fully_unlocked():
    path = SkillPath(name="Defence", skills=[DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)])
    character = Character(name="Hero", hp=100, attack_damage=10)
    path.unlock_next(character)

    try:
        path.unlock_next(character)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_skill_path_next_skill_returns_none_when_fully_unlocked():
    path = SkillPath(name="Defence", skills=[DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)])
    character = Character(name="Hero", hp=100, attack_damage=10)
    path.unlock_next(character)
    assert path.next_skill is None

def test_skill_path_skills_property_returns_copy():
    skill = DefenceBoostSkill(name="Hardened Skin", description="", bonus=2)
    path = SkillPath(name="Defence", skills=[skill])
    path.skills.append(DefenceBoostSkill(name="Aegis Ward", description="", bonus=4))
    assert path.skills == [skill]

def test_skill_tree_initialises_with_zero_skill_points():
    skill_tree = SkillTree()
    assert skill_tree.skill_points == 0

def test_skill_tree_has_attack_and_defence_paths():
    skill_tree = SkillTree()
    assert "attack" in skill_tree.paths
    assert "defence" in skill_tree.paths

def test_skill_tree_invest_raises_error_when_no_skill_points():
    skill_tree = SkillTree()
    character = Character(name="Hero", hp=100, attack_damage=10)

    try:
        skill_tree.invest("defence", character)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_skill_tree_invest_raises_error_for_invalid_path_name():
    skill_tree = SkillTree()
    skill_tree.skill_points = 1
    character = Character(name="Hero", hp=100, attack_damage=10)

    try:
        skill_tree.invest("nonexistent", character)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

def test_skill_tree_invest_decrements_skill_points():
    skill_tree = SkillTree()
    skill_tree.skill_points = 1
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill_tree.invest("defence", character)
    assert skill_tree.skill_points == 0

def test_skill_tree_invest_applies_skill_from_path():
    skill_tree = SkillTree()
    skill_tree.skill_points = 1
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill_tree.invest("defence", character)
    assert character.armour == 2

def test_double_strike_skill_apply_returns_message():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = DoubleStrikeSkill(name="Twin Blades", description="")
    message = skill.apply(character)
    assert message == "Hero learns to strike twice in quick succession."

def test_double_strike_skill_apply_sets_has_double_strike_flag():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = DoubleStrikeSkill(name="Twin Blades", description="")
    skill.apply(character)
    assert character.has_double_strike is True

def test_double_strike_skill_enables_second_hit_on_attack():
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    skill = DoubleStrikeSkill(name="Twin Blades", description="")
    skill.apply(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target)
    assert target.hp == 85
    assert "Hero strikes again for 5 damage." in message

def test_last_stand_skill_apply_returns_message():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = LastStandSkill(name="Unbreakable", description="")
    message = skill.apply(character)
    assert message == "Hero will not fall easily - death itself will have to try twice."

def test_last_stand_skill_apply_sets_has_last_stand_flag():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = LastStandSkill(name="Unbreakable", description="")
    skill.apply(character)
    assert character.has_last_stand is True

def test_last_stand_skill_enables_surviving_lethal_hit():
    character = Character(name="Hero", hp=30, attack_damage=5)
    skill = LastStandSkill(name="Unbreakable", description="")
    skill.apply(character)
    damage_dealt, message = character.take_damage(50)
    assert character.hp == 1

def test_thorns_skill_apply_returns_message():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = ThornsSkill(name="Retribution", description="")
    message = skill.apply(character)
    assert message == "Hero learns to turn an enemy's own strength against them."

def test_thorns_skill_apply_sets_has_thorns_flag():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = ThornsSkill(name="Retribution", description="")
    skill.apply(character)
    assert character.has_thorns is True

def test_skill_tree_attack_path_has_five_skills_with_rising_bonuses():
    skill_tree = SkillTree()
    bonuses = [skill.bonus for skill in skill_tree.paths["attack"].skills]
    assert bonuses == [2, 3, 4, 5, 6]

def test_skill_tree_defence_path_has_five_skills_with_rising_bonuses():
    skill_tree = SkillTree()
    bonuses = [skill.bonus for skill in skill_tree.paths["defence"].skills]
    assert bonuses == [2, 3, 4, 5, 6]

def test_skill_tree_fully_investing_attack_path_adds_twenty_attack():
    skill_tree = SkillTree()
    skill_tree.skill_points = 5
    character = Character(name="Hero", hp=100, attack_damage=10)
    for _ in range(5):
        skill_tree.invest("attack", character)
    assert character.attack_damage == 30

def test_skill_tree_fully_investing_defence_path_adds_twenty_armour():
    skill_tree = SkillTree()
    skill_tree.skill_points = 5
    character = Character(name="Hero", hp=100, attack_damage=10)
    for _ in range(5):
        skill_tree.invest("defence", character)
    assert character.armour == 20

def test_skill_tree_has_abilities_path_with_four_skills():
    skill_tree = SkillTree()
    assert len(skill_tree.paths["abilities"].skills) == 4

def test_skill_tree_invest_abilities_path_applies_double_strike_skill_first():
    skill_tree = SkillTree()
    skill_tree.skill_points = 1
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill_tree.invest("abilities", character)
    assert character.has_double_strike is True

def test_skill_tree_invest_abilities_path_applies_dodge_skill_fourth():
    skill_tree = SkillTree()
    skill_tree.skill_points = 4
    character = Character(name="Hero", hp=100, attack_damage=10)
    for _ in range(4):
        skill_tree.invest("abilities", character)
    assert character.dodge_chance == 0.35

def test_dodge_skill_initialises_with_chance():
    skill = DodgeSkill(name="Nimble Grace", description="A hero's step.", chance=0.35)
    assert skill.chance == 0.35

def test_dodge_skill_apply_increases_dodge_chance():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = DodgeSkill(name="Nimble Grace", description="", chance=0.35)
    skill.apply(character)
    assert character.dodge_chance == 0.35

def test_dodge_skill_apply_stacks_with_existing_dodge_chance():
    character = Character(name="Hero", hp=100, attack_damage=10)
    character.dodge_chance = 0.25
    skill = DodgeSkill(name="Nimble Grace", description="", chance=0.25)
    skill.apply(character)
    assert character.dodge_chance == 0.5

def test_dodge_skill_apply_returns_message():
    character = Character(name="Hero", hp=100, attack_damage=10)
    skill = DodgeSkill(name="Nimble Grace", description="", chance=0.35)
    message = skill.apply(character)
    assert message == "Hero learns to slip aside from incoming blows."

def test_enemy_initialises_with_has_lifesteal_false_by_default():
    enemy = Enemy(name="Goblin", hp=10)
    assert enemy.has_lifesteal is False

def test_enemy_initialises_with_has_lifesteal():
    enemy = Enemy(name="Lamia", hp=10, has_lifesteal=True)
    assert enemy.has_lifesteal is True

def test_enemy_with_lifesteal_heals_when_it_attacks():
    enemy = Enemy(name="Lamia", hp=30, attack_damage=10, has_lifesteal=True)
    enemy.hp = 10
    target = Character(name="Hero", hp=100, attack_damage=0)
    enemy.attack(target)
    assert enemy.hp == 15

def test_enemy_initialises_with_has_petrifying_gaze_false_by_default():
    enemy = Enemy(name="Goblin", hp=10)
    assert enemy.has_petrifying_gaze is False

def test_enemy_initialises_with_has_petrifying_gaze():
    enemy = Enemy(name="Medusa (Awakened)", hp=10, has_petrifying_gaze=True)
    assert enemy.has_petrifying_gaze is True

def test_enemy_initialises_with_no_next_phase_factory_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.next_phase_factory is None

def test_enemy_initialises_with_next_phase_factory():
    factory = lambda: Enemy(name="Goblin Chief", hp=25, attack_damage=6)
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, next_phase_factory=factory)
    assert enemy.next_phase_factory is factory

def test_enemy_initialises_with_no_next_wave_factories_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.next_wave_factories is None

def test_enemy_initialises_with_next_wave_factories():
    factories = [lambda: Enemy(name="Skeleton", hp=5, attack_damage=2)]
    enemy = Enemy(name="Necromancer", hp=15, attack_damage=4, next_wave_factories=factories)
    assert enemy.next_wave_factories is factories

def test_enemy_initialises_with_no_wave_gate_factory_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.wave_gate_factory is None

def test_enemy_initialises_with_wave_gate_factory():
    factory = lambda: Enemy(name="Necromancer (Awakened)", hp=40, attack_damage=20)
    enemy = Enemy(name="Skeleton", hp=5, attack_damage=2, wave_gate_factory=factory)
    assert enemy.wave_gate_factory is factory

def test_enemy_initialises_with_has_been_fled_from_false():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.has_been_fled_from is False

def test_enemy_initialises_with_no_experience_reward_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.experience_reward == 0

def test_enemy_initialises_with_no_gold_reward_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.gold_reward == 0

def test_enemy_initialises_with_experience_reward():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, experience_reward=10)
    assert enemy.experience_reward == 10

def test_enemy_initialises_with_gold_reward():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, gold_reward=5)
    assert enemy.gold_reward == 5

def test_enemy_initialises_with_default_aggression_weight():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.aggression_weight == 1.0

def test_enemy_initialises_with_default_caution_weight():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.caution_weight == 1.0

def test_enemy_initialises_with_default_randomness_weight():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.randomness_weight == 0.3

def test_enemy_initialises_with_custom_aggression_weight():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, aggression_weight=2.5)
    assert enemy.aggression_weight == 2.5

def test_enemy_initialises_with_custom_caution_weight():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, caution_weight=1.8)
    assert enemy.caution_weight == 1.8

def test_enemy_initialises_with_custom_randomness_weight():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, randomness_weight=0.6)
    assert enemy.randomness_weight == 0.6

def test_enemy_initialises_with_no_brace_amount_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.brace_amount == 0

def test_enemy_initialises_with_custom_brace_amount():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, brace_amount=3)
    assert enemy.brace_amount == 3

def test_enemy_initialises_with_no_heal_amount_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.heal_amount == 0

def test_enemy_initialises_with_custom_heal_amount():
    enemy = Enemy(name="Priest", hp=15, attack_damage=4, heal_amount=5)
    assert enemy.heal_amount == 5

def test_enemy_initialises_with_respawns_false_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.respawns is False

def test_enemy_initialises_with_respawns_true():
    enemy = Enemy(name="Practice Enemy", hp=15, attack_damage=4, respawns=True)
    assert enemy.respawns is True

def test_level_up_increases_max_hp_by_hp_per_level():
    player = Player(name="Hero", hp=20)
    player.level_up()
    assert player.max_hp == 20 + HP_PER_LEVEL

def test_level_up_raises_current_hp_by_the_same_amount_rather_than_fully_healing():
    """Levelling up mid-fight must not hand out a free full restore - current HP only rises by HP_PER_LEVEL."""
    player = Player(name="Hero", hp=20)
    player.hp = 5
    player.level_up()
    assert player.hp == 5 + HP_PER_LEVEL

def test_player_initialises_with_no_visited_rooms():
    player = Player(name="Hero", hp=20)
    assert player.visited_rooms == set()

def test_player_initialises_with_auto_map_false():
    player = Player(name="Hero", hp=20)
    assert player.auto_map is False

def test_get_inventory_display_shows_armour_durability():
    player = Player(name="hero", hp=100)
    helm = Armour(name="Weathered Helm", description="", defence=1, slot="helmet", max_durability=5)
    helm.durability = 3
    player.inventory.add(helm)
    assert player.get_inventory_display() == "Weathered Helm - helmet, light, 1 DEF, 3/5 durability"

def test_get_inventory_display_marks_equipped_armour_before_its_durability():
    player = Player(name="hero", hp=100)
    plate = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=8)
    player.inventory.add(plate)
    plate.use(player)
    assert player.get_inventory_display() == "Bronze Breastplate (equipped) - body, light, 2 DEF, 8/8 durability"

def test_get_inventory_display_lists_same_named_armour_pieces_separately():
    """Two pieces can differ in durability, so armour is never grouped into a 'x2' line the way weapons are."""
    player = Player(name="hero", hp=100)
    worn = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=8)
    worn.durability = 2
    fresh = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=8)
    player.inventory.add(worn)
    player.inventory.add(fresh)
    assert player.get_inventory_display() == "Bronze Breastplate - body, light, 2 DEF, 2/8 durability\nBronze Breastplate - body, light, 2 DEF, 8/8 durability"

def test_get_inventory_display_keeps_weapons_and_armour_in_inventory_order():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Armour(name="Wooden Shield", description="", defence=1, max_durability=6))
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    assert player.get_inventory_display() == "Bronze Xiphos x2 - blade, 3 DMG\nWooden Shield - body, light, 1 DEF, 6/6 durability"

def test_skill_tree_stat_skill_descriptions_state_their_bonus():
    skill_tree = SkillTree()
    attack = [skill.description for skill in skill_tree.paths["attack"].skills]
    defence = [skill.description for skill in skill_tree.paths["defence"].skills]
    assert all(desc.endswith(f"(+{bonus} ATK)") for desc, bonus in zip(attack, [2, 3, 4, 5, 6]))
    assert all(desc.endswith(f"(+{bonus} DEF)") for desc, bonus in zip(defence, [2, 3, 4, 5, 6]))

def test_player_initialises_with_no_seen_hints():
    player = Player(name="Hero", hp=20)
    assert player.seen_hints == set()

def test_ally_initialises_with_empty_hint_traded_by_default():
    ally = Ally(name="Chiron")
    assert ally.hint_traded == ""

def test_ally_talk_returns_hint_traded_once_trade_completed():
    player = Player(name="hero", hp=10)
    ally = Ally(name="Athena", hint="Bring me the bow.", hint_complete="Say 'trade'.", hint_traded="Wear it well.", required_items=["Bow"])
    ally.trade_completed = True
    assert ally.talk(player) == "Wear it well."

def test_ally_talk_prefers_hint_complete_over_hint_traded_before_the_trade():
    """hint_traded is only for after the trade - holding the required items still gets the 'say trade' line."""
    player = Player(name="hero", hp=10)
    player.inventory.add(Weapon(name="Bow", description="", damage=1))
    ally = Ally(name="Athena", hint="Bring me the bow.", hint_complete="Say 'trade'.", hint_traded="Wear it well.", required_items=["Bow"])
    assert ally.talk(player) == "Say 'trade'."

def _armour_piece(slot: str, weight: str, defence: int = 1) -> Armour:
    """Test helper - an armour piece of the given slot and weight."""
    return Armour(name=f"{weight} {slot}", description="", defence=defence, slot=slot, weight=weight)

def test_character_initialises_with_no_equipped_shield():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_shield is None

def test_armour_weight_penalty_is_zero_with_no_armour():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.armour_weight_penalty() == 0.0

def test_armour_weight_penalty_sums_helmet_body_and_shield():
    character = Character(name="Hero", hp=30, attack_damage=5)
    _armour_piece("helmet", "light").use(character)
    _armour_piece("body", "medium").use(character)
    _armour_piece("shield", "heavy").use(character)
    expected = ARMOUR_WEIGHT_MISS_PENALTY["light"] + ARMOUR_WEIGHT_MISS_PENALTY["medium"] + ARMOUR_WEIGHT_MISS_PENALTY["heavy"]
    assert abs(character.armour_weight_penalty() - expected) < 1e-9

def test_armour_weight_penalty_still_counts_a_broken_piece():
    """A broken piece is still being worn, so its weight still counts."""
    character = Character(name="Hero", hp=30, attack_damage=5)
    plate = _armour_piece("body", "heavy")
    plate.use(character)
    plate.durability = 0
    assert character.armour_weight_penalty() == ARMOUR_WEIGHT_MISS_PENALTY["heavy"]

def test_get_miss_chance_light_is_zero_when_unarmoured():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.get_miss_chance("light") == 0.0

def test_get_miss_chance_light_is_only_the_armour_weight_penalty():
    character = Character(name="Hero", hp=30, attack_damage=5)
    _armour_piece("body", "medium").use(character)
    assert character.get_miss_chance("light") == ARMOUR_WEIGHT_MISS_PENALTY["medium"]

def test_get_miss_chance_ranged_matches_light():
    character = Character(name="Hero", hp=30, attack_damage=5)
    _armour_piece("body", "heavy").use(character)
    assert character.get_miss_chance("ranged") == character.get_miss_chance("light")

def test_get_miss_chance_heavy_unarmed_is_the_base_chance():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.get_miss_chance("heavy") == HEAVY_ATTACK_MISS_CHANCE

def test_get_miss_chance_heavy_with_a_blade_is_lowered():
    character = Character(name="Hero", hp=30, attack_damage=5)
    Weapon(name="Sword", description="", damage=3, weapon_class="blade").use(character)
    assert abs(character.get_miss_chance("heavy") - (HEAVY_ATTACK_MISS_CHANCE + BLADE_HEAVY_MISS_MODIFIER)) < 1e-9

def test_get_miss_chance_heavy_with_a_heavy_weapon_keeps_the_base_chance():
    character = Character(name="Hero", hp=30, attack_damage=5)
    Weapon(name="Axe", description="", damage=5, weapon_class="heavy").use(character)
    assert character.get_miss_chance("heavy") == HEAVY_ATTACK_MISS_CHANCE

def test_get_miss_chance_heavy_with_a_piercing_weapon_keeps_the_base_chance():
    character = Character(name="Hero", hp=30, attack_damage=5)
    Weapon(name="Spear", description="", damage=5, weapon_class="piercing").use(character)
    assert character.get_miss_chance("heavy") == HEAVY_ATTACK_MISS_CHANCE

def test_get_miss_chance_heavy_adds_the_armour_weight_penalty():
    character = Character(name="Hero", hp=30, attack_damage=5)
    _armour_piece("body", "heavy").use(character)
    assert abs(character.get_miss_chance("heavy") - (HEAVY_ATTACK_MISS_CHANCE + ARMOUR_WEIGHT_MISS_PENALTY["heavy"])) < 1e-9

def test_get_miss_chance_reckless_strength_halves_heavy_after_blade_and_armour():
    """Halving happens last, after the blade modifier and the armour penalty are both applied."""
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_reckless_strength = True
    Weapon(name="Sword", description="", damage=3, weapon_class="blade").use(character)
    _armour_piece("body", "medium").use(character)
    expected = (HEAVY_ATTACK_MISS_CHANCE + BLADE_HEAVY_MISS_MODIFIER + ARMOUR_WEIGHT_MISS_PENALTY["medium"]) / 2
    assert abs(character.get_miss_chance("heavy") - expected) < 1e-9

def test_get_miss_chance_reckless_strength_does_not_halve_light():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_reckless_strength = True
    _armour_piece("body", "medium").use(character)
    assert character.get_miss_chance("light") == ARMOUR_WEIGHT_MISS_PENALTY["medium"]

def test_attack_light_by_an_armoured_attacker_can_miss(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.01)  # below the medium-armour penalty
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    _armour_piece("body", "medium").use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin - but misses!"
    assert target.hp == 100

def test_attack_light_by_an_unarmoured_attacker_makes_no_miss_roll(monkeypatch):
    """Only the target's own dodge roll in take_damage() draws a random number - the attack never rolls to miss."""
    calls = []
    monkeypatch.setattr("random.random", lambda: calls.append(1) or 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=10)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    assert len(calls) == 1

def test_attack_heavy_with_a_blade_hits_on_a_roll_the_base_chance_would_miss(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.35)  # misses at 0.4, lands at 0.3
    attacker = Character(name="Hero", hp=30, attack_damage=7)
    Weapon(name="Sword", description="", damage=3, weapon_class="blade").use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero attacks Goblin for 18 damage."  # round(10 * 1.75)

def test_attack_heavy_with_a_heavy_weapon_uses_the_heavy_weapon_multiplier(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Axe", description="", damage=6, weapon_class="heavy").use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy")
    assert target.hp == 80  # 100 - (4 + 6) * 2.0

def test_attack_light_with_a_heavy_weapon_has_no_multiplier():
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Axe", description="", damage=6, weapon_class="heavy").use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    assert target.hp == 90

def test_attack_with_a_piercing_weapon_ignores_some_of_the_target_armour():
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Spear", description="", damage=6, weapon_class="piercing", armour_pierce=2).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5, armour=3)
    attacker.attack(target)
    assert target.hp == 91  # 10 - (3 - 2)

def test_attack_armour_pierce_beyond_the_target_armour_adds_no_extra_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Spear", description="", damage=6, weapon_class="piercing", armour_pierce=5).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5, armour=2)
    attacker.attack(target)
    assert target.hp == 90

def test_take_damage_armour_pierce_reduces_the_armour_applied():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=4)
    dealt, _ = character.take_damage(10, armour_pierce=3)
    assert dealt == 9

def test_attack_with_a_lifesteal_weapon_heals_the_attacker():
    attacker = Character(name="Hero", hp=10, attack_damage=2)
    attacker.max_hp = 30
    Weapon(name="Fang", description="", damage=2, weapon_class="piercing", lifesteal=True).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target)
    assert attacker.hp == 12  # 4 dealt // 2, under the cap
    assert "Hero drains 2 HP from the wound." in message

def test_attack_lifesteal_only_comes_from_the_weapon_actually_used():
    """A lifesteal bow in the ranged slot does nothing for a light (melee) attack."""
    attacker = Character(name="Hero", hp=10, attack_damage=4)
    attacker.max_hp = 30
    Weapon(name="Leech Bow", description="", damage=4, slot="ranged", weapon_class="ranged", lifesteal=True).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    assert attacker.hp == 10

def _cleaver(attacker: Character) -> Weapon:
    """Test helper - equip a Labrys-like heavy cleave weapon (6 damage) on attacker."""
    axe = Weapon(name="Axe", description="", damage=6, weapon_class="heavy", cleave=True)
    axe.use(attacker)
    return axe

def test_attack_heavy_with_cleave_hits_a_second_enemy_for_half_the_swing(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    second = Enemy(name="Orc", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy", others=[target, second])
    assert second.hp == 90  # (4 + 6) * 2.0 = 20, halved
    assert "The swing carries on into Orc for 10 damage." in message

def test_attack_light_with_a_cleave_weapon_does_not_cleave():
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    second = Enemy(name="Orc", hp=100, attack_damage=5)
    attacker.attack(target, others=[target, second])
    assert second.hp == 100

def test_attack_heavy_without_a_cleave_weapon_does_not_cleave(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Maul", description="", damage=6, weapon_class="heavy").use(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    second = Enemy(name="Orc", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy", others=[target, second])
    assert second.hp == 100

def test_attack_heavy_cleave_with_no_others_only_hits_the_target(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy")
    assert message == "Hero attacks Goblin for 20 damage."

def test_attack_heavy_cleave_skips_dead_and_respawning_combatants(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    dead = Enemy(name="Corpse", hp=0, attack_damage=5)
    dummy = Enemy(name="Dummy", hp=100, attack_damage=0, respawns=True)
    living = Enemy(name="Orc", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy", others=[dead, dummy, target, living])
    assert dummy.hp == 100
    assert living.hp == 90

def test_attack_heavy_cleave_still_carries_on_when_the_target_dies(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=5, attack_damage=5)
    second = Enemy(name="Orc", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy", others=[target, second])
    assert target.hp == 0
    assert second.hp == 90

def test_attack_heavy_cleave_reports_a_kill_on_the_second_enemy(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    second = Enemy(name="Orc", hp=4, attack_damage=5)
    message = attacker.attack(target, attack_type="heavy", others=[target, second])
    assert second.hp == 0
    assert second.on_death() in message

def test_attack_heavy_cleave_does_not_include_bull_rush(monkeypatch):
    """Cleave takes half the swing's damage - the heavy-multiplied hit before Bull Rush's flat +3."""
    monkeypatch.setattr("random.random", lambda: 0.9)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    attacker.has_bull_rush = True
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    second = Enemy(name="Orc", hp=50, attack_damage=5)
    attacker.attack(target, attack_type="heavy", others=[target, second])
    assert target.hp == 77  # 20 + 3
    assert second.hp == 40  # 20 // 2, no Bull Rush

def test_attack_heavy_miss_with_a_cleave_weapon_hits_nobody(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    _cleaver(attacker)
    target = Enemy(name="Goblin", hp=100, attack_damage=5)
    second = Enemy(name="Orc", hp=100, attack_damage=5)
    attacker.attack(target, attack_type="heavy", others=[target, second])
    assert target.hp == 100
    assert second.hp == 100

def test_attack_with_a_poison_weapon_poisons_the_target_on_a_low_roll(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Kiss", description="", damage=3, poison_chance=0.15).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    poison = next(e for e in target.active_effects if e.name == "Poison")
    assert poison.amount == WEAPON_POISON_AMOUNT
    assert poison.duration == WEAPON_POISON_DURATION

def test_attack_with_a_poison_weapon_does_not_poison_on_a_high_roll(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Kiss", description="", damage=3, poison_chance=0.15).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    assert target.active_effects == []

def test_attack_with_a_poison_weapon_never_poisons_a_killed_target(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.1)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    Weapon(name="Kiss", description="", damage=3, poison_chance=0.15).use(attacker)
    target = Character(name="Goblin", hp=5, attack_damage=5)
    attacker.attack(target)
    assert target.active_effects == []

def test_attack_petrifying_gaze_and_weapon_poison_roll_separately(monkeypatch):
    """Both succeed on the same hit, so the second application prolongs the first (durations add)."""
    monkeypatch.setattr("random.random", lambda: 0.1)
    attacker = Character(name="Hero", hp=30, attack_damage=4)
    attacker.has_petrifying_gaze = True
    Weapon(name="Kiss", description="", damage=3, poison_chance=0.15).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    attacker.attack(target)
    poison = next(e for e in target.active_effects if e.name == "Poison")
    assert poison.duration == 3 + WEAPON_POISON_DURATION

def test_take_damage_degrades_an_equipped_shield():
    character = Character(name="Hero", hp=100, attack_damage=5)
    shield = _armour_piece("shield", "light", defence=2)
    shield.use(character)
    character.take_damage(5)
    assert shield.durability == shield.max_durability - 1

def test_take_damage_breaking_a_shield_backs_out_its_defence():
    character = Character(name="Hero", hp=100, attack_damage=5, armour=1)
    shield = _armour_piece("shield", "light", defence=2)
    shield.use(character)
    shield.durability = 1
    character.take_damage(5)
    assert character.armour == 1

def test_get_stats_shows_miss_chance_for_each_attack_type():
    player = Player(name="Hero", hp=20)
    _armour_piece("body", "medium").use(player)
    stats = player.get_stats()
    assert "Miss chance: 5% light / 45% heavy / 5% ranged" in stats

def test_character_initialises_base_armour_from_the_armour_argument():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=2)
    assert character.base_armour == 2

def test_armour_is_base_armour_plus_every_worn_piece():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=1)
    _armour_piece("helmet", "light", defence=1).use(character)
    _armour_piece("body", "light", defence=2).use(character)
    _armour_piece("shield", "light", defence=3).use(character)
    assert character.armour == 7

def test_armour_leaves_out_a_broken_worn_piece():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=1)
    plate = _armour_piece("body", "light", defence=2)
    plate.use(character)
    plate.durability = 0
    assert character.armour == 1

def test_armour_keeps_a_broken_worn_piece_with_unyielding_tide():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=1)
    character.has_unyielding_tide = True
    plate = _armour_piece("body", "light", defence=2)
    plate.use(character)
    plate.durability = 0
    assert character.armour == 3

def test_setting_armour_changes_base_armour_and_leaves_worn_pieces_alone():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=1)
    plate = _armour_piece("body", "light", defence=2)
    plate.use(character)
    character.armour = 10
    assert character.base_armour == 8
    assert plate.defence == 2

def test_defence_boost_skill_with_armour_worn_raises_base_armour():
    """DefenceBoostSkill still does 'armour += bonus' - the setter routes that into base_armour."""
    character = Character(name="Hero", hp=30, attack_damage=5, armour=1)
    _armour_piece("body", "light", defence=2).use(character)
    DefenceBoostSkill("Hardened Skin", "", bonus=2).apply(character)
    assert character.base_armour == 3
    assert character.armour == 5

def test_attack_with_a_lifesteal_weapon_caps_the_heal():
    attacker = Character(name="Hero", hp=10, attack_damage=4)
    attacker.max_hp = 30
    Weapon(name="Fang", description="", damage=4, weapon_class="piercing", lifesteal=True).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target)
    assert attacker.hp == 10 + WEAPON_LIFESTEAL_CAP  # 8 dealt // 2 = 4, capped
    assert f"Hero drains {WEAPON_LIFESTEAL_CAP} HP from the wound." in message

def test_attack_innate_lifesteal_is_not_capped():
    attacker = Character(name="Lamia", hp=10, attack_damage=10)
    attacker.max_hp = 30
    attacker.has_lifesteal = True
    target = Character(name="Hero", hp=100, attack_damage=5)
    attacker.attack(target)
    assert attacker.hp == 15  # 10 dealt // 2, more than WEAPON_LIFESTEAL_CAP

def test_attack_innate_and_weapon_lifesteal_do_not_stack():
    """Both sources heal once, uncapped - the innate heal wins, and the weapon adds nothing on top."""
    attacker = Character(name="Hero", hp=10, attack_damage=6)
    attacker.max_hp = 30
    attacker.has_lifesteal = True
    Weapon(name="Fang", description="", damage=4, weapon_class="piercing", lifesteal=True).use(attacker)
    target = Character(name="Goblin", hp=100, attack_damage=5)
    message = attacker.attack(target)
    assert attacker.hp == 15  # 10 dealt // 2, once
    assert message.count("drains") == 1

def test_enemy_initialises_with_no_defeat_effect_by_default():
    enemy = Enemy(name="Goblin", hp=10)
    assert enemy.defeat_effect is None

def test_enemy_initialises_with_a_custom_defeat_effect():
    effect = lambda player: "done"
    enemy = Enemy(name="Goblin", hp=10, defeat_effect=effect)
    assert enemy.defeat_effect is effect

def test_enemy_initialises_with_no_duel_link():
    enemy = Enemy(name="Goblin", hp=10)
    assert enemy.duel_companion is None
    assert enemy.duel_return_hp is None

def test_player_starts_with_the_starting_experience_threshold():
    player = Player(name="Hero", hp=20)
    assert player.experience_to_next_level == STARTING_EXPERIENCE_TO_NEXT_LEVEL

def _companion(**kwargs) -> Companion:
    """Test helper - a plain companion with a throwaway home room."""
    return Companion(name="Imp", hp=20, home_room=Room("Camp"), attack_damage=5, **kwargs)

def _duel_opponent() -> Enemy:
    """Test helper - a stand-in duel_enemy_factory."""
    return Enemy(name="Imp", hp=30)

def test_companion_initialises_at_level_one_on_the_player_curve():
    companion = _companion()
    assert companion.level == 1
    assert companion.experience == 0
    assert companion.experience_to_next_level == STARTING_EXPERIENCE_TO_NEXT_LEVEL

def test_companion_initialises_with_no_duel_by_default():
    companion = _companion()
    assert companion.duel_enemy_factory is None
    assert companion.duel_won is False

def test_companion_without_a_duel_does_not_require_one():
    companion = _companion()
    assert companion.requires_duel is False

def test_companion_with_a_duel_requires_one():
    companion = _companion(duel_enemy_factory=_duel_opponent)
    assert companion.requires_duel is True

def test_companion_with_a_won_duel_no_longer_requires_one():
    companion = _companion(duel_enemy_factory=_duel_opponent)
    companion.duel_won = True
    assert companion.requires_duel is False

def test_companion_talk_before_the_duel_returns_the_hint():
    companion = _companion(hint="Fight me.", hint_recruitable="Recruit me.", duel_enemy_factory=_duel_opponent)
    assert companion.talk(Player(name="Hero", hp=20)) == "Fight me."

def test_companion_talk_after_the_duel_returns_the_recruitable_line():
    companion = _companion(hint="Fight me.", hint_recruitable="Recruit me.", duel_enemy_factory=_duel_opponent)
    companion.duel_won = True
    assert companion.talk(Player(name="Hero", hp=20)) == "Recruit me."

def test_companion_talk_with_no_duel_returns_the_recruitable_line():
    companion = _companion(hint="Hello.", hint_recruitable="Recruit me.")
    assert companion.talk(Player(name="Hero", hp=20)) == "Recruit me."

def test_companion_talk_with_no_recruitable_line_falls_back_to_the_hint():
    companion = _companion(hint="Hello.")
    assert companion.talk(Player(name="Hero", hp=20)) == "Hello."

def test_companion_talk_with_no_lines_has_nothing_to_say():
    companion = _companion()
    assert companion.talk(Player(name="Hero", hp=20)) == "Imp has nothing to say."

def test_companion_gain_experience_below_the_threshold_does_not_level_up():
    companion = _companion()
    message = companion.gain_experience(10)
    assert companion.level == 1
    assert companion.experience == 10
    assert message == "Imp gains 10 experience."

def test_companion_gain_experience_at_the_threshold_levels_up():
    companion = _companion()
    message = companion.gain_experience(STARTING_EXPERIENCE_TO_NEXT_LEVEL + 3)
    assert companion.level == 2
    assert companion.experience == 3
    assert companion.max_hp == 20 + COMPANION_HP_PER_LEVEL
    assert companion.hp == 20 + COMPANION_HP_PER_LEVEL
    assert companion.attack_damage == 5 + COMPANION_ATTACK_PER_LEVEL
    assert companion.experience_to_next_level == int(STARTING_EXPERIENCE_TO_NEXT_LEVEL * 1.5)
    assert f"Imp reaches level 2! (+{COMPANION_HP_PER_LEVEL} max HP, +{COMPANION_ATTACK_PER_LEVEL} ATK)" in message

def test_companion_gain_experience_can_level_up_more_than_once():
    """Unlike Player.gain_experience(), a companion keeps levelling while the XP covers the next threshold too."""
    companion = _companion()
    companion.gain_experience(STARTING_EXPERIENCE_TO_NEXT_LEVEL + int(STARTING_EXPERIENCE_TO_NEXT_LEVEL * 1.5))
    assert companion.level == 3
    assert companion.experience == 0

def test_companion_levelling_up_while_downed_does_not_revive_them():
    companion = _companion()
    companion.hp = 0
    companion.gain_experience(STARTING_EXPERIENCE_TO_NEXT_LEVEL)
    assert companion.level == 2
    assert companion.hp == 0
    assert companion.max_hp == 20 + COMPANION_HP_PER_LEVEL

def test_companion_restore_level_replays_each_level_up():
    companion = _companion()
    companion.restore_level(3, 12)
    assert companion.level == 3
    assert companion.experience == 12
    assert companion.max_hp == 20 + 2 * COMPANION_HP_PER_LEVEL
    assert companion.attack_damage == 5 + 2 * COMPANION_ATTACK_PER_LEVEL
    assert companion.experience_to_next_level == int(int(STARTING_EXPERIENCE_TO_NEXT_LEVEL * 1.5) * 1.5)

def test_companion_restore_level_one_changes_no_stats():
    companion = _companion()
    companion.restore_level(1, 7)
    assert companion.level == 1
    assert companion.max_hp == 20
    assert companion.experience == 7

def test_player_initialises_with_no_ancestry_keys():
    player = Player(name="Hero", hp=20)
    assert player.ancestry_key is None
    assert player.secondary_ancestry_key is None

def test_player_initialises_with_no_seen_lines():
    player = Player(name="Hero", hp=20)
    assert player.seen_lines == set()

def test_enemy_initialises_with_no_ancestry_lines_by_default():
    assert Enemy(name="Goblin", hp=10).ancestry_lines == {}

def test_enemy_initialises_with_custom_ancestry_lines():
    enemy = Enemy(name="Minotaur", hp=10, ancestry_lines={"minotaur": "Kin."})
    assert enemy.ancestry_lines == {"minotaur": "Kin."}

def test_ally_initialises_with_no_ancestry_lines_by_default():
    assert Ally(name="Sage").ancestry_lines == {}

def test_ally_initialises_with_custom_ancestry_lines():
    ally = Ally(name="Athena", ancestry_lines={"athena": "Mine, then."})
    assert ally.ancestry_lines == {"athena": "Mine, then."}

def test_companion_initialises_with_no_ancestry_or_rival_lines_by_default():
    companion = _companion()
    assert companion.ancestry_lines == {}
    assert companion.rival_lines == {}

def test_companion_initialises_with_custom_rival_lines():
    companion = _companion(rival_lines={"Shade of Hector": "Hector."})
    assert companion.rival_lines == {"Shade of Hector": "Hector."}
