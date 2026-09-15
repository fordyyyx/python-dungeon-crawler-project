Update the following markdown files: $ARGUMENTS (if empty, update all of:
CLAUDE.md, roadmap.md, README.md, dev_guide.md, map.md, porting_notes.md).

Read CLAUDE.md first for project context (even if it's one of the files
being updated), then read every file in scope for this run before changing
any of them.

The goal is to bring these files back in sync with the ACTUAL current state
of `src/dungeon_crawler/` and `tests/` — verify every claim against the real
code (grep/read the actual file), never against what roadmap.md or CLAUDE.md
already says, since those can themselves be stale. Use `git diff`/`git log`
on `src/` and `tests/` to find what's actually changed since these files
were last updated, rather than guessing from memory.

## Per-file responsibilities

- **roadmap.md** — for each "In order"/"Long-term" item, check whether the
  code now genuinely implements what the item describes (not just partially
  — verify the specific decided behaviours listed). If so, move it to
  Completed with a write-up matching the density/style of existing Completed
  entries: what was built, any deliberate deviations from the original plan,
  and any real bug found and fixed along the way. Renumber every remaining
  "In order"/"Long-term" item afterward, and fix every `#N` cross-reference
  anywhere in the file (including inside other Completed entries) to match
  the new numbering — see the file's own cross-reference rule at the top.
- **CLAUDE.md** — update the module ownership list (new functions/files),
  "Canonical attribute names" (new attributes on `Character`/`Player`/
  `Enemy`/`Room`/etc.), and add or update a feature-specific section for any
  newly-built mechanic, matching the density of existing sections like
  "Practice Chamber and respawning enemies" or "Save/load system and the
  title screen". Keep the "Keeping documentation in sync with code" section
  accurate — especially its claim about `get_controls_text()`/README being
  in sync.
- **README.md** — update Features, Project Structure, and the Roadmap
  summary paragraph. Do NOT add anything to the Controls section that isn't
  already in `engine.py`'s `get_controls_text()` — there's no shared source
  between the two (see CLAUDE.md), so README must never get ahead of the
  actual command list. If a command exists in one but not the other, report
  it as a gap rather than silently fixing only one side.
- **dev_guide.md** — cross-check the "What's actually spawnable/addable
  right now" lists against the real `ITEM_REGISTRY`/`ENEMY_REGISTRY`/
  `ALLY_REGISTRY`/`COMPANION_REGISTRY`/`SPELL_REGISTRY` in `dev_tools.py`,
  update Quick Recipes for any new dev-testable flow, and keep the "What
  can't be playtested through real game content yet" section precise about
  exactly which trades/systems are and aren't completable through normal
  play right now (dev-tool-reachable is not the same as real content).
- **map.md** — cross-check the STATUS section and per-room ally/enemy/item
  notes against what each `build_floor_N()` actually wires in via
  `add_ally()`/`add_enemy()`/`add_item()` — not against what `content.py`'s
  `create_*()` functions merely exist to do.
- **porting_notes.md** — add a note only for a newly-built, genuinely
  player-facing mechanic with a real visual-port implication. Skip this file
  entirely if nothing new fits that bar — don't pad it for the sake of
  touching every file.

## Rules

- Documentation-only pass — do not modify any logic in `src/`. If you find
  a real bug while verifying a claim against the code, flag it (same as
  `/update-stale-docstrings` would) rather than fixing it here.
- Don't restate history that isn't useful — describe current behaviour,
  keeping only the short "real bug found and fixed"-style notes this
  codebase already uses when they're genuinely worth remembering.
- Preserve each file's existing voice/density — roadmap.md's entries are
  long and technical, README.md's are short and player-facing; don't
  flatten that distinction.
- After editing, run the test suite as a sanity check even though these are
  docs-only changes — confirms nothing else was accidentally touched.

Report a summary per file: what you changed and why, plus anything you
found but left alone because you couldn't verify it from code alone.
