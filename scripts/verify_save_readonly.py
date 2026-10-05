"""Validate a local PC save without writing it or recording private identifiers."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from auto_elden_ring.core import Database
from auto_elden_ring.history import import_characters
from auto_elden_ring.planner import Planner, default_state
from auto_elden_ring.profiles import Profiles
from auto_elden_ring.save_reader import discover, read_save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    paths = [Path(args.save)] if args.save else discover()
    if len(paths) != 1:
        raise SystemExit("Select a single save using --save.")
    path = paths[0]
    before = path.stat()
    checksum = hashlib.sha256(path.read_bytes()).digest()
    start = time.perf_counter()
    db = Database()
    characters = read_save(path, db)
    profiles = Profiles(db)
    ids = import_characters(profiles, characters, default_state())
    for ident, char in zip(ids, characters):
        state = profiles.select(ident)
        planner = Planner(db, state)
        assert planner.character()["current"] == char["level"]
        assert state["runes"] == char["runes"] and state["stock"] == char["stock"]
        if char["weapons"]:
            name = char["weapons"][0]["name"]
            planner.toggle_weapon(name)
            assert planner.state["selected"][0]["current"] == min(
                i["current"] for i in char["weapons"] if i["name"] == name
            )
    import_characters(profiles, read_save(path, db), default_state())
    assert all(len(profiles.data["profiles"][ident]["checkpoints"]) == 1 for ident in ids)
    after = path.stat()
    unchanged = (
        checksum == hashlib.sha256(path.read_bytes()).digest()
        and before.st_mtime_ns == after.st_mtime_ns
    )
    assert unchanged
    result = {
        "status": "PASS",
        "characters": len(characters),
        "recognized_weapon_variants_per_character": [len(c["weapons"]) for c in characters],
        "armor_variants_per_character": [len(c["armor"]) for c in characters],
        "item_variants_per_character": [len(c["items"]) for c in characters],
        "equipped_slots_per_character": [len(c["equipment"]) for c in characters],
        "unrecognized_items_per_character": [c["unknown_items"] for c in characters],
        "file_sha256_unchanged": True,
        "file_modification_time_unchanged": True,
        "second_import_added_events": 0,
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "privacy": "No character names, account identifiers, paths or save contents recorded.",
    }
    Path(args.report).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
