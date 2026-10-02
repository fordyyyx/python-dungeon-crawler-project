"""Report the gold each floor can give, straight from the game's content - a baseline for pricing Charon's shop (see roadmap.md).

For each floor: gold from gated fights (enemies in a room with a guarded exit - the player must win them to go on), gold from optional fights,
fixed treasure, and what the floor's loot and items would sell to Charon for. Every phase and wave of a fight is counted. This is an upper bound
on what's *available*, not what a real player ends up with - for that, see /balance-check."""

from dungeon_crawler.content import build_world
from dungeon_crawler.content.floor_6 import NYMPHS_TREASURE_GOLD
from dungeon_crawler.exchange import sale_price
from dungeon_crawler.exploration import encounter_enemies

FIXED_TREASURE = {"floor_1": 15,
                  "floor_6": NYMPHS_TREASURE_GOLD + 40}
"""Gold handed out by room interactions rather than enemies: the Sunken Vault's chest (floor 1), and the Cave of the Nymphs' gifts plus the
Throne Room's chest (floor 6). Update this whenever fixed treasure is added. Random chests aren't counted - their gold is rolled per run."""

def sellable_value(items) -> int:
    return sum(price for price in (sale_price(item) for item in items) if price is not None)

def main() -> None:
    dungeon, start, all_floors = build_world()
    print(f"{'Floor':<9}{'Gated':>8}{'Optional':>10}{'Treasure':>10}{'Sellable':>10}{'Floor total':>13}{'Running total':>15}")
    running = 0
    for floor_key, rooms in all_floors.items():
        gated = optional = sellable = 0
        for room in rooms.values():
            stages = [stage for enemy in room.enemies for stage in encounter_enemies(enemy)]
            gold = sum(stage.gold_reward for stage in stages)
            if room.guarded_exits:
                gated += gold
            else:
                optional += gold
            sellable += sellable_value(item for stage in stages for item in stage.loot)
            sellable += sellable_value(room.items)
            sellable += sellable_value(item for ally in room.allies for item in ally.inventory.items)
        treasure = FIXED_TREASURE.get(floor_key, 0)
        total = gated + optional + treasure + sellable
        running += total
        print(f"{floor_key:<9}{gated:>8}{optional:>10}{treasure:>10}{sellable:>10}{total:>13}{running:>15}")

if __name__ == "__main__":
    main()