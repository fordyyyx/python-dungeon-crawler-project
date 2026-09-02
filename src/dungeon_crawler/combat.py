"""Combat resolution - turn-by-turn attacks, defeat handling, and fleeing. The one place that resolves what happens when the player's team
and an enemy team trade blows, and the aftermath (loot, XP, gold, or a boss phase transition) when an enemy is defeated.

Team representation: no dedicated Team class (see CLAUDE.md's "No Team class" rule) - player_team and enemy_team are both
plain lists (list[Character] / list[Enemy]). player_team is currently always [player] until Companions exist."""

import random

from dungeon_crawler.characters import Character, Player, Enemy
from dungeon_crawler.world import Room

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

def _score_candidate_actions(enemy: Enemy, player_team: list[Character]) -> dict[str, float]:
    """Base (pre-randomness) utility score for every action enemy could currently take. 'attack' is always a candidate; 'defend' is
    excluded when brace_amount == 0 (a no-op brace, mirrors heal's exclusion pattern below); 'heal' only joins when enemy.heal_amount > 0
    (a lore-appropriate heal exists) - both are excluded entirely rather than scored at zero, per CLAUDE.md's "Enemy AI and team
    combat" section."""
    target = player_team[0] # always the plyaer for now - real Companion-aware targeting isn't built yet

    target_hp_ratio = target.hp / target.max_hp
    potential_damage = max(0, enemy.attack_damage - target.armour)
    kill_potential = min(1.0, potential_damage / target.hp) if target.hp > 0 else 0.0

    self_missing_hp_ratio = 1 - (enemy.hp / enemy.max_hp)

    scores = {
        "attack": enemy.aggression_weight * (kill_potential + (1 - target_hp_ratio)),
    }

    if enemy.brace_amount > 0:
        # scored on genuine incoming danger, not accumulated damage - a losing enemy with little to fear from the player's own attack
        # shouldn't turtle just because it's already hurt. This was previously caution_weight * self_missing_hp_ratio, which had no
        # ceiling pulling it back down once an enemy got hurt, so it could permanently dominate attack - see CLAUDE.md's "Known
        # issue, fix decided" note.
        potential_damage_to_self = max(0, target.attack_damage - enemy.armour)
        self_kill_potential = min(1.0, potential_damage_to_self / enemy.hp) if enemy.hp > 0 else 0.0
        scores["defend"] = enemy.caution_weight * self_kill_potential

    if enemy.heal_amount > 0:
        # scaled by how much of a top-up the heal actually represents, so a large heal is more attractive to a caution-weighted
        # enemy than a token one
        heal_value_ratio = min(1.0, enemy.heal_amount / enemy.max_hp)
        scores["heal"] = enemy.caution_weight * self_missing_hp_ratio * heal_value_ratio

    return scores

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

def resolve_combat_round(player: Player, target: Enemy, player_team: list[Character], enemy_team: list[Enemy]) -> str:
    """One full round: player attacks target, then every enemy in enemy_team still alive afterwards takes its own turn, decided by
    choose_enemy_action()'s utility scoring. attack, defend (a flat damage reduction consumed by the enemy's next hit taken),
    or heal (only ever chosen by enemies with heal_amount > 0). Enemy targeting is still a placeholder (always the player) until
    Companions exist. Stops rolling further enemy turns once the player is dead - continuing would re-trigger take_damage()'s on_death()
    message repeatedly for no reason."""
    messages = [player.attack(target)]

    for enemy in enemy_team:
        if enemy.is_alive():
            action = choose_enemy_action(enemy, player_team)
            if action == "attack":
                messages.append(enemy.attack(player))
            elif action == "defend":
                enemy.pending_damage_reduction = enemy.brace_amount
                messages.append(f"{enemy.name} braces for incoming damage.")
            elif action == "heal":
                healed = min(enemy.heal_amount, enemy.max_hp - enemy.hp)
                enemy.hp += healed
                messages.append(f"{enemy.name} recovers {healed} HP.")
            if not player.is_alive():
                break

    messages.append(format_hp_line(player_team, enemy_team))
    return "\n".join(messages)

def resolve_attack_and_check_defeat(player: Player, target: Enemy, player_team: list[Character], enemy_team: list[Enemy], room: Room) -> str:
    """The single correct way to resolve an attack - see CLAUDE.md's rule against calling resolve_combat_round() directly.
    Checks every member of enemy_team for defeat afterwards, not just target, since a full team round can defeat more than one
    enemy at once (e.g. a Thorns reflection killing an enemy during its own attack)."""
    enemies_before = [enemy for enemy in enemy_team if enemy.is_alive()]

    result = resolve_combat_round(player, target, player_team, enemy_team)

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

    if command == "attack":
        return resolve_attack_and_check_defeat(player, target, player_team, enemy_team, room)

    if command == "flee":
        result = flee_combat(player, enemy_team)
        player.in_combat = False
        player.current_target = None
        return result

    if command.startswith("use "):
        item_name = command.removeprefix("use ").strip()
        try:
            result = player.inventory.use_item(item_name, player)
        except ValueError as e:
            # return immediately on failure - a failed action must never cost the player's turn (see CLAUDE.md;
            # this exact branch used to fall through into the enemy's attack unconditionally, a real bug)
            return str(e)

        for enemy in enemy_team:
            if enemy.is_alive():
                action = choose_enemy_action(enemy, player_team)
                if action == "attack":
                    result += f"\n{enemy.attack(player)}"
                elif action == "defend":
                    enemy.pending_damage_reduction = enemy.brace_amount
                    result += f"\n{enemy.name} braces for incoming damage."
                elif action == "heal":
                    healed = min(enemy.heal_amount, enemy.max_hp - enemy.hp)
                    enemy.hp += healed
                    result += f"\n{enemy.name} recovers {healed} HP."
                if not player.is_alive():
                    break

        result += "\n" + format_hp_line(player_team, enemy_team)

        if not player.is_alive():
            player.in_combat = False
            player.current_target = None
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