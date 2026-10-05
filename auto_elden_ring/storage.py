"""Versioned project persistence; validate before replacing the active session."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
from . import __version__
from .core import integer, STONE_PRICES, generic_weapon


def validate(data, db):
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise ValueError("Format de projet incompatible (schéma attendu : 1).")
    if data.get("data_sha256") not in (None, hashlib.sha256(db.path.read_bytes()).hexdigest()):
        raise ValueError(
            "Ce projet utilise une autre table de coûts. Utilise sa version correspondante de l'application."
        )
    if not isinstance(data.get("fields"), dict) or not all(
        isinstance(k, str) and isinstance(v, str) for k, v in data["fields"].items()
    ):
        raise ValueError("Champs du projet invalides.")
    if not isinstance(data.get("items"), list) or not isinstance(data.get("extras"), list):
        raise ValueError("Panier invalide.")
    for item in data["items"]:
        weapon = (
            generic_weapon(item["name"], item["kind"], item["base"])
            if item.get("custom")
            else db.weapons[item["name"]]
        )
        current = integer(item["current"], "Actuel", 0, weapon.maximum)
        integer(item["target"], "Cible", current, weapon.maximum)
        integer(item["quantity"], "Quantité", 1, 999)
    for extra in data["extras"]:
        if not isinstance(extra["name"], str):
            raise ValueError("Nom d'achat invalide.")
        integer(extra["quantity"], "Quantité", 1)
        integer(extra["unit"], "Prix")
    for section in ("inventory", "prices"):
        if not isinstance(data.get(section), dict):
            raise ValueError("Inventaire ou prix invalide.")
        for key, value in data[section].items():
            if key not in STONE_PRICES:
                raise ValueError("Pierre inconnue.")
            integer(value, section)
    return data


def load_project(path, db):
    try:
        return validate(json.loads(Path(path).read_text(encoding="utf-8")), db)
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Projet incomplet ou invalide.") from exc


def save_project(path, data, db):
    data = {
        **data,
        "schema": 1,
        "app_version": __version__,
        "data_sha256": hashlib.sha256(db.path.read_bytes()).hexdigest(),
    }
    validate(data, db)
    path = Path(path)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".auto-elden-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()
