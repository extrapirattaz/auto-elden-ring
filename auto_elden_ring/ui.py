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
from PIL import Image
from classes_data import CLASS_DATA, ATTRIBUTES
from . import __version__
from .core import Database, STONE_PRICES, integer, resource_path
from .planner import Planner, default_state, validate_state, TALISMANS, CONSUMABLES
from .i18n import Translator, LANGUAGE_NAMES
from .storage import save_project, load_project

PALETTES = {
    "calm": ("#F2F3EF", "#FFFFFF", "#E7EBE3", "#263A32", "#68756D", "#526E5D"),
    "elden": ("#161B19", "#202824", "#303C33", "#EEE9D8", "#A7B1A4", "#A18B55"),
    "slate": ("#171D29", "#222B3B", "#344158", "#EDF1F8", "#A5B1C6", "#536F9C"),
}


def fmt(value):
    return f"{value:,.0f}".replace(",", " ")


class App(ctk.CTk):
    def __init__(self, db=None, persist=True, state=None):
        super().__init__()
        self.db = db or Database()
        self.persist = persist
        self.session = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "AutoEldenRing" / "session-v2.json"
        self.startup_error = None
        if state is None and persist and self.session.exists():
            try:
                state = load_project(self.session, self.db)
            except (OSError, ValueError) as exc:
                self.startup_error = str(exc)
        self.planner = Planner(self.db, state)
        self.page = "character"
        self.deadline = self.timer_job = self.timer_started = None
        self.timer_duration = 60
        self.full_index = None
        self.awaiting_result = False
        self.timer_buffs = ("none", "none")
        self.images = {}
        self.geometry("1280x860")
        self.minsize(1080, 730)
        self.title(f"Auto Elden Ring · {__version__}")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Map>",self.on_map,add="+")
        try:
            self.iconbitmap(str(resource_path("assets/app.ico")))
        except tk.TclError:
            pass
        self.build_shell()

    @property
    def data(self):
        return self.planner.state

    def t(self, key, **values):
        return self.translator.t(key, **values)

    def label(self, parent, text, size=14, muted=False, **kwargs):
        return ctk.CTkLabel(parent, text=text, text_color=self.muted if muted else self.ink,
                            font=ctk.CTkFont(family="Segoe UI", size=size), **kwargs)

    def button(self, parent, key, command, secondary=False, **kwargs):
        return ctk.CTkButton(parent, text=self.t(key), command=lambda: self.action(command),
                            height=38, corner_radius=9, fg_color=self.soft if secondary else self.accent,
                            hover_color=self.accent, text_color=self.ink if secondary else "#FFFFFF", **kwargs)

    def card(self, parent):
        return ctk.CTkFrame(parent, fg_color=self.paper, corner_radius=14)

    def action(self, command):
        try:
            return command()
        except (ValueError, KeyError, TypeError, OSError) as exc:
            messagebox.showerror(self.t("error"), self.t("invalid") + "\n\n" + str(exc), parent=self)

    def autosave(self):
        if self.persist:
            save_project(self.session, self.data, self.db)

    def build_shell(self):
        if getattr(self,"titlebar_job",None):
            self.after_cancel(self.titlebar_job)
        for child in self.winfo_children():
            child.destroy()
        self.translator = Translator(self.data["language"])
        self.bg, self.paper, self.soft, self.ink, self.muted, self.accent = PALETTES[self.data["theme"]]
        ctk.set_appearance_mode("light" if self.data["theme"] == "calm" else "dark")
        self.configure(fg_color=self.bg)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.chrome=None
        sidebar = ctk.CTkFrame(self, width=220, fg_color=self.paper, corner_radius=0)
        self.sidebar=sidebar
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        self.label(sidebar, "AUTO\nELDEN RING", 24, justify="left").pack(anchor="w", padx=24, pady=(30, 8))
        self.label(sidebar, self.t("tagline"), muted=True, wraplength=180, justify="left").pack(padx=24, anchor="w", pady=(0, 30))
        self.nav={}
        for key in ("character", "weapons", "stones", "farm", "settings"):
            self.nav[key]=self.button(sidebar, key, lambda k=key: self.navigate(k), secondary=key != self.page, width=180)
            self.nav[key].pack(pady=5, padx=20)
        self.label(sidebar, f"v{__version__} · OFFLINE", 12, muted=True).pack(side="bottom", pady=24)
        self.host = ctk.CTkFrame(self, fg_color=self.bg, corner_radius=0)
        self.host.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        self.show(self.page)
        self.titlebar_job=self.after(100, self.blend_titlebar)

    def blend_titlebar(self):
        if os.name != "nt":
            return
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            def color(hex_value):
                r, g, b = bytes.fromhex(hex_value[1:])
                return ctypes.c_int(r | (g << 8) | (b << 16))
            for attribute, value in ((35, self.bg), (36, self.ink), (34, self.bg)):
                packed = color(value)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(packed), 4)
            self.integrated_titlebar(hwnd)
        except (OSError, AttributeError):
            pass

    def on_map(self,event):
        if event.widget==self and hasattr(self,"bg"):
            self.after(100,self.blend_titlebar)

    def integrated_titlebar(self,hwnd):
        """Keep native resizing/taskbar behavior while replacing the caption."""
        user32=ctypes.windll.user32
        user32.GetWindowLongW.argtypes=[ctypes.c_void_p,ctypes.c_int]
        user32.SetWindowLongW.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_long]
        user32.SetWindowPos.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_uint]
        style=user32.GetWindowLongW(hwnd,-16)
        user32.SetWindowLongW(hwnd,-16,style & ~0x00C00000)
        user32.SetWindowPos(hwnd,None,0,0,0,0,0x37)
        if self.chrome is not None:
            return
        self.chrome=ctk.CTkFrame(self,fg_color=self.bg,corner_radius=0,height=32)
        self.chrome.grid(row=0,column=0,columnspan=2,sticky="ew")
        self.chrome.grid_propagate(False)
        self.sidebar.grid_configure(row=1)
        self.host.grid_configure(row=1)
        self.grid_rowconfigure(0,weight=0)
        self.grid_rowconfigure(1,weight=1)
        title=self.label(self.chrome,f"Auto Elden Ring · {__version__}",12,True)
        title.pack(side="left",padx=20)
        for widget in (self.chrome,title):
            widget.bind("<Button-1>",self.begin_drag)
            widget.bind("<B1-Motion>",self.drag_window)
            widget.bind("<Double-Button-1>",lambda _:self.toggle_maximize())
        for symbol,command in (("×",self.close),("□",self.toggle_maximize),("−",self.iconify)):
            ctk.CTkButton(self.chrome,text=symbol,width=44,height=26,corner_radius=7,
                          fg_color=self.bg,hover_color=self.soft,text_color=self.ink,
                          command=command).pack(side="right",padx=3,pady=3)

    def begin_drag(self,event):
        self.drag_origin=(event.x_root,event.y_root,self.winfo_x(),self.winfo_y())

    def drag_window(self,event):
        if self.state()=="zoomed":
            self.state("normal")
            self.begin_drag(event)
        x,y,left,top=self.drag_origin
        self.geometry(f"+{left+event.x_root-x}+{top+event.y_root-y}")

    def toggle_maximize(self):
        self.state("normal" if self.state()=="zoomed" else "zoomed")

    def show(self, page):
        self.page = page
        for key,button in self.nav.items():
            button.configure(fg_color=self.accent if key==page else self.soft,text_color="#FFFFFF" if key==page else self.ink)
        for child in self.host.winfo_children():
            child.destroy()
        self.label(self.host, self.t(page + "_title"), 28).pack(anchor="w", pady=(0, 5))
        hint = page + "_hint"
        if hint in self.translator.text:
            self.label(self.host, self.t(hint), muted=True, wraplength=920, justify="left").pack(anchor="w", pady=(0, 18))
        self.body = ctk.CTkScrollableFrame(self.host, fg_color=self.bg, corner_radius=0,
                     scrollbar_button_color=self.soft, scrollbar_button_hover_color=self.accent)
        self.body.pack(fill="both", expand=True)
        getattr(self, "build_" + page)()

    def navigate(self,page):
        if self.page=="character":
            self.calculate_character()
        elif self.page=="weapons":
            self.read_weapons()
        elif self.page=="farm":
            self.read_farm()
        self.autosave()
        self.show(page)

    def entry(self, parent, key, value, row, command=None, width=160):
        self.label(parent, self.t(key)).grid(row=row, column=0, sticky="w", padx=18, pady=9)
        variable = tk.StringVar(value=str(value))
        widget = ctk.CTkEntry(parent, textvariable=variable, width=width, height=34,
                              fg_color=self.bg, text_color=self.ink, border_color=self.soft, corner_radius=8)
        widget.grid(row=row, column=1, sticky="e", padx=18, pady=9)
        if command:
            widget.bind("<FocusOut>", lambda _: self.action(command))
            widget.bind("<Return>", lambda _: self.action(command))
        return variable

    def option(self, parent, key, identifiers, current, command, row):
        self.label(parent, self.t(key)).grid(row=row, column=0, sticky="w", padx=18, pady=9)
        labels = {self.t(k): k for k in identifiers}
        option = ctk.CTkOptionMenu(parent, values=list(labels), command=lambda v: self.action(lambda: command(labels[v])),
                                  fg_color=self.soft, button_color=self.accent, text_color=self.ink, width=240)
        option.set(self.t(current))
        option.grid(row=row, column=1, sticky="e", padx=18, pady=9)
        return option

    def wallet(self, parent, row=0):
        variable = self.entry(parent, "runes_held", self.data["runes"], row)
        def apply():
            self.planner.set_wallet(variable.get())
            self.autosave()
            self.show(self.page)
        # Read the wallet together with the page's other fields when calculating.
        self.wallet_var = variable
        return apply

    def read_wallet(self):
        if hasattr(self, "wallet_var") and self.page != "settings":
            self.planner.set_wallet(self.wallet_var.get())

    def metrics(self, parent, pairs):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=12)
        for index, (title, value) in enumerate(pairs):
            row.grid_columnconfigure(index, weight=1)
            panel = self.card(row)
            panel.grid(row=0, column=index, sticky="nsew", padx=(0, 10))
            self.label(panel, title, 13, muted=True, wraplength=270).pack(anchor="w", padx=20, pady=(18, 5))
            self.label(panel, value, 24).pack(anchor="w", padx=20, pady=(0, 18))
        return row

    def build_character(self):
        top = self.card(self.body)
        top.pack(fill="x", pady=(0, 12))
        self.option(top, "starting_class", tuple(CLASS_DATA), self.data["class_name"], self.set_class, 0)
        self.wallet(top, 1)
        c = self.planner.character()
        self.level_label = self.label(top, self.t("level_route", current=c["current"], target=c["target"], count=c["levels"]), 18)
        self.level_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=18, pady=14)
        stats = self.card(self.body)
        stats.pack(fill="x")
        for col, key in enumerate(("attribute", "base", "now", "goal")):
            self.label(stats, self.t(key), muted=True).grid(row=0, column=col, padx=20, pady=16, sticky="w")
        self.stat_vars = {}
        for row, attribute in enumerate(ATTRIBUTES, 1):
            self.label(stats, self.t(attribute)).grid(row=row, column=0, sticky="w", padx=20, pady=6)
            self.label(stats, str(CLASS_DATA[self.data["class_name"]]["stats"][attribute]), muted=True).grid(row=row, column=1)
            for col, section in ((2, "stats_current"), (3, "stats_target")):
                variable = tk.StringVar(value=self.data[section][attribute])
                self.stat_vars[section, attribute] = variable
                field = ctk.CTkEntry(stats, textvariable=variable, width=100, border_color=self.soft,
                                     fg_color=self.bg, text_color=self.ink)
                field.grid(row=row, column=col, padx=20, pady=6)
                variable.trace_add("write", lambda *_: self.preview_levels())
        self.button(self.body, "calculate_levels", self.calculate_character).pack(anchor="w", pady=16)
        self.metrics(self.body, [(self.t("remaining_cost"), fmt(c["cost"])),
                     (self.t("paid_since_class", base=CLASS_DATA[self.data["class_name"]]["level"]), fmt(c["spent"])),
                     (self.t("to_maximum", current=c["current"]), fmt(c["maximum_cost"]))])
        self.label(self.body, self.t("budget_route", current=c["current"], target=c["reachable"],
                   count=c["reachable"]-c["current"], left=fmt(c["left"])), 16, wraplength=900).pack(anchor="w", pady=8)
        if c["respec"]:
            self.label(self.body, self.t("respec"), muted=True, wraplength=900).pack(anchor="w")

    def preview_levels(self):
        try:
            clone = deepcopy(self.data)
            for (section, attribute), variable in self.stat_vars.items():
                clone[section][attribute] = integer(variable.get())
            p = Planner(self.db, clone)
            c = p.character()
            self.data.update({k:clone[k] for k in ("stats_current", "stats_target")})
            self.level_label.configure(text=self.t("level_route", current=c["current"], target=c["target"], count=c["levels"]))
        except (ValueError, tk.TclError):
            pass  # An incomplete number during typing is not a modal error.

    def calculate_character(self):
        for (section, attribute), variable in self.stat_vars.items():
            integer(variable.get(), attribute, CLASS_DATA[self.data["class_name"]]["stats"][attribute], 99)
        self.preview_levels()
        self.read_wallet()
        self.autosave()
        self.show("character")

    def set_class(self, name):
        previous_base=CLASS_DATA[self.data["class_name"]]["stats"]
        self.data["class_name"] = name
        for section in ("stats_current", "stats_target"):
            if self.data[section]==previous_base:
                self.data[section]=deepcopy(CLASS_DATA[name]["stats"])
            else:
                for a in ATTRIBUTES:
                    self.data[section][a] = max(self.data[section][a], CLASS_DATA[name]["stats"][a])
        self.autosave()
        self.show("character")

    def build_weapons(self):
        controls = self.card(self.body)
        controls.pack(fill="x", pady=(0, 12))
        modes = {self.t("manual_mode"):"manual", self.t("catalogue_mode"):"catalogue"}
        segmented = ctk.CTkSegmentedButton(controls, values=list(modes), selected_color=self.accent,
                         command=lambda v:self.action(lambda:self.switch_mode(modes[v])))
        segmented.set(next(k for k,v in modes.items() if v == self.data["weapon_mode"]))
        segmented.pack(anchor="w", padx=18, pady=16)
        form = self.card(self.body)
        form.pack(fill="x")
        self.wallet(form)
        self.manual_vars = {}
        self.selected_vars = []
        if self.data["weapon_mode"] == "manual":
            m = self.data["manual"]
            self.option(form, "weapon_type", ("normal", "somber"), m["kind"], self.switch_kind, 1)
            price_key = "base_price" if m["input_mode"] == "base" else "next_price"
            self.label(form, self.t(price_key, current=m["current"], next=m["current"]+1)).grid(row=2,column=0,padx=18,sticky="w")
            price = tk.StringVar(value=m["base"] if m["input_mode"]=="base" else m["observed"])
            ctk.CTkEntry(form,textvariable=price,width=160,fg_color=self.bg,text_color=self.ink,border_color=self.soft).grid(row=2,column=1,padx=18,pady=9)
            self.manual_vars["base" if m["input_mode"]=="base" else "observed"] = price
            self.button(form,"use_next" if m["input_mode"]=="base" else "use_base",self.toggle_inverse,True).grid(row=2,column=2,padx=10)
            for row, (field,key) in enumerate((("current","current_upgrade"),("target","target_upgrade"),("quantity","copies")),3):
                self.manual_vars[field] = self.entry(form,key,m[field],row)
            self.label(self.body,self.t("standard_warning"),muted=True,wraplength=920,justify="left").pack(anchor="w",pady=12)
        else:
            self.button(form,"choose_weapons",self.catalogue).grid(row=1,column=0,padx=18,pady=14,sticky="w")
            self.label(form,self.t("selected_count",count=len(self.data["selected"]))).grid(row=1,column=1,padx=18)
            for item in self.data["selected"]:
                row = self.card(self.body)
                row.pack(fill="x",pady=5)
                self.label(row,self.translator.weapon(item["name"]),16,wraplength=350).grid(row=0,column=0,padx=16,pady=12,sticky="w")
                variables = {}
                for col,(field,key) in enumerate((("current","current_upgrade"),("target","target_upgrade"),("quantity","copies")),1):
                    box = ctk.CTkFrame(row,fg_color="transparent")
                    box.grid(row=0,column=col,padx=12,pady=10)
                    self.label(box,self.t(key),12,True).pack()
                    variables[field] = tk.StringVar(value=item[field])
                    ctk.CTkEntry(box,textvariable=variables[field],width=75,fg_color=self.bg,text_color=self.ink,border_color=self.soft).pack(pady=4)
                self.selected_vars.append((item,variables))
        actions = ctk.CTkFrame(self.body,fg_color="transparent")
        actions.pack(fill="x",pady=16)
        self.button(actions,"calculate_weapons",self.calculate_weapons).pack(side="left",padx=(0,10))
        self.button(actions,"max_without_dragon",self.max_without_dragon,True).pack(side="left")
        self.weapon_summary()

    def read_weapons(self):
        clone = deepcopy(self.data)
        for key,var in self.manual_vars.items():
            clone["manual"][key] = integer(var.get())
        for old, variables in self.selected_vars:
            item = next(i for i in clone["selected"] if i["name"] == old["name"])
            item.update({key:integer(var.get()) for key,var in variables.items()})
        validate_state(clone,self.db)
        Planner(self.db,clone).weapons()
        self.data.update(clone)
        self.read_wallet()

    def calculate_weapons(self):
        self.read_weapons()
        self.autosave()
        self.show("weapons")

    def switch_mode(self, mode):
        self.read_weapons()
        self.data["weapon_mode"] = mode
        self.autosave()
        self.show("weapons")

    def switch_kind(self, kind):
        m = self.data["manual"]
        m.update(kind=kind,current=0,target=24 if kind=="normal" else 10,input_mode="base")
        self.autosave()
        self.show("weapons")

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
        self.autosave()
        self.show("weapons")

    def max_without_dragon(self):
        self.read_weapons()
        self.planner.without_dragon()
        self.autosave()
        self.show("weapons")

    def weapon_summary(self):
        plan = self.planner.weapons()
        self.metrics(self.body,[(self.t("forge_cost"),fmt(plan["forge"])),(self.t("stone_cost"),fmt(plan["stones_cost"])),(self.t("total_cost"),fmt(plan["total"]))])
        self.label(self.body,self.t("to_farm")+": "+fmt(plan["deficit"]),18).pack(anchor="w",pady=5)
        if self.data["weapon_mode"]=="manual" and self.data["manual"]["input_mode"]=="next":
            self.label(self.body,self.t("recovered_base",price=fmt(self.planner.manual_weapon().base))).pack(anchor="w")
        affordable,left = self.planner.affordable_targets()
        route = ", ".join(f'{self.t("manual_mode") if self.data["weapon_mode"]=="manual" else self.translator.weapon(i["weapon"].name)}: +{i["current"]} → +{i["target"]}' for i in affordable)
        self.label(self.body,self.t("affordable_weapon",route=route,left=fmt(left)),muted=True,wraplength=920,justify="left").pack(anchor="w",pady=10)
        if plan["dragon_needed"]:
            self.label(self.body,self.t("dragon_notice"),muted=True,wraplength=920,justify="left").pack(anchor="w",pady=8)
        self.button(self.body,"stone_calculator",self.inventory_popup,True).pack(anchor="w",pady=8)
        self.button(self.body,"missing_stones",self.missing_popup,True).pack(anchor="w",pady=8)
        self.button(self.body,"complete_upgrades",self.complete_upgrades,True).pack(anchor="w",pady=8)
        self.label(self.body,self.t("tracked_gain",runes=fmt(self.planner.tracked_gain())),muted=True).pack(anchor="w",pady=8)

    def popup(self,title,size="960x740"):
        window = ctk.CTkToplevel(self)
        window.title(title)
        window.geometry(size)
        window.configure(fg_color=self.bg)
        window.transient(self)
        window.after(100,window.lift)
        return window

    def catalogue(self):
        if self.page=="weapons":
            self.read_weapons()
        window = self.popup(self.t("choose_weapons"),"1100x800")
        self.label(window,self.t("catalogue_hint"),muted=True).pack(anchor="w",padx=24,pady=16)
        self.label(window,self.t("search"),muted=True).pack(anchor="w",padx=24,pady=(0,5))
        query = tk.StringVar()
        ctk.CTkEntry(window,textvariable=query,placeholder_text=self.t("search"),width=600).pack(padx=24,anchor="w")
        scroll = ctk.CTkScrollableFrame(window,fg_color=self.bg,scrollbar_button_color=self.soft)
        scroll.pack(fill="both",expand=True,padx=18,pady=18)
        tasks = []
        job = [None]
        def cancel_gallery(event):
            if event.widget==window and job[0]:
                try:
                    window.after_cancel(job[0])
                except tk.TclError:
                    pass
        window.bind("<Destroy>",cancel_gallery,add="+")
        def fill():
            if not window.winfo_exists():
                return
            for _ in range(min(16,len(tasks))):
                group,name,index = tasks.pop(0)
                weapon = self.db.weapons[name]
                selected = any(i["name"]==name for i in self.data["selected"])
                tile = ctk.CTkFrame(group,fg_color=self.soft if selected else self.paper,
                                   width=185,height=200,corner_radius=12,border_width=2 if selected else 0,border_color=self.accent)
                tile.grid(row=index//5,column=index%5,padx=6,pady=6,sticky="nsew")
                tile.weapon_name=name
                tile.grid_propagate(False)
                self.label(tile,self.t("dlc")+": "+self.t("yes" if weapon.dlc else "no")+f"   +{weapon.maximum}",11,True).pack(pady=(10,0))
                raw = self.db.raw["weapons_by_category"][weapon.category][name] if hasattr(self.db,"raw") else self.db.data["weapons_by_category"][weapon.category][name]
                path = resource_path(f'assets/catalogue/{raw["id"]}.png')
                if path.exists():
                    if name not in self.images:
                        with Image.open(path) as source:
                            self.images[name] = ctk.CTkImage(source.copy(),size=(105,105))
                    picture = self.label(tile,"")
                    picture.configure(image=self.images[name])
                    picture.pack()
                self.label(tile,self.translator.weapon(name),13,wraplength=170).pack(padx=6,pady=4)
                self.label(tile,self.t(weapon.kind),11,True).pack()
                def toggle(_=None,n=name,panel=tile):
                    self.planner.toggle_weapon(n)
                    on = any(i["name"]==n for i in self.data["selected"])
                    panel.configure(fg_color=self.soft if on else self.paper,border_width=2 if on else 0)
                    self.autosave()
                tile.bind("<Button-1>",toggle)
                for child in tile.winfo_children():
                    child.bind("<Button-1>",toggle)
            if tasks:
                job[0] = window.after(10,fill)
        def render(*_):
            if job[0]:
                window.after_cancel(job[0])
            tasks.clear()
            for child in scroll.winfo_children():
                child.destroy()
            term = query.get().casefold()
            categories = {}
            for name,w in self.db.weapons.items():
                if term in name.casefold() or term in self.translator.weapon(name).casefold():
                    categories.setdefault(w.category,[]).append(name)
            for category,names in categories.items():
                self.label(scroll,self.t(category),22).pack(anchor="w",pady=(20,10))
                group = ctk.CTkFrame(scroll,fg_color="transparent")
                group.pack(fill="x")
                for col in range(5):
                    group.grid_columnconfigure(col,weight=1)
                tasks.extend((group,n,index) for index,n in enumerate(names))
            fill()
        query.trace_add("write",render)
        def done():
            if job[0]:
                window.after_cancel(job[0])
            window.destroy()
            self.data["weapon_mode"]="catalogue"
            self.autosave()
            self.show("weapons")
        self.button(window,"done",done).pack(pady=(0,16))
        window.protocol("WM_DELETE_WINDOW",done)
        render()

    def build_stones(self):
        self.button(self.body,"stone_calculator",self.inventory_popup).pack(anchor="w",pady=8)
        self.button(self.body,"missing_stones",self.missing_popup,True).pack(anchor="w",pady=8)
        prices = self.card(self.body)
        prices.pack(fill="x",pady=12)
        for row,key in enumerate(k for k in STONE_PRICES if not k.endswith("dragon")):
            self.label(prices,self.translator.stone(key)).grid(row=row,column=0,sticky="w",padx=20,pady=7)
            value = self.label(prices,fmt(self.data["prices"].get(key,STONE_PRICES[key])),16)
            value.grid(row=row,column=1,padx=30)
            value.bind("<Double-Button-1>",lambda _,k=key:self.action(lambda:self.edit_price(k)))
        for key in ("normal:dragon","somber:dragon"):
            self.label(self.body,self.translator.stone(key)+"   ·   "+self.t("unit_price")+": ?   ·   "+self.t("required")+": ?   ·   "+self.t("owned")+": ?",muted=True,wraplength=950).pack(anchor="w",pady=10)
        self.button(self.body,"restore_prices",self.restore_prices,True).pack(anchor="w",pady=14)

    def restore_prices(self):
        self.data["prices"]={}
        self.autosave()
        self.show("stones")

    def edit_price(self,key):
        if not messagebox.askyesno(self.t("unit_price"),self.t("confirm_price"),parent=self):
            return
        dialog = ctk.CTkInputDialog(text=self.translator.stone(key),title=self.t("unit_price"))
        value = dialog.get_input()
        if value is not None:
            self.data["prices"][key]=integer(value)
            self.autosave()
            self.show("stones")

    def inventory_popup(self):
        if self.page=="weapons":
            self.read_weapons()
        window = self.popup(self.t("stone_calculator"),"760x760")
        self.label(window,self.t("stock_hint"),muted=True,wraplength=700,justify="left").pack(padx=20,pady=16)
        scroll = ctk.CTkScrollableFrame(window,fg_color=self.bg)
        scroll.pack(fill="both",expand=True,padx=20,pady=10)
        variables = {key:self.entry(scroll,self.translator.stone(key),self.data["stock"].get(key,0),row)
                     for row,key in enumerate(self.data["stock"])}
        def none():
            for var in variables.values():
                var.set("0")
        def apply():
            stock = {key:integer(var.get()) for key,var in variables.items()}
            self.data["stock"]=stock
            self.autosave()
            window.destroy()
            self.show(self.page)
            self.missing_popup()
        actions = ctk.CTkFrame(window,fg_color="transparent")
        actions.pack(pady=15)
        self.button(actions,"no_stones",none,True).pack(side="left",padx=6)
        self.button(actions,"apply_stock",apply).pack(side="left",padx=6)

    def missing_popup(self):
        if self.page=="weapons":
            self.read_weapons()
        window = self.popup(self.t("missing_stones"),"850x650")
        scroll = ctk.CTkScrollableFrame(window,fg_color=self.bg)
        scroll.pack(fill="both",expand=True,padx=20,pady=20)
        def render():
            for child in scroll.winfo_children():
                child.destroy()
            self.label(scroll,self.t("runes_held")+": "+fmt(self.data["runes"]),20).pack(anchor="w",pady=10)
            rows = [r for r in self.planner.weapons()["stones"] if r["missing"] and not r["key"].endswith("dragon")]
            if not rows:
                self.label(scroll,self.t("ready")).pack(pady=20)
            for row in rows:
                panel=self.card(scroll)
                panel.pack(fill="x",pady=5)
                self.label(panel,f'{self.translator.stone(row["key"])}   ×{row["missing"]}   ·   {fmt(row["cost"])}').pack(side="left",padx=14,pady=14)
                def buy(r=row):
                    if messagebox.askyesno(self.t("bought"),self.t("confirm_purchase",quantity=r["missing"],cost=fmt(r["cost"])),parent=window):
                        self.planner.purchase(r["key"])
                        self.autosave()
                        render()
                        self.show(self.page)
                self.button(panel,"bought",buy).pack(side="right",padx=14)
        render()

    def complete_upgrades(self):
        self.read_weapons()
        if not messagebox.askyesno(self.t("complete_upgrades"),self.t("confirm_upgrade"),parent=self):
            return
        dragon = False
        if self.planner.weapons()["dragon_needed"]:
            dragon = messagebox.askyesno(self.t("normal_dragon"),self.t("confirm_dragon"),parent=self)
            if not dragon:
                return
        self.planner.complete_upgrades(dragon)
        self.autosave()
        self.show("weapons")

    def build_farm(self):
        timer = self.card(self.body)
        timer.pack(fill="x",pady=(0,12))
        self.timer_label=self.label(timer,"01:00",40)
        self.timer_label.pack(pady=18)
        buttons=ctk.CTkFrame(timer,fg_color="transparent")
        buttons.pack(pady=(0,18))
        for key,command in (("next_test" if self.full_index is not None else "start_minute",self.start_timer),("stop",self.stop_timer),("reset",self.reset_timer),("full_test",self.start_full_test)):
            self.button(buttons,key,command,secondary=key!="start_minute").pack(side="left",padx=5)
        self.test_label=self.label(timer,"",muted=True)
        self.test_label.pack(pady=(0,12))
        form=self.card(self.body)
        form.pack(fill="x")
        self.wallet(form)
        f=self.data["farm"]
        self.farm_vars={}
        for row,(field,key) in enumerate((("runes","measured_runes"),("seconds","duration"),("efficiency","efficiency")),1):
            self.farm_vars[field]=self.entry(form,key,f[field],row)
        def set_buff(field,value):
            self.read_farm()
            f[field]=value
            f["use_samples"]=False
            self.autosave()
            self.show("farm")
        self.option(form,"talisman",tuple(TALISMANS),f["talisman"],lambda v:set_buff("talisman",v),4)
        self.option(form,"consumable",tuple(CONSUMABLES),f["consumable"],lambda v:set_buff("consumable",v),5)
        goals=("combined","character","weapons","maximum","free")
        identifiers=tuple("goal_"+g for g in goals)
        def set_goal(value):
            self.read_farm()
            f["goal"]=value.removeprefix("goal_")
            self.autosave()
            self.show("farm")
        self.option(form,"goal",identifiers,"goal_"+f["goal"],set_goal,6)
        if f["goal"]=="free":
            self.farm_vars["free_goal"]=self.entry(form,"free_goal",f["free_goal"],7)
        self.farm_vars["notes"]=self.entry(form,"notes",f["notes"],8,width=400)
        actions=ctk.CTkFrame(self.body,fg_color="transparent")
        actions.pack(fill="x",pady=16)
        self.button(actions,"estimate",self.calculate_farm).pack(side="left",padx=(0,10))
        self.button(actions,"record_result",self.record_result,True).pack(side="left")
        if f["samples"] and f["use_samples"]:
            self.label(self.body,self.t("sample_summary",count=len(f["samples"]),seconds=sum(s["seconds"] for s in f["samples"])),muted=True).pack(anchor="w")
        if self.planner.farm_rates()["measured"]>0:
            p=self.planner.farm_projection()
            self.metrics(self.body,[(self.t("rate"),fmt(p["measured"])),(self.t("time_needed"),self.translator.duration(p["time"])),
                                  (self.t("to_maximum",current=self.planner.character()["current"]),self.translator.duration(p["maximum_time"]))])
            for key,field in (("without_buffs","baseline"),("with_scarab","gold_scarab"),("with_foot","gold_foot"),("with_both","scarab_foot"),("optimized","optimized")):
                self.label(self.body,self.t(key)+": "+fmt(p[field]),16).pack(anchor="w",pady=5)
            self.label(self.body,self.t("remaining_plan",runes=fmt(p["remaining"])),18).pack(anchor="w",pady=12)
            if p["incomplete"]:
                self.label(self.body,self.t("dragon_notice"),muted=True,wraplength=900).pack(anchor="w")
        self.label(self.body,self.t("projection_note"),muted=True,wraplength=920,justify="left").pack(anchor="w",pady=12)
        self.update_timer_display()

    def read_farm(self):
        clone=deepcopy(self.data)
        for field,var in self.farm_vars.items():
            clone["farm"][field]=var.get() if field=="notes" else integer(var.get())
        validate_state(clone,self.db)
        if any(clone["farm"][k]!=self.data["farm"][k] for k in ("runes","seconds")):
            clone["farm"]["use_samples"]=False
        # Preserve the dictionary reference used by option callbacks.
        self.data["farm"].update(clone["farm"])
        self.read_wallet()

    def calculate_farm(self):
        self.read_farm()
        self.planner.farm_projection()
        self.autosave()
        self.show("farm")

    def reset_timer(self):
        self.stop_timer()
        self.full_index=None
        self.awaiting_result=False
        self.timer_duration=60
        self.data["farm"]["seconds"]=60
        if self.page=="farm":
            self.farm_vars["seconds"].set("60")
            self.update_timer_display()

    def start_full_test(self):
        self.reset_timer()
        self.data["farm"]["samples"]=[]
        self.data["farm"]["use_samples"]=False
        self.full_index=0
        self.start_timer()

    def start_timer(self):
        if self.deadline is not None:
            return
        if self.awaiting_result:
            raise ValueError(self.t("record_result"))
        if self.page=="farm":
            self.read_farm()
        self.timer_duration=(60,60,180)[self.full_index] if self.full_index is not None else 60
        self.data["farm"]["seconds"]=self.timer_duration
        self.timer_buffs=(self.data["farm"]["talisman"],self.data["farm"]["consumable"])
        self.timer_started=time.monotonic()
        self.deadline=self.timer_started+self.timer_duration
        self.tick_timer()

    def stop_timer(self):
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job=None
        if self.deadline is not None:
            elapsed=max(1,math.ceil(time.monotonic()-self.timer_started))
            self.data["farm"]["seconds"]=min(elapsed,self.timer_duration)
            if self.page=="farm":
                self.farm_vars["seconds"].set(str(self.data["farm"]["seconds"]))
            self.deadline=None
            self.full_index=None
            self.awaiting_result=True
        self.update_timer_display()

    def tick_timer(self):
        if self.deadline is None:
            return
        if time.monotonic()>=self.deadline:
            self.deadline=None
            self.timer_job=None
            self.awaiting_result=True
            self.data["farm"]["seconds"]=self.timer_duration
            if self.page=="farm":
                self.farm_vars["seconds"].set(str(self.timer_duration))
            self.bell()
        else:
            self.timer_job=self.after(100,self.tick_timer)
        self.update_timer_display()

    def update_timer_display(self):
        if self.page!="farm" or not hasattr(self,"timer_label"):
            return
        remaining=max(0,math.ceil(self.deadline-time.monotonic())) if self.deadline else (0 if self.awaiting_result else self.timer_duration)
        self.timer_label.configure(text=f"{remaining//60:02d}:{remaining%60:02d}")
        if self.full_index is not None:
            self.test_label.configure(text=self.t("test_step",index=self.full_index+1,seconds=(60,60,180)[self.full_index]))
        elif self.awaiting_result:
            self.test_label.configure(text=self.t("test_finished"))
        else:
            self.test_label.configure(text="")

    def record_result(self):
        self.read_farm()
        f=self.data["farm"]
        if self.full_index is not None and not self.awaiting_result:
            raise ValueError(self.t("test_finished"))
        seconds=self.timer_duration if self.full_index is not None else f["seconds"]
        buffs=self.timer_buffs if self.awaiting_result else (f["talisman"],f["consumable"])
        self.planner.add_sample(f["runes"],seconds,*buffs,notes=f["notes"])
        self.awaiting_result=False
        if self.full_index is not None:
            self.full_index+=1
            if self.full_index==3:
                self.full_index=None
                self.timer_duration=60
                messagebox.showinfo(self.t("full_test"),self.t("full_finished"),parent=self)
            else:
                self.timer_duration=(60,60,180)[self.full_index]
        self.autosave()
        self.show("farm")

    def build_settings(self):
        form=self.card(self.body)
        form.pack(fill="x")
        self.label(form,self.t("language")).grid(row=0,column=0,padx=18,pady=18,sticky="w")
        self.language_var=tk.StringVar(value=LANGUAGE_NAMES[self.data["language"]])
        ctk.CTkOptionMenu(form,variable=self.language_var,values=list(LANGUAGE_NAMES.values()),width=240).grid(row=0,column=1,padx=18,pady=18)
        self.theme_option=self.option(form,"theme",tuple(PALETTES),self.data["theme"],lambda _:None,1)
        self.button(form,"apply_settings",self.apply_settings).grid(row=2,column=0,padx=18,pady=18)
        self.label(self.body,self.t("autosave_note"),muted=True,wraplength=900,justify="left").pack(anchor="w",pady=20)
        for key,command in (("save_project",self.save),("open_project",self.load),("reset_session",self.reset_session)):
            self.button(self.body,key,command,True).pack(anchor="w",pady=8)
        self.label(self.body,self.t("help_body"),muted=True,wraplength=900,justify="left").pack(anchor="w",pady=24)
        if self.startup_error:
            self.label(self.body,self.startup_error,muted=True,wraplength=900).pack(anchor="w")

    def apply_settings(self):
        self.data["language"]=next(k for k,v in LANGUAGE_NAMES.items() if v==self.language_var.get())
        self.data["theme"]=next(k for k in PALETTES if self.t(k)==self.theme_option.get())
        self.autosave()
        self.build_shell()

    def save(self):
        path=filedialog.asksaveasfilename(parent=self,defaultextension=".json",filetypes=[("Auto Elden Ring project","*.json")])
        if path:
            save_project(path,self.data,self.db)

    def load(self):
        path=filedialog.askopenfilename(parent=self,filetypes=[("Auto Elden Ring project","*.json")])
        if not path:
            return
        state=load_project(path,self.db)
        window=self.popup(self.t("open_project"),"650x370")
        self.label(window,self.t("resume_hint"),wraplength=600,justify="left").pack(padx=24,pady=20)
        keep=tk.BooleanVar(value=True)
        ctk.CTkCheckBox(window,text=self.t("keep_stats"),variable=keep).pack(anchor="w",padx=24,pady=12)
        form=self.card(window)
        form.pack(fill="x",padx=24)
        wallet=self.entry(form,"runes_held",state["runes"],0)
        def resume():
            value=integer(wallet.get())
            self.reset_timer()
            self.planner=Planner(self.db,state)
            self.planner.set_wallet(value)
            self.page="weapons" if keep.get() else "character"
            window.destroy()
            self.autosave()
            self.build_shell()
            self.inventory_popup()
        self.button(window,"done",resume).pack(pady=18)

    def reset_session(self):
        if messagebox.askyesno(self.t("reset_session"),self.t("confirm_reset"),parent=self):
            self.reset_timer()
            self.planner=Planner(self.db,default_state())
            self.page="character"
            self.autosave()
            self.build_shell()

    def close(self):
        try:
            if self.page=="character":
                self.calculate_character()
            elif self.page=="weapons":
                self.read_weapons()
            elif self.page=="farm":
                self.read_farm()
            self.autosave()
        except (ValueError,OSError,tk.TclError):
            pass
        if self.timer_job:
            self.after_cancel(self.timer_job)
        self.destroy()

    def destroy(self):
        # Tk callbacks registered by transient widgets must not outlive a root.
        try:
            for job in self.tk.splitlist(self.tk.call("after","info")):
                self.after_cancel(job)
        except tk.TclError:
            pass
        super().destroy()


def run():
    App().mainloop()

