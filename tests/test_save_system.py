import os

from dungeon_crawler.characters import Player, Enemy, Ally, Companion
from dungeon_crawler.world import Room, Map
from dungeon_crawler.dev_tools import ENEMY_REGISTRY
from dungeon_crawler.content import build_world, create_gorgon, create_medusa_awakened
from dungeon_crawler.combat import handle_enemy_defeat, resolve_pending_defeats
from dungeon_crawler.items import Weapon, Armour
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.spells import Spell
from dungeon_crawler.save_system import (
    slot_path, ensure_profile_dir, slot_exists, slot_summary,
    serialise_player, player_from_save_data,
    serialise_room, apply_room_data,
    serialise_world, apply_world_data,
    save_game, load_game, delete_save, delete_profile,
)

def base_player_data(**overrides) -> dict:
    """A complete, minimal-but-valid save dict for player_from_save_data() - every field player_from_save_data()
    reads must be present, so tests only override the field(s) they're actually about."""
    data = {
        "name": "Hero", "hp": 40, "max_hp": 50, "attack_damage": 8, "armour": 2, "intellect": 3,
        "level": 2, "experience": 10, "experience_to_next_level": 75, "gold": 20, "mana": 12,
        "ancestry_label": "Descendant of Zeus", "secondary_ancestry_label": "", "current_room": "Chamber",
        "visited_floors": [0, 1], "dodge_chance": 0.1, "ability_flags": {}, "skill_tree": {}, "skill_points": 0,
        "known_spells": [], "spell_cooldowns": {}, "active_effects": [], "inventory": [], "companion": None,
        "dev_mode": False,
    }
    data.update(overrides)
    return data

# ---- slot_path ----

def test_slot_path_returns_expected_format():
    assert slot_path(1, 3) == os.path.join("saves", "profile_1", "slot_3.json")

# ---- serialise_player ----

def test_serialise_player_includes_basic_stats():
    player = Player(name="Hero", hp=50, attack_damage=12, armour=3)
    player.intellect = 4
    player.level = 2
    player.experience = 10
    player.gold = 25
    player.mana = 15
    room = Room("Chamber")
    data = serialise_player(player, room)
    assert data["name"] == "Hero"
    assert data["hp"] == 50
    assert data["max_hp"] == 50
    assert data["attack_damage"] == 12
    assert data["armour"] == 3
    assert data["intellect"] == 4
    assert data["level"] == 2
    assert data["experience"] == 10
    assert data["gold"] == 25
    assert data["mana"] == 15

def test_serialise_player_includes_experience_to_next_level():
    player = Player(name="Hero", hp=50)
    player.experience_to_next_level = 253
    data = serialise_player(player, Room("Chamber"))
    assert data["experience_to_next_level"] == 253

def test_serialise_player_includes_ancestry_labels():
    player = Player(name="Hero", hp=50, ancestry_label="Descendant of Ares")
    player.secondary_ancestry_label = "Reckless Strength - heavy attacks never miss"
    data = serialise_player(player, Room("Chamber"))
    assert data["ancestry_label"] == "Descendant of Ares"
    assert data["secondary_ancestry_label"] == "Reckless Strength - heavy attacks never miss"

def test_serialise_player_includes_current_room_name():
    player = Player(name="Hero", hp=50)
    data = serialise_player(player, Room("Sunken Vault"))
    assert data["current_room"] == "Sunken Vault"

def test_serialise_player_includes_sorted_visited_floors():
    player = Player(name="Hero", hp=50)
    player.visited_floors = {3, 1, 2}
    data = serialise_player(player, Room("Chamber"))
    assert data["visited_floors"] == [1, 2, 3]

def test_serialise_player_includes_dodge_chance():
    player = Player(name="Hero", hp=50)
    player.dodge_chance = 0.35
    data = serialise_player(player, Room("Chamber"))
    assert data["dodge_chance"] == 0.35

def test_serialise_player_includes_dev_mode():
    player = Player(name="Hero", hp=50)
    player.dev_mode = True
    data = serialise_player(player, Room("Chamber"))
    assert data["dev_mode"] is True

def test_serialise_player_includes_ability_flags():
    player = Player(name="Hero", hp=50)
    player.has_double_strike = True
    player.has_iron_hide = True
    data = serialise_player(player, Room("Chamber"))
    assert data["ability_flags"]["has_double_strike"] is True
    assert data["ability_flags"]["has_iron_hide"] is True
    assert data["ability_flags"]["has_thorns"] is False

def test_serialise_player_includes_skill_tree_progress():
    player = Player(name="Hero", hp=50)
    player.skill_tree.skill_points = 2
    player.skill_tree.invest("defence", player)
    data = serialise_player(player, Room("Chamber"))
    assert data["skill_tree"]["defence"] == 1
    assert data["skill_points"] == 1

def test_serialise_player_includes_known_spells():
    player = Player(name="Hero", hp=50)
    player.known_spells.append(Spell(name="Firebolt", description="", mana_cost=5, damage=10))
    data = serialise_player(player, Room("Chamber"))
    assert data["known_spells"] == ["Firebolt"]

def test_serialise_player_includes_spell_cooldowns():
    player = Player(name="Hero", hp=50)
    player.spell_cooldowns["Firebolt"] = 1
    data = serialise_player(player, Room("Chamber"))
    assert data["spell_cooldowns"] == {"Firebolt": 1}

def test_serialise_player_includes_active_effects():
    player = Player(name="Hero", hp=50)
    player.apply_status_effect(StatusEffect("Poison", -3, 4))
    data = serialise_player(player, Room("Chamber"))
    assert data["active_effects"] == [{"name": "Poison", "amount": -3, "duration": 4}]

def test_serialise_player_includes_inventory_item_name_and_defaults():
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    data = serialise_player(player, Room("Chamber"))
    assert data["inventory"] == [{"name": "Bronze Xiphos", "equipped": False, "durability": None}]

def test_serialise_player_includes_equipped_flag_in_inventory():
    player = Player(name="Hero", hp=50)
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    player.inventory.add(sword)
    sword.use(player)
    data = serialise_player(player, Room("Chamber"))
    assert data["inventory"][0]["equipped"] is True

def test_serialise_player_includes_durability_for_armour_item():
    player = Player(name="Hero", hp=50)
    armour = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=10)
    armour.durability = 4
    player.inventory.add(armour)
    data = serialise_player(player, Room("Chamber"))
    assert data["inventory"][0]["durability"] == 4

def test_serialise_player_with_no_companion_returns_none():
    player = Player(name="Hero", hp=50)
    data = serialise_player(player, Room("Chamber"))
    assert data["companion"] is None

def test_serialise_player_with_companion_includes_name_and_hp():
    player = Player(name="Hero", hp=50)
    companion = Companion(name="Imp", hp=15, home_room=Room("Camp"))
    companion.hp = 10
    player.companion = companion
    data = serialise_player(player, Room("Chamber"))
    assert data["companion"] == {"name": "Imp", "hp": 10, "active_effects": []}

def test_serialise_player_with_companion_includes_active_effects():
    player = Player(name="Hero", hp=50)
    companion = Companion(name="Imp", hp=15, home_room=Room("Camp"))
    companion.apply_status_effect(StatusEffect("Poison", -2, 3))
    player.companion = companion
    data = serialise_player(player, Room("Chamber"))
    assert data["companion"]["active_effects"] == [{"name": "Poison", "amount": -2, "duration": 3}]

# ---- player_from_save_data ----

def test_player_from_save_data_reconstructs_basic_stats():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(), dungeon)
    assert player.name == "Hero"
    assert player.hp == 40
    assert player.max_hp == 50
    assert player.attack_damage == 8
    assert player.armour == 2
    assert player.intellect == 3
    assert player.level == 2
    assert player.experience == 10
    assert player.gold == 20
    assert player.mana == 12

def test_player_from_save_data_reconstructs_experience_to_next_level():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(experience_to_next_level=253), dungeon)
    assert player.experience_to_next_level == 253

def test_player_from_save_data_reconstructs_ancestry_labels():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(ancestry_label="Descendant of Ares", secondary_ancestry_label="Iron Hide - reduces every hit taken by 1")
    player, current_room = player_from_save_data(data, dungeon)
    assert player.ancestry_label == "Descendant of Ares"
    assert player.secondary_ancestry_label == "Iron Hide - reduces every hit taken by 1"

def test_player_from_save_data_reconstructs_visited_floors():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(visited_floors=[0, 2, 3]), dungeon)
    assert player.visited_floors == {0, 2, 3}

def test_player_from_save_data_reconstructs_dodge_chance():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(dodge_chance=0.35), dungeon)
    assert player.dodge_chance == 0.35

def test_player_from_save_data_reconstructs_dev_mode():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(dev_mode=True), dungeon)
    assert player.dev_mode is True

def test_player_from_save_data_reconstructs_ability_flags():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(ability_flags={"has_iron_hide": True, "has_double_strike": True})
    player, current_room = player_from_save_data(data, dungeon)
    assert player.has_iron_hide is True
    assert player.has_double_strike is True

def test_player_from_save_data_reconstructs_skill_tree_progress():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(skill_tree={"defence": 2}, skill_points=1)
    player, current_room = player_from_save_data(data, dungeon)
    assert player.skill_tree.paths["defence"].unlocked_count == 2
    assert player.skill_tree.skill_points == 1

def test_player_from_save_data_reconstructs_known_spells():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(known_spells=["Test Bolt"]), dungeon)
    assert len(player.known_spells) == 1
    assert player.known_spells[0].name == "Test Bolt"

def test_player_from_save_data_skips_unknown_spell_names():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(known_spells=["Nonexistent Spell"]), dungeon)
    assert player.known_spells == []

def test_player_from_save_data_reconstructs_spell_cooldowns():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(spell_cooldowns={"Test Bolt": 1})
    player, current_room = player_from_save_data(data, dungeon)
    assert player.spell_cooldowns == {"Test Bolt": 1}

def test_player_from_save_data_reconstructs_active_effects():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(active_effects=[{"name": "Poison", "amount": -3, "duration": 4}])
    player, current_room = player_from_save_data(data, dungeon)
    assert len(player.active_effects) == 1
    assert player.active_effects[0].name == "Poison"
    assert player.active_effects[0].amount == -3
    assert player.active_effects[0].duration == 4

def test_player_from_save_data_reconstructs_inventory_item():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(inventory=[{"name": "Bronze Xiphos", "equipped": False, "durability": None}])
    player, current_room = player_from_save_data(data, dungeon)
    assert any(item.name == "Bronze Xiphos" for item in player.inventory.items)

def test_player_from_save_data_reconstructs_equipped_item():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(inventory=[{"name": "Bronze Xiphos", "equipped": True, "durability": None}])
    player, current_room = player_from_save_data(data, dungeon)
    item = next(i for i in player.inventory.items if i.name == "Bronze Xiphos")
    assert item.equipped is True

def test_player_from_save_data_restores_armour_durability():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(inventory=[{"name": "Bronze Breastplate", "equipped": False, "durability": 3}])
    player, current_room = player_from_save_data(data, dungeon)
    item = next(i for i in player.inventory.items if i.name == "Bronze Breastplate")
    assert item.durability == 3

def test_player_from_save_data_skips_unknown_inventory_item_names():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(inventory=[{"name": "Nonexistent Item", "equipped": False, "durability": None}])
    player, current_room = player_from_save_data(data, dungeon)
    assert player.inventory.items == []

def test_player_from_save_data_with_no_companion_leaves_companion_none():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(companion=None), dungeon)
    assert player.companion is None

def test_player_from_save_data_reconstructs_companion():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(companion={"name": "Test Companion", "hp": 7, "active_effects": []})
    player, current_room = player_from_save_data(data, dungeon)
    assert player.companion is not None
    assert player.companion.name == "Test Companion"
    assert player.companion.hp == 7

def test_player_from_save_data_reconstructs_companion_active_effects():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(companion={
        "name": "Test Companion", "hp": 7, "active_effects": [{"name": "Poison", "amount": -2, "duration": 3}],
    })
    player, current_room = player_from_save_data(data, dungeon)
    assert player.companion is not None
    assert len(player.companion.active_effects) == 1
    assert player.companion.active_effects[0].name == "Poison"

def test_player_from_save_data_skips_unknown_companion_name():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(companion={"name": "Nonexistent Companion", "hp": 7})
    player, current_room = player_from_save_data(data, dungeon)
    assert player.companion is None

def test_player_from_save_data_returns_current_room():
    dungeon = Map()
    chamber = Room("Chamber")
    dungeon.add_room(chamber)
    player, current_room = player_from_save_data(base_player_data(current_room="Chamber"), dungeon)
    assert current_room is chamber

def test_player_from_save_data_raises_error_for_unknown_room():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(current_room="Nowhere")
    try:
        player_from_save_data(data, dungeon)
        assert False, "Expected a ValueError but none was raised"
    except ValueError:
        pass

# ---- serialise_room ----

def test_serialise_room_includes_living_enemies():
    room = Room("Chamber")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    room.add_enemy(enemy)
    data = serialise_room(room)
    assert data["enemies"] == [{"name": "Goblin", "hp": 10, "has_been_fled_from": False, "wave_gate": None}]

def test_serialise_room_excludes_dead_enemies():
    room = Room("Chamber")
    dead_enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    dead_enemy.hp = 0
    room.add_enemy(dead_enemy)
    data = serialise_room(room)
    assert data["enemies"] == []

def test_serialise_room_includes_has_been_fled_from():
    room = Room("Chamber")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    enemy.has_been_fled_from = True
    room.add_enemy(enemy)
    data = serialise_room(room)
    assert data["enemies"][0]["has_been_fled_from"] is True

def test_serialise_room_includes_item_names_and_durability():
    room = Room("Chamber")
    armour = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=10)
    armour.durability = 3
    room.add_item(armour)
    data = serialise_room(room)
    assert data["items"] == [{"name": "Bronze Breastplate", "durability": 3}]

def test_serialise_room_non_armour_item_has_none_durability():
    room = Room("Chamber")
    sword = Weapon(name="Bronze Xiphos", description="", damage=3)
    room.add_item(sword)
    data = serialise_room(room)
    assert data["items"] == [{"name": "Bronze Xiphos", "durability": None}]

def test_serialise_room_includes_completed_trade_ally_names():
    room = Room("Chamber")
    ally = Ally(name="Chiron")
    ally.trade_completed = True
    room.add_ally(ally)
    data = serialise_room(room)
    assert data["allies_traded"] == ["Chiron"]

def test_serialise_room_excludes_incomplete_trade_ally_names():
    room = Room("Chamber")
    ally = Ally(name="Chiron")
    room.add_ally(ally)
    data = serialise_room(room)
    assert data["allies_traded"] == []

def test_serialise_room_locked_exits_are_not_captured():
    """Known gap, not yet built (see roadmap.md/CLAUDE.md): unlocked_extras/locked_exits_removed are both
    unconditionally empty placeholders right now, regardless of the room's actual locked_exits state - don't
    treat this as a regression if it's ever touched, it's a deliberately deferred piece of the save/load design."""
    room = Room("Chamber")
    room.lock_exit("east", "Wooden Sword")
    data = serialise_room(room)
    assert data["unlocked_extras"] == []
    assert data["locked_exits_removed"] == []

def test_serialise_room_includes_fast_travel_locks():
    room = Room("Chamber")
    room.lock_fast_travel_exit("prayer room")
    room.lock_fast_travel_exit("stony lair")
    data = serialise_room(room)
    assert data["fast_travel_locks"] == ["prayer room", "stony lair"]

def test_serialise_room_with_no_fast_travel_locks_returns_empty_list():
    room = Room("Chamber")
    data = serialise_room(room)
    assert data["fast_travel_locks"] == []

# ---- apply_room_data ----

def test_apply_room_data_removes_enemy_not_in_save():
    room = Room("Chamber")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    room.add_enemy(enemy)
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": []})
    assert room.enemies == []

def test_apply_room_data_restores_surviving_enemy_hp():
    room = Room("Chamber")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    enemy.hp = 10
    room.add_enemy(enemy)
    data = {"enemies": [{"name": "Goblin", "hp": 4, "has_been_fled_from": True}], "items": [], "allies_traded": []}
    apply_room_data(room, data)
    assert enemy.hp == 4
    assert enemy.has_been_fled_from is True

def test_apply_room_data_replaces_room_items():
    room = Room("Chamber")
    old_item = Weapon(name="Old Sword", description="", damage=1)
    room.add_item(old_item)
    data = {"enemies": [], "items": [{"name": "Bronze Xiphos", "durability": None}], "allies_traded": []}
    apply_room_data(room, data)
    assert old_item not in room.items
    assert any(item.name == "Bronze Xiphos" for item in room.items)

def test_apply_room_data_restores_item_durability():
    room = Room("Chamber")
    data = {"enemies": [], "items": [{"name": "Bronze Breastplate", "durability": 3}], "allies_traded": []}
    apply_room_data(room, data)
    item = next(i for i in room.items if i.name == "Bronze Breastplate")
    assert item.durability == 3

def test_apply_room_data_marks_completed_trades():
    room = Room("Chamber")
    ally = Ally(name="Chiron")
    room.add_ally(ally)
    data = {"enemies": [], "items": [], "allies_traded": ["Chiron"]}
    apply_room_data(room, data)
    assert ally.trade_completed is True

def test_apply_room_data_leaves_incomplete_trades_alone():
    room = Room("Chamber")
    ally = Ally(name="Chiron")
    room.add_ally(ally)
    data = {"enemies": [], "items": [], "allies_traded": []}
    apply_room_data(room, data)
    assert ally.trade_completed is False

def test_apply_room_data_restores_fast_travel_locks():
    room = Room("Chamber")
    room.lock_fast_travel_exit("prayer room")
    data = {"enemies": [], "items": [], "allies_traded": [], "fast_travel_locks": []}
    apply_room_data(room, data)
    assert room.fast_travel_locks == set()

def test_apply_room_data_without_fast_travel_locks_key_leaves_existing_locks_unchanged():
    room = Room("Chamber")
    room.lock_fast_travel_exit("prayer room")
    data = {"enemies": [], "items": [], "allies_traded": []}
    apply_room_data(room, data)
    assert room.fast_travel_locks == {"prayer room"}

# ---- serialise_world / apply_world_data ----

def test_serialise_world_includes_every_room_keyed_by_name():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    dungeon.add_room(Room("Hallway"))
    data = serialise_world(dungeon)
    assert set(data.keys()) == {"Chamber", "Hallway"}

def test_apply_world_data_patches_matching_rooms():
    dungeon = Map()
    room = Room("Chamber")
    enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    room.add_enemy(enemy)
    dungeon.add_room(room)
    data = {"Chamber": {"enemies": [], "items": [], "allies_traded": []}}
    apply_world_data(dungeon, data)
    assert room.enemies == []

def test_apply_world_data_ignores_unknown_room_names():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = {"Nowhere": {"enemies": [], "items": [], "allies_traded": []}}
    apply_world_data(dungeon, data)  # must not raise

# ---- file I/O: ensure_profile_dir, slot_exists, slot_summary, save_game, load_game, delete_save, delete_profile ----

def test_ensure_profile_dir_creates_directory(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    path = ensure_profile_dir(1)
    assert os.path.isdir(path)

def test_ensure_profile_dir_is_safe_to_call_twice(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    ensure_profile_dir(1)
    path = ensure_profile_dir(1)  # must not raise
    assert os.path.isdir(path)

def test_slot_exists_is_false_for_empty_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    assert slot_exists(1, 1) is False

def test_slot_exists_is_true_after_save_game(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    player = Player(name="Hero", hp=50)
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_game(1, 1, player, room, dungeon)
    assert slot_exists(1, 1) is True

def test_slot_summary_returns_none_for_empty_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    assert slot_summary(1, 1) is None

def test_slot_summary_formats_saved_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    player = Player(name="Hero", hp=50, ancestry_label="Descendant of Ares")
    player.level = 3
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_game(1, 1, player, room, dungeon)
    assert slot_summary(1, 1) == "Hero - LVL 3 Descendant of Ares - Chamber"

def test_save_game_then_load_game_restores_player_name(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    player = Player(name="Hero", hp=50)
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_game(1, 1, player, room, dungeon)
    reloaded_player, reloaded_room = load_game(1, 1, dungeon)
    assert reloaded_player.name == "Hero"
    assert reloaded_room is room

def test_save_game_then_load_game_removes_defeated_enemy_from_fresh_world(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    player = Player(name="Hero", hp=50)
    dungeon = Map()
    room = Room("Chamber")  # enemy already defeated - room starts empty
    dungeon.add_room(room)
    save_game(1, 1, player, room, dungeon)

    fresh_dungeon = Map()
    fresh_room = Room("Chamber")
    fresh_enemy = Enemy(name="Goblin", hp=10, attack_damage=3)
    fresh_room.add_enemy(fresh_enemy)
    fresh_dungeon.add_room(fresh_room)

    load_game(1, 1, fresh_dungeon)
    assert fresh_room.enemies == []

def test_save_game_overwrites_existing_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_game(1, 1, Player(name="First", hp=50), room, dungeon)
    save_game(1, 1, Player(name="Second", hp=50), room, dungeon)
    reloaded_player, reloaded_room = load_game(1, 1, dungeon)
    assert reloaded_player.name == "Second"

def test_load_game_raises_file_not_found_for_empty_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    try:
        load_game(1, 1, dungeon)
        assert False, "Expected a FileNotFoundError but none was raised"
    except FileNotFoundError:
        pass

def test_delete_save_returns_false_when_nothing_to_delete(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    assert delete_save(1, 1) is False

def test_delete_save_returns_true_and_removes_file(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_game(1, 1, Player(name="Hero", hp=50), room, dungeon)
    result = delete_save(1, 1)
    assert result is True
    assert slot_exists(1, 1) is False

def test_delete_profile_returns_false_when_profile_does_not_exist(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    assert delete_profile(1) is False

def test_delete_profile_returns_true_for_existing_profile_with_no_slots(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    ensure_profile_dir(1)
    assert delete_profile(1) is True

def test_delete_profile_removes_every_slot(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    save_game(1, 1, Player(name="Hero", hp=50), room, dungeon)
    save_game(1, 2, Player(name="Hero", hp=50), room, dungeon)
    result = delete_profile(1)
    assert result is True
    assert slot_exists(1, 1) is False
    assert slot_exists(1, 2) is False

def test_serialise_player_includes_auto_map():
    player = Player(name="Hero", hp=50)
    player.auto_map = True
    data = serialise_player(player, Room("Chamber"))
    assert data["auto_map"] is True

def test_serialise_player_includes_sorted_visited_rooms():
    player = Player(name="Hero", hp=50)
    player.visited_rooms = {"Styx Crossing", "Cave Entrance"}
    data = serialise_player(player, Room("Chamber"))
    assert data["visited_rooms"] == ["Cave Entrance", "Styx Crossing"]

def test_player_from_save_data_reconstructs_auto_map():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(auto_map=True), dungeon)
    assert player.auto_map is True

def test_player_from_save_data_reconstructs_visited_rooms():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(visited_rooms=["Cave Entrance", "Chamber"]), dungeon)
    assert player.visited_rooms == {"Cave Entrance", "Chamber"}

def test_player_from_save_data_defaults_auto_map_and_visited_rooms_for_older_saves():
    """Saves written before these fields existed have neither key - loading must not crash, and falls back to the defaults."""
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(), dungeon)
    assert player.auto_map is False
    assert player.visited_rooms == set()

def test_serialise_player_includes_sorted_seen_hints():
    player = Player(name="Hero", hp=50)
    player.seen_hints = {"forge", "combat"}
    data = serialise_player(player, Room("Chamber"))
    assert data["seen_hints"] == ["combat", "forge"]

def test_player_from_save_data_reconstructs_seen_hints():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(seen_hints=["combat", "forge"]), dungeon)
    assert player.seen_hints == {"combat", "forge"}

def test_player_from_save_data_defaults_seen_hints_for_older_saves():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, current_room = player_from_save_data(base_player_data(), dungeon)
    assert player.seen_hints == set()

# ---- enemies spawned mid-fight survive a save/load ----

def test_serialise_room_records_a_wave_adds_gate_by_the_next_phases_name():
    room = Room("Lair of Medusa")
    gorgon = create_gorgon()
    gorgon.wave_gate_factory = create_medusa_awakened
    room.add_enemy(gorgon)
    data = serialise_room(room)
    assert data["enemies"][0]["wave_gate"] == "Medusa (Awakened)"

def test_apply_room_data_rebuilds_a_saved_enemy_the_fresh_room_does_not_have():
    """A wave add or later boss phase isn't part of a freshly built room - it's rebuilt from ENEMY_REGISTRY."""
    room = Room("Lair of Medusa")
    data = {"enemies": [{"name": "Gorgon", "hp": 4, "has_been_fled_from": True}], "items": [], "allies_traded": []}

    apply_room_data(room, data)

    assert len(room.enemies) == 1
    gorgon = room.enemies[0]
    assert gorgon.name == "Gorgon"
    assert gorgon.hp == 4
    assert gorgon.has_been_fled_from is True

def test_apply_room_data_skips_a_saved_enemy_nobody_can_rebuild():
    """Not in the fresh room and not in ENEMY_REGISTRY (e.g. the dev test boss's lambda-built adds) - skipped, not a crash."""
    room = Room("Arena")
    data = {"enemies": [{"name": "Test Add", "hp": 1, "has_been_fled_from": False}], "items": [], "allies_traded": []}
    apply_room_data(room, data)
    assert room.enemies == []

def test_apply_room_data_keeps_the_fresh_rooms_own_instance_for_an_unregistered_enemy():
    """The Practice Chamber's dummy isn't in ENEMY_REGISTRY - claiming the fresh room's instance is what keeps it across a reload."""
    room = Room("Practice Chamber")
    dummy = Enemy(name="Practice Enemy", hp=20, respawns=True)
    room.add_enemy(dummy)
    data = {"enemies": [{"name": "Practice Enemy", "hp": 20, "has_been_fled_from": False}], "items": [], "allies_traded": []}

    apply_room_data(room, data)

    assert room.enemies == [dummy]

def test_apply_room_data_gives_same_named_enemies_their_own_saved_hp():
    """Enemies are matched by name in order, not by name alone - two Gorgons no longer collide on reload."""
    room = Room("Lair of Medusa")
    first = create_gorgon()
    second = create_gorgon()
    room.add_enemy(first)
    room.add_enemy(second)
    data = {"enemies": [{"name": "Gorgon", "hp": 4, "has_been_fled_from": False},
                        {"name": "Gorgon", "hp": 9, "has_been_fled_from": False}], "items": [], "allies_traded": []}

    apply_room_data(room, data)

    assert first.hp == 4
    assert second.hp == 9

def test_apply_room_data_removes_only_the_fresh_enemies_nobody_claimed():
    room = Room("Lair of Medusa")
    kept = create_gorgon()
    defeated = create_gorgon()
    room.add_enemy(kept)
    room.add_enemy(defeated)
    data = {"enemies": [{"name": "Gorgon", "hp": 6, "has_been_fled_from": False}], "items": [], "allies_traded": []}

    apply_room_data(room, data)

    assert room.enemies == [kept]

def test_apply_room_data_relinks_a_wave_gate_to_its_registry_factory():
    room = Room("Lair of Medusa")
    data = {"enemies": [{"name": "Gorgon", "hp": 12, "has_been_fled_from": False, "wave_gate": "Medusa (Awakened)"}],
            "items": [], "allies_traded": []}

    apply_room_data(room, data)

    assert room.enemies[0].wave_gate_factory is ENEMY_REGISTRY["medusa (awakened)"]

def test_apply_room_data_reloaded_wave_siblings_share_one_gate_factory():
    """handle_enemy_defeat() groups siblings by factory identity (is, not ==) - reloaded adds must still count as one wave."""
    room = Room("Lair of Medusa")
    entry = {"name": "Gorgon", "hp": 12, "has_been_fled_from": False, "wave_gate": "Medusa (Awakened)"}
    apply_room_data(room, {"enemies": [dict(entry), dict(entry)], "items": [], "allies_traded": []})
    first, second = room.enemies
    assert first.wave_gate_factory is second.wave_gate_factory

def test_apply_room_data_without_wave_gate_key_leaves_no_gate_for_older_saves():
    room = Room("Arena")
    room.add_enemy(Enemy(name="Goblin", hp=10))
    apply_room_data(room, {"enemies": [{"name": "Goblin", "hp": 10, "has_been_fled_from": False}], "items": [], "allies_traded": []})
    assert room.enemies[0].wave_gate_factory is None

def test_world_round_trip_mid_medusa_wave_keeps_the_gorgons_the_guard_and_the_next_phase():
    """Regression: saving after fleeing partway through the Medusa chain used to reload the Lair empty - the Gorgons, Medusa (Awakened),
    Serpent's Kiss and the guard on 'descend' were all lost, letting the player skip the boss entirely."""
    dungeon, _, _ = build_world()
    lair = dungeon.get_room("Lair of Medusa")
    assert lair is not None
    player = Player(name="Hero", hp=50)
    medusa = lair.enemies[0]
    medusa.hp = 0
    handle_enemy_defeat(lair, medusa, player)  # Phase 1 falls, two Gorgons spawn
    lair.enemies[0].hp = 4

    fresh, _, _ = build_world()
    apply_world_data(fresh, serialise_world(dungeon))
    reloaded = fresh.get_room("Lair of Medusa")
    assert reloaded is not None

    assert [(e.name, e.hp) for e in reloaded.enemies] == [("Gorgon", 4), ("Gorgon", 12)]
    assert "descend" in reloaded.guarded_exits
    for gorgon in reloaded.enemies:
        gorgon.hp = 0
    resolve_pending_defeats(player, reloaded)
    assert [e.name for e in reloaded.enemies] == ["Medusa (Awakened)"]
