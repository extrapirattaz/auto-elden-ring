"""Remove this application's local test profiles, never the game's save files.

Run explicitly with --confirm before handing a test PC to another user. Public
builds never run this automatically: future users keep their saved characters.
Unknown files in the directory are preserved rather than recursively deleted.
"""

import argparse
import os
from pathlib import Path

LOCAL_FILES = ("profiles-v3.json", "session-v2.json", "session.json")


def reset_local_data(local_root):
    directory = (Path(local_root) / "AutoEldenRing").resolve()
    if directory.parent != Path(local_root).resolve():
        raise ValueError("The application directory points outside LOCALAPPDATA.")
    removed = []
    for name in LOCAL_FILES:
        path = directory / name
        # Refuse a redirected file outside the explicitly named app directory.
        if path.is_symlink() or path.resolve().parent != directory:
            raise ValueError("A local-data path points outside the application directory.")
        if path.is_file():
            path.unlink()
            removed.append(name)
    return removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    if not args.confirm:
        parser.error("Close Auto Elden Ring and pass --confirm to remove its local profiles.")
    root = os.environ.get("LOCALAPPDATA")
    if not root:
        raise SystemExit("LOCALAPPDATA is not available.")
    removed = reset_local_data(root)
    print(f"Local application reset complete: {len(removed)} state file(s) removed.")


if __name__ == "__main__":
    main()
