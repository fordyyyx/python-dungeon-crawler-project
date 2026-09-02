Read CLAUDE.md for project context, then move existing tests from
$ARGUMENTS.

$ARGUMENTS is given as "OLD_FILE -> NEW_FILE function_names", e.g.
"tests/test_engine.py -> tests/test_combat.py
resolve_combat_round, handle_enemy_defeat, flee_combat,
resolve_attack_and_check_defeat, handle_combat_command,
format_hp_line".

For each named function:
1. Find its existing test(s) in OLD_FILE — do not regenerate them,
   move them verbatim.
2. Fix only the import lines to match the function's new module
   location (per CLAUDE.md's current module ownership list).
3. Append the moved test(s) to NEW_FILE, creating it with the
   standard test-file header if it doesn't exist yet.
4. Remove the moved test(s) from OLD_FILE.

Do not change test logic, assertions, or naming — only the file
location and the import lines. If a named function's tests can't be
found in OLD_FILE, tell me instead of guessing or skipping silently.

KNOWN GAP (see CLAUDE.md): this command does not clean up OLD_FILE's
own top-level import statement for names that just left. After every
run, manually check OLD_FILE's import line and remove any names that
no longer live there — otherwise it fails to import at all with a
confusing ImportError, even though the actual moved tests are fine.

After moving, tell me exactly which tests moved, so I can review
before running pytest.