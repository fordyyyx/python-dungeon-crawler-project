from dungeon_crawler.characters import Character

def test_take_damage_reduces_hp():
    character = Character(name="Hero", hp=100)
    character.take_damage(30)
    assert character.hp == 70

def test_take_damage_cannot_go_below_zero():
    character = Character(name="Hero", hp=10)
    character.take_damage(50)
    assert character.hp == 0

def test_take_damage_kills_character():
    character = Character(name="Hero", hp=10)
    character.take_damage(10)
    assert character.is_alive() is False
