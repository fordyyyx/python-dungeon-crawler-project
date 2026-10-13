from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room
from dungeon_crawler.items import Armour, Consumable, IntellectReward
from dungeon_crawler.status_effects import StatusEffect
from dungeon_crawler.combat import handle_enemy_defeat, handle_combat_command
from dungeon_crawler.trials import (
    TRIAL_STATE, Contest, Trial, trial_active, companion_sits_out, awaiting_next_contest,
    start_trial, next_contest, check_trial_progress, protect_trial_loser, forfeit_trial,
)

def create_runner() -> Enemy:
    return Enemy(name="Runner", hp=10, attack_damage=4)

def create_boxer() -> Enemy:
    return Enemy(name="Boxer", hp=20, attack_damage=6)

def create_archer() -> Enemy:
    return Enemy(name="Archer", hp=8, attack_damage=5)

def shield_prize(player, room) -> str:
    room.add_item(Armour(name="Laurel Shield", description="", defence=3, slot="shield"))
    return "A shield is set at your feet."

def purse_prize(player, room) -> str:
    player.gold += 50
    return "You're thrown a purse. (+50 gold)"

def make_trial(host_calls=None, purse_for_the_race=False) -> Trial:
    """A three-contest trial: one opponent, then one, then a pair, with a shield for winning the last. host_calls, if given, records what
    the host line was called with. purse_for_the_race gives the first contest a prize of its own."""
    def host(player, room):
        if host_calls is not None:
            host_calls.append((player, room))
        return "The host raises a hand."
    race = Contest("The race", [create_runner], "\"Run.\"")
    if purse_for_the_race:
        race = Contest("The race", [create_runner], "\"Run.\"", purse_prize, "games_won:race")
    return Trial(
        contests=[
            race,
            Contest("Boxing", [create_boxer], "\"Fight.\""),
            Contest("Archery", [create_archer, create_archer], "\"Shoot.\"", shield_prize, "games_won"),
        ],
        host_line=host,
        victory_text="You've won the Games.",
        repeat_victory_text="You've won them again.",
        defeat_text="You're carried off the field.",
    )

def started(hp=20, max_hp=20, difficulty="normal", purse_for_the_race=False):
    """A room with a trial just begun, and the player in it."""
    room = Room("Field")
    player = Player(name="Hero", hp=max_hp)
    player.hp = hp
    player.difficulty = difficulty
    trial = make_trial(purse_for_the_race=purse_for_the_race)
    start_trial(trial, player, room)
    return trial, player, room

def beat_the_round(room, player) -> str:
    """Defeat everyone standing, the way combat does - returns the last defeat's message."""
    message = ""
    for opponent in list(room.enemies):
        opponent.hp = 0
        message = handle_enemy_defeat(room, opponent, player)
    return message

def win_the_trial(room, player) -> str:
    """From a trial's first contest to its last."""
    message = beat_the_round(room, player)
    while awaiting_next_contest(room):
        next_contest(player, room)
        message = beat_the_round(room, player)
    return message

# ---- the dataclasses ----

def test_trial_rests_the_player_a_quarter_of_their_health_between_contests_by_default():
    assert make_trial().rest_fraction == 0.25

def test_contest_holds_its_title_opponents_and_announcement():
    contest = Contest("The race", [create_runner], "\"Run.\"")
    assert (contest.title, contest.opponents, contest.announcement) == ("The race", [create_runner], "\"Run.\"")

def test_contest_has_no_prize_by_default():
    contest = Contest("The race", [create_runner], "\"Run.\"")
    assert contest.prize is None
    assert contest.prize_flag == ""

def test_contest_holds_its_prize_and_the_flag_that_records_it():
    contest = Contest("The race", [create_runner], "\"Run.\"", purse_prize, "games_won:race")
    assert contest.prize is purse_prize
    assert contest.prize_flag == "games_won:race"

# ---- state ----

def test_a_room_with_no_trial_is_not_in_one():
    room = Room("Field")
    assert trial_active(room) is False
    assert awaiting_next_contest(room) is False
    assert companion_sits_out(room) is False

def test_trial_active_once_started():
    trial, player, room = started()
    assert trial_active(room) is True

def test_a_companion_sits_out_for_the_whole_of_a_trial():
    """During a contest and between contests alike."""
    trial, player, room = started()
    assert companion_sits_out(room) is True
    beat_the_round(room, player)
    assert companion_sits_out(room) is True

def test_a_trial_lives_in_the_rooms_transient_state():
    """So leaving the room ends it, and it's never saved."""
    trial, player, room = started()
    assert TRIAL_STATE in room.transient_state
    assert room.flags == set()

# ---- start_trial ----

def test_start_trial_brings_out_the_first_contests_opponents():
    trial, player, room = started()
    assert [enemy.name for enemy in room.enemies] == ["Runner"]
    assert room.enemies[0].trial_contestant is True

def test_start_trial_puts_the_player_into_combat_with_the_first_opponent():
    trial, player, room = started()
    assert player.in_combat is True
    assert player.current_target is room.enemies[0]

def test_start_trial_announces_the_contest():
    room = Room("Field")
    message = start_trial(make_trial(), Player(name="Hero", hp=20), room)
    assert message == "The host raises a hand. \"Run.\"\n(Contest 1 of 3: The race)"

def test_start_trial_gives_the_host_line_the_player_and_the_room():
    """Regression: the host line was called with the player alone, while the real one (Achilles) also takes the room - so starting the
    Funeral Games crashed the game."""
    calls = []
    room = Room("Field")
    player = Player(name="Hero", hp=20)
    start_trial(make_trial(calls), player, room)
    assert len(calls) == 1
    assert calls[0][0] is player
    assert calls[0][1] is room

def test_start_trial_scales_the_opponents_for_the_players_difficulty():
    room = Room("Field")
    player = Player(name="Hero", hp=20)
    player.difficulty = "hard"
    start_trial(make_trial(), player, room)
    runner = room.enemies[0]
    assert (runner.hp, runner.max_hp, runner.attack_damage) == (13, 13, 5)

def test_start_trial_builds_fresh_opponents_every_time():
    first_room, second_room = Room("Field"), Room("Field")
    trial = make_trial()
    start_trial(trial, Player(name="Hero", hp=20), first_room)
    start_trial(trial, Player(name="Hero", hp=20), second_room)
    assert first_room.enemies[0] is not second_room.enemies[0]

def test_start_trial_while_one_is_underway_changes_nothing():
    trial, player, room = started()
    message = start_trial(trial, player, room)
    assert message == "The contest is already underway."
    assert len(room.enemies) == 1

# ---- winning a contest ----

def test_winning_a_contest_waits_for_the_player_to_call_the_next():
    trial, player, room = started()
    beat_the_round(room, player)
    assert awaiting_next_contest(room) is True
    assert room.enemies == []
    assert trial_active(room) is True

def test_winning_a_contest_rests_the_player_a_quarter_of_their_max_hp():
    trial, player, room = started(hp=8, max_hp=20)
    message = beat_the_round(room, player)
    assert player.hp == 13
    assert message.endswith("The contest is yours. You catch your breath. (+5 HP. Say 'next contest' when you're ready.)")

def test_the_rest_between_contests_stops_at_the_regen_cap():
    """Regression for the balance check's finding: the rest ignored the setting's regen cap, so winning one contest and walking out, over and
    over, healed to full for free. On Normal the cap is three quarters - 15 of 20."""
    trial, player, room = started(hp=13, max_hp=20)
    message = beat_the_round(room, player)
    assert player.hp == 15
    assert "(+2 HP." in message

def test_the_rest_between_contests_heals_nothing_above_the_regen_cap():
    trial, player, room = started(hp=18, max_hp=20)
    message = beat_the_round(room, player)
    assert player.hp == 18
    assert "(+0 HP." in message

def test_the_rest_between_contests_reaches_full_on_a_setting_that_regenerates_to_full():
    trial, player, room = started(hp=18, max_hp=20, difficulty="story")
    beat_the_round(room, player)
    assert player.hp == 20

def test_the_rest_between_contests_stops_at_half_on_hard():
    trial, player, room = started(hp=8, max_hp=20, difficulty="hard")
    beat_the_round(room, player)
    assert player.hp == 10

def test_check_trial_progress_only_rests_the_player_once_per_contest():
    trial, player, room = started(hp=8, max_hp=20)
    beat_the_round(room, player)
    assert check_trial_progress(room, player) == ""
    assert player.hp == 13

def test_check_trial_progress_does_nothing_while_an_opponent_still_stands():
    trial, player, room = started(hp=8, max_hp=20)
    assert check_trial_progress(room, player) == ""
    assert player.hp == 8
    assert awaiting_next_contest(room) is False

def test_check_trial_progress_with_no_trial_does_nothing():
    assert check_trial_progress(Room("Field"), Player(name="Hero", hp=20)) == ""

def test_contestants_give_no_experience_gold_or_loot():
    """So a trial can't be farmed - it can be entered as often as the player likes."""
    trial, player, room = started()
    win_the_trial(room, player)
    assert (player.experience, player.gold, player.level) == (0, 0, 1)

# ---- next_contest ----

def test_next_contest_brings_out_the_following_round():
    trial, player, room = started()
    beat_the_round(room, player)
    message = next_contest(player, room)
    assert [enemy.name for enemy in room.enemies] == ["Boxer"]
    assert message == "The host raises a hand. \"Fight.\"\n(Contest 2 of 3: Boxing)"
    assert player.in_combat is True
    assert awaiting_next_contest(room) is False

def test_next_contest_with_nothing_waiting_changes_nothing():
    """Mid-contest, or with no trial at all."""
    trial, player, room = started()
    assert next_contest(player, room) == "There's no contest waiting to begin."
    assert [enemy.name for enemy in room.enemies] == ["Runner"]
    assert next_contest(player, Room("Elsewhere")) == "There's no contest waiting to begin."

def test_a_contest_with_two_opponents_is_only_won_when_both_have_fallen():
    trial, player, room = started()
    beat_the_round(room, player)
    next_contest(player, room)
    beat_the_round(room, player)
    next_contest(player, room)
    first, second = room.enemies
    first.hp = 0
    handle_enemy_defeat(room, first, player)
    assert trial_active(room) is True
    assert room.flags == set()
    second.hp = 0
    handle_enemy_defeat(room, second, player)
    assert trial_active(room) is False

# ---- winning the trial ----

def test_winning_the_last_contest_ends_the_trial():
    trial, player, room = started()
    win_the_trial(room, player)
    assert trial_active(room) is False
    assert room.enemies == []

def test_winning_the_trial_for_the_first_time_leaves_the_prize_in_the_room():
    trial, player, room = started()
    message = win_the_trial(room, player)
    assert [item.name for item in room.items] == ["Laurel Shield"]
    assert "games_won" in room.flags
    assert message.endswith("A shield is set at your feet.\nYou've won the Games.")

def test_winning_the_trial_again_gives_no_second_prize():
    trial, player, room = started()
    win_the_trial(room, player)
    start_trial(trial, player, room)
    message = win_the_trial(room, player)
    assert [item.name for item in room.items] == ["Laurel Shield"]
    assert message.endswith("You've won them again.")

def test_winning_the_trial_returns_the_player_to_the_hp_they_entered_with():
    """The rests are for the contests still to come - once the trial is over, win or lose, the player is as they walked in."""
    trial, player, room = started(hp=8, max_hp=20)
    beat_the_round(room, player)
    next_contest(player, room)
    assert player.hp == 13
    win_the_trial(room, player)
    assert player.hp == 8

def test_winning_the_trial_releases_the_player_from_combat():
    trial, player, room = started()
    win_the_trial(room, player)
    assert player.in_combat is False
    assert player.current_target is None

# ---- a prize for a single contest ----

def test_winning_a_contest_with_a_prize_gives_it_at_once():
    trial, player, room = started(hp=8, max_hp=20, purse_for_the_race=True)
    message = beat_the_round(room, player)
    assert player.gold == 50
    assert "games_won:race" in room.flags
    assert message.endswith(
        "You're thrown a purse. (+50 gold)\nThe contest is yours. You catch your breath. (+5 HP. Say 'next contest' when you're ready.)"
    )

def test_a_contest_with_no_prize_records_nothing():
    trial, player, room = started()
    beat_the_round(room, player)
    assert room.flags == set()

def test_a_contests_prize_is_only_given_the_first_time_it_is_won():
    trial, player, room = started(purse_for_the_race=True)
    beat_the_round(room, player)
    forfeit_trial(room, player)
    start_trial(trial, player, room)
    message = beat_the_round(room, player)
    assert player.gold == 50
    assert "purse" not in message

def test_a_contests_prize_is_kept_when_a_later_contest_is_lost():
    trial, player, room = started(purse_for_the_race=True)
    beat_the_round(room, player)
    next_contest(player, room)
    player.hp = 0
    protect_trial_loser(player, room)
    assert player.gold == 50
    assert "games_won:race" in room.flags

def test_each_contests_prize_is_recorded_under_its_own_flag():
    trial, player, room = started(purse_for_the_race=True)
    win_the_trial(room, player)
    assert room.flags == {"games_won:race", "games_won"}

def test_the_last_prize_can_still_be_won_after_an_earlier_one():
    """Losing at the last contest, then coming back: the purse isn't paid again, and the shield still is."""
    trial, player, room = started(purse_for_the_race=True)
    beat_the_round(room, player)
    forfeit_trial(room, player)
    start_trial(trial, player, room)
    message = win_the_trial(room, player)
    assert player.gold == 50
    assert [item.name for item in room.items] == ["Laurel Shield"]
    assert message.endswith("You've won the Games.")

# ---- losing ----

def test_protect_trial_loser_pulls_a_fallen_player_out_at_the_hp_they_entered_with():
    trial, player, room = started(hp=14, max_hp=20)
    player.hp = 0
    message = protect_trial_loser(player, room)
    assert player.hp == 14
    assert player.is_alive()
    assert message == "You're carried off the field."

def test_protect_trial_loser_ends_the_trial_and_clears_the_field():
    trial, player, room = started()
    player.hp = 0
    protect_trial_loser(player, room)
    assert trial_active(room) is False
    assert room.enemies == []
    assert player.in_combat is False
    assert player.current_target is None

def test_protect_trial_loser_clears_the_players_effects():
    trial, player, room = started()
    player.apply_status_effect(StatusEffect("Poison", -3, 3))
    player.hp = 0
    protect_trial_loser(player, room)
    assert player.active_effects == []

def test_protect_trial_loser_never_returns_the_player_at_zero():
    """They entered alive, however barely."""
    room = Room("Field")
    player = Player(name="Hero", hp=20)
    start_trial(make_trial(), player, room)
    room.transient_state[TRIAL_STATE]["snapshot"].hp = 0
    player.hp = 0
    protect_trial_loser(player, room)
    assert player.hp == 1

def test_protect_trial_loser_returns_to_the_hp_at_the_start_of_the_trial_not_the_contest():
    """Rests along the way don't count - a loss in the third contest goes back to the HP at the very start."""
    trial, player, room = started(hp=6, max_hp=20)
    beat_the_round(room, player)
    next_contest(player, room)
    assert player.hp == 11
    player.hp = 0
    protect_trial_loser(player, room)
    assert player.hp == 6

def test_protect_trial_loser_leaves_a_living_player_alone():
    trial, player, room = started(hp=3, max_hp=20)
    assert protect_trial_loser(player, room) == ""
    assert trial_active(room) is True
    assert player.hp == 3

def test_protect_trial_loser_with_no_trial_does_not_save_the_player():
    """Outside a trial a death is a death."""
    player = Player(name="Hero", hp=20)
    player.hp = 0
    assert protect_trial_loser(player, Room("Field")) == ""
    assert player.hp == 0

def test_a_lost_trial_gives_no_prize():
    trial, player, room = started()
    player.hp = 0
    protect_trial_loser(player, room)
    assert room.items == []
    assert room.flags == set()

# ---- walking away ----

def test_forfeit_trial_ends_it_and_sends_the_opponents_away():
    trial, player, room = started()
    message = forfeit_trial(room, player)
    assert message == "You've left the field. The contest is forfeit."
    assert trial_active(room) is False
    assert room.enemies == []

def test_forfeit_trial_with_no_trial_says_nothing():
    assert forfeit_trial(Room("Field"), Player(name="Hero", hp=20)) == ""

def test_forfeit_trial_only_removes_the_trials_own_opponents():
    trial, player, room = started()
    bystander = Enemy(name="Bystander", hp=10)
    room.add_enemy(bystander)
    forfeit_trial(room, player)
    assert room.enemies == [bystander]

def test_a_trial_can_be_entered_again_after_a_forfeit():
    trial, player, room = started()
    forfeit_trial(room, player)
    start_trial(trial, player, room)
    assert [enemy.name for enemy in room.enemies] == ["Runner"]
    assert "(Contest 1 of 3" in start_trial(trial, player, Room("Other Field"))

def test_forfeit_trial_returns_the_player_to_the_hp_they_entered_with():
    """Regression for the balance check's finding: walking out after a rest kept the HP, so the Games doubled as a free heal."""
    trial, player, room = started(hp=8, max_hp=20)
    beat_the_round(room, player)
    assert player.hp == 13
    forfeit_trial(room, player)
    assert player.hp == 8

def test_forfeit_trial_releases_the_player_from_combat():
    trial, player, room = started()
    forfeit_trial(room, player)
    assert player.in_combat is False
    assert player.current_target is None

# ---- a trial puts back everything it cost, however it ends ----

def _started_with_gear():
    """A trial begun by a player carrying a potion and wearing a shield - returns (trial, player, room, potion, shield)."""
    room = Room("Field")
    player = Player(name="Hero", hp=20)
    potion = Consumable(name="Potion", description="", heal_amount=5)
    shield = Armour(name="Shield", description="", defence=2, slot="shield", max_durability=10)
    player.inventory.add(potion)
    player.inventory.add(shield)
    player.inventory.use_item("shield", player)
    trial = make_trial()
    start_trial(trial, player, room)
    return trial, player, room, potion, shield

def test_a_lost_trial_returns_the_potions_drunk_and_the_armour_worn_down():
    """Regression for the balance check's finding: a failed attempt restored HP but kept the potions and durability it had used - on Hard that
    was about five healing items and thirty durability points a try."""
    trial, player, room, potion, shield = _started_with_gear()
    player.inventory.remove(potion)
    shield.durability = 0
    player.hp = 0
    protect_trial_loser(player, room)
    assert potion in player.inventory.items
    assert shield.durability == 10
    assert player.armour == 2

def test_a_forfeited_trial_returns_what_it_cost_too():
    trial, player, room, potion, shield = _started_with_gear()
    player.inventory.remove(potion)
    shield.durability = 4
    forfeit_trial(room, player)
    assert potion in player.inventory.items
    assert shield.durability == 10

def test_a_won_trial_returns_what_it_cost_too():
    trial, player, room, potion, shield = _started_with_gear()
    player.inventory.remove(potion)
    shield.durability = 4
    win_the_trial(room, player)
    assert potion in player.inventory.items
    assert shield.durability == 10

def test_a_trial_restores_mana_spent_during_it():
    trial, player, room, _, _ = _started_with_gear()
    player.mana = 3
    forfeit_trial(room, player)
    assert player.mana == 20

def test_a_won_trial_keeps_its_prizes_through_the_restore():
    trial, player, room = started(hp=8, max_hp=20, purse_for_the_race=True)
    win_the_trial(room, player)
    assert player.gold == 50
    assert [item.name for item in room.items] == ["Laurel Shield"]

def test_a_trial_cannot_be_used_to_farm_an_intellect_item(monkeypatch):
    """Regression: the snapshot returned every item used during a trial - including one whose effect is permanent. Reading the Ledger in the
    first contest and walking away gave the intellect *and* the Ledger back, and a trial can be entered as often as the player likes.
    Either is fine; both is not."""
    monkeypatch.setattr("random.random", lambda: 0.99)
    room = Room("Field")
    player = Player(name="Hero", hp=20)
    ledger = IntellectReward(name="Ledger", description="", amount=2)
    player.inventory.add(ledger)
    start_trial(make_trial(), player, room)
    before = player.intellect
    handle_combat_command("use ledger", player, player.current_target, [player], room.enemies, room)
    forfeit_trial(room, player)
    kept_the_intellect = player.intellect > before
    kept_the_ledger = ledger in player.inventory.items
    assert not (kept_the_intellect and kept_the_ledger)
