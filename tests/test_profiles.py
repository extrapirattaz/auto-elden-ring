"""Profile isolation, immutable checkpoints and old-project migration."""

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from auto_elden_ring.core import Database
from auto_elden_ring.planner import default_state
from auto_elden_ring.profiles import Profiles
from auto_elden_ring.storage import save_project, load_project


class Journals(unittest.TestCase):
    def test_legacy_unnamed_placeholder_does_not_create_a_character(self):
        profiles = Profiles(self.db)
        state = profiles.active["state"]
        for key in ("profile_created", "save_link", "inventory_weapons", "farm_spots"):
            state.pop(key)
        profiles.validate()
        self.assertFalse(profiles.active["state"]["profile_created"])

    def setUp(self):
        self.db = Database()

    def test_independent_profiles_and_immutable_sorted_timeline(self):
        profiles = Profiles(self.db)
        first = profiles.data["active"]
        state = profiles.create("Mage", "Journey 2", "Astrologer", default_state())
        early = profiles.checkpoint(state, "Early", "2025-01-01T10:00:00+01:00")
        state["stats_current"]["vigor"] = 50
        profiles.checkpoint(state, "Later", "2026-01-01T10:00:00+01:00")
        self.assertNotEqual(early["state"]["stats_current"]["vigor"], 50)
        self.assertEqual(profiles.active["checkpoints"][0]["note"], "Early")
        self.assertEqual(profiles.select(first)["character_name"], "Tarnished")

    def test_atomic_library_roundtrip(self):
        profiles = Profiles(self.db)
        state = default_state()
        profiles.checkpoint(state)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "profiles.json"
            profiles.save(path, state)
            restored = Profiles.load(path, self.db)
            self.assertEqual(restored.data, profiles.data)

    def test_v2_project_migration(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "project.json"
            save_project(path, default_state(), self.db)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["schema"] = 2
            for key in (
                "style",
                "dyslexic",
                "character_name",
                "journey_name",
                "music_file",
                "purchased",
            ):
                data["state"].pop(key)
            path.write_text(json.dumps(data), encoding="utf-8")
            state = load_project(path, self.db)
            self.assertEqual(state["style"], "modern")
            self.assertEqual(state["purchased"], {})
