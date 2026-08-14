from dungeon_crawler.characters import Character, Player, Enemy
from dungeon_crawler.items import Weapon, Inventory

def test_character_initialises_with_correct_stats():
    character = Character(name="Hero", hp=30, attack_damage=5)
    assert character.hp == 30
    assert character.attack_damage == 5

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

def test_character_on_death_prints_default_message(capsys):
    character = Character(name="Hero", hp=0, attack_damage=5)
    character.on_death()
    captured = capsys.readouterr()
    assert "Hero has died" in captured.out

def test_player_initialises_with_inventory():
    player = Player(name="Hero", hp=10)
    assert isinstance(player.inventory, Inventory)
    assert len(player.inventory) == 0


def test_player_on_death_prints_game_over(capsys):
    player = Player(name="Hero", hp=10)
    player.on_death()
    captured = capsys.readouterr()
    assert "Hero has fallen. Game Over." in captured.out

def test_enemy_on_death_prints_defeated_message(capsys):
    enemy = Enemy(name="Hades", hp=60, attack_damage=20)
    enemy.on_death()
    captured = capsys.readouterr()
    assert "Hades has been defeated." in captured.out

def test_enemy_on_death_drops_loot(capsys):
    sword = Weapon(name="Iron Sword", description="", damage=5)
    enemy = Enemy(name="Goblin", hp=10, attack_damage=5, loot=[sword])
    enemy.take_damage(10)
    captured = capsys.readouterr()
    assert "Iron Sword" in captured.out

def test_enemy_on_death_with_no_loot_does_not_print_drop_message(capsys):
    enemy = Enemy("Hades", hp=60, attack_damage=20)
    enemy.on_death()
    captured = capsys.readouterr()
    assert "dropped: " not in captured.out
