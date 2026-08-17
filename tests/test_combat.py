from dungeon_crawler.characters import Character

def test_character_attack_deals_damage_to_target():
    attacker = Character(name="hero", hp=100, attack_damage=10)
    target = Character(name="goblin", hp=20, attack_damage=5)

    attacker.attack(target)

    assert target.hp == 10