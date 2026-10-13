from dungeon_crawler.characters import Player, Companion
from dungeon_crawler.items import Weapon, Armour, Consumable, QuestItem
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.content import build_world
from dungeon_crawler.combat import handle_enemy_defeat
from dungeon_crawler.exploration import recruit_companion, dismiss_companion
from dungeon_crawler.new_game_plus import start_new_game_plus

def played_world():
    """A real world and a player who has been through it - the starting point of every cycle."""
    world, start, floors = build_world()
    return world, floors, Player(name="Hero", hp=20)

def room_named(world, name):
    room = world.get_room(name)
    assert room is not None
    return room

def recruit(world, player, room_name, companion_name):
    """Recruit the companion waiting in room_name - with whatever stood in the way cleared first."""
    room = room_named(world, room_name)
    companion = next(c for c in room.companions if c.name == companion_name)
    companion.duel_won = True
    if companion.required_story_flag is not None:
        player.story_flags.add(companion.required_story_flag)
    recruit_companion(companion_name.lower(), room, player)
    assert player.companion is companion
    return companion

def spare_and_recruit_hades(world, player):
    """Promise mercy, beat the whole Hades chain so he yields, and recruit him."""
    player.story_flags.add("promised_mercy")
    hall = room_named(world, "Hall of Hades")
    while hall.enemies:
        enemy = hall.enemies[0]
        enemy.hp = 0
        handle_enemy_defeat(hall, enemy, player)
    recruit_companion("hades", hall, player)
    assert player.companion is not None and player.companion.name == "Hades"
    return player.companion

# ---- what start_new_game_plus returns ----

def test_start_new_game_plus_returns_a_new_world_its_floors_and_its_starting_room():
    world, floors, player = played_world()
    new_world, new_floors, start = start_new_game_plus(player, floors)
    fresh_world, fresh_start, fresh_floors = build_world()
    assert new_world is not world
    assert list(new_floors) == list(fresh_floors)
    assert start.name == fresh_start.name
    assert new_world.get_room(start.name) is start

def test_start_new_game_plus_builds_the_world_fresh():
    """Everything done in the old world is left behind - a defeated enemy is back."""
    world, floors, player = played_world()
    labyrinth = room_named(world, "Labyrinth of the Minotaur")
    labyrinth.remove_enemy(labyrinth.enemies[0])
    new_world, _, _ = start_new_game_plus(player, floors)
    assert [enemy.name for enemy in room_named(new_world, "Labyrinth of the Minotaur").enemies] == ["Minotaur"]

def test_start_new_game_plus_leaves_placed_trophies_behind():
    world, floors, player = played_world()
    room_named(world, "Trophy Room of Zeus").placed_trophies.add("Heart of Typhon")
    new_world, _, _ = start_new_game_plus(player, floors)
    assert room_named(new_world, "Trophy Room of Zeus").placed_trophies == set()

# ---- the cycle ----

def test_start_new_game_plus_raises_the_cycle_by_one():
    world, floors, player = played_world()
    start_new_game_plus(player, floors)
    assert player.ng_plus_cycle == 1

def test_start_new_game_plus_cycles_keep_counting():
    world, floors, player = played_world()
    _, floors, _ = start_new_game_plus(player, floors)
    _, floors, _ = start_new_game_plus(player, floors)
    assert player.ng_plus_cycle == 2

def test_start_new_game_plus_clears_the_request():
    world, floors, player = played_world()
    player.new_game_plus_requested = True
    start_new_game_plus(player, floors)
    assert player.new_game_plus_requested is False

def test_start_new_game_plus_rolls_a_new_run_seed(monkeypatch):
    """So the random chests hold something different each cycle."""
    world, floors, player = played_world()
    monkeypatch.setattr("random.randrange", lambda upper: 424242)
    start_new_game_plus(player, floors)
    assert player.run_seed == 424242

# ---- what the character keeps ----

def test_start_new_game_plus_keeps_level_stats_and_experience():
    world, floors, player = played_world()
    player.level = 7
    player.experience = 33
    player.max_hp = 34
    player.attack_damage = 19
    player.base_armour = 6
    player.intellect = 11
    player.max_mana = 30
    start_new_game_plus(player, floors)
    assert (player.level, player.experience, player.max_hp, player.attack_damage) == (7, 33, 34, 19)
    assert (player.base_armour, player.intellect, player.max_mana) == (6, 11, 30)

def test_start_new_game_plus_keeps_learned_skills_and_unspent_points():
    world, floors, player = played_world()
    player.skill_tree.skill_points = 3
    player.skill_tree.invest("attack", player)
    attack_after_skill = player.attack_damage
    start_new_game_plus(player, floors)
    assert player.skill_tree.total_unlocked == 1
    assert player.skill_tree.skill_points == 2
    assert player.attack_damage == attack_after_skill

def test_start_new_game_plus_keeps_the_difficulty_and_ancestry():
    world, floors, player = played_world()
    player.difficulty = "easy"
    player.ancestry_key = "athena"
    player.has_iron_hide = True
    start_new_game_plus(player, floors)
    assert player.difficulty == "easy"
    assert player.ancestry_key == "athena"
    assert player.has_iron_hide is True

def test_start_new_game_plus_keeps_hints_already_seen():
    world, floors, player = played_world()
    player.seen_hints = {"combat", "forge"}
    start_new_game_plus(player, floors)
    assert player.seen_hints == {"combat", "forge"}

def test_start_new_game_plus_restores_the_player_to_full_health():
    world, floors, player = played_world()
    player.hp = 3
    player.apply_status_effect(StatusEffect("Poison", -2, 3))
    start_new_game_plus(player, floors)
    assert player.hp == player.max_hp
    assert player.active_effects == []

def test_start_new_game_plus_ends_any_combat_state():
    world, floors, player = played_world()
    player.in_combat = True
    player.current_target = room_named(world, "Labyrinth of the Minotaur").enemies[0]
    start_new_game_plus(player, floors)
    assert player.in_combat is False
    assert player.current_target is None

# ---- what's left behind ----

def test_start_new_game_plus_empties_the_inventory():
    world, floors, player = played_world()
    for item in (Weapon("Sword", "", 5), Consumable("Potion", "", 5), QuestItem("Coin", "")):
        player.inventory.add(item)
    start_new_game_plus(player, floors)
    assert player.inventory.items == []

def test_start_new_game_plus_unequips_weapons_and_armour():
    world, floors, player = played_world()
    sword, bow = Weapon("Sword", "", 5), Weapon("Bow", "", 4, slot="ranged", weapon_class="ranged")
    plate, helm, shield = Armour("Plate", "", 4), Armour("Helm", "", 1, slot="helmet"), Armour("Shield", "", 2, slot="shield")
    for item in (sword, bow, plate, helm, shield):
        player.inventory.add(item)
        item.use(player)
    start_new_game_plus(player, floors)
    assert (player.equipped_melee_weapon, player.equipped_ranged_weapon) == (None, None)
    assert (player.equipped_body, player.equipped_helmet, player.equipped_shield) == (None, None, None)

def test_start_new_game_plus_takes_worn_armour_off_the_players_armour():
    """Armour is base armour plus worn gear - stripping the gear must leave exactly the base."""
    world, floors, player = played_world()
    player.base_armour = 3
    plate = Armour("Plate", "", 4)
    player.inventory.add(plate)
    plate.use(player)
    assert player.armour == 7
    start_new_game_plus(player, floors)
    assert player.armour == 3

def test_start_new_game_plus_takes_the_gold():
    world, floors, player = played_world()
    player.gold = 1200
    start_new_game_plus(player, floors)
    assert player.gold == 0

def test_start_new_game_plus_forgets_where_the_player_has_been():
    world, floors, player = played_world()
    player.visited_floors = {"floor_0", "floor_1"}
    player.visited_rooms = {"Styx Crossing"}
    player.seen_lines = {"opening:Oracle"}
    _, _, start = start_new_game_plus(player, floors)
    assert player.visited_floors == {"floor_0"}
    assert player.visited_rooms == {start.name}
    assert player.seen_lines == set()

def test_start_new_game_plus_clears_the_story_flags():
    world, floors, player = played_world()
    player.story_flags = {"suitors_cleared", "hades_defeated", "ending_shown", "trophy_room_complete", "prometheus_offer_made"}
    start_new_game_plus(player, floors)
    assert player.story_flags == set()

def test_start_new_game_plus_carries_hardcore_over():
    """Hardcore, and the fact that Prometheus' offer has been made - so he doesn't offer it a second time."""
    world, floors, player = played_world()
    player.story_flags = {"hardcore", "prometheus_offer_made", "suitors_cleared"}
    start_new_game_plus(player, floors)
    assert player.story_flags == {"hardcore", "prometheus_offer_made"}

# ---- carried companions ----

def test_start_new_game_plus_keeps_the_companion_in_the_party():
    world, floors, player = played_world()
    achilles = recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    start_new_game_plus(player, floors)
    assert player.companion is achilles

def test_start_new_game_plus_points_the_party_companions_home_at_the_new_world():
    world, floors, player = played_world()
    achilles = recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    new_world, _, _ = start_new_game_plus(player, floors)
    assert achilles.home_room is room_named(new_world, "Shadow of Army Camp")

def test_start_new_game_plus_removes_a_carried_companions_fresh_copy_from_their_starting_room():
    """The new world is built with its own Shade of Achilles in the camp - with the carried one in the party, nobody is left there."""
    world, floors, player = played_world()
    recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    new_world, _, _ = start_new_game_plus(player, floors)
    assert room_named(new_world, "Shadow of Army Camp").companions == []

def test_start_new_game_plus_puts_a_dismissed_companion_back_in_their_home_room():
    """Recruited, then sent home: the same companion waits in the new world's camp, in place of the fresh copy."""
    world, floors, player = played_world()
    achilles = recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    dismiss_companion(player)
    new_world, _, _ = start_new_game_plus(player, floors)
    camp = room_named(new_world, "Shadow of Army Camp")
    assert camp.companions == [achilles]
    assert achilles.home_room is camp
    assert player.companion is None

def test_start_new_game_plus_carried_companions_keep_their_level_and_won_duel():
    world, floors, player = played_world()
    achilles = recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    achilles.gain_experience(500)
    level, max_hp, attack = achilles.level, achilles.max_hp, achilles.attack_damage
    assert level > 1
    start_new_game_plus(player, floors)
    assert (achilles.level, achilles.max_hp, achilles.attack_damage) == (level, max_hp, attack)
    assert achilles.duel_won is True

def test_start_new_game_plus_restores_and_revives_carried_companions():
    world, floors, player = played_world()
    achilles = recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    achilles.hp = 0
    achilles.apply_status_effect(StatusEffect("Poison", -2, 3))
    start_new_game_plus(player, floors)
    assert achilles.hp == achilles.max_hp
    assert achilles.active_effects == []

def test_start_new_game_plus_carries_every_recruited_companion_not_only_the_current_one():
    world, floors, player = played_world()
    achilles = recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    dismiss_companion(player)
    odysseus = recruit(world, player, "Shadow of Ithaca", "Odysseus")
    new_world, _, _ = start_new_game_plus(player, floors)
    assert player.companion is odysseus
    assert room_named(new_world, "Shadow of Army Camp").companions == [achilles]
    assert room_named(new_world, "Shadow of Ithaca").companions == []

def test_start_new_game_plus_does_not_carry_a_companion_who_was_never_recruited():
    world, floors, player = played_world()
    old_achilles = room_named(world, "Shadow of Army Camp").companions[0]
    old_achilles.duel_won = True
    new_world, _, _ = start_new_game_plus(player, floors)
    new_achilles = room_named(new_world, "Shadow of Army Camp").companions[0]
    assert new_achilles is not old_achilles
    assert new_achilles.duel_won is False

def test_start_new_game_plus_keeps_the_list_of_recruited_companions():
    world, floors, player = played_world()
    recruit(world, player, "Shadow of Army Camp", "Shade of Achilles")
    start_new_game_plus(player, floors)
    assert player.recruited_companions == {"Shade of Achilles"}

def test_start_new_game_plus_a_companion_whose_home_is_not_in_the_new_world_gets_the_start_as_home():
    """A companion spawned somewhere that isn't on any floor (the dev test room) still needs a home to be dismissed to."""
    world, floors, player = played_world()
    elsewhere = room_named(world, "Dev Test Room")
    stray = Companion(name="Stray", hp=10, home_room=elsewhere)
    elsewhere.add_companion(stray)
    recruit_companion("stray", elsewhere, player)
    new_world, _, start = start_new_game_plus(player, floors)
    assert player.companion is stray
    assert stray.home_room is start

# ---- a carried Hades, and Thanatos ----

def test_start_new_game_plus_a_carried_hades_makes_his_home_with_persephone():
    world, floors, player = played_world()
    hades = spare_and_recruit_hades(world, player)
    new_world, _, _ = start_new_game_plus(player, floors)
    assert player.companion is hades
    assert hades.home_room is room_named(new_world, "Bedchamber of Persephone")

def test_start_new_game_plus_a_dismissed_hades_waits_with_persephone():
    world, floors, player = played_world()
    hades = spare_and_recruit_hades(world, player)
    dismiss_companion(player)
    new_world, _, _ = start_new_game_plus(player, floors)
    assert room_named(new_world, "Bedchamber of Persephone").companions == [hades]
    assert room_named(new_world, "Hall of Hades").companions == []

def test_start_new_game_plus_with_hades_carried_thanatos_holds_the_hall():
    world, floors, player = played_world()
    spare_and_recruit_hades(world, player)
    new_world, _, _ = start_new_game_plus(player, floors)
    assert [enemy.name for enemy in room_named(new_world, "Hall of Hades").enemies] == ["Thanatos"]

def test_start_new_game_plus_scales_thanatos_for_the_new_cycle():
    world, floors, player = played_world()
    spare_and_recruit_hades(world, player)
    new_world, _, _ = start_new_game_plus(player, floors)
    thanatos = room_named(new_world, "Hall of Hades").enemies[0]
    assert thanatos.max_hp == round(thanatos.unscaled_max_hp * 1.5)
    assert thanatos.attack_damage == round(thanatos.unscaled_attack * 1.5)

def test_start_new_game_plus_with_hades_carried_counts_the_promise_as_kept():
    """So Persephone's stair opens without her asking again - Hades is standing right there."""
    world, floors, player = played_world()
    spare_and_recruit_hades(world, player)
    start_new_game_plus(player, floors)
    assert player.story_flags == {"promised_mercy", "hades_spared"}

def test_start_new_game_plus_without_hades_leaves_him_on_his_throne():
    world, floors, player = played_world()
    new_world, _, _ = start_new_game_plus(player, floors)
    assert [enemy.name for enemy in room_named(new_world, "Hall of Hades").enemies] == ["Hades"]
    assert "promised_mercy" not in player.story_flags

def test_start_new_game_plus_a_spared_hades_who_was_never_recruited_is_not_carried():
    """He yielded and stayed in his Hall - next cycle he's back on the throne, to be fought again."""
    world, floors, player = played_world()
    player.story_flags.add("promised_mercy")
    hall = room_named(world, "Hall of Hades")
    while hall.enemies:
        enemy = hall.enemies[0]
        enemy.hp = 0
        handle_enemy_defeat(hall, enemy, player)
    assert [companion.name for companion in hall.companions] == ["Hades"]
    new_world, _, _ = start_new_game_plus(player, floors)
    new_hall = room_named(new_world, "Hall of Hades")
    assert [enemy.name for enemy in new_hall.enemies] == ["Hades"]
    assert new_hall.companions == []
    assert player.story_flags == set()

def test_start_new_game_plus_clearing_thanatos_hall_still_sets_hades_defeated():
    """The Hall's own cleared flag is untouched, so Tartarus still opens and the ending still plays."""
    world, floors, player = played_world()
    spare_and_recruit_hades(world, player)
    new_world, _, _ = start_new_game_plus(player, floors)
    hall = room_named(new_world, "Hall of Hades")
    seen = []
    while hall.enemies:
        enemy = hall.enemies[0]
        seen.append(enemy.name)
        enemy.hp = 0
        handle_enemy_defeat(hall, enemy, player)
    assert seen == ["Thanatos", "Hypnos", "Thanatos (Helm of Darkness)"]
    assert "hades_defeated" in player.story_flags
    assert "Helm of Darkness" in [item.name for item in hall.items]

# ---- the new world is ready to play, and to save, straight away ----

def test_start_new_game_plus_marks_the_starting_room_and_floor_as_visited():
    """Regression: both sets were emptied and never given the new start, so 'uncleared' left the first room out and the first move autosaved
    as though floor 0 had just been reached."""
    world, floors, player = played_world()
    new_world, new_floors, start = start_new_game_plus(player, floors)
    assert start.name in player.visited_rooms
    assert start.name in new_floors["floor_0"]
    assert "floor_0" in player.visited_floors

def test_start_new_game_plus_scales_the_new_world_for_the_new_cycle():
    """Regression: main() autosaves straight after this returns. The world used to be scaled only before the *next* command, so that autosave
    held unscaled HP - and loading it left every enemy wounded against its scaled maximum."""
    world, floors, player = played_world()
    new_world, _, _ = start_new_game_plus(player, floors)
    assert new_world.scaled_for == ("normal", 1)
    for room in new_world.rooms.values():
        for enemy in room.enemies:
            if not enemy.respawns:
                assert enemy.max_hp == max(1, round(enemy.unscaled_max_hp * 1.5)), enemy.name
                assert enemy.hp == enemy.max_hp, enemy.name

def test_start_new_game_plus_scales_for_the_difficulty_as_well_as_the_cycle():
    world, floors, player = played_world()
    player.difficulty = "hard"
    new_world, _, _ = start_new_game_plus(player, floors)
    minotaur = room_named(new_world, "Labyrinth of the Minotaur").enemies[0]
    assert minotaur.max_hp == round(minotaur.unscaled_max_hp * 1.3 * 1.5)
    assert minotaur.attack_damage == round(minotaur.unscaled_attack * 1.2 * 1.5)

def test_start_new_game_plus_never_scales_thanatos_twice():
    """He's scaled when he's installed and again with the rest of the world - always from his unscaled stats, so the result is the same."""
    world, floors, player = played_world()
    spare_and_recruit_hades(world, player)
    new_world, _, _ = start_new_game_plus(player, floors)
    thanatos = room_named(new_world, "Hall of Hades").enemies[0]
    assert (thanatos.hp, thanatos.max_hp) == (93, 93)

# ---- carried companions can always rejoin ----

def test_a_carried_companion_waiting_at_home_can_be_recruited_again_without_their_story_flag():
    """Regression: story flags are reset each cycle, so a dismissed Odysseus refused to rejoin until the Suitors were cleared again."""
    world, floors, player = played_world()
    odysseus = recruit(world, player, "Shadow of Ithaca", "Odysseus")
    dismiss_companion(player)
    new_world, _, _ = start_new_game_plus(player, floors)
    assert "suitors_cleared" not in player.story_flags
    message = recruit_companion("odysseus", room_named(new_world, "Shadow of Ithaca"), player)
    assert message == "Odysseus joins you."
    assert player.companion is odysseus

def test_a_companion_never_recruited_still_needs_their_story_flag_in_the_new_cycle():
    world, floors, player = played_world()
    new_world, _, _ = start_new_game_plus(player, floors)
    recruit_companion("odysseus", room_named(new_world, "Shadow of Ithaca"), player)
    assert player.companion is None

# ---- per-companion New Game+ behaviour is data on the companion ----

def test_start_new_game_plus_sends_a_companion_to_their_new_game_plus_home():
    world, floors, player = played_world()
    camp = room_named(world, "Shadow of Army Camp")
    wanderer = Companion(name="Wanderer", hp=10, home_room=camp, new_game_plus_home="Styx Crossing")
    camp.add_companion(wanderer)
    recruit_companion("wanderer", camp, player)
    dismiss_companion(player)
    new_world, _, _ = start_new_game_plus(player, floors)
    assert wanderer in room_named(new_world, "Styx Crossing").companions
    assert wanderer.home_room is room_named(new_world, "Styx Crossing")
    assert wanderer not in room_named(new_world, "Shadow of Army Camp").companions

def test_start_new_game_plus_runs_a_carried_companions_effect_with_the_player_and_the_new_floors():
    world, floors, player = played_world()
    calls = []
    camp = room_named(world, "Shadow of Army Camp")
    herald = Companion(name="Herald", hp=10, home_room=camp, new_game_plus_effect=lambda player, all_floors: calls.append((player, all_floors)))
    camp.add_companion(herald)
    recruit_companion("herald", camp, player)
    new_world, new_floors, _ = start_new_game_plus(player, floors)
    assert len(calls) == 1
    assert calls[0][0] is player
    assert calls[0][1] is new_floors

def test_start_new_game_plus_runs_the_effect_for_a_companion_waiting_at_home_too():
    world, floors, player = played_world()
    calls = []
    camp = room_named(world, "Shadow of Army Camp")
    herald = Companion(name="Herald", hp=10, home_room=camp, new_game_plus_effect=lambda player, all_floors: calls.append("called"))
    camp.add_companion(herald)
    recruit_companion("herald", camp, player)
    dismiss_companion(player)
    start_new_game_plus(player, floors)
    assert calls == ["called"]

def test_start_new_game_plus_does_not_run_the_effect_of_a_companion_who_was_never_recruited():
    world, floors, player = played_world()
    calls = []
    camp = room_named(world, "Shadow of Army Camp")
    camp.add_companion(Companion(name="Herald", hp=10, home_room=camp, new_game_plus_effect=lambda player, all_floors: calls.append("called")))
    start_new_game_plus(player, floors)
    assert calls == []

def test_start_new_game_plus_an_effects_story_flags_survive_the_reset():
    """The effect runs after the flags are cleared - that's how Hades' kept promise lasts into the new cycle."""
    world, floors, player = played_world()
    player.story_flags = {"suitors_cleared"}
    camp = room_named(world, "Shadow of Army Camp")
    herald = Companion(name="Herald", hp=10, home_room=camp, new_game_plus_effect=lambda player, all_floors: player.story_flags.add("heralded"))
    camp.add_companion(herald)
    recruit_companion("herald", camp, player)
    start_new_game_plus(player, floors)
    assert player.story_flags == {"heralded"}

# ---- mastery: what the carried character's spare points are for ----

def test_start_new_game_plus_keeps_mastery_bought_in_the_last_cycle():
    """A character who has learned everything keeps levelling each cycle - mastery is what those points buy, and it carries over like any
    other skill."""
    world, floors, player = played_world()
    path = player.skill_tree.paths["attack"]
    player.skill_tree.skill_points = len(path.skills) + 2
    for _ in range(len(path.skills) + 2):
        player.skill_tree.invest("attack", player)
    attack = player.attack_damage
    start_new_game_plus(player, floors)
    assert path.mastery_count == 2
    assert player.attack_damage == attack
