Read CLAUDE.md for project context, then generate tests for each of the
following files, one at a time, in order: $ARGUMENTS

For each file, use its matching test file under tests/ (e.g. characters.py
-> tests/test_characters.py). Check what's already there first — do not
duplicate existing tests, only add coverage for what's missing.

Apply every convention in CLAUDE.md exactly, including the None-check
pattern for get_exit/get_room results.

If the file is engine.py, only test standalone functions that take plain
arguments and return a value — do not attempt to test main() itself.

After each file, tell me what behaviours you added tests for before
moving to the next file, so I can review incrementally rather than all
at once at the end.