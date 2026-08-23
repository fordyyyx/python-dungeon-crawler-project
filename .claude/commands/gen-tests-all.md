Read CLAUDE.md for project context. Generate tests for each of these
files, in this order, one at a time:
characters.py, items.py, world.py, content.py, engine.py

For each file, use its matching test file under tests/. Check what's
already there first — never duplicate existing tests, only add missing
coverage. Apply every convention in CLAUDE.md exactly.

For engine.py specifically, only test standalone functions with plain
arguments and return values — never attempt to test main().

Stop after each file and summarize what you added before moving to the
next one.