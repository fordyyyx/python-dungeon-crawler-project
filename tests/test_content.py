from dungeon_crawler.content import create_aegis_fragment, create_ambrosia, create_bronze_breastplate, create_bronze_xiphos, create_charon, create_charons_coin, create_chiron, create_dummy_head, create_hades, create_mentor, create_mentors_token, create_minotaur, create_skeleton_warrior, create_small_healing_potion, create_spear_of_ares, create_training_dummy, create_wooden_shield, create_wooden_sword, create_wounded_soldier, build_world
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
    assert training_dummy.attack_damage == 0
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

def test_create_wounded_soldier_has_correct_name_and_description():
    wounded_soldier = create_wounded_soldier()
    assert wounded_soldier.name == "Wounded Soldier"
    assert wounded_soldier.description == "Bandaged and pale, but still sharp-eyed — clearly more useful than his condition suggests."

def test_create_wounded_soldier_has_no_required_items():
    wounded_soldier = create_wounded_soldier()
    assert wounded_soldier.required_items == []

def test_create_wounded_soldier_talk_returns_default_message():
    wounded_soldier = create_wounded_soldier()
    player = Player(name="hero", hp=100)
    assert wounded_soldier.talk(player) == "Wounded Soldier has nothing to say."

def test_create_wounded_soldier_carries_bronze_xiphos():
    wounded_soldier = create_wounded_soldier()
    item_names = [item.name for item in wounded_soldier.inventory.items]
    assert "Bronze Xiphos" in item_names

def test_create_wounded_soldier_carries_bronze_breastplate():
    wounded_soldier = create_wounded_soldier()
    item_names = [item.name for item in wounded_soldier.inventory.items]
    assert "Bronze Breastplate" in item_names

def test_create_wounded_soldier_carries_small_healing_potion():
    wounded_soldier = create_wounded_soldier()
    item_names = [item.name for item in wounded_soldier.inventory.items]
    assert "Small Healing Potion" in item_names

def test_create_charon_has_correct_name_and_description():
    charon = create_charon()
    assert charon.name == "Charon"
    assert charon.description == "He holds out one weathered hand, saying nothing, waiting for the coin he already knows you'll need."

def test_create_charon_has_empty_inventory():
    charon = create_charon()
    assert len(charon.inventory) == 0

def test_create_charon_talk_returns_hint():
    charon = create_charon()
    player = Player(name="hero", hp=100)
    assert charon.talk(player) == charon.hint

def test_create_bronze_breastplate_has_correct_defence_and_description():
    breastplate = create_bronze_breastplate()
    assert breastplate.name == "Bronze Breastplate"
    assert breastplate.description == "Dented and a size too large, but the bronze is sound - better than the wood you started with, if only just."
    assert breastplate.defence == 2

def test_create_small_healing_potion_has_correct_heal_amount_and_description():
    potion = create_small_healing_potion()
    assert potion.name == "Small Healing Potion"
    assert potion.description == "A cloudy vial, more herb than magic - enough to steady a shaking hand, not much more."
    assert potion.heal_amount == 5

def test_build_world_returns_nine_rooms():
    dungeon, entrance = build_world()
    assert len(dungeon) == 9

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

def test_build_world_locks_descend_exit_requiring_charons_coin():
    dungeon, entrance = build_world()
    assert entrance.locked_exits["descend"] == "Charon's Coin"

def test_build_world_entrance_connects_to_cave_entrance_via_descend():
    dungeon, entrance = build_world()
    assert entrance.get_exit("descend") is dungeon.get_room("Cave Entrance")

def test_build_world_cave_entrance_connects_to_styx_crossing_via_descend():
    dungeon, entrance = build_world()
    cave_entrance = dungeon.get_room("Cave Entrance")
    assert cave_entrance is not None
    assert cave_entrance.get_exit("descend") is dungeon.get_room("Styx Crossing")

def test_build_world_styx_crossing_connects_back_to_cave_entrance_via_ascend():
    dungeon, entrance = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    cave_entrance = dungeon.get_room("Cave Entrance")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("ascend") is cave_entrance

def test_build_world_styx_crossing_connects_to_fields_of_asphodel_via_east():
    dungeon, entrance = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("east") is dungeon.get_room("Fields of Asphodel")

def test_build_world_fields_of_asphodel_connects_back_to_styx_crossing_via_west():
    dungeon, entrance = build_world()
    fields_of_asphodel = dungeon.get_room("Fields of Asphodel")
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert fields_of_asphodel is not None
    assert fields_of_asphodel.get_exit("west") is styx_crossing

def test_build_world_styx_crossing_connects_to_sunken_vault_via_down():
    dungeon, entrance = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("down") is dungeon.get_room("Sunken Vault")

def test_build_world_sunken_vault_connects_back_to_styx_crossing_via_up():
    dungeon, entrance = build_world()
    sunken_vault = dungeon.get_room("Sunken Vault")
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert sunken_vault is not None
    assert sunken_vault.get_exit("up") is styx_crossing

def test_build_world_cave_entrance_has_wounded_soldier_as_ally():
    dungeon, entrance = build_world()
    cave_entrance = dungeon.get_room("Cave Entrance")
    assert cave_entrance is not None
    ally_names = [ally.name for ally in cave_entrance.allies]
    assert "Wounded Soldier" in ally_names

def test_build_world_styx_crossing_has_charon_as_ally():
    dungeon, entrance = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    ally_names = [ally.name for ally in styx_crossing.allies]
    assert "Charon" in ally_names

def test_build_world_sunken_vault_has_skeleton_warrior_enemy():
    dungeon, entrance = build_world()
    sunken_vault = dungeon.get_room("Sunken Vault")
    assert sunken_vault is not None
    enemy_names = [enemy.name for enemy in sunken_vault.enemies]
    assert "Skeleton Warrior" in enemy_names


