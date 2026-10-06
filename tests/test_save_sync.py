"""Read-only rescans preserve plans, windows and meaningful timeline history."""

from copy import deepcopy
import hashlib
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from auto_elden_ring.core import Database
from auto_elden_ring.history import import_characters
from auto_elden_ring.planner import default_state
from auto_elden_ring.profiles import Profiles
from auto_elden_ring.save_reader import read_save, STRIDE
from auto_elden_ring.save_sync import read_remembered, saved_paths
from auto_elden_ring.ui import App
from test_save_reader import fixture


class SaveSyncTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = Path(self.folder.name) / "ER0000.sl2"
        self.path.write_bytes(fixture(gear=True))
        self.db = Database()
        self.characters = read_save(self.path, self.db)
        self.profiles = Profiles(self.db)
        self.ids = import_characters(self.profiles, self.characters, default_state())
        self.profiles.select(self.ids[0])

    def tearDown(self):
        self.folder.cleanup()

    def test_source_registry_survives_restart_and_finds_added_files(self):
        library = self.profiles.data
        library["installation_folder"] = self.folder.name
        library["save_sources"] = [str(self.path)]
        store = Path(self.folder.name) / "profiles.json"
        self.profiles.save(store, self.profiles.active["state"])
        loaded = Profiles.load(store, self.db)
        additional = self.path.with_suffix(".co2")
        additional.write_bytes(self.path.read_bytes())
        with patch("auto_elden_ring.save_sync.discover", return_value=[]):
            paths = saved_paths(loaded.data)
            before = {
                p: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in paths
            }
            characters, scanned = read_remembered(loaded.data, self.db)
        self.assertEqual(set(paths), {self.path, additional})
        self.assertEqual(scanned, paths)
        self.assertEqual(len(characters), 2)
        self.assertEqual(
            before,
            {p: (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns) for p in paths},
        )
        self.assertEqual(loaded.data["installation_folder"], self.folder.name)

    def test_transient_save_write_retries_are_bounded(self):
        with (
            patch("auto_elden_ring.save_sync.discover", return_value=[]),
            patch("auto_elden_ring.save_sync.time.sleep") as sleep,
        ):
            with patch(
                "auto_elden_ring.save_sync.read_saves",
                side_effect=[OSError("busy"), ValueError("changing"), self.characters],
            ) as reader:
                self.assertEqual(read_remembered(self.profiles.data, self.db)[0], self.characters)
                self.assertEqual(reader.call_count, 3)
                self.assertEqual(sleep.call_count, 2)
            with patch(
                "auto_elden_ring.save_sync.read_saves", side_effect=ValueError("corrupt")
            ) as reader:
                with self.assertRaises(ValueError):
                    read_remembered(self.profiles.data, self.db)
                self.assertEqual(reader.call_count, 3)

    def test_only_meaningful_progress_creates_an_event(self):
        changed = deepcopy(self.characters)
        changed[0]["fingerprint"] = "opaque-playtime-change"
        import_characters(self.profiles, changed, self.profiles.active["state"])
        self.assertEqual(len(self.profiles.active["checkpoints"]), 1)
        changed[0].update(runes=40000, fingerprint="rune-change")
        import_characters(self.profiles, changed, self.profiles.active["state"])
        self.assertEqual(len(self.profiles.active["checkpoints"]), 2)
        import_characters(self.profiles, changed, self.profiles.active["state"])
        self.assertEqual(len(self.profiles.active["checkpoints"]), 2)
        changed[0]["equipment"] = []
        changed[0]["fingerprint"] = "equipment-change"
        import_characters(self.profiles, changed, self.profiles.active["state"])
        self.assertEqual(len(self.profiles.active["checkpoints"]), 3)
        self.assertEqual(
            self.profiles.active["checkpoints"][-1]["changes"][0]["field"], "equipment"
        )

    def test_identical_rescan_accepts_disk_values_without_an_event(self):
        state = deepcopy(self.profiles.active["state"])
        state["runes"] = 999999
        state["stock"] = {key: 0 for key in state["stock"]}
        state["stats_target"]["vigor"] = 60
        self.profiles.sync(state)
        import_characters(self.profiles, self.characters, state)
        refreshed = self.profiles.active["state"]
        self.assertEqual(refreshed["runes"], self.characters[0]["runes"])
        self.assertEqual(refreshed["stock"], self.characters[0]["stock"])
        self.assertEqual(refreshed["stats_target"]["vigor"], 60)
        self.assertEqual(len(self.profiles.active["checkpoints"]), 1)

    def test_binary_only_change_is_accepted_without_a_timeline_event(self):
        binary = bytearray(self.path.read_bytes())
        binary[0x300 + STRIDE - 1] = 1
        slot = binary[0x310 : 0x300 + STRIDE]
        binary[0x300:0x310] = hashlib.md5(slot).digest()
        self.path.write_bytes(binary)
        latest = read_save(self.path, self.db)
        self.assertNotEqual(latest[0]["fingerprint"], self.characters[0]["fingerprint"])
        import_characters(self.profiles, latest, self.profiles.active["state"])
        self.assertEqual(len(self.profiles.active["checkpoints"]), 1)
        self.assertEqual(
            self.profiles.active["state"]["save_link"]["fingerprint"], latest[0]["fingerprint"]
        )

    def test_latest_accepted_save_survives_restart_without_empty_events(self):
        latest = deepcopy(self.characters)
        latest[0]["fingerprint"] = "latest-opaque-bytes"
        import_characters(self.profiles, latest, self.profiles.active["state"])
        store = Path(self.folder.name) / "profiles.json"
        self.profiles.save(store, self.profiles.active["state"])
        loaded = Profiles.load(store, self.db)
        self.assertEqual(loaded.active["state"]["save_link"]["fingerprint"], "latest-opaque-bytes")
        self.assertEqual(loaded.active["last_import"]["runes"], latest[0]["runes"])
        import_characters(loaded, latest, loaded.active["state"])
        self.assertEqual(len(loaded.active["checkpoints"]), 1)
        # Progress comparisons remain independent of the binary identity marker.
        latest[0]["runes"] += 100
        import_characters(loaded, latest, loaded.active["state"])
        self.assertEqual(len(loaded.active["checkpoints"]), 2)
        self.assertEqual(
            loaded.active["checkpoints"][-1]["changes"],
            [
                {
                    "field": "runes",
                    "before": self.characters[0]["runes"],
                    "after": latest[0]["runes"],
                }
            ],
        )

    def test_latest_import_baseline_is_independent_of_timeline_dates(self):
        latest = deepcopy(self.characters)
        latest[0].update(runes=40000, fingerprint="progress")
        import_characters(self.profiles, latest, self.profiles.active["state"])
        point = self.profiles.active["checkpoints"][-1]
        point["date"] = "2000-01-01T00:00:00+00:00"
        self.profiles.active["checkpoints"].sort(key=lambda item: item["date"])
        latest[0]["fingerprint"] = "playtime-only"
        import_characters(self.profiles, latest, self.profiles.active["state"])
        self.assertEqual(len(self.profiles.active["checkpoints"]), 2)

    def wait_scan(self, app):
        end = time.monotonic() + 12
        while getattr(app, "import_in_progress", False) and time.monotonic() < end:
            app.update()
            time.sleep(0.01)
        self.assertFalse(getattr(app, "import_in_progress", False))

    def test_manual_scan_updates_calculators_without_reopening_and_keeps_goals(self):
        app = App(persist=False)
        try:
            app.profiles = self.profiles
            app.activate_profile(self.profiles.select(self.ids[0]))
            app.stat_vars["stats_target", "vigor"].set("60")
            app.commit_current()
            frames = {k: v["frame"] for k, v in app.views.items()}
            native = app.winfo_id()
            changed = deepcopy(self.characters)
            changed[0].update(runes=50000, fingerprint="new-progress")
            changed[0]["stats"]["vigor"] += 5
            changed[0]["stats"]["dexterity"] += 2
            with patch(
                "auto_elden_ring.save_sync.read_remembered", return_value=(changed, [self.path])
            ):
                app.rescan_game()
                app.rescan_game()  # A second click cannot queue a competing import.
                self.wait_scan(app)
            self.assertEqual(app.data["runes"], 50000)
            self.assertEqual(app.data["stats_target"]["vigor"], 60)
            self.assertEqual(app.data["stats_current"], changed[0]["stats"])
            self.assertEqual(app.wallet_vars["character"].get(), "50000")
            self.assertEqual(app.winfo_id(), native)
            self.assertEqual({k: v["frame"] for k, v in app.views.items()}, frames)
            self.assertEqual(len(app.profiles.active["checkpoints"]), 2)
            self.assertEqual(app.callback_errors, [])
        finally:
            app.destroy()

    def test_failed_scan_preserves_profiles_and_allows_retry(self):
        app = App(persist=False)
        try:
            app.profiles = self.profiles
            app.activate_profile(self.profiles.select(self.ids[0]))
            app.commit_current()
            app.profiles.sync(app.data)
            before = deepcopy(app.profiles.data)
            with patch(
                "auto_elden_ring.save_sync.read_remembered", side_effect=ValueError("writing")
            ):
                app.rescan_game()
                self.wait_scan(app)
            self.assertEqual(app.profiles.data, before)
            self.assertEqual(app.rescan_button.cget("state"), "normal")
            self.assertEqual(app.scan_message_key[0], "scan_failed")
            self.assertEqual(app.callback_errors, [])
        finally:
            app.destroy()

    def test_startup_rescans_saved_link_and_keeps_character_chooser(self):
        local = Path(self.folder.name) / "local"
        self.profiles.save(local / "AutoEldenRing/profiles-v3.json", self.profiles.active["state"])
        changed = deepcopy(self.characters)
        changed[0].update(runes=60000, fingerprint="startup-progress")
        with (
            patch.dict("os.environ", {"LOCALAPPDATA": str(local)}),
            patch("auto_elden_ring.save_sync.read_remembered", return_value=(changed, [self.path])),
        ):
            app = App(persist=True)
            try:
                picker = app.profile_picker
                end = time.monotonic() + 12
                while (
                    getattr(app, "scan_message_key", (None,))[0] != "scan_done"
                    and time.monotonic() < end
                ):
                    app.update()
                    time.sleep(0.01)
                self.assertEqual(app.scan_message_key[0], "scan_done")
                self.assertIs(app.profile_picker, picker)
                self.assertTrue(app.profile_selection_pending)
                self.assertTrue(picker.winfo_exists())
                self.assertEqual(app.data["runes"], 60000)
                self.assertEqual(len(app.profiles.active["checkpoints"]), 2)
                self.assertEqual(app.callback_errors, [])
            finally:
                app.close()
