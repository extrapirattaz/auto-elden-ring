"""Calm, offline desktop interface backed by explicit planner transactions."""

from copy import deepcopy
import ctypes
import math
import os
from pathlib import Path
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from .dropdown import NativeOptionMenu
from PIL import Image
from classes_data import CLASS_DATA, ATTRIBUTES
from . import __version__
from .core import Database, STONE_PRICES, integer, resource_path
from .planner import Planner, default_state, validate_state, TALISMANS, CONSUMABLES
from .i18n import Translator, LANGUAGE_NAMES
from .storage import save_project, load_project


from .styles import STYLES, PALETTES, appearance
from .gallery import Gallery
from .profiles import Profiles, timestamp
from .audio import Music
from .windows import load_reading_font, caption_color, cancel_widget_jobs, presentation_transaction


class ManagedWindow(ctk.CTkToplevel):
    # CTk's withdraw/update/reveal cycle can crash Tk during queued resize events.
    _deactivate_windows_window_header_manipulation = True

    def iconbitmap(self, bitmap=None, default=None):
        if bitmap and "CustomTkinter_icon" in str(bitmap):
            bitmap = str(resource_path("assets/app.ico"))
        return super().iconbitmap(bitmap, default)

    def destroy(self):
        if not self.winfo_exists():
            return
        previous = getattr(self, "_previous_grab", None)
        cancel_widget_jobs(self)
        self.master.popups.discard(self)
        super().destroy()
        if previous is not None and not self.master._closing and previous.winfo_exists():
            previous.grab_set()


def fmt(value):
    return f"{value:,.0f}".replace(",", " ")


from .presentation import Features
from .panels import Panel


class App(Features, ctk.CTk):
    _deactivate_windows_window_header_manipulation = True

    def __init__(self, db=None, persist=True, state=None):
        super().__init__()
        if persist:
            self.withdraw()
        self.profile_selection_pending = False
        self.db = db or Database()
        self.persist = persist
        self._closing = False
        self.callback_errors = []
        self.popups = set()
        self.views = {}
        self.wallet_vars = {}
        self.save_job = None
        self.page = "character"
        self.deadline = self.timer_job = self.timer_started = None
        self.timer_duration = 60
        self.full_index = None
        self.awaiting_result = False
        self.timer_buffs = ("none", "none")
        self.images = {}
        self.fonts = {}
        self.startup_error = None
        directory = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AutoEldenRing"
        self.session = directory / "profiles-v3.json"
        self.profiles = None
        if state is None and persist:
            try:
                if self.session.exists():
                    self.profiles = Profiles.load(self.session, self.db)
                    state = self.profiles.active["state"]
                elif (directory / "session-v2.json").exists():
                    state = load_project(directory / "session-v2.json", self.db)
            except (OSError, ValueError) as exc:
                self.startup_error = str(exc)
        self.planner = Planner(self.db, state)
        self.profiles = self.profiles or Profiles(self.db, self.data)
        self.music = Music()
        load_reading_font()
        self.translator = Translator(self.data["language"])
        self.style_spec, palette = appearance(self.data)
        self.bg, self.paper, self.soft, self.ink, self.muted, self.accent = palette
        self.font_family = "OpenDyslexic" if self.data["dyslexic"] else self.style_spec["font"]
        self.geometry("1280x860")
        self.minsize(1080, 730)
        self.title(f"Auto Elden Ring · {__version__}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.iconbitmap(str(resource_path("assets/app.ico")))
        except tk.TclError:
            pass
        self.build_shell()
        if persist:
            self.show_profile_picker(startup=True)
            self.profile_picker.present()
            self.state("zoomed")
        self.after_idle(self.blend_titlebar)
        if persist:
            self.after(150, lambda: self.rescan_game(startup=True))

    @property
    def data(self):
        return self.planner.state

    def t(self, key, **values):
        return self.translator.t(key, **values)

    def label(self, parent, text, size=14, muted=False, **kwargs):
        label = ctk.CTkLabel(
            parent,
            text=text,
            text_color=self.muted if muted else self.ink,
            font=self.font(size),
            **kwargs,
        )
        label._reading_size = size
        label._text_role = "muted" if muted else "ink"
        return label

    def font(self, size=14, bold=False):
        actual = size + 2 if self.data["dyslexic"] else size
        key = (self.font_family, actual, bold)
        if key not in self.fonts:
            self.fonts[key] = ctk.CTkFont(
                family=self.font_family, size=actual, weight="bold" if bold else "normal"
            )
        return self.fonts[key]

    def control_font_changes(self, widget):
        """Return only a changed font while preserving the original point size."""
        try:
            font = widget.cget("font")
            size = getattr(widget, "_reading_size", None)
            if size is None:
                size = font.cget("size") - (2 if font.cget("family") == "OpenDyslexic" else 0)
                widget._reading_size = size
            desired = self.font(size, font.cget("weight") == "bold")
            return {"font": desired} if font is not desired else {}
        except ValueError, AttributeError, tk.TclError:
            return {}

    def refresh_page_fonts(self, page):
        """Apply deferred font metrics when a retained calculator becomes active."""
        record = self.views[page]
        signature = (self.font_family, self.data["dyslexic"])
        if record.get("font_signature") == signature:
            return

        def visit(widget):
            changes = self.control_font_changes(widget)
            if changes:
                widget.configure(**changes)
            for child in widget.winfo_children():
                visit(child)

        visit(record["frame"])
        record["font_signature"] = signature

    def button(self, parent, key, command, secondary=False, **kwargs):
        widget = ctk.CTkButton(
            parent,
            text=self.t(key),
            command=lambda: self.action(command),
            height=38,
            corner_radius=self.style_spec["button_radius"],
            font=self.font(13),
            fg_color=self.soft if secondary else self.accent,
            hover_color=self.accent,
            text_color=self.ink if secondary else "#FFFFFF",
            **kwargs,
        )
        widget._translation_key = key
        widget._secondary = secondary
        return widget

    def card(self, parent):
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.paper,
            corner_radius=self.style_spec["radius"],
            border_width=(
                2 if self.data["style"] == "xp" else 1 if self.data["style"] == "elden" else 0
            ),
            border_color=self.soft,
        )
        frame._surface_role = "paper"
        return frame

    def action(self, command):
        try:
            return command()
        except (ValueError, KeyError, TypeError, OSError) as exc:
            messagebox.showerror(
                self.t("error"), self.t("invalid") + "\n\n" + str(exc), parent=self
            )

    def autosave(self):
        if self.persist and not self._closing:
            if self.save_job:
                self.after_cancel(self.save_job)
            self.save_job = self.after(400, self.flush_save)

    def flush_save(self):
        self.save_job = None
        if self.persist:
            self.profiles.save(self.session, self.data)

    def build_shell(self):
        self.configure(fg_color=self.bg)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sidebar = ctk.CTkFrame(
            self, width=self.style_spec["sidebar"], fg_color=self.paper, corner_radius=0
        )
        self.sidebar._surface_role = "paper"
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.brand = self.label(self.sidebar, "AUTO\nELDEN RING", 24)
        self.tagline = self.label(
            self.sidebar, self.t("tagline"), muted=True, wraplength=190, justify="left"
        )
        self.profile_button = self.button(
            self.sidebar, "switch_character", self.show_profile_picker, True, width=180
        )
        self.nav = {}
        for key in ("character", "weapons", "stones", "farm", "journal", "settings"):
            self.nav[key] = self.button(
                self.sidebar, key, lambda k=key: self.navigate(k), True, width=180
            )
        self.equipment_button = self.button(
            self.sidebar, "equipment", self.equipment_view, True, width=180
        )
        self.version_label = self.label(
            self.sidebar, f"v{__version__} · {self.t('offline')}", 12, True
        )
        self.rescan_button = self.button(
            self.sidebar, "rescan_game", self.rescan_game, True, width=180
        )
        self.rescan_status = self.label(self.sidebar, "", 11, muted=True, wraplength=180)
        self.host = ctk.CTkFrame(self, fg_color=self.bg, corner_radius=0)
        self.host._surface_role = "bg"
        self.host.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        self.layout_style()
        self.show(self.page)

    def layout_style(self):
        classic = self.data["style"] == "xp" and not self.data["dyslexic"]
        self._layout_signature = classic
        self.sidebar.configure(width=self.style_spec["sidebar"], fg_color=self.paper)
        for widget in self.sidebar.winfo_children():
            widget.pack_forget()
        for row in (0, 1):
            self.grid_rowconfigure(row, weight=0)
        for col in (0, 1):
            self.grid_columnconfigure(col, weight=0)
        if classic:
            self.grid_rowconfigure(1, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.sidebar.grid_configure(row=0, column=0, columnspan=2, sticky="ew")
            self.sidebar.grid_propagate(True)
            self.host.grid_configure(row=1, column=0, columnspan=2, sticky="nsew", padx=18, pady=14)
            self.brand.configure(text="AUTO ELDEN RING", font=self.font(13, True))
            self.brand.pack(side="left", padx=12, pady=14)
            self.profile_button.pack(side="left", padx=4, pady=10)
            for button in self.nav.values():
                button.configure(width=96, height=32)
                button.pack(side="left", padx=3, pady=10)
        else:
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.sidebar.grid_configure(row=0, column=0, columnspan=1, sticky="ns")
            self.sidebar.grid_propagate(False)
            self.host.grid_configure(row=0, column=1, columnspan=1, sticky="nsew", padx=24, pady=20)
            self.brand.configure(text="AUTO\nELDEN RING", font=self.font(24))
            self.brand.pack(anchor="w", padx=24, pady=(26, 8))
            self.tagline.pack(anchor="w", padx=24, pady=(0, 16))
            self.profile_button.configure(
                text=(
                    self.data["character_name"]
                    if self.data["profile_created"]
                    else self.t("switch_character")
                )
            )
            self.profile_button.pack(pady=(0, 12), padx=16)
            for key, button in self.nav.items():
                button.configure(width=180, height=38)
                button.pack(pady=5, padx=20)
            self.version_label.pack(side="bottom", pady=18)
            self.rescan_status.pack(side="bottom", padx=16, pady=6)
            self.rescan_button.pack(side="bottom", padx=16, pady=6)
        if classic:
            self.rescan_button.configure(width=100, height=32)
            self.rescan_button.pack(side="right", padx=8, pady=10)
        else:
            self.rescan_button.configure(width=180, height=38)
        self.equipment_button.configure(width=110 if classic else 180)
        self.equipment_button.pack(side="left" if classic else "top", padx=12, pady=8)
        self.refresh_nav()

    def blend_titlebar(self):
        # Native caption, movement and resize loops are deliberately retained.
        if not self._closing:
            classic = self.data["style"] == "xp" and not self.data["dyslexic"]
            caption_color(
                self, self.accent if classic else self.bg, "#FFFFFF" if classic else self.ink
            )

    def toggle_maximize(self):
        self.state("normal" if self.state() == "zoomed" else "zoomed")

    def show(self, page, refresh=False):
        if self._closing:
            return
        self.page = page
        if page == "farm" and getattr(self, "farm_spot_dirty", False):
            refresh = True
            self.farm_spot_dirty = False
        for record in self.views.values():
            record["frame"].pack_forget()
        if refresh and page in self.views:
            cancel_widget_jobs(self.views[page]["frame"])
            self.views.pop(page)["frame"].destroy()
        if page not in self.views:
            frame = ctk.CTkFrame(self.host, fg_color=self.bg, corner_radius=0)
            frame._surface_role = "bg"
            record = {"frame": frame}
            self.views[page] = record
            title = self.label(frame, self.t(page + "_title"), 28)
            title.pack(anchor="w", pady=(0, 5))
            title._translation_key = page + "_title"
            hint = page + "_hint"
            if hint in self.translator.text:
                label = self.label(frame, self.t(hint), muted=True, wraplength=920, justify="left")
                label._translation_key = hint
                label.pack(anchor="w", pady=(0, 18))
            self.body = ctk.CTkScrollableFrame(
                frame,
                fg_color=self.bg,
                corner_radius=0,
                scrollbar_button_color=self.soft,
                scrollbar_button_hover_color=self.accent,
            )
            self.body.pack(fill="both", expand=True)
            record["body"] = self.body
            getattr(self, "build_" + page)()
        record = self.views[page]
        self.body = record["body"]
        record["frame"].pack(fill="both", expand=True)
        if page in self.wallet_vars:
            self.wallet_var = self.wallet_vars[page]
            self.wallet_var.set(str(self.data["runes"]))
        self.refresh_character()
        self.refresh_weapons()
        self.refresh_farm_results()
        self.refresh_goal_spots()
        if (
            "weapons" in self.views
            and self.data["weapon_mode"] == "catalogue"
            and self.selected_vars
        ):
            self.selected_editor.configure(
                values=[self.translator.weapon(i["name"]) for i in self.data["selected"]]
            )
            self.selected_editor.set(self.translator.weapon(self.selected_vars[0][0]["name"]))
        if (
            "weapons" in self.views
            and self.data["manual"]["input_mode"] == "next"
            and self.data["weapon_mode"] == "manual"
        ):
            self.update_price_prompt()
        self.refresh_nav()
        self.refresh_page_fonts(page)
        self.normalize_surfaces(self.views[page]["frame"])
        if page == "journal":
            self.draw_timeline()
        if page == "farm":
            self.update_timer_display()
        if self.data["style"] == "elden":
            self.body.pack_configure(padx=24, pady=18)
        else:
            self.body.pack_configure(padx=0, pady=0)

    def refresh_nav(self):
        icons = {
            "character": "◇",
            "weapons": "⚔",
            "stones": "◈",
            "farm": "◷",
            "journal": "✦",
            "settings": "⚙",
        }
        for index, (key, button) in enumerate(self.nav.items()):
            color = self.accent
            prefix = icons[key] + "  " if self.data["style"] == "elden" else ""
            button.configure(
                text=prefix + self.t(key),
                fg_color=color if key == self.page else self.soft,
                text_color="#FFFFFF" if key == self.page else self.ink,
            )

    def navigate(self, page):
        if not self.data["profile_created"] or self.profile_selection_pending:
            return self.show_profile_picker(startup=True)
        self.dismiss_menu()
        for panel in tuple(self.popups):
            if isinstance(panel, Panel):
                panel.destroy()
        self.commit_current()
        self.autosave()
        self.show(page)

    def commit_current(self):
        if self.page == "character" and hasattr(self, "stat_vars"):
            for (section, attribute), variable in self.stat_vars.items():
                integer(
                    variable.get(),
                    attribute,
                    CLASS_DATA[self.data["class_name"]]["stats"][attribute],
                    99,
                )
            self.preview_levels()
            self.read_wallet()
        elif self.page == "weapons" and hasattr(self, "manual_vars"):
            self.read_weapons()
        elif self.page == "farm" and hasattr(self, "farm_vars"):
            self.read_farm()

    def entry(self, parent, key, value, row, command=None, width=160):
        label = self.label(parent, self.t(key))
        if key in self.translator.text:
            label._translation_key = key
        label.grid(row=row, column=0, sticky="w", padx=18, pady=9)
        variable = tk.StringVar(value=str(value))
        widget = ctk.CTkEntry(
            parent,
            textvariable=variable,
            width=width,
            height=34,
            font=self.font(),
            fg_color=self.bg,
            text_color=self.ink,
            border_color=self.soft,
            corner_radius=self.style_spec["button_radius"],
        )
        widget.grid(row=row, column=1, sticky="e", padx=18, pady=9)
        widget._reading_size = 14
        if command:
            widget.bind("<FocusOut>", lambda _: self.action(command))
            widget.bind("<Return>", lambda _: self.action(command))
        return variable

    def option(self, parent, key, identifiers, current, command, row):
        label = self.label(parent, self.t(key))
        label._translation_key = key
        label.grid(row=row, column=0, sticky="w", padx=18, pady=9)
        option = NativeOptionMenu(
            parent,
            values=[self.t(k) for k in identifiers],
            font=self.font(13),
            fg_color=self.soft,
            button_color=self.accent,
            text_color=self.ink,
            width=260,
        )
        option._enum_ids = tuple(identifiers)
        option._enum_current = current

        def choose(value):
            ident = next(k for k in option._enum_ids if self.t(k) == value)
            option._enum_current = ident
            if command:
                self.action(lambda: command(ident))

        option.configure(command=choose)
        option.set(self.t(current))
        option.grid(row=row, column=1, sticky="e", padx=18, pady=9)
        return option

    def wallet(self, parent, row=0):
        variable = self.entry(parent, "runes_held", self.data["runes"], row)
        self.wallet_vars[self.page] = variable
        self.wallet_var = variable
        return variable

    def read_wallet(self):
        if self.page in self.wallet_vars:
            self.planner.set_wallet(self.wallet_vars[self.page].get())

    def metrics(self, parent, pairs):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=12)
        row.titles = []
        row.values = []
        for index, (title, value) in enumerate(pairs):
            row.grid_columnconfigure(index, weight=1)
            panel = self.card(row)
            panel.grid(row=0, column=index, sticky="nsew", padx=(0, 10))
            heading = self.label(panel, title, 13, True, wraplength=270)
            heading.pack(anchor="w", padx=20, pady=(18, 5))
            number = self.label(panel, value, 24)
            number.pack(anchor="w", padx=20, pady=(0, 18))
            row.titles.append(heading)
            row.values.append(number)
        return row

    def build_character(self):
        top = self.card(self.body)
        top.pack(fill="x", pady=(0, 12))
        self.class_option = self.option(
            top, "starting_class", tuple(CLASS_DATA), self.data["class_name"], self.set_class, 0
        )
        if self.data["profile_created"]:
            self.class_option.configure(state="disabled")
        self.wallet(top, 1)
        if self.data["save_link"]:
            self.button(top, "refresh_save", self.refresh_import, True).grid(
                row=1, column=2, padx=14
            )
        self.level_label = self.label(top, "", 18)
        self.level_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=18, pady=14)
        self.stats_frame = self.card(self.body)
        self.stats_frame.pack(fill="x")
        self.rebuild_stats_table()
        self.button(self.body, "calculate_levels", self.calculate_character).pack(
            anchor="w", pady=16
        )
        self.character_metrics = self.metrics(self.body, [("", ""), ("", ""), ("", "")])
        self.character_budget = self.label(self.body, "", 16, wraplength=900, justify="left")
        self.character_budget.pack(anchor="w", pady=8)
        self.respec_label = self.label(self.body, "", muted=True, wraplength=900)
        self.respec_label.pack(anchor="w")
        self.character_time = self.goal_farm_summary(self.body, "character")
        self.refresh_character()

    def rebuild_stats_table(self):
        cancel_widget_jobs(self.stats_frame)
        for child in self.stats_frame.winfo_children():
            child.destroy()
        for col, key in enumerate(("attribute", "base", "now", "goal")):
            label = self.label(self.stats_frame, self.t(key), muted=True)
            label._translation_key = key
            label.grid(row=0, column=col, padx=20, pady=16, sticky="w")
        self.stat_vars = {}
        for row, attribute in enumerate(ATTRIBUTES, 1):
            label = self.label(self.stats_frame, self.t(attribute))
            label._translation_key = attribute
            label.grid(row=row, column=0, sticky="w", padx=20, pady=6)
            self.label(
                self.stats_frame,
                str(CLASS_DATA[self.data["class_name"]]["stats"][attribute]),
                muted=True,
            ).grid(row=row, column=1)
            for col, section in ((2, "stats_current"), (3, "stats_target")):
                variable = tk.StringVar(value=self.data[section][attribute])
                self.stat_vars[section, attribute] = variable
                entry = ctk.CTkEntry(
                    self.stats_frame,
                    textvariable=variable,
                    width=100,
                    font=self.font(),
                    border_color=self.soft,
                    fg_color=self.bg,
                    text_color=self.ink,
                    corner_radius=self.style_spec["button_radius"],
                )
                entry.grid(row=row, column=col, padx=20, pady=6)
                variable.trace_add("write", lambda *_: self.preview_levels())

    def refresh_character(self):
        if "character" not in self.views or not hasattr(self, "character_metrics"):
            return
        c = self.planner.character()
        self.level_label.configure(
            text=self.t("level_route", current=c["current"], target=c["target"], count=c["levels"])
        )
        pairs = (
            (self.t("remaining_cost"), c["cost"]),
            (
                self.t("paid_since_class", base=CLASS_DATA[self.data["class_name"]]["level"]),
                c["spent"],
            ),
            (self.t("to_maximum", current=c["current"]), c["maximum_cost"]),
        )
        for index, (title, value) in enumerate(pairs):
            self.character_metrics.titles[index].configure(text=title)
            self.character_metrics.values[index].configure(text=fmt(value))
        self.character_budget.configure(
            text=self.t(
                "budget_route",
                current=c["current"],
                target=c["reachable"],
                count=c["reachable"] - c["current"],
                left=fmt(c["left"]),
            )
        )
        self.respec_label.configure(text=self.t("respec") if c["respec"] else "")
        if hasattr(self, "character_time"):
            self.character_time()

    def preview_levels(self):
        if getattr(self, "_refreshing_scan", False):
            return
        try:
            clone = deepcopy(self.data)
            for (section, attribute), variable in self.stat_vars.items():
                clone[section][attribute] = integer(variable.get())
            p = Planner(self.db, clone)
            c = p.character()
            self.data.update({k: clone[k] for k in ("stats_current", "stats_target")})
            self.level_label.configure(
                text=self.t(
                    "level_route", current=c["current"], target=c["target"], count=c["levels"]
                )
            )
        except ValueError, tk.TclError:
            pass  # An incomplete number during typing is not a modal error.

    def calculate_character(self):
        self.commit_current()
        self.refresh_character()
        self.autosave()

    def set_class(self, name):
        if self.data["profile_created"]:
            return
        previous = CLASS_DATA[self.data["class_name"]]["stats"]
        self.data["class_name"] = name
        for section in ("stats_current", "stats_target"):
            if self.data[section] == previous:
                self.data[section] = deepcopy(CLASS_DATA[name]["stats"])
            else:
                for attribute in ATTRIBUTES:
                    self.data[section][attribute] = max(
                        self.data[section][attribute], CLASS_DATA[name]["stats"][attribute]
                    )
        self.rebuild_stats_table()
        self.refresh_character()
        self.normalize_surfaces()
        self.autosave()

    def build_weapons(self):
        controls = self.card(self.body)
        controls.pack(fill="x", pady=(0, 12))
        self.mode_control = ctk.CTkSegmentedButton(
            controls,
            values=[self.t("manual_mode"), self.t("catalogue_mode")],
            selected_color=self.accent,
            font=self.font(13),
            command=lambda value: self.action(
                lambda: self.switch_mode(
                    "manual" if value == self.t("manual_mode") else "catalogue"
                )
            ),
        )
        self.mode_control.set(
            self.t("manual_mode" if self.data["weapon_mode"] == "manual" else "catalogue_mode")
        )
        self.mode_control.pack(anchor="w", padx=18, pady=14)
        wallet = self.card(self.body)
        wallet.pack(fill="x", pady=(0, 12))
        self.wallet(wallet)
        hint = self.label(
            wallet, self.t("planning_wallet"), muted=True, wraplength=850, justify="left"
        )
        hint._translation_key = "planning_wallet"
        hint.grid(row=1, column=0, columnspan=2, padx=18, pady=(0, 12), sticky="w")
        self.weapon_form = self.card(self.body)
        self.weapon_form.pack(fill="x")
        self.rebuild_weapon_form()
        warning = self.label(
            self.body, self.t("standard_warning"), muted=True, wraplength=920, justify="left"
        )
        warning._translation_key = "standard_warning"
        warning.pack(anchor="w", pady=12)
        actions = ctk.CTkFrame(self.body, fg_color="transparent")
        actions.pack(fill="x", pady=16)
        self.button(actions, "calculate_weapons", self.calculate_weapons).pack(
            side="left", padx=(0, 10)
        )
        self.button(actions, "max_without_dragon", self.max_without_dragon, True).pack(side="left")
        self.weapon_summary()
        self.weapon_time = self.goal_farm_summary(self.body, "weapons")

    def rebuild_weapon_form(self):
        if not hasattr(self, "weapon_form"):
            return
        cancel_widget_jobs(self.weapon_form)
        for child in self.weapon_form.winfo_children():
            child.destroy()
        self.manual_vars = {}
        self.selected_vars = []
        self.mode_control.set(
            self.t("manual_mode" if self.data["weapon_mode"] == "manual" else "catalogue_mode")
        )
        if self.data["weapon_mode"] == "manual":
            m = self.data["manual"]
            self.option(
                self.weapon_form,
                "weapon_type",
                ("normal", "somber"),
                m["kind"],
                self.switch_kind,
                0,
            )
            if m["input_mode"] == "base":
                self.manual_vars["base"] = self.entry(self.weapon_form, "base_price", m["base"], 1)
                self.manual_vars["current"] = self.entry(
                    self.weapon_form, "current_upgrade", m["current"], 2
                )
                self.button(self.weapon_form, "custom_quote", self.toggle_inverse, True).grid(
                    row=1, column=2, padx=12
                )
            else:
                self.manual_vars["current"] = self.entry(
                    self.weapon_form, "current_upgrade", m["current"], 1
                )
                self.price_caption = self.label(self.weapon_form, "")
                self.price_caption.grid(row=2, column=0, padx=18, sticky="w")
                variable = tk.StringVar(value=m["observed"])
                ctk.CTkEntry(
                    self.weapon_form,
                    textvariable=variable,
                    width=160,
                    font=self.font(),
                    fg_color=self.bg,
                    text_color=self.ink,
                    border_color=self.soft,
                    corner_radius=self.style_spec["button_radius"],
                ).grid(row=2, column=1, padx=18, pady=9)
                self.manual_vars["observed"] = variable
                self.manual_vars["current"].trace_add(
                    "write", lambda *_: self.update_price_prompt()
                )
                self.button(self.weapon_form, "base_quote", self.toggle_inverse, True).grid(
                    row=2, column=2, padx=12
                )
                self.update_price_prompt()
            self.manual_vars["target"] = self.entry(
                self.weapon_form, "target_upgrade", m["target"], 3
            )
            self.manual_vars["quantity"] = self.entry(self.weapon_form, "copies", m["quantity"], 4)
        else:
            self.button(self.weapon_form, "choose_weapons", self.catalogue).grid(
                row=0, column=0, padx=18, pady=16, sticky="w"
            )
            self.label(
                self.weapon_form, self.t("selected_count", count=len(self.data["selected"]))
            ).grid(row=0, column=1, padx=18)
            selection = self.data["selected"]
            if selection:
                self.selected_overview = ctk.CTkTextbox(
                    self.weapon_form,
                    height=125,
                    font=self.font(13),
                    fg_color=self.bg,
                    text_color=self.ink,
                )
                self.selected_overview.grid(
                    row=1, column=0, columnspan=3, padx=18, pady=8, sticky="ew"
                )
                names = [self.translator.weapon(i["name"]) for i in selection]
                self.selected_editor = NativeOptionMenu(
                    self.weapon_form,
                    values=names,
                    width=330,
                    font=self.font(13),
                    fg_color=self.soft,
                    button_color=self.accent,
                    text_color=self.ink,
                    command=self.select_weapon_editor,
                )
                self.selected_editor.set(names[0])
                self.selected_editor.grid(
                    row=2, column=0, columnspan=2, padx=18, pady=12, sticky="w"
                )
                variables = {
                    key: self.entry(self.weapon_form, label, selection[0][key], row)
                    for row, (key, label) in enumerate(
                        (
                            ("current", "current_upgrade"),
                            ("target", "target_upgrade"),
                            ("quantity", "copies"),
                        ),
                        3,
                    )
                }
                self.selected_vars = [(selection[0], variables)]
                self.refresh_selected_overview()

    def update_price_prompt(self):
        try:
            current = integer(self.manual_vars["current"].get())
            self.price_caption.configure(
                text=self.t("next_price", current=current, next=current + 1)
            )
        except ValueError:
            pass

    def select_weapon_editor(self, value):
        self.read_weapons()
        item = next(i for i in self.data["selected"] if self.translator.weapon(i["name"]) == value)
        variables = self.selected_vars[0][1]
        for key, var in variables.items():
            var.set(str(item[key]))
        self.selected_vars = [(item, variables)]
        self.refresh_weapons()

    def refresh_selected_overview(self):
        if (
            self.data["weapon_mode"] != "catalogue"
            or not self.data["selected"]
            or not hasattr(self, "selected_overview")
        ):
            return
        text = "\n".join(
            f'{self.translator.weapon(i["name"])}   +{i["current"]} → +{i["target"]}   ×{i["quantity"]}'
            for i in self.data["selected"]
        )
        self.selected_overview.configure(state="normal")
        self.selected_overview.delete("1.0", "end")
        self.selected_overview.insert("1.0", text)
        self.selected_overview.configure(state="disabled")

    def read_weapons(self):
        clone = deepcopy(self.data)
        for key, var in self.manual_vars.items():
            clone["manual"][key] = integer(var.get())
        for old, variables in self.selected_vars:
            item = next(i for i in clone["selected"] if i["name"] == old["name"])
            item.update({key: integer(var.get()) for key, var in variables.items()})
        validate_state(clone, self.db)
        Planner(self.db, clone).weapons()
        self.data.update(clone)
        self.selected_vars = [
            (next(i for i in self.data["selected"] if i["name"] == old["name"]), variables)
            for old, variables in self.selected_vars
        ]
        self.read_wallet()

    def calculate_weapons(self):
        self.read_weapons()
        self.refresh_weapons()
        self.autosave()

    def switch_mode(self, mode):
        self.read_weapons()
        self.data["weapon_mode"] = mode
        self.rebuild_weapon_form()
        self.refresh_weapons()
        self.autosave()

    def switch_kind(self, kind):
        self.read_weapons()
        m = self.data["manual"]
        m.update(kind=kind, current=0, target=24 if kind == "normal" else 10, input_mode="base")
        self.rebuild_weapon_form()
        self.refresh_weapons()
        self.autosave()

    def toggle_inverse(self):
        self.read_weapons()
        m = self.data["manual"]
        weapon = self.planner.manual_weapon()
        if m["input_mode"] == "base":
            if m["current"] >= weapon.maximum:
                raise ValueError(self.t("inverse_error"))
            m["observed"] = weapon.costs[m["current"]]
            m["input_mode"] = "next"
        else:
            m["base"] = weapon.base
            m["input_mode"] = "base"
        self.rebuild_weapon_form()
        self.refresh_weapons()
        self.autosave()

    def max_without_dragon(self):
        self.read_weapons()
        self.planner.without_dragon()
        if self.data["weapon_mode"] == "manual":
            self.manual_vars["target"].set(str(self.data["manual"]["target"]))
        else:
            for item, variables in self.selected_vars:
                variables["target"].set(str(item["target"]))
        self.refresh_weapons()
        self.autosave()

    def weapon_summary(self):
        self.weapon_metrics = self.metrics(self.body, [("", ""), ("", ""), ("", "")])
        self.weapon_deficit = self.label(self.body, "", 18)
        self.weapon_deficit.pack(anchor="w", pady=5)
        self.weapon_recovered = self.label(self.body, "")
        self.weapon_recovered.pack(anchor="w")
        self.weapon_affordable = self.label(
            self.body, "", muted=True, wraplength=920, justify="left"
        )
        self.weapon_affordable.pack(anchor="w", pady=10)
        self.weapon_dragon = self.label(self.body, "", muted=True, wraplength=920, justify="left")
        self.weapon_dragon.pack(anchor="w", pady=8)
        for key, command in (
            ("stone_calculator", self.inventory_popup),
            ("missing_stones", self.missing_popup),
            ("complete_upgrades", self.complete_upgrades),
        ):
            self.button(self.body, key, command, True).pack(anchor="w", pady=8)
        self.refresh_weapons()

    def refresh_weapons(self):
        if "weapons" not in self.views or not hasattr(self, "weapon_metrics"):
            return
        plan = self.planner.weapons()
        for index, (key, value) in enumerate(
            (
                ("forge_cost", plan["forge"]),
                ("stone_cost", plan["stones_cost"]),
                ("total_cost", plan["total"]),
            )
        ):
            self.weapon_metrics.titles[index].configure(text=self.t(key))
            self.weapon_metrics.values[index].configure(text=fmt(value))
        self.weapon_deficit.configure(text=self.t("to_farm") + ": " + fmt(plan["deficit"]))
        recovered = (
            self.data["weapon_mode"] == "manual" and self.data["manual"]["input_mode"] == "next"
        )
        self.weapon_recovered.configure(
            text=(
                self.t("recovered_base", price=fmt(self.planner.manual_weapon().base))
                if recovered
                else ""
            )
        )
        affordable, left = self.planner.affordable_targets()
        route = ", ".join(
            f'{self.t("manual_mode") if self.data["weapon_mode"]=="manual" else self.translator.weapon(i["weapon"].name)}: +{i["current"]} → +{i["target"]}'
            for i in affordable
        )
        self.weapon_affordable.configure(
            text=self.t("affordable_weapon", route=route, left=fmt(left))
        )
        self.weapon_dragon.configure(text=self.t("dragon_notice") if plan["dragon_needed"] else "")
        self.refresh_selected_overview()
        if hasattr(self, "weapon_time"):
            self.weapon_time()

    def popup(self, title, size="960x740"):
        self.dismiss_menu()
        window = Panel(self, title)
        self.popups.add(window)

        def present():
            if window.winfo_exists():
                self.normalize_surfaces(window)
                window.present()

        window.after(0, present)
        return window

    def native_popup(self, title, size="960x740"):
        window = ManagedWindow(self)
        self.popups.add(window)
        window.title(title)
        window.iconbitmap(str(resource_path("assets/app.ico")))
        window.geometry(size)
        window.configure(fg_color=self.bg)
        window.transient(self)
        window.protocol("WM_DELETE_WINDOW", window.destroy)
        window.lift()

        def present():
            self.normalize_surfaces(window)
            classic = self.data["style"] == "xp" and not self.data["dyslexic"]
            caption_color(
                window, self.accent if classic else self.bg, "#FFFFFF" if classic else self.ink
            )

        # Some CTk constructors process idle work before their child scrollbars
        # exist. Present on the next event cycle, after construction is complete.
        window.after(0, present)
        return window

    def catalogue(self):
        if self.page == "weapons":
            self.read_weapons()
        if getattr(self, "gallery_window", None) and self.gallery_window.winfo_exists():
            self.gallery_window.lift()
            return
        window = self.popup(self.t("choose_weapons"), "1100x800")
        self.gallery_window = window
        self.label(window, self.t("catalogue_hint"), muted=True).pack(anchor="w", padx=24, pady=16)
        self.label(window, self.t("ownership_hint"), muted=True, wraplength=1040).pack(
            anchor="w", padx=24, pady=(0, 8)
        )
        query = tk.StringVar()
        self.label(window, self.t("search"), muted=True).pack(anchor="w", padx=24)
        ctk.CTkEntry(window, textvariable=query, width=600, font=self.font()).pack(
            anchor="w", padx=24, pady=8
        )
        gallery = Gallery(window, self)
        self.gallery = gallery
        gallery.pack(fill="both", expand=True, padx=20, pady=14)
        search_job = [None]

        def search(*_):
            if search_job[0]:
                window.after_cancel(search_job[0])
            search_job[0] = window.after(180, lambda: gallery.filter(query.get()))

        query.trace_add("write", search)

        def done():
            window.destroy()
            self.data["weapon_mode"] = "catalogue"
            self.autosave()
            self.rebuild_weapon_form()
            self.refresh_weapons()

        self.button(window, "done", done).pack(pady=(0, 14))
        window.protocol("WM_DELETE_WINDOW", done)

    def build_stones(self):
        self.button(self.body, "stone_calculator", self.inventory_popup).pack(anchor="w", pady=8)
        self.button(self.body, "missing_stones", self.missing_popup, True).pack(anchor="w", pady=8)
        self.price_labels = {}
        prices = self.card(self.body)
        prices.pack(fill="x", pady=12)
        for row, key in enumerate(k for k in STONE_PRICES if not k.endswith("dragon")):
            self.label(prices, self.translator.stone(key)).grid(
                row=row, column=0, sticky="w", padx=20, pady=7
            )
            value = self.label(prices, fmt(self.data["prices"].get(key, STONE_PRICES[key])), 16)
            value.grid(row=row, column=1, padx=30)
            self.price_labels[key] = value
            value.bind(
                "<Double-Button-1>", lambda _, k=key: self.action(lambda: self.edit_price(k))
            )
        for key in ("normal:dragon", "somber:dragon"):
            self.label(
                self.body,
                self.translator.stone(key)
                + "   ·   "
                + self.t("unit_price")
                + ": ?   ·   "
                + self.t("required")
                + ": ?   ·   "
                + self.t("owned")
                + ": ?",
                muted=True,
                wraplength=950,
            ).pack(anchor="w", pady=10)
        self.button(self.body, "restore_prices", self.restore_prices, True).pack(
            anchor="w", pady=14
        )
        self.normalize_surfaces()

    def restore_prices(self):
        self.data["prices"] = {}
        self.autosave()
        for key, label in self.price_labels.items():
            label.configure(text=fmt(STONE_PRICES[key]))
        self.refresh_weapons()

    def edit_price(self, key):
        if not messagebox.askyesno(self.t("unit_price"), self.t("confirm_price"), parent=self):
            return
        window = self.popup(self.t("unit_price"), "650x270")
        form = self.card(window)
        form.pack(fill="x", padx=20, pady=20)
        variable = self.entry(
            form, self.translator.stone(key), self.data["prices"].get(key, STONE_PRICES[key]), 0
        )

        def apply():
            self.data["prices"][key] = integer(variable.get())
            self.autosave()
            self.price_labels[key].configure(text=fmt(self.data["prices"][key]))
            self.refresh_weapons()
            window.destroy()

        self.button(window, "done", apply).pack(pady=12)
        window.price_var = variable
        window.apply_price = apply
        return window

    def inventory_popup(self):
        if self.page == "weapons":
            self.read_weapons()
        window = self.popup(self.t("stone_calculator"), "760x760")
        self.label(window, self.t("stock_hint"), muted=True, wraplength=700, justify="left").pack(
            padx=20, pady=16
        )
        scroll = ctk.CTkScrollableFrame(window, fg_color=self.bg)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        variables = {
            key: self.entry(scroll, self.translator.stone(key), self.data["stock"].get(key, 0), row)
            for row, key in enumerate(self.data["stock"])
        }

        def none():
            for var in variables.values():
                var.set("0")

        def apply():
            self.data["stock"] = {key: integer(var.get()) for key, var in variables.items()}
            self.data["purchased"] = {}
            self.autosave()
            window.destroy()
            self.refresh_weapons()
            self.missing_popup()

        actions = ctk.CTkFrame(window, fg_color="transparent")
        actions.pack(pady=15)
        self.button(actions, "no_stones", none, True).pack(side="left", padx=6)
        self.button(actions, "apply_stock", apply).pack(side="left", padx=6)
        window.stock_vars = variables
        window.apply_stock = apply

    def missing_popup(self):
        if self.page == "weapons":
            self.read_weapons()
        window = self.popup(self.t("missing_stones"), "850x650")
        self.label(
            window, self.t("planning_wallet"), muted=True, wraplength=780, justify="left"
        ).pack(padx=20, pady=16)

        def acknowledge_all():
            self.acknowledge_all_stones()
            for row in window.purchase_rows.values():
                row["update"]()

        self.button(window, "all_stones", acknowledge_all, True).pack(pady=6)
        scroll = ctk.CTkScrollableFrame(window, fg_color=self.bg)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        rows = [r for r in self.planner.weapons()["stones"] if not r["key"].endswith("dragon")]
        window.purchase_rows = {}
        for row in rows:
            key = row["key"]
            panel = self.card(scroll)
            panel.pack(fill="x", pady=5)
            label = self.label(panel, "")
            label.pack(side="left", padx=14, pady=14)

            def update(k=key, p=panel, l=label):
                current = next(r for r in self.planner.weapons()["stones"] if r["key"] == k)
                complete = current["missing"] == 0
                bought = self.data["purchased"].get(k, 0)
                p.configure(border_width=2 if complete else 0, border_color="#438B64")
                l.configure(
                    text=("✓  " if complete else "")
                    + self.translator.stone(k)
                    + f'   ×{current["missing"]}   ·   {fmt(current["cost"])}'
                    + ("   " + self.t("purchased_quantity", quantity=bought) if bought else "")
                )
                window.purchase_rows[k]["button"].configure(
                    state="disabled" if complete else "normal",
                    text="✓" if complete else self.t("bought"),
                    fg_color="#438B64" if complete else self.accent,
                )

            def buy(k=key, refresh=update):
                self.planner.purchase(k)
                refresh()
                self.refresh_weapons()
                self.autosave()

            button = self.button(panel, "bought", buy)
            button.pack(side="right", padx=14)
            window.purchase_rows[key] = {
                "panel": panel,
                "label": label,
                "button": button,
                "buy": buy,
                "update": update,
            }
            update()
        if not rows:
            self.label(scroll, self.t("ready")).pack(pady=20)

    def complete_upgrades(self):
        self.read_weapons()
        if messagebox.askyesno(
            self.t("complete_upgrades"), self.t("confirm_upgrade_record"), parent=self
        ):
            completed = (
                deepcopy(self.data["selected"]) if self.data["weapon_mode"] == "catalogue" else []
            )
            before = deepcopy(self.data)
            self.planner.complete_upgrades()
            for item in completed:
                owned = self.data["inventory_weapons"]
                remaining = item["quantity"]
                for record in owned:
                    if record["name"] == item["name"] and record["current"] == item["current"]:
                        count = min(remaining, record["quantity"])
                        record["quantity"] -= count
                        remaining -= count
                owned[:] = [i for i in owned if i["quantity"] > 0]
                existing = next(
                    (
                        i
                        for i in owned
                        if i["name"] == item["name"] and i["current"] == item["target"]
                    ),
                    None,
                )
                if existing:
                    existing["quantity"] += item["quantity"]
                else:
                    owned.append(
                        {
                            "name": item["name"],
                            "current": item["target"],
                            "quantity": item["quantity"],
                        }
                    )
            if self.data["profile_created"]:
                from .history import differences

                point = self.profiles.checkpoint(self.data, "upgrade_event")
                next(p for p in self.profiles.active["checkpoints"] if p["id"] == point["id"])[
                    "changes"
                ] = differences(before, self.data)
            for window in tuple(self.popups):
                if hasattr(window, "purchase_rows") or hasattr(window, "stock_vars"):
                    window.destroy()
            self.wallet_vars["weapons"].set("0")
            self.rebuild_weapon_form()
            self.refresh_weapons()
            self.autosave()

    def build_farm(self):
        timer = self.card(self.body)
        timer.pack(fill="x", pady=(0, 12))
        self.timer_label = self.label(timer, "01:00", 40)
        self.timer_label.pack(pady=18)
        buttons = ctk.CTkFrame(timer, fg_color="transparent")
        buttons.pack(pady=(0, 18))
        self.start_test_button = self.button(buttons, "start_minute", self.start_timer)
        self.start_test_button.pack(side="left", padx=5)
        for key, command in (
            ("stop", self.stop_timer),
            ("reset", self.reset_timer),
            ("full_test", self.start_full_test),
        ):
            self.button(buttons, key, command, True).pack(side="left", padx=5)
        self.test_label = self.label(timer, "", muted=True)
        self.test_label.pack(pady=(0, 12))
        form = self.card(self.body)
        form.pack(fill="x")
        self.wallet(form)
        f = self.data["farm"]
        spots = ctk.CTkFrame(self.body, fg_color="transparent")
        spots.pack(fill="x", pady=12)
        self.spot_option = NativeOptionMenu(
            spots,
            values=[self.t("new_measurement")] + [s["name"] for s in self.data["farm_spots"]],
            command=lambda name: self.action(lambda: self.select_farm_spot(name)),
            fg_color=self.soft,
            button_color=self.accent,
            text_color=self.ink,
            font=self.font(),
        )
        self.spot_option.pack(side="left", padx=6)
        self.button(spots, "save_spot", self.save_farm_spot, True).pack(side="left", padx=6)
        self.farm_vars = {}
        for row, (field, key) in enumerate(
            (("runes", "measured_runes"), ("seconds", "duration"), ("efficiency", "efficiency")), 1
        ):
            self.farm_vars[field] = self.entry(form, key, f[field], row)
        self.option(
            form,
            "talisman",
            tuple(TALISMANS),
            f["talisman"],
            lambda v: self.set_farm_option("talisman", v),
            4,
        )
        self.option(
            form,
            "consumable",
            tuple(CONSUMABLES),
            f["consumable"],
            lambda v: self.set_farm_option("consumable", v),
            5,
        )
        self.option(
            form,
            "goal",
            tuple("goal_" + g for g in ("combined", "character", "weapons", "maximum", "free")),
            "goal_" + f["goal"],
            lambda v: self.set_farm_option("goal", v.removeprefix("goal_")),
            6,
        )
        self.free_goal_frame = ctk.CTkFrame(form, fg_color="transparent")
        self.free_goal_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
        self.farm_vars["free_goal"] = self.entry(
            self.free_goal_frame, "free_goal", f["free_goal"], 0
        )
        if f["goal"] != "free":
            self.free_goal_frame.grid_remove()
        self.maximum_goal_frame = ctk.CTkFrame(form, fg_color="transparent")
        self.maximum_goal_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
        self.farm_vars["maximum_current"] = self.entry(
            self.maximum_goal_frame, "farm_current_level", self.planner.maximum_farm_level(), 0
        )
        if f["goal"] != "maximum":
            self.maximum_goal_frame.grid_remove()
        self.farm_vars["notes"] = self.entry(form, "notes", f["notes"], 8, width=400)
        actions = ctk.CTkFrame(self.body, fg_color="transparent")
        actions.pack(fill="x", pady=16)
        self.button(actions, "estimate", self.calculate_farm).pack(side="left", padx=(0, 10))
        self.button(actions, "record_result", self.record_result, True).pack(side="left")
        self.sample_label = self.label(self.body, "", muted=True)
        self.sample_label.pack(anchor="w")
        self.farm_metrics = self.metrics(self.body, [("", "—")] * 3)
        self.invested_metrics = self.metrics(self.body, [("", "—")] * 2)
        self.invested_metrics.pack_forget()
        self.rate_labels = {}
        for key in (
            "without_buffs",
            "with_scarab",
            "with_foot",
            "with_both",
            "optimized",
            "remaining_plan",
        ):
            label = self.label(self.body, "", 16)
            label.pack(anchor="w", pady=5)
            self.rate_labels[key] = label
        self.farm_dragon = self.label(self.body, "", muted=True, wraplength=900)
        self.farm_dragon.pack(anchor="w")
        note = self.label(
            self.body, self.t("projection_note"), muted=True, wraplength=920, justify="left"
        )
        note._translation_key = "projection_note"
        note.pack(anchor="w", pady=12)
        self.refresh_farm_results()
        self.update_timer_display()

    def set_farm_option(self, field, value):
        self.read_farm()
        self.data["farm"][field] = value
        if field in ("talisman", "consumable"):
            self.data["farm"]["use_samples"] = False
        if field == "goal":
            if value == "free":
                self.free_goal_frame.grid()
            else:
                self.free_goal_frame.grid_remove()
            if value == "maximum":
                if self.data["farm"].get("maximum_current") is None:
                    self.farm_vars["maximum_current"].set(str(self.planner.character()["current"]))
                self.maximum_goal_frame.grid()
            else:
                self.maximum_goal_frame.grid_remove()
        self.refresh_farm_results()
        self.autosave()

    def refresh_farm_results(self):
        if "farm" not in self.views or not hasattr(self, "farm_metrics"):
            return
        f = self.data["farm"]
        maximum_goal = f["goal"] == "maximum"
        # Remove the duplicate maximum-duration card rather than leaving a blank.
        if maximum_goal:
            self.farm_metrics.values[2].master.grid_remove()
            self.farm_metrics.grid_columnconfigure(2, weight=0)
            self.invested_metrics.pack(fill="x", pady=12, after=self.farm_metrics)
        else:
            self.farm_metrics.values[2].master.grid()
            self.farm_metrics.grid_columnconfigure(2, weight=1)
            self.invested_metrics.pack_forget()
        invested = (
            self.planner.db.level_cost(
                CLASS_DATA[self.data["class_name"]]["level"], self.planner.maximum_farm_level()
            )
            if maximum_goal
            else 0
        )
        self.invested_metrics.titles[0].configure(text=self.t("invested_runes"))
        self.invested_metrics.titles[1].configure(text=self.t("invested_farm_time"))
        self.invested_metrics.values[0].configure(text=fmt(invested))
        self.invested_metrics.values[1].configure(text="—")
        self.sample_label.configure(
            text=(
                self.t(
                    "sample_summary",
                    count=len(f["samples"]),
                    seconds=sum(s["seconds"] for s in f["samples"]),
                )
                if f["samples"] and f["use_samples"]
                else ""
            )
        )
        titles = (
            self.t("rate"),
            self.t("time_needed"),
            self.t("to_maximum", current=self.planner.character()["current"]),
        )
        values = ("—", "—", "—")
        if self.planner.farm_rates()["measured"] > 0:
            p = self.planner.farm_projection()
            values = (
                fmt(p["measured"]),
                self.translator.duration(p["time"]),
                self.translator.duration(p["maximum_time"]),
            )
            self.invested_metrics.values[1].configure(
                text=self.translator.duration(p["invested_time"])
            )
            for key, field in (
                ("without_buffs", "baseline"),
                ("with_scarab", "gold_scarab"),
                ("with_foot", "gold_foot"),
                ("with_both", "scarab_foot"),
                ("optimized", "optimized"),
            ):
                self.rate_labels[key].configure(text=self.t(key) + ": " + fmt(p[field]))
            self.rate_labels["remaining_plan"].configure(
                text=self.t("remaining_plan", runes=fmt(p["remaining"]))
            )
            self.farm_dragon.configure(text=self.t("dragon_notice") if p["incomplete"] else "")
        else:
            for label in self.rate_labels.values():
                label.configure(text="")
            self.farm_dragon.configure(text="")
        for label, text in zip(self.farm_metrics.titles, titles):
            label.configure(text=text)
        for label, text in zip(self.farm_metrics.values, values):
            label.configure(text=text)

    def read_farm(self):
        clone = deepcopy(self.data)
        for field, var in self.farm_vars.items():
            if field == "maximum_current" and clone["farm"]["goal"] != "maximum":
                continue
            clone["farm"][field] = var.get() if field == "notes" else integer(var.get())
        validate_state(clone, self.db)
        if any(clone["farm"][k] != self.data["farm"][k] for k in ("runes", "seconds")):
            clone["farm"]["use_samples"] = False
        # Preserve the dictionary reference used by option callbacks.
        self.data["farm"].update(clone["farm"])
        self.read_wallet()

    def calculate_farm(self):
        self.read_farm()
        self.planner.farm_projection()
        self.refresh_farm_results()
        self.autosave()

    def reset_timer(self):
        self.stop_timer()
        self.full_index = None
        self.awaiting_result = False
        self.timer_duration = 60
        self.data["farm"]["seconds"] = 60
        if self.page == "farm":
            self.farm_vars["seconds"].set("60")
            self.update_timer_display()

    def start_full_test(self):
        self.reset_timer()
        self.data["farm"]["samples"] = []
        self.data["farm"]["use_samples"] = False
        self.full_index = 0
        self.start_timer()

    def start_timer(self):
        if self.deadline is not None:
            return
        if self.awaiting_result:
            raise ValueError(self.t("record_result"))
        if self.page == "farm":
            self.read_farm()
        self.timer_duration = (60, 60, 180)[self.full_index] if self.full_index is not None else 60
        self.data["farm"]["seconds"] = self.timer_duration
        self.timer_buffs = (self.data["farm"]["talisman"], self.data["farm"]["consumable"])
        self.timer_started = time.monotonic()
        self.deadline = self.timer_started + self.timer_duration
        self.tick_timer()

    def stop_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        if self.deadline is not None:
            elapsed = max(1, math.ceil(time.monotonic() - self.timer_started))
            self.data["farm"]["seconds"] = min(elapsed, self.timer_duration)
            if self.page == "farm":
                self.farm_vars["seconds"].set(str(self.data["farm"]["seconds"]))
            self.deadline = None
            self.full_index = None
            self.awaiting_result = True
        self.update_timer_display()

    def tick_timer(self):
        if self.deadline is None:
            return
        if time.monotonic() >= self.deadline:
            self.deadline = None
            self.timer_job = None
            self.awaiting_result = True
            self.data["farm"]["seconds"] = self.timer_duration
            if self.page == "farm":
                self.farm_vars["seconds"].set(str(self.timer_duration))
            self.bell()
        else:
            self.timer_job = self.after(100, self.tick_timer)
        self.update_timer_display()

    def update_timer_display(self):
        if self.page != "farm" or not hasattr(self, "timer_label"):
            return
        remaining = (
            max(0, math.ceil(self.deadline - time.monotonic()))
            if self.deadline
            else (0 if self.awaiting_result else self.timer_duration)
        )
        self.timer_label.configure(text=f"{remaining//60:02d}:{remaining%60:02d}")
        self.start_test_button.configure(
            text=self.t("next_test" if self.full_index is not None else "start_minute")
        )
        if self.full_index is not None:
            self.test_label.configure(
                text=self.t(
                    "test_step", index=self.full_index + 1, seconds=(60, 60, 180)[self.full_index]
                )
            )
        elif self.awaiting_result:
            self.test_label.configure(text=self.t("test_finished"))
        else:
            self.test_label.configure(text="")

    def record_result(self):
        self.read_farm()
        f = self.data["farm"]
        if self.full_index is not None and not self.awaiting_result:
            raise ValueError(self.t("test_finished"))
        seconds = self.timer_duration if self.full_index is not None else f["seconds"]
        buffs = self.timer_buffs if self.awaiting_result else (f["talisman"], f["consumable"])
        self.planner.add_sample(f["runes"], seconds, *buffs, notes=f["notes"])
        self.awaiting_result = False
        if self.full_index is not None:
            self.full_index += 1
            if self.full_index == 3:
                self.full_index = None
                self.timer_duration = 60
                messagebox.showinfo(self.t("full_test"), self.t("full_finished"), parent=self)
            else:
                self.timer_duration = (60, 60, 180)[self.full_index]
        self.autosave()
        self.refresh_farm_results()
        self.update_timer_display()

    def build_settings(self):
        form = self.card(self.body)
        form.pack(fill="x")
        self.style_option = self.option(
            form,
            "style",
            tuple("style_" + k for k in STYLES),
            "style_" + self.data["style"],
            self.set_visual_style,
            0,
        )
        self.theme_option = self.option(
            form,
            "color_palette",
            STYLES[self.data["style"]]["themes"],
            self.data["theme"],
            self.set_palette,
            1,
        )
        label = self.label(form, self.t("language"))
        label._translation_key = "language"
        label.grid(row=2, column=0, padx=18, pady=18, sticky="w")
        self.language_var = tk.StringVar(value=LANGUAGE_NAMES[self.data["language"]])
        self.language_option = NativeOptionMenu(
            form,
            variable=self.language_var,
            values=list(LANGUAGE_NAMES.values()),
            width=260,
            font=self.font(13),
            fg_color=self.soft,
            button_color=self.accent,
            text_color=self.ink,
            command=lambda v: self.set_language(
                next(k for k, name in LANGUAGE_NAMES.items() if name == v)
            ),
        )
        self.language_option.grid(row=2, column=1, padx=18, pady=18)
        self.dyslexic_var = tk.BooleanVar(value=self.data["dyslexic"])
        self.reading_check = ctk.CTkCheckBox(
            form,
            text=self.t("dyslexic"),
            variable=self.dyslexic_var,
            font=self.font(14),
            command=self.set_reading_mode,
            fg_color=self.accent,
            text_color=self.ink,
        )
        self.reading_check._translation_key = "dyslexic"
        self.reading_check.grid(row=3, column=0, columnspan=2, padx=18, pady=14, sticky="w")
        reading = self.label(
            form, self.t("reading_hint"), muted=True, wraplength=830, justify="left"
        )
        reading._translation_key = "reading_hint"
        reading.grid(row=4, column=0, columnspan=2, padx=18, pady=(0, 16), sticky="w")
        self.style_description = self.label(
            self.body,
            self.t("style_hint_" + self.data["style"]),
            muted=True,
            wraplength=880,
            justify="left",
        )
        self.style_description.pack(anchor="w", pady=16)
        audio = self.card(self.body)
        audio.pack(fill="x", pady=12)
        self.music_label = self.label(
            audio, self.data["music_file"] or self.t("no_music"), wraplength=820
        )
        self.music_label.pack(anchor="w", padx=18, pady=16)
        actions = ctk.CTkFrame(audio, fg_color="transparent")
        actions.pack(anchor="w", padx=18, pady=(0, 16))
        for key, command in (
            ("choose_music", self.choose_music),
            ("play_music", lambda: self.music.play(self.data["music_file"])),
            ("pause_music", self.music.pause),
        ):
            self.button(actions, key, command, True).pack(side="left", padx=4)
        label = self.label(audio, self.t("music_hint"), muted=True, wraplength=830, justify="left")
        label._translation_key = "music_hint"
        label.pack(anchor="w", padx=18, pady=(0, 16))
        self.button(self.body, "small_mode", self.compact_mode, True).pack(anchor="w", pady=8)
        self.button(self.body, "import_save", self.import_dialog, True).pack(anchor="w", pady=8)
        for key in ("autosave_note", "scan_hint"):
            label = self.label(self.body, self.t(key), muted=True, wraplength=900, justify="left")
            label._translation_key = key
            label.pack(anchor="w", pady=16)
        if self.startup_error:
            self.label(self.body, self.startup_error, muted=True, wraplength=900).pack(anchor="w")

    def choose_music(self):
        path = filedialog.askopenfilename(
            parent=self, filetypes=[("MP3 / WAV / FLAC / OGG", "*.mp3 *.wav *.flac *.ogg")]
        )
        if path:
            self.music.close()
            self.data["music_file"] = path
            self.music_label.configure(text=path)
            self.autosave()

    def set_visual_style(self, value):
        style = value.removeprefix("style_")
        self.data["style"] = style
        if self.data["theme"] not in STYLES[style]["themes"]:
            self.data["theme"] = STYLES[style]["themes"][0]
        self.apply_appearance()

    def set_palette(self, value):
        self.data["theme"] = value
        self.apply_appearance()

    def set_language(self, value):
        self.data["language"] = value
        self.apply_appearance()

    def set_reading_mode(self):
        self.data["dyslexic"] = self.dyslexic_var.get()
        self.apply_appearance()

    def update_controls_appearance(self):
        old = (self.bg, self.paper, self.soft, self.ink, self.muted, self.accent)
        previous = self.translator
        language_changed = previous.language != self.data["language"]
        if language_changed:
            self.translator = Translator(self.data["language"])
        reverse = (
            {value: key for key, value in previous.text.items() if "{" not in value}
            if language_changed
            else {}
        )
        self.style_spec, palette = appearance(self.data)
        self.bg, self.paper, self.soft, self.ink, self.muted, self.accent = palette
        self.font_family = "OpenDyslexic" if self.data["dyslexic"] else self.style_spec["font"]
        mapping = dict(zip(old, palette))
        self.configure(fg_color=self.bg)
        if self.sidebar.cget("width") != self.style_spec["sidebar"]:
            self.sidebar.configure(width=self.style_spec["sidebar"])

        inactive_frames = {
            record["frame"] for key, record in self.views.items() if key != self.page
        }

        def visit(widget, index=0, update_fonts=True):
            update_fonts = update_fonts and widget not in inactive_frames
            if not isinstance(widget, (ctk.CTkBaseClass, ctk.CTkScrollableFrame)):
                try:
                    color = widget.cget("background")
                    if color in mapping:
                        widget.configure(background=mapping[color])
                except tk.TclError, TypeError, ValueError:
                    pass
            if isinstance(widget, (ctk.CTkBaseClass, ctk.CTkScrollableFrame)):
                # CTk redraws on configure: collect changed properties and paint
                # each retained control once instead of once per color/font.
                pending = {}
                for prop in (
                    "fg_color",
                    "bg_color",
                    "text_color",
                    "border_color",
                    "button_color",
                    "button_hover_color",
                    "hover_color",
                    "selected_color",
                    "unselected_color",
                    "scrollbar_button_color",
                ):
                    try:
                        current = widget.cget(prop)
                        if (
                            isinstance(current, str)
                            and current in mapping
                            and current != mapping[current]
                        ):
                            pending[prop] = mapping[current]
                    except ValueError, AttributeError:
                        pass
                try:
                    current = widget.cget("text")
                    key = getattr(widget, "_translation_key", None) or reverse.get(current)
                    if key and current != self.t(key):
                        pending["text"] = self.t(key)
                except ValueError, AttributeError:
                    pass
                if update_fonts:
                    pending.update(self.control_font_changes(widget))
                try:
                    radius = (
                        self.style_spec["radius"]
                        if isinstance(widget, ctk.CTkFrame)
                        else self.style_spec["button_radius"]
                    )
                    if (
                        widget not in (self.sidebar, self.host)
                        and widget.cget("corner_radius") != radius
                    ):
                        pending["corner_radius"] = radius
                except ValueError, AttributeError:
                    pass
                if isinstance(widget, ctk.CTkLabel) and getattr(widget, "_text_role", None):
                    color = self.muted if widget._text_role == "muted" else self.ink
                    if widget.cget("text_color") != color:
                        pending["text_color"] = color
                if hasattr(widget, "_enum_ids"):
                    values = [self.t(k) for k in widget._enum_ids]
                    if widget.cget("values") != values:
                        pending["values"] = values
                    value = self.t(widget._enum_current)
                    if widget.get() != value:
                        widget.set(value)
                if pending:
                    widget.configure(**pending)
                if isinstance(widget, ctk.CTkScrollableFrame):
                    widget._scrollbar.configure(
                        fg_color=self.bg,
                        bg_color=self.bg,
                        button_color=self.soft,
                        button_hover_color=self.accent,
                    )
            for i, child in enumerate(widget.winfo_children()):
                visit(child, index + i + 1, update_fonts)

        for child in self.winfo_children():
            visit(child)
        if self.page in self.views:
            self.views[self.page]["font_signature"] = (self.font_family, self.data["dyslexic"])
        if "settings" in self.views:
            ids = STYLES[self.data["style"]]["themes"]
            self.theme_option._enum_ids = ids
            self.theme_option._enum_current = self.data["theme"]
            self.theme_option.configure(values=[self.t(k) for k in ids])
            self.theme_option.set(self.t(self.data["theme"]))
            self.style_option._enum_current = "style_" + self.data["style"]
            self.style_option.set(self.t(self.style_option._enum_current))
            self.language_var.set(LANGUAGE_NAMES[self.data["language"]])
            self.style_description.configure(text=self.t("style_hint_" + self.data["style"]))
            self.dyslexic_var.set(self.data["dyslexic"])
        classic = self.data["style"] == "xp" and not self.data["dyslexic"]
        if getattr(self, "_layout_signature", None) != classic:
            self.layout_style()
        else:
            self.refresh_nav()
        self.refresh_character()
        self.refresh_weapons()
        self.refresh_farm_results()
        if getattr(self, "gallery_window", None) and self.gallery_window.winfo_exists():
            self.gallery.reflow()
        if (
            "weapons" in self.views
            and self.data["weapon_mode"] == "catalogue"
            and self.selected_vars
        ):
            self.selected_editor.configure(
                values=[self.translator.weapon(i["name"]) for i in self.data["selected"]]
            )
            self.selected_editor.set(self.translator.weapon(self.selected_vars[0][0]["name"]))
        if (
            "weapons" in self.views
            and self.data["weapon_mode"] == "manual"
            and self.data["manual"]["input_mode"] == "next"
        ):
            self.update_price_prompt()
        if hasattr(self, "scan_message_key"):
            key, values = self.scan_message_key
            self.scan_status(key, **values)
        self.blend_titlebar()
        self.autosave()

    def apply_settings(self):
        self.apply_appearance()

    def save(self):
        path = filedialog.asksaveasfilename(
            parent=self, defaultextension=".json", filetypes=[("Auto Elden Ring project", "*.json")]
        )
        if path:
            save_project(path, self.data, self.db)

    def load(self):
        path = filedialog.askopenfilename(
            parent=self, filetypes=[("Auto Elden Ring project", "*.json")]
        )
        if not path:
            return
        state = load_project(path, self.db)
        window = self.popup(self.t("open_project"), "650x370")
        self.label(window, self.t("resume_hint"), wraplength=600, justify="left").pack(
            padx=24, pady=20
        )
        keep = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(window, text=self.t("keep_stats"), variable=keep, font=self.font()).pack(
            anchor="w", padx=24, pady=12
        )
        form = self.card(window)
        form.pack(fill="x", padx=24)
        wallet = self.entry(form, "runes_held", state["runes"], 0)

        def resume():
            state["runes"] = integer(wallet.get())
            state["wallet_baseline"] = state["runes"]
            self.commit_current()
            self.profiles.sync(self.data)
            if (state["character_name"], state["journey_name"]) != (
                self.data["character_name"],
                self.data["journey_name"],
            ):
                self.profiles.create(
                    state["character_name"], state["journey_name"], state["class_name"], state
                )
            self.profiles.sync(state)
            window.destroy()
            self.page = "weapons" if keep.get() else "character"
            self.activate_profile(state)
            self.inventory_popup()

        self.button(window, "done", resume).pack(pady=18)

    def reset_session(self):
        if messagebox.askyesno(self.t("reset_session"), self.t("confirm_reset"), parent=self):
            self.reset_timer()
            fresh = default_state()
            for key in (
                "language",
                "style",
                "theme",
                "dyslexic",
                "character_name",
                "journey_name",
                "music_file",
            ):
                fresh[key] = self.data[key]
            self.planner = Planner(self.db, fresh)
            self.replace_views()
            self.profiles.sync(self.data)
            self.autosave()

    def close(self):
        if self._closing:
            return
        try:
            self.commit_current()
        except ValueError, KeyError, tk.TclError:
            pass  # Preserve the last valid state when an entry is incomplete.
        self._closing = True
        try:
            self.flush_save()
        except OSError as exc:
            self.startup_error = str(exc)
        self.destroy()

    def destroy(self):
        self._closing = True
        if hasattr(self, "reader_pool"):
            self.reader_pool.shutdown(wait=False, cancel_futures=True)
        try:
            self.music.close()
        except ValueError, AttributeError:
            pass
        for window in tuple(getattr(self, "popups", ())):
            if window.winfo_exists():
                window.destroy()
        try:
            for job in self.tk.splitlist(self.tk.call("after", "info")):
                self.tk.call("after", "cancel", job)
        except tk.TclError:
            pass
        super().destroy()

    def report_callback_exception(self, exc, value, trace):
        self.callback_errors.append(str(value))
        if not self._closing:
            super().report_callback_exception(exc, value, trace)

    def checkpoint_detail(self, point):
        return self.checkpoint_cards(point)

    def new_profile(self):
        return self.profile_form(True)

    def rename_profile(self):
        return self.profile_form(False)

    def switch_profile(self, ident):
        if ident == self.profiles.data["active"]:
            return
        self.commit_current()
        self.profiles.sync(self.data)
        self.activate_profile(self.profiles.select(ident))

    def activate_profile(self, state):
        with presentation_transaction(self):
            self.profile_selection_pending = False
            self.timeline_offset = 0
            self.reset_timer()
            self.music.close()
            for window in tuple(self.popups):
                window.destroy()
            self.planner = Planner(self.db, state)
            if getattr(self, "profile_sidebar_hidden", False):
                self.profile_sidebar_hidden = False
                self.layout_style()
            self.replace_views()
            self.autosave()

    def replace_views(self):
        for record in self.views.values():
            cancel_widget_jobs(record["frame"])
            record["frame"].destroy()
        self.views.clear()
        self.wallet_vars.clear()
        self.show(self.page)
        self.apply_appearance()


def run():
    App().mainloop()
