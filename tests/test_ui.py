"""Real Tk widgets exercised via their application callbacks (no game needed)."""

import copy
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from auto_elden_ring.ui import App
from auto_elden_ring.storage import save_project, load_project


class Interface(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.withdraw()
        self.errors = []
        self.patch = patch(
            "auto_elden_ring.ui.messagebox.showerror",
            side_effect=lambda *a, **kw: self.errors.append(a),
        )
        self.patch.start()
        self.app.update()

    def tearDown(self):
        self.app.stop_timer()
        self.app.destroy()
        self.patch.stop()

    def test_catalogue_to_basket_to_farm(self):
        a = self.app
        self.assertEqual(len(a.catalogue.get_children()), 487)
        a.catalogue.selection_set(("Dagger", "Black Knife"))
        a.fields["weapon_target"].set(9)
        a.add_weapons()
        self.assertEqual(len(a.items), 2)
        a.fields["farm_goal"].set("Panier armes / achats")
        a.calculate_farm()
        self.assertIn("runes à récolter", a.farm_result.get())
        self.assertTrue(a.last_plan["complete"])
        self.assertFalse(self.errors)

    def test_stats_and_inverse_callbacks(self):
        a = self.app
        a.fields["class"].set("Indigent")
        a.reset_class()
        a.fields["stat_target_vigor"].set(12)
        a.calculate_stats()
        self.assertEqual(a.fields["level_target"].get(), "3")
        a.calculate_inverse()
        self.assertEqual(a.fields["custom_base"].get(), "100")
        a.add_custom()
        self.assertEqual(len(a.items), 1)
        self.assertFalse(self.errors)

    def test_save_restore_and_csv(self):
        a = self.app
        a.items = [{"name": "Dagger", "current": 0, "target": 25, "quantity": 2, "custom": False}]
        a.inventory = {"normal:dragon": 2, "normal:1": 6}
        a.extras = [{"name": "=unsafe formula", "quantity": 2, "unit": 600}]
        a.fields["farm_notes"].set("Scarabée d'or, spot de test")
        a.update_plan()
        initial = a.last_plan["combined"]
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "plan.json"
            save_project(project, a.project_data(), a.db)
            a.items = []
            a.inventory = {}
            a.apply_project(load_project(project, a.db))
            self.assertEqual(a.last_plan["combined"], initial)
            self.assertEqual(a.inventory["normal:dragon"], 2)
            a.write_csv(Path(temp) / "plan.csv")
            csv = (Path(temp) / "plan.csv").read_text(encoding="utf-8-sig")
            self.assertIn("'=unsafe formula", csv)
            self.assertIn("Total chiffré", csv)
        self.assertFalse(self.errors)

    def test_invalid_project_does_not_replace_session(self):
        a = self.app
        data = copy.deepcopy(a.project_data())
        data["fields"]["wallet"] = "-10"
        with self.assertRaises(ValueError):
            a.apply_project(data)
        self.assertEqual(a.fields["wallet"].get(), "0")

    def test_timer_stop_and_deadline(self):
        a = self.app
        a.start_timer()
        self.assertIsNotNone(a.timer_job)
        a.timer_started = time.monotonic() - 17
        a.stop_timer()
        self.assertEqual(a.fields["farm_seconds"].get(), "17")
        a.start_timer()
        a.after_cancel(a.timer_job)
        a.deadline = time.monotonic() - 1
        a.tick()
        self.assertEqual(a.fields["farm_seconds"].get(), "60")
        self.assertIsNone(a.timer_job)
        self.assertEqual(a.timer_label.get(), "Test terminé")

    def test_bad_inputs_show_validation(self):
        a = self.app
        a.fields["farm_runes"].set(0)
        a.calculate_farm()
        self.assertEqual(len(self.errors), 1)


if __name__ == "__main__":
    unittest.main()
