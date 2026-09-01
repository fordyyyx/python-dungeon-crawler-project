Read CLAUDE.md for project context, then move the following functions
from $ARGUMENTS (format: "OLD_FILE -> NEW_FILE function_names").

For each function: move it verbatim (do not rewrite logic), add it
to NEW_FILE with correct imports, remove it from OLD_FILE, and add
the correct import back into OLD_FILE for any place OLD_FILE still
calls that function.

Do not create NEW_FILE's tests file, get_skills_display-style method
promotions, or any other restructuring beyond the literal move --
flag anything that looks like it needs a design decision instead of
guessing.

Tell me every call site you updated, so I can verify none were missed.