from dungeon_crawler.content import create_aegis_fragment, create_ambrosia, create_bronze_xiphos, create_hades, create_minotaur, create_skeleton_warrior, build_world


def test_create_minotaur_has_correct_stats():
    minotaur = create_minotaur()
    assert minotaur.name == "Minotaur"
    assert minotaur.hp == 25
    assert minotaur.attack_damage == 8
    assert minotaur.armour == 2
    assert len(minotaur.loot) == 1

def test_create_minotaur_drops_bronze_xiphos(capsys):
    minotaur = create_minotaur()
    minotaur.on_death()
    captured = capsys.readouterr()
    assert "Bronze Xiphos" in captured.out

def test_create_skeleton_warrior_has_correct_stats():
    skeleton_warrior = create_skeleton_warrior()
    assert skeleton_warrior.name == "Skeleton Warrior"
    assert skeleton_warrior.hp == 8
    assert skeleton_warrior.attack_damage == 3
    assert skeleton_warrior.armour == 0
    assert len(skeleton_warrior.loot) == 0


def create_hades_has_correct_stats():
    hades = create_hades()
    assert hades.name == "Hades"
    assert hades.hp == 60
    assert hades.attack_damage == 15
    assert hades.armour == 5
    assert len(hades.loot) == 1

def create_bronze_xiphos_has_correct_damage_and_description():
    sword = create_bronze_xiphos()
    assert sword.name == "Bronze Xiphos"
    assert sword.description == "A short, leaf-bladed sword - favoured by soldiers who valued speed over reach."
    assert sword.damage == 3

def create_aegis_fragment_has_correct_defence_and_description():
    shield = create_aegis_fragment()
    assert shield.name == "Shield of Aegis (fragment)"
    assert shield.description == "A shard of bronze etched with a single unblinking eye."
    assert shield.defence == 2

def create_ambrosia_has_correct_heal_amount_and_description():
    potion = create_ambrosia()
    assert potion.name == "Vial of Ambrosia"
    assert potion.heal_amount == 20
    assert potion.description == "Golden and faintly humming - mortal hands were never meant to hold this."


