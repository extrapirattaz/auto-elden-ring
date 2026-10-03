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
        cls.db=Database()

    def test_multi_weapon_purchase_consumes_once_preserves_surplus(self):
        p=Planner(self.db)
        p.state["weapon_mode"]="catalogue"
        p.toggle_weapon("Dagger")
        p.toggle_weapon("Longsword")
        for item in p.state["selected"]:
            item["target"]=1
        p.state["stock"]["normal:1"]=1
        p.set_wallet(10000)
        before=p.weapons()
        self.assertEqual(before["stones"][0]["missing"],3)
        p.purchase("normal:1")
        with self.assertRaises(ValueError):
            p.purchase("normal:1")
        p.state["stock"]["normal:1"]+=5
        p.complete_upgrades()
        self.assertEqual(p.state["stock"]["normal:1"],5)
        self.assertEqual(p.state["runes"],10000-before["total"])
        self.assertTrue(all(i["current"]==1 for i in p.state["selected"]))
        self.assertEqual(p.weapons()["total"],0)

    def test_failed_transactions_do_not_change_state(self):
        p=Planner(self.db)
        original=deepcopy(p.state)
        with self.assertRaises(ValueError):
            p.purchase("normal:1")
        self.assertEqual(p.state,original)
        with self.assertRaises(ValueError):
            p.complete_upgrades()
        self.assertEqual(p.state,original)

    def test_ancient_material_needs_separate_confirmation(self):
        p=Planner(self.db)
        p.state["manual"].update(kind="somber",current=9,target=10,base=160)
        p.set_wallet(1000)
        self.assertEqual(p.weapons()["dragon_needed"],1)
        with self.assertRaises(ValueError):
            p.complete_upgrades()
        p.complete_upgrades(True)
        self.assertEqual(p.state["runes"],40)

    def test_buff_normalization_and_weighted_samples(self):
        p=Planner(self.db)
        p.add_sample(1560,60,"gold","gold_foot")
        p.add_sample(2000,60,"none","none")
        p.add_sample(5040,180,"gold","gold_horn")
        rates=p.farm_rates()
        self.assertEqual(rates["measured"],1720)
        self.assertEqual(rates["baseline"],1200)
        self.assertEqual(rates["optimized"],2016)
        self.assertEqual(buff_multiplier("silver","silver_foot"),1)
        self.assertEqual(buff_multiplier("gold","gold_horn"),Fraction(42,25))

    def test_shared_budget_boundary(self):
        p=Planner(self.db)
        p.state["manual"].update(target=1)
        p.set_wallet(529)
        self.assertEqual(p.affordable_targets()[0][0]["target"],0)
        p.set_wallet(530)
        self.assertEqual(p.affordable_targets()[0][0]["target"],1)
        self.assertEqual(p.affordable_targets()[1],0)

    def test_localized_catalogue_and_placeholder_parity(self):
        reference=TEXT["en"]
        placeholders=lambda text:{field for _,field,_,_ in Formatter().parse(text) if field}
        for language,table in TEXT.items():
            self.assertEqual(set(table),set(reference))
            for key in reference:
                self.assertEqual(placeholders(table[key]),placeholders(reference[key]),key)
            translator=Translator(language)
            self.assertEqual(set(translator.names[language]),set(self.db.weapons))
            for name,w in self.db.weapons.items():
                entry=self.db.raw["weapons_by_category"][w.category][name]
                self.assertTrue(resource_path(f'assets/catalogue/{entry["id"]}.png').is_file())


if __name__=="__main__":
    unittest.main()
