from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room
from dungeon_crawler.items import Weapon, Consumable
from dungeon_crawler.combat import resolve_combat_round, handle_enemy_defeat, flee_combat, handle_combat_command, resolve_attack_and_check_defeat, format_hp_line

def test_resolve_combat_round_reduces_enemy_hp():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert enemy.hp == 10

def test_resolve_combat_round_reduces_player_hp_when_enemy_survives():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert player.hp == 95

def test_resolve_combat_round_returns_both_attack_messages_when_both_survive():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert "Hero attacks Goblin" in result
    assert "Goblin attacks Hero" in result

def test_resolve_combat_round_enemy_defeated_does_not_counter_attack():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    resolve_combat_round(player, enemy)

    assert player.hp == 100

def test_resolve_combat_round_returns_fallen_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert "Goblin has been defeated." in result

def test_resolve_combat_round_returns_fallen_message_when_player_defeated():
    player = Player(name="Hero", hp=5, attack_damage=1)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=20)

    result = resolve_combat_round(player, enemy)

    assert "Hero has fallen." in result

def test_resolve_combat_round_returns_full_message_when_both_survive():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert result == "Hero attacks Goblin for 10 damage.\nGoblin attacks Hero for 5 damage.\nHero: 95/100 HP  |  Goblin: 10/20 HP"

def test_resolve_combat_round_returns_full_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy)

    assert result == "Hero attacks Goblin for 20 damage.\nGoblin has been defeated.\nHero: 100/100 HP"

def test_handle_enemy_defeat_removes_enemy_from_room():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert enemy not in room.enemies

def test_handle_enemy_defeat_adds_loot_to_room():
    room = Room("Armoury")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert sword in room.items

def test_handle_enemy_defeat_with_no_loot_adds_nothing_to_room():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert room.items == []

def test_handle_enemy_defeat_with_no_rewards_returns_empty_message():
    """Enemy.on_death() (called earlier, via take_damage()) already reports the defeat itself -
    handle_enemy_defeat() only reports what it alone grants: gold, experience, or a phase transition."""
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert message == ""

def test_handle_enemy_defeat_with_only_loot_returns_empty_message():
    """Loot is moved into the room, but not reported here - Enemy.on_death() already lists what dropped,
    so handle_enemy_defeat() would otherwise duplicate that line."""
    room = Room("Armoury")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert message == ""

def test_handle_enemy_defeat_message_omits_drop_line_when_no_loot():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert "dropped" not in message.lower()

def test_handle_enemy_defeat_adds_gold_reward_to_player():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, gold_reward=10)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.gold == 10

def test_handle_enemy_defeat_message_includes_gold_reward():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, gold_reward=10)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert "Hero picked up 10 gold." in message

def test_handle_enemy_defeat_with_no_gold_reward_does_not_change_player_gold():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.gold == 0

def test_handle_enemy_defeat_with_no_gold_reward_omits_gold_line():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert "gold" not in message.lower()

def test_handle_enemy_defeat_grants_experience_reward_to_player():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, experience_reward=15)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.experience == 15

def test_handle_enemy_defeat_message_includes_experience_gain():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5, experience_reward=15)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert "Hero gains 15 experience." in message

def test_handle_enemy_defeat_with_no_experience_reward_does_not_change_player_experience():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.experience == 0

def test_handle_enemy_defeat_with_no_experience_reward_omits_experience_line():
    room = Room("Armoury")
    enemy = Enemy(name="Goblin", hp=0, attack_damage=5)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert "experience" not in message.lower()

def test_handle_enemy_defeat_with_next_phase_factory_removes_original_enemy():
    room = Room("Throne Room")
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=0, attack_damage=15, next_phase_factory=lambda: next_phase)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert enemy not in room.enemies

def test_handle_enemy_defeat_with_next_phase_factory_adds_next_phase_to_room():
    room = Room("Throne Room")
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=0, attack_damage=15, next_phase_factory=lambda: next_phase)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert next_phase in room.enemies

def test_handle_enemy_defeat_with_next_phase_factory_sets_player_current_target():
    room = Room("Throne Room")
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=0, attack_damage=15, next_phase_factory=lambda: next_phase)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.current_target is next_phase

def test_handle_enemy_defeat_with_next_phase_factory_keeps_player_in_combat():
    room = Room("Throne Room")
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=0, attack_damage=15, next_phase_factory=lambda: next_phase)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.in_combat is True

def test_handle_enemy_defeat_with_next_phase_factory_returns_transition_message():
    room = Room("Throne Room")
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=0, attack_damage=15, next_phase_factory=lambda: next_phase)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    message = handle_enemy_defeat(room, enemy, player)

    assert message == "Hades falls, but something rises to take its place - Hades (Enraged)."

def test_handle_enemy_defeat_with_next_phase_factory_does_not_grant_gold_or_experience():
    room = Room("Throne Room")
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=0, attack_damage=15, gold_reward=50, experience_reward=50, next_phase_factory=lambda: next_phase)
    room.add_enemy(enemy)
    player = Player(name="Hero", hp=50)

    handle_enemy_defeat(room, enemy, player)

    assert player.gold == 0
    assert player.experience == 0

def test_flee_lands_free_hit_when_random_forces_it(monkeypatch):
    """Deterministic version of the free-hit chance - forces random.random() to return 0.0 (always below any nonzero chance)
    so the hit branch is guaranteed to fire, rather than relying on running the test many times."""
    monkeypatch.setattr("random.random", lambda: 0.0)
    player = Player(name="Hero", hp=20)
    enemy = Enemy(name="Test", hp=10, attack_damage=3)
    enemy.hp = 5 # half health -> chance_of_free_hit = 0.5, genuinely above 0.1

    result = flee_combat(player, enemy)

    assert "gets a hit in"in result
    assert enemy.has_been_fled_from is True

def test_flee_escapes_cleanly_when_random_forces_it(monkeypatch):
    """Forces random.random() to return 0.99 above the enemy's actual (non-maximal) flee-hit chance, so the clean-escape branch 
    is guaranteed to fire."""
    monkeypatch.setattr("random.random", lambda: 0.99)
    player = Player(name="Hero", hp=20)
    starting_hp = player.hp
    enemy = Enemy(name="Test", hp=10, attack_damage=3)
    enemy.hp = 5

    result = flee_combat(player, enemy)

    assert "cleanly" in result
    assert player.hp == starting_hp # confirms no damage was taken

def test_flee_combat_clean_escape_when_enemy_at_zero_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0

    message = flee_combat(player, enemy)

    assert message == "You disengage cleanly, leaving the Goblin behind."

def test_flee_combat_clean_escape_does_not_damage_player():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0

    flee_combat(player, enemy)

    assert player.hp == 50

def test_flee_combat_gets_hit_when_enemy_at_full_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    message = flee_combat(player, enemy)

    assert message == "You disengage, but the Goblin gets a hit in as you go - 5 damage."
    assert player.hp == 45

def test_flee_combat_hit_can_defeat_player():
    player = Player(name="Hero", hp=5, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=20)

    message = flee_combat(player, enemy)

    assert message == "You disengage, but the Goblin gets a hit in as you go - 20 damage.\nHero has fallen. Game Over."
    assert player.hp == 0

def test_handle_combat_command_attack_reduces_enemy_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    handle_combat_command("attack", player, enemy, room)

    assert enemy.hp == 10

def test_handle_combat_command_attack_returns_combat_round_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("attack", player, enemy, room)

    assert "Hero attacks Goblin for 10 damage." in message

def test_handle_combat_command_attack_when_enemy_defeated_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_combat_command("attack", player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_combat_command_attack_when_enemy_defeated_removes_enemy_from_room():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_combat_command("attack", player, enemy, room)

    assert enemy not in room.enemies

def test_handle_combat_command_attack_when_enemy_survives_does_not_clear_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=5)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("attack", player, enemy, room)

    assert player.in_combat is True
    assert player.current_target is enemy

def test_handle_combat_command_flee_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("flee", player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_combat_command_flee_returns_flee_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("flee", player, enemy, room)

    assert message == "You disengage cleanly, leaving the Goblin behind."

def test_handle_combat_command_use_item_heals_player():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    handle_combat_command("use potion", player, enemy, room)

    assert player.hp == 40

def test_handle_combat_command_use_item_returns_use_message_when_enemy_not_alive():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, room)

    assert message == "Hero uses Potion, healing 10 HP."

def test_handle_combat_command_use_item_with_invalid_name_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("use nonexistent", player, enemy, room)

    assert message == "No item named 'nonexistent' in inventory."

def test_handle_combat_command_use_item_with_invalid_name_does_not_trigger_enemy_counterattack():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use nonexistent", player, enemy, room)

    assert message == "No item named 'nonexistent' in inventory."
    assert player.hp == 50

def test_handle_combat_command_use_item_triggers_enemy_counterattack_when_enemy_alive():
    player = Player(name="Hero", hp=50, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=5)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, room)

    assert message == "Hero uses Potion, healing 5 HP.\nGoblin attacks Hero for 5 damage.\nHero: 45/50 HP  |  Goblin: 20/20 HP"
    assert player.hp == 45

def test_handle_combat_command_use_item_enemy_counterattack_can_defeat_player_clears_combat_state():
    player = Player(name="Hero", hp=5, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=1)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=20)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("use potion", player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None
    assert player.hp == 0

def test_handle_combat_command_stats_returns_player_stats():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("stats", player, enemy, room)

    assert message.startswith("Hero ():")

def test_handle_combat_command_skills_returns_skills_display():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("skills", player, enemy, room)

    assert "Skill Points available: 0" in message

def test_handle_combat_command_learn_invests_skill():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 1
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("learn defence", player, enemy, room)

    assert player.armour == 2
    assert message == "Hero gains +2 armour from Hardened Skin."

def test_handle_combat_command_learn_with_no_skill_points_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("learn defence", player, enemy, room)

    assert message == "No skill points available"

def test_handle_combat_command_inventory_returns_inventory_display():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("inventory", player, enemy, room)

    assert message == "Your inventory is empty."

def test_handle_combat_command_unrecognised_command_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("dance", player, enemy, room)

    assert message == "You can't do that mid-combat. Try 'attack', 'flee', 'use <item>', 'stats', 'skills', or 'inventory'."

def test_resolve_attack_and_check_defeat_reduces_enemy_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    resolve_attack_and_check_defeat(player, enemy, room)

    assert enemy.hp == 10

def test_resolve_attack_and_check_defeat_returns_combat_round_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = resolve_attack_and_check_defeat(player, enemy, room)

    assert "Hero attacks Goblin for 10 damage." in message

def test_resolve_attack_and_check_defeat_when_enemy_defeated_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_resolve_attack_and_check_defeat_when_enemy_defeated_removes_enemy_from_room():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, room)

    assert enemy not in room.enemies

def test_resolve_attack_and_check_defeat_when_enemy_survives_does_not_clear_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=5)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    resolve_attack_and_check_defeat(player, enemy, room)

    assert player.in_combat is True
    assert player.current_target is enemy

def test_resolve_attack_and_check_defeat_with_no_rewards_does_not_append_trailing_line():
    """handle_enemy_defeat() returns an empty string when there's nothing extra to report -
    resolve_attack_and_check_defeat() must not append a blank line in that case."""
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, room)

    assert message == "Hero attacks Goblin for 100 damage.\nGoblin has been defeated.\nHero: 50/50 HP"

def test_resolve_attack_and_check_defeat_appends_gold_reward_message():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, gold_reward=10)
    room = Room("Arena")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, room)

    assert "Hero picked up 10 gold." in message
    assert player.gold == 10

def test_resolve_attack_and_check_defeat_appends_experience_reward_message():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, experience_reward=15)
    room = Room("Arena")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, room)

    assert "Hero gains 15 experience." in message
    assert player.experience == 15

def test_resolve_attack_and_check_defeat_with_next_phase_factory_appends_transition_message():
    player = Player(name="Hero", hp=50, attack_damage=100)
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=10, attack_damage=15, next_phase_factory=lambda: next_phase)
    room = Room("Throne Room")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, room)

    assert "Hades falls, but something rises to take its place - Hades (Enraged)." in message

def test_resolve_attack_and_check_defeat_with_next_phase_factory_ends_with_player_still_in_combat():
    """handle_enemy_defeat() runs after resolve_attack_and_check_defeat() clears combat state,
    and re-enables it for the new phase - the net effect is combat stays locked in on the next phase."""
    player = Player(name="Hero", hp=50, attack_damage=100)
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=10, attack_damage=15, next_phase_factory=lambda: next_phase)
    room = Room("Throne Room")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, room)

    assert player.in_combat is True
    assert player.current_target is next_phase

def test_format_hp_line_returns_expected_format():
    player = Player(name="Hero", hp=95, attack_damage=10)
    player.max_hp = 100
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    enemy.max_hp = 20

    line = format_hp_line(player, enemy)

    assert line == "Hero: 95/100 HP  |  Goblin: 10/20 HP"
