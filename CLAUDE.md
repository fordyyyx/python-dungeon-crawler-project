# Project Context for Claude Code

## What this project is
A text-based dungeon crawler RPG in pure Python, Greek mythology themed, built as an OOP portfolio project. The person building this is a first-year Computer Science student — code should stay readable and instructive, not overly clever or terse.

## Code style
- **British English spelling** in all identifiers, comments, and strings — `armour` not `armor`, `defence` not `defense`, `colour` not `color`, etc.
- `src/` layout: source lives in `src/dungeon_crawler/`, tests in `tests/`
- One responsibility per module: `characters.py` (Character/Player/Enemy/Ally), `items.py` (Item/Weapon/Armour/Consumable/Inventory), `world.py` (Room/Map), `content.py` (actual game content — instances, not class definitions), `engine.py` (game loop and command-handling functions)

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
- **Test naming**: `test_<what>_<expected_behavior>`, e.g. `test_take_damage_reduces_hp`, `test_inventory_add_adds_item`.
- **Arrange–Act–Assert** structure in every test, even if not commented as such.
- **Identity vs equality**: classes in this project do NOT define `__eq__`. When testing whether a specific object ended up somewhere (e.g. an item in a room, an enemy in a list), use `is`/`in` against the *actual object reference*, not a freshly-constructed equivalent object. Do not add `__eq__` to any class to make tests easier — that's a deliberate design choice, not an oversight.
- **Private attributes**: `Room` and `Inventory` both use a private list (`_items`, `_enemies`) with controlled methods (`add_item`/`remove_item`, `add`, etc.) and a read-only `@property` for reading (`.items`, `.enemies`). Tests must go through the public methods/properties — never assert against `._items` or `._enemies` directly.
- Tests that involve `print()` output (e.g. checking `on_death()` messages) use pytest's built-in `capsys` fixture to capture stdout.

## Design principles already established — don't fight these
- Composition over inheritance where the relationship is "has-a" (e.g. `Player.inventory: Inventory`), inheritance only for genuine "is-a" relationships.
- `Ally` is a standalone class, NOT `Ally(Character)` — allies don't have hp/combat stats, deliberately, to avoid unused capability.
- Functions that coordinate two independent classes (e.g. moving an item between a `Room` and a `Player`) live as standalone functions in `engine.py`, not as a method on either class. Functions that only touch one class's own state are methods on that class.
- Don't add `__eq__`, extra attributes, or extra methods "for flexibility" unless something in the actual design already needs them.
- Any new create_*() item function should also be added to ITEM_REGISTRY in engine.py.

## When generating tests for existing files
Match the existing test files' style exactly (check `tests/test_characters.py` and `tests/test_items.py` for the established pattern before writing anything new). Do not introduce `pytest.raises`, `unittest.mock`, fixtures beyond `capsys`, or any testing library/pattern not already in use, without asking first.

## Type-checking pattern
`Room.get_exit()` and `Map.get_room()` return `Room | None`. Any test that
calls one of these and then uses the result must first assert it isn't
None (`assert result is not None`) before accessing attributes or calling
methods on it — this narrows the type for Pylance and prevents
"attribute not on None" warnings. Never skip this check just to shorten
a test.