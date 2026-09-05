Read CLAUDE.md for project context, then scan the following files for
stale docstrings/comments: $ARGUMENTS (if empty, scan every file under
src/dungeon_crawler/).

Look specifically for language describing something as missing,
unbuilt, or pending — phrases like "not yet", "yet to be", "no real ...
yet", "known gap", "not yet placed", "not yet built", "not yet decided",
"pending", "still to do", "TBD", "for now" — in docstrings, inline
comments, and module-level docstrings.

For each match, verify against the ACTUAL current code (not roadmap.md
or CLAUDE.md alone, since those can themselves be stale) whether the
described gap is still real:
- If the code the docstring is attached to now does the thing it says
  is missing, the docstring is stale — rewrite it to describe current
  behaviour.
- If the gap is genuinely still open, leave it alone.
- If you're not sure whether it's closed (e.g. it depends on a design
  decision you can't verify from code alone), don't guess — flag it in
  your summary instead of editing it.

When rewriting a stale docstring:
- Describe what the code does now, not the history of what changed
  unless that history is genuinely useful (follow the existing
  precedent in this codebase of keeping a short note when a past bug
  or decision is worth remembering — don't strip those out
  indiscriminately, only the parts that are factually wrong now).
- Keep the same length/style convention as the rest of the file: one
  line for anything self-explanatory, a short paragraph only where
  behaviour genuinely needs explaining.
- Preserve the blank line between a class's docstring and its first
  method (pydocstyle D204).
- Don't touch wording that's still accurate just because it's nearby.

Do not modify any actual logic — this is a documentation-only pass.
Do not touch roadmap.md, CLAUDE.md, README.md, or dev_guide.md in this
pass — flag anything in them that looks equally stale so it can be
handled separately, since those carry cross-reference numbering rules
(see CLAUDE.md) that need their own dedicated check.

After each file, report:
1. Every docstring/comment you rewrote, with old text -> new text.
2. Anything you found but left alone because you couldn't verify it's
   actually closed, with a reason.

Stop after each file so I can review before moving to the next one.