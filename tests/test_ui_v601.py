"""Native menu selection and appearance changes must retain a visible window."""

import ctypes
from ctypes import wintypes
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from auto_elden_ring.ui import App
from auto_elden_ring.dropdown import NativeOptionMenu
from scripts.reset_local_data import reset_local_data
from native_menu_helpers import interact_native_menu


class NativeMenusAndAppearance(unittest.TestCase):
    def setUp(self):
        self.app = App(persist=False)
        state = self.app.profiles.create(
            "Test character", "Test character", "Warrior", self.app.data
        )
        self.app.activate_profile(state)
        self.app.show("settings")
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def test_native_clicks_apply_each_setting_once_and_escape_does_not_select(self):
        a = self.app
        native = a.winfo_id()
        controls = (a.style_option, a.theme_option, a.language_option)
        for option in controls:
            self.assertIsInstance(option, NativeOptionMenu)
            command = option.cget("command")
            changes = []

            def selected(value, fn=command, events=changes):
                events.append(value)
                fn(value)

            option.configure(command=selected)
            interact_native_menu(a, option, index=1)
            self.assertEqual(len(changes), 1)
            value = option.get()
            interact_native_menu(a, option)
            self.assertEqual(changes, [value])
            self.assertEqual(a.winfo_id(), native)
            self.assertTrue(a.winfo_viewable())
        self.assertEqual(a.callback_errors, [])

    def test_native_keyboard_selection_changes_language(self):
        a = self.app
        interact_native_menu(a, a.language_option, index="keyboard:2")
        self.assertEqual(a.data["language"], "cs")
        self.assertIsNone(a.scroll_menu)

    def test_hidden_page_fonts_update_when_shown_without_rebuilding_controls(self):
        a = self.app
        frame = a.views["character"]["frame"]
        a.dyslexic_var.set(True)
        a.set_reading_mode()
        a.show("character")
        self.assertIs(a.views["character"]["frame"], frame)
        self.assertEqual(a.level_label.cget("font").cget("family"), "OpenDyslexic")
        a.show("settings")
        a.dyslexic_var.set(False)
        a.set_reading_mode()
        a.show("character")
        self.assertIs(a.views["character"]["frame"], frame)
        self.assertEqual(a.level_label.cget("font").cget("family"), "Segoe UI")
        self.assertEqual(a.level_label.cget("font").cget("size"), 18)

    def test_reading_language_and_palette_keep_native_visibility_and_control_identity(self):
        a = self.app
        user = ctypes.windll.user32
        user.GetParent.argtypes = [wintypes.HWND]
        user.GetParent.restype = wintypes.HWND
        user.IsWindowVisible.argtypes = [wintypes.HWND]
        hwnd = user.GetParent(a.winfo_id())
        controls = (a.style_option, a.theme_option, a.language_option, a.reading_check)
        visibility = []
        original = a.update_controls_appearance

        def inspect_during_change():
            visibility.append(bool(user.IsWindowVisible(hwnd)))
            original()
            visibility.append(bool(user.IsWindowVisible(hwnd)))

        with patch.object(a, "update_controls_appearance", inspect_during_change):
            for style in ("style_elden", "style_xp", "style_modern"):
                a.set_visual_style(style)
                a.reading_check.toggle()
                a.update()
                a.reading_check.toggle()
                a.update()
        self.assertTrue(all(visibility))
        self.assertEqual(
            controls, (a.style_option, a.theme_option, a.language_option, a.reading_check)
        )
        self.assertEqual(user.GetParent(a.winfo_id()), hwnd)
        self.assertEqual(a.callback_errors, [])


class LocalReset(unittest.TestCase):
    def test_reset_removes_only_app_state_and_preserves_unknown_files_and_game_saves(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            app = root / "AutoEldenRing"
            app.mkdir()
            for name in ("profiles-v3.json", "session-v2.json", "session.json"):
                (app / name).write_text("{}")
            unrelated = app / "keep.txt"
            unrelated.write_text("keep")
            save = root / "EldenRing" / "ER0000.sl2"
            save.parent.mkdir()
            save.write_bytes(b"untouched game save")
            self.assertEqual(len(reset_local_data(root)), 3)
            self.assertEqual(unrelated.read_text(), "keep")
            self.assertEqual(save.read_bytes(), b"untouched game save")
            self.assertEqual(reset_local_data(root), [])
