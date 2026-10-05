"""End-to-end purchase, upgrade and farm accounting invariants."""

from copy import deepcopy
from fractions import Fraction
import json
from string import Formatter
import unittest
from auto_elden_ring.core import Database, resource_path
from auto_elden_ring.planner import Planner, buff_multiplier
from auto_elden_ring.i18n import TEXT, Translator


class Planning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database()

    def test_acknowledgements_ignore_wallet_and_reset_inventory(self):
        p = Planner(self.db)
        p.state["weapon_mode"] = "catalogue"
        p.toggle_weapon("Dagger")
        p.toggle_weapon("Longsword")
        for item in p.state["selected"]:
            item["target"] = 1
        p.state["stock"]["normal:1"] = 1
        p.set_wallet(10000)
        before = p.weapons()
        self.assertEqual(before["stones"][0]["missing"], 3)
        p.purchase("normal:1")
        with self.assertRaises(ValueError):
            p.purchase("normal:1")
        p.state["stock"]["normal:1"] += 5
        p.complete_upgrades()
        self.assertTrue(all(v == 0 for v in p.state["stock"].values()))
        self.assertEqual(p.state["runes"], 0)
        self.assertTrue(all(i["current"] == 1 for i in p.state["selected"]))
        self.assertEqual(p.weapons()["total"], 0)

    def test_purchase_without_wallet_and_duplicate_rejected(self):
        p = Planner(self.db)
        p.state["manual"]["target"] = 1
        p.set_wallet(0)
        self.assertEqual(p.purchase("normal:1"), (2, 400))
        original = deepcopy(p.state)
        with self.assertRaises(ValueError):
            p.purchase("normal:1")
        self.assertEqual(p.state, original)
        self.assertEqual(p.state["runes"], 0)
        self.assertEqual(p.state["purchased"]["normal:1"], 2)

    def test_upgrade_acknowledges_real_outcome_without_material_checks(self):
        p = Planner(self.db)
        p.state["manual"].update(kind="somber", current=9, target=10, base=160)
        p.set_wallet(1000)
        self.assertEqual(p.weapons()["dragon_needed"], 1)
        p.complete_upgrades()
        self.assertEqual(p.state["runes"], 0)
        self.assertEqual(p.state["manual"]["current"], 10)

    def test_buff_normalization_and_weighted_samples(self):
        p = Planner(self.db)
        p.add_sample(1560, 60, "gold", "gold_foot")
        p.add_sample(2000, 60, "none", "none")
        p.add_sample(5040, 180, "gold", "gold_horn")
        rates = p.farm_rates()
        self.assertEqual(rates["measured"], 1720)
        self.assertEqual(rates["baseline"], 1200)
        self.assertEqual(rates["optimized"], 2016)
        self.assertEqual(buff_multiplier("silver", "silver_foot"), 1)
        self.assertEqual(buff_multiplier("gold", "gold_horn"), Fraction(42, 25))

    def test_maximum_farm_level_accounts_for_investment_and_wallet_separately(self):
        p = Planner(self.db)
        original = deepcopy(p.state["stats_current"])
        p.state["farm"].update(goal="maximum", maximum_current=150, runes=12000, efficiency=80)
        p.set_wallet(1234)
        result = p.farm_projection()
        invested = self.db.level_cost(9, 150)
        self.assertEqual(result["goal"], self.db.level_cost(150, 713))
        self.assertEqual(result["invested"], invested)
        self.assertEqual(
            result["invested"] + result["remaining"] + 1234, self.db.level_cost(9, 713)
        )
        self.assertEqual(result["invested_time"], int(-(-Fraction(invested * 60) // 9600)))
        self.assertEqual(result["time"], result["maximum_time"])
        self.assertEqual(p.state["stats_current"], original)
        p.set_wallet(result["goal"] + 1)
        self.assertEqual(p.farm_projection()["time"], 0)
        self.assertEqual(p.farm_projection()["invested"], invested)

    def test_maximum_farm_level_boundaries_and_legacy_default(self):
        p = Planner(self.db)
        p.state["farm"].update(goal="maximum", runes=1000)
        p.state["farm"].pop("maximum_current")
        self.assertEqual(p.farm_projection()["invested"], 0)
        for level in (0, 8, 714):
            p.state["farm"]["maximum_current"] = level
            with self.assertRaises(ValueError):
                p.farm_projection()
        p.state["farm"]["maximum_current"] = 713
        result = p.farm_projection()
        self.assertEqual(result["time"], 0)
        self.assertEqual(result["invested"], self.db.level_cost(9, 713))

    def test_shared_budget_boundary(self):
        p = Planner(self.db)
        p.state["manual"].update(target=1)
        p.set_wallet(529)
        self.assertEqual(p.affordable_targets()[0][0]["target"], 0)
        p.set_wallet(530)
        self.assertEqual(p.affordable_targets()[0][0]["target"], 1)
        self.assertEqual(p.affordable_targets()[1], 0)

    def test_localized_catalogue_and_placeholder_parity(self):
        reference = TEXT["en"]
        placeholders = lambda text: {field for _, field, _, _ in Formatter().parse(text) if field}
        for language, table in TEXT.items():
            self.assertEqual(set(table), set(reference))
            for key in reference:
                self.assertEqual(placeholders(table[key]), placeholders(reference[key]), key)
            translator = Translator(language)
            self.assertEqual(set(translator.names[language]), set(self.db.weapons))
            for name, w in self.db.weapons.items():
                entry = self.db.raw["weapons_by_category"][w.category][name]
                self.assertTrue(resource_path(f'assets/catalogue/{entry["id"]}.webp').is_file())


if __name__ == "__main__":
    unittest.main()
