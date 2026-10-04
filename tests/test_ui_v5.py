"""Exercise profile decisions, inventory visuals, local scrolling and mini tools."""
from copy import deepcopy
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
from auto_elden_ring.ui import App
from auto_elden_ring.history import import_characters
from auto_elden_ring.save_reader import read_save,discover
from auto_elden_ring.windows import snap_position,monitor_workarea
from test_save_reader import fixture


class CompanionFlows(unittest.TestCase):
    def setUp(self):
        self.app=App(persist=False)
        self.app.withdraw()
        self.app.update()

    def tearDown(self):
        self.app.destroy()

    def create(self):
        a=self.app
        state=a.profiles.create("Demo","Demo","Warrior",a.data)
        a.activate_profile(state)
        return a

    def test_empty_picker_and_explicit_profile_selection(self):
        a=self.app
        picker=a.show_profile_picker()
        self.assertEqual(picker.profile_cards,{})
        form=a.new_profile()
        self.assertIs(a.grab_current(),form)
        form.destroy()
        self.assertIs(a.grab_current(),picker)
        picker.destroy()
        a=self.create()
        ident=a.profiles.data["active"]
        picker=a.show_profile_picker()
        self.assertEqual(set(picker.profile_cards),{ident})
        picker.profile_cards[ident].invoke()
        self.assertFalse(picker.winfo_exists())
        self.assertEqual(a.page,"character")
        self.assertEqual(a.data["character_name"],"Demo")

    def test_keep_replace_and_failed_import_rollback(self):
        a=self.create()
        ident=a.profiles.data["active"]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ER0000.sl2"
            path.write_bytes(fixture())
            chars=read_save(path,a.db)
            ids=import_characters(a.profiles,chars,a.data)
            self.assertIn(ident,a.profiles.data["profiles"])
            original=deepcopy(a.profiles.data)
            bad=deepcopy(chars)
            bad[0]["class_name"]="Invalid"
            with self.assertRaises((KeyError,ValueError)):
                import_characters(a.profiles,bad,a.data,replace_manual=True)
            self.assertEqual(a.profiles.data,original)
            import_characters(a.profiles,chars,a.data,replace_manual=True)
            self.assertNotIn(ident,a.profiles.data["profiles"])
            self.assertIn(ids[0],a.profiles.data["profiles"])
            self.assertIn(a.profiles.data["active"],a.profiles.data["profiles"])
            a.profiles.validate()

    def test_initial_import_asks_policy_before_any_mutation(self):
        a=self.create()
        previous=deepcopy(a.profiles.data)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"ER0000.sl2"
            path.write_bytes(fixture())
            dialog=a.begin_import(path,policy=None)
            self.assertEqual(a.profiles.data,previous)
            self.assertFalse(getattr(a,"import_in_progress",False))
            dialog.replace_profiles()
            end=time.monotonic()+5
            while a.import_in_progress and time.monotonic()<end:
                a.update()
                time.sleep(.01)
            self.assertFalse(a.import_in_progress)
            self.assertTrue(all(p["state"]["save_link"] for p in a.profiles.data["profiles"].values() if p["state"]["profile_created"]))
            self.assertEqual(len(a.profile_picker.profile_cards),1)

    def test_installation_discovery_checks_roaming_and_local_saves(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            local=root/"installation/Game"
            roaming=root/"roaming/EldenRing/account"
            local.mkdir(parents=True)
            roaming.mkdir(parents=True)
            (local/"ER0000.co2").write_bytes(b"fixture")
            (roaming/"ER0000.sl2").write_bytes(b"fixture")
            with patch.dict("os.environ",{"APPDATA":str(root/"roaming")}):
                paths=discover(root/"installation")
            self.assertEqual(set(paths),{(local/"ER0000.co2").resolve(),(roaming/"ER0000.sl2").resolve()})

    def test_inventory_badges_and_checkpoint_icons(self):
        a=self.create()
        a.data["inventory_weapons"]=[{"name":"Dagger","current":6,"quantity":2}]
        a.show("weapons")
        a.catalogue()
        a.gallery.filter("Dagger")
        a.update()
        badge=a.gallery.ownership_badges["Dagger"]
        self.assertIn("+6 ×2",a.gallery.canvas.itemcget(badge,"text"))
        self.assertEqual(a.gallery.canvas.itemcget(badge,"fill"),"#428DDF")
        point=a.profiles.checkpoint(a.data)
        window=a.checkpoint_detail(point)
        self.assertEqual(set(window.weapon_cards),{("Dagger",6)})
        window.render_tab(a.t("goal"))
        self.assertEqual(window.weapon_cards,{})
        window.render_tab(a.t("owned_weapons"))
        self.assertEqual(len(window.weapon_cards),1)

    def test_dropdown_wheel_scrolls_list_without_page_movement(self):
        a=self.create()
        a.deiconify()
        a.set_visual_style("style_xp")
        a.show("settings")
        option=a.language_option if hasattr(a,"language_option") else a.style_option
        option.configure(values=[f"Item {i}" for i in range(70)])
        before=a.body._parent_canvas.yview()
        menu=a.open_scroll_menu(option)
        a.update()
        first=menu.menu_list.yview()
        menu.menu_list.event_generate("<MouseWheel>",delta=-120)
        a.update()
        self.assertGreater(menu.menu_list.yview()[0],first[0])
        self.assertEqual(a.body._parent_canvas.yview(),before)
        menu.destroy()

    def test_compact_stones_timer_and_borderless_snap(self):
        a=self.create()
        a.show("weapons")
        a.manual_vars["target"].set("1")
        a.calculate_weapons()
        window=a.compact_dashboard()
        a.update()
        self.assertTrue(window.overrideredirect())
        window.mode_var.set("weapons")
        window.refresh_summary()
        window.rune_var.set("0")
        self.assertGreater(a.planner.weapons()["stones_cost"],0)
        window.all_stones()
        self.assertEqual(a.planner.weapons()["stones_cost"],0)
        self.assertEqual(a.data["runes"],0)
        self.assertTrue(all(row["button"].cget("state")=="disabled" for row in window.purchase_rows.values()))
        window.mode_var.set("farm")
        window.refresh_summary()
        window.start_sample()
        a.timer_started=time.monotonic()-60
        a.deadline=time.monotonic()-1
        a.tick_timer()
        window.rune_var.set("2400")
        self.assertEqual(window.gain_var.get(),"2400")
        window.record_sample()
        self.assertEqual(a.planner.farm_rates()["measured"],2400)
        area=monitor_workarea(window)
        self.assertEqual(snap_position(area[0]+5,area[1]+6,430,630,area),(area[0],area[1]))
        self.assertEqual(snap_position(-1915,6,430,630,(-1920,0,0,1080)),(-1920,0))
        window.reopen()
        self.assertEqual(a.data["farm"]["samples"][-1]["runes"],2400)

    def test_rgb_changes_native_text_without_surface_redraw(self):
        a=self.create()
        a.deiconify()
        a.set_visual_style("style_rainbow")
        a.update()
        panel=a.views[a.page]["frame"]
        background=panel.cget("fg_color")
        before=a.brand._label.cget("fg")
        a.rgb_started-=1
        a.rgb_tick()
        self.assertEqual(panel.cget("fg_color"),background)
        self.assertNotEqual(a.brand._label.cget("fg"),before)
        a.set_visual_style("style_modern")
        self.assertIsNone(a.rgb_job)

    def test_elden_palettes_replace_art_and_restore_plain_surfaces(self):
        a=self.create()
        a.deiconify()
        a.set_visual_style("style_elden")
        pictures=[]
        for palette in ("elden","moon","ember"):
            a.set_palette(palette)
            a.update()
            a.paint_background()
            self.assertEqual(a.background_key[3],palette)
            self.assertTrue(a.background_text)
            self.assertTrue(all(widget._label.cget("image") for widget,_ in a.background_text))
            pictures.append(a.background_layers[0].photo)
        self.assertEqual(len(set(pictures)),3)
        labels=[widget for widget,_ in a.background_text]
        a.set_visual_style("style_modern")
        self.assertEqual(a.background_layers,[])
        self.assertTrue(all(not widget._label.cget("image") for widget in labels if widget.winfo_exists()))


class StartupSelection(unittest.TestCase):
    def test_fresh_start_requires_explicit_character_selection(self):
        with tempfile.TemporaryDirectory() as folder,patch.dict("os.environ",{"LOCALAPPDATA":folder}):
            a=App(persist=True)
            try:
                end=time.monotonic()+.3
                while time.monotonic()<end:
                    a.update()
                    time.sleep(.01)
                self.assertEqual(a.profile_picker.profile_cards,{})
                self.assertIs(a.grab_current(),a.profile_picker)
                self.assertFalse(a.data["profile_created"])
            finally:
                a.close()


if __name__=="__main__":
    unittest.main()
