"""Save/load system - profile and slot management, JSON persistence for Player state and per-room deltas. See roadmap.md's
Save/load system item for the full design."""

import os

PROFILE_LIMIT = 3
SAVE_SLOTS_PER_PROFILE = 5

SAVES_DIR = "saves"


def slot_path(profile_num: int, slot_num: int) -> str:
    """Path to a given profile/slots's save file e.g. saves/profile_1/slot_3.json, Does not create anything - see ensure_profile_dir()."""
    return os.path.join(SAVES_DIR, f"profile_{profile_num}", f"slot_{slot_num}.json")

def ensure_profile_dir(profile_num: int) -> str:
    """Create profile_num's save directory if it doesn't already exist (saves/profile_N/), returning its path. Safe to call every time a save
    happens - exist_ok=True means an existing directory is left untouched."""
    path = os.path.join(SAVES_DIR, f"profile_{profile_num}")
    os.makedirs(path, exist_ok=True)
    return path