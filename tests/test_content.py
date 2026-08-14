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

def test_build_world_creates_all_rooms():
    dungeon, current_room = build_world()
    assert len(dungeon) == 6

def test_build_world_connects_all_rooms_correctly():
    dungeon, entrance = build_world()

    styx = dungeon.get_room("Styx Crossing")
    armoury = dungeon.get_room("Armoury of Ares")
    library = dungeon.get_room("Library of Athena")
    vault = dungeon.get_room("Sunken Vault")
    hall = dungeon.get_room("Hall of Hades")

    assert styx is not None
    assert armoury is not None
    assert library is not None
    assert vault is not None
    assert hall is not None

    assert entrance.get_exit("north") is styx
    assert styx.get_exit("south") is entrance

    assert styx.get_exit("west") is armoury
    assert armoury.get_exit("east") is styx

    assert styx.get_exit("east") is library
    assert library.get_exit("west") is styx

    assert styx.get_exit("north") is hall
    assert hall.get_exit("south") is styx

    assert entrance.get_exit("down") is vault
    assert vault.get_exit("up") is entrance

def test_build_world_places_items_in_correct_rooms():
    dungeon, entrance = build_world()

    styx = dungeon.get_room("Styx Crossing")
    armoury = dungeon.get_room("Armoury of Ares")
    library = dungeon.get_room("Library of Athena")
    vault = dungeon.get_room("Sunken Vault")       
    hall = dungeon.get_room("Hall of Hades")
    
    assert styx is not None
    assert armoury is not None
    assert library is not None
    assert vault is not None
    assert hall is not None

    assert len(armoury.items) == 1
    assert len(library.items) == 1
    assert len(vault.items) == 1


def test_build_world_places_enemies_in_correct_rooms():
    dungeon, entrance = build_world()
    
    styx = dungeon.get_room("Styx Crossing")
    armoury = dungeon.get_room("Armoury of Ares")
    library = dungeon.get_room("Library of Athena")
    vault = dungeon.get_room("Sunken Vault")       
    hall = dungeon.get_room("Hall of Hades")
    
    assert styx is not None
    assert armoury is not None
    assert library is not None
    assert vault is not None
    assert hall is not None

    assert len(hall.enemies) == 1
    assert len(vault.enemies) == 1

def test_build_world_returns_starting_room_as_cave_entrance():
    dungeon, entrance = build_world()

    assert entrance.name == "Cave Entrance"