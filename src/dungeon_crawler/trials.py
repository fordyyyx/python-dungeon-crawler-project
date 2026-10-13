"""Trials - a series of contests fought in one room, each harder than the last, each with a prize the first time it's won. A trial's progress
lives in the room's transient_state, so leaving the room ends it. However it ends - won, lost or walked away from - the player is put back as
they entered (see PlayerSnapshot), keeping only the prizes; losing is never a real death. Contestants give no XP, gold or loot, so a trial
can't be farmed. The player fights alone - a companion sits out. The Funeral Games of Patroclus (floor 5) are the first."""

from dataclasses import dataclass
from typing import Callable

from dungeon_crawler.difficulty import scale_for, get_difficulty
from dungeon_crawler.characters import PlayerSnapshot

TRIAL_STATE = "trial"

@dataclass
class Contest:
    """One round: its title, its opponents (enemy factories), and the host's announcement. prize(player, room), if set, gives this round's
    prize and returns its message - once only, recorded with prize_flag in the room's flags, which are saved."""

    title: str
    opponents: list[Callable]
    announcement: str
    prize: Callable | None = None
    prize_flag: str = ""

@dataclass
class Trial:
    """A whole trial. host_line(player, room) introduces each contest - so it can depend on where the host is. victory_text follows the last
    contest's prize; repeat_victory_text is shown instead when that prize has already been won. Between contests the player recovers
    rest_fraction of their max HP, never past the difficulty's regen cap."""

    contests: list[Contest]
    host_line: Callable
    victory_text: str
    repeat_victory_text: str
    defeat_text: str
    rest_fraction: float = 0.25

def trial_active(room) -> bool:
    """Whether a trial is underway in room - during a contest, or waiting between two."""
    return TRIAL_STATE in room.transient_state

def companion_sits_out(room) -> bool:
    """Whether the player's companion is kept out of combat here - true for the whole of a trial."""
    return trial_active(room)

def awaiting_next_contest(room) -> bool:
    """Whether a trial here has finished a contest and is waiting for the player to call the next one."""
    state = room.transient_state.get(TRIAL_STATE)
    return state is not None and state["awaiting_next"]

def _contestants(room) -> list:
    """The trial's own opponents still in room."""
    return [enemy for enemy in room.enemies if enemy.trial_contestant]

def _spawn_contest(state, room, player) -> str:
    """Bring out the current round's opponents - scaled for the run, like any enemy - and start the fight."""
    trial, index = state["trial"], state["round"]
    contest = trial.contests[index]
    opponents = []
    for factory in contest.opponents:
        opponent = factory()
        opponent.trial_contestant = True
        scale_for(opponent, player)
        room.add_enemy(opponent)
        opponents.append(opponent)
    state["awaiting_next"] = False
    player.in_combat = True
    player.current_target = opponents[0]
    return f"{trial.host_line(player, room)} {contest.announcement}\n(Contest {index + 1} of {len(trial.contests)}: {contest.title})"

def _end_trial(room, player) -> None:
    """Remove any contestants still standing, forget the trial's progress, and put the player back as they entered."""
    state = room.transient_state.pop(TRIAL_STATE, None)
    for opponent in _contestants(room):
        room.remove_enemy(opponent)
    if state is not None:
        state["snapshot"].restore(player, room)
    player.in_combat = False
    player.current_target = None

def start_trial(trial, player, room) -> str:
    """Begin a trial at its first contest, taking a PlayerSnapshot so the player can be put back as they entered when it ends."""
    if trial_active(room):
        return "The contest is already underway."
    state = {"trial": trial, "round": 0, "snapshot": PlayerSnapshot.take(player), "awaiting_next": False}
    room.transient_state[TRIAL_STATE] = state
    return _spawn_contest(state, room, player)

def next_contest(player, room) -> str:
    """Begin the next contest, once the player is ready."""
    state = room.transient_state.get(TRIAL_STATE)
    if state is None or not state["awaiting_next"]:
        return "There's no contest waiting to begin."
    state["round"] += 1
    return _spawn_contest(state, room, player)

def check_trial_progress(room, player) -> str:
    """Called after every defeat. When the last contestant of a round falls, the round's prize is given if it hasn't been before. Then, between
    rounds, the player recovers rest_fraction of their max HP (up to the difficulty's regen cap) and the trial waits for 'next contest'; after
    the final round, the trial ends."""
    state = room.transient_state.get(TRIAL_STATE)
    if state is None or state["awaiting_next"] or any(opponent.is_alive() for opponent in _contestants(room)):
        return ""
    trial = state["trial"]
    contest = trial.contests[state["round"]]
    lines = []
    if contest.prize is not None and contest.prize_flag not in room.flags:
        room.flags.add(contest.prize_flag)
        lines.append(contest.prize(player, room))

    if state["round"] + 1 >= len(trial.contests):
        _end_trial(room, player)
        lines.append(trial.victory_text if lines else trial.repeat_victory_text)
        return "\n".join(lines)
    
    cap = int(player.max_hp * get_difficulty(player.difficulty).regen_cap)
    healed = max(0, min(round(player.max_hp * trial.rest_fraction), cap - player.hp))
    player.hp += healed
    state["awaiting_next"] = True
    lines.append(f"The contest is yours. You catch your breath. (+{healed} HP. Say 'next contest' when you're ready.)")
    return "\n".join(lines)

def protect_trial_loser(player, room) -> str:
    """If the player has fallen during a trial, pull them out instead of letting them die: put back as they entered, effects cleared, the
    trial ended and its contestants gone. A failed attempt, never a real death - in hardcore too."""
    state = room.transient_state.get(TRIAL_STATE)
    if state is None or player.hp > 0:
        return ""
    player.active_effects = []
    player.in_combat = False
    player.current_target = None
    defeat_text = state["trial"].defeat_text
    _end_trial(room, player)
    return defeat_text

def forfeit_trial(room, player) -> str:
    """End a trial the player has walked away from - by fleeing, or by leaving the room - putting them back as they entered."""
    if not trial_active(room):
        return ""
    _end_trial(room, player)
    return "You've left the field. The contest is forfeit."