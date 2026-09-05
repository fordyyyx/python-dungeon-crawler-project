from dungeon_crawler.characters import Player, Enemy, Ally, Companion
from dungeon_crawler.world import Room, Map
from dungeon_crawler.items import Weapon, Armour
from dungeon_crawler.dev_tools import find_item_by_name, handle_dev_command, handle_dev_set, find_enemy_by_name, find_ally_by_name, find_companion_by_name, find_spell_by_name, handle_dev_kill, find_room_by_name_ci, handle_dev_remove, handle_dev_remove_all, handle_dev_clear_room, handle_dev_afflict, handle_dev_set_durability

def test_find_item_by_name_returns_item_for_known_name():
    item = find_item_by_name("wooden sword")
    assert item is not None
    assert item.name == "Wooden Sword"

def test_find_item_by_name_is_case_insensitive():
    item = find_item_by_name("WOODEN SWORD")
    assert item is not None
    assert item.name == "Wooden Sword"

def test_find_item_by_name_returns_none_for_unknown_name():
    item = find_item_by_name("nonexistent item")
    assert item is None

def test_find_item_by_name_returns_new_instance_each_call():
    item1 = find_item_by_name("wooden sword")
    item2 = find_item_by_name("wooden sword")
    assert item1 is not item2

def test_find_item_by_name_returns_test_spellbook_for_known_name():
    item = find_item_by_name("test spellbook")
    assert item is not None
    assert item.name == "Test Spellbook"

def test_find_item_by_name_returns_test_healing_tonic_for_known_name():
    item = find_item_by_name("test healing tonic")
    assert item is not None
    assert item.name == "Test Healing Tonic"

def test_find_item_by_name_returns_test_venom_vial_for_known_name():
    item = find_item_by_name("test venom vial")
    assert item is not None
    assert item.name == "Test Venom Vial"

def test_handle_dev_command_add_known_item_adds_to_inventory():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    handle_dev_command("add wooden sword", player, room, dungeon)
    item_names = [item.name for item in player.inventory.items]
    assert "Wooden Sword" in item_names

def test_handle_dev_command_add_known_item_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("add wooden sword", player, room, dungeon)
    assert message == "[DEV] Added Wooden Sword to inventory."
    assert new_room is None

def test_handle_dev_command_add_unknown_item_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("add nonexistent thing", player, room, dungeon)
    assert message == "[DEV] No known item named 'nonexistent thing'."

def test_handle_dev_command_add_unknown_item_does_not_add_to_inventory():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    handle_dev_command("add nonexistent thing", player, room, dungeon)
    assert len(player.inventory) == 0

def test_handle_dev_command_set_dispatches_to_handle_dev_set():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("set atk 50", player, room, dungeon)
    assert player.attack_damage == 50
    assert message == "[DEV] atk set to 50."
    assert new_room is None

def test_handle_dev_command_set_with_missing_value_returns_usage_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("set atk", player, room, dungeon)
    assert message == "[DEV] Usage: dev set <stat> <value>"

def test_handle_dev_command_unlock_all_clears_locked_exits():
    room = Room("A")
    room.lock_exit("north", "Key")
    room.lock_exit("east", "Shield")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    handle_dev_command("unlock all", player, room, dungeon)
    assert room.locked_exits == {}

def test_handle_dev_command_unlock_all_returns_message_listing_unlocked_directions():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock all", player, room, dungeon)
    assert message == "[DEV] Unlocked: north."

def test_handle_dev_command_unlock_all_with_no_locked_exits_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock all", player, room, dungeon)
    assert message == "[DEV] No locked exits in this room."

def test_handle_dev_command_unlock_direction_removes_lock():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    handle_dev_command("unlock north", player, room, dungeon)
    assert "north" not in room.locked_exits

def test_handle_dev_command_unlock_direction_returns_confirmation_message():
    room = Room("A")
    room.lock_exit("north", "Key")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock north", player, room, dungeon)
    assert message == "[DEV] Unlocked exit: north."

def test_handle_dev_command_unlock_direction_not_locked_returns_message():
    room = Room("A")
    player = Player(name="hero", hp=100)
    dungeon = Map()
    message, new_room = handle_dev_command("unlock north", player, room, dungeon)
    assert message == "[DEV] north is not a locked exit here."

def test_handle_dev_command_help_returns_help_text():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("help", player, room, dungeon)
    assert message == (
        "[DEV] Commands: dev add <item>, dev set <stat> <n>\n"
        "dev unlock <direction>, dev unlock all\n"
        "dev set durability <slot> <value>, dev spawn <character>\n"
        "dev remove <character/all>, dev clear room\n"
        "dev afflict <target> <effect> <amount> <duration>\n"
        "dev kill <enemy>, dev teleport <room>, dev learn <skill>\n"
        "dev grant spell <name>"
    )

def test_handle_dev_command_unrecognised_command_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("frobnicate", player, room, dungeon)
    assert message == "[DEV] Unrecognised dev command: frobnicate. Try 'dev help'."

def test_handle_dev_command_spawn_enemy_adds_to_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn minotaur", player, room, dungeon)
    assert message == "[DEV] Spawned Minotaur."
    enemy_names = [enemy.name for enemy in room.enemies]
    assert "Minotaur" in enemy_names

def test_handle_dev_command_spawn_ally_adds_to_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn chiron", player, room, dungeon)
    assert message == "[DEV] Spawned Chiron."
    ally_names = [ally.name for ally in room.allies]
    assert "Chiron" in ally_names

def test_handle_dev_command_spawn_companion_adds_to_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn test companion", player, room, dungeon)
    assert message == "[DEV] Spawned Test Companion. Use 'recruit Test Companion' to add them to your team."
    companion_names = [companion.name for companion in room.companions]
    assert "Test Companion" in companion_names

def test_handle_dev_command_spawn_unknown_name_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("spawn nonexistent", player, room, dungeon)
    assert message == "[DEV] No known character names nonexistent."

def test_handle_dev_command_remove_removes_named_enemy():
    player = Player(name="hero", hp=100)
    room = Room("A")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)
    dungeon = Map()
    message, new_room = handle_dev_command("remove goblin", player, room, dungeon)
    assert message == "[DEV] Removed Goblin."
    assert enemy not in room.enemies

def test_handle_dev_command_remove_all_removes_every_matching_enemy():
    player = Player(name="hero", hp=100)
    room = Room("A")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    dungeon = Map()
    message, new_room = handle_dev_command("remove all goblin", player, room, dungeon)
    assert message == "[DEV] Removed 2 instance(s) of 'goblin'."
    assert room.enemies == []

def test_handle_dev_command_clear_room_removes_all_enemies_and_allies():
    player = Player(name="hero", hp=100)
    room = Room("A")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_ally(Ally(name="Chiron"))
    dungeon = Map()
    message, new_room = handle_dev_command("clear room", player, room, dungeon)
    assert message == "[DEV] Cleared room: removed 1 enemies and 1 allies."
    assert room.enemies == []
    assert room.allies == []

def test_handle_dev_command_kill_defeats_first_enemy_in_room():
    player = Player(name="hero", hp=100)
    room = Room("A")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)
    dungeon = Map()
    message, new_room = handle_dev_command("kill", player, room, dungeon)
    assert message == "[DEV] Killed Goblin."
    assert enemy not in room.enemies

def test_handle_dev_command_kill_with_no_enemy_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("kill", player, room, dungeon)
    assert message == "[DEV] No enemy here to kill."

def test_handle_dev_command_teleport_to_known_room_returns_target_room():
    player = Player(name="hero", hp=100)
    room = Room("Start")
    target = Room("Alpha")
    dungeon = Map()
    dungeon.add_room(target)
    message, new_room = handle_dev_command("teleport Alpha", player, room, dungeon)
    assert message == "[DEV] Teleported to Alpha."
    assert new_room is target

def test_handle_dev_command_teleport_to_unknown_room_returns_error_message():
    player = Player(name="hero", hp=100)
    room = Room("Start")
    dungeon = Map()
    message, new_room = handle_dev_command("teleport Nowhere", player, room, dungeon)
    assert message == "[DEV] No room named 'Nowhere'."
    assert new_room is None

def test_handle_dev_command_teleport_clears_combat_state():
    player = Player(name="hero", hp=100)
    player.in_combat = True
    player.current_target = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Start")
    target = Room("Alpha")
    dungeon = Map()
    dungeon.add_room(target)
    handle_dev_command("teleport Alpha", player, room, dungeon)
    assert player.in_combat is False
    assert player.current_target is None

def test_handle_dev_command_learn_invests_a_free_skill_point():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    message, new_room = handle_dev_command("learn defence", player, room, dungeon)
    assert message == "[DEV] hero gains +2 armour from Hardened Skin."
    assert player.armour == 2
    assert player.skill_tree.skill_points == 0

def test_handle_dev_command_learn_with_invalid_path_refunds_the_free_skill_point():
    player = Player(name="hero", hp=100)
    room = Room("A")
    dungeon = Map()
    handle_dev_command("learn nonexistent", player, room, dungeon)
    assert player.skill_tree.skill_points == 0

def test_handle_dev_set_updates_aliased_stat():
    player = Player(name="hero", hp=100, attack_damage=10)
    handle_dev_set("atk", "50", player)
    assert player.attack_damage == 50

def test_handle_dev_set_returns_confirmation_message():
    player = Player(name="hero", hp=100, attack_damage=10)
    message = handle_dev_set("atk", "50", player)
    assert message == "[DEV] atk set to 50."

def test_handle_dev_set_skillpoints_sets_exact_value():
    player = Player(name="hero", hp=100)
    player.skill_tree.skill_points = 5
    handle_dev_set("skillpoints", "3", player)
    assert player.skill_tree.skill_points == 3

def test_handle_dev_set_returns_skillpoints_message():
    player = Player(name="hero", hp=100)
    message = handle_dev_set("skillpoints", "3", player)
    assert message == "[DEV] Skill points set to 3."

def test_handle_dev_set_unknown_stat_returns_error_message():
    player = Player(name="hero", hp=100)
    message = handle_dev_set("nonsense", "5", player)
    assert message == "[DEV] Unknown stat 'nonsense'."

def test_handle_dev_set_invalid_value_returns_error_message():
    player = Player(name="hero", hp=100)
    message = handle_dev_set("atk", "abc", player)
    assert message == "[DEV] Invalid value 'abc'."

def test_handle_dev_set_hp_above_max_hp_raises_max_hp():
    player = Player(name="hero", hp=100)
    handle_dev_set("hp", "150", player)
    assert player.max_hp == 150

def test_handle_dev_set_hp_below_max_hp_does_not_change_max_hp():
    player = Player(name="hero", hp=100)
    handle_dev_set("hp", "50", player)
    assert player.max_hp == 100

def test_handle_dev_set_maxhp_below_current_hp_clamps_hp_down():
    player = Player(name="hero", hp=100)
    handle_dev_set("maxhp", "50", player)
    assert player.hp == 50

def test_handle_dev_set_maxhp_above_current_hp_does_not_change_hp():
    player = Player(name="hero", hp=100)
    handle_dev_set("maxhp", "150", player)
    assert player.hp == 100

def test_find_enemy_by_name_returns_enemy_for_known_name():
    enemy = find_enemy_by_name("minotaur")
    assert enemy is not None
    assert enemy.name == "Minotaur"

def test_find_enemy_by_name_is_case_insensitive():
    enemy = find_enemy_by_name("MINOTAUR")
    assert enemy is not None
    assert enemy.name == "Minotaur"

def test_find_enemy_by_name_returns_none_for_unknown_name():
    enemy = find_enemy_by_name("nonexistent")
    assert enemy is None

def test_find_enemy_by_name_returns_new_instance_each_call():
    enemy1 = find_enemy_by_name("minotaur")
    enemy2 = find_enemy_by_name("minotaur")
    assert enemy1 is not enemy2

def test_find_ally_by_name_returns_ally_for_known_name():
    ally = find_ally_by_name("chiron")
    assert ally is not None
    assert ally.name == "Chiron"

def test_find_ally_by_name_is_case_insensitive():
    ally = find_ally_by_name("CHIRON")
    assert ally is not None
    assert ally.name == "Chiron"

def test_find_ally_by_name_returns_none_for_unknown_name():
    ally = find_ally_by_name("nonexistent")
    assert ally is None

def test_find_ally_by_name_returns_new_instance_each_call():
    ally1 = find_ally_by_name("chiron")
    ally2 = find_ally_by_name("chiron")
    assert ally1 is not ally2

def test_handle_dev_kill_prefers_players_current_target():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    other_enemy = Enemy(name="Other", hp=10, attack_damage=5)
    target_enemy = Enemy(name="Target", hp=10, attack_damage=5)
    room.add_enemy(other_enemy)
    room.add_enemy(target_enemy)
    player.current_target = target_enemy

    message = handle_dev_kill(player, room)

    assert message == "[DEV] Killed Target."
    assert target_enemy not in room.enemies
    assert other_enemy in room.enemies

def test_handle_dev_kill_falls_back_to_first_enemy_in_room():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)

    message = handle_dev_kill(player, room)

    assert message == "[DEV] Killed Goblin."

def test_handle_dev_kill_with_no_enemies_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_kill(player, room)

    assert message == "[DEV] No enemy here to kill."

def test_handle_dev_kill_includes_loot_in_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)

    message = handle_dev_kill(player, room)

    assert message == "[DEV] Killed Goblin. Dropped: Bronze Xiphos."

def test_handle_dev_kill_with_no_loot_does_not_include_dropped_text():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)

    message = handle_dev_kill(player, room)

    assert "Dropped" not in message

def test_handle_dev_kill_grants_gold_reward_to_player():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, gold_reward=7)
    room.add_enemy(enemy)

    handle_dev_kill(player, room)

    assert player.gold == 7

def test_handle_dev_kill_grants_experience_reward_to_player():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, experience_reward=12)
    room.add_enemy(enemy)

    handle_dev_kill(player, room)

    assert player.experience == 12

def test_handle_dev_kill_clears_combat_state():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)
    player.in_combat = True
    player.current_target = enemy

    handle_dev_kill(player, room)

    assert player.in_combat is False
    assert player.current_target is None

def test_handle_dev_kill_moves_loot_into_room():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    room.add_enemy(enemy)

    handle_dev_kill(player, room)

    assert sword in room.items

def test_find_room_by_name_ci_returns_room_for_known_name():
    dungeon = Map()
    room = Room("Alpha")
    dungeon.add_room(room)
    found = find_room_by_name_ci(dungeon, "Alpha")
    assert found is room

def test_find_room_by_name_ci_is_case_insensitive():
    dungeon = Map()
    room = Room("Alpha")
    dungeon.add_room(room)
    found = find_room_by_name_ci(dungeon, "ALPHA")
    assert found is room

def test_find_room_by_name_ci_returns_none_for_unknown_name():
    dungeon = Map()
    found = find_room_by_name_ci(dungeon, "Nowhere")
    assert found is None

def test_handle_dev_remove_removes_enemy_from_room():
    room = Room("Arena")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room.add_enemy(enemy)

    message = handle_dev_remove("goblin", room)

    assert message == "[DEV] Removed Goblin."
    assert enemy not in room.enemies

def test_handle_dev_remove_removes_ally_from_room():
    room = Room("Arena")
    ally = Ally(name="Chiron")
    room.add_ally(ally)

    message = handle_dev_remove("chiron", room)

    assert message == "[DEV] Removed Chiron."
    assert ally not in room.allies

def test_handle_dev_remove_not_found_returns_message():
    room = Room("Arena")

    message = handle_dev_remove("nonexistent", room)

    assert message == "[DEV] No character named 'nonexistent' found here."

def test_handle_dev_remove_all_removes_every_matching_enemy():
    room = Room("Arena")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_enemy(Enemy(name="Other", hp=10, attack_damage=5))

    message = handle_dev_remove_all("goblin", room)

    assert message == "[DEV] Removed 2 instance(s) of 'goblin'."
    remaining_names = [enemy.name for enemy in room.enemies]
    assert remaining_names == ["Other"]

def test_handle_dev_remove_all_removes_matching_allies():
    room = Room("Arena")
    room.add_ally(Ally(name="Chiron"))
    room.add_ally(Ally(name="Chiron"))

    message = handle_dev_remove_all("chiron", room)

    assert message == "[DEV] Removed 2 instance(s) of 'chiron'."
    assert room.allies == []

def test_handle_dev_remove_all_not_found_returns_message():
    room = Room("Arena")

    message = handle_dev_remove_all("nonexistent", room)

    assert message == "[DEV] No character named 'nonexistent' found here."

def test_handle_dev_clear_room_removes_all_enemies_and_allies():
    room = Room("Arena")
    room.add_enemy(Enemy(name="Goblin", hp=10, attack_damage=5))
    room.add_ally(Ally(name="Chiron"))

    message = handle_dev_clear_room(room)

    assert message == "[DEV] Cleared room: removed 1 enemies and 1 allies."
    assert room.enemies == []
    assert room.allies == []

def test_handle_dev_clear_room_with_empty_room_returns_zero_counts():
    room = Room("Arena")

    message = handle_dev_clear_room(room)

    assert message == "[DEV] Cleared room: removed 0 enemies and 0 allies."

def test_find_companion_by_name_returns_companion_for_known_name():
    companion = find_companion_by_name("test companion")
    assert companion is not None
    assert companion.name == "Test Companion"

def test_find_companion_by_name_is_case_insensitive():
    companion = find_companion_by_name("TEST COMPANION")
    assert companion is not None
    assert companion.name == "Test Companion"

def test_find_companion_by_name_returns_none_for_unknown_name():
    companion = find_companion_by_name("nonexistent")
    assert companion is None

def test_find_companion_by_name_returns_new_instance_each_call():
    companion1 = find_companion_by_name("test companion")
    companion2 = find_companion_by_name("test companion")
    assert companion1 is not companion2

def test_find_spell_by_name_returns_spell_for_known_name():
    spell = find_spell_by_name("test bolt")
    assert spell is not None
    assert spell.name == "Test Bolt"

def test_find_spell_by_name_is_case_insensitive():
    spell = find_spell_by_name("TEST BOLT")
    assert spell is not None
    assert spell.name == "Test Bolt"

def test_find_spell_by_name_returns_none_for_unknown_name():
    spell = find_spell_by_name("nonexistent")
    assert spell is None

def test_find_spell_by_name_returns_new_instance_each_call():
    spell1 = find_spell_by_name("test bolt")
    spell2 = find_spell_by_name("test bolt")
    assert spell1 is not spell2

def test_handle_dev_afflict_applies_effect_to_player():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    handle_dev_afflict("player", "Poison", "-3", "4", player, room)

    assert len(player.active_effects) == 1
    assert player.active_effects[0].name == "Poison"
    assert player.active_effects[0].amount == -3
    assert player.active_effects[0].duration == 4

def test_handle_dev_afflict_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_afflict("player", "Poison", "-3", "4", player, room)

    assert message == "[DEV] hero is afflicted with Poison."

def test_handle_dev_afflict_applies_effect_to_companion():
    player = Player(name="hero", hp=100)
    home = Room("Camp")
    player.companion = Companion(name="Imp", hp=10, home_room=home)
    room = Room("Arena")

    handle_dev_afflict("companion", "Regen", "3", "5", player, room)

    assert len(player.companion.active_effects) == 1
    assert player.companion.active_effects[0].name == "Regen"

def test_handle_dev_afflict_with_no_companion_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_afflict("companion", "Regen", "3", "5", player, room)

    assert message == "[DEV] No companion to afflict."

def test_handle_dev_afflict_applies_effect_to_named_enemy_in_room():
    player = Player(name="hero", hp=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_dev_afflict("goblin", "Poison", "-3", "4", player, room)

    assert len(enemy.active_effects) == 1

def test_handle_dev_afflict_enemy_name_matching_is_case_insensitive():
    player = Player(name="hero", hp=100)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5)
    room = Room("Arena")
    room.add_enemy(enemy)

    handle_dev_afflict("GOBLIN", "Poison", "-3", "4", player, room)

    assert len(enemy.active_effects) == 1

def test_handle_dev_afflict_with_unknown_target_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_afflict("nonexistent", "Poison", "-3", "4", player, room)

    assert message == "[DEV] No character named 'nonexistent' found here."

def test_handle_dev_afflict_with_invalid_amount_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_afflict("player", "Poison", "abc", "4", player, room)

    assert message == "[DEV] amount and duration must be whole numbers."

def test_handle_dev_afflict_with_invalid_duration_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    message = handle_dev_afflict("player", "Poison", "-3", "xyz", player, room)

    assert message == "[DEV] amount and duration must be whole numbers."

def test_handle_dev_afflict_reapplication_prolongs_duration():
    """Reuses Character.apply_status_effect() directly, so the decided stacking rule (reapplication prolongs
    duration, doesn't stack a separate instance) applies exactly as it would in real play."""
    player = Player(name="hero", hp=100)
    room = Room("Arena")

    handle_dev_afflict("player", "Poison", "-3", "4", player, room)
    handle_dev_afflict("player", "Poison", "-3", "2", player, room)

    assert len(player.active_effects) == 1
    assert player.active_effects[0].duration == 6

def test_handle_dev_set_durability_with_invalid_slot_returns_message():
    player = Player(name="hero", hp=100)

    message = handle_dev_set_durability("shield", "5", player)

    assert message == "[DEV] Unknown slot 'shield' - use 'helmet' or 'body'."

def test_handle_dev_set_durability_with_no_armour_equipped_returns_message():
    player = Player(name="hero", hp=100)

    message = handle_dev_set_durability("body", "5", player)

    assert message == "[DEV] No armour equipped in the body slot."

def test_handle_dev_set_durability_with_invalid_value_returns_message():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    message = handle_dev_set_durability("body", "abc", player)

    assert message == "[DEV] Invalid value 'abc'."

def test_handle_dev_set_durability_sets_durability():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    handle_dev_set_durability("body", "4", player)

    assert armour.durability == 4

def test_handle_dev_set_durability_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    message = handle_dev_set_durability("body", "4", player)

    assert message == "[DEV] Shield durability set to 4/10."

def test_handle_dev_set_durability_clamps_value_above_max_durability():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    handle_dev_set_durability("body", "999", player)

    assert armour.durability == 10

def test_handle_dev_set_durability_clamps_negative_value_to_zero():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    handle_dev_set_durability("body", "-5", player)

    assert armour.durability == 0

def test_handle_dev_set_durability_breaking_backs_out_defence():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    handle_dev_set_durability("body", "0", player)

    assert player.armour == 0

def test_handle_dev_set_durability_restoring_from_broken_adds_back_defence():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)
    handle_dev_set_durability("body", "0", player)

    handle_dev_set_durability("body", "5", player)

    assert player.armour == 3

def test_handle_dev_set_durability_staying_nonzero_does_not_change_defence():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)

    handle_dev_set_durability("body", "5", player)

    assert player.armour == 3

def test_handle_dev_set_durability_works_on_helmet_slot():
    player = Player(name="hero", hp=100)
    helmet = Armour(name="Helm", description="", defence=2, slot="helmet", max_durability=8)
    helmet.use(player)

    handle_dev_set_durability("helmet", "3", player)

    assert helmet.durability == 3

def test_handle_dev_command_set_durability_dispatches_correctly():
    player = Player(name="hero", hp=100)
    armour = Armour(name="Shield", description="", defence=3, slot="body", max_durability=10)
    armour.use(player)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("set durability body 4", player, room, dungeon)

    assert armour.durability == 4
    assert message == "[DEV] Shield durability set to 4/10."
    assert new_room is None

def test_handle_dev_command_set_durability_with_missing_value_returns_usage_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("set durability body", player, room, dungeon)

    assert message == "[DEV] Usage: dev set durability <helmet|body> <value>"

def test_handle_dev_command_afflict_dispatches_correctly():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("afflict player poison -3 4", player, room, dungeon)

    assert len(player.active_effects) == 1
    assert new_room is None

def test_handle_dev_command_afflict_with_wrong_number_of_arguments_returns_usage_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("afflict player poison -3", player, room, dungeon)

    assert message == "[DEV] Usage: dev afflict <target> <effect> <amount> <duration> - effect name must be a single word."

def test_handle_dev_command_afflict_supports_multi_word_target_name():
    """Regression test for the fix: the last three tokens are always effect/amount/duration - everything
    before them, however many words, is the target name. 'Skeleton Warrior' previously split into two
    tokens and broke the old exact-count check."""
    player = Player(name="hero", hp=100)
    enemy = Enemy(name="Skeleton Warrior", hp=8, attack_damage=3)
    room = Room("Arena")
    room.add_enemy(enemy)
    dungeon = Map()

    message, new_room = handle_dev_command("afflict skeleton warrior poison -2 3", player, room, dungeon)

    assert message == "[DEV] Skeleton Warrior is afflicted with poison."
    assert len(enemy.active_effects) == 1
    assert enemy.active_effects[0].amount == -2
    assert enemy.active_effects[0].duration == 3

def test_handle_dev_command_afflict_unknown_multi_word_target_returns_full_name_in_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("afflict some unknown thing poison -3 4", player, room, dungeon)

    assert message == "[DEV] No character named 'some unknown thing' found here."

def test_handle_dev_command_grant_spell_with_unknown_spell_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("grant spell firebolt", player, room, dungeon)

    assert message == "[DEV] No known spell named 'firebolt'."

def test_handle_dev_command_grant_spell_adds_to_known_spells():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    handle_dev_command("grant spell test bolt", player, room, dungeon)

    spell_names = [spell.name for spell in player.known_spells]
    assert "Test Bolt" in spell_names

def test_handle_dev_command_grant_spell_returns_confirmation_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()

    message, new_room = handle_dev_command("grant spell test bolt", player, room, dungeon)

    assert message == "[DEV] Granted spell: Test Bolt."

def test_handle_dev_command_grant_spell_already_known_returns_message():
    player = Player(name="hero", hp=100)
    room = Room("Arena")
    dungeon = Map()
    handle_dev_command("grant spell test bolt", player, room, dungeon)

    message, new_room = handle_dev_command("grant spell test bolt", player, room, dungeon)

    assert message == "[DEV] Test Bolt is already known."
