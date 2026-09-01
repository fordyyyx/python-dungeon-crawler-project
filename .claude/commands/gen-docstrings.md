Read CLAUDE.md for project context, then add docstrings and comments to
$ARGUMENTS.

Only add docstrings to functions, methods, and classes that don't
already have one — check first, never overwrite an existing docstring.
Follow CLAUDE.md's convention exactly: one line for anything
self-explanatory from its name/signature, a short paragraph only when
behaviour genuinely needs explaining (a non-obvious return shape, a
side effect, a design decision worth knowing). Comments explain *why*,
not *what* — only add one where there's a genuine non-obvious reason
worth capturing, not restating what the code already says.

Always leave one blank line between a class's docstring and its first
method (pydocstyle's D204) — this is the one formatting rule this
project follows; ignore pydocstyle's other stricter opinions (D205,
D209, D400, D401 — mood, punctuation, multi-line blank-line placement).

Do not modify any actual logic — this is a documentation-only pass.

After each file, tell me exactly which functions/classes/methods got
a new docstring and which comments were added, so I can review before
moving to the next file.