Read CLAUDE.md for project context, then generate tests for the file
$ARGUMENTS, in its matching test file under tests/ (e.g. characters.py
-> tests/test_characters.py). 

Check what's already there first — do not duplicate existing tests, only
add coverage for what's missing.

Apply every convention in CLAUDE.md exactly, including the None-check
pattern for get_exit/get_room results.

If the file is engine.py, only test standalone functions that take plain
arguments and return a value — do not attempt to test main() itself.
If you find command-handling logic still sitting inline inside main()
rather than pulled into its own function, tell me which one, but don't
refactor it yourself.

After generating, tell me which specific behaviours you added tests for,
so I can review before running them.