Read CLAUDE.md for project context, then generate tests for each of the
following files, one at a time, in order: $ARGUMENTS

For each file, use its matching test file under tests/ (e.g. characters.py
-> tests/test_characters.py). Check what's already there first — do not
duplicate existing tests, only add coverage for what's missing.

Apply every convention in CLAUDE.md exactly, including the None-check
pattern for get_exit/get_room results, and the monkeypatch rules
(approved only for randomness, input/file mocking, and main() smoke tests
— see CLAUDE.md's "Testing main()" section).

If the file is engine.py, unit-test every standalone function that takes
plain arguments and returns a value as normal. For main() itself, add
only a small number of end-to-end smoke tests (scripted input() sequences
via monkeypatch, output checked via capsys) covering high-value flows
like a full happy-path playthrough or dev-command routing — do not try
to exhaustively script every command/state combination; that's what
manual playtesting is for. Keep these smoke tests clearly distinct from
the granular unit tests elsewhere.

After each file, tell me what behaviours you added tests for before
moving to the next file, so I can review incrementally rather than all
at once at the end.