# Project Context for Claude Code

## What this project is
A text-based dungeon crawler RPG in pure Python, Greek mythology themed, built as an OOP portfolio project. The person building this is a first-year Computer Science student — code should stay readable and instructive, not overly clever or terse.

## Code style
- **British English spelling** in all identifiers, comments, and strings — `armour` not `armor`, `defence` not `defense`, `colour` not `color`, etc.
- `src/` layout: source lives in `src/dungeon_crawler/`, tests in `tests/`
- One responsibility per module:
  - `characters.py` — `Character`, `Player`, `Enemy`, `Ally`, `Skill`, `SkillPath`, `SkillTree`
  - `items.py` — `Item`, `Weapon`, `Armour`, `Consumable`, `QuestItem`, `Inventory`
  - `world.py` — `Room`, `Map`
  - `content.py` — actual game content (instances, not class definitions), organized by floor via `build_floor_0()`, `build_floor_1()`, etc., assembled by `build_world()`. Also holds `ANCESTRIES`, the ancestry-selection data.
  - `engine.py` — the game loop, standalone command-handling functions, and dev tooling (`ITEM_REGISTRY`, `handle_dev_command`)

## Canonical attribute names — do not drift from these
- `Character.attack_damage` — **not** `attack_power`. This project has used `attack_power` inconsistently in earlier design discussion; `attack_damage` is the real, current name. Always check the actual file before assuming.
- `Character.armour`, `Character.hp`, `Character.max_hp` — as expected.
- `Character.has_double_strike`, `Character.has_thorns`, `Character.has_last_stand` — ability flags, live on `Character` (not `Player`), since `Enemy` could plausibly use them too.
- `Player.ancestry_label` — set at character creation, displayed in `get_stats()`.

## Testing conventions — follow these exactly, don't introduce new patterns
- **Plain `assert` statements only** — do NOT use `pytest.raises`. For testing that an exception is raised, use the manual pattern:
  ```python
  def test_example_raises_error():
      try:
          thing_that_should_fail()
          assert False, "Expected a ValueError but none was raised"
      except ValueError:
          pass
  ```
- **One test per behavior**, not one test per method. Multiple `assert` lines in one test are fine if they're all checking the result of the *same* action — split into separate tests if you'd need "and" to describe what's being checked.
- **Test naming**: `test_<what>_<expected_behavior>`.
- **Arrange-Act-Assert** structure in every test.
- **Identity vs equality**: classes in this project do NOT define `__eq__`. Test object presence with `is`/`in` against actual object references, never a freshly-constructed equivalent. Do not add `__eq__` to make tests easier.
- **Private attributes**: `Room` and `Inventory` use private lists (`_items`, `_enemies`, `_allies`) with controlled methods and a read-only `@property` for reading. Tests must go through public methods/properties, never `._items` etc. directly.
- Tests involving printed output use `capsys` — but note most methods that used to print now **return strings instead** (see below). Check whether `capsys` is actually still needed before using it.
- **Type-checking pattern**: `Room.get_exit()` and `Map.get_room()` return `Room | None`. Any test using the result must `assert result is not None` before accessing attributes, to satisfy Pylance's type narrowing.

## Design principles already established - don't fight these
- Composition over inheritance where the relationship is "has-a" (`Player.inventory`, `Player.skill_tree`), inheritance only for genuine "is-a" relationships.
- `Ally` is a standalone class, NOT `Ally(Character)`. Allies don't have combat stats.
- Functions that coordinate two independent classes (moving an item between a `Room` and a `Player`, trading between an `Ally` and a `Player`) live as standalone functions in `engine.py`. Functions that only touch one class's own state are methods on that class. Exception: `Inventory.use_item()` and `Inventory.unequip_item()` are methods on `Inventory` despite touching a `Character` too - this is established precedent, don't "fix" it to be a standalone function.
- **Per-ally behaviour is data, not branching.** Trade requirements (`Ally.required_items`), rewards (`Ally.reward`), and conditional dialogue (`Ally.hint_complete`) live as attributes on the `Ally` object. Never write `if ally.name == "X"` in `engine.py` - if new per-ally behaviour is needed, add a new attribute to `Ally` instead.
- **`take_damage()` returns `tuple[int, str]`**: the actual damage dealt (after armour reduction) and a message (empty string if the target survived). It takes an optional `attacker: Character | None = None` parameter, used only for the Thorns ability to reflect damage back.
- **`on_death()` returns a string, does not print.** All defeat/loot messaging is assembled and printed once, at the `engine.py` level, in the correct order - never print directly from inside `Character`/`Enemy`/`Player` methods.
- **Equip is single-slot per category.** A `Character` has `equipped_weapon`/`equipped_armour` (max one of each). Equipping a new weapon automatically unequips the old one first - it does not stack. Do not add multi-weapon/dual-wielding support without an explicit design discussion first.
- **Quest items** (`QuestItem` subclass) cannot be dropped (`Inventory.drop_item` raises `ValueError`) and are displayed separately, on their own line, at the bottom of `get_inventory_display()`.
- **Locked exits**: `Room.locked_exits: dict[str, str]` maps a direction to a required item name. `is_exit_locked(room, direction, player)` in `engine.py` checks it. Never hardcode "first room only" logic - locking is what enforces order.
- **`map` vs `fullmap`/`world` are deliberately different**: `map` shows only the current room's own exits (cheap, local). `fullmap`/`world` does a recursive traversal from the current room, stopping at any locked exit, showing everything currently reachable. Don't merge these back into one command.
- **Dev commands** (`handle_dev_command`, gated by the `DEV_MODE` flag, toggled via the `developer mode` command) are testing-only and must never be referenced in the README or any player-facing text.
- Don't add `__eq__`, extra attributes, or extra methods "for flexibility" unless something in the actual design already needs them.

## Ancestry / character creation system
- `content.py` holds `ANCESTRIES: dict[str, dict]` - each entry has `label`, `attack`, `armour`, `hp`, `bonus_skill_point`.
- Stats are **set outright**, not added to a baseline. Picking an ancestry replaces the player's starting stats entirely.
- `engine.py`'s `choose_ancestry()` and `create_player()` handle selection and construction, called in `main()` before the world is built.
- If adding a new ancestry: keep its total "power budget" roughly proportional to existing entries (no strict upgrades over `"basic"` in every stat at once) - see the existing table for the balance pattern (offence-leaning options sacrifice defence, defence-leaning options sacrifice offence, HP-heavy options sacrifice both).

## When generating tests for existing files
Match the existing test files' style exactly. Check what's already there first - never duplicate. Do not introduce `pytest.raises`, `unittest.mock`, fixtures beyond `capsys`, or any pattern not already in use, without asking first.

## Maintenance reminders
- Every new `create_*()` item function in `content.py` should also be added to `ITEM_REGISTRY` in `engine.py`, so `dev add` can find it.
- Every `create_*()` function for enemies/allies needs a non-empty `description`.