from dungeon_crawler.characters import Character
from dungeon_crawler.content import create_minotaur, create_bronze_xiphos, create_skeleton_warrior
from dungeon_crawler.world import Room
from dungeon_crawler.engine import handle_enemy_defeat

def test_character_attack_deals_damage_to_target():
    attacker = Character(name="hero", hp=100, attack_damage=10)
    target = Character(name="goblin", hp=20, attack_damage=5)

    attacker.attack(target)

    assert target.hp == 10

def test_handle_enemy_defeat_moves_loot_into_room():
    room = Room("Labyrinth")
    sword = create_bronze_xiphos()
    enemy = create_minotaur()
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert enemy not in room.enemies
    assert sword.name in [item.name for item in room.items]

def test_handle_enemy_defeat_with_no_loot_adds_no_items():
    room = Room("Labyrinth")
    enemy = create_skeleton_warrior()
    room.add_enemy(enemy)

    handle_enemy_defeat(room, enemy)

    assert room.items == []