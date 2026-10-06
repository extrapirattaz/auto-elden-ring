"""Background, read-only synchronization of remembered PC save locations."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import time
import tkinter as tk

from .history import import_characters
from .save_reader import discover, read_saves


def saved_paths(library):
    """Discover new saves only after the user has opted into importing the game."""
    sources = set(library.get("save_sources", []))
    sources.update(
        p["state"]["save_link"]["path"]
        for p in library["profiles"].values()
        if p["state"]["save_link"].get("path")
    )
    folder = library.get("installation_folder", "")
    if not sources and not folder:
        return []
    paths = {Path(p).resolve() for p in sources if Path(p).is_file()}
    paths.update(discover(folder or None))
    # Linked custom directories can also acquire an additional .sl2/.co2 file.
    for source in sources:
        for pattern in ("*.sl2", "*.co2"):
            paths.update(p.resolve() for p in Path(source).parent.glob(pattern) if p.is_file())
    return sorted(paths)


def read_remembered(library, db):
    paths = saved_paths(library)
    if not paths:
        raise ValueError("Remembered save files are unavailable.")
    # A save can be replaced while the game autosaves. Bounded retries run only
    # on the worker; read_save verifies size, timestamps and all slot checksums.
    for attempt in range(3):
        try:
            return read_saves(paths, db), paths
        except OSError, ValueError:
            if attempt == 2:
                raise
            time.sleep(0.15 * (attempt + 1))


class SaveSync:
    def remember_sources(self, paths):
        previous = self.profiles.data.get("save_sources", [])
        merged = sorted(set(previous) | {str(Path(p).resolve()) for p in paths})
        if len(merged) > 20:
            raise ValueError("At most twenty save files can be remembered.")
        self.profiles.data["save_sources"] = merged

    def scan_status(self, key, **values):
        self.scan_message = self.t(key, **values)
        self.scan_message_key = (key, values)
        for label in (
            getattr(self, "rescan_status", None),
            getattr(getattr(self, "profile_picker", None), "rescan_status", None),
        ):
            if label is not None and label.winfo_exists():
                label.configure(text=self.scan_message)

    def rescan_game(self, startup=False):
        if self._closing or getattr(self, "import_in_progress", False):
            return
        linked = any(p["state"]["save_link"] for p in self.profiles.data["profiles"].values())
        if (
            not linked
            and not self.profiles.data.get("save_sources")
            and not self.profiles.data.get("installation_folder")
        ):
            if not startup:
                self.import_dialog()
            return
        try:
            self.commit_current()
            self.profiles.sync(self.data)
        except ValueError, tk.TclError:
            self.scan_status("scan_invalid")
            return
        if not hasattr(self, "reader_pool"):
            self.reader_pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="save-reader")
        self.import_in_progress = True
        self.rescan_button.configure(state="disabled")
        self.scan_status("importing")
        # The reader needs locations, not thousands of historical snapshots.
        locations = {
            "save_sources": list(self.profiles.data.get("save_sources", [])),
            "installation_folder": self.profiles.data.get("installation_folder", ""),
            "profiles": {
                i: {"state": {"save_link": dict(p["state"]["save_link"])}}
                for i, p in self.profiles.data["profiles"].items()
            },
        }
        self.scan_future = self.reader_pool.submit(read_remembered, locations, self.db)

        def poll():
            if self._closing:
                return
            if not self.scan_future.done():
                self.after(80, poll)
                return
            try:
                characters, paths = self.scan_future.result()
                # Commit again: the user may have edited a goal or switched
                # characters while reading. Merge into that current library.
                self.commit_current()
                self.profiles.sync(self.data)
                merged = set(self.profiles.data.get("save_sources", [])) | {str(p) for p in paths}
                if len(merged) > 20:
                    raise ValueError("At most twenty save files can be remembered.")
                counts = sum(len(p["checkpoints"]) for p in self.profiles.data["profiles"].values())
                import_characters(self.profiles, characters, self.data)
                self.remember_sources(paths)
                added = (
                    sum(len(p["checkpoints"]) for p in self.profiles.data["profiles"].values())
                    - counts
                )
                self.data.update(deepcopy(self.profiles.active["state"]))
                self.refresh_scanned_controls()
                self.autosave()
                self.scan_status("scan_done", count=len(characters), events=added)
            except OSError, ValueError, KeyError, tk.TclError:
                # Keep the previous snapshot and goals intact. The same button
                # can retry after a running game's next completed autosave.
                self.scan_status("scan_failed")
            finally:
                self.import_in_progress = False
                if not self._closing:
                    self.rescan_button.configure(state="normal")

        self.after(80, poll)

    def refresh_scanned_controls(self):
        """Refresh current values without recreating the window or calculator pages."""
        self._refreshing_scan = True
        try:
            for (section, stat), variable in getattr(self, "stat_vars", {}).items():
                variable.set(str(self.data[section][stat]))
        finally:
            self._refreshing_scan = False
        for variable in self.wallet_vars.values():
            variable.set(str(self.data["runes"]))
        if hasattr(self, "class_option"):
            self.class_option._enum_current = self.data["class_name"]
            self.class_option.set(self.t(self.data["class_name"]))
        refreshed = []
        for old, variables in getattr(self, "selected_vars", []):
            item = next(i for i in self.data["selected"] if i["name"] == old["name"])
            for key, variable in variables.items():
                variable.set(str(item[key]))
            refreshed.append((item, variables))
        if hasattr(self, "selected_vars"):
            self.selected_vars = refreshed
        self.profile_button.configure(
            text=(
                self.data["character_name"]
                if self.data["profile_created"]
                else self.t("switch_character")
            )
        )
        self.refresh_character()
        self.refresh_weapons()
        self.refresh_farm_results()
        if self.page == "journal":
            self.draw_timeline()
        picker = getattr(self, "profile_picker", None)
        if picker is not None and picker.winfo_exists():
            self.populate_profile_cards(picker)
        gallery = getattr(self, "gallery_window", None)
        if gallery is not None and gallery.winfo_exists():
            self.gallery.reflow()
        compact = getattr(self, "compact_window", None)
        if compact is not None and compact.winfo_exists():
            compact.rune_var.set(str(self.data["runes"]))
            compact.refresh_summary()
