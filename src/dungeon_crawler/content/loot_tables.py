"""Loot tables for random chests, by stage of the game. Plain items only - never unique items - and gear within the shop's limit."""

from dungeon_crawler.chests import LootTable
from .common import (
    create_small_healing_potion, create_field_dressing, create_kelp_poultice, create_cup_of_kykeon,
    create_bronze_xiphos, create_bronze_buckler, create_bronze_greataxe, create_hoplite_sword, create_obol_of_return,
)

EARLY_LOOT = LootTable(gold=(15, 30), rolls=1, items=[(2, create_small_healing_potion), (2, create_field_dressing), (3, create_bronze_xiphos)])
"""Floors 1-3."""

MIDDLE_LOOT = LootTable(gold=(25, 50), rolls=1, items=[(3, create_kelp_poultice), (3, create_bronze_buckler), (3, create_bronze_greataxe)])
"""Floors 4-5."""

LATE_LOOT = LootTable(gold=(35, 65), rolls=1, items=[(2, create_cup_of_kykeon), (2, create_obol_of_return), (3, create_hoplite_sword)])
"""Floors 6 onwards."""