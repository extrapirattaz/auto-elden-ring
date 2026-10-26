"""Verify the one-window navigation contract and retired preference migration."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from auto_elden_ring.ui import App
from auto_elden_ring.profiles import Profiles


class InWindowFlows(unittest.TestCase):
    def setUp(self):
        self.app = App(persist=False)
        state = self.app.profiles.create("Demo", "Demo", "Warrior", self.app.data)
        self.app.activate_profile(state)
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def test_navigation_forms_catalogue_and_details_share_one_native_window(self):
        a = self.app
        native = a.winfo_id()
        picker = a.show_profile_picker()
        form = a.new_profile()
        self.assertIs(form.winfo_toplevel(), a)
        form.back.invoke()
        self.assertTrue(picker.winfo_exists())
        picker.back.invoke()
        a.show("weapons")
        a.catalogue()
        self.assertIs(a.gallery_window.winfo_toplevel(), a)
        a.gallery_window.back.invoke()
        self.assertFalse(a.gallery_window.winfo_exists())
        details = a.equipment_view()
        self.assertIs(details.winfo_toplevel(), a)
        details.back.invoke()
        self.assertEqual(a.winfo_id(), native)
        self.assertFalse(any(w.winfo_class() == "Toplevel" for w in a.winfo_children()))
        self.assertEqual(a.callback_errors, [])

    def test_dropdown_is_dismissed_by_move_and_navigation_without_selection(self):
        a = self.app
        a.show("settings")
        a.update()
        changes = []
        a.language_option.configure(command=changes.append)
        menu = a.language_option._dropdown_menu
        # Posting is covered by the native-input tests. Here exercise the owner
        # cancellation hooks without entering the blocking Windows tracking loop.
        with patch.object(menu, "tk_popup"):
            a.open_native_menu(a.language_option)
            self.assertEqual(menu.winfo_class(), "Menu")
            a.geometry("1280x860+200+100")
            a.update()
            self.assertIsNone(a.scroll_menu)
            a.open_native_menu(a.language_option)
            a.navigate("farm")
            self.assertIsNone(a.scroll_menu)
        self.assertTrue(menu.winfo_exists())
        self.assertEqual(changes, [])

    def test_retired_background_is_removed_without_losing_profile_data(self):
        from auto_elden_ring.storage import upgrade_state

        a = self.app
        old = dict(a.data, custom_background="old-decoration.png", style="rainbow", theme="prism")
        a.profiles.active["state"] = old
        a.profiles.validate()
        migrated = a.profiles.active["state"]
        self.assertEqual(migrated["style"], "ledger")
        self.assertNotIn("theme", migrated)
        self.assertNotIn("custom_background", migrated)
        self.assertEqual(migrated["character_name"], "Demo")
        self.assertEqual(
            upgrade_state(dict(a.data, style="modern", theme="calm"))["style"], "readable"
        )
        self.assertEqual(
            upgrade_state(dict(a.data, style="xp", theme="xp_blue"))["style"], "readable"
        )
        a.show("settings")
        self.assertFalse(hasattr(a, "background_actions"))
        self.assertFalse(hasattr(a, "theme_option"))

    def test_equipment_overview_does_not_list_all_upgraded_weapons(self):
        a = self.app
        a.data["inventory_weapons"] = [
            {"name": "Dagger", "current": 6, "quantity": 2},
            {"name": "Black Knife", "current": 4, "quantity": 1},
        ]
        a.data["equipment"] = [
            {"id": 1000006, "slot": 1, "quantity": 1, "name": "Dagger", "current": 6}
        ]
        a.data["inventory_armor"] = [{"id": 0x100249F0, "quantity": 2}]
        a.data["inventory_items"] = [{"id": 0x40000000 | 8951, "quantity": 1}]
        view = a.equipment_view()
        self.assertEqual(set(view.weapon_cards), {("Dagger", 6)})
        view.render_tab(a.t("owned_weapons"))
        self.assertEqual(len(view.weapon_cards), 2)
        view.render_tab(a.t("armor"))
        self.assertEqual(view.weapon_cards, {})
        view.render_tab(a.t("items"))
        self.assertTrue(a.item_icons)
        self.assertLessEqual(len(a.item_icons), 64)


class FreshPublicStart(unittest.TestCase):
    def test_future_profiles_survive_restart_after_clean_first_start(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict("os.environ", {"LOCALAPPDATA": directory}),
        ):
            a = App(persist=True)
            try:
                a.update()
                self.assertEqual(a.state(), "zoomed")
                self.assertEqual(a.profile_picker.profile_cards, {})
                self.assertEqual(a.sidebar.winfo_manager(), "")
                self.assertFalse(any(w.winfo_class() == "Toplevel" for w in a.winfo_children()))
                state = a.profiles.create("Persistent demo", "Persistent demo", "Warrior", a.data)
                a.activate_profile(state)
                self.assertEqual(a.sidebar.winfo_manager(), "grid")
            finally:
                a.close()
            a = App(persist=True)
            try:
                self.assertEqual(len(a.profile_picker.profile_cards), 1)
                self.assertEqual(a.data["character_name"], "Persistent demo")
            finally:
                a.close()
