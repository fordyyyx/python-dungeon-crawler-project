"""Combat resolution - turn-by-turn attacks, defeat handling, and fleeing. The one place that resolves what happens when the player's team
and an enemy team trade blows, and the aftermath (loot, XP, gold, or a boss phase transition) when an enemy is defeated.

Team representation: no dedicated Team class (see CLAUDE.md's "No Team class" rule) - player_team and enemy_team are both
plain lists (list[Character] / list[Enemy]). player_team comes from Player.team - [player], or [player, companion] once a Companion
is recruited and alive."""

import random

from dungeon_crawler.characters import Character, Player, Enemy, Companion
from dungeon_crawler.world import Room
from typing import Sequence

def get_enemy_display_name(enemy: Enemy, enemy_team: list[Enemy]) -> str:
    """The name to show for enemy in displays - appends a stable (n) index only when enemy_team has more than one enemy sharing this name, so
    uniquely-named enemies display exactly as before. The index is based on the enemy's position among the same-named enemies within 
    enemy_team (including defeated ones, so a survivor's number never shifts when a teammate dies) - callers should always pass the full
    team, not a filtered list."""
    same_named = [e for e in enemy_team if e.name == enemy.name]
    if len(same_named) <= 1:
        return enemy.name
    index = same_named.index(enemy) + 1
    return f"{enemy.name} ({index})"

def format_hp_line(player_team: list[Character], enemy_team: list[Enemy]) -> str:
    """HP status line for every currently living combatant on both sides - never rebuild this string elsewhere, see CLAUDE.md
    for why this exists as its own function. Defeated combatants are omitted; their defeat is already reported separately by 
    handle_enemy_defeat()/on_death()."""
    living_player_team = [character for character in player_team if character.is_alive()]
    living_enemy_team = [character for character in enemy_team if character.is_alive()]
    player_parts = [f"{character.name}: {character.hp}/{character.max_hp} HP" for character in living_player_team]
    enemy_parts = [f"{get_enemy_display_name(enemy, enemy_team)}: {enemy.hp}/{enemy.max_hp} HP" for enemy in living_enemy_team]
    return "   |   ".join(player_parts + enemy_parts)

def _candidate_attack_score(attacker: Character, candidate: Character) -> float:
    """Base (pre-randomness) attractiveness of attacker attacking candidate specifically - kill_potential + (1 - candidate's own hp_ratio).
    Shared by _best_attack_score() (a deterministic max, judging whether attacking is worthwhile at all) and choose_enemy_target()
    (the same formula per candidate, with independent noise added, used to actually pick who gets hit). attacker is typed generically
    (not Enemy) since Companion's own AI will reuse this exact formula once built."""
    target_hp_ratio = candidate.hp / candidate.max_hp
    potential_damage = max(0, attacker.attack_damage - candidate.armour)
    kill_potential = min(1.0, potential_damage / candidate.hp) if candidate.hp > 0 else 0.0
    return kill_potential + (1 - target_hp_ratio)

def _best_attack_score(attacker: Character, player_team: Sequence[Character]) -> float:
    """The best-case attack score available against any living member of player_team (deterministic, no randomness) - used only to
    judge whether attacking is worthwhile at all; see choose_enemy_target() for the separate, independently-noisy choice of who
    specifically gets hit. Filters to is_alive() first - player_team can go stale mid round if a companion is downed ny an earlier
    enemy's turn, and a dead candidate must never be scored as attack worthy."""
    living_team = [c for c in player_team if c.is_alive()]
    if not living_team:
        return 0.0
    return max(_candidate_attack_score(attacker, candidate) for candidate in living_team)

def _greatest_threat_to_self(self_character: Character, opposing_team: Sequence[Character]) -> float:
    """The highest self_kill_potential posed by any living member of opposing_team against self_character - used to judge how urgently 'defend' is needed.
    min(1.0, max(0, threat.attack_damage - enemy_armour) / enemy.hp) per candidate, maximised across the team (deterministic - defend
    reacts to the worst-case threat, not a specific target, since defending doesn't target back). Shared by both Enemy's and Companion's scoring -
    genuinely symmetric, unlike the action-choosing functions themselves, which stay separate per CLAUDE.md's decision."""
    living_team = [c for c in opposing_team if c.is_alive()]
    if not living_team or self_character.hp == 0:
        return 0.0
    return max(min(1.0, max(0, threat.attack_damage - self_character.armour) / self_character.hp) for threat in living_team)

def choose_enemy_target(enemy: Enemy, player_team: list[Character]) -> Character:
    """Pick which member of player_team enemy should attack. With only one living candidate, returns it directly with no scoring/randomness
    involved - preserves single-target behaviour and random.random() call counts exactly for every enemy fought without a companion present. 
    With two or more, scores each using _candidate_attack_score() plus the same random noise treatment as action selection, so targeting
    isn't always optimal either."""
    living_team = [c for c in player_team if c.is_alive()]
    if len(living_team) == 1:
        return living_team[0]

    noisy_scores = {
        candidate: _candidate_attack_score(enemy, candidate) + (random.random() - 0.5) * enemy.randomness_weight
        for candidate in living_team
    }
    return max(noisy_scores, key=lambda candidate: noisy_scores[candidate])

def _score_candidate_actions(enemy: Enemy, player_team: list[Character]) -> dict[str, float]:
    """Base (pre-randomness) utility score for every action enemy could currently take. 'attack' is scored against the single best
    available target in player_team (see _best_attack_score()) - not necessarily who ends up actually attacked, since choose_enemy_target()
    makes that choice independently once 'attack' has already won. 'defend' reacts to the greatest threat posed by any member of player_team
    (see _greatest_threat_to_self()), and is excluded when brace_amount == 0 (a no-op brace, mirrors heal's exclusion pattern below).
    'heal' only joins when eenmy.heal_amount > 0 - both are excluded entirely rather than scored at zero, per CLAUDE.md's "Enemy AI
    and team combat" section."""
    self_missing_hp_ratio = 1 - (enemy.hp / enemy.max_hp)

    scores = {
        "attack": enemy.aggression_weight * _best_attack_score(enemy, player_team),
    }

    if enemy.brace_amount > 0:
        scores["defend"] = enemy.caution_weight * _greatest_threat_to_self(enemy, player_team)

    if enemy.heal_amount > 0:
        heal_value_ratio = min(1.0, enemy.heal_amount / enemy.max_hp)
        scores["heal"] = enemy.caution_weight * self_missing_hp_ratio * heal_value_ratio

    return scores

def _score_companion_candidate_actions(companion: Companion, enemy_team: list[Enemy]) -> dict[str, float]:
    """Companion's mirror of _score_candidate_actions() - same shape and formulas (see CLAUDE.md's "Enemy AI and team combat"), 
    scored against enemy_team instead of player_team. Kept as a separate, mirrored function rather than a shared one (per that
    same decision) even though the underlying per-candidate math (_best_attack_score(), _greatest_threat_to_self()) is fully reused."""
    self_missing_hp_ratio = 1 - (companion.hp / companion.max_hp)

    scores = {
        "attack": companion.aggression_weight * _best_attack_score(companion, enemy_team),
    }

    if companion.brace_amount > 0:
        scores["defend"] = companion.caution_weight * _greatest_threat_to_self(companion, enemy_team)

    if companion.heal_amount > 0:
        heal_value_ratio = min(1.0, companion.heal_amount / companion.max_hp)
        scores['heal'] = companion.caution_weight * self_missing_hp_ratio * heal_value_ratio

    return scores

def choose_companion_action(companion: Companion, enemy_team: list[Enemy]) -> str:
    """Companion's mirror of choose_enemy_action() - identical scoring/noise treatment, via _score_companion_candidate_actions()."""
    scores = _score_companion_candidate_actions(companion, enemy_team)

    noisy_scores = {
        action: score + (random.random() - 0.5) * companion.randomness_weight
        for action, score in scores.items()
    }

    return max(noisy_scores, key=lambda action: noisy_scores[action])

def choose_companion_target(companion: Companion, enemy_team: list[Enemy]) -> Enemy:
    """Companion's mirror of choose_enemy_target() - identical single-candidate short-circuit and noisy-scoring logic, picking which member
    of enemy_team to attack."""
    living_team = [e for e in enemy_team if e.is_alive()]
    if len(living_team) == 1:
        return living_team[0]

    noisy_scores = {
        candidate: _candidate_attack_score(companion, candidate) + (random.random() - 0.5) * companion.randomness_weight
        for candidate in living_team
    }
    return max(noisy_scores, key=lambda candidate: noisy_scores[candidate])

def choose_enemy_action(enemy: Enemy, player_team: list[Character]) -> str:
    """Decide what enemy does this turn via utility-based scoring: each candidate action from _score_candidate_actions() gets a random
    noise term added (from random.random(), keeping this testable via the existing monkeypatch convention - not a random.uniform()),
    then the highest-scoring action wins. This means the AI won't always play optimally, giving the player occasional lucky escapes.
    See CLAUDE.md's "Enemy AI and team combat" section for the full decided design."""
    scores = _score_candidate_actions(enemy, player_team)

    noisy_scores = {
        action: score + (random.random() - 0.5) * enemy.randomness_weight
        for action, score in scores.items()
    }

    return max(noisy_scores, key=lambda action: noisy_scores[action])

def tick_start_of_turn_if_needed(player: Player) -> list[str]:
    """Tick status effects/spell cooldowns once per round, not once per command - guarded by player.turn_started so a free (non-turn-ending)
    action followed by a real one in the same round doesn't double-tick. Whichever action actually ends the round is responsible
    for letting resolve_companion_and_enemy_turns() reset turn_started back to False."""
    if player.turn_started:
        return []
    player.turn_started = True
    if not player.is_alive():
        return []
    messages = player.tick_status_effects()
    player.tick_spell_cooldowns()
    return messages

def resolve_combat_round(player: Player, target: Enemy, player_team: list[Character], enemy_team: list[Enemy], attack_type: str = "light") -> str:
    """One full round: player attacks target, then their companion (if any, and still alive) takes its own turn via
    choose_companion_action(), then every enemy in enemy_team still alive takes its own turn via choose_enemy_action() -
    attack (with real target selection once either side has more than one living member), defend, or heal throughout.
    Stops rolling further turns the moment the player is dead."""
    messages = tick_start_of_turn_if_needed(player)

    if player.is_alive():
        messages.append(player.attack(target, attack_type))

    tail = resolve_companion_and_enemy_turns(player, player_team, enemy_team)
    if tail:
        messages.append(tail)
    messages.append(format_hp_line(player_team, enemy_team))
    return "\n".join(messages)

def resolve_attack_and_check_defeat(player: Player, target: Enemy, player_team: list[Character], enemy_team: list[Enemy], room: Room, attack_type: str = "light") -> str:
    """The single correct way to resolve an attack - see CLAUDE.md's rule against calling resolve_combat_round() directly."""
    enemies_before = [enemy for enemy in enemy_team if enemy.is_alive()]

    result = resolve_combat_round(player, target, player_team, enemy_team, attack_type)

    newly_defeated = [enemy for enemy in enemies_before if not enemy.is_alive()]
    for enemy in newly_defeated:
        # default to ending combat - handle_enemy_defeat() overrides this back to True (with a new
        # current_target) if the enemy has a next_phase_factory, i.e. a boss phase transition
        player.in_combat = False
        player.current_target = None
        defeat_extras = handle_enemy_defeat(room, enemy, player)
        if defeat_extras:
            result += f"\n{defeat_extras}"

    if newly_defeated and any(enemy.is_alive() for enemy in room.enemies):
        # something died this round, but the room still has living enemies (either teammates who survived, or a fresh boss
        # phase handle_enemy_defeat() just added) - combat isn't over, even though the loop above just cleared in_combat
        # for the specific enemy that died 
        player.in_combat = True

    return result

def resolve_companion_and_enemy_turns(player: Player, player_team: list[Character], enemy_team: list[Enemy]) -> str:
    """Companion's turn (if present and alive), then every living enemy's turn, in enemy_team order - the shared tail common
    to attack/use/cast, always called after the player's own action and tick have already happened. Returns a message, does not print.
    Safe to call even if the player is already dead (returns "" immediately) - though the real guard for that should already exist
    at the call site before this is reached."""
    if not player.is_alive():
        player.turn_started = False
        return ""

    messages = []
    if player.companion is not None and player.companion.is_alive():
        messages.extend(player.companion.tick_status_effects())
    if player.is_alive() and player.companion is not None and player.companion.is_alive():
        companion_action = choose_companion_action(player.companion, enemy_team)
        if companion_action == "attack":
            companion_target = choose_companion_target(player.companion, enemy_team)
            messages.append(player.companion.attack(companion_target))
        elif companion_action == "defend":
            player.companion.pending_damage_reduction = player.companion.brace_amount
            messages.append(f"{player.companion.name} braces for incoming damage.")
        elif companion_action == "heal":
            healed = min(player.companion.heal_amount, player.companion.max_hp - player.companion.hp)
            player.companion.hp += healed
            messages.append(f"{player.companion.name} recovers {healed} HP.")

    if player.is_alive():
        for enemy in enemy_team:
            if enemy.is_alive():
                messages.extend(enemy.tick_status_effects())
            if enemy.is_alive():
                action = choose_enemy_action(enemy, player_team)
                if action == "attack":
                    enemy_target = choose_enemy_target(enemy, player_team)
                    messages.append(enemy.attack(enemy_target))
                elif action == "defend":
                    enemy.pending_damage_reduction = enemy.brace_amount
                    messages.append(f"{enemy.name} braces for incoming damage.")
                elif action == "heal":
                    healed = min(enemy.heal_amount, enemy.max_hp - enemy.hp)
                    enemy.hp += healed
                    messages.append(f"{enemy.name} recovers {healed} HP.")
            if not player.is_alive():
                break

    player.turn_started = False
    return "\n".join(messages)

def handle_enemy_defeat(room: Room, enemy: Enemy, player: Player) -> str:
    """Remove the defeated enemy, drop loot (or trigger a phase transition), and grant XP/gold. Assembles one combined message, does not print."""
    if enemy.next_phase_factory is not None:
        next_phase = enemy.next_phase_factory()
        room.remove_enemy(enemy)
        room.add_enemy(next_phase)
        # transition stays seamless (roadmap.md's boss-fights decision) - combat stays locked in,
        # current_target just moves to the new phase, no need for the player to re-attack
        player.in_combat = True
        player.current_target = next_phase
        return f"{enemy.name} falls, but something rises to take its place - {next_phase.name}."

    room.remove_enemy(enemy)

    messages = []

    # move loot into the room only - Enemy.on_death() already reports what dropped
    for item in enemy.loot:
        room.add_item(item)

    if enemy.gold_reward > 0:
        player.gold += enemy.gold_reward
        messages.append(f"{player.name} picked up {enemy.gold_reward} gold.")

    if enemy.experience_reward > 0:
        messages.append(player.gain_experience(enemy.experience_reward))

    return "\n".join(messages)

def flee_combat(player: Player, enemy_team: list[Enemy]) -> str:
    """Attempt to disengage from combat. Always succeeds, but every still=living enemy in enemy_team independently rolls its own
    chance of landing a free hit as the player disengages, scaled by that enemy's own HP%."""
    messages = []
    hit_landed = False

    for enemy in enemy_team:
        if not enemy.is_alive():
            continue

        chance_of_free_hit = enemy.hp / enemy.max_hp
        enemy.has_been_fled_from = True

        if random.random() < chance_of_free_hit:
            hit_landed = True
            damage_dealt, death_message = player.take_damage(enemy.attack_damage, attacker=enemy)
            messages.append(f"The {enemy.name} gets a hit in as you go - {damage_dealt} damage.")
            if death_message:
                messages.append(death_message)
            if not player.is_alive():
                # a parting hit finished the player off - stop rolling further enemies
                break

    if hit_landed:
        return "You disengage but not without cost.\n" + "\n".join(messages)
    return "You disengage cleanly, leaving your enemies behind."

def handle_target_command(command: str, enemy_team: list[Enemy], player: Player) -> str:
    """Handle 'target <name>' or 'target <name> <number>' - sets player.current_target to a matching, still-living, enemy in enemy_team.
    The trailing number disambiguates when two or more living enemies share a name; see get_enemy_display_name() for the matching
    numbering shown in combat displays."""
    argument = command.removeprefix("target ").strip()
    if not argument:
        return "Target who?"

    parts = argument.split()
    requested_number = None
    if len(parts) > 1 and parts[-1].isdigit():
        requested_number = int(parts[-1])
        name = " ".join(parts[:-1])
    else:
        name = argument

    same_named = [enemy for enemy in enemy_team if enemy.name.lower() == name.lower()]

    if requested_number is not None:
        if not (1 <= requested_number <= len(same_named)):
            return f"There's no {name} number {requested_number} here."
        candidate = same_named[requested_number - 1]
        if not candidate.is_alive():
            return f"The {get_enemy_display_name(candidate, enemy_team)} has already been defeated."
        player.current_target = candidate
        return f"You focus on the {get_enemy_display_name(candidate, enemy_team)}."


    living_matches = [enemy for enemy in same_named if enemy.is_alive()]

    if not living_matches:
        return f"There's no '{name}' here to target."

    if len(living_matches) == 1:
        player.current_target = living_matches[0]
        return f"You focus on the {get_enemy_display_name(living_matches[0], enemy_team)}."

    options = ", ".join(get_enemy_display_name(enemy, enemy_team) for enemy in living_matches)
    return f"There's more than one {name} here - which one? Try: {options}"

def handle_combat_command(command: str, player: Player, target: Enemy, player_team: list[Character], enemy_team: list[Enemy], room: Room) -> str:
    """Dispatcher for everything valid while player.in_combat is True."""
    if command.startswith("target "):
        return handle_target_command(command, enemy_team, player)

    if command == "attack" or command.startswith("attack "):
        attack_type = command.removeprefix("attack").strip() or "light"
        if attack_type not in ("light", "heavy", "ranged"):
            return f"Unknown attack type '{attack_type}'. Try 'attack light', 'attack heavy', or 'attack ranged'."
        if attack_type == "ranged" and player.equipped_ranged_weapon is None:
            return "You have nothing to shoot with - equip a ranged weapon first."
        return resolve_attack_and_check_defeat(player, target, player_team, enemy_team, room, attack_type)

    if command.startswith("cast "):
        spell_name = command.removeprefix("cast ").strip()
        spell = next((s for s in player.known_spells if s.name.lower() == spell_name.lower()), None)
        if spell is None:
            return f"You don't know a spell called '{spell_name}'."
        if spell.name in player.spell_cooldowns:
            return f"{spell.name} is still on cooldown."
        if player.mana < spell.mana_cost:
            return f"Not enough mana for {spell.name} ({spell.mana_cost} needed, {player.mana} available)."

        failure = spell.would_fail(player, target)
        if failure is not None:
            return failure
        
        tick_messages = tick_start_of_turn_if_needed(player)

        result = spell.cast(player, target)
        player.mana -= spell.mana_cost
        player.spell_cooldowns[spell.name] = 1

        result = "\n".join(tick_messages + [result]) if tick_messages else result

        tail = resolve_companion_and_enemy_turns(player, player_team, enemy_team)
        if tail:
            result += f"\n{tail}"

        result += f"\n{format_hp_line(player_team, enemy_team)}"
        return result

    if command == "flee":
        result = flee_combat(player, enemy_team)
        player.in_combat = False
        player.current_target = None
        player.turn_started = False
        return result

    if command.startswith("use "):
        item_name = command.removeprefix("use ").strip()
        item = next((i for i in player.inventory.items if i.name.lower() == item_name.lower()), None)
        if item is None:
            return f"No item named '{item_name}' in inventory."

        failure = item.would_fail(player)
        if failure is not None:
            return failure

        tick_messages = tick_start_of_turn_if_needed(player)

        result = player.inventory.use_item(item_name, player)

        result = "\n".join(tick_messages + [result]) if tick_messages else result

        if item.ends_turn(player):
            tail = resolve_companion_and_enemy_turns(player, player_team, enemy_team)
            if tail:
                result += f"\n{tail}"

        if not player.is_alive():
            player.in_combat = False
            player.current_target = None
            player.turn_started = False

        result += f"\n{format_hp_line(player_team, enemy_team)}"
        return result

    if command == "stats":
        return player.get_stats()

    if command == "skills":
        return player.get_skills_display()

    if command.startswith("learn "):
        path_name = command.removeprefix("learn ").strip()
        try:
            return player.skill_tree.invest(path_name, player)
        except ValueError as e:
            return str(e)

    if command == "inventory":
        return player.get_inventory_display()

    return "You can't do that mid-combat. Try 'attack', 'flee', 'use <item>', 'stats', 'skills', or 'inventory'." 