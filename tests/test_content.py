from dungeon_crawler.content import create_suitor, create_antinous, create_eurymachus, create_antinous_goblet, create_penelope, create_penelopes_thread, create_circe, create_nestor, create_poseidon, create_hippocampus, create_poseidon_earth_shaker, create_trident_of_the_depths, create_kelp_poultice, create_odysseus, create_charybdis, create_hoplon_of_the_drowned, resolve_charybdis_action, CHARYBDIS_PHASES, create_polyphemus, create_polyphemus_blinded, create_olive_wood_stake, create_wheel_of_cheese, create_head_of_scylla, create_boars_tusk_helm, ANCESTRIES, create_laestrygonian, create_antiphates, create_laestrygonian_hide, create_antiphates_club, create_shade_of_ajax, create_tower_shield_of_ajax, create_myrmidon_soldier, create_field_dressing, create_shade_of_paris, create_bow_of_paris, create_nestor, create_cup_of_kykeon, create_shade_of_hector, create_hectors_helm, create_shade_of_achilles, create_shade_of_achilles_duellist, create_ambrosia, create_ares, create_athena, create_breastplate_of_athena, create_bronze_breastplate, create_bronze_xiphos, create_centaur, create_centaurs_broken_bow, create_charon, create_charons_coin, create_chiron, create_chipped_stone_aegis, create_crypt_keeper, create_cyclops_eye, create_ember_wraith, create_fanatic, create_harpy, create_gorgon, create_harpy_fletched_bow, create_lamia, create_lamias_fang, create_lurker, create_medusa, create_medusa_awakened, create_petrified_guardian, create_prayer_bolt, create_satyr, create_serpents_kiss, create_sunscorched_dagger, create_talos, create_talos_bronze_plating, create_tome_of_old_prayers, create_wineskin_of_dionysus, create_cyclops, create_dummy_head, create_hades, create_hermes, create_hermes_favour, create_labrys, create_mentor, create_mentors_token, create_minotaur, create_prometheus, create_shade, create_skeleton_bone, create_skeleton_warrior, create_small_healing_potion, create_spear_of_ares, create_practice_dummy, create_training_dummy, create_vial_of_grave_rot, create_weathered_helm, create_wooden_shield, create_wooden_sword, create_wounded_soldier, build_world, build_floor_0, build_floor_1, build_floor_2, build_floor_3, build_floor_4, build_floor_5, build_floor_6, build_floor_7, build_floor_8, build_floor_9, build_blank_test_room, build_companion_test_camp, create_test_companion, create_test_spell, create_test_spellbook, create_test_healing_tonic, create_test_venom_vial, create_test_boss, ANCESTRIES
from dungeon_crawler.characters import Player, Companion, Enemy
from dungeon_crawler.world import Room
from dungeon_crawler.exploration import talk_to, get_story_gate
from dungeon_crawler.dialogue import continue_dialogue
from dungeon_crawler.content import create_oracle, create_tiresias, create_persephone, create_pomegranate, ORACLE_TWIST, ORACLE_PHRASES, ORACLE_NOTHING_STRANGE, PROMISED_MERCY, REFUSED_MERCY
from dungeon_crawler.dev_tools import find_item_by_name, ALLY_REGISTRY
from dungeon_crawler.items import LoyaltyToken, QuestItem, StatusEffectItem, Weapon, SpellBook, Armour


def test_create_minotaur_has_correct_stats():
    minotaur = create_minotaur()
    assert minotaur.name == "Minotaur"
    assert minotaur.hp == 28
    assert minotaur.attack_damage == 8
    assert minotaur.armour == 3
    assert len(minotaur.loot) == 1
    assert minotaur.experience_reward == 30
    assert minotaur.gold_reward == 18

def test_create_minotaur_drops_labrys():
    minotaur = create_minotaur()
    message = minotaur.on_death()
    assert "Labrys" in message

def test_create_minotaur_has_correct_defensive_ai_stats():
    minotaur = create_minotaur()
    assert minotaur.brace_amount == 3
    assert minotaur.heal_amount == 0

def test_create_labrys_has_correct_damage_and_description():
    labrys = create_labrys()
    assert labrys.name == "Labrys"
    assert labrys.description == "Two crescent blades on a single haft, heavy enough that every swing feels like it's pulling you along with it."
    assert labrys.damage == 7
    assert labrys.slot == "melee"

def test_create_centaur_has_correct_stats():
    centaur = create_centaur()
    assert centaur.name == "Centaur"
    assert centaur.hp == 18
    assert centaur.attack_damage == 6
    assert centaur.armour == 1
    assert len(centaur.loot) == 1
    assert centaur.experience_reward == 10
    assert centaur.gold_reward == 5

def test_create_centaur_drops_centaurs_broken_bow():
    centaur = create_centaur()
    message = centaur.on_death()
    assert "Centaur's Broken Bow" in message

def test_create_cyclops_has_correct_stats():
    cyclops = create_cyclops()
    assert cyclops.name == "Cyclops"
    assert cyclops.hp == 22
    assert cyclops.attack_damage == 7
    assert cyclops.armour == 1
    assert len(cyclops.loot) == 1
    assert cyclops.experience_reward == 25
    assert cyclops.gold_reward == 15

def test_create_cyclops_drops_cyclops_eye():
    cyclops = create_cyclops()
    message = cyclops.on_death()
    assert "Cyclops' Eye" in message

def test_create_shade_has_correct_stats():
    shade = create_shade()
    assert shade.name == "Shade"
    assert shade.hp == 7
    assert shade.attack_damage == 4
    assert shade.armour == 0
    assert len(shade.loot) == 1
    assert shade.experience_reward == 4
    assert shade.gold_reward == 1

def test_create_shade_drops_weathered_helm():
    shade = create_shade()
    message = shade.on_death()
    assert "Weathered Helm" in message

def test_create_crypt_keeper_has_correct_stats():
    keeper = create_crypt_keeper()
    assert keeper.name == "Crypt Keeper"
    assert keeper.hp == 16
    assert keeper.attack_damage == 6
    assert keeper.armour == 1
    assert len(keeper.loot) == 2
    assert keeper.experience_reward == 12
    assert keeper.gold_reward == 6

def test_create_crypt_keeper_drops_vial_of_grave_rot():
    keeper = create_crypt_keeper()
    message = keeper.on_death()
    assert "Vial of Grave Rot" in message

def test_create_crypt_keeper_drops_small_healing_potion():
    keeper = create_crypt_keeper()
    message = keeper.on_death()
    assert "Small Healing Potion" in message

def test_create_vial_of_grave_rot_has_correct_name_and_description():
    vial = create_vial_of_grave_rot()
    assert vial.name == "Vial of Grave Rot"
    assert vial.description == "Thick, dark, and faintly luminous - whatever's in here hasn't been alive for a very long time."

def test_create_vial_of_grave_rot_applies_a_three_turn_poison():
    vial = create_vial_of_grave_rot()
    assert vial.effect_name == "Poison"
    assert vial.amount == -3
    assert vial.duration == 3

def test_create_vial_of_grave_rot_is_a_status_effect_item():
    vial = create_vial_of_grave_rot()
    assert isinstance(vial, StatusEffectItem)

def test_create_harpy_has_correct_stats():
    harpy = create_harpy()
    assert harpy.name == "Harpy"
    assert harpy.hp == 13
    assert harpy.attack_damage == 7
    assert harpy.armour == 0
    assert len(harpy.loot) == 1
    assert harpy.experience_reward == 11
    assert harpy.gold_reward == 4

def test_create_harpy_has_raised_aggression_weight():
    harpy = create_harpy()
    assert harpy.aggression_weight == 1.5

def test_create_harpy_drops_harpy_fletched_bow():
    harpy = create_harpy()
    message = harpy.on_death()
    assert "Harpy-fletched Bow" in message

def test_create_harpy_fletched_bow_has_correct_stats():
    bow = create_harpy_fletched_bow()
    assert bow.name == "Harpy-fletched Bow"
    assert bow.damage == 4

def test_create_harpy_fletched_bow_occupies_the_ranged_slot():
    bow = create_harpy_fletched_bow()
    assert isinstance(bow, Weapon)
    assert bow.slot == "ranged"

def test_create_harpy_fletched_bow_equips_into_the_ranged_slot():
    player = Player(name="hero", hp=100)
    bow = create_harpy_fletched_bow()
    bow.use(player)
    assert player.equipped_ranged_weapon is bow
    assert player.equipped_melee_weapon is None

def test_create_fanatic_has_correct_stats():
    fanatic = create_fanatic()
    assert fanatic.name == "Fanatic"
    assert fanatic.hp == 15
    assert fanatic.attack_damage == 6
    assert fanatic.armour == 0
    assert len(fanatic.loot) == 1
    assert fanatic.experience_reward == 13
    assert fanatic.gold_reward == 7

def test_create_fanatic_drops_tome_of_old_prayers():
    fanatic = create_fanatic()
    message = fanatic.on_death()
    assert "Tome of Old Prayers" in message

def test_create_prayer_bolt_has_correct_stats():
    spell = create_prayer_bolt()
    assert spell.name == "Prayer Bolt"
    assert spell.mana_cost == 6
    assert spell.damage == 8

def test_create_tome_of_old_prayers_is_a_spell_book_teaching_prayer_bolt():
    tome = create_tome_of_old_prayers()
    assert isinstance(tome, SpellBook)
    assert tome.spell.name == "Prayer Bolt"

def test_create_tome_of_old_prayers_use_teaches_prayer_bolt():
    player = Player(name="hero", hp=100)
    tome = create_tome_of_old_prayers()
    tome.use(player)
    assert [spell.name for spell in player.known_spells] == ["Prayer Bolt"]

def test_create_lurker_has_correct_stats():
    lurker = create_lurker()
    assert lurker.name == "Lurker"
    assert lurker.hp == 17
    assert lurker.attack_damage == 7
    assert lurker.armour == 1
    assert len(lurker.loot) == 1
    assert lurker.experience_reward == 14
    assert lurker.gold_reward == 8

def test_create_lurker_drops_small_healing_potion():
    lurker = create_lurker()
    message = lurker.on_death()
    assert "Small Healing Potion" in message

def test_create_petrified_guardian_has_correct_stats():
    guardian = create_petrified_guardian()
    assert guardian.name == "Petrified Guardian"
    assert guardian.hp == 18
    assert guardian.attack_damage == 6
    assert guardian.armour == 3
    assert len(guardian.loot) == 2
    assert guardian.experience_reward == 16
    assert guardian.gold_reward == 9

def test_create_petrified_guardian_drops_chipped_stone_aegis():
    guardian = create_petrified_guardian()
    message = guardian.on_death()
    assert "Chipped Stone Aegis" in message

def test_create_petrified_guardian_drops_small_healing_potion():
    guardian = create_petrified_guardian()
    message = guardian.on_death()
    assert "Small Healing Potion" in message

def test_create_chipped_stone_aegis_has_correct_defence_and_occupies_the_shield_slot():
    aegis = create_chipped_stone_aegis()
    assert isinstance(aegis, Armour)
    assert aegis.name == "Chipped Stone Aegis"
    assert aegis.defence == 3
    assert aegis.slot == "shield"

def test_create_chipped_stone_aegis_has_correct_max_durability():
    aegis = create_chipped_stone_aegis()
    assert aegis.max_durability == 10

def test_create_satyr_has_correct_stats():
    satyr = create_satyr()
    assert satyr.name == "Satyr"
    assert satyr.hp == 26
    assert satyr.attack_damage == 6
    assert satyr.armour == 1
    assert len(satyr.loot) == 1
    assert satyr.experience_reward == 14
    assert satyr.gold_reward == 8

def test_create_satyr_drops_wineskin_of_dionysus():
    satyr = create_satyr()
    message = satyr.on_death()
    assert "Wineskin of Dionysus" in message

def test_create_wineskin_of_dionysus_applies_a_three_turn_regen():
    wineskin = create_wineskin_of_dionysus()
    assert isinstance(wineskin, StatusEffectItem)
    assert wineskin.effect_name == "Regen"
    assert wineskin.amount == 3
    assert wineskin.duration == 3

def test_create_wineskin_of_dionysus_use_applies_regen_to_the_user():
    player = Player(name="hero", hp=100)
    wineskin = create_wineskin_of_dionysus()
    wineskin.use(player)
    assert [effect.name for effect in player.active_effects] == ["Regen"]

def test_create_wineskin_of_dionysus_is_a_free_action_mid_combat():
    player = Player(name="hero", hp=100)
    wineskin = create_wineskin_of_dionysus()
    assert wineskin.ends_turn(player) is False

def test_create_lamia_has_correct_stats():
    lamia = create_lamia()
    assert lamia.name == "Lamia"
    assert lamia.hp == 30
    assert lamia.attack_damage == 7
    assert lamia.armour == 1
    assert len(lamia.loot) == 1
    assert lamia.experience_reward == 18
    assert lamia.gold_reward == 10

def test_create_lamia_has_lifesteal():
    lamia = create_lamia()
    assert lamia.has_lifesteal is True

def test_create_lamia_attack_drains_hp_from_the_target():
    lamia = create_lamia()
    lamia.hp = 5
    player = Player(name="hero", hp=100)
    lamia.attack(player)
    assert lamia.hp == 8  # 7 damage dealt (no armour), heals 7 // 2

def test_create_ember_wraith_has_correct_stats():
    wraith = create_ember_wraith()
    assert wraith.name == "Ember Wraith"
    assert wraith.hp == 28
    assert wraith.attack_damage == 7
    assert wraith.armour == 1
    assert len(wraith.loot) == 1
    assert wraith.experience_reward == 17
    assert wraith.gold_reward == 9

def test_create_ember_wraith_drops_sunscorched_dagger():
    wraith = create_ember_wraith()
    message = wraith.on_death()
    assert "Sun-scorched Dagger" in message

def test_create_sunscorched_dagger_has_correct_damage_and_defaults_to_melee_slot():
    dagger = create_sunscorched_dagger()
    assert isinstance(dagger, Weapon)
    assert dagger.name == "Sun-scorched Dagger"
    assert dagger.damage == 5
    assert dagger.slot == "melee"

def test_create_talos_has_correct_stats():
    talos = create_talos()
    assert talos.name == "Talos"
    assert talos.hp == 30
    assert talos.attack_damage == 9
    assert talos.armour == 3
    assert len(talos.loot) == 1
    assert talos.experience_reward == 35
    assert talos.gold_reward == 20

def test_create_talos_drops_talos_bronze_plating():
    talos = create_talos()
    message = talos.on_death()
    assert "Talos' Bronze Plating" in message

def test_create_talos_bronze_plating_has_correct_defence_and_defaults_to_body_slot():
    plating = create_talos_bronze_plating()
    assert isinstance(plating, Armour)
    assert plating.name == "Talos' Bronze Plating"
    assert plating.defence == 6
    assert plating.slot == "body"

def test_create_talos_bronze_plating_has_correct_max_durability():
    plating = create_talos_bronze_plating()
    assert plating.max_durability == 18

def test_create_medusa_has_correct_stats():
    medusa = create_medusa()
    assert medusa.name == "Medusa"
    assert medusa.hp == 25
    assert medusa.attack_damage == 6
    assert medusa.armour == 2

def test_create_medusa_has_two_gorgon_wave_add_factories():
    medusa = create_medusa()
    assert len(medusa.next_wave_factories) == 2
    adds = [factory() for factory in medusa.next_wave_factories]
    assert [add.name for add in adds] == ["Gorgon", "Gorgon"]

def test_create_medusa_next_phase_factory_produces_medusa_awakened():
    medusa = create_medusa()
    awakened = medusa.next_phase_factory()
    assert awakened.name == "Medusa (Awakened)"

def test_create_gorgon_has_correct_stats():
    gorgon = create_gorgon()
    assert gorgon.name == "Gorgon"
    assert gorgon.hp == 12
    assert gorgon.attack_damage == 5
    assert gorgon.armour == 1
    assert len(gorgon.loot) == 1
    assert gorgon.experience_reward == 8
    assert gorgon.gold_reward == 4

def test_create_gorgon_drops_small_healing_potion():
    gorgon = create_gorgon()
    message = gorgon.on_death()
    assert "Small Healing Potion" in message

def test_create_medusa_awakened_has_correct_stats():
    awakened = create_medusa_awakened()
    assert awakened.name == "Medusa (Awakened)"
    assert awakened.hp == 35
    assert awakened.attack_damage == 8
    assert awakened.armour == 3
    assert len(awakened.loot) == 1
    assert awakened.experience_reward == 40
    assert awakened.gold_reward == 25

def test_create_medusa_awakened_has_petrifying_gaze():
    awakened = create_medusa_awakened()
    assert awakened.has_petrifying_gaze is True

def test_create_medusa_awakened_has_correct_defensive_ai_stats():
    awakened = create_medusa_awakened()
    assert awakened.heal_amount == 2
    assert awakened.brace_amount == 2
    assert awakened.caution_weight == 1.2

def test_create_medusa_awakened_drops_serpents_kiss():
    awakened = create_medusa_awakened()
    message = awakened.on_death()
    assert "Serpent's Kiss" in message

def test_create_serpents_kiss_has_correct_damage_and_defaults_to_melee_slot():
    kiss = create_serpents_kiss()
    assert isinstance(kiss, Weapon)
    assert kiss.name == "Serpent's Kiss"
    assert kiss.damage == 6
    assert kiss.slot == "melee"

def test_create_lamia_drops_lamias_fang():
    lamia = create_lamia()
    message = lamia.on_death()
    assert "Lamia's Fang" in message

def test_create_lamias_fang_has_correct_damage_and_defaults_to_melee_slot():
    fang = create_lamias_fang()
    assert isinstance(fang, Weapon)
    assert fang.name == "Lamia's Fang"
    assert fang.damage == 4
    assert fang.slot == "melee"

def test_create_skeleton_warrior_has_correct_stats():
    skeleton_warrior = create_skeleton_warrior()
    assert skeleton_warrior.name == "Skeleton Warrior"
    assert skeleton_warrior.hp == 8
    assert skeleton_warrior.attack_damage == 4
    assert skeleton_warrior.armour == 0
    assert len(skeleton_warrior.loot) == 2
    assert skeleton_warrior.experience_reward == 5
    assert skeleton_warrior.gold_reward == 2

def test_create_skeleton_warrior_drops_small_healing_potion():
    skeleton_warrior = create_skeleton_warrior()
    message = skeleton_warrior.on_death()
    assert "Small Healing Potion" in message

def test_create_skeleton_warrior_drops_skeleton_bone():
    skeleton_warrior = create_skeleton_warrior()
    message = skeleton_warrior.on_death()
    assert "Skeleton Bone" in message

def test_create_skeleton_bone_has_correct_name_and_description():
    bone = create_skeleton_bone()
    assert bone.name == "Skeleton Bone"
    assert bone.description == "Picked clean, oddly light - the kind of thing a god who deals in messages and thresholds might want as proof of passage."

def test_create_skeleton_bone_is_a_quest_item():
    bone = create_skeleton_bone()
    assert isinstance(bone, QuestItem)


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

def test_create_weathered_helm_has_correct_defence_and_description():
    helm = create_weathered_helm()
    assert helm.name == "Weathered Helm"
    assert helm.description == "Bronze gone dull and pitted, but the shape still holds - whoever wore it last isn't wearing it now."
    assert helm.defence == 1

def test_create_weathered_helm_occupies_the_helmet_slot():
    helm = create_weathered_helm()
    assert helm.slot == "helmet"

def test_create_weathered_helm_has_correct_max_durability():
    helm = create_weathered_helm()
    assert helm.max_durability == 5

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

def test_create_practice_dummy_has_correct_stats():
    practice_dummy = create_practice_dummy()
    assert practice_dummy.name == "Practice Enemy"
    assert practice_dummy.hp == 20
    assert practice_dummy.attack_damage == 1
    assert practice_dummy.armour == 0
    assert practice_dummy.experience_reward == 0
    assert practice_dummy.gold_reward == 0

def test_create_practice_dummy_respawns():
    practice_dummy = create_practice_dummy()
    assert practice_dummy.respawns is True

def test_create_practice_dummy_has_no_loot():
    practice_dummy = create_practice_dummy()
    assert practice_dummy.loot == []

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

def test_create_wooden_shield_has_correct_max_durability():
    shield = create_wooden_shield()
    assert shield.max_durability == 6

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
    assert basic["attack"] == 4
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
    assert athena["attack"] == 3
    assert athena["armour"] == 3
    assert athena["hp"] == 20
    assert athena["intellect"] == 5

def test_ancestries_hermes_has_correct_stats():
    hermes = ANCESTRIES["hermes"]
    assert hermes["label"] == "Descendant of Hermes"
    assert hermes["attack"] == 4
    assert hermes["armour"] == 1
    assert hermes["hp"] == 20
    assert hermes["intellect"] == 3

def test_ancestries_poseidon_has_correct_stats():
    poseidon = ANCESTRIES["poseidon"]
    assert poseidon["label"] == "Descendant of Poseidon"
    assert poseidon["attack"] == 2
    assert poseidon["armour"] == 3
    assert poseidon["hp"] == 23
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
    assert atalanta["hp"] == 18
    assert atalanta["intellect"] == 2

def test_ancestries_medusa_has_correct_stats():
    medusa = ANCESTRIES["medusa"]
    assert medusa["label"] == "Descendant of Medusa"
    assert medusa["attack"] == 2
    assert medusa["armour"] == 3
    assert medusa["hp"] == 21
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
    assert cyclops["attack"] == 4
    assert cyclops["armour"] == 1
    assert cyclops["hp"] == 23
    assert cyclops["intellect"] == 0

def test_ancestries_basic_has_no_secondary_effect():
    basic = ANCESTRIES["basic"]
    assert basic["secondary_effect"] is None
    assert basic["secondary_ability_label"] == "No secondary gift"

def test_ancestries_ares_secondary_effect_grants_reckless_strength():
    ares = ANCESTRIES["ares"]
    player = Player(name="hero", hp=100)
    ares["secondary_effect"](player)
    assert player.has_reckless_strength is True
    assert ares["secondary_ability_label"] == "Reckless Strength - heavy attack miss chance halves"

def test_ancestries_athena_secondary_effect_grants_measured_casting():
    athena = ANCESTRIES["athena"]
    player = Player(name="hero", hp=100)
    athena["secondary_effect"](player)
    assert player.has_measured_casting is True
    assert athena["secondary_ability_label"] == "Measured Casting - spells never go on cooldown"

def test_ancestries_hermes_secondary_effect_grants_swift_feet():
    hermes = ANCESTRIES["hermes"]
    player = Player(name="hero", hp=100)
    hermes["secondary_effect"](player)
    assert player.has_swift_feet is True
    assert hermes["secondary_ability_label"] == "Swift Feet - fleeing always succeeds cleanly"

def test_ancestries_poseidon_secondary_effect_grants_unyielding_tide():
    poseidon = ANCESTRIES["poseidon"]
    player = Player(name="hero", hp=100)
    poseidon["secondary_effect"](player)
    assert player.has_unyielding_tide is True
    assert poseidon["secondary_ability_label"] == "Unyielding Tide - armour's defence never breaks"

def test_ancestries_achilles_secondary_effect_grants_berserking():
    achilles = ANCESTRIES["achilles"]
    player = Player(name="hero", hp=100)
    achilles["secondary_effect"](player)
    assert player.has_berserking is True
    assert achilles["secondary_ability_label"] == "Berserking - +2 damage at or below half HP"

def test_ancestries_odysseus_secondary_effect_grants_silver_tongue():
    odysseus = ANCESTRIES["odysseus"]
    player = Player(name="hero", hp=100)
    odysseus["secondary_effect"](player)
    assert player.has_silver_tongue is True
    assert odysseus["secondary_ability_label"] == "Silver Tongue - trades never consume your items"

def test_ancestries_atalanta_secondary_effect_grants_ranged_without_weapon():
    atalanta = ANCESTRIES["atalanta"]
    player = Player(name="hero", hp=100)
    atalanta["secondary_effect"](player)
    assert player.can_ranged_without_weapon is True
    assert atalanta["secondary_ability_label"] == "Fleet-Footed - ranged attacks need no weapon"

def test_ancestries_medusa_secondary_effect_grants_petrifying_gaze():
    medusa = ANCESTRIES["medusa"]
    player = Player(name="hero", hp=100)
    medusa["secondary_effect"](player)
    assert player.has_petrifying_gaze is True
    assert medusa["secondary_ability_label"] == "Petrifying Gaze - chance to poison on attack"

def test_ancestries_minotaur_secondary_effect_grants_bull_rush():
    minotaur = ANCESTRIES["minotaur"]
    player = Player(name="hero", hp=100)
    minotaur["secondary_effect"](player)
    assert player.has_bull_rush is True
    assert minotaur["secondary_ability_label"] == "Bull Rush - bonus damage vs a full-HP target"

def test_ancestries_cyclops_secondary_effect_grants_iron_hide():
    cyclops = ANCESTRIES["cyclops"]
    player = Player(name="hero", hp=100)
    cyclops["secondary_effect"](player)
    assert player.has_iron_hide is True
    assert cyclops["secondary_ability_label"] == "Iron Hide - reduces every hit taken by 1"

def test_create_bronze_breastplate_has_correct_defence_and_description():
    breastplate = create_bronze_breastplate()
    assert breastplate.name == "Bronze Breastplate"
    assert breastplate.description == "Dented and a size too large, but the bronze is sound - better than the wood you started with, if only just."
    assert breastplate.defence == 2

def test_create_bronze_breastplate_has_correct_max_durability():
    breastplate = create_bronze_breastplate()
    assert breastplate.max_durability == 8

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

def test_create_athena_talk_without_the_bow_points_the_player_to_the_centaur():
    athena = create_athena()
    player = Player(name="hero", hp=100)
    message = athena.talk(player)
    assert message == athena.hint
    assert "centaur" in message
    assert "bow" in message

def test_create_athena_has_hint_traded_and_post_trade_message():
    athena = create_athena()
    assert athena.hint_traded == "\"Wear it well. Hades is patient, and so are his halls - don't mistake either for weakness.\""
    assert athena.post_trade_message == "\"The owl on it watches whichever side you forget to.\""

def test_create_athena_talk_after_trade_returns_hint_traded():
    athena = create_athena()
    athena.trade_completed = True
    assert athena.talk(Player(name="hero", hp=100)) == athena.hint_traded

def test_create_athena_talk_with_the_bow_tells_the_player_to_trade():
    athena = create_athena()
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Centaur's Broken Bow", description=""))
    assert athena.talk(player) == athena.hint_complete
    assert "'trade'" in athena.hint_complete

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

def test_create_ares_talk_without_the_eye_points_the_player_to_the_cyclops():
    ares = create_ares()
    player = Player(name="hero", hp=100)
    message = ares.talk(player)
    assert message == ares.hint
    assert "Cyclops" in message
    assert "labyrinth" in message

def test_create_ares_has_hint_traded_and_post_trade_message():
    ares = create_ares()
    assert ares.hint_traded == "\"Don't hold it like a broom. Point, then push.\""
    assert ares.post_trade_message == "\"Now go and use it on something that deserves it.\""

def test_create_ares_talk_after_trade_returns_hint_traded():
    ares = create_ares()
    ares.trade_completed = True
    assert ares.talk(Player(name="hero", hp=100)) == ares.hint_traded

def test_create_ares_talk_with_the_eye_tells_the_player_to_trade():
    ares = create_ares()
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Cyclops' Eye", description=""))
    assert ares.talk(player) == "\"That's the eye. Say 'trade'.\""

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

def test_create_hermes_talk_without_the_bone_points_the_player_to_the_hidden_vault():
    """Hermes is the in-fiction hint for the Sunken Vault - the hidden exit off Styx Crossing, revealed by 'examine'."""
    hermes = create_hermes()
    player = Player(name="hero", hp=100)
    message = hermes.talk(player)
    assert message == hermes.hint
    assert "Styx Crossing" in message
    assert "'examine'" in message

def test_create_hermes_has_hint_traded_and_post_trade_message():
    hermes = create_hermes()
    assert hermes.hint_traded.startswith("\"Still here?")
    assert hermes.post_trade_message == "\"A little something for your trouble. Use it wisely - or quickly, which is usually the same thing.\""

def test_create_hermes_talk_after_trade_returns_hint_traded():
    hermes = create_hermes()
    hermes.trade_completed = True
    assert hermes.talk(Player(name="hero", hp=100)) == hermes.hint_traded

def test_create_hermes_talk_with_the_bone_tells_the_player_to_trade():
    hermes = create_hermes()
    player = Player(name="hero", hp=100)
    player.inventory.add(QuestItem(name="Skeleton Bone", description=""))
    assert hermes.talk(player) == "\"Oh, that's a good one. Say 'trade' - quickly, I've places to be.\""

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

def test_create_prometheus_talk_mentions_the_forge():
    prometheus = create_prometheus()
    player = Player(name="hero", hp=100)
    message = prometheus.talk(player)
    assert message == prometheus.hint
    assert "forge" in message

def test_create_cyclops_eye_has_correct_name_and_description():
    eye = create_cyclops_eye()
    assert eye.name == "Cyclops' Eye"
    assert eye.description == "Still faintly warm and unsettlingly heavy for its size - Ares will know exactly what this cost you."

def test_create_breastplate_of_athena_has_correct_defence_and_description():
    breastplate = create_breastplate_of_athena()
    assert breastplate.name == "Breastplate of Athena"
    assert breastplate.description == "Cool to the touch even in the deepest heat, etched with an owl that seems to watch whichever way danger comes from."
    assert breastplate.defence == 4

def test_create_breastplate_of_athena_has_correct_max_durability():
    breastplate = create_breastplate_of_athena()
    assert breastplate.max_durability == 15

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

def test_build_world_returns_fifty_one_rooms():
    dungeon, entrance, floors = build_world()
    assert len(dungeon) == 51

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

def test_build_world_floor_2_rooms_dict_contains_six_rooms():
    dungeon, entrance, floors = build_world()
    assert len(floors["floor_2"]) == 6

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

def test_build_world_prayer_room_has_forge_shortcut_to_forge_of_prometheus():
    dungeon, entrance, floors = build_world()
    prayer_room = dungeon.get_room("Prayer Room")
    assert prayer_room is not None
    assert prayer_room.get_exit("forge") is dungeon.get_room("Forge of Prometheus")

def test_build_world_stony_lair_has_forge_shortcut_to_forge_of_prometheus():
    dungeon, entrance, floors = build_world()
    stony_lair = dungeon.get_room("Stony Lair")
    assert stony_lair is not None
    assert stony_lair.get_exit("forge") is dungeon.get_room("Forge of Prometheus")

def test_build_world_maze_of_pillars_has_forge_shortcut_to_forge_of_prometheus():
    dungeon, entrance, floors = build_world()
    maze_of_pillars = dungeon.get_room("Maze of Pillars")
    assert maze_of_pillars is not None
    assert maze_of_pillars.get_exit("forge") is dungeon.get_room("Forge of Prometheus")

def test_build_world_forge_of_prometheus_has_reciprocal_exit_to_prayer_room():
    dungeon, entrance, floors = build_world()
    forge = dungeon.get_room("Forge of Prometheus")
    assert forge is not None
    assert forge.get_exit("prayer room") is dungeon.get_room("Prayer Room")

def test_build_world_forge_of_prometheus_has_reciprocal_exit_to_stony_lair():
    dungeon, entrance, floors = build_world()
    forge = dungeon.get_room("Forge of Prometheus")
    assert forge is not None
    assert forge.get_exit("stony lair") is dungeon.get_room("Stony Lair")

def test_build_world_forge_of_prometheus_has_reciprocal_exit_to_maze_of_pillars():
    dungeon, entrance, floors = build_world()
    forge = dungeon.get_room("Forge of Prometheus")
    assert forge is not None
    assert forge.get_exit("maze of pillars") is dungeon.get_room("Maze of Pillars")

def test_build_world_forge_of_prometheus_reciprocal_exits_start_fast_travel_locked():
    dungeon, entrance, floors = build_world()
    forge = dungeon.get_room("Forge of Prometheus")
    assert forge is not None
    assert forge.fast_travel_locks == {"prayer room", "stony lair", "maze of pillars", "shadow of pylos", "shadow of ithaca"}

def test_build_world_prayer_room_forge_exit_registers_activation_for_forge_of_prometheus():
    dungeon, entrance, floors = build_world()
    prayer_room = dungeon.get_room("Prayer Room")
    forge = dungeon.get_room("Forge of Prometheus")
    assert prayer_room is not None
    assert prayer_room.exit_activations["forge"] == (forge, "prayer room")

def test_build_world_stony_lair_forge_exit_registers_activation_for_forge_of_prometheus():
    dungeon, entrance, floors = build_world()
    stony_lair = dungeon.get_room("Stony Lair")
    forge = dungeon.get_room("Forge of Prometheus")
    assert stony_lair is not None
    assert stony_lair.exit_activations["forge"] == (forge, "stony lair")

def test_build_world_maze_of_pillars_forge_exit_registers_activation_for_forge_of_prometheus():
    dungeon, entrance, floors = build_world()
    maze_of_pillars = dungeon.get_room("Maze of Pillars")
    forge = dungeon.get_room("Forge of Prometheus")
    assert maze_of_pillars is not None
    assert maze_of_pillars.exit_activations["forge"] == (forge, "maze of pillars")

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

def test_build_floor_1_fields_of_asphodel_has_shade_enemy():
    start, rooms = build_floor_1()
    enemy_names = [enemy.name for enemy in rooms["Fields of Asphodel"].enemies]
    assert "Shade" in enemy_names

def test_build_floor_2_returns_library_of_athena_as_start_room():
    start, rooms = build_floor_2()
    assert start.name == "Library of Athena"

def test_build_floor_2_returns_rooms_dict_with_six_rooms():
    start, rooms = build_floor_2()
    assert len(rooms) == 6

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

def test_build_floor_2_forge_of_prometheus_is_a_forge():
    start, rooms = build_floor_2()
    forge = rooms["Forge of Prometheus"]
    assert forge.is_forge is True

def test_build_floor_2_other_rooms_are_not_forges():
    start, rooms = build_floor_2()
    assert rooms["Library of Athena"].is_forge is False
    assert rooms["Armoury of Ares"].is_forge is False
    assert rooms["Hall of Hermes"].is_forge is False
    assert rooms["Trophy Room of Zeus"].is_forge is False
    assert rooms["Practice Chamber"].is_forge is False

def test_build_floor_2_forge_connects_to_practice_chamber_via_east():
    start, rooms = build_floor_2()
    forge = rooms["Forge of Prometheus"]
    assert forge.get_exit("east") is rooms["Practice Chamber"]

def test_build_floor_2_practice_chamber_connects_back_to_forge_via_west():
    start, rooms = build_floor_2()
    practice_chamber = rooms["Practice Chamber"]
    assert practice_chamber.get_exit("west") is rooms["Forge of Prometheus"]

def test_build_floor_2_practice_chamber_is_a_practice_chamber():
    start, rooms = build_floor_2()
    assert rooms["Practice Chamber"].is_practice_chamber is True

def test_build_floor_2_other_rooms_are_not_practice_chambers():
    start, rooms = build_floor_2()
    assert rooms["Library of Athena"].is_practice_chamber is False
    assert rooms["Armoury of Ares"].is_practice_chamber is False
    assert rooms["Hall of Hermes"].is_practice_chamber is False
    assert rooms["Forge of Prometheus"].is_practice_chamber is False
    assert rooms["Trophy Room of Zeus"].is_practice_chamber is False

def test_build_floor_2_practice_chamber_has_practice_dummy_enemy():
    start, rooms = build_floor_2()
    practice_chamber = rooms["Practice Chamber"]
    assert len(practice_chamber.enemies) == 1
    assert practice_chamber.enemies[0].name == "Practice Enemy"

def test_build_floor_2_library_of_athena_has_athena_ally():
    start, rooms = build_floor_2()
    ally_names = [ally.name for ally in rooms["Library of Athena"].allies]
    assert "Athena" in ally_names

def test_build_floor_2_armoury_of_ares_has_ares_ally():
    start, rooms = build_floor_2()
    ally_names = [ally.name for ally in rooms["Armoury of Ares"].allies]
    assert "Ares" in ally_names

def test_build_floor_2_hall_of_hermes_has_hermes_ally():
    start, rooms = build_floor_2()
    ally_names = [ally.name for ally in rooms["Hall of Hermes"].allies]
    assert "Hermes" in ally_names

def test_build_floor_2_forge_of_prometheus_has_prometheus_ally():
    start, rooms = build_floor_2()
    ally_names = [ally.name for ally in rooms["Forge of Prometheus"].allies]
    assert "Prometheus" in ally_names

def test_build_floor_2_trophy_room_of_zeus_has_no_ally():
    """Trophy Room of Zeus is still shell-only - populating it isn't part of what this pass wired up."""
    start, rooms = build_floor_2()
    assert rooms["Trophy Room of Zeus"].allies == []

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

def test_build_floor_3_cave_of_harpies_has_harpy_enemy():
    start, rooms = build_floor_3()
    enemy_names = [enemy.name for enemy in rooms["Cave of Harpies"].enemies]
    assert "Harpy" in enemy_names

def test_build_floor_3_prayer_room_has_fanatic_enemy():
    start, rooms = build_floor_3()
    enemy_names = [enemy.name for enemy in rooms["Prayer Room"].enemies]
    assert "Fanatic" in enemy_names

def test_build_floor_3_dim_corridor_has_lurker_enemy():
    start, rooms = build_floor_3()
    enemy_names = [enemy.name for enemy in rooms["Dim Corridor"].enemies]
    assert "Lurker" in enemy_names

def test_build_floor_3_bony_crypt_has_crypt_keeper_enemy():
    start, rooms = build_floor_3()
    enemy_names = [enemy.name for enemy in rooms["Bony Crypt"].enemies]
    assert "Crypt Keeper" in enemy_names

def test_build_floor_3_overgrown_forest_has_centaur_enemy():
    start, rooms = build_floor_3()
    enemy_names = [enemy.name for enemy in rooms["Overgrown Forest"].enemies]
    assert "Centaur" in enemy_names

def test_build_floor_3_overgrown_forest_has_examine_text():
    start, rooms = build_floor_3()
    assert "learn <path>" in rooms["Overgrown Forest"].examine_text

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

def test_build_floor_4_labyrinth_of_the_minotaur_has_minotaur_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Labyrinth of the Minotaur"].enemies]
    assert "Minotaur" in enemy_names

def test_build_floor_4_stony_lair_has_petrified_guardian_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Stony Lair"].enemies]
    assert "Petrified Guardian" in enemy_names

def test_build_floor_4_mossy_grove_has_satyr_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Mossy Grove"].enemies]
    assert "Satyr" in enemy_names

def test_build_floor_4_shadowy_corner_has_lamia_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Shadowy Corner"].enemies]
    assert "Lamia" in enemy_names

def test_build_floor_4_sandy_expanse_has_ember_wraith_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Sandy Expanse"].enemies]
    assert "Ember Wraith" in enemy_names

def test_build_floor_4_maze_of_pillars_has_talos_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Maze of Pillars"].enemies]
    assert "Talos" in enemy_names

def test_build_floor_4_lair_of_medusa_has_medusa_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Lair of Medusa"].enemies]
    assert "Medusa" in enemy_names

def test_build_floor_4_cavern_of_the_cyclops_has_cyclops_enemy():
    start, rooms = build_floor_4()
    enemy_names = [enemy.name for enemy in rooms["Cavern of the Cyclops"].enemies]
    assert "Cyclops" in enemy_names

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

def test_build_floor_6_calm_waters_connects_to_narrow_river_via_south():
    start, rooms = build_floor_6()
    assert rooms["Calm Waters"].get_exit("south") is rooms["Narrow River"]

def test_build_floor_6_rocky_shore_connects_to_poseidons_depths_via_south():
    start, rooms = build_floor_6()
    assert rooms["Rocky Shore"].get_exit("south") is rooms["Poseidon's Depths"]

def test_build_floor_6_narrow_river_connects_to_calm_waters_via_north():
    start, rooms = build_floor_6()
    assert rooms["Narrow River"].get_exit("north") is rooms["Calm Waters"]

def test_build_floor_6_narrow_river_connects_to_poseidons_depths_via_west():
    start, rooms = build_floor_6()
    assert rooms["Narrow River"].get_exit("west") is rooms["Poseidon's Depths"]

def test_build_floor_6_poseidons_depths_connects_to_rocky_shore_via_north():
    start, rooms = build_floor_6()
    assert rooms["Poseidon's Depths"].get_exit("north") is rooms["Rocky Shore"]

def test_build_floor_6_poseidons_depths_connects_to_narrow_river_via_east():
    start, rooms = build_floor_6()
    assert rooms["Poseidon's Depths"].get_exit("east") is rooms["Narrow River"]

def test_build_floor_6_poseidons_depths_connects_to_shadow_of_ithaca_via_south():
    start, rooms = build_floor_6()
    assert rooms["Poseidon's Depths"].get_exit("south") is rooms["Shadow of Ithaca"]

def test_build_floor_6_shadow_of_ithaca_connects_to_poseidons_depths_via_north():
    start, rooms = build_floor_6()
    assert rooms["Shadow of Ithaca"].get_exit("north") is rooms["Poseidon's Depths"]

def test_build_floor_6_scylla_and_charybdis_are_parallel_routes_to_poseidons_depths():
    """Deliberate: Rocky Shore (Scylla) and Narrow River (Charybdis) each lead from Calm Waters to Poseidon's Depths on their own,
    so only one has to be passed - matching Nestor's advice on floor 5."""
    start, rooms = build_floor_6()
    assert rooms["Rocky Shore"].get_exit("south") is rooms["Poseidon's Depths"]
    assert rooms["Narrow River"].get_exit("west") is rooms["Poseidon's Depths"]
    assert rooms["Narrow River"] not in rooms["Rocky Shore"].exits.values()

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

def test_build_companion_test_camp_has_correct_name_and_description():
    room = build_companion_test_camp()
    assert room.name == "Companion Test Camp"
    assert room.description == "A quiet clearing set aside for testing recruitment and dismissal - not part of any real floor."

def test_create_test_companion_has_correct_stats():
    companion = create_test_companion()
    assert companion.name == "Test Companion"
    assert companion.hp == 20
    assert companion.attack_damage == 6
    assert companion.armour == 1
    assert companion.heal_amount == 4
    assert companion.brace_amount == 2

def test_create_test_companion_has_no_required_items():
    companion = create_test_companion()
    assert companion.required_items == []

def test_create_test_companion_home_room_is_companion_test_camp():
    companion = create_test_companion()
    assert companion.home_room.name == "Companion Test Camp"

def test_create_test_spell_has_correct_stats():
    spell = create_test_spell()
    assert spell.name == "Test Bolt"
    assert spell.mana_cost == 5
    assert spell.damage == 6

def test_create_test_spell_has_correct_effect():
    spell = create_test_spell()
    assert spell.effect_name == "Poison"
    assert spell.effect_amount == -2
    assert spell.effect_duration == 3

def test_create_test_spellbook_has_correct_name_and_description():
    spellbook = create_test_spellbook()
    assert spellbook.name == "Test Spellbook"
    assert spellbook.description == "A dev-only spellbook. Reading it teaches Test Bolt."

def test_create_test_spellbook_teaches_test_bolt():
    spellbook = create_test_spellbook()
    assert spellbook.spell.name == "Test Bolt"

def test_create_test_healing_tonic_has_correct_effect():
    tonic = create_test_healing_tonic()
    assert tonic.name == "Test Healing Tonic"
    assert tonic.effect_name == "Regen"
    assert tonic.amount == 3
    assert tonic.duration == 3

def test_create_test_venom_vial_has_correct_effect():
    vial = create_test_venom_vial()
    assert vial.name == "Test Venom Vial"
    assert vial.effect_name == "Poison"
    assert vial.amount == -3
    assert vial.duration == 3

def test_create_test_boss_has_correct_stats():
    boss = create_test_boss()
    assert boss.name == "Test Boss"
    assert boss.hp == 1
    assert boss.attack_damage == 1

def test_create_test_boss_has_two_wave_add_factories():
    boss = create_test_boss()
    assert len(boss.next_wave_factories) == 2

def test_create_test_boss_wave_add_factories_produce_test_adds():
    boss = create_test_boss()
    add = boss.next_wave_factories[0]()
    assert add.name == "Test Add"
    assert add.hp == 1
    assert add.attack_damage == 1
    assert add.experience_reward == 1
    assert add.gold_reward == 1

def test_create_test_boss_next_phase_factory_produces_phase_two():
    boss = create_test_boss()
    phase_two = boss.next_phase_factory()
    assert phase_two.name == "Test Boss (Phase 2)"
    assert phase_two.hp == 1
    assert phase_two.attack_damage == 1
    assert phase_two.experience_reward == 5
    assert phase_two.gold_reward == 5

def test_build_floor_4_labyrinth_of_the_minotaur_guards_south_exit():
    start, rooms = build_floor_4()
    assert "south" in rooms["Labyrinth of the Minotaur"].guarded_exits

def test_build_floor_4_labyrinth_of_the_minotaur_only_guards_south_exit():
    """West (Stony Lair), east (Cyclops) and ascend stay open - the player can still retreat or explore the side rooms first."""
    start, rooms = build_floor_4()
    assert rooms["Labyrinth of the Minotaur"].guarded_exits == {"south"}

def test_build_floor_4_maze_of_pillars_guards_south_exit_to_lair_of_medusa():
    start, rooms = build_floor_4()
    assert rooms["Maze of Pillars"].guarded_exits == {"south"}

def test_build_world_overgrown_forest_guards_descend_exit():
    dungeon, entrance, floors = build_world()
    overgrown_forest = dungeon.get_room("Overgrown Forest")
    assert overgrown_forest is not None
    assert overgrown_forest.guarded_exits == {"descend"}

def test_build_world_lair_of_medusa_guards_descend_exit():
    dungeon, entrance, floors = build_world()
    lair = dungeon.get_room("Lair of Medusa")
    assert lair is not None
    assert lair.guarded_exits == {"descend"}

def test_create_wooden_sword_is_a_blade():
    assert create_wooden_sword().weapon_class == "blade"

def test_create_wooden_shield_is_a_light_shield():
    shield = create_wooden_shield()
    assert shield.slot == "shield"
    assert shield.weight == "light"

def test_create_weathered_helm_is_light():
    assert create_weathered_helm().weight == "light"

def test_create_bronze_xiphos_is_a_blade():
    assert create_bronze_xiphos().weapon_class == "blade"

def test_create_bronze_breastplate_is_medium_weight():
    assert create_bronze_breastplate().weight == "medium"

def test_create_breastplate_of_athena_is_light():
    assert create_breastplate_of_athena().weight == "light"

def test_create_spear_of_ares_is_piercing_with_two_pierce():
    spear = create_spear_of_ares()
    assert spear.weapon_class == "piercing"
    assert spear.armour_pierce == 2

def test_create_harpy_fletched_bow_is_ranged_class():
    assert create_harpy_fletched_bow().weapon_class == "ranged"

def test_create_labrys_is_a_two_handed_heavy_weapon_with_cleave():
    labrys = create_labrys()
    assert labrys.weapon_class == "heavy"
    assert labrys.two_handed is True
    assert labrys.cleave is True

def test_create_chipped_stone_aegis_is_heavy():
    assert create_chipped_stone_aegis().weight == "heavy"

def test_create_lamias_fang_is_piercing_with_lifesteal():
    fang = create_lamias_fang()
    assert fang.weapon_class == "piercing"
    assert fang.armour_pierce == 2
    assert fang.lifesteal is True

def test_create_sunscorched_dagger_is_a_blade():
    assert create_sunscorched_dagger().weapon_class == "blade"

def test_create_talos_bronze_plating_is_heavy():
    assert create_talos_bronze_plating().weight == "heavy"

def test_create_serpents_kiss_is_a_blade_with_poison_chance():
    kiss = create_serpents_kiss()
    assert kiss.weapon_class == "blade"
    assert kiss.poison_chance == 0.15

def test_create_shade_of_achilles_duellist_has_correct_stats():
    duellist = create_shade_of_achilles_duellist()
    assert isinstance(duellist, Enemy)
    assert duellist.name == "Shade of Achilles"
    assert duellist.hp == 50
    assert duellist.attack_damage == 14
    assert duellist.armour_pierce == 5
    assert duellist.armour == 3
    assert duellist.brace_amount == 5
    assert duellist.dodge_chance == 0.15

def test_create_shade_of_achilles_duellist_gives_no_xp_or_gold():
    duellist = create_shade_of_achilles_duellist()
    assert duellist.experience_reward == 0
    assert duellist.gold_reward == 0

def test_create_shade_of_achilles_duellist_defeat_effect_grants_a_skill_point():
    player = Player(name="Hero", hp=20)
    duellist = create_shade_of_achilles_duellist()
    assert duellist.defeat_effect is not None
    message = duellist.defeat_effect(player)
    assert player.skill_tree.skill_points == 1
    assert message == "Hero gains a skill point for besting Achilles."

def test_create_shade_of_achilles_is_a_companion_with_correct_stats():
    achilles = create_shade_of_achilles()
    assert isinstance(achilles, Companion)
    assert achilles.name == "Shade of Achilles"
    assert achilles.hp == 20
    assert achilles.attack_damage == 6
    assert achilles.armour == 2
    assert achilles.brace_amount == 3

def test_create_shade_of_achilles_must_be_duelled_before_recruiting():
    achilles = create_shade_of_achilles()
    assert achilles.duel_enemy_factory is create_shade_of_achilles_duellist
    assert achilles.requires_duel is True

def test_create_shade_of_achilles_has_every_line_of_dialogue():
    achilles = create_shade_of_achilles()
    assert "challenge shade of achilles" in achilles.hint
    assert "recruit shade of achilles" in achilles.hint_recruitable
    assert achilles.duel_won_message != ""
    assert achilles.duel_lost_message != ""

def test_create_shade_of_achilles_duellist_shares_the_companions_name():
    """The combat form is the same person - target/HP lines read naturally, and nothing looks up the duellist by a different name."""
    assert create_shade_of_achilles_duellist().name == create_shade_of_achilles().name

def test_create_shade_of_achilles_uses_the_home_room_it_is_given():
    camp = Room("Shadow of Army Camp")
    achilles = create_shade_of_achilles(camp)
    assert achilles.home_room is camp

def test_create_shade_of_achilles_without_a_home_room_gets_a_placeholder_camp():
    """Only so the no-argument COMPANION_REGISTRY factory works - a save load re-links the real room by name."""
    achilles = create_shade_of_achilles()
    assert achilles.home_room.name == "Shadow of Army Camp"

def test_build_floor_5_places_the_shade_of_achilles_in_the_army_camp():
    start, rooms = build_floor_5()
    camp = rooms["Shadow of Army Camp"]
    assert [c.name for c in camp.companions] == ["Shade of Achilles"]
    assert camp.companions[0].home_room is camp

def test_build_floor_5_holds_no_other_companions():
    _, rooms = build_floor_5()
    others = [c for name, room in rooms.items() if name != "Shadow of Army Camp" for c in room.companions]
    assert others == []

def test_create_shade_of_hector_has_correct_stats():
    hector = create_shade_of_hector()
    assert hector.name == "Shade of Hector"
    assert hector.hp == 32
    assert hector.attack_damage == 9
    assert hector.armour == 5
    assert hector.experience_reward == 38
    assert hector.gold_reward == 22

def test_create_shade_of_hector_has_no_brace_heal_or_special_ability():
    """The whole fight is armour 5 - nothing else."""
    hector = create_shade_of_hector()
    assert hector.brace_amount == 0
    assert hector.heal_amount == 0
    assert hector.has_lifesteal is False
    assert hector.has_petrifying_gaze is False

def test_create_shade_of_hector_drops_hectors_helm():
    loot = create_shade_of_hector().loot
    assert [item.name for item in loot] == ["Hector's Helm"]

def test_create_hectors_helm_is_a_medium_helmet():
    helm = create_hectors_helm()
    assert isinstance(helm, Armour)
    assert helm.slot == "helmet"
    assert helm.weight == "medium"
    assert helm.defence == 2
    assert helm.max_durability == 12

def test_build_floor_5_places_the_shade_of_hector_in_troy_north():
    _, rooms = build_floor_5()
    assert [e.name for e in rooms["Shadow of Troy (North)"].enemies] == ["Shade of Hector"]

def test_create_shade_of_achilles_has_a_rival_line_for_the_real_shade_of_hector():
    """Rival lines are keyed by enemy name - this one must match the name Hector actually has."""
    achilles = create_shade_of_achilles()
    assert create_shade_of_hector().name in achilles.rival_lines

def test_ancestry_lines_are_on_the_matching_figures():
    speakers = {
        "athena": create_athena(), "ares": create_ares(), "hermes": create_hermes(), "minotaur": create_minotaur(),
        "cyclops": create_cyclops(), "medusa": create_medusa(), "achilles": create_shade_of_achilles(),
    }
    for key, speaker in speakers.items():
        assert key in speaker.ancestry_lines, speaker.name

def test_every_ancestry_line_in_the_world_uses_a_real_ancestry_key():
    """A typo'd key would silently never fire - every key must be one of ANCESTRIES'."""
    _, _, all_floors = build_world()
    speakers = [s for rooms in all_floors.values() for room in rooms.values() for s in (*room.enemies, *room.allies, *room.companions)]
    keys = {key for s in speakers for key in s.ancestry_lines}
    assert keys
    assert keys <= set(ANCESTRIES)

def test_medusa_ancestry_line_is_on_her_first_phase_only():
    """Phase 1 is who the player first sees - the line would otherwise fire again mid-fight."""
    assert "medusa" in create_medusa().ancestry_lines
    assert create_medusa_awakened().ancestry_lines == {}

def test_create_shade_of_ajax_has_correct_stats():
    ajax = create_shade_of_ajax()
    assert ajax.name == "Shade of Ajax"
    assert ajax.hp == 46
    assert ajax.attack_damage == 14
    assert ajax.armour_pierce == 3
    assert ajax.armour == 1
    assert ajax.experience_reward == 42
    assert ajax.gold_reward == 24

def test_create_shade_of_ajax_drops_the_tower_shield():
    assert [item.name for item in create_shade_of_ajax().loot] == ["Tower Shield of Ajax"]

def test_create_tower_shield_of_ajax_is_a_heavy_shield():
    shield = create_tower_shield_of_ajax()
    assert isinstance(shield, Armour)
    assert shield.slot == "shield"
    assert shield.weight == "heavy"
    assert shield.defence == 4
    assert shield.max_durability == 20

def test_create_myrmidon_soldier_has_correct_stats():
    myrmidon = create_myrmidon_soldier()
    assert myrmidon.name == "Myrmidon Soldier"
    assert myrmidon.hp == 22
    assert myrmidon.attack_damage == 9
    assert myrmidon.armour_pierce == 2
    assert myrmidon.armour == 3
    assert myrmidon.brace_amount == 3
    assert myrmidon.caution_weight == 1.2

def test_create_myrmidon_soldier_drops_a_field_dressing():
    assert [item.name for item in create_myrmidon_soldier().loot] == ["Field Dressing"]

def test_create_field_dressing_heals_ten():
    dressing = create_field_dressing()
    assert dressing.heal_amount == 10

def test_create_shade_of_paris_has_correct_stats():
    paris = create_shade_of_paris()
    assert paris.name == "Shade of Paris"
    assert paris.hp == 20
    assert paris.attack_damage == 10
    assert paris.armour == 1
    assert paris.experience_reward == 40
    assert paris.gold_reward == 30

def test_create_shade_of_paris_is_evasive_in_melee_and_pierces_armour():
    paris = create_shade_of_paris()
    assert paris.melee_dodge_chance == 0.5
    assert paris.armour_pierce == 8

def test_create_shade_of_paris_drops_the_bow_of_paris():
    assert [item.name for item in create_shade_of_paris().loot] == ["Bow of Paris"]

def test_create_bow_of_paris_is_a_piercing_ranged_weapon():
    bow = create_bow_of_paris()
    assert isinstance(bow, Weapon)
    assert bow.slot == "ranged"
    assert bow.weapon_class == "ranged"
    assert bow.damage == 6
    assert bow.armour_pierce == 2

def test_create_nestor_gives_away_a_cup_of_kykeon():
    nestor = create_nestor()
    assert [item.name for item in nestor.inventory.items] == ["Cup of Kykeon"]
    assert "take cup of kykeon from nestor" in nestor.hint

def test_create_nestor_has_nothing_to_trade():
    nestor = create_nestor()
    assert nestor.required_items == []
    assert nestor.reward is None

def test_create_cup_of_kykeon_is_a_free_action_regen():
    cup = create_cup_of_kykeon()
    assert isinstance(cup, StatusEffectItem)
    assert cup.effect_name == "Regen"
    assert cup.amount == 4
    assert cup.duration == 4
    assert cup.ends_turn(Player(name="Hero", hp=20)) is False

def test_build_floor_5_places_every_enemy_in_its_room():
    _, rooms = build_floor_5()
    assert [e.name for e in rooms["Shadow of Troy (Central)"].enemies] == ["Shade of Ajax"]
    assert [e.name for e in rooms["Shadow of Troy (Alleyway)"].enemies] == ["Myrmidon Soldier", "Myrmidon Soldier"]
    assert [e.name for e in rooms["Shadow of Troy (South)"].enemies] == ["Shade of Paris"]

def test_build_floor_5_myrmidons_are_separate_with_their_own_dressings():
    _, rooms = build_floor_5()
    first, second = rooms["Shadow of Troy (Alleyway)"].enemies
    assert first is not second
    assert first.loot[0] is not second.loot[0]

def test_build_floor_5_places_nestor_in_pylos():
    _, rooms = build_floor_5()
    assert [a.name for a in rooms["Shadow of Pylos"].allies] == ["Nestor"]

def test_every_achilles_rival_line_names_a_real_placed_enemy():
    """Rival lines are keyed by enemy name - a renamed enemy would silently drop its line."""
    _, _, all_floors = build_world()
    placed = {e.name for rooms in all_floors.values() for room in rooms.values() for e in room.enemies}
    assert set(create_shade_of_achilles().rival_lines) <= placed

def test_create_shade_of_hector_pierces_three_armour():
    assert create_shade_of_hector().armour_pierce == 3

def test_build_floor_5_hector_ajax_and_paris_each_guard_the_way_on():
    _, rooms = build_floor_5()
    assert rooms["Shadow of Troy (North)"].guarded_exits == {"south"}
    assert rooms["Shadow of Troy (Central)"].guarded_exits == {"west"}
    assert rooms["Shadow of Troy (South)"].guarded_exits == {"east"}

def test_build_floor_5_leaves_the_myrmidons_exit_unguarded():
    """Deliberate: the Myrmidons can be walked past, and skipping them means giving up their Field Dressings."""
    _, rooms = build_floor_5()
    assert rooms["Shadow of Troy (Alleyway)"].guarded_exits == set()

def test_create_laestrygonian_has_correct_stats():
    giant = create_laestrygonian()
    assert giant.name == "Laestrygonian"
    assert giant.hp == 30
    assert giant.attack_damage == 12
    assert giant.armour == 1
    assert giant.armour_pierce == 2
    assert giant.aggression_weight == 1.3

def test_create_laestrygonian_drops_laestrygonian_hide():
    assert [item.name for item in create_laestrygonian().loot] == ["Laestrygonian Hide"]

def test_create_antiphates_has_correct_stats():
    king = create_antiphates()
    assert king.name == "Antiphates"
    assert king.hp == 36
    assert king.attack_damage == 13
    assert king.armour == 2
    assert king.armour_pierce == 2

def test_create_antiphates_is_tougher_than_his_giant():
    king = create_antiphates()
    giant = create_laestrygonian()
    assert king.hp > giant.hp
    assert king.attack_damage > giant.attack_damage
    assert king.experience_reward > giant.experience_reward

def test_create_antiphates_drops_his_club():
    loot = create_antiphates().loot
    assert len(loot) == 1
    assert isinstance(loot[0], Weapon)
    assert loot[0].damage == 8

def test_create_laestrygonian_hide_is_medium_body_armour():
    hide = create_laestrygonian_hide()
    assert isinstance(hide, Armour)
    assert hide.slot == "body"
    assert hide.weight == "medium"
    assert hide.defence == 5
    assert hide.max_durability == 14

def test_create_antiphates_club_is_a_two_handed_heavy_weapon_without_cleave():
    club = create_antiphates_club()
    assert club.name == "Antiphates' Club"
    assert club.weapon_class == "heavy"
    assert club.two_handed is True
    assert club.cleave is False
    assert club.damage == 8

def test_create_antiphates_club_out_damages_the_labrys():
    assert create_antiphates_club().damage > create_labrys().damage

def test_create_laestrygonian_builds_a_fresh_hide_each_time():
    assert create_laestrygonian().loot[0] is not create_laestrygonian().loot[0]

def test_build_floor_6_places_antiphates_and_a_laestrygonian_in_bright_cave():
    _, rooms = build_floor_6()
    assert [e.name for e in rooms["Bright Cave"].enemies] == ["Antiphates", "Laestrygonian"]

def test_build_floor_6_calm_waters_offers_the_sirens_three_verbs():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    assert calm_waters.available_interactions(Player(name="Hero", hp=20)) == ["listen", "give in", "resist"]

def test_build_floor_6_only_calm_waters_and_narrow_river_have_interactions():
    _, rooms = build_floor_6()
    assert [name for name, room in rooms.items() if room.interactions] == ["Calm Waters", "Narrow River"]

def test_sirens_listen_changes_nothing():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=20)
    calm_waters.interactions["listen"].handler(player, calm_waters)
    assert player.skill_tree.skill_points == 0
    assert player.max_hp == 20
    assert calm_waters.flags == set()

def test_sirens_listen_explains_how_to_accept_and_refuse():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    message = calm_waters.interactions["listen"].handler(Player(name="Hero", hp=20), calm_waters)
    assert "'give in'" in message
    assert "'resist'" in message
    assert "+2 skill points" in message
    assert "-5 max HP" in message

def test_sirens_give_in_grants_two_skill_points_for_five_max_hp():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=20)
    calm_waters.interactions["give in"].handler(player, calm_waters)
    assert player.skill_tree.skill_points == 2
    assert player.max_hp == 15

def test_sirens_give_in_caps_current_hp_to_the_new_maximum():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=20)
    calm_waters.interactions["give in"].handler(player, calm_waters)
    assert player.hp == 15

def test_sirens_give_in_leaves_hp_already_below_the_new_maximum_alone():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=20)
    player.hp = 8
    calm_waters.interactions["give in"].handler(player, calm_waters)
    assert player.hp == 8

def test_sirens_give_in_never_drops_max_hp_below_one():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=4)
    calm_waters.interactions["give in"].handler(player, calm_waters)
    assert player.max_hp == 1
    assert player.hp == 1

def test_sirens_give_in_reports_the_new_max_hp():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    message = calm_waters.interactions["give in"].handler(Player(name="Hero", hp=20), calm_waters)
    assert "Max HP is now 15" in message

def test_sirens_give_in_silences_every_verb():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=20)
    calm_waters.interactions["give in"].handler(player, calm_waters)
    assert "sirens_bargain_taken" in calm_waters.flags
    assert calm_waters.available_interactions(player) == []

def test_sirens_resist_changes_nothing_and_keeps_the_offer_open():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    player = Player(name="Hero", hp=20)
    calm_waters.interactions["resist"].handler(player, calm_waters)
    assert player.skill_tree.skill_points == 0
    assert player.max_hp == 20
    assert calm_waters.available_interactions(player) == ["listen", "give in", "resist"]

def test_sirens_verbs_have_their_own_unavailable_messages():
    _, rooms = build_floor_6()
    calm_waters = rooms["Calm Waters"]
    assert calm_waters.interactions["listen"].unavailable_message == "The Sirens are silent now."
    assert calm_waters.interactions["give in"].unavailable_message == "The Sirens are silent now."
    assert calm_waters.interactions["resist"].unavailable_message == "There's nothing left to resist."

def test_build_world_shadow_of_pylos_connects_to_the_forge():
    dungeon, entrance, floors = build_world()
    assert floors["floor_5"]["Shadow of Pylos"].get_exit("forge") is floors["floor_2"]["Forge of Prometheus"]

def test_build_world_shadow_of_ithaca_connects_to_the_forge():
    dungeon, entrance, floors = build_world()
    assert floors["floor_6"]["Shadow of Ithaca"].get_exit("forge") is floors["floor_2"]["Forge of Prometheus"]

def test_build_world_forge_connects_back_to_shadow_of_pylos_and_shadow_of_ithaca():
    dungeon, entrance, floors = build_world()
    forge = floors["floor_2"]["Forge of Prometheus"]
    assert forge.get_exit("shadow of pylos") is floors["floor_5"]["Shadow of Pylos"]
    assert forge.get_exit("shadow of ithaca") is floors["floor_6"]["Shadow of Ithaca"]

def test_build_world_shadow_of_pylos_forge_exit_registers_activation_for_the_forge():
    dungeon, entrance, floors = build_world()
    forge = floors["floor_2"]["Forge of Prometheus"]
    assert floors["floor_5"]["Shadow of Pylos"].exit_activations["forge"] == (forge, "shadow of pylos")

def test_build_world_shadow_of_ithaca_forge_exit_registers_activation_for_the_forge():
    dungeon, entrance, floors = build_world()
    forge = floors["floor_2"]["Forge of Prometheus"]
    assert floors["floor_6"]["Shadow of Ithaca"].exit_activations["forge"] == (forge, "shadow of ithaca")

def test_build_world_pylos_and_ithaca_descriptions_point_at_the_forge_exit():
    dungeon, entrance, floors = build_world()
    assert "say 'forge'" in floors["floor_5"]["Shadow of Pylos"].description
    assert "say 'forge'" in floors["floor_6"]["Shadow of Ithaca"].description

def test_create_laestrygonian_hide_sits_between_athenas_breastplate_and_talos_plating():
    defence = create_laestrygonian_hide().defence
    assert create_breastplate_of_athena().defence < defence < create_talos_bronze_plating().defence

def test_create_polyphemus_has_correct_stats():
    polyphemus = create_polyphemus()
    assert polyphemus.name == "Polyphemus"
    assert polyphemus.hp == 42
    assert polyphemus.attack_damage == 12
    assert polyphemus.armour == 3
    assert polyphemus.brace_amount == 4

def test_create_polyphemus_rises_again_as_his_blinded_phase():
    assert create_polyphemus().next_phase_factory is create_polyphemus_blinded

def test_create_polyphemus_first_phase_carries_no_rewards():
    """Only the final phase pays out - same as Medusa."""
    polyphemus = create_polyphemus()
    assert polyphemus.loot == []
    assert polyphemus.experience_reward == 0
    assert polyphemus.gold_reward == 0

def test_create_polyphemus_greets_cyclops_and_poseidon_descendants():
    lines = create_polyphemus().ancestry_lines
    assert set(lines) == {"cyclops", "poseidon"}
    assert set(lines) <= set(ANCESTRIES)

def test_create_polyphemus_blinded_has_correct_stats():
    blinded = create_polyphemus_blinded()
    assert blinded.name == "Polyphemus (Blinded)"
    assert blinded.hp == 36
    assert blinded.attack_damage == 17
    assert blinded.armour == 3
    assert blinded.aggression_weight == 1.6
    assert blinded.next_phase_factory is None

def test_create_polyphemus_blinded_starts_blinded_for_the_whole_fight():
    blinded = create_polyphemus_blinded()
    assert [effect.name for effect in blinded.active_effects] == ["Blinded"]
    assert blinded.active_effects[0].duration >= 100
    assert blinded.get_miss_chance("light") == 0.35

def test_create_polyphemus_blinded_pays_out_and_drops_the_stake():
    blinded = create_polyphemus_blinded()
    assert [item.name for item in blinded.loot] == ["Olive-wood Stake"]
    assert blinded.experience_reward == 60
    assert blinded.gold_reward == 35

def test_create_polyphemus_blinded_builds_a_fresh_blindness_each_time():
    assert create_polyphemus_blinded().active_effects[0] is not create_polyphemus_blinded().active_effects[0]

def test_create_olive_wood_stake_is_a_blinding_piercing_weapon():
    stake = create_olive_wood_stake()
    assert stake.name == "Olive-wood Stake"
    assert stake.weapon_class == "piercing"
    assert stake.damage == 7
    assert stake.armour_pierce == 3
    assert stake.blind_chance == 0.2
    assert stake.two_handed is False

def test_create_wheel_of_cheese_is_a_free_eight_hp_heal():
    cheese = create_wheel_of_cheese()
    assert cheese.heal_amount == 8
    assert cheese.ends_turn(Player(name="Hero", hp=20)) is False

def test_create_head_of_scylla_has_correct_stats():
    head = create_head_of_scylla()
    assert head.name == "Head of Scylla"
    assert head.hp == 12
    assert head.attack_damage == 7
    assert head.armour == 0
    assert head.aggression_weight == 1.4

def test_create_head_of_scylla_drops_no_items():
    assert create_head_of_scylla().loot == []

def test_create_boars_tusk_helm_is_a_heavy_helmet():
    helm = create_boars_tusk_helm()
    assert helm.name == "Boar's-Tusk Helm"
    assert helm.slot == "helmet"
    assert helm.weight == "heavy"
    assert helm.defence == 3
    assert helm.max_durability == 14

def test_create_boars_tusk_helm_out_defends_hectors_helm():
    assert create_boars_tusk_helm().defence > create_hectors_helm().defence

def test_build_floor_6_places_polyphemus_and_two_wheels_of_cheese():
    _, rooms = build_floor_6()
    cavern = rooms["Cavern of Polyphemus"]
    assert [e.name for e in cavern.enemies] == ["Polyphemus"]
    assert [item.name for item in cavern.items] == ["Wheel of Cheese", "Wheel of Cheese"]
    assert cavern.items[0] is not cavern.items[1]

def test_build_floor_6_leaves_the_optional_cavern_unguarded():
    _, rooms = build_floor_6()
    assert rooms["Cavern of Polyphemus"].guarded_exits == set()

def test_build_floor_6_places_six_separate_heads_of_scylla():
    _, rooms = build_floor_6()
    heads = rooms["Rocky Shore"].enemies
    assert [e.name for e in heads] == ["Head of Scylla"] * 6
    assert len({id(head) for head in heads}) == 6

def test_build_floor_6_places_the_boars_tusk_helm_on_rocky_shore():
    _, rooms = build_floor_6()
    assert [item.name for item in rooms["Rocky Shore"].items] == ["Boar's-Tusk Helm"]

def test_build_floor_6_scylla_guards_the_way_south():
    _, rooms = build_floor_6()
    assert rooms["Rocky Shore"].guarded_exits == {"south"}

def test_titled_enemies_are_introduced_with_the():
    for factory in (create_crypt_keeper, create_minotaur, create_shade_of_hector, create_shade_of_ajax, create_shade_of_paris,
                    create_shade_of_achilles_duellist):
        enemy = factory()
        assert enemy.with_article() == f"The {enemy.name}", enemy.name

def test_proper_named_enemies_take_no_article():
    for factory in (create_lamia, create_talos, create_medusa, create_medusa_awakened, create_antiphates, create_polyphemus,
                    create_polyphemus_blinded):
        enemy = factory()
        assert enemy.with_article() == enemy.name, enemy.name

def charybdis_state():
    return {"phase": 0, "position": "raft", "freed": False}

def test_create_charybdis_is_an_invulnerable_placeholder():
    charybdis = create_charybdis()
    assert charybdis.name == "Charybdis"
    assert charybdis.invulnerable is True
    assert charybdis.hp == 1
    assert charybdis.attack_damage == 0
    assert charybdis.article == ""
    assert charybdis.invulnerable_message == "You can't fight a whirlpool - you'll have to find another way past."

def test_create_charybdis_carries_the_puzzles_rewards():
    charybdis = create_charybdis()
    assert [item.name for item in charybdis.loot] == ["Hoplon of the Drowned"]
    assert charybdis.experience_reward == 50
    assert charybdis.gold_reward == 25
    assert "Charybdis sinks" in charybdis.defeat_effect(Player(name="Hero", hp=20))

def test_create_hoplon_of_the_drowned_is_a_light_shield():
    hoplon = create_hoplon_of_the_drowned()
    assert hoplon.slot == "shield"
    assert hoplon.weight == "light"
    assert hoplon.defence == 2
    assert hoplon.max_durability == 12

def test_build_floor_6_places_charybdis_guarding_narrow_rivers_way_west():
    _, rooms = build_floor_6()
    assert [e.name for e in rooms["Narrow River"].enemies] == ["Charybdis"]
    assert rooms["Narrow River"].guarded_exits == {"west"}

def test_build_floor_6_narrow_river_offers_the_four_charybdis_verbs():
    _, rooms = build_floor_6()
    assert rooms["Narrow River"].available_interactions(Player(name="Hero", hp=20)) == ["watch", "climb", "let go", "row"]

def test_build_floor_6_charybdis_verbs_fall_silent_once_she_is_gone():
    _, rooms = build_floor_6()
    river = rooms["Narrow River"]
    river.enemies[0].hp = 0
    assert river.available_interactions(Player(name="Hero", hp=20)) == []
    assert river.interactions["row"].unavailable_message == "The water is calm now - Charybdis has let you pass."

def test_charybdis_phases_run_still_swallowing_drained_spewing():
    assert CHARYBDIS_PHASES == ("still", "swallowing", "drained", "spewing")

def test_resolve_charybdis_action_the_myths_solution_solves_it():
    """Climb while she swallows, hold on while she's drained, let go as she spews the raft back up, row while the water is still - with the
    whirlpool advancing one phase after every action, exactly as the room's handler does."""
    state = charybdis_state()
    outcomes = []
    for verb in ("climb", "watch", "watch", "let go", "row"):
        outcome, _ = resolve_charybdis_action(verb, CHARYBDIS_PHASES[state["phase"]], state)
        outcomes.append(outcome)
        state["phase"] = (state["phase"] + 1) % len(CHARYBDIS_PHASES)
    assert outcomes == ["ok", "ok", "ok", "ok", "solved"]

def test_resolve_charybdis_action_climbing_puts_you_in_the_fig_tree():
    state = charybdis_state()
    outcome, _ = resolve_charybdis_action("climb", "swallowing", state)
    assert outcome == "ok"
    assert state["position"] == "tree"

def test_resolve_charybdis_action_staying_on_the_raft_while_she_swallows_fails():
    for verb in ("watch", "row", "let go"):
        outcome, _ = resolve_charybdis_action(verb, "swallowing", charybdis_state())
        assert outcome == "fail", verb

def test_resolve_charybdis_action_letting_go_too_early_fails():
    for phase in ("swallowing", "drained"):
        state = charybdis_state()
        state["position"] = "tree"
        outcome, _ = resolve_charybdis_action("let go", phase, state)
        assert outcome == "fail", phase

def test_resolve_charybdis_action_letting_go_as_she_spews_frees_the_raft():
    state = charybdis_state()
    state["position"] = "tree"
    outcome, _ = resolve_charybdis_action("let go", "spewing", state)
    assert outcome == "ok"
    assert state["position"] == "raft"
    assert state["freed"] is True

def test_resolve_charybdis_action_letting_go_on_still_water_drops_you_back_unfreed():
    state = charybdis_state()
    state["position"] = "tree"
    resolve_charybdis_action("let go", "still", state)
    assert state["position"] == "raft"
    assert state["freed"] is False

def test_resolve_charybdis_action_rowing_before_the_raft_is_freed_does_not_solve_it():
    outcome, _ = resolve_charybdis_action("row", "still", charybdis_state())
    assert outcome == "ok"

def test_resolve_charybdis_action_rowing_freed_but_not_on_still_water_does_not_solve_it():
    state = charybdis_state()
    state["freed"] = True
    outcome, _ = resolve_charybdis_action("row", "drained", state)
    assert outcome == "ok"

def test_resolve_charybdis_action_holding_on_in_the_tree_is_always_safe():
    for phase in CHARYBDIS_PHASES:
        state = charybdis_state()
        state["position"] = "tree"
        for verb in ("watch", "climb", "row"):
            outcome, _ = resolve_charybdis_action(verb, phase, state)
            assert outcome == "ok", (verb, phase)
            assert state["position"] == "tree"

def run_charybdis_verbs(river, player, verbs):
    return [river.interactions[verb].handler(player, river) for verb in verbs]

def test_charybdis_verb_advances_the_whirlpool_and_describes_it():
    _, rooms = build_floor_6()
    river = rooms["Narrow River"]
    message = river.interactions["climb"].handler(Player(name="Hero", hp=30), river)
    assert "fig tree" in message
    assert "The sea begins to" in message
    assert river.transient_state["charybdis"]["phase"] == 1

def test_charybdis_verb_failure_deals_twelve_damage_and_restarts_the_puzzle():
    _, rooms = build_floor_6()
    river = rooms["Narrow River"]
    player = Player(name="Hero", hp=30)
    messages = run_charybdis_verbs(river, player, ["climb", "let go"])
    assert player.hp == 18
    assert "(You take 12 damage.)" in messages[-1]
    assert "spits you back out" in messages[-1]
    assert "charybdis" not in river.transient_state

def test_charybdis_verb_failure_can_kill():
    _, rooms = build_floor_6()
    river = rooms["Narrow River"]
    player = Player(name="Hero", hp=10)
    messages = run_charybdis_verbs(river, player, ["climb", "let go"])
    assert player.hp == 0
    assert "The sea closes over you." in messages[-1]

def test_charybdis_solving_the_puzzle_pays_out_and_opens_the_way():
    _, rooms = build_floor_6()
    river = rooms["Narrow River"]
    player = Player(name="Hero", hp=30)
    messages = run_charybdis_verbs(river, player, ["climb", "watch", "watch", "let go", "row"])
    assert "Charybdis sinks" in messages[-1]
    assert river.enemies == []
    assert [item.name for item in river.items] == ["Hoplon of the Drowned"]
    assert player.gold == 25
    assert river.available_interactions(player) == []
    assert "charybdis" not in river.transient_state

def test_charybdis_clearing_transient_state_restarts_the_puzzle():
    """main() clears it on leaving the room - a half-finished attempt never carries over."""
    _, rooms = build_floor_6()
    river = rooms["Narrow River"]
    player = Player(name="Hero", hp=30)
    river.interactions["climb"].handler(player, river)
    river.transient_state.clear()
    message = river.interactions["let go"].handler(player, river)
    assert "You're not holding on to anything." in message
    assert player.hp == 30

def test_create_poseidon_has_correct_stats():
    poseidon = create_poseidon()
    assert poseidon.name == "Poseidon"
    assert poseidon.hp == 48
    assert poseidon.attack_damage == 13
    assert poseidon.armour == 4
    assert poseidon.armour_pierce == 3
    assert poseidon.heal_amount == 8
    assert poseidon.brace_amount == 4
    assert poseidon.caution_weight == 1.4
    assert poseidon.article == ""

def test_create_poseidon_first_phase_carries_no_rewards():
    poseidon = create_poseidon()
    assert poseidon.loot == []
    assert poseidon.experience_reward == 0
    assert poseidon.gold_reward == 0

def test_create_poseidon_rises_again_as_the_earth_shaker():
    assert create_poseidon().next_phase_factory is create_poseidon_earth_shaker

def test_create_poseidon_greets_his_own_and_odysseus_descendants():
    lines = create_poseidon().ancestry_lines
    assert set(lines) == {"poseidon", "odysseus"}
    assert set(lines) <= set(ANCESTRIES)

def test_create_hippocampus_has_correct_stats_and_drops_a_kelp_poultice():
    hippocampus = create_hippocampus()
    assert hippocampus.name == "Hippocampus"
    assert hippocampus.hp == 14
    assert hippocampus.attack_damage == 9
    assert hippocampus.armour == 1
    assert hippocampus.aggression_weight == 1.5
    assert [item.name for item in hippocampus.loot] == ["Kelp Poultice"]

def test_create_poseidon_earth_shaker_has_correct_stats():
    shaker = create_poseidon_earth_shaker()
    assert shaker.name == "Poseidon (Earth-Shaker)"
    assert shaker.hp == 42
    assert shaker.attack_damage == 16
    assert shaker.armour == 3
    assert shaker.armour_pierce == 3
    assert shaker.heal_amount == 5
    assert shaker.aggression_weight == 1.6
    assert shaker.caution_weight == 0.8
    assert shaker.article == ""
    assert shaker.next_phase_factory is None

def test_create_poseidon_earth_shaker_pays_out_and_drops_the_trident():
    shaker = create_poseidon_earth_shaker()
    assert [item.name for item in shaker.loot] == ["Trident of the Depths"]
    assert shaker.experience_reward == 90
    assert shaker.gold_reward == 50

def test_create_trident_of_the_depths_pierces_and_cleaves():
    trident = create_trident_of_the_depths()
    assert trident.weapon_class == "piercing"
    assert trident.damage == 8
    assert trident.armour_pierce == 3
    assert trident.cleave is True
    assert trident.two_handed is False

def test_create_kelp_poultice_is_a_free_twelve_hp_heal():
    poultice = create_kelp_poultice()
    assert poultice.heal_amount == 12
    assert poultice.ends_turn(Player(name="Hero", hp=20)) is False

def test_create_odysseus_has_correct_stats():
    odysseus = create_odysseus()
    assert odysseus.name == "Odysseus"
    assert odysseus.hp == 36
    assert odysseus.attack_damage == 11
    assert odysseus.armour == 2
    assert odysseus.brace_amount == 3
    assert odysseus.heal_amount == 4

def test_create_odysseus_fights_at_range_and_gives_advice():
    odysseus = create_odysseus()
    assert odysseus.attack_type == "ranged"
    assert odysseus.gives_advice is True

def test_create_odysseus_waits_for_the_suitors_to_be_cleared():
    odysseus = create_odysseus()
    player = Player(name="Hero", hp=20)
    assert odysseus.required_story_flag == "suitors_cleared"
    assert odysseus.can_be_recruited(player) is False
    player.story_flags.add("suitors_cleared")
    assert odysseus.can_be_recruited(player) is True

def test_create_odysseus_has_no_duel_and_an_ancestry_line_for_his_own():
    odysseus = create_odysseus()
    assert odysseus.requires_duel is False
    assert set(odysseus.ancestry_lines) == {"odysseus"}

def test_create_odysseus_with_no_home_room_gets_a_placeholder():
    assert create_odysseus().home_room.name == "Shadow of Ithaca"

def test_build_floor_6_places_poseidon_guarding_the_depths():
    _, rooms = build_floor_6()
    depths = rooms["Poseidon's Depths"]
    assert [e.name for e in depths.enemies] == ["Poseidon"]
    assert depths.guarded_exits == {"south"}

def test_build_floor_6_places_odysseus_at_home_in_ithaca():
    _, rooms = build_floor_6()
    ithaca = rooms["Shadow of Ithaca"]
    assert [c.name for c in ithaca.companions] == ["Odysseus"]
    assert ithaca.companions[0].home_room is ithaca

def test_build_floor_6_gives_the_sirens_and_charybdis_rooms_their_own_advice():
    _, rooms = build_floor_6()
    assert "mast" in rooms["Calm Waters"].advice
    assert "swallow" in rooms["Narrow River"].advice
    assert [name for name, room in rooms.items() if room.advice] == ["Calm Waters", "Narrow River"]

def test_create_poseidon_wave_is_built_from_factories():
    """Regression: the wave was first written as [create_hippocampus(), create_hippocampus()] - two Enemy instances - so defeating
    Poseidon's first phase crashed the game calling them."""
    wave = create_poseidon().next_wave_factories
    assert wave == [create_hippocampus, create_hippocampus]

def test_odysseus_talk_changes_once_the_suitors_are_cleared():
    odysseus = create_odysseus()
    player = Player(name="Hero", hp=20)
    assert "Twenty years" in odysseus.talk(player)
    player.story_flags.add("suitors_cleared")
    assert "recruit odysseus" in odysseus.talk(player)

def test_create_circe_makes_six_offers():
    offers = create_circe().offers
    assert len(offers) == 6
    assert [offer.describe() for offer in offers[:5]] == [
        "Bronze Xiphos + 20 gold -> Kelp Poultice",
        "Weathered Helm + 20 gold -> Kelp Poultice",
        "Bronze Breastplate + 30 gold -> Cup of Kykeon",
        "Harpy-fletched Bow + 30 gold -> Cup of Kykeon",
        "Small Healing Potion + 10 gold -> Kelp Poultice",
    ]

def test_create_circe_has_nothing_to_trade():
    circe = create_circe()
    assert circe.required_items == []
    assert circe.reward is None

def test_create_circe_has_an_exchange_line_and_points_at_offers():
    circe = create_circe()
    assert circe.exchange_line != ""
    assert "'offers'" in circe.hint

def test_build_floor_6_places_circe_in_the_muddy_pigsty():
    _, rooms = build_floor_6()
    assert [a.name for a in rooms["Muddy Pigsty"].allies] == ["Circe"]

def test_nestor_and_circe_share_the_cup_of_kykeon_factory():
    """Used by two floors now, so it lives in content/common.py."""
    nestor_cup = create_nestor().inventory.items[0]
    circe_cup = next(o for o in create_circe().offers if o.output_name == "Cup of Kykeon").output_factory()
    assert nestor_cup.name == circe_cup.name == "Cup of Kykeon"
    assert nestor_cup is not circe_cup

def test_every_circe_offer_asks_for_a_real_item():
    """Regression: the Wineskin of Dionysus offer was spelt 'Wineskine', so it could never be accepted. Every input must be an item
    ITEM_REGISTRY can build under that exact name."""
    for offer in create_circe().offers:
        item = find_item_by_name(offer.input_name)
        assert item is not None, offer.input_name
        assert item.name == offer.input_name

def test_create_circe_sixth_offer_turns_the_wineskin_into_kykeon():
    assert create_circe().offers[5].describe() == "Wineskin of Dionysus + 20 gold -> Cup of Kykeon"

def test_possessive_named_items_take_no_article():
    for factory in (create_mentors_token, create_charons_coin, create_lamias_fang, create_talos_bronze_plating, create_serpents_kiss,
                    create_hectors_helm, create_antiphates_club):
        item = factory()
        assert item.with_article() == item.name, item.name

def test_unique_titled_items_always_take_the():
    for factory in (create_cyclops_eye, create_spear_of_ares, create_breastplate_of_athena, create_tower_shield_of_ajax, create_bow_of_paris,
                    create_hoplon_of_the_drowned, create_trident_of_the_depths):
        item = factory()
        assert item.with_article() == f"the {item.name}", item.name

def test_ordinary_items_take_a_or_an():
    assert create_bronze_xiphos().with_article() == "a Bronze Xiphos"
    assert create_olive_wood_stake().with_article() == "an Olive-wood Stake"

def test_create_suitor_has_correct_stats():
    suitor = create_suitor()
    assert suitor.name == "Suitor"
    assert (suitor.hp, suitor.attack_damage, suitor.armour) == (16, 8, 1)
    assert suitor.loot == []
    assert (suitor.experience_reward, suitor.gold_reward) == (14, 15)

def test_create_antinous_is_an_aggressive_named_suitor_with_a_goblet():
    antinous = create_antinous()
    assert (antinous.hp, antinous.attack_damage, antinous.armour) == (24, 10, 2)
    assert antinous.aggression_weight == 1.5
    assert antinous.article == ""
    assert [item.name for item in antinous.loot] == ["Antinous' Goblet"]
    assert set(antinous.ancestry_lines) == {"odysseus"}

def test_create_eurymachus_braces_and_heals():
    eurymachus = create_eurymachus()
    assert (eurymachus.hp, eurymachus.attack_damage, eurymachus.armour) == (22, 9, 2)
    assert (eurymachus.brace_amount, eurymachus.heal_amount, eurymachus.caution_weight) == (3, 4, 1.3)
    assert [item.name for item in eurymachus.loot] == ["Kelp Poultice"]

def test_create_antinous_goblet_is_a_free_regen():
    goblet = create_antinous_goblet()
    assert (goblet.effect_name, goblet.amount, goblet.duration) == ("Regen", 5, 3)
    assert goblet.ends_turn(Player(name="Hero", hp=20)) is False
    assert goblet.with_article() == "Antinous' Goblet"

def test_create_penelopes_thread_is_a_loyalty_token():
    thread = create_penelopes_thread()
    assert isinstance(thread, LoyaltyToken)
    assert thread.with_article() == "Penelope's Thread"

def test_create_penelope_gives_her_thread_and_has_nothing_to_trade():
    penelope = create_penelope()
    assert [item.name for item in penelope.inventory.items] == ["Penelope's Thread"]
    assert penelope.required_items == []
    assert penelope.reward is None
    assert "take penelope's thread from penelope" in penelope.hint

def test_create_penelope_has_lines_for_odysseus_and_achilles():
    assert set(create_penelope().companion_lines) == {"Odysseus", "Shade of Achilles"}

def test_penelopes_companion_lines_name_real_companions():
    """Keyed by companion name - a renamed companion would silently lose its line."""
    names = {create_odysseus().name, create_shade_of_achilles().name}
    assert set(create_penelope().companion_lines) <= names

def test_build_floor_6_places_the_suitors_in_the_throne_room_antinous_first():
    _, rooms = build_floor_6()
    assert [e.name for e in rooms["Throne Room of Odysseus"].enemies] == ["Antinous", "Eurymachus", "Suitor", "Suitor", "Suitor"]

def test_build_floor_6_the_suitors_guard_the_way_to_the_bedchamber():
    _, rooms = build_floor_6()
    throne = rooms["Throne Room of Odysseus"]
    assert throne.guarded_exits == {"west"}
    assert throne.get_exit("west") is rooms["Bedchamber of Odysseus"]

def test_build_floor_6_clearing_the_throne_room_sets_suitors_cleared():
    _, rooms = build_floor_6()
    throne = rooms["Throne Room of Odysseus"]
    assert throne.cleared_story_flag == "suitors_cleared"
    assert throne.cleared_message != ""

def test_the_throne_rooms_flag_is_the_one_odysseus_waits_for():
    _, rooms = build_floor_6()
    assert rooms["Throne Room of Odysseus"].cleared_story_flag == create_odysseus().required_story_flag

def test_build_floor_6_places_penelope_in_the_bedchamber():
    _, rooms = build_floor_6()
    assert [a.name for a in rooms["Bedchamber of Odysseus"].allies] == ["Penelope"]

def test_penelopes_description_has_her_sitting_at_the_loom():
    assert create_penelope().description.startswith("She sits at the loom")

def _tiresias_and_player():
    """The world-wired Tiresias, and a player who has reached floor 7 (floor 8 below has no enemies yet), carries a heal, and has a
    companion - so none of his warnings apply."""
    dungeon, start, floors = build_world()
    tiresias = floors["floor_7"]["Shadow of Thebes"].allies[0]
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_7"}
    player.inventory.add(create_small_healing_potion())
    player.companion = Companion(name="Imp", hp=10, home_room=Room("Camp"))
    return tiresias, player

def test_tiresias_with_nothing_to_warn_about_says_go_down():
    """Regression: the reading crashed with AttributeError (inventory.item for inventory.items), and this line had a comma splice."""
    tiresias, player = _tiresias_and_player()
    message = tiresias.talk(player)
    assert message.endswith('"I look, and I find nothing waiting. Go down, then."')

def test_tiresias_names_a_carried_signature_weapon_that_is_never_equipped():
    tiresias, player = _tiresias_and_player()
    player.inventory.add(create_labrys())
    assert '"You carry a Labrys and never raise it."' in tiresias.talk(player)

def test_oracle_ask_ahead_ends_with_the_prophecies_remaining():
    """Regression: the remaining-count line printed the helper function itself, since _remaining_note was never called."""
    dungeon, start, floors = build_world()
    chamber = floors["floor_7"]["Chamber of the Oracle"]
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_5"}
    message = chamber.interactions["ask ahead"].handler(player, chamber)
    assert message.endswith("\n(2 prophecies remain.)")

def test_persephone_first_conversation_gives_the_pomegranate_and_sets_its_flag():
    """The flag is saved in Player.story_flags, so its spelling is pinned (it was first 'persophone_...')."""
    dungeon, start, floors = build_world()
    bedchamber = floors["floor_7"]["Bedchamber of Persephone"]
    player = Player(name="Hero", hp=20)
    talk_to(bedchamber.allies[0], player, bedchamber)
    assert "persephone_pomegranate_given" in player.story_flags
    assert [item.name for item in player.inventory.items] == ["Pomegranate"]

# ---- floor 7: the Oracle ----

def _oracle_chamber():
    dungeon, start, floors = build_world()
    return floors["floor_7"]["Chamber of the Oracle"]

def _ask(chamber, verb, player):
    return chamber.interactions[verb].handler(player, chamber)

def test_build_world_gives_the_oracle_her_two_questions():
    chamber = _oracle_chamber()
    assert chamber.available_interactions(Player(name="Hero", hp=20)) == ["ask ahead", "ask secrets"]

def test_oracle_first_talk_opens_with_the_twist_prophecy():
    chamber = _oracle_chamber()
    message = talk_to(chamber.allies[0], Player(name="Hero", hp=20), chamber)
    assert message.startswith(ORACLE_TWIST)

def test_oracle_twist_prophecy_is_only_given_once():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    talk_to(chamber.allies[0], player, chamber)
    assert ORACLE_TWIST not in talk_to(chamber.allies[0], player, chamber)

def test_oracle_talk_itself_has_no_side_effects():
    """Regression: the greeting used to record the twist as seen from inside talk(), which must stay free of side effects - it's
    the Oracle's opening_line now, consumed by talk_to()."""
    player = Player(name="Hero", hp=20)
    message = create_oracle().talk(player)
    assert ORACLE_TWIST not in message
    assert player.seen_lines == set()

def test_oracle_twist_given_by_a_question_is_not_repeated_on_talk():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_0"}
    first = _ask(chamber, "ask ahead", player)
    assert first.startswith(ORACLE_TWIST)
    assert ORACLE_TWIST not in talk_to(chamber.allies[0], player, chamber)

def test_oracle_ask_ahead_foretells_the_next_floors_traits_in_order():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.seen_lines.add("opening:Oracle")
    player.visited_floors = {"floor_5"}
    message = _ask(chamber, "ask ahead", player)
    expected = [f'"{ORACLE_PHRASES[trait]}"' for trait in ("heavy_armour", "heals", "pierces", "numerous", "puzzle")]
    assert message.split("\n") == expected + ["(2 prophecies remain.)"]

def test_oracle_ask_ahead_with_no_notable_traits_sees_only_strength():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.seen_lines.add("opening:Oracle")
    player.visited_floors = {"floor_0"}
    assert _ask(chamber, "ask ahead", player) == f'"{ORACLE_NOTHING_STRANGE}"\n(2 prophecies remain.)'

def test_oracle_ask_ahead_with_no_enemies_below_is_not_spent():
    """Floor 8 has no enemies placed yet, so from floor 7 there's nothing to foretell."""
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_7"}
    message = _ask(chamber, "ask ahead", player)
    assert "(That prophecy was not spent.)" in message
    assert chamber.flags == set()

def test_oracle_ask_ahead_twice_for_the_same_floor_is_not_spent_again():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_5"}
    _ask(chamber, "ask ahead", player)
    message = _ask(chamber, "ask ahead", player)
    assert message == '"I have told you what waits below. Go and meet it." (That prophecy was not spent.)'
    assert chamber.flags == {"prophecy:ahead:floor_6"}

def test_oracle_ask_secrets_names_the_first_unfound_hidden_exit():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.seen_lines.add("opening:Oracle")
    player.visited_floors = {"floor_1", "floor_2"}
    message = _ask(chamber, "ask secrets", player)
    assert message == '"In Styx Crossing, a way lies hidden that you have walked straight past."\n(2 prophecies remain.)'

def test_oracle_ask_secrets_moves_on_and_warns_when_intellect_is_too_low():
    chamber = _oracle_chamber()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_1", "floor_2"}
    _ask(chamber, "ask secrets", player)
    message = _ask(chamber, "ask secrets", player)
    assert '"In Armoury of Ares, a way lies hidden' in message
    assert '"It will not show itself to a mind duller than 3."' in message

def test_oracle_ask_secrets_skips_a_hidden_exit_already_found():
    dungeon, start, floors = build_world()
    chamber = floors["floor_7"]["Chamber of the Oracle"]
    floors["floor_1"]["Styx Crossing"].reveal_hidden_exits()
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_1"}
    message = chamber.interactions["ask secrets"].handler(player, chamber)
    assert "(That prophecy was not spent.)" in message
    assert chamber.flags == set()

def test_oracle_last_prophecy_says_she_will_answer_no_more():
    chamber = _oracle_chamber()
    chamber.flags.update({"prophecy:ahead:floor_1", "prophecy:ahead:floor_2"})
    player = Player(name="Hero", hp=20)
    player.visited_floors = {"floor_1"}
    assert _ask(chamber, "ask secrets", player).endswith("(She will answer no more.)")

def test_oracle_questions_fall_silent_after_three_prophecies():
    chamber = _oracle_chamber()
    chamber.flags.update({"prophecy:ahead:floor_1", "prophecy:ahead:floor_2", "prophecy:secret:Styx Crossing"})
    player = Player(name="Hero", hp=20)
    assert chamber.available_interactions(player) == []
    assert chamber.interactions["ask ahead"].unavailable_message == '"I have said all I will say."'

# ---- floor 7: Tiresias ----

def _tiresias_reading(player, visited_floor):
    tiresias, _ = _tiresias_and_player()
    player.visited_floors = {visited_floor}
    return tiresias.talk(player)

def test_tiresias_before_world_wiring_has_a_placeholder_line():
    assert create_tiresias().talk(Player(name="Hero", hp=20)) == '"Not yet," he murmurs. "Come back when I can see you properly."'

def test_build_world_gives_tiresias_his_readings():
    dungeon, start, floors = build_world()
    assert floors["floor_7"]["Shadow of Thebes"].allies[0].dialogue_function is not None

def test_tiresias_warns_about_one_unspent_skill_point():
    tiresias, player = _tiresias_and_player()
    player.skill_tree.skill_points = 1
    assert '"You hold 1 skill point you have not spent.' in tiresias.talk(player)

def test_tiresias_warns_about_several_unspent_skill_points():
    tiresias, player = _tiresias_and_player()
    player.skill_tree.skill_points = 3
    assert '"You hold 3 skill points you have not spent.' in tiresias.talk(player)

def test_tiresias_warns_when_nothing_carried_reaches_an_evasive_enemy():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    assert "Something below keeps its distance" in tiresias.talk(player)

def test_tiresias_does_not_warn_about_evasion_with_a_bow_equipped():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    create_harpy_fletched_bow().use(player)
    assert "Something below keeps its distance" not in tiresias.talk(player)

def test_tiresias_does_not_warn_about_evasion_with_a_ranged_companion():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    player.companion = Companion(name="Archer", hp=10, home_room=Room("Camp"), attack_type="ranged")
    assert "Something below keeps its distance" not in tiresias.talk(player)

def test_tiresias_warns_that_heavy_armour_is_wasted_against_piercing():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    create_bronze_breastplate().use(player)
    assert "You pay for your armour with every swing" in tiresias.talk(player)

def test_tiresias_does_not_warn_about_piercing_in_light_armour():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    create_breastplate_of_athena().use(player)
    assert "You pay for your armour with every swing" not in tiresias.talk(player)

def test_tiresias_warns_a_blade_will_skid_off_heavy_armour():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    create_wooden_sword().use(player)
    assert "Your blade will skid off what waits below." in tiresias.talk(player)

def test_tiresias_does_not_warn_about_heavy_armour_with_a_piercing_weapon():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_4"}
    create_spear_of_ares().use(player)
    assert "Your blade will skid off" not in tiresias.talk(player)

def test_tiresias_warns_about_many_enemies_without_a_cleaving_weapon():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_5"}
    assert "Many will come at you at once" in tiresias.talk(player)

def test_tiresias_does_not_warn_about_many_enemies_with_a_cleaving_weapon():
    tiresias, player = _tiresias_and_player()
    player.visited_floors = {"floor_5"}
    create_labrys().use(player)
    assert "Many will come at you at once" not in tiresias.talk(player)

def test_tiresias_warns_when_nothing_carried_heals():
    tiresias, player = _tiresias_and_player()
    player.inventory.remove(player.inventory.items[0])
    assert '"You carry nothing to mend yourself."' in tiresias.talk(player)

def test_tiresias_counts_a_heal_over_time_as_healing():
    tiresias, player = _tiresias_and_player()
    player.inventory.remove(player.inventory.items[0])
    player.inventory.add(create_cup_of_kykeon())
    assert "You carry nothing to mend yourself." not in tiresias.talk(player)

def test_tiresias_suggests_a_companion_to_a_player_alone():
    tiresias, player = _tiresias_and_player()
    player.companion = None
    assert '"You walk alone. You need not."' in tiresias.talk(player)

def test_tiresias_notices_a_downed_companion():
    tiresias, player = _tiresias_and_player()
    player.companion.hp = 0
    assert '"Imp lies broken beside you. See to that before you go down."' in tiresias.talk(player)

# ---- floor 7: Persephone ----

def _persephone_conversation():
    dungeon, start, floors = build_world()
    bedchamber = floors["floor_7"]["Bedchamber of Persephone"]
    player = Player(name="Hero", hp=20)
    opening = talk_to(bedchamber.allies[0], player, bedchamber)
    return bedchamber, player, opening

def test_persephone_only_gives_one_pomegranate():
    bedchamber, player, opening = _persephone_conversation()
    second = talk_to(bedchamber.allies[0], player, bedchamber)
    assert "(You receive a Pomegranate.)" not in second
    assert len(player.inventory.items) == 1

def test_persephone_why_topic_leads_back_to_the_start():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("1", bedchamber, player)
    message = continue_dialogue("1", bedchamber, player)
    assert "Ask what you want to ask." in message

def test_persephone_promise_sets_promised_mercy():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("2", bedchamber, player)
    message = continue_dialogue("1", bedchamber, player)
    assert PROMISED_MERCY in player.story_flags
    assert REFUSED_MERCY not in player.story_flags
    assert "Thank you." in message

def test_persephone_refusal_sets_refused_mercy():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("2", bedchamber, player)
    continue_dialogue("2", bedchamber, player)
    assert REFUSED_MERCY in player.story_flags
    assert PROMISED_MERCY not in player.story_flags

def test_persephone_thinking_it_over_sets_no_flag():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("2", bedchamber, player)
    message = continue_dialogue("3", bedchamber, player)
    assert "Ask what you want to ask." in message
    assert player.story_flags == {"persephone_pomegranate_given"}

def test_persephone_stops_asking_once_the_choice_is_made():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("2", bedchamber, player)
    continue_dialogue("1", bedchamber, player)
    continue_dialogue("1", bedchamber, player)
    message = talk_to(bedchamber.allies[0], player, bedchamber)
    assert "Ask what she wants of you" not in message
    assert "    2. Leave her be" in message

def test_persephone_leaving_ends_the_conversation():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("3", bedchamber, player)
    assert "dialogue" not in bedchamber.transient_state

def test_pomegranate_restores_full_hp():
    player = Player(name="Hero", hp=30)
    player.hp = 1
    create_pomegranate().use(player)
    assert player.hp == 30

# ---- floor 9 ----

def test_tartarus_is_concealed_until_hades_is_defeated():
    start, rooms = build_floor_9()
    assert rooms["Tartarus"].concealed_until == "hades_defeated"

def _every_real_dialogue():
    """(speaker name, dialogue) for every ally with a branching dialogue, whether placed by build_world() or only spawnable by dev tools."""
    dungeon, start, floors = build_world()
    allies = [ally for rooms in floors.values() for room in rooms.values() for ally in room.allies]
    allies += [factory() for factory in ALLY_REGISTRY.values()]
    return [(ally.name, ally.dialogue) for ally in allies if ally.dialogue]

def test_real_dialogue_exists_to_check():
    assert "Persephone" in [name for name, dialogue in _every_real_dialogue()]

def test_every_real_dialogue_begins_at_a_start_node():
    for name, dialogue in _every_real_dialogue():
        assert "start" in dialogue, name

def test_every_real_dialogue_node_always_offers_an_option():
    """A node with no options offered would leave the conversation open with nothing to answer ('Choose an option from 1 to 0.') until
    the player left the room. Deliberately not handled in dialogue.py - so no real node may do it, whatever the player's state. At least
    one option per node must have no availability check."""
    for name, dialogue in _every_real_dialogue():
        for node_id, node in dialogue.items():
            assert any(option.available is None for option in node.options), f"{name}: '{node_id}' can offer no options"

def test_every_real_dialogue_option_leads_to_a_node_that_exists():
    for name, dialogue in _every_real_dialogue():
        for node_id, node in dialogue.items():
            for option in node.options:
                assert option.next_node is None or option.next_node in dialogue, f"{name}: '{node_id}' -> '{option.next_node}'"

def test_every_real_dialogue_can_be_left():
    """Some option somewhere ends the conversation - otherwise only walking out would."""
    for name, dialogue in _every_real_dialogue():
        assert any(option.next_node is None for node in dialogue.values() for option in node.options), name

def test_build_world_gates_persephones_descent_on_her_choice():
    dungeon, start, floors = build_world()
    gate = floors["floor_7"]["Bedchamber of Persephone"].story_gates["descend"]
    assert gate.required_flags == (PROMISED_MERCY, REFUSED_MERCY)
    assert gate.map_label == "Persephone is waiting for your answer"
    assert gate.blocked_message == (
        "Persephone rises as you reach the stair. \"Not yet. There's something I need to ask of you before you go down to him.\" "
        "(Talk to Persephone.)"
    )

def test_persephone_answering_either_way_opens_the_descent():
    for answer, flag in (("1", PROMISED_MERCY), ("2", REFUSED_MERCY)):
        bedchamber, player, opening = _persephone_conversation()
        continue_dialogue("2", bedchamber, player)
        continue_dialogue(answer, bedchamber, player)
        assert flag in player.story_flags
        assert get_story_gate(bedchamber, "descend", player) is None, flag

def test_persephone_thinking_it_over_leaves_the_descent_shut():
    bedchamber, player, opening = _persephone_conversation()
    continue_dialogue("2", bedchamber, player)
    continue_dialogue("3", bedchamber, player)
    assert get_story_gate(bedchamber, "descend", player) is not None
