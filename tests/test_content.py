from dungeon_crawler.content import create_aegis_fragment, create_ambrosia, create_ares, create_athena, create_breastplate_of_athena, create_bronze_breastplate, create_bronze_xiphos, create_centaurs_broken_bow, create_charon, create_charons_coin, create_chiron, create_cyclops_eye, create_dummy_head, create_hades, create_hermes, create_hermes_favour, create_mentor, create_mentors_token, create_minotaur, create_prometheus, create_skeleton_warrior, create_small_healing_potion, create_spear_of_ares, create_training_dummy, create_wooden_shield, create_wooden_sword, create_wounded_soldier, build_world, build_floor_0, build_floor_1, build_floor_2, build_floor_3, build_floor_4, build_floor_5, build_floor_6, build_floor_7, build_floor_8, build_floor_9, build_blank_test_room, ANCESTRIES
from dungeon_crawler.characters import Player
from dungeon_crawler.items import QuestItem


def test_create_minotaur_has_correct_stats():
    minotaur = create_minotaur()
    assert minotaur.name == "Minotaur"
    assert minotaur.hp == 25
    assert minotaur.attack_damage == 8
    assert minotaur.armour == 2
    assert len(minotaur.loot) == 1
    assert minotaur.experience_reward == 30
    assert minotaur.gold_reward == 18

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
    assert len(skeleton_warrior.loot) == 1
    assert skeleton_warrior.experience_reward == 5
    assert skeleton_warrior.gold_reward == 2

def test_create_skeleton_warrior_drops_small_healing_potion():
    skeleton_warrior = create_skeleton_warrior()
    message = skeleton_warrior.on_death()
    assert "Small Healing Potion" in message


def test_create_hades_has_correct_stats():
    hades = create_hades()
    assert hades.name == "Hades"
    assert hades.hp == 60
    assert hades.attack_damage == 15
    assert hades.armour == 5
    assert len(hades.loot) == 1
    assert hades.experience_reward == 80
    assert hades.gold_reward == 55

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
    assert spear.description == "Bronze-tipped and perfectly balanced - it feels less like you're holding a weapon, and more like it's holding you steady"
    assert spear.damage == 6

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

def test_create_chiron_reward_is_charons_coin():
    chiron = create_chiron()
    assert chiron.reward is not None
    assert chiron.reward.name == "Charon's Coin"

def test_create_chiron_has_correct_post_trade_message():
    chiron = create_chiron()
    assert chiron.post_trade_message == "You feel ready. Type 'descend' when you're prepared to leave this place behind."

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
    assert training_dummy.experience_reward == 0
    assert training_dummy.gold_reward == 0

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

def test_create_wounded_soldier_talk_returns_hint():
    wounded_soldier = create_wounded_soldier()
    player = Player(name="hero", hp=100)
    assert wounded_soldier.talk(player) == wounded_soldier.hint

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

def test_ancestries_contains_expected_keys():
    assert set(ANCESTRIES.keys()) == {
        "basic", "ares", "athena", "hermes", "poseidon", "achilles",
        "odysseus", "atalanta", "medusa", "minotaur", "cyclops",
    }

def test_ancestries_only_odysseus_grants_bonus_skill_point():
    bonus_keys = [key for key, data in ANCESTRIES.items() if data["bonus_skill_point"]]
    assert bonus_keys == ["odysseus"]

def test_ancestries_basic_has_correct_stats():
    basic = ANCESTRIES["basic"]
    assert basic["label"] == "No lineage"
    assert basic["attack"] == 3
    assert basic["armour"] == 1
    assert basic["hp"] == 20
    assert basic["intellect"] == 2

def test_ancestries_ares_has_correct_stats():
    ares = ANCESTRIES["ares"]
    assert ares["label"] == "Descendant of Ares"
    assert ares["attack"] == 5
    assert ares["armour"] == 1
    assert ares["hp"] == 19
    assert ares["intellect"] == 1

def test_ancestries_athena_has_correct_stats():
    athena = ANCESTRIES["athena"]
    assert athena["label"] == "Descendant of Athena"
    assert athena["attack"] == 4
    assert athena["armour"] == 3
    assert athena["hp"] == 20
    assert athena["intellect"] == 5

def test_ancestries_hermes_has_correct_stats():
    hermes = ANCESTRIES["hermes"]
    assert hermes["label"] == "Descendant of Hermes"
    assert hermes["attack"] == 4
    assert hermes["armour"] == 1
    assert hermes["hp"] == 22
    assert hermes["intellect"] == 3

def test_ancestries_poseidon_has_correct_stats():
    poseidon = ANCESTRIES["poseidon"]
    assert poseidon["label"] == "Descendant of Poseidon"
    assert poseidon["attack"] == 2
    assert poseidon["armour"] == 5
    assert poseidon["hp"] == 19
    assert poseidon["intellect"] == 2

def test_ancestries_achilles_has_correct_stats():
    achilles = ANCESTRIES["achilles"]
    assert achilles["label"] == "Descendant of Achilles"
    assert achilles["attack"] == 6
    assert achilles["armour"] == 1
    assert achilles["hp"] == 16
    assert achilles["intellect"] == 1

def test_ancestries_odysseus_has_correct_stats():
    odysseus = ANCESTRIES["odysseus"]
    assert odysseus["label"] == "Descendant of Odysseus"
    assert odysseus["attack"] == 3
    assert odysseus["armour"] == 1
    assert odysseus["hp"] == 20
    assert odysseus["intellect"] == 4

def test_ancestries_atalanta_has_correct_stats():
    atalanta = ANCESTRIES["atalanta"]
    assert atalanta["label"] == "Descendant of Atalanta"
    assert atalanta["attack"] == 5
    assert atalanta["armour"] == 1
    assert atalanta["hp"] == 20
    assert atalanta["intellect"] == 2

def test_ancestries_medusa_has_correct_stats():
    medusa = ANCESTRIES["medusa"]
    assert medusa["label"] == "Descendant of Medusa"
    assert medusa["attack"] == 2
    assert medusa["armour"] == 4
    assert medusa["hp"] == 19
    assert medusa["intellect"] == 3

def test_ancestries_minotaur_has_correct_stats():
    minotaur = ANCESTRIES["minotaur"]
    assert minotaur["label"] == "Descendant of the Minotaur"
    assert minotaur["attack"] == 6
    assert minotaur["armour"] == 0
    assert minotaur["hp"] == 21
    assert minotaur["intellect"] == 0

def test_ancestries_cyclops_has_correct_stats():
    cyclops = ANCESTRIES["cyclops"]
    assert cyclops["label"] == "Descendant of a Cyclops"
    assert cyclops["attack"] == 3
    assert cyclops["armour"] == 0
    assert cyclops["hp"] == 25
    assert cyclops["intellect"] == 0

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

def test_create_athena_has_correct_name_and_description():
    athena = create_athena()
    assert athena.name == "Athena"
    assert athena.description == "Calm, measured, and faintly amused — as if she already knows exactly how this ends."

def test_create_athena_has_correct_required_items():
    athena = create_athena()
    assert athena.required_items == ["Centaur's Broken Bow"]

def test_create_athena_reward_is_breastplate_of_athena():
    athena = create_athena()
    assert athena.reward is not None
    assert athena.reward.name == "Breastplate of Athena"

def test_create_athena_talk_returns_default_message_when_player_missing_required_items():
    athena = create_athena()
    player = Player(name="hero", hp=100)
    assert athena.talk(player) == "Athena has nothing to say."

def test_create_athena_talk_returns_empty_string_when_player_has_required_items():
    athena = create_athena()
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Centaur's Broken Bow", description=""))
    assert athena.talk(player) == ""

def test_create_ares_has_correct_name_and_description():
    ares = create_ares()
    assert ares.name == "Ares"
    assert ares.description == "He barely looks up from sharpening a blade, though he's clearly aware of every move you make."

def test_create_ares_has_correct_required_items():
    ares = create_ares()
    assert ares.required_items == ["Cyclops' Eye"]

def test_create_ares_reward_is_spear_of_ares():
    ares = create_ares()
    assert ares.reward is not None
    assert ares.reward.name == "Spear of Ares"

def test_create_ares_talk_returns_default_message_when_player_missing_required_items():
    ares = create_ares()
    player = Player(name="hero", hp=100)
    assert ares.talk(player) == "Ares has nothing to say."

def test_create_ares_talk_returns_empty_string_when_player_has_required_items():
    ares = create_ares()
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Cyclops' Eye", description=""))
    assert ares.talk(player) == ""

def test_create_hermes_has_correct_name_and_description():
    hermes = create_hermes()
    assert hermes.name == "Hermes"
    assert hermes.description == "Never quite still, halfway through some errand even while talking to you."

def test_create_hermes_has_correct_required_items():
    hermes = create_hermes()
    assert hermes.required_items == ["Skeleton Bone"]

def test_create_hermes_reward_is_hermes_favour():
    hermes = create_hermes()
    assert hermes.reward is not None
    assert hermes.reward.name == "Favour of Hermes"

def test_create_hermes_talk_returns_default_message_when_player_missing_required_items():
    hermes = create_hermes()
    player = Player(name="hero", hp=100)
    assert hermes.talk(player) == "Hermes has nothing to say."

def test_create_hermes_talk_returns_empty_string_when_player_has_required_items():
    hermes = create_hermes()
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Skeleton Bone", description=""))
    assert hermes.talk(player) == ""

def test_create_prometheus_has_correct_name_and_description():
    prometheus = create_prometheus()
    assert prometheus.name == "Prometheus"
    assert prometheus.description == "Chained but unbroken, watching you with the weary patience of someone who's paid dearly for helping before."

def test_create_prometheus_has_no_required_items():
    prometheus = create_prometheus()
    assert prometheus.required_items == []

def test_create_prometheus_has_no_reward():
    prometheus = create_prometheus()
    assert prometheus.reward is None

def test_create_prometheus_talk_returns_default_message():
    prometheus = create_prometheus()
    player = Player(name="hero", hp=100)
    assert prometheus.talk(player) == "Prometheus has nothing to say."

def test_create_cyclops_eye_has_correct_name_and_description():
    eye = create_cyclops_eye()
    assert eye.name == "Cyclops' Eye"
    assert eye.description == "Still faintly warm and unsettlingly heavy for its size - Ares will know exactly what this cost you."

def test_create_breastplate_of_athena_has_correct_defence_and_description():
    breastplate = create_breastplate_of_athena()
    assert breastplate.name == "Breastplate of Athena"
    assert breastplate.description == "Cool to the touch even in the deepest heat, etched with an owl that seems to watch whichever way danger comes from."
    assert breastplate.defence == 4

def test_create_centaurs_broken_bow_has_correct_name_and_description():
    bow = create_centaurs_broken_bow()
    assert bow.name == "Centaur's Broken Bow"
    assert bow.description == "Snapped clean at the riser - proof you closed the distance before it ever got a clean shot off."

def test_create_hermes_favour_has_correct_name_and_description():
    favour = create_hermes_favour()
    assert favour.name == "Favour of Hermes"
    assert favour.description == "Quick, light, and gone before you've noticed - much like the god who gave it."

def test_create_hermes_favour_has_correct_points():
    favour = create_hermes_favour()
    assert favour.points == 1

def test_build_world_returns_fifty_rooms():
    dungeon, entrance, floors = build_world()
    assert len(dungeon) == 50

def test_build_blank_test_room_has_correct_name_and_description():
    room = build_blank_test_room()
    assert room.name == "Dev Test Room"
    assert room.description == "A featureless void, useful for exactly nothing except testing things in isolation."

def test_build_blank_test_room_has_no_exits():
    room = build_blank_test_room()
    assert room.exits == {}

def test_build_world_includes_dev_test_room():
    dungeon, entrance, floors = build_world()
    dev_test_room = dungeon.get_room("Dev Test Room")
    assert dev_test_room is not None
    assert dev_test_room.name == "Dev Test Room"

def test_build_world_dev_test_room_is_not_part_of_any_floor():
    dungeon, entrance, floors = build_world()
    all_floor_room_names = {
        name for floor_rooms in floors.values() for name in floor_rooms
    }
    assert "Dev Test Room" not in all_floor_room_names

def test_build_world_entrance_is_chamber_of_chiron():
    dungeon, entrance, floors = build_world()
    assert entrance.name == "Chamber of Chiron"
    assert entrance is dungeon.get_room("Chamber of Chiron")

def test_build_world_entrance_connects_to_all_four_directions():
    dungeon, entrance, floors = build_world()
    assert entrance.get_exit("north") is dungeon.get_room("Chamber of Chiron (North)")
    assert entrance.get_exit("east") is dungeon.get_room("Chamber of Chiron (East)")
    assert entrance.get_exit("south") is dungeon.get_room("Chamber of Chiron (South)")
    assert entrance.get_exit("west") is dungeon.get_room("Chamber of Chiron (West)")

def test_build_world_north_room_connects_back_to_entrance():
    dungeon, entrance, floors = build_world()
    north_room = dungeon.get_room("Chamber of Chiron (North)")
    assert north_room is not None
    assert north_room.get_exit("south") is entrance

def test_build_world_east_room_connects_back_to_entrance():
    dungeon, entrance, floors = build_world()
    east_room = dungeon.get_room("Chamber of Chiron (East)")
    assert east_room is not None
    assert east_room.get_exit("west") is entrance

def test_build_world_south_room_connects_back_to_entrance():
    dungeon, entrance, floors = build_world()
    south_room = dungeon.get_room("Chamber of Chiron (South)")
    assert south_room is not None
    assert south_room.get_exit("north") is entrance

def test_build_world_west_room_connects_back_to_entrance():
    dungeon, entrance, floors = build_world()
    west_room = dungeon.get_room("Chamber of Chiron (West)")
    assert west_room is not None
    assert west_room.get_exit("east") is entrance

def test_build_world_entrance_has_chiron_as_ally():
    dungeon, entrance, floors = build_world()
    ally_names = [ally.name for ally in entrance.allies]
    assert "Chiron" in ally_names

def test_build_world_south_room_has_training_dummy_enemy():
    dungeon, entrance, floors = build_world()
    south_room = dungeon.get_room("Chamber of Chiron (South)")
    assert south_room is not None
    enemy_names = [enemy.name for enemy in south_room.enemies]
    assert "Training Dummy" in enemy_names

def test_build_world_north_room_has_wooden_sword_item():
    dungeon, entrance, floors = build_world()
    north_room = dungeon.get_room("Chamber of Chiron (North)")
    assert north_room is not None
    item_names = [item.name for item in north_room.items]
    assert "Wooden Sword" in item_names

def test_build_world_east_room_has_wooden_shield_item():
    dungeon, entrance, floors = build_world()
    east_room = dungeon.get_room("Chamber of Chiron (East)")
    assert east_room is not None
    item_names = [item.name for item in east_room.items]
    assert "Wooden Shield" in item_names

def test_build_world_west_room_has_mentor_as_ally():
    dungeon, entrance, floors = build_world()
    west_room = dungeon.get_room("Chamber of Chiron (West)")
    assert west_room is not None
    ally_names = [ally.name for ally in west_room.allies]
    assert "Mentor" in ally_names

def test_build_world_locks_east_exit_requiring_wooden_sword():
    dungeon, entrance, floors = build_world()
    assert entrance.locked_exits["east"] == "Wooden Sword"

def test_build_world_locks_south_exit_requiring_wooden_shield():
    dungeon, entrance, floors = build_world()
    assert entrance.locked_exits["south"] == "Wooden Shield"

def test_build_world_locks_west_exit_requiring_dummy_head():
    dungeon, entrance, floors = build_world()
    assert entrance.locked_exits["west"] == "Dummy Head"

def test_build_world_locks_descend_exit_requiring_charons_coin():
    dungeon, entrance, floors = build_world()
    assert entrance.locked_exits["descend"] == "Charon's Coin"

def test_build_world_entrance_connects_to_cave_entrance_via_descend():
    dungeon, entrance, floors = build_world()
    assert entrance.get_exit("descend") is dungeon.get_room("Cave Entrance")

def test_build_world_cave_entrance_connects_to_styx_crossing_via_descend():
    dungeon, entrance, floors = build_world()
    cave_entrance = dungeon.get_room("Cave Entrance")
    assert cave_entrance is not None
    assert cave_entrance.get_exit("descend") is dungeon.get_room("Styx Crossing")

def test_build_world_styx_crossing_connects_back_to_cave_entrance_via_ascend():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    cave_entrance = dungeon.get_room("Cave Entrance")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("ascend") is cave_entrance

def test_build_world_styx_crossing_connects_to_fields_of_asphodel_via_east():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("east") is dungeon.get_room("Fields of Asphodel")

def test_build_world_fields_of_asphodel_connects_back_to_styx_crossing_via_west():
    dungeon, entrance, floors = build_world()
    fields_of_asphodel = dungeon.get_room("Fields of Asphodel")
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert fields_of_asphodel is not None
    assert fields_of_asphodel.get_exit("west") is styx_crossing

def test_build_world_styx_crossing_down_exit_to_sunken_vault_is_hidden_until_revealed():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("down") is None
    assert styx_crossing.hidden_exits["down"] is dungeon.get_room("Sunken Vault")

def test_build_world_styx_crossing_down_exit_revealed_via_reveal_hidden_exits():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    styx_crossing.reveal_hidden_exits()
    assert styx_crossing.get_exit("down") is dungeon.get_room("Sunken Vault")

def test_build_world_styx_crossing_has_examine_text():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    assert styx_crossing.examine_text == (
        "The stonework here looks subtly disturbed — as if something below "
        "has shifted, recently, on its own."
    )

def test_build_world_sunken_vault_connects_back_to_styx_crossing_via_up():
    dungeon, entrance, floors = build_world()
    sunken_vault = dungeon.get_room("Sunken Vault")
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert sunken_vault is not None
    assert sunken_vault.get_exit("up") is styx_crossing

def test_build_world_cave_entrance_has_wounded_soldier_as_ally():
    dungeon, entrance, floors = build_world()
    cave_entrance = dungeon.get_room("Cave Entrance")
    assert cave_entrance is not None
    ally_names = [ally.name for ally in cave_entrance.allies]
    assert "Wounded Soldier" in ally_names

def test_build_world_styx_crossing_has_charon_as_ally():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    ally_names = [ally.name for ally in styx_crossing.allies]
    assert "Charon" in ally_names

def test_build_world_sunken_vault_has_skeleton_warrior_enemy():
    dungeon, entrance, floors = build_world()
    sunken_vault = dungeon.get_room("Sunken Vault")
    assert sunken_vault is not None
    enemy_names = [enemy.name for enemy in sunken_vault.enemies]
    assert "Skeleton Warrior" in enemy_names

def test_build_world_returns_floors_dict_with_ten_floor_keys():
    dungeon, entrance, floors = build_world()
    assert set(floors.keys()) == {
        "floor_0", "floor_1", "floor_2", "floor_3", "floor_4",
        "floor_5", "floor_6", "floor_7", "floor_8", "floor_9",
    }

def test_build_world_floor_0_rooms_dict_contains_five_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_0"]) == 5

def test_build_world_floor_1_rooms_dict_contains_four_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_1"]) == 4

def test_build_world_floor_2_rooms_dict_contains_five_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_2"]) == 5

def test_build_world_floor_3_rooms_dict_contains_five_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_3"]) == 5

def test_build_world_floor_4_rooms_dict_contains_eight_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_4"]) == 8

def test_build_world_floor_5_rooms_dict_contains_six_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_5"]) == 6

def test_build_world_floor_6_rooms_dict_contains_ten_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_6"]) == 10

def test_build_world_floor_7_rooms_dict_contains_three_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_7"]) == 3

def test_build_world_floor_8_rooms_dict_contains_two_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_8"]) == 2

def test_build_world_floor_9_rooms_dict_contains_one_room():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_9"]) == 1

def test_build_world_forge_of_prometheus_connects_to_bony_crypt_via_descend():
    dungeon, entrance, floors = build_world()
    forge = dungeon.get_room("Forge of Prometheus")
    assert forge is not None
    assert forge.get_exit("descend") is dungeon.get_room("Bony Crypt")

def test_build_world_bony_crypt_connects_back_to_forge_of_prometheus_via_ascend():
    dungeon, entrance, floors = build_world()
    bony_crypt = dungeon.get_room("Bony Crypt")
    assert bony_crypt is not None
    assert bony_crypt.get_exit("ascend") is dungeon.get_room("Forge of Prometheus")

def test_build_world_overgrown_forest_connects_to_labyrinth_via_descend():
    dungeon, entrance, floors = build_world()
    overgrown_forest = dungeon.get_room("Overgrown Forest")
    assert overgrown_forest is not None
    assert overgrown_forest.get_exit("descend") is dungeon.get_room("Labyrinth of the Minotaur")

def test_build_world_labyrinth_connects_back_to_overgrown_forest_via_ascend():
    dungeon, entrance, floors = build_world()
    labyrinth = dungeon.get_room("Labyrinth of the Minotaur")
    assert labyrinth is not None
    assert labyrinth.get_exit("ascend") is dungeon.get_room("Overgrown Forest")

def test_build_world_lair_of_medusa_connects_to_shadow_of_army_camp_via_descend():
    dungeon, entrance, floors = build_world()
    lair_of_medusa = dungeon.get_room("Lair of Medusa")
    assert lair_of_medusa is not None
    assert lair_of_medusa.get_exit("descend") is dungeon.get_room("Shadow of Army Camp")

def test_build_world_shadow_of_army_camp_connects_back_to_lair_of_medusa_via_ascend():
    dungeon, entrance, floors = build_world()
    shadow_of_army_camp = dungeon.get_room("Shadow of Army Camp")
    assert shadow_of_army_camp is not None
    assert shadow_of_army_camp.get_exit("ascend") is dungeon.get_room("Lair of Medusa")

def test_build_world_shadow_of_pylos_connects_to_bright_cave_via_descend():
    dungeon, entrance, floors = build_world()
    shadow_of_pylos = dungeon.get_room("Shadow of Pylos")
    assert shadow_of_pylos is not None
    assert shadow_of_pylos.get_exit("descend") is dungeon.get_room("Bright Cave")

def test_build_world_bright_cave_connects_back_to_shadow_of_pylos_via_ascend():
    dungeon, entrance, floors = build_world()
    bright_cave = dungeon.get_room("Bright Cave")
    assert bright_cave is not None
    assert bright_cave.get_exit("ascend") is dungeon.get_room("Shadow of Pylos")

def test_build_world_bedchamber_of_odysseus_connects_to_chamber_of_the_oracle_via_descend():
    dungeon, entrance, floors = build_world()
    bedchamber_of_odysseus = dungeon.get_room("Bedchamber of Odysseus")
    assert bedchamber_of_odysseus is not None
    assert bedchamber_of_odysseus.get_exit("descend") is dungeon.get_room("Chamber of the Oracle")

def test_build_world_chamber_of_the_oracle_connects_back_to_bedchamber_of_odysseus_via_ascend():
    dungeon, entrance, floors = build_world()
    chamber_of_the_oracle = dungeon.get_room("Chamber of the Oracle")
    assert chamber_of_the_oracle is not None
    assert chamber_of_the_oracle.get_exit("ascend") is dungeon.get_room("Bedchamber of Odysseus")

def test_build_world_bedchamber_of_persephone_connects_to_gate_of_cerberus_via_descend():
    dungeon, entrance, floors = build_world()
    bedchamber_of_persephone = dungeon.get_room("Bedchamber of Persephone")
    assert bedchamber_of_persephone is not None
    assert bedchamber_of_persephone.get_exit("descend") is dungeon.get_room("Gate of Cerberus")

def test_build_world_gate_of_cerberus_connects_back_to_bedchamber_of_persephone_via_ascend():
    dungeon, entrance, floors = build_world()
    gate_of_cerberus = dungeon.get_room("Gate of Cerberus")
    assert gate_of_cerberus is not None
    assert gate_of_cerberus.get_exit("ascend") is dungeon.get_room("Bedchamber of Persephone")

def test_build_world_hall_of_hades_connects_to_tartarus_via_descend():
    dungeon, entrance, floors = build_world()
    hall_of_hades = dungeon.get_room("Hall of Hades")
    assert hall_of_hades is not None
    assert hall_of_hades.get_exit("descend") is dungeon.get_room("Tartarus")

def test_build_world_tartarus_connects_back_to_hall_of_hades_via_ascend():
    dungeon, entrance, floors = build_world()
    tartarus = dungeon.get_room("Tartarus")
    assert tartarus is not None
    assert tartarus.get_exit("ascend") is dungeon.get_room("Hall of Hades")

def test_build_world_includes_trophy_room_of_zeus():
    dungeon, entrance, floors = build_world()
    assert dungeon.get_room("Trophy Room of Zeus") is not None

def test_build_world_trophy_room_of_zeus_is_part_of_floor_2():
    dungeon, entrance, floors = build_world()
    assert "Trophy Room of Zeus" in floors["floor_2"]

def test_build_world_armoury_of_ares_north_exit_to_trophy_room_is_hidden_until_revealed():
    dungeon, entrance, floors = build_world()
    armoury = dungeon.get_room("Armoury of Ares")
    assert armoury is not None
    assert armoury.get_exit("north") is None
    assert armoury.hidden_exits["north"] is dungeon.get_room("Trophy Room of Zeus")

def test_build_world_armoury_of_ares_north_exit_revealed_via_reveal_hidden_exits():
    dungeon, entrance, floors = build_world()
    armoury = dungeon.get_room("Armoury of Ares")
    assert armoury is not None
    armoury.reveal_hidden_exits()
    assert armoury.get_exit("north") is dungeon.get_room("Trophy Room of Zeus")

def test_build_world_trophy_room_of_zeus_connects_back_to_armoury_via_south():
    dungeon, entrance, floors = build_world()
    trophy_room = dungeon.get_room("Trophy Room of Zeus")
    assert trophy_room is not None
    assert trophy_room.get_exit("south") is dungeon.get_room("Armoury of Ares")

def test_build_world_includes_muddy_pigsty():
    dungeon, entrance, floors = build_world()
    assert dungeon.get_room("Muddy Pigsty") is not None

def test_build_world_muddy_pigsty_is_part_of_floor_6():
    dungeon, entrance, floors = build_world()
    assert "Muddy Pigsty" in floors["floor_6"]

def test_build_world_shadow_of_ithaca_connects_to_muddy_pigsty_via_east():
    dungeon, entrance, floors = build_world()
    shadow_of_ithaca = dungeon.get_room("Shadow of Ithaca")
    assert shadow_of_ithaca is not None
    assert shadow_of_ithaca.get_exit("east") is dungeon.get_room("Muddy Pigsty")

def test_build_world_muddy_pigsty_connects_back_to_shadow_of_ithaca_via_west():
    dungeon, entrance, floors = build_world()
    muddy_pigsty = dungeon.get_room("Muddy Pigsty")
    assert muddy_pigsty is not None
    assert muddy_pigsty.get_exit("west") is dungeon.get_room("Shadow of Ithaca")

def test_build_world_armoury_of_ares_has_examine_text():
    dungeon, entrance, floors = build_world()
    armoury = dungeon.get_room("Armoury of Ares")
    assert armoury is not None
    assert armoury.examine_text == "One section of the far wall looks less like stone, and more like it's been built to resemble stone."

def test_build_world_armoury_of_ares_required_intellect_is_three():
    dungeon, entrance, floors = build_world()
    armoury = dungeon.get_room("Armoury of Ares")
    assert armoury is not None
    assert armoury.required_intellect == 3

def test_build_world_styx_crossing_connects_to_library_of_athena_via_descend():
    dungeon, entrance, floors = build_world()
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert styx_crossing is not None
    assert styx_crossing.get_exit("descend") is dungeon.get_room("Library of Athena")

def test_build_world_library_of_athena_connects_back_to_styx_crossing_via_ascend():
    dungeon, entrance, floors = build_world()
    library_of_athena = dungeon.get_room("Library of Athena")
    styx_crossing = dungeon.get_room("Styx Crossing")
    assert library_of_athena is not None
    assert library_of_athena.get_exit("ascend") is styx_crossing

def test_build_floor_0_returns_chamber_of_chiron_as_start_room():
    start, rooms = build_floor_0()
    assert start.name == "Chamber of Chiron"

def test_build_floor_0_returns_rooms_dict_with_five_rooms():
    start, rooms = build_floor_0()
    assert len(rooms) == 5

def test_build_floor_0_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_0()
    assert rooms["Chamber of Chiron"] is start

def test_build_floor_1_returns_cave_entrance_as_start_room():
    start, rooms = build_floor_1()
    assert start.name == "Cave Entrance"

def test_build_floor_1_returns_rooms_dict_with_four_rooms():
    start, rooms = build_floor_1()
    assert len(rooms) == 4

def test_build_floor_1_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_1()
    assert rooms["Cave Entrance"] is start

def test_build_floor_2_returns_library_of_athena_as_start_room():
    start, rooms = build_floor_2()
    assert start.name == "Library of Athena"

def test_build_floor_2_returns_rooms_dict_with_five_rooms():
    start, rooms = build_floor_2()
    assert len(rooms) == 5

def test_build_floor_2_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_2()
    assert rooms["Library of Athena"] is start

def test_build_floor_2_library_connects_to_armoury_via_west():
    start, rooms = build_floor_2()
    assert start.get_exit("west") is rooms["Armoury of Ares"]

def test_build_floor_2_armoury_connects_back_to_library_via_east():
    start, rooms = build_floor_2()
    armoury = rooms["Armoury of Ares"]
    assert armoury.get_exit("east") is start

def test_build_floor_2_library_connects_to_hall_of_hermes_via_south():
    start, rooms = build_floor_2()
    assert start.get_exit("south") is rooms["Hall of Hermes"]

def test_build_floor_2_hall_of_hermes_connects_back_to_library_via_north():
    start, rooms = build_floor_2()
    hall_of_hermes = rooms["Hall of Hermes"]
    assert hall_of_hermes.get_exit("north") is start

def test_build_floor_2_hall_of_hermes_connects_to_forge_via_south():
    start, rooms = build_floor_2()
    hall_of_hermes = rooms["Hall of Hermes"]
    assert hall_of_hermes.get_exit("south") is rooms["Forge of Prometheus"]

def test_build_floor_2_forge_connects_back_to_hall_of_hermes_via_north():
    start, rooms = build_floor_2()
    forge = rooms["Forge of Prometheus"]
    assert forge.get_exit("north") is rooms["Hall of Hermes"]

def test_build_floor_3_returns_bony_crypt_as_start_room():
    start, rooms = build_floor_3()
    assert start.name == "Bony Crypt"

def test_build_floor_3_returns_rooms_dict_with_five_rooms():
    start, rooms = build_floor_3()
    assert len(rooms) == 5

def test_build_floor_3_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_3()
    assert rooms["Bony Crypt"] is start

def test_build_floor_3_bony_crypt_connects_to_cave_of_harpies_via_south():
    start, rooms = build_floor_3()
    assert rooms["Bony Crypt"].get_exit("south") is rooms["Cave of Harpies"]

def test_build_floor_3_cave_of_harpies_connects_to_bony_crypt_via_north():
    start, rooms = build_floor_3()
    assert rooms["Cave of Harpies"].get_exit("north") is rooms["Bony Crypt"]

def test_build_floor_3_cave_of_harpies_connects_to_prayer_room_via_east():
    start, rooms = build_floor_3()
    assert rooms["Cave of Harpies"].get_exit("east") is rooms["Prayer Room"]

def test_build_floor_3_cave_of_harpies_connects_to_dim_corridor_via_south():
    start, rooms = build_floor_3()
    assert rooms["Cave of Harpies"].get_exit("south") is rooms["Dim Corridor"]

def test_build_floor_3_prayer_room_connects_to_cave_of_harpies_via_west():
    start, rooms = build_floor_3()
    assert rooms["Prayer Room"].get_exit("west") is rooms["Cave of Harpies"]

def test_build_floor_3_dim_corridor_connects_to_cave_of_harpies_via_north():
    start, rooms = build_floor_3()
    assert rooms["Dim Corridor"].get_exit("north") is rooms["Cave of Harpies"]

def test_build_floor_3_dim_corridor_connects_to_overgrown_forest_via_south():
    start, rooms = build_floor_3()
    assert rooms["Dim Corridor"].get_exit("south") is rooms["Overgrown Forest"]

def test_build_floor_3_overgrown_forest_connects_to_dim_corridor_via_north():
    start, rooms = build_floor_3()
    assert rooms["Overgrown Forest"].get_exit("north") is rooms["Dim Corridor"]

def test_build_floor_4_returns_labyrinth_of_the_minotaur_as_start_room():
    start, rooms = build_floor_4()
    assert start.name == "Labyrinth of the Minotaur"

def test_build_floor_4_returns_rooms_dict_with_eight_rooms():
    start, rooms = build_floor_4()
    assert len(rooms) == 8

def test_build_floor_4_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_4()
    assert rooms["Labyrinth of the Minotaur"] is start

def test_build_floor_4_labyrinth_of_the_minotaur_connects_to_stony_lair_via_west():
    start, rooms = build_floor_4()
    assert rooms["Labyrinth of the Minotaur"].get_exit("west") is rooms["Stony Lair"]

def test_build_floor_4_labyrinth_of_the_minotaur_connects_to_cavern_of_the_cyclops_via_east():
    start, rooms = build_floor_4()
    assert rooms["Labyrinth of the Minotaur"].get_exit("east") is rooms["Cavern of the Cyclops"]

def test_build_floor_4_labyrinth_of_the_minotaur_connects_to_mossy_grove_via_south():
    start, rooms = build_floor_4()
    assert rooms["Labyrinth of the Minotaur"].get_exit("south") is rooms["Mossy Grove"]

def test_build_floor_4_stony_lair_connects_to_labyrinth_of_the_minotaur_via_east():
    start, rooms = build_floor_4()
    assert rooms["Stony Lair"].get_exit("east") is rooms["Labyrinth of the Minotaur"]

def test_build_floor_4_cavern_of_the_cyclops_connects_to_labyrinth_of_the_minotaur_via_west():
    start, rooms = build_floor_4()
    assert rooms["Cavern of the Cyclops"].get_exit("west") is rooms["Labyrinth of the Minotaur"]

def test_build_floor_4_mossy_grove_connects_to_labyrinth_of_the_minotaur_via_north():
    start, rooms = build_floor_4()
    assert rooms["Mossy Grove"].get_exit("north") is rooms["Labyrinth of the Minotaur"]

def test_build_floor_4_mossy_grove_connects_to_shadowy_corner_via_west():
    start, rooms = build_floor_4()
    assert rooms["Mossy Grove"].get_exit("west") is rooms["Shadowy Corner"]

def test_build_floor_4_mossy_grove_connects_to_sandy_expanse_via_south():
    start, rooms = build_floor_4()
    assert rooms["Mossy Grove"].get_exit("south") is rooms["Sandy Expanse"]

def test_build_floor_4_shadowy_corner_connects_to_mossy_grove_via_east():
    start, rooms = build_floor_4()
    assert rooms["Shadowy Corner"].get_exit("east") is rooms["Mossy Grove"]

def test_build_floor_4_sandy_expanse_connects_to_mossy_grove_via_north():
    start, rooms = build_floor_4()
    assert rooms["Sandy Expanse"].get_exit("north") is rooms["Mossy Grove"]

def test_build_floor_4_sandy_expanse_connects_to_maze_of_pillars_via_east():
    start, rooms = build_floor_4()
    assert rooms["Sandy Expanse"].get_exit("east") is rooms["Maze of Pillars"]

def test_build_floor_4_maze_of_pillars_connects_to_sandy_expanse_via_west():
    start, rooms = build_floor_4()
    assert rooms["Maze of Pillars"].get_exit("west") is rooms["Sandy Expanse"]

def test_build_floor_4_maze_of_pillars_connects_to_lair_of_medusa_via_south():
    start, rooms = build_floor_4()
    assert rooms["Maze of Pillars"].get_exit("south") is rooms["Lair of Medusa"]

def test_build_floor_4_lair_of_medusa_connects_to_maze_of_pillars_via_north():
    start, rooms = build_floor_4()
    assert rooms["Lair of Medusa"].get_exit("north") is rooms["Maze of Pillars"]

def test_build_floor_5_returns_shadow_of_army_camp_as_start_room():
    start, rooms = build_floor_5()
    assert start.name == "Shadow of Army Camp"

def test_build_floor_5_returns_rooms_dict_with_six_rooms():
    start, rooms = build_floor_5()
    assert len(rooms) == 6

def test_build_floor_5_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Army Camp"] is start

def test_build_floor_5_shadow_of_army_camp_connects_to_shadow_of_troy_north_via_south():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Army Camp"].get_exit("south") is rooms["Shadow of Troy (North)"]

def test_build_floor_5_shadow_of_troy_north_connects_to_shadow_of_army_camp_via_north():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (North)"].get_exit("north") is rooms["Shadow of Army Camp"]

def test_build_floor_5_shadow_of_troy_north_connects_to_shadow_of_troy_central_via_south():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (North)"].get_exit("south") is rooms["Shadow of Troy (Central)"]

def test_build_floor_5_shadow_of_troy_central_connects_to_shadow_of_troy_north_via_north():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (Central)"].get_exit("north") is rooms["Shadow of Troy (North)"]

def test_build_floor_5_shadow_of_troy_central_connects_to_shadow_of_troy_alleyway_via_west():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (Central)"].get_exit("west") is rooms["Shadow of Troy (Alleyway)"]

def test_build_floor_5_shadow_of_troy_alleyway_connects_to_shadow_of_troy_central_via_east():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (Alleyway)"].get_exit("east") is rooms["Shadow of Troy (Central)"]

def test_build_floor_5_shadow_of_troy_alleyway_connects_to_shadow_of_troy_south_via_south():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (Alleyway)"].get_exit("south") is rooms["Shadow of Troy (South)"]

def test_build_floor_5_shadow_of_troy_south_connects_to_shadow_of_troy_alleyway_via_north():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (South)"].get_exit("north") is rooms["Shadow of Troy (Alleyway)"]

def test_build_floor_5_shadow_of_troy_south_connects_to_shadow_of_pylos_via_east():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Troy (South)"].get_exit("east") is rooms["Shadow of Pylos"]

def test_build_floor_5_shadow_of_pylos_connects_to_shadow_of_troy_south_via_west():
    start, rooms = build_floor_5()
    assert rooms["Shadow of Pylos"].get_exit("west") is rooms["Shadow of Troy (South)"]

def test_build_floor_6_returns_bright_cave_as_start_room():
    start, rooms = build_floor_6()
    assert start.name == "Bright Cave"

def test_build_floor_6_returns_rooms_dict_with_ten_rooms():
    start, rooms = build_floor_6()
    assert len(rooms) == 10

def test_build_floor_6_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_6()
    assert rooms["Bright Cave"] is start

def test_build_floor_6_bright_cave_connects_to_calm_waters_via_south():
    start, rooms = build_floor_6()
    assert rooms["Bright Cave"].get_exit("south") is rooms["Calm Waters"]

def test_build_floor_6_calm_waters_connects_to_bright_cave_via_north():
    start, rooms = build_floor_6()
    assert rooms["Calm Waters"].get_exit("north") is rooms["Bright Cave"]

def test_build_floor_6_calm_waters_connects_to_cavern_of_polyphemus_via_east():
    start, rooms = build_floor_6()
    assert rooms["Calm Waters"].get_exit("east") is rooms["Cavern of Polyphemus"]

def test_build_floor_6_calm_waters_connects_to_rocky_shore_via_west():
    start, rooms = build_floor_6()
    assert rooms["Calm Waters"].get_exit("west") is rooms["Rocky Shore"]

def test_build_floor_6_cavern_of_polyphemus_connects_to_calm_waters_via_west():
    start, rooms = build_floor_6()
    assert rooms["Cavern of Polyphemus"].get_exit("west") is rooms["Calm Waters"]

def test_build_floor_6_rocky_shore_connects_to_calm_waters_via_east():
    start, rooms = build_floor_6()
    assert rooms["Rocky Shore"].get_exit("east") is rooms["Calm Waters"]

def test_build_floor_6_rocky_shore_connects_to_narrow_river_via_south():
    start, rooms = build_floor_6()
    assert rooms["Rocky Shore"].get_exit("south") is rooms["Narrow River"]

def test_build_floor_6_narrow_river_connects_to_rocky_shore_via_north():
    start, rooms = build_floor_6()
    assert rooms["Narrow River"].get_exit("north") is rooms["Rocky Shore"]

def test_build_floor_6_narrow_river_connects_to_poseidons_depths_via_south():
    start, rooms = build_floor_6()
    assert rooms["Narrow River"].get_exit("south") is rooms["Poseidon's Depths"]

def test_build_floor_6_poseidons_depths_connects_to_narrow_river_via_north():
    start, rooms = build_floor_6()
    assert rooms["Poseidon's Depths"].get_exit("north") is rooms["Narrow River"]

def test_build_floor_6_poseidons_depths_connects_to_shadow_of_ithaca_via_east():
    start, rooms = build_floor_6()
    assert rooms["Poseidon's Depths"].get_exit("east") is rooms["Shadow of Ithaca"]

def test_build_floor_6_shadow_of_ithaca_connects_to_poseidons_depths_via_west():
    start, rooms = build_floor_6()
    assert rooms["Shadow of Ithaca"].get_exit("west") is rooms["Poseidon's Depths"]

def test_build_floor_6_shadow_of_ithaca_connects_to_muddy_pigsty_via_east():
    start, rooms = build_floor_6()
    assert rooms["Shadow of Ithaca"].get_exit("east") is rooms["Muddy Pigsty"]

def test_build_floor_6_shadow_of_ithaca_connects_to_throne_room_of_odysseus_via_south():
    start, rooms = build_floor_6()
    assert rooms["Shadow of Ithaca"].get_exit("south") is rooms["Throne Room of Odysseus"]

def test_build_floor_6_muddy_pigsty_connects_to_shadow_of_ithaca_via_west():
    start, rooms = build_floor_6()
    assert rooms["Muddy Pigsty"].get_exit("west") is rooms["Shadow of Ithaca"]

def test_build_floor_6_throne_room_of_odysseus_connects_to_shadow_of_ithaca_via_north():
    start, rooms = build_floor_6()
    assert rooms["Throne Room of Odysseus"].get_exit("north") is rooms["Shadow of Ithaca"]

def test_build_floor_6_throne_room_of_odysseus_connects_to_bedchamber_of_odysseus_via_west():
    start, rooms = build_floor_6()
    assert rooms["Throne Room of Odysseus"].get_exit("west") is rooms["Bedchamber of Odysseus"]

def test_build_floor_6_bedchamber_of_odysseus_connects_to_throne_room_of_odysseus_via_east():
    start, rooms = build_floor_6()
    assert rooms["Bedchamber of Odysseus"].get_exit("east") is rooms["Throne Room of Odysseus"]

def test_build_floor_7_returns_chamber_of_the_oracle_as_start_room():
    start, rooms = build_floor_7()
    assert start.name == "Chamber of the Oracle"

def test_build_floor_7_returns_rooms_dict_with_three_rooms():
    start, rooms = build_floor_7()
    assert len(rooms) == 3

def test_build_floor_7_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_7()
    assert rooms["Chamber of the Oracle"] is start

def test_build_floor_7_chamber_of_the_oracle_connects_to_shadow_of_thebes_via_south():
    start, rooms = build_floor_7()
    assert rooms["Chamber of the Oracle"].get_exit("south") is rooms["Shadow of Thebes"]

def test_build_floor_7_shadow_of_thebes_connects_to_chamber_of_the_oracle_via_north():
    start, rooms = build_floor_7()
    assert rooms["Shadow of Thebes"].get_exit("north") is rooms["Chamber of the Oracle"]

def test_build_floor_7_shadow_of_thebes_connects_to_bedchamber_of_persephone_via_south():
    start, rooms = build_floor_7()
    assert rooms["Shadow of Thebes"].get_exit("south") is rooms["Bedchamber of Persephone"]

def test_build_floor_7_bedchamber_of_persephone_connects_to_shadow_of_thebes_via_north():
    start, rooms = build_floor_7()
    assert rooms["Bedchamber of Persephone"].get_exit("north") is rooms["Shadow of Thebes"]

def test_build_floor_8_returns_gate_of_cerberus_as_start_room():
    start, rooms = build_floor_8()
    assert start.name == "Gate of Cerberus"

def test_build_floor_8_returns_rooms_dict_with_two_rooms():
    start, rooms = build_floor_8()
    assert len(rooms) == 2

def test_build_floor_8_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_8()
    assert rooms["Gate of Cerberus"] is start

def test_build_floor_8_gate_of_cerberus_connects_to_hall_of_hades_via_south():
    start, rooms = build_floor_8()
    assert rooms["Gate of Cerberus"].get_exit("south") is rooms["Hall of Hades"]

def test_build_floor_8_hall_of_hades_connects_to_gate_of_cerberus_via_north():
    start, rooms = build_floor_8()
    assert rooms["Hall of Hades"].get_exit("north") is rooms["Gate of Cerberus"]

def test_build_floor_9_returns_tartarus_as_start_room():
    start, rooms = build_floor_9()
    assert start.name == "Tartarus"

def test_build_floor_9_returns_rooms_dict_with_one_rooms():
    start, rooms = build_floor_9()
    assert len(rooms) == 1

def test_build_floor_9_rooms_dict_keyed_by_room_name():
    start, rooms = build_floor_9()
    assert rooms["Tartarus"] is start
