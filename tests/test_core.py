"""Boundary, regression and catalogue-wide checks (no external dependencies)."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from auto_elden_ring.core import *
from auto_elden_ring.storage import save_project, load_project
from auto_elden_ring.selfcheck import self_check


class Calculations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database()

    def test_self_check(self):
        self.assertEqual(json.loads(self_check())["status"], "PASS")

    def test_levels_every_transition(self):
        for level in range(1, 713):
            expected = ((max(0, level - 11) * 2 + 10) * (level + 81) ** 2) // 100 + 1
            self.assertEqual(self.db.level_cost(level, level + 1), expected)

    def test_level_known_values(self):
        self.assertEqual(self.db.level_cost(1, 2), 673)
        self.assertEqual(self.db.level_cost(12, 13), 1038)
        self.assertEqual(self.db.level_cost(712, 713), 8879348)
        self.assertEqual(self.db.level_cost(1, 713), 1692566842)
        self.assertEqual(self.db.level_cost(713, 713), 0)

    def test_level_invalid(self):
        for current, target in ((0, 10), (10, 9), (1, 714), (-1, 10)):
            with self.assertRaises(ValueError):
                self.db.level_cost(current, target)

    def test_budget_boundaries(self):
        for current in (1, 9, 50, 150, 712):
            cost = self.db.level_cost(current, current + 1)
            self.assertEqual(self.db.affordable_level(current, cost), (current + 1, 0))
            self.assertEqual(self.db.affordable_level(current, cost - 1), (current, cost - 1))
        self.assertEqual(self.db.affordable_level(713, 999), (713, 999))

    def test_level_tracking_independent_origin(self):
        plan = level_plan(self.db, "Vagabond", 80, 150, 50)
        self.assertEqual(plan["spent_tracking"], self.db.level_cost(50, 80))
        self.assertEqual(plan["spent_class"], self.db.level_cost(9, 80))
        self.assertEqual(plan["missing_levels"], 70)
        with self.assertRaises(ValueError):
            level_plan(self.db, "Vagabond", 80, 150, 81)

    def test_all_classes(self):
        for name, info in CLASS_DATA.items():
            self.assertEqual(stats_level(name, info["stats"]), info["level"])
            self.assertEqual(sum(info["stats"].values()) - 79, info["level"])
            self.assertEqual(stats_level(name, {a: 99 for a in ATTRIBUTES}), 713)
            stats = dict(info["stats"])
            stats["vigor"] -= 1
            with self.assertRaises(ValueError):
                stats_level(name, stats)
            stats["vigor"] = 100
            with self.assertRaises(ValueError):
                stats_level(name, stats)

    def test_non_integer_rejected(self):
        for value in (True, 1.5, "1.0", "abc", None, -1):
            with self.assertRaises(ValueError):
                integer(value)

    def test_normal_stones(self):
        w = self.db.weapons["Dagger"]
        self.assertEqual(stone_requirements(w, 0, 24), {f"normal:{i}": 12 for i in range(1, 9)})
        self.assertEqual(stone_requirements(w, 1, 3), {"normal:1": 10})
        p = shopping_plan([{"weapon": w, "current": 0, "target": 24}])
        self.assertEqual(p["stones_cost"], 129600)
        self.assertEqual(p["forge"], 10296)

    def test_somber_stones_and_final(self):
        w = self.db.weapons["Black Knife"]
        self.assertEqual(stone_requirements(w, 0, 9), {f"somber:{i}": 1 for i in range(1, 10)})
        p = shopping_plan([{"weapon": w, "current": 0, "target": 10}])
        self.assertEqual(p["stones_cost"], 97000)
        self.assertEqual(p["forge"], 5280)
        self.assertFalse(p["complete"])
        self.assertEqual(w.costs[9], 960)

    def test_final_normal_stone_no_tier8_substitution(self):
        w = self.db.weapons["Dagger"]
        p = shopping_plan([{"weapon": w, "current": 24, "target": 25}])
        self.assertEqual(p["forge"], 754)
        self.assertEqual(p["stones_cost"], 0)
        self.assertEqual(p["stones"][0]["key"], "normal:dragon")
        self.assertFalse(p["complete"])

    def test_final_stone_owned_or_manual_price(self):
        items = [{"weapon": self.db.weapons["Dagger"], "current": 24, "target": 25}]
        p = shopping_plan(items, owned={"normal:dragon": 1})
        self.assertTrue(p["complete"])
        self.assertEqual(p["total"], 754)
        p = shopping_plan(items, prices={"normal:dragon": 20000})
        self.assertTrue(p["complete"])
        self.assertEqual(p["total"], 20754)

    def test_shared_stock_deducted_once(self):
        items = [{"weapon": self.db.weapons["Dagger"], "current": 0, "target": 1}] * 2
        p = shopping_plan(items, owned={"normal:1": 2})
        self.assertEqual(p["stones"][0]["required"], 4)
        self.assertEqual(p["stones"][0]["missing"], 2)
        self.assertEqual(p["total"], 660)
        self.assertEqual(shopping_plan(items, owned={"normal:1": 999})["stones_cost"], 0)

    def test_partial_bearings(self):
        items = [{"weapon": self.db.weapons["Dagger"], "current": 6, "target": 7}]
        self.assertFalse(shopping_plan(items, normal_bearings=1)["complete"])
        self.assertTrue(shopping_plan(items, normal_bearings=2)["complete"])
        self.assertTrue(shopping_plan(items, normal_bearings=0, owned={"normal:3": 2})["complete"])
        self.assertTrue(
            shopping_plan(items, normal_bearings=0, prices={"normal:3": 900})["complete"]
        )

    def test_all_catalogue_passages_and_spent(self):
        for w in self.db.weapons.values():
            for current in range(w.maximum):
                p = shopping_plan([{"weapon": w, "current": current, "target": current + 1}])
                self.assertEqual(p["forge"], w.costs[current])
                self.assertEqual(p["past_forge"], sum(w.costs[:current]))
                self.assertGreater(sum(s["required"] for s in p["stones"]), 0)

    def test_exceptional_catalogue_prices_preserved(self):
        self.assertEqual(self.db.weapons["Soldier's Crossbow"].costs[1], 336)
        self.assertEqual(self.db.weapons["Pulley Crossbow"].costs[9], 720)
        self.assertEqual(self.db.weapons["Jar Cannon"].costs[9], 1740)

    def test_non_upgradable(self):
        w = self.db.weapons["Meteorite Staff"]
        self.assertEqual(shopping_plan([{"weapon": w, "current": 0, "target": 0}])["total"], 0)
        with self.assertRaises(ValueError):
            shopping_plan([{"weapon": w, "current": 0, "target": 1}])

    def test_quantity_and_extras(self):
        p = shopping_plan(
            [{"weapon": self.db.weapons["Dagger"], "current": 0, "target": 1, "quantity": 3}],
            extras=[{"name": "Item", "quantity": 2, "unit": 600}],
        )
        self.assertEqual(p["total"], 2790)
        with self.assertRaises(ValueError):
            shopping_plan([{"weapon": self.db.weapons["Dagger"], "current": 2, "target": 1}])

    def test_inverse_every_standard_step(self):
        for kind in ("normal", "somber"):
            for base in (1, 7, 100, 130, 288, 580):
                w = generic_weapon("Test", kind, base)
                for current in range(w.maximum):
                    self.assertIn(base, inverse_base(kind, current, current + 1, w.costs[current]))
                self.assertIn(base, inverse_base(kind, 0, w.maximum, sum(w.costs)))
        self.assertEqual(inverse_base("normal", 4, 5, 180), [100])
        self.assertEqual(inverse_base("somber", 9, 10, 960), [160])

    def test_weapon_budget_exact_boundary(self):
        w = self.db.weapons["Dagger"]
        self.assertEqual(affordable_weapon(w, 0, 530), (1, 0))
        self.assertEqual(affordable_weapon(w, 0, 529), (0, 529))
        self.assertEqual(affordable_weapon(w, 24, 754), (24, 754))
        self.assertEqual(affordable_weapon(w, 24, 754, owned={"normal:dragon": 1}), (25, 0))

    def test_farm_ceiling_wallet_efficiency(self):
        self.assertEqual(farm_estimate(50000, 60, 100000)["seconds"], 120)
        self.assertEqual(farm_estimate(50000, 60, 100000, wallet=50000)["seconds"], 60)
        self.assertEqual(farm_estimate(50000, 60, 100000, efficiency=50)["seconds"], 240)
        self.assertEqual(farm_estimate(3, 60, 1)["seconds"], 20)
        self.assertEqual(farm_estimate(3, 60, 4)["seconds"], 80)
        self.assertEqual(farm_estimate(1, 60, 1, wallet=2)["seconds"], 0)
        with self.assertRaises(ValueError):
            farm_estimate(0, 60, 100)

    def test_standard_profile_totals(self):
        stats = dict(CLASS_DATA["Wretch"]["stats"])
        stats["vigor"] += 1
        self.assertEqual(stats_level("Wretch", stats), 2)
        self.assertEqual(self.db.level_cost(1, 2), 673)
        self.assertEqual(
            shopping_plan(
                [{"weapon": generic_weapon("Test", "normal", 130), "current": 0, "target": 25}]
            )["total"],
            140650,
        )
        self.assertEqual(
            shopping_plan(
                [{"weapon": generic_weapon("Test", "somber", 160), "current": 0, "target": 10}]
            )["total"],
            102280,
        )

    def test_project_roundtrip_and_invalid(self):
        from auto_elden_ring.planner import default_state

        data = default_state()
        data["selected"] = [{"name": "Dagger", "current": 0, "target": 24, "quantity": 2}]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "projet.json"
            save_project(path, data, self.db)
            self.assertEqual(load_project(path, self.db)["selected"], data["selected"])
            bad = copy.deepcopy(data)
            bad["selected"][0]["target"] = 26
            with self.assertRaises(ValueError):
                save_project(path, bad, self.db)
            self.assertEqual(load_project(path, self.db)["selected"], data["selected"])
            path.write_text('{"schema":99}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_project(path, self.db)


if __name__ == "__main__":
    unittest.main()
