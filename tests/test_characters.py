from dungeon_crawler.characters import Character, Player, Enemy

def test_take_damage_reduces_hp():
    character = Character(name="Hero", hp=100)
    character.take_damage(30)
    assert character.hp == 70

def test_player_attack():
    player = Player(name="Hero", hp=100, level=5, attack_damage=20, inventory=[])
    enemy = Enemy(name="Goblin", hp=50, attack_damage=10)
    player.attack(enemy)
    assert enemy.hp == 30

def test_enemy_attack():
    enemy = Enemy(name="Goblin", hp=50, attack_damage=10)
    player = Player(name="Hero", hp=100, level=5, attack_damage=20, inventory=[])
    enemy.attack(player)
    assert player.hp == 90

def test_take_damage_cannot_go_below_zero():
    character = Character(name="Hero", hp=10)
    character.take_damage(50)
    assert character.hp == 0

def test_take_damage_kills_character():
    character = Character(name="Hero", hp=10)
    character.take_damage(10)
    assert character.is_alive() is False
