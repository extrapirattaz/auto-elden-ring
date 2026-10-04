"""Exercise real widgets, including timed multi-measurement workflows."""
import time
import unittest
from unittest.mock import patch
from auto_elden_ring.ui import App


class Interface(unittest.TestCase):
    def setUp(self):
        self.app = App(persist=False)
        self.app.withdraw()
        self.app.update()

    def tearDown(self):
        if self.app.timer_job:
            self.app.after_cancel(self.app.timer_job)
        self.app.destroy()

    def test_attributes_compute_levels_and_wallet_route(self):
        a = self.app
        a.stat_vars["stats_target","vigor"].set("60")
        a.wallet_var.set("1500")
        a.calculate_character()
        a.update()
        a.blend_titlebar()
        a.toggle_maximize()
        self.assertEqual(a.state(),"zoomed")
        a.toggle_maximize()
        self.assertEqual(a.state(),"normal")
        self.assertEqual(a.planner.character()["target"],54)
        self.assertEqual(a.planner.character()["current"],9)
        self.assertEqual(a.data["runes"],1500)

    def test_manual_inverse_and_no_dragon_shortcut(self):
        a = self.app
        a.show("weapons")
        a.manual_vars["current"].set("9")
        a.toggle_inverse()
        self.assertEqual(a.data["manual"]["input_mode"],"next")
        self.assertEqual(a.planner.manual_weapon().base,130)
        a.max_without_dragon()
        self.assertEqual(a.data["manual"]["target"],24)

    def test_all_languages_and_themes_render_every_page(self):
        a = self.app
        for language in ("en","fr","cs","de","es","ja"):
            a.data["language"]=language
            from auto_elden_ring.styles import STYLES
            for style in STYLES:
                a.set_visual_style("style_"+style)
                for page in ("character","weapons","stones","farm","journal","settings"):
                    a.show(page)
                    a.update_idletasks()

    def test_gallery_card_toggles_selection(self):
        a = self.app
        a.deiconify()
        a.update()
        a.show("weapons")
        a.catalogue()
        a.update()
        self.assertGreater(len(a.gallery.cache),0)
        name,x,y,_,_=next(box for box in a.gallery.hitboxes if box[0]=="Dagger")
        a.gallery.canvas.event_generate("<Button-1>",x=int(x+20),y=int(y+20))
        a.update()
        self.assertEqual(a.data["selected"][0]["name"],"Dagger")
        a.gallery.canvas.event_generate("<Button-1>",x=int(x+20),y=int(y+20))
        a.update()
        self.assertEqual(a.data["selected"],[])
        a.planner.toggle_weapon("Dagger")
        a.planner.toggle_weapon("Black Knife")
        a.show("weapons")
        self.assertEqual(len(a.data["selected"]),2)
        a.planner.toggle_weapon("Dagger")
        self.assertEqual(a.data["selected"][0]["name"],"Black Knife")

    def test_calculation_and_palette_preserve_page_widgets(self):
        a=self.app
        a.show("weapons")
        frame=a.views["weapons"]["frame"]
        metric=a.weapon_metrics
        a.calculate_weapons()
        self.assertIs(a.weapon_metrics,metric)
        a.show("settings")
        settings=a.views["settings"]["frame"]
        a.set_palette("slate")
        self.assertIs(a.views["settings"]["frame"],settings)
        self.assertIs(a.views["weapons"]["frame"],frame)
        a.dyslexic_var.set(True)
        a.set_reading_mode()
        self.assertEqual(a.font_family,"OpenDyslexic")
        a.dyslexic_var.set(False)
        a.set_reading_mode()
        self.assertEqual(a.data["theme"],"slate")

    def test_zero_wallet_checklist_and_upgrade_reset(self):
        a=self.app
        a.show("weapons")
        a.manual_vars["target"].set("1")
        a.calculate_weapons()
        a.missing_popup()
        window=next(w for w in a.popups if hasattr(w,"purchase_rows"))
        row=window.purchase_rows["normal:1"]
        row["buy"]()
        self.assertEqual(row["button"].cget("text"),"✓")
        self.assertEqual(a.data["runes"],0)
        with patch("auto_elden_ring.ui.messagebox.askyesno",return_value=True):
            a.complete_upgrades()
        self.assertEqual(a.data["manual"]["current"],1)
        self.assertTrue(all(v==0 for v in a.data["stock"].values()))

    def test_free_goal_switch_preserves_inputs(self):
        a=self.app
        a.show("farm")
        control=a.farm_vars["runes"]
        self.assertEqual(a.free_goal_frame.winfo_manager(),"")
        a.set_farm_option("goal","free")
        self.assertEqual(a.free_goal_frame.winfo_manager(),"grid")
        a.set_farm_option("goal","combined")
        self.assertIs(a.farm_vars["runes"],control)
        self.assertEqual(a.free_goal_frame.winfo_manager(),"")

    def test_profiles_checkpoint_and_switch_render(self):
        a=self.app
        first=a.profiles.data["active"]
        state=a.profiles.create("Ranni","NG+","Wretch",a.data)
        a.activate_profile(state)
        a.show("journal")
        window=a.event_dialog()
        window.event_note.set("First step")
        window.save_current()
        point=a.profiles.active["checkpoints"][0]
        a.checkpoint_detail(point)
        a.switch_profile(first)
        a.update()
        self.assertEqual(a.data["character_name"],"Tarnished")
        self.assertEqual(a.callback_errors,[])

    def test_gallery_cache_bounded_and_window_close_stress(self):
        a=self.app
        a.show("weapons")
        for index in range(12):
            a.catalogue()
            a.update()
            for fraction in (0,.2,.4,.6,.8,1):
                a.gallery.canvas.yview_moveto(fraction)
                a.gallery.draw()
            self.assertLessEqual(len(a.gallery.cache),64)
            self.assertLess(len(a.gallery.hitboxes),40)
            a.gallery_window.destroy()
            a.update()
        self.assertEqual(a.callback_errors,[])

    def test_resize_with_active_timer_and_popup_callbacks(self):
        a=self.app
        a.deiconify()
        a.show("farm")
        a.start_timer()
        for index in range(30):
            a.geometry(f"{1080+index%3*30}x{730+index%5*20}+{30+index%4*10}+30")
            window=a.popup("Lifecycle test","500x300")
            window.after(100,lambda:None)
            window.destroy()
            a.update()
        self.assertEqual(a.callback_errors,[])
        self.assertIsNotNone(a.deadline)
        a.stop_timer()

    def test_catalogue_editor_updates_selected_weapon_only(self):
        a=self.app
        a.planner.toggle_weapon("Dagger")
        a.planner.toggle_weapon("Black Knife")
        a.data["weapon_mode"]="catalogue"
        a.show("weapons")
        a.selected_vars[0][1]["target"].set("12")
        a.select_weapon_editor(a.translator.weapon("Black Knife"))
        a.selected_vars[0][1]["target"].set("7")
        a.calculate_weapons()
        self.assertEqual([i["target"] for i in a.data["selected"]],[12,7])
        a.max_without_dragon()
        self.assertEqual(a.selected_vars[0][1]["target"].get(),"9")

    def test_price_editor_preserves_page_and_updates_one_value(self):
        a=self.app
        a.show("stones")
        panel=a.views["stones"]["frame"]
        with patch("auto_elden_ring.ui.messagebox.askyesno",return_value=True):
            window=a.edit_price("normal:1")
        window.price_var.set("250")
        window.apply_price()
        self.assertIs(a.views["stones"]["frame"],panel)
        self.assertEqual(a.price_labels["normal:1"].cget("text"),"250")
        self.assertEqual(a.price_labels["normal:2"].cget("text"),"400")
        a.restore_prices()
        self.assertEqual(a.price_labels["normal:1"].cget("text"),"200")

    def test_full_timer_sequence_records_weighted_five_minutes(self):
        a = self.app
        a.show("farm")
        a.start_full_test()
        with patch("auto_elden_ring.ui.messagebox.showinfo"):
            for index,runes in enumerate((1000,2000,9000)):
                self.assertEqual(a.timer_duration,(60,60,180)[index])
                a.after_cancel(a.timer_job)
                a.timer_job=None
                a.deadline=time.monotonic()-1
                a.tick_timer()
                a.farm_vars["runes"].set(str(runes))
                a.record_result()
                if index<2:
                    a.start_timer()
        self.assertEqual(a.planner.farm_rates()["seconds"],300)
        self.assertEqual(a.planner.farm_rates()["measured"],2400)
        self.assertIsNone(a.full_index)
        a.reset_timer()
        self.assertEqual(a.timer_label.cget("text"),"01:00")
        a.start_timer()
        a.timer_started=time.monotonic()-17
        a.stop_timer()
        self.assertIn(a.data["farm"]["seconds"],(17,18))
        self.assertEqual(int(a.farm_vars["seconds"].get()),a.data["farm"]["seconds"])


if __name__=="__main__":
    unittest.main()
