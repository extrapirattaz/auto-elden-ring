"""Exercise profile decisions, inventory visuals, local scrolling and mini tools."""

from copy import deepcopy
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from auto_elden_ring.ui import App
from auto_elden_ring.history import import_characters
from auto_elden_ring.save_reader import read_save, discover
from auto_elden_ring.windows import snap_position, monitor_workarea
from test_save_reader import fixture
from native_menu_helpers import interact_native_menu


class CompanionFlows(unittest.TestCase):
    def setUp(self):
        self.app = App(persist=False)
        self.app.withdraw()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def create(self):
        a = self.app
        state = a.profiles.create("Demo", "Demo", "Warrior", a.data)
        a.activate_profile(state)
        return a

    def test_empty_picker_and_explicit_profile_selection(self):
        a = self.app
        picker = a.show_profile_picker()
        self.assertEqual(picker.profile_cards, {})
        form = a.new_profile()
        self.assertIs(form.winfo_toplevel(), a)
        form.destroy()
        self.assertIs(picker.winfo_toplevel(), a)
        picker.destroy()
        a = self.create()
        ident = a.profiles.data["active"]
        picker = a.show_profile_picker()
        self.assertEqual(set(picker.profile_cards), {ident})
        picker.profile_cards[ident].invoke()
        self.assertFalse(picker.winfo_exists())
        self.assertEqual(a.page, "character")
        self.assertEqual(a.data["character_name"], "Demo")

    def test_keep_replace_and_failed_import_rollback(self):
        a = self.create()
        ident = a.profiles.data["active"]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ER0000.sl2"
            path.write_bytes(fixture())
            chars = read_save(path, a.db)
            ids = import_characters(a.profiles, chars, a.data)
            self.assertIn(ident, a.profiles.data["profiles"])
            original = deepcopy(a.profiles.data)
            bad = deepcopy(chars)
            bad[0]["class_name"] = "Invalid"
            with self.assertRaises((KeyError, ValueError)):
                import_characters(a.profiles, bad, a.data, replace_manual=True)
            self.assertEqual(a.profiles.data, original)
            import_characters(a.profiles, chars, a.data, replace_manual=True)
            self.assertNotIn(ident, a.profiles.data["profiles"])
            self.assertIn(ids[0], a.profiles.data["profiles"])
            self.assertIn(a.profiles.data["active"], a.profiles.data["profiles"])
            a.profiles.validate()

    def test_initial_import_asks_policy_before_any_mutation(self):
        a = self.create()
        previous = deepcopy(a.profiles.data)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ER0000.sl2"
            path.write_bytes(fixture())
            dialog = a.begin_import(path, policy=None)
            self.assertEqual(a.profiles.data, previous)
            self.assertFalse(getattr(a, "import_in_progress", False))
            dialog.replace_profiles()
            end = time.monotonic() + 10
            while a.import_in_progress and time.monotonic() < end:
                a.update()
                time.sleep(0.01)
            self.assertFalse(a.import_in_progress)
            self.assertTrue(
                all(
                    p["state"]["save_link"]
                    for p in a.profiles.data["profiles"].values()
                    if p["state"]["profile_created"]
                )
            )
            self.assertEqual(len(a.profile_picker.profile_cards), 1)

    def test_installation_discovery_checks_roaming_and_local_saves(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            local = root / "installation/Game"
            roaming = root / "roaming/EldenRing/account"
            local.mkdir(parents=True)
            roaming.mkdir(parents=True)
            (local / "ER0000.co2").write_bytes(b"fixture")
            (roaming / "ER0000.sl2").write_bytes(b"fixture")
            with patch.dict("os.environ", {"APPDATA": str(root / "roaming")}):
                paths = discover(root / "installation")
            self.assertEqual(
                set(paths), {(local / "ER0000.co2").resolve(), (roaming / "ER0000.sl2").resolve()}
            )

    def test_inventory_badges_and_checkpoint_icons(self):
        a = self.create()
        a.data["inventory_weapons"] = [{"name": "Dagger", "current": 6, "quantity": 2}]
        a.show("weapons")
        a.catalogue()
        a.gallery.filter("Dagger")
        a.update()
        badge = a.gallery.ownership_badges["Dagger"]
        self.assertIn("+6 ×2", a.gallery.canvas.itemcget(badge, "text"))
        self.assertEqual(a.gallery.canvas.itemcget(badge, "fill"), "#428DDF")
        point = a.profiles.checkpoint(a.data)
        window = a.checkpoint_detail(point)
        self.assertEqual(window.weapon_cards, {})
        window.render_tab(a.t("owned_weapons"))
        self.assertEqual(set(window.weapon_cards), {("Dagger", 6)})
        window.render_tab(a.t("goal"))
        self.assertEqual(window.weapon_cards, {})
        window.render_tab(a.t("owned_weapons"))
        self.assertEqual(len(window.weapon_cards), 1)

    def test_long_native_dropdown_does_not_move_the_page_on_cancel(self):
        a = self.create()
        a.deiconify()
        a.set_visual_style("style_xp")
        a.show("settings")
        option = a.language_option if hasattr(a, "language_option") else a.style_option
        option.configure(values=[f"Item {i}" for i in range(70)])
        before = a.body._parent_canvas.yview()
        menu = interact_native_menu(a, option, index="wheel")
        self.assertEqual(menu.winfo_class(), "Menu")
        self.assertEqual(menu.index("end"), 69)
        self.assertEqual(a.body._parent_canvas.yview(), before)
        self.assertIsNone(a.scroll_menu)

    def test_compact_stones_timer_and_borderless_snap(self):
        a = self.create()
        a.show("weapons")
        a.manual_vars["target"].set("1")
        a.calculate_weapons()
        window = a.compact_dashboard()
        a.update()
        self.assertTrue(window.overrideredirect())
        window.mode_var.set("weapons")
        window.refresh_summary()
        window.rune_var.set("0")
        self.assertGreater(a.planner.weapons()["stones_cost"], 0)
        window.all_stones()
        self.assertEqual(a.planner.weapons()["stones_cost"], 0)
        self.assertEqual(a.data["runes"], 0)
        self.assertTrue(
            all(row["button"].cget("state") == "disabled" for row in window.purchase_rows.values())
        )
        window.mode_var.set("farm")
        window.refresh_summary()
        window.start_sample()
        a.timer_started = time.monotonic() - 60
        a.deadline = time.monotonic() - 1
        a.tick_timer()
        window.rune_var.set("2400")
        self.assertEqual(window.gain_var.get(), "2400")
        window.record_sample()
        self.assertEqual(a.planner.farm_rates()["measured"], 2400)
        area = monitor_workarea(window)
        self.assertEqual(
            snap_position(area[0] + 5, area[1] + 6, 430, 630, area), (area[0], area[1])
        )
        self.assertEqual(snap_position(-1915, 6, 430, 630, (-1920, 0, 0, 1080)), (-1920, 0))
        window.reopen()
        self.assertEqual(a.data["farm"]["samples"][-1]["runes"], 2400)

    def test_only_three_static_styles_are_available(self):
        from auto_elden_ring.styles import STYLES

        a = self.create()
        a.show("settings")
        self.assertEqual(tuple(STYLES), ("modern", "elden", "xp"))
        self.assertEqual(a.style_option.cget("values"), [a.t("style_" + k) for k in STYLES])
        self.assertFalse(hasattr(a, "rgb_tick"))

    def test_gothic_palettes_keep_pages_without_artwork(self):
        a = self.create()
        a.deiconify()
        a.set_visual_style("style_elden")
        frame = a.views[a.page]["frame"]
        for palette in ("elden", "moon", "ember"):
            a.set_palette(palette)
            a.update()
            a.body._parent_canvas.yview_moveto(0.5)
            a.update()
            self.assertEqual(frame.cget("fg_color"), a.bg)
            self.assertIs(a.views[a.page]["frame"], frame)
        self.assertFalse(hasattr(a, "background_layers"))


class StartupSelection(unittest.TestCase):
    def test_fresh_start_requires_explicit_character_selection(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.dict("os.environ", {"LOCALAPPDATA": folder}),
        ):
            a = App(persist=True)
            try:
                end = time.monotonic() + 0.3
                while time.monotonic() < end:
                    a.update()
                    time.sleep(0.01)
                self.assertEqual(a.profile_picker.profile_cards, {})
                self.assertIs(a.profile_picker.winfo_toplevel(), a)
                self.assertEqual(a.state(), "zoomed")
                self.assertFalse(a.data["profile_created"])
            finally:
                a.close()


if __name__ == "__main__":
    unittest.main()
