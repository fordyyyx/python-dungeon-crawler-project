"""Upgrading weapons and armour with Daedalus' tools, in his Workshop. Each level adds +1 damage or +1 defence. How far an item can go depends on
the player's intellect - the tools are only as useful as your understanding of them. The game's main gold sink."""

from dungeon_crawler.exchange import item_value
from dungeon_crawler.items import Armour, Weapon

MAX_UPGRADE_LEVEL = 5
UPGRADE_COST_FACTOR = 1.0
UPGRADE_MIN_COST = 40
"""Cost per level is max(UPGRADE_MIN_COST, the item's value before upgrades * UPGRADE_COST_FACTOR), multiplied by the level being bought."""

def upgrade_cap(player) -> int:
    """The highest level the player can upgrade an item to: 1 + intellect // 3, up to MAX_UPGRADE_LEVEL, and never below 1, so every ancestry can
    upgrade something. Only limits further upgrades - an item already above it keeps its level."""
    return min(MAX_UPGRADE_LEVEL, 1 + player.intellect // 3)

def is_upgradeable(item) -> bool:
    """Whether item is something Daedalus' tools can improve - a weapon or a piece of armour."""
    return isinstance(item, (Weapon, Armour))

def base_value(item) -> int:
    """The value of item as if it had never been upgraded, so each level's cost doesn't feed into the next. Sets the level to 0 briefly and always
    restores it."""
    level = item.upgrade_level
    item.upgrade_level = 0
    try:
        return item_value(item) or 0
    finally:
        item.upgrade_level = level

def upgrade_cost(item) -> int:
    """The gold cost of item's next level - the per-level price, scaled to its value before upgrades, times the level being bought."""
    per_level = max(UPGRADE_MIN_COST, round(base_value(item) * UPGRADE_COST_FACTOR))
    return per_level * (item.upgrade_level + 1)

def _find_upgradeable(player, item_name: str):
    """The named weapon or armour piece - preferring an equipped copy, since that's the one the player is relying on. None if they don't have one."""
    copies = [item for item in player.inventory.items if item.name.lower() == item_name.lower() and is_upgradeable(item)]
    return next((item for item in copies if item.equipped), copies[0] if copies else None)

def list_upgrades(room, player) -> str:
    """Everything the player could upgrade: current level, the next level's cost, or why they can't go further. Only in the Workshop."""
    if not room.is_workshop:
        return "You'd need proper tools for that."
    cap = upgrade_cap(player)
    items = [item for item in player.inventory.items if is_upgradeable(item)]
    if not items:
        return "You have nothing that Daedalus' tools could improve."
    lines = [f"You understand his tools well enough to upgrade an item to +{cap}. You have {player.gold} gold."]
    for item in items:
        if item.upgrade_level >= MAX_UPGRADE_LEVEL:
            status = "as good as it can ever be"
        elif item.upgrade_level >= cap:
            status = "beyond what you understand, for now"
        else:
            status = f"+{item.upgrade_level + 1} for {upgrade_cost(item)} gold"
        lines.append(f"    {item.display_name} - {status}")
    lines.append("Say 'upgrade' followed by an item's name to improve it.")
    return "\n".join(lines)

def upgrade_item(item_name: str, room, player) -> str:
    """Upgrade the named weapon or armour piece by one level, for upgrade_cost() gold. Refused outside the Workshop, at the item's limit, or without
    enough gold - always changing nothing."""
    if not room.is_workshop:
        return "You'd need proper tools for that."
    item = _find_upgradeable(player, item_name)
    if item is None:
        return f"You have no weapon or armour called '{item_name}'."
    if item.upgrade_level >= MAX_UPGRADE_LEVEL:
        return f"{item.display_name} is as good as it can ever be."
    if item.upgrade_level >= upgrade_cap(player):
        return f"You don't understand Daedalus' tools well enough to improve {item.with_article(definite=True)} any further."
    cost = upgrade_cost(item)
    if player.gold < cost:
        return f"Upgrading it to +{item.upgrade_level + 1} costs {cost} gold - you have {player.gold}."

    player.gold -= cost
    item.upgrade_level += 1
    return f"You work at the bench until the light starts to fail. {item.display_name} - {item.details()}. (Paid {cost} gold.)"