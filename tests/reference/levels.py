"""Compatibility API for the original calculator, using exact level costs."""

from classes_data import CLASS_DATA, ATTRIBUTES
from auto_elden_ring.core import Database, stats_level


def calculate_level(class_name: str, target_stats: dict[str, int]) -> tuple[int, int]:
    info = CLASS_DATA[class_name]
    target = stats_level(class_name, {a: target_stats.get(a, info["stats"][a]) for a in ATTRIBUTES})
    return target, Database().level_cost(info["level"], target)
