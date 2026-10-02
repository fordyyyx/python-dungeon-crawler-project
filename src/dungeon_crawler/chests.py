"""Searchable chests - a room verb, 'open chest', usable once the room is clear (room_is_clear()). Contents land in the room as items, any gold goes
straight to the player, and a room flag records the chest as opened, so nothing new needs saving. One chest per room, so 'open chest' is never
ambiguous. Fixed chests hold hand-chosen contents; random chests roll from a loot table using the player's run seed and the room's name, so a
reload can never change the result."""

import random
import zlib
from dataclasses import dataclass, field
from typing import Callable

from dungeon_crawler.exploration import room_is_clear, CHEST_OPENED

@dataclass
class LootTable:
    """What a random chest can hold: a gold range, and items chosen with replacement, by weight, 'rolls' times. Random chests never hold unique
    items, and their gear stays within the shop's limit - plain items only."""

    gold: tuple[int, int]
    items: list[tuple[int, Callable]] = field(default_factory=list)
    rolls: int = 2

def chest_rng(player, room) -> random.Random:
    """A random-number generator for one chest in one run: seeded from the run seed and the room's name. Uses zlib.crc32 rather than Python's
    hash(), which gives a different answer every time the program runs, and its own Random object, so chest rolls never affect, or are affected
    by, any other roll in the game."""
    return random.Random(zlib.crc32(f"{player.run_seed}:{room.name}".encode("utf-8")))

def roll_loot(table: LootTable, player, room) -> tuple[list, int]:
    """Roll a random chest's contents - (items, gold). The same player run and room always give the same result."""
    rng = chest_rng(player, room)
    gold = rng.randint(*table.gold)
    weights = [weight for weight, _ in table.items]
    factories = [factory for _, factory in table.items]
    items = [rng.choices(factories, weights=weights)[0]() for _ in range(table.rolls)] if factories else []
    return items, gold

def _chest_closed(player, room) -> bool:
    return CHEST_OPENED not in room.flags

def _open_chest(contents: Callable):
    """Build the 'open chest' handler. contents(player, room) returns (items, gold). Refuses, with the reason, while the room isn't clear."""
    def handler(player, room) -> str:
        if not room_is_clear(room):
            blocker = next(enemy for enemy in room.enemies if enemy.is_alive() and not enemy.respawns)
            return f"{blocker.with_article(definite=True)} won't let you anywhere near the chest."
        items, gold = contents(player, room)
        room.flags.add(CHEST_OPENED)
        for item in items:
            room.add_item(item)
        player.gold += gold
        found = [item.with_article() for item in items] + ([f"{gold} gold"] if gold else [])
        if not found:
            return "You force the lid open. It's empty."
        return f"You force the lid open. Inside: {', '.join(found)}." + (" (The items are on the floor - 'take all' to pick them up.)" if items else "")
    return handler

def add_fixed_chest(room, items: list[Callable], gold: int = 0) -> None:
    """Place a chest with hand-chosen contents - item factories and an amount of gold."""
    room.add_interaction("open chest", _open_chest(lambda player, room: ([factory() for factory in items], gold)), _chest_closed, "The chest is empty.")

def add_random_chest(room, table: LootTable) -> None:
    """Place a chest that rolls its contents from table when it's opened."""
    room.add_interaction("open chest", _open_chest(lambda player, room: roll_loot(table, player, room)), _chest_closed, "The chest is empty.")