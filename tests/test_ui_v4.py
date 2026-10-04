"""Exercise profile-first workflows and retained widgets with real Tk controls."""
from copy import deepcopy
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from auto_elden_ring.ui import App
from auto_elden_ring.history import import_characters
from auto_elden_ring.save_reader import read_save
from auto_elden_ring.styles import STYLES
from test_save_reader import fixture


class ProgressInterface(unittest.TestCase):
    def setUp(self):
        self.app=App(persist=False)
        self.app.withdraw()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def create(self):
        a=self.app
        state=a.profiles.create("Test Tarnished","Ignored journey label","Warrior",a.data)
        a.activate_profile(state)
        return a

    def test_initial_empty_journal_and_named_immutable_class(self):
        a=self.app
        a.show("journal")
        self.assertIsNone(a.timeline)
        self.create()
        a.show("journal")
        self.assertIsNotNone(a.timeline)
        self.assertEqual(len(a.timeline.find_all()),1)
        self.assertEqual(a.data["journey_name"],"Test Tarnished")
        a.show("character")
        self.assertEqual(a.class_option.cget("state"),"disabled")
        a.set_class("Wretch")
        self.assertEqual(a.data["class_name"],"Warrior")

    def test_custom_event_derives_level_and_keeps_live_attributes(self):
        a=self.create()
        a.show("journal")
        dialog=a.event_dialog()
        custom=a.custom_event(dialog,"Progress","03/10/2026 12:30")
        custom.stat_vars["vigor"].set("60")
        custom.weapon_choice.set(a.translator.weapon("Dagger"))
        custom.weapon_upgrade.set("6")
        custom.add_weapon()
        custom.save_event()
        point=a.profiles.active["checkpoints"][0]
        self.assertEqual(sum(point["state"]["stats_current"].values())-79,57)
        self.assertEqual(a.data["stats_current"]["vigor"],11)
        self.assertEqual(point["state"]["inventory_weapons"],[{"name":"Dagger","current":6,"quantity":1}])
        self.assertEqual(a.callback_errors,[])

    def test_import_refresh_keeps_selected_slot_and_no_duplicate_event(self):
        a=self.app
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"ER0000.sl2"
            path.write_bytes(fixture())
            chars=read_save(path,a.db)
            other=deepcopy(chars[0])
            other.update(slot=1,name="Second fixture",fingerprint="second")
            chars.append(other)
            ids=import_characters(a.profiles,chars,a.data)
            a.activate_profile(a.profiles.select(ids[1]))
            with patch("auto_elden_ring.ui_v4.read_save",return_value=chars):
                a.begin_import(path)
                until=time.monotonic()+5
                while time.monotonic()<until and a.import_in_progress:
                    a.update()
                    time.sleep(.02)
            self.assertEqual(a.profiles.data["active"],ids[1])
            self.assertEqual(len(a.profiles.active["checkpoints"]),1)
            self.assertEqual(a.data["runes"],12345)
            self.assertEqual(a.data["inventory_weapons"][0]["current"],6)
            self.assertEqual(a.page,"character")

    def test_upgrade_records_event_and_preserves_other_owned_copies(self):
        a=self.create()
        a.data["inventory_weapons"]=[{"name":"Dagger","current":0,"quantity":2}]
        a.data["weapon_mode"]="catalogue"
        a.planner.toggle_weapon("Dagger")
        a.show("weapons")
        a.selected_vars[0][1]["target"].set("12")
        with patch("auto_elden_ring.ui.messagebox.askyesno",return_value=True):
            a.complete_upgrades()
        self.assertEqual(sorted((i["current"],i["quantity"]) for i in a.data["inventory_weapons"]),[(0,1),(12,1)])
        point=a.profiles.active["checkpoints"][-1]
        self.assertEqual(point["note"],"upgrade_event")
        self.assertTrue(point["changes"])
        self.assertEqual(a.data["runes"],0)
        a.show("journal")
        self.assertGreater(len(a.timeline.find_all()),1)

    def test_named_farm_spot_and_compact_wallet(self):
        a=self.create()
        a.show("farm")
        a.farm_vars["runes"].set("1000")
        dialog=a.save_farm_spot()
        dialog.spot_name.set("Palace route")
        dialog.save_spot()
        a.data["farm"]["runes"]=123
        a.select_farm_spot("Palace route")
        self.assertEqual(a.planner.farm_rates()["measured"],1000)
        a.compact_mode()
        window=a.compact_window
        a.update()
        self.assertTrue(window.winfo_viewable())
        self.assertFalse(a.winfo_viewable())
        self.assertEqual(len(a.views),1)
        window.rune_var.set("500")
        self.assertEqual(a.data["runes"],500)
        window.mode_var.set("farm")
        window.refresh_summary()
        self.assertIn(f'{a.planner.farm_projection()["remaining"]:,}',window.summary_label.cget("text"))
        window.reopen()
        self.assertFalse(window.winfo_exists())
        self.assertEqual(a.data["farm_spots"][0]["name"],"Palace route")

    def test_palette_surfaces_and_language_do_not_replace_pages(self):
        a=self.app
        for page in ("character","weapons","stones","farm","journal","settings"):
            a.show(page)
        frames={key:value["frame"] for key,value in a.views.items()}
        for style,spec in STYLES.items():
            a.set_visual_style("style_"+style)
            for palette in spec["themes"]:
                a.set_palette(palette)
                self.assertEqual(a.weapon_form.cget("fg_color"),a.paper)
                self.assertEqual(a.weapon_form.cget("bg_color"),a.bg)
                self.assertEqual(a.views["stones"]["body"]._parent_canvas.cget("bg"),a.bg)
                self.assertEqual(a.views["stones"]["body"].tk.call(a.views["stones"]["body"]._w,"cget","-bg"),a.bg)
        for language in ("fr","ja","en"):
            a.set_language(language)
        self.assertEqual({key:value["frame"] for key,value in a.views.items()},frames)
        self.assertEqual(a.callback_errors,[])

    def test_reading_font_does_not_grow_and_rgb_stops(self):
        a=self.app
        a.show("settings")
        frame=a.views["settings"]["frame"]
        for _ in range(4):
            a.dyslexic_var.set(True)
            a.set_reading_mode()
            self.assertEqual(a.brand.cget("font").cget("size"),26)
            a.dyslexic_var.set(False)
            a.set_reading_mode()
            self.assertEqual(a.brand.cget("font").cget("size"),24)
        a.set_visual_style("style_rainbow")
        self.assertIsNotNone(a.rgb_job)
        a.set_visual_style("style_modern")
        self.assertIsNone(a.rgb_job)
        self.assertIs(a.views["settings"]["frame"],frame)

    def test_elden_background_is_reused_on_move_and_stays_at_scroll_viewport(self):
        a=self.app
        a.deiconify()
        a.show("stones")
        a.set_visual_style("style_elden")
        a.update()
        a.paint_background()
        layers=tuple(a.background_layers)
        a.geometry("1280x860+350+80")
        a.update()
        a.paint_background()
        self.assertEqual(tuple(a.background_layers),layers)
        body=a.views["stones"]["body"]
        body._parent_canvas.yview_moveto(.4)
        a.update()
        self.assertEqual(int(body._background_layer.place_info()["y"]),int(body._parent_canvas.canvasy(0)))
        self.assertEqual(tuple(a.background_layers),layers)
