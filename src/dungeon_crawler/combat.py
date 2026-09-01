"""Combat resolution - turn-by-turn attacks, defeat handling, and fleeing. The one place that resolves what happens when the player
and an enemy trade blows, and the aftermath (loot, XP, gold, or a boss phase transition) when an enemy is defeated."""

import random

from dungeon_crawler.characters import Player, Enemy
from dungeon_crawler.world import Room

def format_hp_line(player: Player, enemy: Enemy) -> str:
    """See HP status line - never rebuild this string elsewhere. See CLAUDE.md fro why this exists as its own function."""
    return f"{player.name}: {player.hp}/{player.max_hp} HP  |  {enemy.name}: {enemy.hp}/{enemy.max_hp} HP"

def resolve_combat_round(player: Player, enemy: Enemy):
    """One full exchange: player attacks, enemy counter-attacks if it survived."""
    messages = [player.attack(enemy)]

    if not enemy.is_alive():
        # enemy is already defeated - show only the player's own HP, not the two-sided format_hp_line
        messages.append(f"{player.name}: {player.hp}/{player.max_hp} HP")
        return "\n".join(messages)

    messages.append(enemy.attack(player))
    messages.append(format_hp_line(player, enemy))

    return "\n".join(messages)

def resolve_attack_and_check_defeat(player: Player, enemy: Enemy, room: Room) -> str:
    """The single correct way to resolve an attack - see CLAUDE.md's rule against calling resolve_combat_round() directly."""
    result = resolve_combat_round(player, enemy)
    if not enemy.is_alive():
        player.in_combat = False
        player.current_target = None
        defeat_extras = handle_enemy_defeat(room, enemy, player)
        if defeat_extras:
            result += f"\n{defeat_extras}"
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

def flee_combat(player: Player, enemy: Enemy) -> str:
    """Attempt to disengage from combat. Always succeeds, but a healthier enemy has a higher chance
    of landing a free hit as the player disengages."""
    chance_of_free_hit = enemy.hp / enemy.max_hp
    enemy.has_been_fled_from = True
    if random.random() < chance_of_free_hit:
        damage_dealt, death_message = player.take_damage(enemy.attack_damage, attacker=enemy)
        message = f"You disengage, but the {enemy.name} gets a hit in as you go - {damage_dealt} damage."
        if death_message:
            message += f"\n{death_message}"
        return message
    return f"You disengage cleanly, leaving the {enemy.name} behind."

def handle_combat_command(command: str, player: Player, enemy: Enemy, room: Room) -> str:
    """Dispatcher for everything calid while player.in_combat is True."""
    if command == "attack":
        return resolve_attack_and_check_defeat(player, enemy, room)

    if command == "flee":
        result = flee_combat(player, enemy)
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

        if enemy.is_alive():
            enemy_message = enemy.attack(player)
            result += f"\n{enemy_message}"
            result += "\n" + format_hp_line(player, enemy)
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