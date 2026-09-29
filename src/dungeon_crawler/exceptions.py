"""Custom exceptions.

ActionRefused is raised when the game deliberately refuses something the player asked for - using an item that can't be used, dropping a quest
item, learning a skill with no points. Its message is written for the player, and whatever catches it prints it as-is.

It is deliberately NOT a subclass of ValueError. ValueError is kept for programmer mistakes (invalid constructor arguments) and
Python's own errors (int() failing to parse), so a genuine bug is never caught and shown as though it were an ordinary game message.

Subclasses only where calling code genuinely needs to tell two kinds of refusal apart - none does yet.

SaveFileError is raised by load_game() when a save file exists but can't be read - see its own docstring."""


class ActionRefused(Exception):
    """A player-facing refusal - the message is shown to the player exactly as written."""

class SaveFileError(Exception):
    """A save file exists but can't be read - damaged, hand-edited, or from an incompatible version. Its message is written for the player.
    Separate from ActionRefused: it isn't the game refusing an action, and nothing that handles refusals should ever catch it by accident."""