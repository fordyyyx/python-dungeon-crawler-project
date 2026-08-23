from dungeon_crawler.content import create_aegis_fragment, create_ambrosia, create_bronze_xiphos, create_charons_coin, create_chiron, create_dummy_head, create_hades, create_mentor, create_mentors_token, create_minotaur, create_skeleton_warrior, create_spear_of_ares, create_training_dummy, create_wooden_shield, create_wooden_sword, build_world
from dungeon_crawler.characters import Player
from dungeon_crawler.items import QuestItem


def test_create_minotaur_has_correct_stats():
    minotaur = create_minotaur()
    assert minotaur.name == "Minotaur"
    assert minotaur.hp == 25
    assert minotaur.attack_damage == 8
    assert minotaur.armour == 2
    assert len(minotaur.loot) == 1

def test_create_minotaur_drops_bronze_xiphos():
    minotaur = create_minotaur()
    message = minotaur.on_death()
    assert "Bronze Xiphos" in message

def test_create_skeleton_warrior_has_correct_stats():
    skeleton_warrior = create_skeleton_warrior()
    assert skeleton_warrior.name == "Skeleton Warrior"
    assert skeleton_warrior.hp == 8
    assert skeleton_warrior.attack_damage == 3
    assert skeleton_warrior.armour == 0
    assert len(skeleton_warrior.loot) == 0


def test_create_hades_has_correct_stats():
    hades = create_hades()
    assert hades.name == "Hades"
    assert hades.hp == 60
    assert hades.attack_damage == 15
    assert hades.armour == 5
    assert len(hades.loot) == 1

def test_create_hades_drops_ambrosia():
    hades = create_hades()
    message = hades.on_death()
    assert "Vial of Ambrosia" in message

def test_create_bronze_xiphos_has_correct_damage_and_description():
    sword = create_bronze_xiphos()
    assert sword.name == "Bronze Xiphos"
    assert sword.description == "A short, leaf-bladed sword - favoured by soldiers who valued speed over reach."
    assert sword.damage == 3

def test_create_aegis_fragment_has_correct_defence_and_description():
    shield = create_aegis_fragment()
    assert shield.name == "Shield of Aegis (fragment)"
    assert shield.description == "A shard of bronze etched with a single unblinking eye."
    assert shield.defence == 2

def test_create_ambrosia_has_correct_heal_amount_and_description():
    potion = create_ambrosia()
    assert potion.name == "Vial of Ambrosia"
    assert potion.heal_amount == 20
    assert potion.description == "Golden and faintly humming - mortal hands were never meant to hold this."

def test_create_spear_of_ares_has_correct_damage_and_description():
    spear = create_spear_of_ares()
    assert spear.name == "Spear of Ares"
    assert spear.description == "Bronze-tipped and still warm, as if recently thrown in anger."
    assert spear.damage == 8

def test_create_chiron_has_correct_name_and_description():
    chiron = create_chiron()
    assert chiron.name == "Chiron"
    assert chiron.description == "Half man, half horse, entirely patient — he's trained more heroes than he can easily count, and it shows."

def test_create_chiron_has_correct_required_items():
    chiron = create_chiron()
    assert chiron.required_items == ["Wooden Sword", "Wooden Shield", "Dummy Head", "Mentor's Token"]

def test_create_chiron_has_empty_inventory():
    chiron = create_chiron()
    assert len(chiron.inventory) == 0

def test_create_chiron_talk_returns_hint_when_player_missing_required_items():
    chiron = create_chiron()
    player = Player(name="hero", hp=100)
    assert chiron.talk(player) == chiron.hint

def test_create_chiron_talk_returns_hint_complete_when_player_has_required_items():
    chiron = create_chiron()
    player = Player(name="hero", hp=100)
    for item_name in chiron.required_items:
        player.inventory.add(QuestItem(name=item_name, description=""))
    assert chiron.talk(player) == chiron.hint_complete

def test_create_training_dummy_has_correct_stats():
    training_dummy = create_training_dummy()
    assert training_dummy.name == "Training Dummy"
    assert training_dummy.hp == 5
    assert training_dummy.attack_damage == 5
    assert training_dummy.armour == 0

def test_create_training_dummy_drops_dummy_head():
    training_dummy = create_training_dummy()
    message = training_dummy.on_death()
    assert "Dummy Head" in message

def test_create_wooden_sword_has_correct_damage_and_description():
    sword = create_wooden_sword()
    assert sword.name == "Wooden Sword"
    assert sword.description == "Blunt, splintered, and entirely harmless to anyone but a straw dummy — exactly as intended."
    assert sword.damage == 1

def test_create_wooden_shield_has_correct_defence_and_description():
    shield = create_wooden_shield()
    assert shield.name == "Wooden Shield"
    assert shield.description == "Warped and dry-rotted at the edges, but it'll turn aside a training blow well enough."
    assert shield.defence == 1

def test_create_mentor_has_correct_name_and_description():
    mentor = create_mentor()
    assert mentor.name == "Mentor"
    assert mentor.description == "He nods once in greeting, the kind of nod that says he's seen a lot of hopefuls pass through here."

def test_create_mentor_talk_returns_hint():
    mentor = create_mentor()
    player = Player(name="hero", hp=100)
    assert mentor.talk(player) == mentor.hint

def test_create_mentor_has_no_required_items():
    mentor = create_mentor()
    assert mentor.required_items == []

def test_create_mentor_carries_mentors_token():
    mentor = create_mentor()
    item_names = [item.name for item in mentor.inventory.items]
    assert "Mentor's Token" in item_names

def test_create_dummy_head_has_correct_name_and_description():
    dummy_head = create_dummy_head()
    assert dummy_head.name == "Dummy Head"
    assert dummy_head.description == "A straw-stuffed head, still faintly dented from your practice blows — proof enough for Chiron that the lesson's been learned."

def test_create_charons_coin_has_correct_name_and_description():
    coin = create_charons_coin()
    assert coin.name == "Charon's Coin"
    assert coin.description == "Cold and unnaturally heavy for its size — the ferryman won't so much as glance at you without it."

def test_create_mentors_token_has_correct_name_and_description():
    token = create_mentors_token()
    assert token.name == "Mentor's Token"
    assert token.description == "A small carved token, worn smooth — Mentor's simple way of saying you've earned his approval."

def test_build_world_returns_five_rooms():
    dungeon, entrance = build_world()
    assert len(dungeon) == 5

def test_build_world_entrance_is_chamber_of_chiron():
    dungeon, entrance = build_world()
    assert entrance.name == "Chamber of Chiron"
    assert entrance is dungeon.get_room("Chamber of Chiron")

def test_build_world_entrance_connects_to_all_four_directions():
    dungeon, entrance = build_world()
    assert entrance.get_exit("north") is dungeon.get_room("Chamber of Chiron (North)")
    assert entrance.get_exit("east") is dungeon.get_room("Chamber of Chiron (East)")
    assert entrance.get_exit("south") is dungeon.get_room("Chamber of Chiron (South)")
    assert entrance.get_exit("west") is dungeon.get_room("Chamber of Chiron (West)")

def test_build_world_north_room_connects_back_to_entrance():
    dungeon, entrance = build_world()
    north_room = dungeon.get_room("Chamber of Chiron (North)")
    assert north_room is not None
    assert north_room.get_exit("south") is entrance

def test_build_world_east_room_connects_back_to_entrance():
    dungeon, entrance = build_world()
    east_room = dungeon.get_room("Chamber of Chiron (East)")
    assert east_room is not None
    assert east_room.get_exit("west") is entrance

def test_build_world_south_room_connects_back_to_entrance():
    dungeon, entrance = build_world()
    south_room = dungeon.get_room("Chamber of Chiron (South)")
    assert south_room is not None
    assert south_room.get_exit("north") is entrance

def test_build_world_west_room_connects_back_to_entrance():
    dungeon, entrance = build_world()
    west_room = dungeon.get_room("Chamber of Chiron (West)")
    assert west_room is not None
    assert west_room.get_exit("east") is entrance

def test_build_world_entrance_has_chiron_as_ally():
    dungeon, entrance = build_world()
    ally_names = [ally.name for ally in entrance.allies]
    assert "Chiron" in ally_names

def test_build_world_south_room_has_training_dummy_enemy():
    dungeon, entrance = build_world()
    south_room = dungeon.get_room("Chamber of Chiron (South)")
    assert south_room is not None
    enemy_names = [enemy.name for enemy in south_room.enemies]
    assert "Training Dummy" in enemy_names

def test_build_world_north_room_has_wooden_sword_item():
    dungeon, entrance = build_world()
    north_room = dungeon.get_room("Chamber of Chiron (North)")
    assert north_room is not None
    item_names = [item.name for item in north_room.items]
    assert "Wooden Sword" in item_names

def test_build_world_east_room_has_wooden_shield_item():
    dungeon, entrance = build_world()
    east_room = dungeon.get_room("Chamber of Chiron (East)")
    assert east_room is not None
    item_names = [item.name for item in east_room.items]
    assert "Wooden Shield" in item_names

def test_build_world_west_room_has_mentor_as_ally():
    dungeon, entrance = build_world()
    west_room = dungeon.get_room("Chamber of Chiron (West)")
    assert west_room is not None
    ally_names = [ally.name for ally in west_room.allies]
    assert "Mentor" in ally_names

def test_build_world_locks_east_exit_requiring_wooden_sword():
    dungeon, entrance = build_world()
    assert entrance.locked_exits["east"] == "Wooden Sword"

def test_build_world_locks_south_exit_requiring_wooden_shield():
    dungeon, entrance = build_world()
    assert entrance.locked_exits["south"] == "Wooden Shield"

def test_build_world_locks_west_exit_requiring_dummy_head():
    dungeon, entrance = build_world()
    assert entrance.locked_exits["west"] == "Dummy Head"


