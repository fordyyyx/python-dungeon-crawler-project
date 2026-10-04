"""Difficulty settings - Story, Easy, Normal, and Hard. Chosen at a new game and fixed for the run (achievements will depend on it). Each scales
enemy HP and attack, and passive regeneration; healing found, gold, and XP are the same on every setting. New Game+ adds a stacking multiplier per
cycle on top. Every enemy is scaled through scale_enemy(), by every route that creates one."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Difficulty:
    """One difficulty setting: its name and one-line description for the new-game prompt, what it multiplies enemy HP and attack by, and how
    passive regeneration behaves - the fraction of max HP that walking restores up to (regen_cap), and the HP restored per move."""

    label: str
    description: str
    hp_multiplier: float
    attack_multiplier: float
    regen_cap: float
    regen_per_move: int

DIFFICULTIES: dict[str, Difficulty] = {
    "story": Difficulty("Story", "for the myths, not the fighting", 0.5, 0.5, 1.0, 2),
    "easy": Difficulty("Easy", "forgiving, but not effortless", 0.75, 0.8, 1.0, 1),
    "normal": Difficulty("Normal", "the game as it was designed", 1.0, 1.0, 0.75, 1),
    "hard": Difficulty("Hard", "for those who know what's coming", 1.3, 1.2, 0.5, 1),
}

DEFAULT_DIFFICULTY = "normal"
NG_PLUS_MULTIPLIER_PER_CYCLE = 0.25
"""Each New Game+ cycle adds this much to enemy HP and attack, stacking - on top of the setting's own multipliers."""

def get_difficulty(key: str) -> Difficulty:
    """The setting for a DIFFICULTIES key. An unknown key raises KeyError - in a save file, that's a damaged save."""
    return DIFFICULTIES[key]

def enemy_multipliers(difficulty: str, cycle: int) -> tuple[float, float]:
    """(HP multiplier, attack multiplier) for a setting at a given New Game+ cycle."""
    setting = get_difficulty(difficulty)
    cycle_bonus = 1 + NG_PLUS_MULTIPLIER_PER_CYCLE * cycle
    return setting.hp_multiplier * cycle_bonus, setting.attack_multiplier * cycle_bonus

def scale_enemy(enemy, difficulty: str, cycle: int, keep_hp: bool = False) -> None:
    """Set enemy's max HP and attack for this setting and cycle, always from its *unscaled* values - so scaling twice gives the same result as
    scaling once, and rescaling to a new setting never compounds. By default, current HP keeps the same share of max HP (a full-health enemy stays
    full; a half-health one stays at half), and a living enemy never drops to 0. keep_hp keeps current HP exactly instead, capped at the new
    maximum - for loading a save, where HP was saved already scaled. Respawning enemies are never scaled: the Practice Chamber's dummy is the
    player's own sandbox, set with 'dummy set'."""
    if enemy.respawns:
        return
    hp_multiplier, attack_multiplier = enemy_multipliers(difficulty, cycle)
    share = enemy.hp / enemy.max_hp if enemy.max_hp else 1.0
    enemy.max_hp = max(1, round(enemy.unscaled_max_hp * hp_multiplier))
    enemy.attack_damage = round(enemy.unscaled_attack * attack_multiplier)
    if keep_hp:
        enemy.hp = min(enemy.hp, enemy.max_hp)
    elif enemy.hp > 0:
        enemy.hp = max(1, round(share * enemy.max_hp))

def scale_rooms(rooms, difficulty: str, cycle: int, keep_hp: bool = False) -> None:
    """Scale every enemy in every one of rooms."""
    for room in rooms:
        for enemy in room.enemies:
            scale_enemy(enemy, difficulty, cycle, keep_hp)

def scale_for(enemy, player) -> None:
    """Scale a single newly created enemy for the player's run - the call every mid-game route uses."""
    scale_enemy(enemy, player.difficulty, player.ng_plus_cycle)

def scale_world(world, difficulty: str, cycle: int, keep_hp: bool = False) -> None:
    """Scale every enemy in the world, and record the setting it was scaled for - see ensure_world_scaled()."""
    scale_rooms(world.rooms.values(), difficulty, cycle, keep_hp)
    world.scaled_for = (difficulty, cycle)

def ensure_world_scaled(world, player) -> None:
    """Rescale the world if the player's setting or New Game+ cycle has changed since it was last scaled - each enemy keeps its share of its HP.
    Called once per command by main(), so any change - Prometheus raising a run to Hard, 'dev difficulty', New Game+ - applies straight away,
    without whatever made the change needing access to the world."""
    if getattr(world, "scaled_for", None) != (player.difficulty, player.ng_plus_cycle):
        scale_world(world, player.difficulty, player.ng_plus_cycle)