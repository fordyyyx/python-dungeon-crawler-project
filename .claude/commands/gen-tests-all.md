Read CLAUDE.md for project context. Generate tests for each of these
files, in this order, one at a time:
characters.py, items.py, world.py, content/ (the whole package), combat.py,
exploration.py, character_creation.py, save_system.py, dev_tools.py,
engine.py, status_effects.py, spells.py, hints.py

(The engine.py reorganisation is complete, status effects/spells, the
save/load system, and one-off contextual hints (hints.py) are built, and
content.py is now a content/ package - this is the full current module list. Add new files to it as future roadmap items
introduce them, e.g. skills.py, achievements.py, shop.py, difficulty.py.)

For each file, use its matching test file under tests/. The content/
package (one module per floor, plus common.py, dev_content.py,
ancestries.py and world_builder.py) is still covered by the single
tests/test_content.py - every name is re-exported from
dungeon_crawler.content, so tests import from there, not from the
submodules. Check what's already there first - never duplicate existing
tests, only add missing coverage. Apply every convention in CLAUDE.md
exactly, including the monkeypatch rules (approved only for randomness,
input/file mocking, and main() smoke tests - see CLAUDE.md's "Testing
main()" section).

For engine.py specifically, unit-test standalone functions with plain
arguments and return values as normal. For main() itself, add only a
small number of end-to-end smoke tests (scripted input() via monkeypatch,
output via capsys) for high-value flows - not exhaustive coverage of
every command/state combination.

Stop after each file and summarize what you added before moving to the
next one.
