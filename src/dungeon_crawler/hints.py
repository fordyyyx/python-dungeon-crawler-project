"""One-off contextual hints - each explains a mechanic the first time it becomes relevant, then never again. Tracked per save via
Player.seen_hints (see save_system.py). The text lives here rather than at the trigger sites, so wording can be tuned in one place."""

HINTS: dict[str, str] = {
    "combat": (
        "There's something here that wants a fight. 'attack light' never misses; 'attack heavy' hits much harder but can miss; "
        "'attack ranged' needs a ranged weapon equipped; 'cast <spell>' uses mana. Drinking a healing item or grabbing loot with "
        "'take' doesn't cost your turn. 'flee' gets you out, at the risk of a parting blow."
    ),
    "passive_regen": "Moving between rooms slowly restores HP, but only up to three quarters of your maximum - beyond that you'll need healing items.",
    "guarded_exit": (
        "Some ways forward are guarded - you can't pass until everything in the room is defeated. The way you came in stays open "
        "if you need to retreat and recover."
    ),
    "forge": "This is the forge. 'repair <armour>' restores your armour's durability for gold - armour that breaks stops protecting you entirely.",
    "forge_shortcut": "You've opened a shortcut to the Forge of Prometheus. From the Forge, say <room name> to come straight back here.",
    "practice_chamber": (
        "The dummy here never stays down and gives no rewards - it's for testing - 'dummy set <stat> <value>' changes its stats, "
        "and spells cost no mana while you're in this room."
    ),
    "skill_points": "You have a skill point to spend. Say 'skills' to see what's on offer, then 'learn <path>' - attack, defence, or abilities.",
    "autosave": "The game autosaves the first time you reach each new floor. Outside combat, 'save' saves to your current slot at any time.",
}

def show_hint(player, key: str) -> str:
    """HINTS[key] formatted as a hint the first time it's requested for this player (marking it seen), or '' on every later call. Callers
    print the result only if it's non-empty."""
    if key in player.seen_hints:
        return ""
    player.seen_hints.add(key)
    return f"[Hint] {HINTS[key]}"