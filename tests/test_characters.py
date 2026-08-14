from dungeon_crawler.characters import Character, Player, Enemy
from dungeon_crawler.items import Weapon

def test_take_damage_reduces_hp():
    character = Character(name="Hero", hp=100, attack_damage=10)
    character.take_damage(30)
    assert character.hp == 70

def test_player_attack():
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy = Enemy(name="Goblin", hp=50, loot=[], attack_damage=10)
    player.attack(enemy)
    assert enemy.hp == 30

def test_enemy_attack():
    enemy = Enemy(name="Goblin", hp=50, loot=[], attack_damage=10)
    player = Player(name="Hero", hp=100, attack_damage=20)
    enemy.attack(player)
    assert player.hp == 90

def test_take_damage_cannot_go_below_zero():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.take_damage(50)
    assert character.hp == 0

def test_take_damage_kills_character():
    character = Character(name="Hero", hp=10, attack_damage=5)
    character.take_damage(10)
    assert character.is_alive() is False

def test_enemy_on_death_drops_loot(capsys):
    sword = Weapon(name="Iron Sword", description="", damage=5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    enemy.take_damage(10)
    captured = capsys.readouterr()
    assert "Iron Sword" in captured.out
