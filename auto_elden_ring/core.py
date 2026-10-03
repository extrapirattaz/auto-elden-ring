"""Pure calculations. Rune amounts are integers; observations use rational math.

The catalogue tables are authoritative for known weapons. Generic profiles are
explicit assumptions and must never override an exceptional catalogue weapon.
"""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import json
from pathlib import Path
import sys

from classes_data import CLASS_DATA, ATTRIBUTES

MAX_LEVEL = 713
NORMAL_PRICES = (200, 400, 600, 900, 1200, 1500, 2400, 3600)
SOMBER_PRICES = (2000, 3000, 4000, 6000, 9000, 12000, 16000, 20000, 25000)
STONE_PRICES = {**{f"normal:{i}": p for i, p in enumerate(NORMAL_PRICES, 1)},
                **{f"somber:{i}": p for i, p in enumerate(SOMBER_PRICES, 1)},
                "normal:dragon": None, "somber:dragon": None}


def integer(value, label="Value", minimum=0, maximum=None):
    if isinstance(value, bool):
        raise ValueError(f"{label} : integer required.")
    try:
        number = int(value)
        if str(number) != str(value).strip():
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        raise ValueError(f"{label} : integer required.") from None
    if number < minimum or (maximum is not None and number > maximum):
        raise ValueError(f"{label} : expected between {minimum} and {maximum or '∞'}.")
    return number


def resource_path(name):
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)) / name


@dataclass(frozen=True)
class Weapon:
    name: str
    category: str
    dlc: bool
    maximum: int
    base: int | None
    costs: tuple[int, ...]
    offers: dict

    @property
    def kind(self):
        return "somber" if self.maximum == 10 else "normal"


class Database:
    def __init__(self, path=None):
        self.path = Path(path) if path else resource_path("elden_ring_costs.json")
        self.raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.metadata = self.raw["metadata"]
        self.categories = self.raw["category_names_fr"]
        if self.raw["max_character_level"] != MAX_LEVEL:
            raise ValueError("Unexpected maximum level in game data.")
        table = self.raw["character_level_cost_runes"]
        self.level_costs = tuple(integer(table[f"{i}->{i+1}"], "Level cost", 1)
                                 for i in range(1, MAX_LEVEL))
        self.weapons = {}
        for category, entries in self.raw["weapons_by_category"].items():
            for name, entry in entries.items():
                maximum = entry["max_upgrade"]
                if maximum not in (0, 10, 25) or name in self.weapons:
                    raise ValueError(f"Invalid or duplicate weapon : {name}")
                costs = tuple(integer(entry["upgrade_cost_runes"][f"{i}->{i+1}"], "Forge cost", 1)
                              for i in range(maximum))
                base = entry["upgrade_base_cost_runes"]
                if costs and costs[0] != base:
                    raise ValueError(f"Inconsistent base : {name}")
                self.weapons[name] = Weapon(name, category, entry["dlc"], maximum,
                                            base, costs, entry.get("shop_offers", {}))

    def level_cost(self, current, target):
        current = integer(current, "Current level", 1, MAX_LEVEL)
        target = integer(target, "Target level", current, MAX_LEVEL)
        return sum(self.level_costs[current-1:target-1])

    def affordable_level(self, current, budget):
        current = integer(current, "Current level", 1, MAX_LEVEL)
        budget = integer(budget, "Budget")
        target = current
        while target < MAX_LEVEL and self.level_costs[target-1] <= budget:
            budget -= self.level_costs[target-1]
            target += 1
        return target, budget


def stats_level(class_name, stats):
    if class_name not in CLASS_DATA:
        raise ValueError("Unknown starting class.")
    info = CLASS_DATA[class_name]
    if set(stats) != set(ATTRIBUTES):
        raise ValueError("All eight permanent attributes are required (without equipment bonuses).")
    return info["level"] + sum(integer(stats[a], a, info["stats"][a], 99) - info["stats"][a]
                                for a in ATTRIBUTES)


def level_plan(db, class_name, current, target, origin=None):
    info = CLASS_DATA.get(class_name)
    if not info:
        raise ValueError("Unknown starting class.")
    current = integer(current, "Current level", info["level"], MAX_LEVEL)
    target = integer(target, "Target level", current, MAX_LEVEL)
    origin = info["level"] if origin is None else integer(origin, "Tracking origin", info["level"], current)
    return {"current": current, "target": target, "missing_levels": target-current,
            "remaining": db.level_cost(current, target),
            "spent_tracking": db.level_cost(origin, current),
            "spent_class": db.level_cost(info["level"], current),
            "to_max": db.level_cost(current, MAX_LEVEL)}


def generic_weapon(name, kind, base):
    """Standard reinforcement profile, including somber +10's exceptional ×6.

    This is a model for an unknown weapon, not a way to identify its name.
    Python round on Fraction provides exact ties-to-even rounding (ERDB method).
    """
    if kind not in ("normal", "somber"):
        raise ValueError("Unknown weapon type.")
    base = integer(base, "Forge +0 → +1", 1)
    rates = ([Fraction(5+i, 5) for i in range(25)] if kind == "normal" else
             [Fraction(2+i, 2) for i in range(9)] + [Fraction(6)])
    return Weapon(name.strip() or "Custom weapon", "custom", False, len(rates), base,
                  tuple(round(base*r) for r in rates), {})


def inverse_base(kind, current, target, observed):
    """Return every integer base consistent with an observed *forge-only* total.

    Each rounded transition can differ by at most half a rune from its ideal
    rational value. This bounds the search rather than guessing one result.
    """
    model = generic_weapon("", kind, 10)
    current = integer(current, "Start", 0, model.maximum-1)
    target = integer(target, "End", current+1, model.maximum)
    observed = integer(observed, "Observed forge runes", 1)
    rates = ([Fraction(5+i, 5) for i in range(25)] if kind == "normal" else
             [Fraction(2+i, 2) for i in range(9)] + [Fraction(6)])
    factor = sum(rates[current:target])
    error = Fraction(target-current, 2)
    lower = max(1, int((observed-error)//factor))
    upper = int((observed+error)//factor)+1
    return [b for b in range(lower, upper+1)
            if sum(generic_weapon("", kind, b).costs[current:target]) == observed]


def stone_label(key):
    kind, tier = key.split(":")
    if tier == "dragon":
        return ("Somber ancient dragon smithing stone" if kind == "somber" else "Ancient dragon smithing stone")
    return f"{'Somber smithing stone' if kind == 'somber' else 'Smithing stone'} [{tier}]"


def stone_requirements(weapon, current, target):
    current = integer(current, "Current upgrade", 0, weapon.maximum)
    target = integer(target, "Target upgrade", current, weapon.maximum)
    stones = Counter()
    for step in range(current+1, target+1):
        if step == weapon.maximum:
            if weapon.maximum in (25, 10):
                stones[f"{weapon.kind}:dragon"] += 1
                continue
        if weapon.kind == "normal":
            stones[f"normal:{(step-1)//3+1}"] += (2, 4, 6)[(step-1)%3]
        else:
            stones[f"somber:{step}"] += 1
    return stones


def unlocked(key, normal_bearings, somber_bearings):
    kind, tier = key.split(":")
    if tier == "dragon":
        return False
    limit = 2*normal_bearings if kind == "normal" else (0, 2, 4, 6, 8, 9)[somber_bearings]
    return int(tier) <= limit


def shopping_plan(items, owned=None, prices=None, normal_bearings=4, somber_bearings=5, extras=()):
    """Aggregate all demands BEFORE deducting inventory once across the basket.

    Ancient stones without inventory or a manual acquisition cost are unresolved,
    never silently replaced by a purchasable tier-8/9 stone.
    """
    owned = owned or {}
    price_map = dict(STONE_PRICES)
    if prices:
        if set(prices) - set(STONE_PRICES):
            raise ValueError("Unknown material.")
        price_map.update(prices)
    for key, value in owned.items():
        if key not in STONE_PRICES:
            raise ValueError("Unknown inventory material.")
        integer(value, stone_label(key))
    for key, value in price_map.items():
        if value is not None:
            integer(value, f"Price {stone_label(key)}")
    normal_bearings = integer(normal_bearings, "Normal bell bearings", 0, 4)
    somber_bearings = integer(somber_bearings, "Somber bell bearings", 0, 5)
    demand = Counter()
    forge = spent = 0
    lines = []
    for item in items:
        weapon = item["weapon"]
        current = integer(item["current"], "Current", 0, weapon.maximum)
        target = integer(item["target"], "Target", current, weapon.maximum)
        quantity = integer(item.get("quantity", 1), "Weapon copies", 1, 999)
        requirements = stone_requirements(weapon, current, target)
        demand.update({key: n*quantity for key, n in requirements.items()})
        cost = sum(weapon.costs[current:target])*quantity
        paid = sum(weapon.costs[:current])*quantity
        forge += cost
        spent += paid
        lines.append({"name": weapon.name, "current": current, "target": target,
                      "quantity": quantity, "forge": cost, "past_forge": paid})
    stones = []
    stone_cost = 0
    for key, required in demand.items():
        stock = integer(owned.get(key, 0), "Stock")
        missing = max(0, required-stock)
        unit = price_map[key]
        available = unlocked(key, normal_bearings, somber_bearings)
        cost = missing*unit if unit is not None else 0
        stone_cost += cost
        unresolved = bool(missing and (unit is None or (not available and key not in (prices or {}))))
        stones.append({"key": key, "required": required, "used": min(stock, required),
                       "missing": missing, "unit": unit, "cost": cost,
                       "unlocked": available, "unresolved": unresolved})
    extra_cost = sum(integer(e["quantity"], "Quantity", 1)*integer(e["unit"], "Price") for e in extras)
    return {"lines": lines, "stones": stones, "forge": forge, "stones_cost": stone_cost,
            "extras": extra_cost, "total": forge+stone_cost+extra_cost, "past_forge": spent,
            "complete": not any(s["unresolved"] for s in stones)}


def affordable_weapon(weapon, current, budget, **options):
    current = integer(current, "Current upgrade", 0, weapon.maximum)
    budget = integer(budget, "Budget")
    best = current
    cost = 0
    for target in range(current+1, weapon.maximum+1):
        plan = shopping_plan([{"weapon": weapon, "current": current, "target": target}], **options)
        if not plan["complete"] or plan["total"] > budget:
            break
        best, cost = target, plan["total"]
    return best, budget-cost


def farm_estimate(runes, seconds, needed, wallet=0, efficiency=100):
    runes = integer(runes, "Measured runes", 1)
    seconds = integer(seconds, "Measured duration (s)", 1)
    needed = integer(needed, "Goal")
    wallet = integer(wallet, "Runes held")
    efficiency = integer(efficiency, "Sustained efficiency (%)", 1, 100)
    remaining = max(0, needed-wallet)
    rate = Fraction(runes*efficiency, seconds*100)
    # Ceiling: round time upwards so the estimate doesn't fall below the goal.
    duration = -(-remaining // rate)
    return {"remaining": remaining, "runes_per_minute": float(rate*60),
            "seconds": int(duration)}


def duration_label(seconds):
    days, seconds = divmod(integer(seconds), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days} d {hours:02d} h {minutes:02d} min {seconds:02d} s"
