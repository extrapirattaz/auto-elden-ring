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
            for theme in ("calm","elden","slate"):
                a.data["theme"]=theme
                a.build_shell()
                for page in ("character","weapons","stones","farm","settings"):
                    a.show(page)
                    a.update_idletasks()

    def test_gallery_card_toggles_selection(self):
        a = self.app
        a.show("weapons")
        a.catalogue()
        a.update()
        self.assertGreater(len(a.images),0)
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        tile=next(w for w in descendants(a) if getattr(w,"weapon_name",None)=="Dagger")
        tile._canvas.event_generate("<Button-1>",x=20,y=20)
        a.update()
        self.assertEqual(a.data["selected"][0]["name"],"Dagger")
        tile._canvas.event_generate("<Button-1>",x=20,y=20)
        a.update()
        self.assertEqual(a.data["selected"],[])
        a.planner.toggle_weapon("Dagger")
        a.planner.toggle_weapon("Black Knife")
        a.show("weapons")
        self.assertEqual(len(a.data["selected"]),2)
        a.planner.toggle_weapon("Dagger")
        self.assertEqual(a.data["selected"][0]["name"],"Black Knife")

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


if __name__=="__main__":
    unittest.main()
