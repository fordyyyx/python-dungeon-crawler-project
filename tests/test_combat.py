from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room
from dungeon_crawler.items import Weapon, Consumable
from dungeon_crawler.combat import resolve_combat_round, handle_enemy_defeat, flee_combat, handle_combat_command, resolve_attack_and_check_defeat, format_hp_line, get_enemy_display_name, handle_target_command, choose_enemy_action, _score_candidate_actions

def test_resolve_combat_round_reduces_enemy_hp():
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    resolve_combat_round(player, enemy, [player], [enemy])

    assert enemy.hp == 10

def test_resolve_combat_round_reduces_player_hp_when_enemy_survives(monkeypatch):
    """caution_weight=0 and neutral noise force the enemy to always choose 'attack' over 'defend' -
    without this, a damaged enemy's utility-scored AI can rationally choose to Defend instead (see
    choose_enemy_action() tests), which this test isn't about."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)

    resolve_combat_round(player, enemy, [player], [enemy])

    assert player.hp == 95

def test_resolve_combat_round_returns_both_attack_messages_when_both_survive(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert "Hero attacks Goblin" in result
    assert "Goblin attacks Hero" in result

def test_resolve_combat_round_enemy_defeated_does_not_counter_attack():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    resolve_combat_round(player, enemy, [player], [enemy])

    assert player.hp == 100

def test_resolve_combat_round_returns_fallen_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert "Goblin has been defeated." in result

def test_resolve_combat_round_returns_fallen_message_when_player_defeated():
    player = Player(name="Hero", hp=5, attack_damage=1)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=20)

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert "Hero has fallen." in result

def test_resolve_combat_round_returns_full_message_when_both_survive(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert result == "Hero attacks Goblin for 10 damage.\nGoblin attacks Hero for 5 damage.\nHero: 95/100 HP   |   Goblin: 10/20 HP"

def test_resolve_combat_round_returns_full_message_when_enemy_defeated():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert result == "Hero attacks Goblin for 20 damage.\nGoblin has been defeated.\nHero: 100/100 HP"

def test_resolve_combat_round_every_living_enemy_in_team_attacks_player(monkeypatch):
    """New team-combat behavior - the player only attacks the chosen target, but every still-living
    member of enemy_team gets its own turn, not just the target."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=10)
    target = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)
    teammate = Enemy(name="Imp", hp=20, attack_damage=3, caution_weight=0)

    result = resolve_combat_round(player, target, [player], [target, teammate])

    assert "Goblin attacks Hero for 5 damage." in result
    assert "Imp attacks Hero for 3 damage." in result
    assert player.hp == 92

def test_resolve_combat_round_dead_teammate_in_enemy_team_does_not_attack(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=10)
    target = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)
    dead_teammate = Enemy(name="Imp", hp=20, attack_damage=3)
    dead_teammate.hp = 0

    result = resolve_combat_round(player, target, [player], [target, dead_teammate])

    assert "Imp attacks" not in result
    assert player.hp == 95

def test_resolve_combat_round_enemy_defend_sets_pending_damage_reduction_and_message(monkeypatch):
    """A heavily-damaged, high-caution enemy facing a full-HP target with no real kill potential should
    reliably choose Defend over Attack, even under neutral noise."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=1)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, caution_weight=5.0, brace_amount=3)
    enemy.hp = 5

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert "Goblin braces for incoming damage." in result
    assert enemy.pending_damage_reduction == 3

def test_resolve_combat_round_enemy_heal_action_restores_hp_capped_at_max(monkeypatch):
    """heal_amount (20) deliberately exceeds the enemy's actual missing HP (15) - healed must be capped
    at what's actually missing, not the full heal_amount."""
    enemy = Enemy(name="Priest", hp=20, attack_damage=0, aggression_weight=0.0, caution_weight=1.0, heal_amount=20)
    enemy.hp = 5 # missing 15 HP; heal_value_ratio ties defend's base score, see _score_candidate_actions tests
    player = Player(name="Hero", hp=100, attack_damage=0) # 0 damage so the player's own attack doesn't touch enemy.hp

    values = iter([0.0, 0.0, 1.0]) # attack, defend roll low noise; heal rolls high noise, per dict insertion order
    monkeypatch.setattr("random.random", lambda: next(values))

    result = resolve_combat_round(player, enemy, [player], [enemy])

    assert "Priest recovers 15 HP." in result
    assert enemy.hp == 20

def test_resolve_combat_round_stops_rolling_further_enemies_once_player_defeated(monkeypatch):
    """Mirrors flee_combat()'s same rule - once a preceding enemy's turn kills the player, later
    enemies in enemy_team must not get a turn of their own."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=1)
    lethal_enemy = Enemy(name="Cyclops", hp=20, attack_damage=50, caution_weight=0)
    second_enemy = Enemy(name="Harpy", hp=20, attack_damage=5, caution_weight=0)

    result = resolve_combat_round(player, lethal_enemy, [player], [lethal_enemy, second_enemy])

    assert "Cyclops attacks Hero" in result
    assert "Harpy attacks" not in result # format_hp_line still lists it (still alive) - it just never got a turn
    assert player.hp == 0

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

    result = flee_combat(player, [enemy])

    assert "gets a hit in" in result
    assert enemy.has_been_fled_from is True

def test_flee_escapes_cleanly_when_random_forces_it(monkeypatch):
    """Forces random.random() to return 0.99 above the enemy's actual (non-maximal) flee-hit chance, so the clean-escape branch
    is guaranteed to fire."""
    monkeypatch.setattr("random.random", lambda: 0.99)
    player = Player(name="Hero", hp=20)
    starting_hp = player.hp
    enemy = Enemy(name="Test", hp=10, attack_damage=3)
    enemy.hp = 5

    result = flee_combat(player, [enemy])

    assert "cleanly" in result
    assert player.hp == starting_hp # confirms no damage was taken

def test_flee_combat_clean_escape_when_enemy_at_zero_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0

    message = flee_combat(player, [enemy])

    assert message == "You disengage cleanly, leaving your enemies behind."

def test_flee_combat_clean_escape_does_not_damage_player():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0

    flee_combat(player, [enemy])

    assert player.hp == 50

def test_flee_combat_gets_hit_when_enemy_at_full_hp():
    """No monkeypatch needed - a full-HP enemy has a 100% free-hit chance, and random.random() is always < 1.0,
    so the hit branch fires deterministically."""
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)

    message = flee_combat(player, [enemy])

    assert message == "You disengage but not without cost.\nThe Goblin gets a hit in as you go - 5 damage."
    assert player.hp == 45

def test_flee_combat_hit_can_defeat_player():
    player = Player(name="Hero", hp=5, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=20)

    message = flee_combat(player, [enemy])

    assert message == "You disengage but not without cost.\nThe Goblin gets a hit in as you go - 20 damage.\nHero has fallen. Game Over."
    assert player.hp == 0

def test_flee_combat_stops_rolling_further_enemies_once_player_defeated():
    """Both enemies are at full HP, so both have a deterministic 100% free-hit chance - but the first enemy's
    hit kills the player, and the loop must stop rather than rolling the second enemy too."""
    player = Player(name="Hero", hp=1)
    lethal_enemy = Enemy(name="Cyclops", hp=20, attack_damage=10)
    second_enemy = Enemy(name="Harpy", hp=20, attack_damage=5)

    message = flee_combat(player, [lethal_enemy, second_enemy])

    assert "Cyclops gets a hit in" in message
    assert "Harpy gets a hit in" not in message
    assert lethal_enemy.has_been_fled_from is True
    assert second_enemy.has_been_fled_from is False

def test_flee_combat_sets_has_been_fled_from_only_on_living_enemies(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.99)
    player = Player(name="Hero", hp=50)
    dead_enemy = Enemy(name="Fallen Imp", hp=10, attack_damage=3)
    dead_enemy.hp = 0
    alive_enemy = Enemy(name="Goblin", hp=100, attack_damage=1)
    alive_enemy.hp = 1 # low chance of a free hit, but still alive

    flee_combat(player, [dead_enemy, alive_enemy])

    assert dead_enemy.has_been_fled_from is False
    assert alive_enemy.has_been_fled_from is True

def test_handle_combat_command_attack_reduces_enemy_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    handle_combat_command("attack", player, enemy, [player], [enemy], room)

    assert enemy.hp == 10

def test_handle_combat_command_attack_returns_combat_round_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("attack", player, enemy, [player], [enemy], room)

    assert "Hero attacks Goblin for 10 damage." in message

def test_handle_combat_command_attack_when_enemy_defeated_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_combat_command("attack", player, enemy, [player], room.enemies, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_combat_command_attack_when_enemy_defeated_removes_enemy_from_room():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_combat_command("attack", player, enemy, [player], room.enemies, room)

    assert enemy not in room.enemies

def test_handle_combat_command_attack_when_enemy_survives_does_not_clear_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=5)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("attack", player, enemy, [player], [enemy], room)

    assert player.in_combat is True
    assert player.current_target is enemy

def test_handle_combat_command_flee_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("flee", player, enemy, [player], [enemy], room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_combat_command_flee_returns_flee_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("flee", player, enemy, [player], [enemy], room)

    assert message == "You disengage cleanly, leaving your enemies behind."

def test_handle_combat_command_use_item_heals_player():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    handle_combat_command("use potion", player, enemy, [player], [enemy], room)

    assert player.hp == 40

def test_handle_combat_command_use_item_returns_use_message_when_enemy_not_alive():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, [player], [enemy], room)

    assert message == "Hero uses Potion, healing 10 HP.\nHero: 40/50 HP"

def test_handle_combat_command_use_item_with_invalid_name_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 0
    room = Room("Arena")

    message = handle_combat_command("use nonexistent", player, enemy, [player], [enemy], room)

    assert message == "No item named 'nonexistent' in inventory."

def test_handle_combat_command_use_item_with_invalid_name_does_not_trigger_enemy_counterattack():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use nonexistent", player, enemy, [player], [enemy], room)

    assert message == "No item named 'nonexistent' in inventory."
    assert player.hp == 50

def test_handle_combat_command_use_item_triggers_enemy_counterattack_when_enemy_alive(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=50, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=5)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, [player], [enemy], room)

    assert message == "Hero uses Potion, healing 5 HP.\nGoblin attacks Hero for 5 damage.\nHero: 45/50 HP   |   Goblin: 20/20 HP"
    assert player.hp == 45

def test_handle_combat_command_use_item_only_living_enemies_in_team_counterattack():
    """A dead teammate in enemy_team must neither attack nor appear in the trailing HP line."""
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.hp = 30
    potion = Consumable(name="Potion", heal_amount=10)
    player.inventory.add(potion)
    dead_enemy = Enemy(name="Fallen Imp", hp=10, attack_damage=3)
    dead_enemy.hp = 0
    alive_enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("use potion", player, alive_enemy, [player], [dead_enemy, alive_enemy], room)

    assert message == "Hero uses Potion, healing 10 HP.\nGoblin attacks Hero for 5 damage.\nHero: 35/50 HP   |   Goblin: 20/20 HP"

def test_handle_combat_command_use_item_enemy_defend_action_sets_pending_damage_reduction(monkeypatch):
    """The 'use' branch's enemy-turn loop duplicates resolve_combat_round()'s action handling - this
    guards against the two implementations drifting apart."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=1)
    potion = Consumable(name="Potion", heal_amount=1)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, caution_weight=5.0, brace_amount=4)
    enemy.hp = 5
    room = Room("Arena")

    message = handle_combat_command("use potion", player, enemy, [player], [enemy], room)

    assert "Goblin braces for incoming damage." in message
    assert enemy.pending_damage_reduction == 4

def test_handle_combat_command_use_item_enemy_counterattack_can_defeat_player_clears_combat_state():
    player = Player(name="Hero", hp=5, attack_damage=10)
    potion = Consumable(name="Potion", heal_amount=1)
    player.inventory.add(potion)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=20)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    handle_combat_command("use potion", player, enemy, [player], [enemy], room)

    assert player.in_combat is False
    assert player.current_target is None
    assert player.hp == 0

def test_handle_combat_command_stats_returns_player_stats():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("stats", player, enemy, [player], [enemy], room)

    assert message.startswith("Hero ():")

def test_handle_combat_command_skills_returns_skills_display():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("skills", player, enemy, [player], [enemy], room)

    assert "Skill Points available: 0" in message

def test_handle_combat_command_learn_invests_skill():
    player = Player(name="Hero", hp=50, attack_damage=10)
    player.skill_tree.skill_points = 1
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("learn defence", player, enemy, [player], [enemy], room)

    assert player.armour == 2
    assert message == "Hero gains +2 armour from Hardened Skin."

def test_handle_combat_command_learn_with_no_skill_points_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("learn defence", player, enemy, [player], [enemy], room)

    assert message == "No skill points available"

def test_handle_combat_command_inventory_returns_inventory_display():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("inventory", player, enemy, [player], [enemy], room)

    assert message == "Your inventory is empty."

def test_handle_combat_command_unrecognised_command_returns_error_message():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("dance", player, enemy, [player], [enemy], room)

    assert message == "You can't do that mid-combat. Try 'attack', 'flee', 'use <item>', 'stats', 'skills', or 'inventory'."

def test_resolve_attack_and_check_defeat_reduces_enemy_hp():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    resolve_attack_and_check_defeat(player, enemy, [player], [enemy], room)

    assert enemy.hp == 10

def test_resolve_attack_and_check_defeat_returns_combat_round_result():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = resolve_attack_and_check_defeat(player, enemy, [player], [enemy], room)

    assert "Hero attacks Goblin for 10 damage." in message

def test_resolve_attack_and_check_defeat_when_enemy_defeated_clears_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_resolve_attack_and_check_defeat_when_enemy_defeated_removes_enemy_from_room():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert enemy not in room.enemies

def test_resolve_attack_and_check_defeat_when_enemy_survives_does_not_clear_combat_state():
    player = Player(name="Hero", hp=50, attack_damage=5)
    enemy = Enemy(name="Goblin", hp=100, attack_damage=5)
    player.in_combat = True
    player.current_target = enemy
    room = Room("Arena")

    resolve_attack_and_check_defeat(player, enemy, [player], [enemy], room)

    assert player.in_combat is True
    assert player.current_target is enemy

def test_resolve_attack_and_check_defeat_with_no_rewards_does_not_append_trailing_line():
    """handle_enemy_defeat() returns an empty string when there's nothing extra to report -
    resolve_attack_and_check_defeat() must not append a blank line in that case."""
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert message == "Hero attacks Goblin for 100 damage.\nGoblin has been defeated.\nHero: 50/50 HP"

def test_resolve_attack_and_check_defeat_appends_gold_reward_message():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, gold_reward=10)
    room = Room("Arena")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert "Hero picked up 10 gold." in message
    assert player.gold == 10

def test_resolve_attack_and_check_defeat_appends_experience_reward_message():
    player = Player(name="Hero", hp=50, attack_damage=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, experience_reward=15)
    room = Room("Arena")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert "Hero gains 15 experience." in message
    assert player.experience == 15

def test_resolve_attack_and_check_defeat_with_next_phase_factory_appends_transition_message():
    player = Player(name="Hero", hp=50, attack_damage=100)
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=10, attack_damage=15, next_phase_factory=lambda: next_phase)
    room = Room("Throne Room")
    room.add_enemy(enemy)

    message = resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert "Hades falls, but something rises to take its place - Hades (Enraged)." in message

def test_resolve_attack_and_check_defeat_with_next_phase_factory_ends_with_player_still_in_combat():
    """handle_enemy_defeat() runs after resolve_attack_and_check_defeat() clears combat state,
    and re-enables it for the new phase - the net effect is combat stays locked in on the next phase."""
    player = Player(name="Hero", hp=50, attack_damage=100)
    next_phase = Enemy(name="Hades (Enraged)", hp=40, attack_damage=20)
    enemy = Enemy(name="Hades", hp=10, attack_damage=15, next_phase_factory=lambda: next_phase)
    room = Room("Throne Room")
    room.add_enemy(enemy)

    resolve_attack_and_check_defeat(player, enemy, [player], room.enemies, room)

    assert player.in_combat is True
    assert player.current_target is next_phase

def test_resolve_attack_and_check_defeat_keeps_combat_locked_when_enemy_team_has_survivors():
    """A defeated target ends its own combat state by default, but the trailing check re-enables in_combat
    when the room still has other living enemies - a full team fight isn't over just because one member fell."""
    player = Player(name="Hero", hp=50, attack_damage=100)
    target = Enemy(name="Goblin", hp=10, attack_damage=5)
    teammate = Enemy(name="Imp", hp=20, attack_damage=1)
    room = Room("Arena")
    room.add_enemy(target)
    room.add_enemy(teammate)

    resolve_attack_and_check_defeat(player, target, [player], room.enemies, room)

    assert target not in room.enemies
    assert teammate in room.enemies
    assert player.in_combat is True

def test_resolve_attack_and_check_defeat_removes_enemy_defeated_via_thorns_even_if_not_the_target(monkeypatch):
    """Checks every member of enemy_team for defeat, not just the target - here Thorns reflects
    damage back onto a teammate who counterattacks, killing it during its own turn. caution_weight=0
    and neutral noise force both enemies to choose 'attack' - Thorns only triggers on a real hit."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    player = Player(name="Hero", hp=100, attack_damage=1)
    player.has_thorns = True
    target = Enemy(name="Goblin", hp=20, attack_damage=5, caution_weight=0)
    teammate = Enemy(name="Imp", hp=1, attack_damage=3, caution_weight=0)
    room = Room("Arena")
    room.add_enemy(target)
    room.add_enemy(teammate)

    resolve_attack_and_check_defeat(player, target, [player], room.enemies, room)

    assert teammate not in room.enemies
    assert target in room.enemies

def test_format_hp_line_returns_expected_format():
    player = Player(name="Hero", hp=95, attack_damage=10)
    player.max_hp = 100
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    enemy.max_hp = 20

    line = format_hp_line([player], [enemy])

    assert line == "Hero: 95/100 HP   |   Goblin: 10/20 HP"

def test_format_hp_line_omits_defeated_player_team_members():
    player = Player(name="Hero", hp=0)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    enemy.hp = 10

    line = format_hp_line([player], [enemy])

    assert line == "Goblin: 10/20 HP"

def test_format_hp_line_omits_defeated_enemy_team_members():
    player = Player(name="Hero", hp=100, attack_damage=10)
    player.hp = 95
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    enemy.hp = 0

    line = format_hp_line([player], [enemy])

    assert line == "Hero: 95/100 HP"

def test_format_hp_line_supports_multiple_living_combatants_on_each_side():
    player = Player(name="Hero", hp=100, attack_damage=10)
    companion = Player(name="Ally", hp=80, attack_damage=5)
    goblin = Enemy(name="Goblin", hp=20, attack_damage=5)
    harpy = Enemy(name="Harpy", hp=15, attack_damage=4)

    line = format_hp_line([player, companion], [goblin, harpy])

    assert line == "Hero: 100/100 HP   |   Ally: 80/80 HP   |   Goblin: 20/20 HP   |   Harpy: 15/15 HP"

def test_format_hp_line_shows_disambiguation_index_for_duplicate_enemy_names():
    player = Player(name="Hero", hp=50)
    harpy1 = Enemy(name="Harpy", hp=10)
    harpy2 = Enemy(name="Harpy", hp=8)

    line = format_hp_line([player], [harpy1, harpy2])

    assert line == "Hero: 50/50 HP   |   Harpy (1): 10/10 HP   |   Harpy (2): 8/8 HP"

def test_format_hp_line_keeps_stable_index_when_a_same_named_teammate_is_dead():
    """get_enemy_display_name() numbers by position in the full enemy_team, including the dead - a
    survivor's number must not shift just because an earlier same-named teammate fell."""
    player = Player(name="Hero", hp=50)
    dead_harpy = Enemy(name="Harpy", hp=10)
    dead_harpy.hp = 0
    living_harpy = Enemy(name="Harpy", hp=8)

    line = format_hp_line([player], [dead_harpy, living_harpy])

    assert line == "Hero: 50/50 HP   |   Harpy (2): 8/8 HP"

def test_get_enemy_display_name_returns_plain_name_when_unique_in_team():
    enemy = Enemy(name="Goblin", hp=10)

    assert get_enemy_display_name(enemy, [enemy]) == "Goblin"

def test_get_enemy_display_name_returns_plain_name_when_no_other_enemy_shares_its_name():
    goblin = Enemy(name="Goblin", hp=10)
    harpy = Enemy(name="Harpy", hp=10)

    assert get_enemy_display_name(goblin, [goblin, harpy]) == "Goblin"

def test_get_enemy_display_name_appends_index_when_names_shared():
    harpy1 = Enemy(name="Harpy", hp=10)
    harpy2 = Enemy(name="Harpy", hp=10)

    assert get_enemy_display_name(harpy1, [harpy1, harpy2]) == "Harpy (1)"
    assert get_enemy_display_name(harpy2, [harpy1, harpy2]) == "Harpy (2)"

def test_get_enemy_display_name_index_counts_defeated_teammates():
    dead_harpy = Enemy(name="Harpy", hp=10)
    dead_harpy.hp = 0
    living_harpy = Enemy(name="Harpy", hp=10)

    assert get_enemy_display_name(living_harpy, [dead_harpy, living_harpy]) == "Harpy (2)"

def test_handle_target_command_with_no_argument_returns_target_who():
    player = Player(name="Hero", hp=50)

    message = handle_target_command("target ", [], player)

    assert message == "Target who?"

def test_handle_target_command_single_match_sets_current_target():
    player = Player(name="Hero", hp=50)
    enemy = Enemy(name="Harpy", hp=10)

    handle_target_command("target harpy", [enemy], player)

    assert player.current_target is enemy

def test_handle_target_command_single_match_returns_focus_message():
    player = Player(name="Hero", hp=50)
    enemy = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target harpy", [enemy], player)

    assert message == "You focus on the Harpy."

def test_handle_target_command_matching_is_case_insensitive():
    player = Player(name="Hero", hp=50)
    enemy = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target HaRpY", [enemy], player)

    assert player.current_target is enemy
    assert message == "You focus on the Harpy."

def test_handle_target_command_no_match_returns_error_message():
    player = Player(name="Hero", hp=50)
    enemy = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target goblin", [enemy], player)

    assert message == "There's no 'goblin' here to target."
    assert player.current_target is None

def test_handle_target_command_dead_enemy_is_not_matched():
    player = Player(name="Hero", hp=50)
    enemy = Enemy(name="Harpy", hp=10)
    enemy.hp = 0

    message = handle_target_command("target harpy", [enemy], player)

    assert message == "There's no 'harpy' here to target."

def test_handle_target_command_multiple_matches_without_number_lists_display_names():
    player = Player(name="Hero", hp=50)
    harpy1 = Enemy(name="Harpy", hp=10)
    harpy2 = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target harpy", [harpy1, harpy2], player)

    assert message == "There's more than one harpy here - which one? Try: Harpy (1), Harpy (2)"
    assert player.current_target is None

def test_handle_target_command_multiple_matches_with_valid_number_sets_target():
    player = Player(name="Hero", hp=50)
    harpy1 = Enemy(name="Harpy", hp=10)
    harpy2 = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target harpy 2", [harpy1, harpy2], player)

    assert player.current_target is harpy2
    assert message == "You focus on the Harpy (2)."

def test_handle_target_command_multiple_matches_with_invalid_number_returns_error():
    player = Player(name="Hero", hp=50)
    harpy1 = Enemy(name="Harpy", hp=10)
    harpy2 = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target harpy 5", [harpy1, harpy2], player)

    assert message == "There's no harpy number 5 here."
    assert player.current_target is None

def test_handle_target_command_number_with_no_matching_name_at_all_returns_error():
    """same_named is empty here, not just filtered down to nothing - a distinct path from the
    'name exists but that number is out of range' case above."""
    player = Player(name="Hero", hp=50)
    harpy = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target goblin 2", [harpy], player)

    assert message == "There's no goblin number 2 here."
    assert player.current_target is None

def test_handle_target_command_number_selects_correct_survivor_despite_a_dead_teammate_between():
    """Regression test for the fix: the number now indexes into the full enemy_team (dead included),
    matching get_enemy_display_name()'s numbering - so 'target harpy 3' correctly reaches the third
    Harpy even though the second one (which used to shift the numbering) has died."""
    player = Player(name="Hero", hp=50)
    harpy1 = Enemy(name="Harpy", hp=10)
    dead_harpy2 = Enemy(name="Harpy", hp=10)
    dead_harpy2.hp = 0
    harpy3 = Enemy(name="Harpy", hp=10)

    message = handle_target_command("target harpy 3", [harpy1, dead_harpy2, harpy3], player)

    assert player.current_target is harpy3
    assert message == "You focus on the Harpy (3)."

def test_handle_target_command_number_targeting_a_defeated_enemy_returns_error():
    player = Player(name="Hero", hp=50)
    harpy1 = Enemy(name="Harpy", hp=10)
    dead_harpy2 = Enemy(name="Harpy", hp=10)
    dead_harpy2.hp = 0

    message = handle_target_command("target harpy 2", [harpy1, dead_harpy2], player)

    assert message == "The Harpy (2) has already been defeated."
    assert player.current_target is None

def test_score_candidate_actions_attack_scales_with_aggression_weight():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=25, aggression_weight=2.0)
    player = Player(name="Hero", hp=100, attack_damage=1, armour=0)
    player.hp = 50 # half health -> target_hp_ratio 0.5, kill_potential 25/50 = 0.5

    scores = _score_candidate_actions(enemy, [player])

    assert scores["attack"] == 2.0 # 2.0 * (0.5 + (1 - 0.5))

def test_score_candidate_actions_kill_potential_caps_at_one():
    """potential_damage can exceed target.hp (a one-shot kill) - kill_potential must clamp to 1.0, not go higher."""
    enemy = Enemy(name="Goblin", hp=10, attack_damage=1000, aggression_weight=1.0)
    player = Player(name="Hero", hp=100, attack_damage=1, armour=0) # full HP, target_hp_ratio 1.0

    scores = _score_candidate_actions(enemy, [player])

    assert scores["attack"] == 1.0 # 1.0 * (1.0 + (1 - 1.0))

def test_score_candidate_actions_armour_reduces_kill_potential():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=10, aggression_weight=1.0)
    player = Player(name="Hero", hp=100, attack_damage=1, armour=10) # armour fully blocks the hit, full HP

    scores = _score_candidate_actions(enemy, [player])

    assert scores["attack"] == 0.0

def test_score_candidate_actions_low_target_hp_raises_attack_score():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, aggression_weight=1.0) # 0 damage isolates the hp_ratio term
    player = Player(name="Hero", hp=100, attack_damage=1, armour=0)
    player.hp = 25 # target_hp_ratio 0.25

    scores = _score_candidate_actions(enemy, [player])

    assert scores["attack"] == 0.75 # 1.0 * (0.0 + (1 - 0.25))

def test_score_candidate_actions_only_considers_first_player_team_member():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, aggression_weight=1.0)
    full_hp_player = Player(name="Hero", hp=100, attack_damage=1, armour=0)
    low_hp_companion = Player(name="Ally", hp=100, attack_damage=1, armour=0)
    low_hp_companion.hp = 1 # would score much higher if this one were used instead

    scores = _score_candidate_actions(enemy, [full_hp_player, low_hp_companion])

    assert scores["attack"] == 0.0

def test_score_candidate_actions_always_includes_defend():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    assert "defend" in scores

def test_score_candidate_actions_defend_is_zero_at_full_health():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, caution_weight=2.0) # full HP, never damaged
    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    assert scores["defend"] == 0.0

def test_score_candidate_actions_defend_scales_with_caution_weight_and_missing_hp():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, caution_weight=2.0)
    enemy.hp = 5 # self_missing_hp_ratio 0.5

    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    assert scores["defend"] == 1.0 # 2.0 * 0.5

def test_score_candidate_actions_excludes_heal_when_heal_amount_is_zero():
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5) # heal_amount defaults to 0
    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    assert "heal" not in scores

def test_score_candidate_actions_includes_heal_when_heal_amount_positive():
    enemy = Enemy(name="Priest", hp=10, attack_damage=5, heal_amount=5)
    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    assert "heal" in scores

def test_score_candidate_actions_heal_score_formula():
    enemy = Enemy(name="Priest", hp=10, attack_damage=0, caution_weight=2.0, heal_amount=5)
    enemy.hp = 5 # self_missing_hp_ratio 0.5

    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    # heal_value_ratio = min(1.0, 5/10) = 0.5; heal = caution(2.0) * missing_hp_ratio(0.5) * heal_value_ratio(0.5)
    assert scores["heal"] == 0.5

def test_score_candidate_actions_heal_value_ratio_caps_at_one():
    """heal_amount can exceed max_hp - heal_value_ratio must clamp to 1.0, tying (never exceeding) defend's
    base score, since heal is structurally defend's score scaled down by how much of a top-up it represents."""
    enemy = Enemy(name="Priest", hp=20, attack_damage=0, caution_weight=1.0, heal_amount=100)
    enemy.hp = 10 # self_missing_hp_ratio 0.5

    player = Player(name="Hero", hp=100, attack_damage=1)

    scores = _score_candidate_actions(enemy, [player])

    assert scores["heal"] == 0.5
    assert scores["defend"] == 0.5

def test_choose_enemy_action_picks_the_dominant_action(monkeypatch):
    """Neutral noise (random.random() == 0.5 -> noise term is exactly 0) isolates the base-score comparison:
    a full-HP enemy with strong kill potential should always attack over defending."""
    monkeypatch.setattr("random.random", lambda: 0.5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=100) # full HP -> defend scores 0; huge kill potential
    player = Player(name="Hero", hp=50)
    player.hp = 25 # half health, raises attack's score further

    assert choose_enemy_action(enemy, [player]) == "attack"

def test_choose_enemy_action_picks_defend_when_it_dominates(monkeypatch):
    monkeypatch.setattr("random.random", lambda: 0.5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, aggression_weight=1.0, caution_weight=5.0)
    enemy.hp = 1 # nearly dead -> self_missing_hp_ratio 0.9, defend score 4.5
    player = Player(name="Hero", hp=100, attack_damage=1) # full HP and attack_damage 0 -> attack scores 0.0

    assert choose_enemy_action(enemy, [player]) == "defend"

def test_choose_enemy_action_random_noise_can_flip_a_tied_race(monkeypatch):
    """With attack and defend scored exactly equal, the per-action noise term decides the tie - this is the
    'lucky escape' mechanic CLAUDE.md describes: the AI won't always play optimally. random.random() is called
    once per candidate action, in the order _score_candidate_actions() builds the dict (attack, then defend)."""
    enemy = Enemy(name="Goblin", hp=10, attack_damage=0, aggression_weight=1.0, caution_weight=1.0, randomness_weight=1.0)
    enemy.hp = 5 # self_missing_hp_ratio 0.5 -> defend score 0.5
    player = Player(name="Hero", hp=100, attack_damage=1)
    player.hp = 50 # target_hp_ratio 0.5 -> attack score 0.5, tied with defend

    low_then_high = iter([0.0, 1.0]) # attack rolls low noise, defend rolls high noise
    monkeypatch.setattr("random.random", lambda: next(low_then_high))
    assert choose_enemy_action(enemy, [player]) == "defend"

    high_then_low = iter([1.0, 0.0]) # reversed - attack now rolls high noise, defend rolls low noise
    monkeypatch.setattr("random.random", lambda: next(high_then_low))
    assert choose_enemy_action(enemy, [player]) == "attack"

def test_choose_enemy_action_can_choose_heal_when_it_ties_defend_and_noise_favours_it(monkeypatch):
    """heal_amount == max_hp makes heal's base score exactly tie defend's (see the heal_value_ratio cap test) -
    with aggression 0.0 keeping attack out of contention, noise alone decides between the two survivors."""
    enemy = Enemy(name="Priest", hp=10, attack_damage=0, aggression_weight=0.0, caution_weight=1.0, heal_amount=10)
    enemy.hp = 1 # self_missing_hp_ratio 0.9 -> defend and heal both score 0.9
    player = Player(name="Hero", hp=100, attack_damage=1)

    values = iter([0.0, 0.0, 1.0]) # attack, defend roll low noise; heal rolls high noise
    monkeypatch.setattr("random.random", lambda: next(values))
    assert choose_enemy_action(enemy, [player]) == "heal"

def test_handle_combat_command_target_sets_current_target():
    player = Player(name="Hero", hp=50, attack_damage=10)
    enemy = Enemy(name="Goblin", hp=20, attack_damage=5)
    room = Room("Arena")

    message = handle_combat_command("target goblin", player, enemy, [player], [enemy], room)

    assert player.current_target is enemy
    assert message == "You focus on the Goblin."
