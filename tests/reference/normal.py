"""Original API: standard profile. Ancient stone acquisition cost excluded.

Use the catalogue for known weapons; some weapons have exceptional tariffs.
"""

from auto_elden_ring.core import NORMAL_PRICES, generic_weapon, shopping_plan

STONE_PRICES_NORMAL = list(NORMAL_PRICES)


def calcul_arme_normale(base_price: int, target_level: int, stone_prices=None) -> int:
    prices = STONE_PRICES_NORMAL if stone_prices is None else stone_prices
    if len(prices) != 8:
        raise ValueError("Huit prix de pierres normales sont requis.")
    weapon = generic_weapon("Arme normale", "normal", base_price)
    return shopping_plan(
        [{"weapon": weapon, "current": 0, "target": target_level}],
        prices={f"normal:{i}": p for i, p in enumerate(prices, 1)},
    )["total"]
