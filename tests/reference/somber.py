"""Original API: standard somber profile; ancient stone cost excluded."""

from auto_elden_ring.core import SOMBER_PRICES, generic_weapon, shopping_plan

STONE_PRICES_DARK = list(SOMBER_PRICES)


def calcul_arme_sombre(base_price: int, target_level: int, stone_prices=None) -> int:
    prices = STONE_PRICES_DARK if stone_prices is None else stone_prices
    if len(prices) != 9:
        raise ValueError("Neuf prix de pierres sombres sont requis.")
    weapon = generic_weapon("Arme sombre", "somber", base_price)
    return shopping_plan(
        [{"weapon": weapon, "current": 0, "target": target_level}],
        prices={f"somber:{i}": p for i, p in enumerate(prices, 1)},
    )["total"]
