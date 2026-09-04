from dungeon_crawler.characters import Character, Player, Enemy, Ally, Companion, Skill, AttackBoostSkill, DefenceBoostSkill, DoubleStrikeSkill, LastStandSkill, ThornsSkill, DodgeSkill, SkillPath, SkillTree
from dungeon_crawler.items import Weapon, Inventory, QuestItem
from dungeon_crawler.world import Room

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

def test_take_damage_with_armour_exceeding_damage_deals_no_damage():
    character = Character(name="Hero", hp=30, attack_damage=5, armour=10)
    character.take_damage(4)
    assert character.hp == 30

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

def test_take_damage_with_thorns_does_not_trigger_when_damage_fully_blocked_by_armour():
    target = Character(name="Goblin", hp=30, attack_damage=5, armour=10)
    target.has_thorns = True
    attacker = Character(name="Hero", hp=50, attack_damage=10)
    target.take_damage(4, attacker=attacker)
    assert attacker.hp == 50

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

def test_take_damage_with_pending_damage_reduction_exceeding_damage_deals_no_damage():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.pending_damage_reduction = 20
    character.take_damage(10)
    assert character.hp == 30

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

def test_take_damage_with_pending_damage_reduction_fully_blocking_prevents_thorns():
    character = Character(name="Hero", hp=30, attack_damage=5)
    character.has_thorns = True
    character.pending_damage_reduction = 20
    attacker = Character(name="Goblin", hp=10, attack_damage=5)
    character.take_damage(10, attacker=attacker)
    assert attacker.hp == 10 # no damage got through, so no counter-strike

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

def test_attack_message_shows_full_deflection_when_armour_blocks_all_damage():
    attacker = Character(name="Hero", hp=30, attack_damage=5)
    target = Character(name="Goblin", hp=20, attack_damage=5, armour=10)
    message = attacker.attack(target)
    assert message == "Hero attacks Goblin for 0 damage. (5 deflected by armour)"

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
    assert message == "Hero gains 50 experience.\nHero reaches level 2! A skill point is available."

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
    assert message == "Hero reaches level 2! A skill point is available."

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

def test_get_stats_header_line_includes_ancestry_label_when_set():
    player = Player(name="hero", hp=100, ancestry_label="Descendant of Zeus")
    stats = player.get_stats()
    assert stats.startswith("hero (Descendant of Zeus):")

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

def test_character_initialises_with_no_equipped_weapon():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.equipped_weapon is None

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

def test_get_inventory_display_returns_empty_message_when_no_items():
    player = Player(name="hero", hp=100)
    assert player.get_inventory_display() == "Your inventory is empty."

def test_get_inventory_display_lists_single_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    assert player.get_inventory_display() == "Bronze Xiphos"

def test_get_inventory_display_shows_count_for_duplicate_items():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    assert player.get_inventory_display() == "Bronze Xiphos x2"

def test_get_inventory_display_lists_multiple_items_on_separate_lines():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(Weapon(name="Shield", description="", damage=1))
    assert player.get_inventory_display() == "Bronze Xiphos\nShield"

def test_get_inventory_display_marks_equipped_item():
    player = Player(name="hero", hp=100)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    sword.use(player)
    assert player.get_inventory_display() == "Bronze Xiphos (equipped)"

def test_get_inventory_display_marks_duplicate_group_equipped_if_any_instance_equipped():
    player = Player(name="hero", hp=100)
    equipped_sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    spare_sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(equipped_sword)
    player.inventory.add(spare_sword)
    equipped_sword.use(player)
    assert player.get_inventory_display() == "Bronze Xiphos x2 (equipped)"

def test_get_inventory_display_lists_quest_item_in_separate_section():
    player = Player(name="hero", hp=100)
    player.inventory.add(Weapon(name="Bronze Xiphos", description="", damage=3))
    player.inventory.add(QuestItem(name="Dummy Head", description=""))
    assert player.get_inventory_display() == "Bronze Xiphos\n\nQuest Items: Dummy Head"

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
    assert player.get_inventory_display() == "Bronze Xiphos\n\nGold: 5"

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
    player.skill_tree.skill_points = 3
    player.skill_tree.invest("attack", player)
    player.skill_tree.invest("attack", player)
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

def test_enemy_initialises_with_no_next_phase_factory_by_default():
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4)
    assert enemy.next_phase_factory is None

def test_enemy_initialises_with_next_phase_factory():
    factory = lambda: Enemy(name="Goblin Chief", hp=25, attack_damage=6)
    enemy = Enemy(name="Goblin", hp=15, attack_damage=4, next_phase_factory=factory)
    assert enemy.next_phase_factory is factory

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