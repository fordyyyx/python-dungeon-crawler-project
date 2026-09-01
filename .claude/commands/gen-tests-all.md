Read CLAUDE.md for project context. Generate tests for each of these
files, in this order, one at a time:
characters.py, items.py, world.py, content.py, combat.py, dev_tools.py, engine.py

(This list reflects the engine.py reorganisation in progress — add new
files to it as more modules get split out, e.g. exploration.py,
character_creation.py, skills.py, once they exist.)

For each file, use its matching test file under tests/. Check what's
already there first — never duplicate existing tests, only add missing
coverage. Apply every convention in CLAUDE.md exactly, including the
monkeypatch rules (approved only for randomness, input/file mocking, and
main() smoke tests — see CLAUDE.md's "Testing main()" section).

For engine.py specifically, unit-test standalone functions with plain
arguments and return values as normal. For main() itself, add only a
small number of end-to-end smoke tests (scripted input() via monkeypatch,
output via capsys) for high-value flows — not exhaustive coverage of
every command/state combination.

Stop after each file and summarize what you added before moving to the
next one.