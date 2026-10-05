"""Profile selection, local menus, illustrated snapshots and compact workflows."""

from copy import deepcopy
from collections import OrderedDict
import math
import json
from functools import lru_cache
import time
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from classes_data import ATTRIBUTES
from .core import integer, resource_path
from .profiles import timestamp
from .windows import monitor_workarea, snap_position, position_window


@lru_cache(maxsize=1)
def item_catalogue():
    return json.loads(resource_path("assets/item_catalogue.json").read_text(encoding="utf-8"))[
        "items"
    ]


class JourneyFeatures:
    def modal(self, window):
        window._previous_grab = self.grab_current()
        window.grab_set()

    def rgb_notice(self):
        if self._closing or self.data["style"] != "rainbow":
            return
        window = self.popup(self.t("rgb_beta"), "650x300")
        self.rgb_notice_panel = window
        self.label(window, "RGB", 30).pack(pady=(22, 8))
        self.label(window, self.t("rgb_beta_hint"), 16, wraplength=580, justify="left").pack(
            padx=24, pady=18
        )
        self.button(window, "done", window.destroy).pack(pady=12)
        return window

    def show_profile_picker(self, startup=False):
        current = getattr(self, "profile_picker", None)
        if current is not None and current.winfo_exists():
            current.lift()
            return current
        self.commit_current()
        self.profile_selection_pending = True
        self.profiles.sync(self.data)
        window = self.popup(self.t("choose_profile"), "820x650")
        self.profile_picker = window
        if startup:
            self.profile_sidebar_hidden = True
            self.sidebar.grid_remove()
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=0)
            self.host.grid_configure(column=0, columnspan=2)
            window.heading.pack_forget()
        self.label(window, self.t("choose_profile"), 26).pack(pady=(24, 8))
        self.label(window, self.t("profile_hint"), muted=True, wraplength=740).pack(pady=8)
        actions = ctk.CTkFrame(window, fg_color="transparent")
        actions.pack(pady=14)
        self.button(actions, "new_character", self.new_profile).pack(side="left", padx=6)
        self.button(actions, "import_save", self.import_dialog, True).pack(side="left", padx=6)
        scroll = ctk.CTkScrollableFrame(window, fg_color=self.bg)
        scroll.pack(fill="both", expand=True, padx=22, pady=18)
        window.profile_cards = {}
        for ident, profile in self.profiles.data["profiles"].items():
            state = profile["state"]
            if not state["profile_created"]:
                continue
            card = self.card(scroll)
            card.pack(fill="x", pady=6)
            self.label(card, state["character_name"][:1].upper(), 30).pack(
                side="left", padx=20, pady=14
            )
            title = (
                state["character_name"]
                + "\n"
                + self.t(state["class_name"])
                + " · "
                + self.t("level")
                + " "
                + str(sum(state["stats_current"].values()) - 79)
            )

            def select(i=ident):
                self.page = "character"
                self.activate_profile(self.profiles.select(i))

            button = ctk.CTkButton(
                card,
                text=title,
                font=self.font(16),
                height=68,
                anchor="w",
                fg_color=self.paper,
                text_color=self.ink,
                command=lambda f=select: self.action(f),
            )
            button.pack(fill="x", expand=True, padx=14, pady=10)
            window.profile_cards[ident] = button
        if not window.profile_cards:
            self.label(scroll, self.t("empty_profiles"), muted=True, wraplength=650).pack(pady=35)
        window.back.configure(
            state="disabled" if startup or not self.data["profile_created"] else "normal"
        )

        def back():
            self.profile_selection_pending = False
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", back)
        self.modal(window)
        self.normalize_surfaces(window)
        return window

    def ask_import_policy(self, path, window, status):
        prompt = self.popup(self.t("import_profiles"), "700x350")
        self.label(prompt, self.t("import_policy_hint"), 18, wraplength=620, justify="left").pack(
            padx=25, pady=30
        )

        def choose(replace):
            prompt.destroy()
            self.begin_import(path, window, status, policy="replace" if replace else "keep")

        self.button(prompt, "keep_manual", lambda: choose(False)).pack(pady=8)
        self.button(prompt, "replace_manual", lambda: choose(True), True).pack(pady=8)
        prompt.keep_profiles = lambda: choose(False)
        prompt.replace_profiles = lambda: choose(True)
        self.modal(prompt)
        return prompt

    def import_save_list(self, paths, parent=None):
        window = self.popup(self.t("select_save"), "800x500")
        self.label(window, self.t("save_accounts"), wraplength=730).pack(pady=20)
        scroll = ctk.CTkScrollableFrame(window, fg_color=self.bg)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        self.button(
            window, "import_all_saves", lambda: self.begin_import(paths, window, policy=None)
        ).pack(pady=12)
        for path in paths:
            button = ctk.CTkButton(
                scroll,
                text=path.parent.name + " · " + path.name,
                font=self.font(),
                fg_color=self.soft,
                text_color=self.ink,
                height=42,
                command=lambda p=path: self.begin_import(p, window, policy=None),
            )
            button.pack(fill="x", pady=6)
        return window

    def install_native_menu(self, option):
        """Install cancellation once, without replacing Tk's menu implementation."""
        if getattr(self, "_menu_bindings", False):
            return
        self._menu_bindings = True

        def moved(event):
            if event.widget is not self:
                return
            geometry = (self.winfo_x(), self.winfo_y(), self.winfo_width(), self.winfo_height())
            if geometry != getattr(self, "menu_geometry", None):
                self.dismiss_menu()

        self.bind("<Configure>", moved, add="+")
        self.bind("<Unmap>", lambda e: self.dismiss_menu() if e.widget is self else None, add="+")

    def dismiss_menu(self, event=None):
        """Unpost a native menu; keep it alive with its owning option control."""
        menu = getattr(self, "scroll_menu", None)
        self.scroll_menu = None
        if menu is not None and menu.winfo_exists():
            menu.unpost()
            if self.grab_current() is menu:
                menu.grab_release()

    def open_native_menu(self, option):
        self.install_native_menu(option)
        option._open_dropdown_menu()
        return option._dropdown_menu

    def weapon_icon(self, name, size=52):
        cache = getattr(self, "detail_icons", None)
        if cache is None:
            self.detail_icons = cache = OrderedDict()
        key = (name, size)
        if key not in cache:
            weapon = self.db.weapons[name]
            ident = self.db.raw["weapons_by_category"][weapon.category][name]["id"]
            with Image.open(resource_path(f"assets/catalogue/{ident}.webp")) as source:
                image = source.convert("RGBA")
            cache[key] = ctk.CTkImage(image, size=(size, size))
            while len(cache) > 64:
                cache.popitem(last=False)
        cache.move_to_end(key)
        return cache[key]

    def item_name(self, ident):
        item = item_catalogue().get(str(ident))
        if item:
            return item["names"].get(self.data["language"], item["name"])
        return self.t("unknown_item_id", id=ident)

    def item_icon(self, ident, size=84):
        if not hasattr(self, "item_icons"):
            self.item_icons = OrderedDict()
        key = (ident, size)
        if key not in self.item_icons:
            item = item_catalogue().get(str(ident), {})
            if not item.get("icon"):
                return None
            with Image.open(resource_path(item["icon"])) as source:
                image = source.convert("RGBA")
            self.item_icons[key] = ctk.CTkImage(image, size=(size, size))
            while len(self.item_icons) > 64:
                self.item_icons.popitem(last=False)
        self.item_icons.move_to_end(key)
        return self.item_icons[key]

    def equipment_view(self):
        if not self.data["profile_created"] or self.profile_selection_pending:
            return self.show_profile_picker(startup=True)
        self.commit_current()
        return self.checkpoint_cards(
            {"state": deepcopy(self.data), "date": timestamp(), "note": "equipped"}
        )

    def checkpoint_cards(self, point):
        from .presentation import display_date

        state = point["state"]
        window = self.popup(self.t("view_checkpoint"), "920x740")
        self.label(window, state["character_name"], 28).pack(pady=(18, 6))
        self.label(
            window, display_date(point["date"]) + " · " + self.t(state["class_name"]), muted=True
        ).pack(pady=6)
        body = ctk.CTkScrollableFrame(window, fg_color=self.bg)
        body.pack(fill="both", expand=True, padx=22, pady=14)
        note = self.t(point["note"]) if point["note"] in self.translator.text else point["note"]
        self.label(body, note, 18, wraplength=820).pack(anchor="w", pady=8)
        self.metrics(
            body,
            [
                (self.t("level"), str(sum(state["stats_current"].values()) - 79)),
                (self.t("runes_held"), f'{state["runes"]:,}'),
            ],
        )
        stats = self.card(body)
        stats.pack(fill="x", pady=8)
        for index, key in enumerate(ATTRIBUTES):
            self.label(stats, self.t(key) + "   " + str(state["stats_current"][key]), 16).grid(
                row=index // 4, column=index % 4, sticky="w", padx=20, pady=10
            )
        held = {i["id"]: i["quantity"] for i in state.get("inventory_items", [])}
        bearings = [
            {"id": int(ident), "quantity": held.get(int(ident), 0)}
            for ident, item in item_catalogue().items()
            if "Miner's Bell Bearing" in item["name"]
        ]
        keys = ("equipped", "owned_weapons", "armor", "items", "bearings", "changes", "goal")
        tabs = ctk.CTkSegmentedButton(body, values=[self.t(k) for k in keys], font=self.font())
        tabs.pack(fill="x", pady=14)
        content = ctk.CTkFrame(body, fg_color="transparent")
        content.pack(fill="x")
        window.weapon_cards = {}

        def render(value, offset=0):
            for child in content.winfo_children():
                child.destroy()
            window.weapon_cards = {}
            inventory = {
                self.t("equipped"): state.get("equipment", []),
                self.t("owned_weapons"): state["inventory_weapons"],
                self.t("armor"): state.get("inventory_armor", []),
                self.t("items"): state.get("inventory_items", []),
                self.t("bearings"): bearings,
            }
            if value in inventory:
                all_items = inventory[value]
                items = all_items[offset : offset + 24]
                window.weapon_page_offset = offset
                for index, item in enumerate(items):
                    card = self.card(content)
                    card.grid(row=index // 2, column=index % 2, sticky="ew", padx=5, pady=5)
                    icon = (
                        self.weapon_icon(item["name"], 84)
                        if "name" in item
                        else self.item_icon(item["id"])
                    )
                    if icon:
                        label = self.label(card, "", image=icon)
                        label.pack(side="left", padx=12, pady=12)
                        label.snapshot_icon = icon
                    name = (
                        self.translator.weapon(item["name"])
                        if "name" in item
                        else self.item_name(item["id"])
                    )
                    upgrade = f'+{item["current"]}  ' if "current" in item else ""
                    quantity = f'×{item["quantity"]}' if item["quantity"] else "?"
                    self.label(
                        card, name + "\n" + upgrade + quantity, 16, wraplength=340, justify="left"
                    ).pack(side="left", padx=8, pady=20)
                    if "name" in item:
                        window.weapon_cards[(item["name"], item["current"])] = card
                content.grid_columnconfigure((0, 1), weight=1)
                if value == self.t("bearings"):
                    self.label(content, self.t("bearing_unknown"), 13, True, wraplength=820).grid(
                        row=5, column=0, columnspan=2, pady=14
                    )
                if not items:
                    self.label(content, self.t("empty_equipment"), muted=True, wraplength=800).grid(
                        row=0, column=0, columnspan=2, pady=30
                    )
                if len(all_items) > 24:
                    navigation = ctk.CTkFrame(content, fg_color="transparent")
                    navigation.grid(row=12, column=0, columnspan=2, pady=12)
                    if offset:
                        self.button(
                            navigation,
                            "previous_page",
                            lambda: render(value, max(0, offset - 24)),
                            True,
                        ).pack(side="left", padx=6)
                    if offset + 24 < len(all_items):
                        self.button(
                            navigation, "next_page", lambda: render(value, offset + 24), True
                        ).pack(side="left", padx=6)
            else:
                if value == self.t("changes"):
                    lines = []
                    for change in point.get("changes", []):
                        field = change["field"]
                        if field == "weapon":
                            title = (
                                self.translator.weapon(change["name"]) + f' +{change["upgrade"]}'
                            )
                        elif field == "item":
                            title = self.item_name(change["id"])
                        else:
                            title = self.translator.stone(field) if ":" in field else self.t(field)
                        lines.append(f'{title}: {change["before"]} → {change["after"]}')
                else:
                    lines = [
                        self.t(k) + f': {state["stats_current"][k]} → {state["stats_target"][k]}'
                        for k in ATTRIBUTES
                    ]
                    lines.extend(
                        self.translator.weapon(i["name"])
                        + f'  +{i["current"]} → +{i["target"]} ×{i["quantity"]}'
                        for i in state["selected"]
                    )
                    if state["weapon_mode"] == "manual":
                        m = state["manual"]
                        lines.append(
                            self.t("manual_mode")
                            + f'  +{m["current"]} → +{m["target"]} ×{m["quantity"]}'
                        )
                for line in lines:
                    self.label(content, line, 15, wraplength=820, justify="left").pack(
                        anchor="w", pady=6
                    )
            self.normalize_surfaces(content)

        tabs.configure(command=render)
        tabs.set(self.t("equipped"))
        render(tabs.get())
        window.detail_tabs = tabs
        window.render_tab = render
        self.normalize_surfaces(window)
        return window

    def acknowledge_all_stones(self):
        """Acknowledge possessions independently of the informational wallet."""
        for row in self.planner.weapons()["stones"]:
            if row["missing"] and not row["key"].endswith("dragon"):
                self.planner.purchase(row["key"])
        self.autosave()
        self.refresh_weapons()

    def compact_dashboard(self):
        self.commit_current()
        current = getattr(self, "compact_window", None)
        if current is not None and current.winfo_exists():
            current.lift()
            return current
        for popup in tuple(self.popups):
            popup.destroy()
        if hasattr(self, "gallery"):
            self.gallery.cache.clear()
        window = self.native_popup(self.t("small_mode"), "430x630")
        self.compact_window = window
        window.transient("")
        window.overrideredirect(True)
        window.resizable(False, False)
        window.attributes("-topmost", True)
        heading = self.card(window)
        heading.pack(fill="x", padx=8, pady=8)
        title = self.label(heading, self.data["character_name"], 19)
        title.pack(side="left", padx=14, pady=12)
        drag = {}

        def press(event):
            drag.update(x=event.x_root - window.winfo_x(), y=event.y_root - window.winfo_y())

        def move(event):
            if drag:
                position_window(window, event.x_root - drag["x"], event.y_root - drag["y"])

        def snap(_=None):
            x, y = snap_position(
                window.winfo_x(),
                window.winfo_y(),
                window.winfo_width(),
                window.winfo_height(),
                monitor_workarea(window),
            )
            position_window(window, x, y)

        for widget in (heading, title):
            widget.bind("<ButtonPress-1>", press)
            widget.bind("<B1-Motion>", move)
            widget.bind("<ButtonRelease-1>", snap)
        controls = ctk.CTkFrame(window, fg_color="transparent")
        controls.pack(fill="x", padx=12, pady=6)
        mode = tk.StringVar(
            value=self.page if self.page in ("character", "weapons", "farm") else "character"
        )
        body = ctk.CTkFrame(window, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12)
        text = self.label(body, "", wraplength=390, justify="left", size=15)
        text.pack(anchor="w", padx=6, pady=8)
        wallet = self.card(window)
        wallet.pack(fill="x", padx=12, pady=6)
        runes = self.entry(wallet, "runes_held", self.data["runes"], 0, width=145)
        panes = {
            key: ctk.CTkFrame(body, fg_color="transparent")
            for key in ("character", "weapons", "farm")
        }
        materials = ctk.CTkScrollableFrame(panes["weapons"], fg_color=self.bg, height=190)
        materials.pack(fill="both", expand=True)
        window.purchase_rows = {}

        def paint_stones():
            rows = [r for r in self.planner.weapons()["stones"] if not r["key"].endswith("dragon")]
            for row in rows:
                key = row["key"]
                if key not in window.purchase_rows:
                    panel = self.card(materials)
                    panel.pack(fill="x", pady=3)
                    label = self.label(panel, "", 13)
                    label.pack(side="left", padx=10, pady=9)

                    def buy(k=key):
                        self.planner.purchase(k)
                        self.autosave()
                        refresh()

                    button = self.button(panel, "bought", buy, True, width=90)
                    button.pack(side="right", padx=8)
                    window.purchase_rows[key] = {"label": label, "button": button, "buy": buy}
                widgets = window.purchase_rows[key]
                complete = row["missing"] == 0
                widgets["label"].configure(
                    text=("✓ " if complete else "")
                    + self.translator.stone(key)
                    + f' ×{row["missing"]}'
                )
                widgets["button"].configure(
                    state="disabled" if complete else "normal",
                    text="✓" if complete else self.t("bought"),
                    fg_color="#438B64" if complete else self.soft,
                )

        def all_stones():
            self.acknowledge_all_stones()
            refresh()

        self.button(panes["weapons"], "all_stones", all_stones, True).pack(fill="x", pady=7)
        timer = self.label(panes["farm"], "01:00", 30)
        timer.pack(pady=7)
        timer_actions = ctk.CTkFrame(panes["farm"], fg_color="transparent")
        timer_actions.pack()
        baseline = [self.data["runes"]]

        def start():
            baseline[0] = self.data["runes"]
            self.start_timer()

        for key, command in (
            ("mini_start", start),
            ("stop", self.stop_timer),
            ("mini_reset", self.reset_timer),
        ):
            self.button(timer_actions, key, command, True, width=115).pack(side="left", padx=3)
        gain_form = self.card(panes["farm"])
        gain_form.pack(fill="x", pady=8)
        gain = self.entry(gain_form, "measured_runes", 0, 0, width=130)

        def record():
            if self.deadline is not None:
                raise ValueError(self.t("test_finished"))
            measured = integer(gain.get(), "Measured runes", 1)
            f = self.data["farm"]
            seconds = f["seconds"] if self.awaiting_result else 60
            if self.full_index is not None:
                self.farm_vars["runes"].set(str(measured))
                self.record_result()
                refresh()
                return
            self.planner.add_sample(
                measured,
                seconds,
                *(self.timer_buffs if self.awaiting_result else (f["talisman"], f["consumable"])),
            )
            f.update(runes=measured, seconds=seconds)
            self.awaiting_result = False
            self.full_index = None
            self.timer_duration = 60
            if hasattr(self, "farm_vars"):
                for key in ("runes", "seconds"):
                    self.farm_vars[key].set(str(f[key]))
            self.autosave()
            refresh()

        self.button(panes["farm"], "record_result", record).pack(pady=10)

        def refresh():
            c = self.planner.character()
            value = mode.get()
            remaining = c["deficit"]
            detail = self.t(
                "level_route", current=c["current"], target=c["target"], count=c["levels"]
            )
            if value == "weapons":
                w = self.planner.weapons()
                remaining = w["deficit"]
                detail = self.t("total_cost") + ": " + f'{w["total"]:,}'
                paint_stones()
            elif value == "farm":
                goal, _ = self.planner.farm_goal()
                remaining = max(0, goal - self.data["runes"])
                try:
                    detail = (
                        self.t("time_needed")
                        + ": "
                        + self.translator.duration(self.planner.farm_projection()["time"])
                    )
                except ValueError:
                    detail = self.t("new_measurement")
            text.configure(text=detail + "\n" + self.t("to_farm") + ": " + f"{remaining:,}")
            for key, pane in panes.items():
                pane.pack_forget()
                if key == value:
                    pane.pack(fill="both", expand=True)

        def wallet_changed(*_):
            try:
                value = integer(runes.get())
            except ValueError:
                return
            self.data["runes"] = value
            for var in self.wallet_vars.values():
                var.set(str(value))
            if self.deadline is not None or self.awaiting_result:
                gain.set(str(max(0, value - baseline[0])))
            self.autosave()
            refresh()

        runes.trace_add("write", wallet_changed)
        for key in panes:
            self.button(
                controls, key, lambda k=key: (mode.set(k), refresh()), True, width=125
            ).pack(side="left", padx=3)

        def reopen():
            self.deiconify()
            self.show(mode.get())
            window.destroy()
            self.refresh_farm_results()

        window.protocol("WM_DELETE_WINDOW", reopen)
        self.button(window, "full_window", reopen).pack(fill="x", padx=12, pady=10)
        window.rune_var = runes
        window.mode_var = mode
        window.summary_label = text
        window.refresh_summary = refresh
        window.reopen = reopen
        window.snap = snap
        window.gain_var = gain
        window.record_sample = record
        window.start_sample = start
        window.timer_label = timer
        window.all_stones = all_stones

        def pulse():
            remaining = (
                max(0, math.ceil(self.deadline - time.monotonic()))
                if self.deadline
                else (0 if self.awaiting_result else self.timer_duration)
            )
            timer.configure(text=f"{remaining//60:02d}:{remaining%60:02d}")
            window.after(250, pulse)

        refresh()
        self.withdraw()
        window.deiconify()
        window.lift()
        window.after(10, snap)
        pulse()
        self.release_compact_pages()
        return window
