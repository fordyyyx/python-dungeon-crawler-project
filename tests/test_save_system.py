import json
import os

from dungeon_crawler.characters import Player, Enemy, Ally, Companion
from dungeon_crawler.world import Room, Map
from dungeon_crawler.character_creation import create_player
from dungeon_crawler.dev_tools import ENEMY_REGISTRY
from dungeon_crawler.content import build_world, create_penelopes_thread, create_odysseus, create_poseidon, create_charybdis, create_polyphemus_blinded, create_antiphates_club, create_cyclops_eye, create_shade_of_achilles, create_gorgon, create_medusa_awakened
from dungeon_crawler.combat import handle_enemy_defeat, resolve_pending_defeats
from dungeon_crawler.items import Weapon, Armour
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.spells import Spell
from dungeon_crawler.exceptions import SaveFileError, ActionRefused
from dungeon_crawler.save_system import (
    slot_path, ensure_profile_dir, slot_exists, slot_summary,
    serialise_player, player_from_save_data, serialise_companion, companion_from_save_data,
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
    assert data["base_armour"] == 3
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
    assert data["active_effects"] == [{"name": "Poison", "amount": -3, "duration": 4, "miss_chance": 0.0}]

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
    assert data["companion"] == {"name": "Imp", "hp": 10, "level": 1, "experience": 0, "duel_won": False, "home_room": "Camp", "active_effects": []}

def test_serialise_player_with_companion_includes_active_effects():
    player = Player(name="Hero", hp=50)
    companion = Companion(name="Imp", hp=15, home_room=Room("Camp"))
    companion.apply_status_effect(StatusEffect("Poison", -2, 3))
    player.companion = companion
    data = serialise_player(player, Room("Chamber"))
    assert data["companion"]["active_effects"] == [{"name": "Poison", "amount": -2, "duration": 3, "miss_chance": 0.0}]

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
    """unlocked_extras/locked_exits_removed are still unconditionally empty placeholders, whatever the room's locks - the real lock
    state now travels under "locked_exits" instead (see test_serialise_room_includes_locked_exits)."""
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
    """An enemy ENEMY_REGISTRY doesn't know by its own name - claiming the fresh room's instance is what keeps it across a reload."""
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

def test_serialise_player_base_armour_leaves_out_worn_gear():
    player = Player(name="Hero", hp=50, armour=1)
    plate = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=8)
    player.inventory.add(plate)
    plate.use(player)
    data = serialise_player(player, Room("Chamber"))
    assert data["base_armour"] == 1

def test_player_from_save_data_restores_base_armour():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(base_armour=4)
    player, _ = player_from_save_data(data, dungeon)
    assert player.base_armour == 4

def test_player_round_trip_with_worn_armour_does_not_grow_armour():
    """Regression: the saved total already included worn pieces, and re-equipping them on load added them again - every reload
    raised armour by the worn pieces' defence."""
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    player = Player(name="Hero", hp=20, armour=1)
    plate = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=8)
    player.inventory.add(plate)
    plate.use(player)
    for _ in range(3):
        player, room = player_from_save_data(serialise_player(player, room), dungeon)
    assert player.armour == 3

def test_player_round_trip_with_broken_worn_armour_keeps_it_broken():
    dungeon = Map()
    room = Room("Chamber")
    dungeon.add_room(room)
    player = Player(name="Hero", hp=20, armour=1)
    plate = Armour(name="Bronze Breastplate", description="", defence=2, max_durability=8)
    player.inventory.add(plate)
    plate.use(player)
    plate.durability = 0
    loaded, _ = player_from_save_data(serialise_player(player, room), dungeon)
    assert loaded.armour == 1

def test_player_from_save_data_older_total_armour_save_is_not_double_counted():
    """An older save stored total armour (worn pieces included) and no base_armour - loading it must land on the same total."""
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(armour=4, inventory=[{"name": "Bronze Breastplate", "equipped": True, "durability": 8}])
    player, _ = player_from_save_data(data, dungeon)
    assert player.armour == 4
    assert player.base_armour == 2

def test_serialise_room_includes_locked_exits():
    room = Room("Chamber")
    room.lock_exit("east", "Wooden Sword")
    room.lock_exit("south", "Wooden Shield")
    data = serialise_room(room)
    assert data["locked_exits"] == ["east", "south"]

def test_apply_room_data_unlocks_exits_the_save_had_unlocked():
    room = Room("Chamber")
    room.lock_exit("east", "Wooden Sword")
    room.lock_exit("south", "Wooden Shield")
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": [], "locked_exits": ["south"]})
    assert "east" not in room.locked_exits
    assert room.locked_exits["south"] == "Wooden Shield"

def test_apply_room_data_without_locked_exits_leaves_locks_alone():
    """An older save has no "locked_exits" key at all - every lock build_world() made stays in place."""
    room = Room("Chamber")
    room.lock_exit("east", "Wooden Sword")
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": []})
    assert room.locked_exits["east"] == "Wooden Sword"

# ---- companions: serialise_companion / companion_from_save_data ----

def test_serialise_companion_saves_level_and_experience_not_stats():
    companion = Companion(name="Imp", hp=15, home_room=Room("Camp"))
    companion.restore_level(3, 8)
    data = serialise_companion(companion)
    assert data["level"] == 3
    assert data["experience"] == 8
    assert "max_hp" not in data
    assert "attack_damage" not in data

def test_serialise_companion_saves_the_home_room_by_name_so_it_is_json_safe():
    """Regression: the Room object itself used to be stored, so every save crashed - the floor 5 camp always holds a companion."""
    companion = Companion(name="Imp", hp=15, home_room=Room("Camp"))
    data = serialise_companion(companion)
    assert data["home_room"] == "Camp"
    assert json.loads(json.dumps(data)) == data

def test_serialise_companion_saves_whether_the_duel_is_won():
    companion = Companion(name="Imp", hp=15, home_room=Room("Camp"))
    companion.duel_won = True
    assert serialise_companion(companion)["duel_won"] is True

def test_companion_from_save_data_rebuilds_a_registered_companion():
    """Regression: the rebuilt companion was never returned, so every loaded companion vanished."""
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 30}, None)
    assert companion is not None
    assert companion.name == "Shade of Achilles"

def test_companion_from_save_data_with_an_unknown_name_returns_none():
    assert companion_from_save_data({"name": "Nobody", "hp": 5}, None) is None

def test_companion_from_save_data_replays_the_saved_level():
    """Regression: restore_level() referenced _level_up without calling it, so a reloaded companion was always level 1."""
    fresh = create_shade_of_achilles()
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 30, "level": 3, "experience": 4}, None)
    assert companion.level == 3
    assert companion.experience == 4
    assert companion.max_hp > fresh.max_hp
    assert companion.attack_damage > fresh.attack_damage

def test_companion_from_save_data_keeps_saved_hp_that_only_a_higher_level_allows():
    fresh_max = create_shade_of_achilles().max_hp
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": fresh_max + 2, "level": 2}, None)
    assert companion.hp == fresh_max + 2

def test_companion_from_save_data_clamps_hp_to_max_hp():
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 999}, None)
    assert companion.hp == companion.max_hp

def test_companion_from_save_data_restores_the_duel_as_won():
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 30, "duel_won": True}, None)
    assert companion.duel_won is True
    assert companion.requires_duel is False

def test_companion_from_save_data_older_save_defaults_to_level_one_and_no_duel_won():
    """An older save only had name, hp and active_effects."""
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 30, "active_effects": []}, None)
    assert companion.level == 1
    assert companion.duel_won is False

def test_companion_from_save_data_relinks_the_given_home_room():
    camp = Room("Shadow of Army Camp")
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 30}, camp)
    assert companion.home_room is camp

def test_companion_from_save_data_without_a_home_room_keeps_the_factory_default():
    companion = companion_from_save_data({"name": "Shade of Achilles", "hp": 30}, None)
    assert companion.home_room.name == "Shadow of Army Camp"

def test_player_from_save_data_relinks_the_companions_home_room_from_the_world():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    camp = Room("Shadow of Army Camp")
    dungeon.add_room(camp)
    data = base_player_data(companion={"name": "Shade of Achilles", "hp": 30, "home_room": "Shadow of Army Camp", "active_effects": []})
    player, _ = player_from_save_data(data, dungeon)
    assert player.companion is not None
    assert player.companion.home_room is camp

# ---- companions in rooms ----

def test_serialise_room_includes_its_companions():
    room = Room("Camp")
    room.add_companion(Companion(name="Imp", hp=15, home_room=room))
    data = serialise_room(room)
    assert [c["name"] for c in data["companions"]] == ["Imp"]

def test_apply_room_data_restores_a_companions_won_duel():
    room = Room("Shadow of Army Camp")
    room.add_companion(create_shade_of_achilles(room))
    data = {"enemies": [], "items": [], "allies_traded": [],
            "companions": [{"name": "Shade of Achilles", "hp": 30, "duel_won": True, "home_room": "Shadow of Army Camp", "active_effects": []}]}
    apply_room_data(room, data)
    assert len(room.companions) == 1
    assert room.companions[0].duel_won is True
    assert room.companions[0].home_room is room

def test_apply_room_data_with_no_saved_companions_removes_a_recruited_one():
    room = Room("Shadow of Army Camp")
    room.add_companion(create_shade_of_achilles(room))
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": [], "companions": []})
    assert room.companions == []

def test_apply_room_data_older_save_without_companions_leaves_them_alone():
    room = Room("Shadow of Army Camp")
    achilles = create_shade_of_achilles(room)
    room.add_companion(achilles)
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": []})
    assert room.companions == [achilles]

def test_apply_room_data_skips_a_saved_item_nobody_can_rebuild():
    room = Room("Chamber")
    apply_room_data(room, {"enemies": [], "items": [{"name": "Mystery Box", "durability": None}], "allies_traded": []})
    assert room.items == []

def test_world_round_trip_keeps_a_won_duel_in_the_camp():
    dungeon, _, all_floors = build_world()
    camp = all_floors["floor_5"]["Shadow of Army Camp"]
    camp.companions[0].duel_won = True
    data = json.loads(json.dumps(serialise_world(dungeon)))
    fresh, _, fresh_floors = build_world()
    apply_world_data(fresh, data)
    fresh_camp = fresh_floors["floor_5"]["Shadow of Army Camp"]
    assert [c.name for c in fresh_camp.companions] == ["Shade of Achilles"]
    assert fresh_camp.companions[0].duel_won is True

def test_world_round_trip_with_the_companion_recruited_leaves_the_camp_empty():
    dungeon, _, all_floors = build_world()
    camp = all_floors["floor_5"]["Shadow of Army Camp"]
    camp.remove_companion(camp.companions[0])
    data = json.loads(json.dumps(serialise_world(dungeon)))
    fresh, _, fresh_floors = build_world()
    apply_world_data(fresh, data)
    assert fresh_floors["floor_5"]["Shadow of Army Camp"].companions == []

# ---- ancestry keys and seen_lines ----

def test_serialise_player_includes_ancestry_keys_and_seen_lines():
    player = Player(name="Hero", hp=20)
    player.ancestry_key = "athena"
    player.secondary_ancestry_key = "medusa"
    player.seen_lines = {"ancestry:Athena:athena"}
    data = serialise_player(player, Room("Chamber"))
    assert data["ancestry_key"] == "athena"
    assert data["secondary_ancestry_key"] == "medusa"
    assert data["seen_lines"] == ["ancestry:Athena:athena"]

def test_player_from_save_data_restores_ancestry_keys_and_seen_lines():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    data = base_player_data(ancestry_key="athena", secondary_ancestry_key="medusa", seen_lines=["ancestry:Athena:athena"])
    player, _ = player_from_save_data(data, dungeon)
    assert player.ancestry_key == "athena"
    assert player.secondary_ancestry_key == "medusa"
    assert player.seen_lines == {"ancestry:Athena:athena"}

def test_player_from_save_data_older_save_recovers_both_ancestry_keys():
    """Regression: the secondary key was looked up by ancestry name, but secondary_ancestry_label holds the ability's description, so
    it never matched and an older save reloaded with no secondary key."""
    dungeon, start, _ = build_world()
    data = serialise_player(create_player("Hero", "athena", "medusa"), start)
    del data["ancestry_key"]
    del data["secondary_ancestry_key"]
    player, _ = player_from_save_data(data, dungeon)
    assert player.ancestry_key == "athena"
    assert player.secondary_ancestry_key == "medusa"

def test_player_from_save_data_with_no_secondary_gift_leaves_the_secondary_key_unset():
    """Also a regression: the recovery lookup used to crash with KeyError whenever it ran, including for this common case."""
    dungeon, start, _ = build_world()
    data = serialise_player(create_player("Hero", "athena", "basic"), start)
    player, _ = player_from_save_data(data, dungeon)
    assert player.secondary_ancestry_key is None

def test_player_from_save_data_older_save_without_seen_lines_starts_empty():
    dungeon = Map()
    dungeon.add_room(Room("Chamber"))
    player, _ = player_from_save_data(base_player_data(), dungeon)
    assert player.seen_lines == set()

def test_serialise_room_includes_its_flags_sorted():
    room = Room("Shore")
    room.flags = {"b_flag", "a_flag"}
    assert serialise_room(room)["flags"] == ["a_flag", "b_flag"]

def test_serialise_room_with_no_flags_returns_empty_list():
    assert serialise_room(Room("Shore"))["flags"] == []

def test_apply_room_data_restores_flags():
    room = Room("Shore")
    data = {"enemies": [], "items": [], "allies_traded": [], "flags": ["sirens_bargain_taken"]}
    apply_room_data(room, data)
    assert room.flags == {"sirens_bargain_taken"}

def test_apply_room_data_without_flags_key_leaves_flags_alone():
    """Older saves have no 'flags' key - a fresh room's (empty) flags stay as they are."""
    room = Room("Shore")
    data = {"enemies": [], "items": [], "allies_traded": []}
    apply_room_data(room, data)
    assert room.flags == set()

def test_save_game_then_load_game_keeps_the_sirens_bargain_taken(monkeypatch, tmp_path):
    """A taken bargain is permanent - reloading must not reopen the offer for a second helping of skill points."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, entrance, floors = build_world()
    calm_waters = floors["floor_6"]["Calm Waters"]
    player = Player(name="Hero", hp=20)
    calm_waters.interactions["give in"].handler(player, calm_waters)
    save_game(1, 1, player, calm_waters, dungeon)

    fresh_dungeon, _, fresh_floors = build_world()
    reloaded_player, reloaded_room = load_game(1, 1, fresh_dungeon)

    assert reloaded_room is fresh_floors["floor_6"]["Calm Waters"]
    assert reloaded_room.available_interactions(reloaded_player) == []
    assert reloaded_player.max_hp == 15
    assert reloaded_player.skill_tree.skill_points == 2

def test_player_from_save_data_keeps_antiphates_club():
    """Regression: the club's misspelt name didn't match its registry key, so every reload silently dropped it from the inventory."""
    dungeon, start, floors = build_world()
    player = Player(name="Hero", hp=20)
    player.inventory.add(create_antiphates_club())
    reloaded, _ = player_from_save_data(serialise_player(player, start), dungeon)
    assert [item.name for item in reloaded.inventory.items] == ["Antiphates' Club"]

def test_player_from_save_data_keeps_the_cyclops_eye():
    """Regression: the registry key was "cyclops eye", so a reload dropped Ares' only trade item - and the Cyclops is its only source."""
    dungeon, start, floors = build_world()
    player = Player(name="Hero", hp=20)
    player.inventory.add(create_cyclops_eye())
    reloaded, _ = player_from_save_data(serialise_player(player, start), dungeon)
    assert [item.name for item in reloaded.inventory.items] == ["Cyclops' Eye"]

def test_serialise_player_includes_an_effects_miss_chance():
    player = Player(name="Hero", hp=20)
    player.apply_status_effect(StatusEffect("Blinded", 0, 2, miss_chance=0.3))
    assert serialise_player(player, Room("Chamber"))["active_effects"] == [{"name": "Blinded", "amount": 0, "duration": 2, "miss_chance": 0.3}]

def test_player_from_save_data_restores_an_effects_miss_chance():
    dungeon, start, floors = build_world()
    player = Player(name="Hero", hp=20)
    player.apply_status_effect(StatusEffect("Blinded", 0, 2, miss_chance=0.3))
    reloaded, _ = player_from_save_data(serialise_player(player, start), dungeon)
    assert reloaded.active_effects[0].miss_chance == 0.3
    assert reloaded.get_miss_chance("light") == 0.3

def test_player_from_save_data_older_effect_without_miss_chance_defaults_to_zero():
    dungeon, start, floors = build_world()
    data = serialise_player(Player(name="Hero", hp=20), start)
    data["active_effects"] = [{"name": "Poison", "amount": -3, "duration": 4}]
    reloaded, _ = player_from_save_data(data, dungeon)
    assert reloaded.active_effects[0].miss_chance == 0.0

def test_companion_round_trip_keeps_an_effects_miss_chance():
    companion = create_shade_of_achilles()
    companion.apply_status_effect(StatusEffect("Blinded", 0, 2, miss_chance=0.3))
    reloaded = companion_from_save_data(serialise_companion(companion), None)
    assert reloaded.active_effects[0].miss_chance == 0.3

def test_companion_from_save_data_older_effect_without_miss_chance_defaults_to_zero():
    data = serialise_companion(create_shade_of_achilles())
    data["active_effects"] = [{"name": "Poison", "amount": -2, "duration": 3}]
    assert companion_from_save_data(data, None).active_effects[0].miss_chance == 0.0

def test_apply_room_data_rebuilds_polyphemus_blinded_still_blinded():
    """Mid-fight, only phase 2 is left - a reload rebuilds it from ENEMY_REGISTRY, and its factory is what makes it blind again."""
    dungeon, start, floors = build_world()
    cavern = floors["floor_6"]["Cavern of Polyphemus"]
    source = Room("Cavern of Polyphemus")
    blinded = create_polyphemus_blinded()
    blinded.hp = 20
    source.add_enemy(blinded)
    apply_room_data(cavern, serialise_room(source))
    assert [e.name for e in cavern.enemies] == ["Polyphemus (Blinded)"]
    assert cavern.enemies[0].hp == 20
    assert cavern.enemies[0].get_miss_chance("light") == 0.35

def test_apply_room_data_keeps_an_unsolved_charybdis_guarding_the_river():
    dungeon, start, floors = build_world()
    river = floors["floor_6"]["Narrow River"]
    source = Room("Narrow River")
    source.add_enemy(create_charybdis())
    apply_room_data(river, serialise_room(source))
    assert [e.name for e in river.enemies] == ["Charybdis"]
    assert river.enemies[0].invulnerable is True

def test_apply_room_data_a_solved_charybdis_stays_solved():
    dungeon, start, floors = build_world()
    river = floors["floor_6"]["Narrow River"]
    apply_room_data(river, serialise_room(Room("Narrow River")))
    assert river.enemies == []
    assert river.available_interactions(Player(name="Hero", hp=20)) == []

def test_serialise_room_never_saves_transient_state():
    room = Room("Narrow River")
    room.transient_state["charybdis"] = {"phase": 2, "position": "tree", "freed": False}
    assert "transient_state" not in serialise_room(room)
    assert all("charybdis" not in str(value) for value in serialise_room(room).values())

def test_serialise_player_includes_story_flags_sorted():
    player = Player(name="Hero", hp=20)
    player.story_flags = {"b_flag", "a_flag"}
    assert serialise_player(player, Room("Chamber"))["story_flags"] == ["a_flag", "b_flag"]

def test_player_from_save_data_restores_story_flags():
    dungeon, start, floors = build_world()
    player = Player(name="Hero", hp=20)
    player.story_flags.add("suitors_cleared")
    reloaded, _ = player_from_save_data(serialise_player(player, start), dungeon)
    assert reloaded.story_flags == {"suitors_cleared"}

def test_player_from_save_data_older_save_without_story_flags_starts_with_none():
    dungeon, start, floors = build_world()
    data = serialise_player(Player(name="Hero", hp=20), start)
    del data["story_flags"]
    reloaded, _ = player_from_save_data(data, dungeon)
    assert reloaded.story_flags == set()

def test_companion_round_trip_keeps_odysseus_ranged_and_advising():
    odysseus = create_odysseus()
    reloaded = companion_from_save_data(serialise_companion(odysseus), None)
    assert reloaded.name == "Odysseus"
    assert reloaded.attack_type == "ranged"
    assert reloaded.gives_advice is True
    assert reloaded.required_story_flag == "suitors_cleared"

def test_apply_room_data_rebuilds_poseidons_hippocampi_still_gated_on_the_earth_shaker():
    """Mid-wave save: the adds aren't in a fresh Depths, so they're rebuilt from ENEMY_REGISTRY and re-linked to the next phase."""
    dungeon, start, floors = build_world()
    depths = floors["floor_6"]["Poseidon's Depths"]
    source = Room("Poseidon's Depths")
    poseidon = create_poseidon()
    source.add_enemy(poseidon)
    player = Player(name="Hero", hp=50)
    poseidon.hp = 0
    resolve_pending_defeats(player, source)
    apply_room_data(depths, serialise_room(source))
    assert [e.name for e in depths.enemies] == ["Hippocampus", "Hippocampus"]
    assert all(e.wave_gate_factory is ENEMY_REGISTRY["poseidon (earth-shaker)"] for e in depths.enemies)

def test_player_from_save_data_keeps_penelopes_thread_as_a_loyalty_token():
    dungeon, start, floors = build_world()
    player = Player(name="Hero", hp=20)
    player.inventory.add(create_penelopes_thread())
    reloaded, _ = player_from_save_data(serialise_player(player, start), dungeon)
    assert reloaded.has_loyalty_token() is True

def write_raw_save(tmp_path, profile, slot, content):
    """Write content straight into a slot's file, bypassing save_game() - for simulating a damaged save."""
    ensure_profile_dir(profile)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(slot_path(profile, slot), mode) as f:
        f.write(content)

def valid_save_data(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    save_game(1, 1, Player(name="Hero", hp=20), start, dungeon)
    with open(slot_path(1, 1), encoding="utf-8") as f:
        return json.load(f)

def assert_load_refused(profile=1, slot=1):
    dungeon, _, _ = build_world()
    try:
        load_game(profile, slot, dungeon)
        assert False, "Expected a SaveFileError but none was raised"
    except SaveFileError as error:
        return error

def test_save_file_error_is_neither_a_refusal_nor_a_value_error():
    """Nothing that handles ActionRefused or ValueError should catch a damaged save by accident."""
    assert not issubclass(SaveFileError, ActionRefused)
    assert not issubclass(SaveFileError, ValueError)

def test_load_game_malformed_json_raises_save_file_error(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 1, 1, '{"player": {"name": "Hero"')
    error = assert_load_refused()
    assert isinstance(error.__cause__, json.JSONDecodeError)

def test_load_game_damaged_save_message_names_the_slot_and_the_fix(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 2, 3, "not json at all")
    assert str(assert_load_refused(2, 3)) == (
        "Profile 2, slot 3 can't be read - the save may be damaged. You can remove it with Delete Save on the title screen."
    )

def test_load_game_an_empty_file_raises_save_file_error(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 1, 1, "")
    assert_load_refused()

def test_load_game_undecodable_bytes_raise_save_file_error(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 1, 1, b"\xff\xfe\x00garbage")
    assert isinstance(assert_load_refused().__cause__, UnicodeDecodeError)

def test_load_game_a_missing_section_raises_save_file_error(monkeypatch, tmp_path):
    data = valid_save_data(monkeypatch, tmp_path)
    del data["world"]
    write_raw_save(tmp_path, 1, 1, json.dumps(data))
    assert isinstance(assert_load_refused().__cause__, KeyError)

def test_load_game_a_field_of_the_wrong_kind_raises_save_file_error(monkeypatch, tmp_path):
    data = valid_save_data(monkeypatch, tmp_path)
    data["player"] = ["not", "a", "dictionary"]
    write_raw_save(tmp_path, 1, 1, json.dumps(data))
    assert isinstance(assert_load_refused().__cause__, TypeError)

def test_load_game_an_unknown_room_raises_save_file_error(monkeypatch, tmp_path):
    data = valid_save_data(monkeypatch, tmp_path)
    data["player"]["current_room"] = "Nowhere At All"
    write_raw_save(tmp_path, 1, 1, json.dumps(data))
    assert isinstance(assert_load_refused().__cause__, ValueError)

def test_load_game_an_empty_slot_still_raises_file_not_found(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    try:
        load_game(1, 1, build_world()[0])
        assert False, "Expected a FileNotFoundError but none was raised"
    except FileNotFoundError:
        pass

def test_slot_summary_of_a_damaged_save_says_so(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 1, 1, "{broken")
    assert slot_summary(1, 1) == "Damaged save - can't be loaded."

def test_slot_summary_of_a_save_missing_its_player_says_so(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 1, 1, json.dumps({"world": {}}))
    assert slot_summary(1, 1) == "Damaged save - can't be loaded."

def test_delete_save_removes_a_damaged_save(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    write_raw_save(tmp_path, 1, 1, "{broken")
    assert delete_save(1, 1) is True
    assert slot_exists(1, 1) is False

def test_save_game_leaves_no_temporary_file_behind(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    save_game(1, 1, Player(name="Hero", hp=20), start, dungeon)
    assert os.listdir(os.path.dirname(slot_path(1, 1))) == ["slot_1.json"]

def test_save_game_a_failed_write_keeps_the_previous_save(monkeypatch, tmp_path):
    """Saves are written to a temporary file then swapped in - a crash part-way through can't damage the save already there."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    save_game(1, 1, Player(name="Before", hp=20), start, dungeon)

    def fail_part_way(*args, **kwargs):
        raise OSError("disk full")
    monkeypatch.setattr("dungeon_crawler.save_system.json.dump", fail_part_way)
    try:
        save_game(1, 1, Player(name="After", hp=20), start, dungeon)
        assert False, "Expected an OSError but none was raised"
    except OSError:
        pass

    monkeypatch.undo()
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    reloaded, _ = load_game(1, 1, build_world()[0])
    assert reloaded.name == "Before"
    assert os.listdir(os.path.dirname(slot_path(1, 1))) == ["slot_1.json"]

def test_load_game_a_field_that_gets_a_method_called_on_it_raises_save_file_error(monkeypatch, tmp_path):
    """Regression: a saved enemy's wave_gate stored as true raised an uncaught AttributeError ('bool' has no .lower()) - it wasn't in
    SAVE_READ_ERRORS, so a corrupted save like this still crashed the game."""
    data = valid_save_data(monkeypatch, tmp_path)
    room = next(r for r in data["world"].values() if r["enemies"])
    room["enemies"][0]["wave_gate"] = True
    write_raw_save(tmp_path, 1, 1, json.dumps(data))
    assert isinstance(assert_load_refused().__cause__, AttributeError)

def test_player_from_save_data_ignores_an_unknown_skill_path(monkeypatch, tmp_path):
    """A path renamed or removed since the save was made is skipped, not a crash."""
    data = valid_save_data(monkeypatch, tmp_path)
    data["player"]["skill_tree"]["Forgotten Arts"] = 2
    write_raw_save(tmp_path, 1, 1, json.dumps(data))
    player, _ = load_game(1, 1, build_world()[0])
    assert "Forgotten Arts" not in player.skill_tree.paths

def test_apply_room_data_skips_a_companion_the_registry_does_not_know():
    room = Room("Camp")
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": [],
                           "companions": [{"name": "Nobody Known", "hp": 5, "duel_won": False, "home_room": "Camp", "active_effects": []}]})
    assert room.companions == []

def test_save_game_that_fails_before_writing_anything_still_raises(monkeypatch, tmp_path):
    """If even the temporary file can't be opened there's nothing to clean up - the error still reaches the caller."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()

    def refuse_to_open(*args, **kwargs):
        raise PermissionError("read-only")
    monkeypatch.setattr("builtins.open", refuse_to_open)
    try:
        save_game(1, 1, Player(name="Hero", hp=20), start, dungeon)
        assert False, "Expected a PermissionError but none was raised"
    except PermissionError:
        pass

def test_save_and_load_keeps_the_oracles_spent_prophecies(monkeypatch, tmp_path):
    """Her prophecies are counted from the chamber's flags, which are saved - so a reload can't refill them."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    chamber = floors["floor_7"]["Chamber of the Oracle"]
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_5"}
    chamber.interactions["ask ahead"].handler(player, chamber)
    save_game(1, 1, player, chamber, dungeon)

    fresh, _, fresh_floors = build_world()
    load_game(1, 1, fresh)

    assert fresh_floors["floor_7"]["Chamber of the Oracle"].flags == {"prophecy:ahead:floor_6"}

def test_save_and_load_keeps_a_spared_hades_in_his_hall(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    hall = floors["floor_8"]["Hall of Hades"]
    player = Player(name="Hero", hp=20)
    player.story_flags.add("promised_mercy")
    while hall.enemies:
        for enemy in hall.enemies:
            enemy.hp = 0
        resolve_pending_defeats(player, hall)
    save_game(1, 1, player, hall, dungeon)

    fresh, _, fresh_floors = build_world()
    reloaded, room = load_game(1, 1, fresh)

    fresh_hall = fresh_floors["floor_8"]["Hall of Hades"]
    assert fresh_hall.enemies == []
    assert [c.name for c in fresh_hall.companions] == ["Hades"]
    assert fresh_hall.companions[0].home_room is fresh_hall
    assert "hades_spared" in reloaded.story_flags

def test_save_and_load_keeps_the_heads_of_scylla_striking_wildly(monkeypatch, tmp_path):
    """Enemy effects aren't saved, so the miss chance has to come back from the heads' factory - a reload mid-route mustn't make them sure-footed."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    rocky_shore = floors["floor_6"]["Rocky Shore"]
    rocky_shore.enemies[0].hp = 4
    save_game(1, 1, Player(name="Hero", hp=20), rocky_shore, dungeon)

    fresh, _, fresh_floors = build_world()
    load_game(1, 1, fresh)

    heads = fresh_floors["floor_6"]["Rocky Shore"].enemies
    assert heads[0].hp == 4
    assert [head.get_miss_chance("light") for head in heads] == [0.3] * 6

def test_slot_summary_marks_a_hardcore_save(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    player = Player(name="Hero", hp=20)
    player.story_flags.add("hardcore")
    save_game(1, 1, player, start, dungeon)
    assert slot_summary(1, 1).endswith(" (Hardcore)")

def test_slot_summary_of_an_ordinary_save_has_no_hardcore_mark(monkeypatch, tmp_path):
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    save_game(1, 1, Player(name="Hero", hp=20), start, dungeon)
    assert "Hardcore" not in slot_summary(1, 1)

def test_slot_summary_of_an_older_save_without_story_flags(monkeypatch, tmp_path):
    data = valid_save_data(monkeypatch, tmp_path)
    del data["player"]["story_flags"]
    write_raw_save(tmp_path, 1, 1, json.dumps(data))
    summary = slot_summary(1, 1)
    assert summary.startswith("Hero - LVL 1")
    assert "Hardcore" not in summary

def test_serialise_room_records_the_exits_still_hidden():
    room = Room("Styx Crossing")
    room.add_hidden_exit("down", Room("Sunken Vault"))
    room.add_hidden_exit("north", Room("Cellar"))
    room.reveal_hidden_exit("north")
    assert serialise_room(room)["hidden_exits"] == ["down"]

def test_apply_room_data_reveals_exits_the_save_no_longer_lists_as_hidden():
    vault = Room("Sunken Vault")
    room = Room("Styx Crossing")
    room.add_hidden_exit("down", vault)
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": [], "hidden_exits": []})
    assert room.get_exit("down") is vault
    assert room.hidden_exits == {}

def test_apply_room_data_keeps_exits_the_save_lists_as_hidden():
    room = Room("Styx Crossing")
    room.add_hidden_exit("down", Room("Sunken Vault"))
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": [], "hidden_exits": ["down"]})
    assert "down" in room.hidden_exits
    assert room.get_exit("down") is None

def test_apply_room_data_from_an_older_save_leaves_hidden_exits_hidden():
    room = Room("Styx Crossing")
    room.add_hidden_exit("down", Room("Sunken Vault"))
    apply_room_data(room, {"enemies": [], "items": [], "allies_traded": []})
    assert "down" in room.hidden_exits

def test_save_and_load_keeps_a_revealed_hidden_exit_open(monkeypatch, tmp_path):
    """Regression: loading rebuilds the world fresh, so an exit revealed before saving used to be hidden again after a reload."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    styx = floors["floor_1"]["Styx Crossing"]
    styx.reveal_hidden_exit("down")
    save_game(1, 1, Player(name="Hero", hp=20), styx, dungeon)

    fresh, _, fresh_floors = build_world()
    load_game(1, 1, fresh)

    fresh_styx = fresh_floors["floor_1"]["Styx Crossing"]
    assert fresh_styx.get_exit("down") is fresh_floors["floor_1"]["Sunken Vault"]
    assert fresh_styx.hidden_exits == {}

def test_save_and_load_in_the_banks_of_the_lethe(monkeypatch, tmp_path):
    """Regression: the room was missing from floor 1's room dict, so a save made there referenced an unknown room and couldn't be loaded."""
    monkeypatch.setattr("dungeon_crawler.save_system.SAVES_DIR", str(tmp_path))
    dungeon, start, floors = build_world()
    fields = floors["floor_1"]["Fields of Asphodel"]
    fields.reveal_hidden_exit("south")
    save_game(1, 1, Player(name="Hero", hp=20), floors["floor_1"]["Banks of the Lethe"], dungeon)

    fresh, _, fresh_floors = build_world()
    player, room = load_game(1, 1, fresh)

    assert room is fresh_floors["floor_1"]["Banks of the Lethe"]
    assert fresh_floors["floor_1"]["Fields of Asphodel"].get_exit("south") is room
