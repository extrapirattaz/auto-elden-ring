"""Native, offline Tk interface. Calculations remain independently testable."""

import csv
from functools import wraps
import math
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from classes_data import CLASS_DATA, ATTRIBUTES
from . import __version__
from .core import (
    Database,
    integer,
    stats_level,
    level_plan,
    generic_weapon,
    inverse_base,
    shopping_plan,
    affordable_weapon,
    farm_estimate,
    duration_label,
    STONE_PRICES,
    stone_label,
    resource_path,
)
from .storage import save_project, load_project

LABELS = dict(
    zip(
        ATTRIBUTES,
        (
            "Vigueur",
            "Esprit",
            "Endurance",
            "Force",
            "Dextérité",
            "Intelligence",
            "Foi",
            "Ésotérisme",
        ),
    )
)
CLASSES_FR = dict(
    zip(
        CLASS_DATA,
        (
            "Vagabond",
            "Guerrier",
            "Héros",
            "Bandit",
            "Astrologue",
            "Prophète",
            "Samouraï",
            "Prisonnier",
            "Confesseur",
            "Indigent",
        ),
    )
)
ENUMS = {
    "custom_kind": ("Normale", "Sombre"),
    "dlc_filter": ("Tout", "Jeu de base", "DLC"),
    "farm_goal": (
        "Projet complet",
        "Niveaux visés",
        "Panier armes / achats",
        "Niveau maximum 713",
        "Objectif libre",
    ),
    "farm_talisman": ("Aucun", "Scarabée d'or", "Scarabée d'argent", "Autre"),
    "farm_consumable": (
        "Aucun",
        "Patte de volaille dorée en saumure",
        "Patte de volaille argentée en saumure",
        "Corne dorée",
        "Autre",
    ),
}


def fmt(number):
    return f"{number:,}".replace(",", " ")


def guarded(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except (ValueError, KeyError, OSError, TypeError) as exc:
            messagebox.showerror("Vérifier les valeurs", str(exc), parent=self)

    return wrapper


class App(tk.Tk):
    def __init__(self, db=None):
        super().__init__()
        self.db = db or Database()
        self.title(f"Auto Elden Ring • {__version__}")
        self.geometry("1200x850")
        self.minsize(1060, 760)
        self.configure(background="#101719")
        icon = resource_path("assets/app.ico")
        if icon.exists():
            try:
                self.iconbitmap(str(icon))
            except tk.TclError:
                pass
        self.fields, self.inventory, self.prices = {}, {}, {}
        self.items, self.extras = [], []
        self.deadline = self.timer_job = self.timer_started = None
        self.last_plan = None
        self.style_ui()
        header = ttk.Frame(self, padding=(24, 18))
        header.pack(fill="x")
        ttk.Label(header, text="AUTO ELDEN RING", style="Title.TLabel").pack(side="left")
        ttk.Label(
            header,
            text=f"PLANIFIER · AMÉLIORER · FARMER   /   v{__version__}",
            style="Muted.TLabel",
        ).pack(side="left", padx=24)
        ttk.Button(header, text="Enregistrer…", command=self.save).pack(side="right")
        ttk.Button(header, text="Ouvrir…", command=self.load).pack(side="right", padx=8)
        ttk.Label(
            self,
            text="Hors ligne  •  Forge et pierres séparées  •  Données : "
            + self.db.metadata["regulation_version"],
            style="Muted.TLabel",
            padding=(24, 6),
        ).pack(side="bottom", fill="x")
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 12))
        self.pages, self.canvases = {}, {}
        for name in (
            "Personnage",
            "Catalogue & armes",
            "Calcul inverse",
            "Panier & pierres",
            "Farm",
            "Données & aide",
        ):
            holder = ttk.Frame(self.tabs)
            canvas = tk.Canvas(holder, bg="#101719", highlightthickness=0, width=10, height=10)
            scrollbar = ttk.Scrollbar(holder, command=canvas.yview)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            canvas.configure(yscrollcommand=scrollbar.set)
            page = ttk.Frame(canvas, padding=18)
            window = canvas.create_window(0, 0, window=page, anchor="nw")

            def fit(_=None, c=canvas, p=page, w=window):
                c.itemconfigure(
                    w, width=c.winfo_width(), height=max(p.winfo_reqheight(), c.winfo_height())
                )
                c.configure(scrollregion=c.bbox("all"))

            canvas.bind("<Configure>", fit)
            page.bind("<Configure>", fit)
            self.tabs.add(holder, text=f"  {name}  ")
            self.pages[name] = page
            self.canvases[name] = canvas
        self.build_levels()
        self.build_weapons()
        self.build_inverse()
        self.build_plan()
        self.build_farm()
        self.build_help()
        self.reset_class()
        self.refresh_catalogue()
        self.update_plan()
        self.recalc_job = None
        for key in (
            "level_current",
            "level_target",
            "level_origin",
            "wallet",
            "normal_bearings",
            "somber_bearings",
        ):
            self.fields[key].trace_add("write", self.schedule_recalculation)
        self.bind_all("<MouseWheel>", self.scroll_page, add="+")

    def scroll_page(self, event):
        if event.widget.winfo_class() not in ("Treeview", "Text", "TCombobox"):
            name = list(self.pages)[self.tabs.index("current")]
            self.canvases[name].yview_scroll(int(-event.delta / 120), "units")

    def destroy(self):
        for name in ("timer_job", "recalc_job"):
            job = getattr(self, name, None)
            if job:
                self.after_cancel(job)
                setattr(self, name, None)
        super().destroy()

    def schedule_recalculation(self, *_):
        if self.recalc_job:
            self.after_cancel(self.recalc_job)
        self.recalc_job = self.after(250, self.recalculate)

    def recalculate(self):
        self.recalc_job = None
        try:
            self.compute_plan()
            integer(self.fields["wallet"].get(), "Runes en poche")
        except ValueError, KeyError:
            self.plan_result.set(
                "Saisie incomplète ou incohérente : vérifie les niveaux, le budget et les perles."
            )
            self.level_result.set("Saisie incomplète ou incohérente : vérifie les niveaux.")
            return
        self.calculate_levels()
        self.update_plan()

    def style_ui(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", font=("Segoe UI", 10), background="#101719", foreground="#edf0eb")
        s.configure("TFrame", background="#101719")
        s.configure("TLabel", background="#101719")
        s.configure("Title.TLabel", font=("Segoe UI", 22, "bold"), foreground="#d6b86a")
        s.configure("Heading.TLabel", font=("Segoe UI", 15, "bold"), foreground="#d6b86a")
        s.configure("Muted.TLabel", foreground="#aab7b5")
        s.configure("Result.TLabel", foreground="#e9ca7e", font=("Segoe UI", 11, "bold"))
        s.configure("TLabelframe", background="#101719", bordercolor="#344342")
        s.configure("TLabelframe.Label", foreground="#d6b86a", background="#101719")
        s.configure("TButton", background="#283735", padding=(12, 7), borderwidth=0)
        s.map("TButton", background=[("active", "#48625a")])
        s.configure(
            "TEntry",
            fieldbackground="#21302f",
            foreground="#ffffff",
            insertcolor="#ffffff",
            padding=5,
        )
        s.configure(
            "TCombobox",
            fieldbackground="#21302f",
            background="#283735",
            foreground="#ffffff",
            padding=5,
        )
        s.map(
            "TCombobox",
            fieldbackground=[("readonly", "#21302f")],
            foreground=[("readonly", "#ffffff")],
        )
        s.configure("TNotebook", background="#101719", borderwidth=0)
        s.configure("TNotebook.Tab", background="#23312f", padding=(8, 10))
        s.map(
            "TNotebook.Tab",
            background=[("selected", "#d6b86a")],
            foreground=[("selected", "#101719")],
        )
        s.configure(
            "Treeview", background="#172321", fieldbackground="#172321", rowheight=27, borderwidth=0
        )
        s.configure("Treeview.Heading", background="#2b3a36", padding=7)
        s.map("Treeview", background=[("selected", "#5a543a")])
        self.option_add("*TCombobox*Listbox.background", "#21302f")
        self.option_add("*TCombobox*Listbox.foreground", "#ffffff")

    def var(self, key, default=""):
        self.fields[key] = tk.StringVar(self, str(default))
        return self.fields[key]

    def entry(self, parent, label, key, default, row, width=14):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 14))
        ttk.Entry(parent, textvariable=self.var(key, default), width=width).grid(
            row=row, column=1, sticky="w", pady=5
        )

    def combo(self, parent, label, key, default, choices, row, width=27):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 14))
        box = ttk.Combobox(
            parent,
            textvariable=self.var(key, default),
            values=choices,
            state="readonly",
            width=width,
        )
        box.grid(row=row, column=1, sticky="w", pady=5)
        return box

    def heading(self, page, title, text):
        ttk.Label(page, text=title, style="Heading.TLabel").pack(anchor="w")
        ttk.Label(page, text=text, style="Muted.TLabel", wraplength=1020).pack(
            anchor="w", pady=(5, 12)
        )

    def tree(self, parent, columns, widths, height):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=8)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        for column, width in zip(columns, widths):
            tree.heading(column, text=column)
            tree.column(column, width=width, minwidth=50, anchor="w")
        tree.pack(side="left", fill="both", expand=True)
        bar = ttk.Scrollbar(frame, command=tree.yview)
        bar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=bar.set)
        return tree

    def class_name(self):
        return next(k for k, v in CLASSES_FR.items() if v == self.fields["class"].get())

    def build_levels(self):
        p = self.pages["Personnage"]
        self.heading(
            p,
            "Du premier niveau à ton build final",
            "Saisis les attributs permanents, sans talisman, rune majeure ni bonus temporaire. Niveau maximal : 713.",
        )
        body = ttk.Frame(p)
        body.pack(fill="x")
        left = ttk.LabelFrame(body, text="Progression", padding=14)
        left.pack(side="left", fill="y", padx=(0, 20))
        box = self.combo(left, "Classe", "class", "Vagabond", list(CLASSES_FR.values()), 0)
        box.bind("<<ComboboxSelected>>", lambda _: self.reset_class())
        for row, (label, key, default) in enumerate(
            (
                ("Niveau actuel", "level_current", 9),
                ("Niveau cible", "level_target", 150),
                ("Début du suivi (niveau)", "level_origin", 9),
                ("Budget / runes en poche", "wallet", 0),
            ),
            1,
        ):
            self.entry(left, label, key, default, row)
        ttk.Button(left, text="Calculer les niveaux", command=self.calculate_levels).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=10
        )
        ttk.Button(left, text="Niveau atteignable avec ce budget", command=self.level_budget).grid(
            row=6, column=0, columnspan=2, sticky="ew"
        )
        right = ttk.LabelFrame(body, text="Attributs → niveau automatique", padding=14)
        right.pack(side="left", fill="both", expand=True)
        for col, text in enumerate(("Attribut", "Classe", "Actuel", "Cible")):
            ttk.Label(right, text=text, style="Muted.TLabel").grid(
                row=0, column=col, padx=10, pady=5
            )
        self.base_labels = {}
        for row, attr in enumerate(ATTRIBUTES, 1):
            ttk.Label(right, text=LABELS[attr]).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            label = ttk.Label(right)
            label.grid(row=row, column=1, padx=10)
            self.base_labels[attr] = label
            for col, prefix in ((2, "stat_current_"), (3, "stat_target_")):
                ttk.Entry(right, textvariable=self.var(prefix + attr, 10), width=7).grid(
                    row=row, column=col, padx=10, pady=5
                )
        ttk.Button(right, text="Calculer depuis ces attributs", command=self.calculate_stats).grid(
            row=9, column=0, columnspan=4, sticky="ew", pady=10
        )
        self.level_result = tk.StringVar(self)
        ttk.Label(
            p,
            textvariable=self.level_result,
            style="Result.TLabel",
            justify="left",
            wraplength=1020,
        ).pack(anchor="w", pady=20)
        ttk.Label(
            p,
            text="Le début du suivi peut être ton premier niveau enregistré, indépendamment du niveau initial de la classe.\nLes runes déjà dépensées sont les coûts théoriques des niveaux, sans achats ni pertes.",
            style="Muted.TLabel",
            wraplength=1020,
        ).pack(anchor="w")

    def reset_class(self):
        info = CLASS_DATA[self.class_name()]
        for attr in ATTRIBUTES:
            self.base_labels[attr].configure(text=info["stats"][attr])
            for prefix in ("stat_current_", "stat_target_"):
                self.fields[prefix + attr].set(info["stats"][attr])
        self.fields["level_current"].set(info["level"])
        self.fields["level_origin"].set(info["level"])
        try:
            target = max(info["level"], int(self.fields["level_target"].get()))
        except ValueError:
            target = info["level"]
        self.fields["level_target"].set(target)
        self.calculate_levels()

    def level_values(self):
        return level_plan(
            self.db,
            self.class_name(),
            self.fields["level_current"].get(),
            self.fields["level_target"].get(),
            self.fields["level_origin"].get(),
        )

    @guarded
    def calculate_levels(self):
        plan = self.level_values()
        self.level_result.set(
            f"Niveau {plan['current']} → {plan['target']}   •   {plan['missing_levels']} niveaux restants\n"
            f"À payer : {fmt(plan['remaining'])} runes\nDéjà dépensé depuis le début du suivi : {fmt(plan['spent_tracking'])} runes\n"
            f"Depuis la classe de départ : {fmt(plan['spent_class'])} runes\nDu niveau actuel au niveau 713 : {fmt(plan['to_max'])} runes"
        )

    @guarded
    def calculate_stats(self):
        name = self.class_name()
        current = stats_level(name, {a: self.fields["stat_current_" + a].get() for a in ATTRIBUTES})
        target = stats_level(name, {a: self.fields["stat_target_" + a].get() for a in ATTRIBUTES})
        if target < current:
            raise ValueError(
                "Les attributs cibles nécessitent une réattribution, sans niveau supérieur."
            )
        level_plan(self.db, name, current, target, self.fields["level_origin"].get())
        decreased = [
            LABELS[a]
            for a in ATTRIBUTES
            if int(self.fields["stat_target_" + a].get())
            < int(self.fields["stat_current_" + a].get())
        ]
        self.fields["level_current"].set(current)
        self.fields["level_target"].set(target)
        self.calculate_levels()
        if decreased:
            self.level_result.set(
                self.level_result.get()
                + "\nRéattribution nécessaire : "
                + ", ".join(decreased)
                + " (larme larvaire non comprise)."
            )

    @guarded
    def level_budget(self):
        plan = self.level_values()
        level, remainder = self.db.affordable_level(plan["current"], self.fields["wallet"].get())
        self.level_result.set(
            f"Budget disponible → niveau {level}, soit {level-plan['current']} niveaux gagnés.\nReste : {fmt(remainder)} runes."
        )

    def build_weapons(self):
        p = self.pages["Catalogue & armes"]
        self.heading(
            p,
            "Toutes tes armes, un seul plan",
            f"{len(self.db.weapons)} entrées du fichier fourni, dont le DLC. Noms anglais. Sélection multiple avec Ctrl ou Maj.",
        )
        search = ttk.Frame(p)
        search.pack(fill="x")
        ttk.Label(search, text="Rechercher").pack(side="left")
        ttk.Entry(search, textvariable=self.var("search"), width=32).pack(side="left", padx=10)
        ttk.Combobox(
            search,
            textvariable=self.var("category", "Toutes"),
            values=["Toutes"] + list(self.db.categories.values()),
            state="readonly",
            width=24,
        ).pack(side="left")
        ttk.Combobox(
            search,
            textvariable=self.var("dlc_filter", "Tout"),
            values=ENUMS["dlc_filter"],
            state="readonly",
            width=16,
        ).pack(side="left", padx=10)
        for key in ("search", "category", "dlc_filter"):
            self.fields[key].trace_add("write", lambda *_: self.refresh_catalogue())
        self.catalogue = self.tree(
            p,
            ("Arme", "Catégorie", "Type", "Max", "Forge +1", "DLC"),
            (320, 210, 90, 60, 100, 60),
            10,
        )
        self.catalogue.bind("<<TreeviewSelect>>", self.weapon_selected)
        options = ttk.Frame(p)
        options.pack(fill="x")
        for col, (key, label, default) in enumerate(
            (
                ("weapon_current", "Actuel +", 0),
                ("weapon_target", "Cible +", 24),
                ("weapon_quantity", "Exemplaires", 1),
                ("weapon_budget", "Budget", 150000),
            )
        ):
            ttk.Label(options, text=label).grid(row=0, column=col * 2, padx=(0, 8))
            ttk.Entry(options, textvariable=self.var(key, default), width=9).grid(
                row=0, column=col * 2 + 1, padx=(0, 16)
            )
        actions = ttk.Frame(p)
        actions.pack(fill="x", pady=10)
        for text, callback in (
            ("Chiffrer la sélection", self.preview_weapons),
            ("Ajouter la sélection au panier", self.add_weapons),
            ("Amélioration atteignable (1 arme)", self.weapon_budget),
        ):
            ttk.Button(actions, text=text, command=callback).pack(side="left", padx=(0, 8))
        self.weapon_result = tk.StringVar(self, "Choisis une ou plusieurs armes.")
        ttk.Label(p, textvariable=self.weapon_result, style="Result.TLabel", wraplength=1020).pack(
            anchor="w", pady=8
        )
        ttk.Label(
            p,
            text="Sélection mixte : la cible est plafonnée au maximum de chaque arme (ex. +25 → +10 sombre).\nLe coût de forge passé est calculé depuis +0 ; l'achat passé de pierres n'est pas connu.",
            style="Muted.TLabel",
        ).pack(anchor="w")

    def refresh_catalogue(self):
        if not hasattr(self, "catalogue"):
            return
        selected = set(self.catalogue.selection())
        self.catalogue.delete(*self.catalogue.get_children())
        query, category, dlc = (self.fields[k].get() for k in ("search", "category", "dlc_filter"))
        for name, w in sorted(self.db.weapons.items()):
            cat = self.db.categories[w.category]
            if query.casefold() not in name.casefold() or (
                category != "Toutes" and category != cat
            ):
                continue
            if (dlc == "DLC" and not w.dlc) or (dlc == "Jeu de base" and w.dlc):
                continue
            self.catalogue.insert(
                "",
                "end",
                iid=name,
                values=(
                    name,
                    cat,
                    "Fixe" if not w.maximum else "Sombre" if w.kind == "somber" else "Normale",
                    f"+{w.maximum}",
                    "—" if w.base is None else fmt(w.base),
                    "Oui" if w.dlc else "Non",
                ),
            )
        self.catalogue.selection_set([n for n in selected if self.catalogue.exists(n)])

    def weapon_selected(self, _=None):
        selection = self.catalogue.selection()
        if len(selection) == 1:
            self.fields["weapon_target"].set(self.db.weapons[selection[0]].maximum)

    def selected_items(self):
        selection = self.catalogue.selection()
        if not selection:
            raise ValueError("Sélectionne au moins une arme.")
        current = integer(self.fields["weapon_current"].get())
        target = integer(self.fields["weapon_target"].get(), "Cible", current, 25)
        quantity = integer(self.fields["weapon_quantity"].get(), "Exemplaires", 1, 999)
        items = []
        for name in selection:
            w = self.db.weapons[name]
            if current > w.maximum:
                raise ValueError(f"{name} ne peut pas être à +{current}.")
            items.append(
                {
                    "name": name,
                    "custom": False,
                    "current": current,
                    "target": min(target, w.maximum),
                    "quantity": quantity,
                }
            )
        return items

    def resolved(self, items=None):
        result = []
        for item in self.items if items is None else items:
            w = (
                generic_weapon(item["name"], item["kind"], item["base"])
                if item.get("custom")
                else self.db.weapons[item["name"]]
            )
            result.append({**item, "weapon": w})
        return result

    def options(self):
        return {
            "owned": self.inventory,
            "prices": self.prices,
            "normal_bearings": integer(
                self.fields["normal_bearings"].get(), "Perles normales", 0, 4
            ),
            "somber_bearings": integer(
                self.fields["somber_bearings"].get(), "Perles sombres", 0, 5
            ),
        }

    @guarded
    def preview_weapons(self):
        result = shopping_plan(self.resolved(self.selected_items()), **self.options())
        self.weapon_result.set(
            f"Forge restante : {fmt(result['forge'])}  •  Pierres : {fmt(result['stones_cost'])}\nTotal chiffré : {fmt(result['total'])} runes  •  Forge passée : {fmt(result['past_forge'])}\n"
            + (
                "Approvisionnement chiffré."
                if result["complete"]
                else "Matériaux à obtenir / prix à renseigner : voir le panier."
            )
        )

    @guarded
    def add_weapons(self):
        items = self.selected_items()
        self.items.extend(items)
        self.update_plan()
        self.weapon_result.set(f"{len(items)} ligne(s) ajoutée(s) au panier.")

    @guarded
    def weapon_budget(self):
        items = self.selected_items()
        if len(items) != 1 or items[0]["quantity"] != 1:
            raise ValueError("Sélectionne une arme et un exemplaire pour ce calcul.")
        item = self.resolved(items)[0]
        target, remainder = affordable_weapon(
            item["weapon"], item["current"], self.fields["weapon_budget"].get(), **self.options()
        )
        self.weapon_result.set(
            f"Amélioration atteignable avec les matériaux accessibles : +{target}\nReste : {fmt(remainder)} runes. Le stock et les prix des pierres de dragon conditionnent le dernier passage."
        )

    def build_inverse(self):
        p = self.pages["Calcul inverse"]
        self.heading(
            p,
            "Retrouver le coût de base",
            "Entre un prix de forge observé entre deux améliorations. Exclue l'achat des pierres. Plusieurs armes peuvent partager le même prix.",
        )
        form = ttk.Frame(p)
        form.pack(anchor="w")
        self.combo(form, "Profil standard", "custom_kind", "Normale", ENUMS["custom_kind"], 0)
        for row, (label, key, default) in enumerate(
            (
                ("Nom de ton arme", "custom_name", "Mon arme"),
                ("Prix +0 → +1 (si connu)", "custom_base", 100),
                ("Départ de l'observation +", "inverse_current", 4),
                ("Arrivée de l'observation +", "inverse_target", 5),
                ("Total de forge observé", "inverse_cost", 180),
            ),
            1,
        ):
            self.entry(form, label, key, default, row, 28 if key == "custom_name" else 14)
        ttk.Button(
            form, text="Retrouver la base et les armes compatibles", command=self.calculate_inverse
        ).grid(row=6, column=0, columnspan=2, sticky="ew", pady=12)
        self.entry(form, "Actuel + (plan personnalisé)", "custom_current", 0, 7)
        self.entry(form, "Cible + (plan personnalisé)", "custom_target", 24, 8)
        ttk.Button(
            form, text="Ajouter l'arme personnalisée au panier", command=self.add_custom
        ).grid(row=9, column=0, columnspan=2, sticky="ew", pady=12)
        self.inverse_result = tk.StringVar(self)
        ttk.Label(p, textvariable=self.inverse_result, style="Result.TLabel", wraplength=1020).pack(
            anchor="w", pady=12
        )
        ttk.Label(
            p,
            text="Les profils standards sont des hypothèses pour une arme absente du catalogue. Certaines arbalètes et balistes suivent d'autres tarifs.\nPour une arme connue, sélectionne son nom dans le catalogue : chaque passage y suit le JSON fourni.",
            style="Muted.TLabel",
            wraplength=1020,
        ).pack(anchor="w")

    @guarded
    def calculate_inverse(self):
        kind = "normal" if self.fields["custom_kind"].get() == "Normale" else "somber"
        maximum = 25 if kind == "normal" else 10
        current = integer(self.fields["inverse_current"].get(), "Départ", 0, maximum - 1)
        target = integer(self.fields["inverse_target"].get(), "Arrivée", current + 1, maximum)
        cost = integer(self.fields["inverse_cost"].get(), "Prix observé", 1)
        bases = inverse_base(kind, current, target, cost)
        matches = [
            w.name
            for w in self.db.weapons.values()
            if w.maximum == maximum and sum(w.costs[current:target]) == cost
        ]
        if len(bases) == 1:
            self.fields["custom_base"].set(bases[0])
        self.inverse_result.set(
            "Base(s) compatibles avec le profil standard : "
            + (", ".join(map(str, bases)) or "aucune")
            + "\nArmes compatibles, sans identification certaine : "
            + (", ".join(matches[:14]) or "aucune")
            + (f" … et {len(matches)-14} autres" if len(matches) > 14 else "")
        )

    @guarded
    def add_custom(self):
        kind = "normal" if self.fields["custom_kind"].get() == "Normale" else "somber"
        base = integer(self.fields["custom_base"].get(), "Base", 1)
        name = self.fields["custom_name"].get().strip()
        if name in self.db.weapons:
            raise ValueError(
                "Ce nom existe dans le catalogue : utilise ses tarifs exacts dans l'onglet Catalogue."
            )
        w = generic_weapon(name, kind, base)
        current = integer(self.fields["custom_current"].get(), "Actuel", 0, w.maximum)
        target = integer(self.fields["custom_target"].get(), "Cible", current, w.maximum)
        self.items.append(
            {
                "name": w.name,
                "custom": True,
                "kind": kind,
                "base": base,
                "current": current,
                "target": target,
                "quantity": 1,
            }
        )
        self.update_plan()
        self.inverse_result.set("Arme personnalisée ajoutée avec un profil standard.")

    def build_plan(self):
        p = self.pages["Panier & pierres"]
        self.heading(
            p,
            "Le coût de ton projet complet",
            "Personnage + armes + achats libres. Le stock de pierres est partagé et déduit une seule fois pour tout le panier.",
        )
        settings = ttk.Frame(p)
        settings.pack(fill="x")
        self.combo(
            settings,
            "Perles normales obtenues (dans l'ordre)",
            "normal_bearings",
            4,
            tuple(range(5)),
            0,
            5,
        )
        self.combo(
            settings,
            "Perles sombres obtenues (dans l'ordre)",
            "somber_bearings",
            5,
            tuple(range(6)),
            1,
            5,
        )
        ttk.Button(settings, text="Actualiser le total", command=self.update_plan).grid(
            row=0, column=2, rowspan=2, padx=18
        )
        ttk.Button(settings, text="Exporter le bilan CSV…", command=self.export_csv).grid(
            row=0, column=3, rowspan=2
        )
        self.cart = self.tree(
            p,
            ("Objet / arme", "Actuel", "Cible", "Qté", "Forge / achat", "Forge passée"),
            (350, 70, 70, 50, 130, 140),
            4,
        )
        actions = ttk.Frame(p)
        actions.pack(fill="x")
        ttk.Button(actions, text="Retirer la sélection", command=self.remove_items).pack(
            side="left"
        )
        ttk.Button(actions, text="Ajouter un achat libre…", command=self.extra_dialog).pack(
            side="left", padx=8
        )
        self.stock = self.tree(
            p,
            ("Pierre", "Besoin", "Stock", "Manque", "Prix unitaire", "Runes", "Accès / statut"),
            (265, 60, 60, 60, 100, 100, 240),
            6,
        )
        self.stock.bind("<Double-1>", lambda _: self.edit_stock())
        ttk.Button(
            p, text="Modifier le stock / prix de la pierre sélectionnée…", command=self.edit_stock
        ).pack(anchor="w")
        self.plan_result = tk.StringVar(self)
        ttk.Label(p, textvariable=self.plan_result, style="Result.TLabel", wraplength=1020).pack(
            anchor="w", pady=12
        )

    def compute_plan(self):
        level = self.level_values()
        result = shopping_plan(self.resolved(), extras=self.extras, **self.options())
        return {
            **result,
            "level_cost": level["remaining"],
            "combined": level["remaining"] + result["total"],
        }

    @guarded
    def update_plan(self):
        if not hasattr(self, "cart"):
            return
        result = self.compute_plan()
        wallet = integer(self.fields["wallet"].get(), "Runes en poche")
        self.last_plan = result
        self.cart.delete(*self.cart.get_children())
        for index, line in enumerate(result["lines"]):
            suffix = " [profil standard]" if self.items[index].get("custom") else ""
            self.cart.insert(
                "",
                "end",
                iid=f"w{index}",
                values=(
                    line["name"] + suffix,
                    f"+{line['current']}",
                    f"+{line['target']}",
                    line["quantity"],
                    fmt(line["forge"]),
                    fmt(line["past_forge"]),
                ),
            )
        for index, extra in enumerate(self.extras):
            self.cart.insert(
                "",
                "end",
                iid=f"e{index}",
                values=(
                    extra["name"],
                    "—",
                    "—",
                    extra["quantity"],
                    fmt(extra["quantity"] * extra["unit"]),
                    "Inconnu",
                ),
            )
        self.refresh_inventory(result)
        self.plan_result.set(
            f"Niveaux : {fmt(result['level_cost'])}  •  Forge : {fmt(result['forge'])}  •  Pierres : {fmt(result['stones_cost'])}  •  Achats : {fmt(result['extras'])}\n"
            f"Total chiffré : {fmt(result['combined'])} runes   /   À farmer après déduction des runes en poche : {fmt(max(0,result['combined']-wallet))}\n"
            + (
                "Approvisionnement chiffré avec tes paramètres."
                if result["complete"]
                else "BILAN INCOMPLET : pierres manquantes sans prix ou sans perle. Les coûts inconnus ne sont pas inclus."
            )
        )

    def refresh_inventory(self, plan):
        lookup = {s["key"]: s for s in plan["stones"]}
        self.stock.delete(*self.stock.get_children())
        for key, default in STONE_PRICES.items():
            s = lookup.get(key)
            unit = self.prices.get(key, default)
            status = "Non requis"
            if s:
                status = (
                    "Stock suffisant"
                    if not s["missing"]
                    else (
                        "À obtenir / renseigner"
                        if s["unresolved"]
                        else "Prix manuel" if key in self.prices else "Perle débloquée"
                    )
                )
            self.stock.insert(
                "",
                "end",
                iid=key,
                values=(
                    stone_label(key),
                    s["required"] if s else 0,
                    self.inventory.get(key, 0),
                    s["missing"] if s else 0,
                    "?" if unit is None else fmt(unit),
                    fmt(s["cost"]) if s else 0,
                    status,
                ),
            )

    @guarded
    def remove_items(self):
        selected = self.cart.selection()
        for prefix, items in (("w", self.items), ("e", self.extras)):
            for index in sorted(
                (int(i[1:]) for i in selected if i.startswith(prefix)), reverse=True
            ):
                items.pop(index)
        self.update_plan()

    def dialog(self, title, fields, accept, note=""):
        win = tk.Toplevel(self)
        win.title(title)
        win.configure(bg="#101719")
        win.transient(self)
        variables = []
        for row, (label, default) in enumerate(fields):
            ttk.Label(win, text=label).grid(row=row, column=0, padx=16, pady=9)
            var = tk.StringVar(win, str(default))
            ttk.Entry(win, textvariable=var, width=24).grid(row=row, column=1, padx=16)
            variables.append(var)
        if note:
            ttk.Label(win, text=note, style="Muted.TLabel").grid(
                row=len(fields), column=0, columnspan=2, padx=16, pady=12
            )

        @guarded
        def apply(app):
            accept([v.get() for v in variables])
            app.update_plan()
            win.destroy()

        ttk.Button(win, text="Appliquer", command=lambda: apply(self)).grid(
            row=len(fields) + 1, column=0, columnspan=2, pady=12
        )

    def extra_dialog(self):
        def accept(values):
            name, quantity, unit = values
            if not name.strip():
                raise ValueError("Nom requis.")
            self.extras.append(
                {
                    "name": name.strip(),
                    "quantity": integer(quantity, "Quantité", 1),
                    "unit": integer(unit, "Prix"),
                }
            )

        self.dialog(
            "Achat libre",
            (("Objet", "Consommable"), ("Quantité", 1), ("Prix unitaire en runes", 0)),
            accept,
        )

    @guarded
    def edit_stock(self):
        selection = self.stock.selection()
        if not selection:
            raise ValueError("Sélectionne une pierre.")
        key = selection[0]

        def accept(values):
            count = integer(values[0], "Stock")
            price = integer(values[1], "Prix") if values[1].strip() else None
            self.inventory[key] = count
            if price is None:
                self.prices.pop(key, None)
            else:
                self.prices[key] = price

        self.dialog(
            stone_label(key),
            (
                ("Stock déjà possédé", self.inventory.get(key, 0)),
                ("Prix manuel (vide = défaut)", self.prices.get(key, "")),
            ),
            accept,
            "Un prix manuel suppose une source accessible.\nLes pierres de dragon ont une disponibilité limitée.",
        )

    def build_farm(self):
        p = self.pages["Farm"]
        self.heading(
            p,
            "Une minute de mesure, ton temps de farm",
            "Note tes runes avant et après : la différence suffit, sans devoir mourir. Inclus les trajets et retours à la grâce.",
        )
        body = ttk.Frame(p)
        body.pack(fill="x")
        form = ttk.Frame(body)
        form.pack(side="left", anchor="n", padx=(0, 30))
        for row, (label, key, default) in enumerate(
            (
                ("Runes récoltées pendant le test", "farm_runes", 50000),
                ("Durée réellement mesurée (secondes)", "farm_seconds", 60),
                ("Rendement soutenu (%)", "farm_efficiency", 100),
            )
        ):
            self.entry(form, label, key, default, row)
        self.combo(form, "Objectif", "farm_goal", "Projet complet", ENUMS["farm_goal"], 3)
        self.entry(form, "Objectif libre (runes)", "farm_custom_goal", 100000, 4)
        self.combo(form, "Talisman du test", "farm_talisman", "Aucun", ENUMS["farm_talisman"], 5)
        self.combo(
            form, "Consommable du test", "farm_consumable", "Aucun", ENUMS["farm_consumable"], 6, 35
        )
        self.entry(form, "Méthode / autres buffs (facultatif)", "farm_notes", "", 7, 35)
        ttk.Button(form, text="Estimer le temps nécessaire", command=self.calculate_farm).grid(
            row=8, column=0, columnspan=2, sticky="ew", pady=16
        )
        timer = ttk.LabelFrame(body, text="Chronomètre · test de 60 secondes", padding=24)
        timer.pack(side="left", fill="both", expand=True, anchor="n")
        self.timer_label = tk.StringVar(self, "01:00")
        ttk.Label(timer, textvariable=self.timer_label, style="Title.TLabel").pack(pady=16)
        ttk.Button(timer, text="Démarrer une minute", command=self.start_timer).pack(
            fill="x", pady=5
        )
        ttk.Button(timer, text="Arrêter et garder la durée", command=self.stop_timer).pack(
            fill="x", pady=5
        )
        ttk.Label(
            timer,
            text="Le chronomètre continue dans les autres onglets.\nSaisis les runes récoltées à la fin du test.\nL'application ne lit pas le jeu.",
            style="Muted.TLabel",
            wraplength=320,
        ).pack(pady=18)
        self.farm_result = tk.StringVar(self)
        ttk.Label(p, textvariable=self.farm_result, style="Result.TLabel", wraplength=1020).pack(
            anchor="w", pady=18
        )
        ttk.Label(
            p,
            text="Le gain mesuré inclut déjà tes buffs : ils ne sont pas appliqués une seconde fois. Les effets argentés augmentent la découverte d'objets, pas les runes.\nEstimation à méthode et buffs constants. Le rendement soutenu permet de tenir compte des pauses et interruptions.",
            style="Muted.TLabel",
            wraplength=1020,
        ).pack(anchor="w")

    def start_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.timer_started = time.monotonic()
        self.deadline = self.timer_started + 60
        self.tick()

    def tick(self):
        remaining = max(0, math.ceil(self.deadline - time.monotonic()))
        self.timer_label.set(f"{remaining//60:02d}:{remaining%60:02d}")
        if remaining:
            self.timer_job = self.after(100, self.tick)
        else:
            self.timer_job = self.deadline = None
            self.fields["farm_seconds"].set(60)
            self.timer_label.set("Test terminé")
            self.bell()

    def stop_timer(self):
        if self.deadline is None:
            return
        if self.timer_job:
            self.after_cancel(self.timer_job)
        elapsed = min(60, max(1, round(time.monotonic() - self.timer_started)))
        self.fields["farm_seconds"].set(elapsed)
        self.timer_label.set(f"Arrêté : {elapsed} s")
        self.deadline = self.timer_job = None

    @guarded
    def calculate_farm(self):
        result = self.compute_plan()
        level = self.level_values()
        goal = self.fields["farm_goal"].get()
        goals = {
            "Projet complet": result["combined"],
            "Niveaux visés": level["remaining"],
            "Panier armes / achats": result["total"],
            "Niveau maximum 713": level["to_max"],
        }
        needed = (
            integer(self.fields["farm_custom_goal"].get(), "Objectif")
            if goal == "Objectif libre"
            else goals[goal]
        )
        args = (self.fields["farm_runes"].get(), self.fields["farm_seconds"].get())
        options = {
            "wallet": self.fields["wallet"].get(),
            "efficiency": self.fields["farm_efficiency"].get(),
        }
        estimate = farm_estimate(*args, needed, **options)
        maximum = farm_estimate(*args, level["to_max"], **options)
        self.farm_result.set(
            f"Rendement : {fmt(round(estimate['runes_per_minute']))} runes/min\n{goal} : {fmt(estimate['remaining'])} runes à récolter → {duration_label(estimate['seconds'])}\n"
            f"Du niveau actuel au niveau 713 : {duration_label(maximum['seconds'])}"
            + (
                "\nSous-total connu seulement : des matériaux restent à chiffrer/obtenir."
                if not result["complete"] and goal in ("Projet complet", "Panier armes / achats")
                else ""
            )
        )

    def build_help(self):
        p = self.pages["Données & aide"]
        self.heading(
            p,
            "Des coûts traçables, un projet portable",
            "Le fichier fourni reste intact. Voir aussi README.md et docs/SOURCES.md.",
        )
        frame = ttk.Frame(p)
        frame.pack(fill="both", expand=True)
        text = tk.Text(
            frame,
            wrap="word",
            bg="#172321",
            fg="#edf0eb",
            font=("Segoe UI", 11),
            relief="flat",
            padx=20,
            pady=18,
        )
        text.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, command=text.yview)
        scroll.pack(side="right", fill="y")
        text.configure(yscrollcommand=scroll.set)
        text.insert(
            "1.0",
            f"AUTO ELDEN RING  {__version__}\n\n{len(self.db.weapons)} objets • {len(self.db.categories)} catégories • 712 passages de niveau\nRégulation déclarée : {self.db.metadata['regulation_version']}\n\n"
            "UTILISATION\n1. Personnage : classe, niveau actuel/cible ou huit attributs permanents.\n2. Catalogue : noms anglais, sélection multiple, ajout au panier.\n"
            "3. Panier : perles de mineur et stock de pierres. Double-clique une pierre pour son stock/prix.\n4. Farm : mesure un gain réel sur 60 s, puis estime le temps nécessaire.\n"
            "5. Enregistre le projet JSON pour reprendre tes saisies, panier, inventaire et mesure. Exporte le bilan CSV.\n\n"
            "PRIX ET MATÉRIAUX\nLe prix +0 → +1 est le paiement au forgeron, pas l'achat de l'arme.\nLes coûts d'amélioration sont ceux du JSON fourni, sans approximation par formule pour les armes connues.\n"
            "Une arme normale demande 12 pierres de chaque palier [1–8] jusqu'à +24 ; une sombre une pierre de chaque palier [1–9] jusqu'à +9.\n"
            "Les derniers passages +25 / +10 demandent une pierre de dragon ancienne normale/sombre, disponible en quantité limitée.\n"
            "Les perles de mineur ne vendent pas ces pierres finales à l'infini. Leur prix reste inconnu sans stock ou source avec prix manuel.\n"
            "Les perles sont supposées obtenues dans l'ordre. Un prix manuel suppose une source accessible, sans garantir sa disponibilité.\n"
            "Le suivi passé des armes compte uniquement la forge depuis +0. Il ne permet pas de distinguer les pierres trouvées des pierres achetées.\n\n"
            "NIVEAUX\nChaque attribut est plafonné à 99 et ne peut descendre sous celui de la classe. Une réattribution peut nécessiter une larme larvaire.\n"
            "Le début du suivi est un niveau libre entre celui de la classe et le niveau actuel. Il sert au calcul des runes dépensées depuis ton propre point de départ.\n"
            "Le niveau peut être saisi directement ; le bouton « Calculer depuis ces attributs » synchronise le niveau avec les statistiques.\n\n"
            "PÉRIMÈTRE\nCette version calcule les runes, niveaux, améliorations, matériaux, budgets, achats libres et temps de farm.\n"
            "Le JSON ne contient pas les dégâts, affinités, résistances, poids, sorts ou recettes : ces calculs ne sont pas implémentés.\n"
            "Les noms sont en anglais. Certaines entrées des paramètres peuvent ne pas être accessibles dans ton édition. Le DLC est celui indiqué par le JSON.\n"
            "Application indépendante, sans connexion ni lecture du jeu. Les sources ci-dessous sont celles déclarées dans le fichier fourni.\n\n"
            + "\n".join(f"{k} : {v}" for k, v in self.db.metadata["sources"].items()),
        )
        text.configure(state="disabled")

    def project_data(self):
        return {
            "fields": {k: v.get() for k, v in self.fields.items()},
            "items": self.items,
            "extras": self.extras,
            "inventory": self.inventory,
            "prices": self.prices,
        }

    def validate_fields(self, fields):
        if set(fields) != set(self.fields):
            raise ValueError("Liste de champs incompatible avec cette version.")
        name = next((k for k, v in CLASSES_FR.items() if v == fields["class"]), None)
        level_plan(
            self.db, name, fields["level_current"], fields["level_target"], fields["level_origin"]
        )
        for prefix in ("stat_current_", "stat_target_"):
            stats_level(name, {a: fields[prefix + a] for a in ATTRIBUTES})
        bounds = {
            "normal_bearings": (0, 4),
            "somber_bearings": (0, 5),
            "farm_efficiency": (1, 100),
            "weapon_current": (0, 25),
            "weapon_target": (0, 25),
            "weapon_quantity": (1, 999),
            "custom_current": (0, 25),
            "custom_target": (0, 25),
            "inverse_current": (0, 24),
            "inverse_target": (1, 25),
            "farm_seconds": (1, None),
            "farm_runes": (1, None),
            "custom_base": (1, None),
            "inverse_cost": (1, None),
            "wallet": (0, None),
            "weapon_budget": (0, None),
            "farm_custom_goal": (0, None),
        }
        for key, (low, high) in bounds.items():
            integer(fields[key], key, low, high)
        enums = {**ENUMS, "category": ["Toutes"] + list(self.db.categories.values())}
        for key, values in enums.items():
            if fields[key] not in values:
                raise ValueError(f"Choix invalide : {key}")

    @guarded
    def save(self):
        self.validate_fields({k: v.get() for k, v in self.fields.items()})
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".json",
            initialfile="mon-build.auto-elden.json",
            filetypes=[("Projet Auto Elden Ring", "*.json")],
        )
        if path:
            save_project(path, self.project_data(), self.db)

    def apply_project(self, data):
        # Validation completes before replacing the active session.
        self.validate_fields(data["fields"])
        self.stop_timer()
        self.items, self.extras = data["items"], data["extras"]
        self.inventory, self.prices = data["inventory"], data["prices"]
        for key, value in data["fields"].items():
            self.fields[key].set(value)
        for attr, label in self.base_labels.items():
            label.configure(text=CLASS_DATA[self.class_name()]["stats"][attr])
        self.refresh_catalogue()
        self.calculate_levels()
        self.update_plan()

    @guarded
    def load(self):
        path = filedialog.askopenfilename(
            parent=self, filetypes=[("Projet Auto Elden Ring", "*.json")]
        )
        if path:
            self.apply_project(load_project(path, self.db))

    def write_csv(self, path):
        result = self.compute_plan()

        def safe_name(name):
            return "'" + name if name.startswith(("=", "+", "-", "@")) else name

        with open(path, "w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream, delimiter=";")
            writer.writerow(
                ["Auto Elden Ring", __version__, self.db.metadata["regulation_version"]]
            )
            writer.writerow(["Approvisionnement complet", result["complete"]])
            writer.writerow(["Niveaux", result["level_cost"]])
            writer.writerow(
                ["Arme", "Actuel", "Cible", "Quantité", "Forge restante", "Forge passée"]
            )
            for line in result["lines"]:
                writer.writerow(
                    [
                        safe_name(line["name"]),
                        line["current"],
                        line["target"],
                        line["quantity"],
                        line["forge"],
                        line["past_forge"],
                    ]
                )
            writer.writerow(
                ["Pierre", "Besoin", "Stock utilisé", "Manque", "Prix", "Coût connu", "À résoudre"]
            )
            for s in result["stones"]:
                writer.writerow(
                    [
                        stone_label(s["key"]),
                        s["required"],
                        s["used"],
                        s["missing"],
                        s["unit"],
                        s["cost"],
                        s["unresolved"],
                    ]
                )
            writer.writerow(["Achat libre", "Quantité", "Prix unitaire", "Total"])
            for e in self.extras:
                writer.writerow(
                    [safe_name(e["name"]), e["quantity"], e["unit"], e["quantity"] * e["unit"]]
                )
            writer.writerow(["Total chiffré", result["combined"]])
            writer.writerow(
                ["À farmer", max(0, result["combined"] - integer(self.fields["wallet"].get()))]
            )

    @guarded
    def export_csv(self):
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            initialfile="bilan-auto-elden.csv",
            filetypes=[("CSV", "*.csv")],
        )
        if path:
            self.write_csv(path)


def run():
    App().mainloop()
