"""Profile selection, local menus, illustrated snapshots and compact workflows."""
from copy import deepcopy
from collections import OrderedDict
import math
import time
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from classes_data import ATTRIBUTES
from .core import integer, resource_path
from .windows import monitor_workarea, snap_position, position_window


class JourneyFeatures:
    def modal(self,window):
        window._previous_grab=self.grab_current()
        window.grab_set()

    def rgb_notice(self):
        if self._closing or self.data["style"]!="rainbow":
            return
        window=self.popup(self.t("rgb_beta"),"650x300")
        self.label(window,"RGB",30).pack(pady=(22,8))
        self.label(window,self.t("rgb_beta_hint"),16,wraplength=580,justify="left").pack(padx=24,pady=18)
        self.button(window,"done",window.destroy).pack(pady=12)
        return window

    def show_profile_picker(self,startup=False):
        current=getattr(self,"profile_picker",None)
        if current is not None and current.winfo_exists():
            current.destroy()
        self.profiles.sync(self.data)
        window=self.popup(self.t("choose_profile"),"820x650")
        self.profile_picker=window
        self.label(window,self.t("choose_profile"),26).pack(pady=(24,8))
        self.label(window,self.t("profile_hint"),muted=True,wraplength=740).pack(pady=8)
        actions=ctk.CTkFrame(window,fg_color="transparent")
        actions.pack(pady=14)
        self.button(actions,"new_character",self.new_profile).pack(side="left",padx=6)
        self.button(actions,"import_save",self.import_dialog,True).pack(side="left",padx=6)
        scroll=ctk.CTkScrollableFrame(window,fg_color=self.bg)
        scroll.pack(fill="both",expand=True,padx=22,pady=18)
        window.profile_cards={}
        for ident,profile in self.profiles.data["profiles"].items():
            state=profile["state"]
            if not state["profile_created"]:
                continue
            card=self.card(scroll)
            card.pack(fill="x",pady=6)
            self.label(card,state["character_name"][:1].upper(),30).pack(side="left",padx=20,pady=14)
            title=state["character_name"]+"\n"+self.t(state["class_name"])+" · "+self.t("level")+" "+str(sum(state["stats_current"].values())-79)
            def select(i=ident):
                self.page="character"
                self.activate_profile(self.profiles.select(i))
            button=ctk.CTkButton(card,text=title,font=self.font(16),height=68,anchor="w",
                fg_color=self.paper,text_color=self.ink,command=lambda f=select:self.action(f))
            button.pack(fill="x",expand=True,padx=14,pady=10)
            window.profile_cards[ident]=button
        if not window.profile_cards:
            self.label(scroll,self.t("empty_profiles"),muted=True,wraplength=650).pack(pady=35)
        window.protocol("WM_DELETE_WINDOW",self.close if startup else window.destroy)
        self.modal(window)
        self.normalize_surfaces(window)
        return window

    def ask_import_policy(self,path,window,status):
        prompt=self.popup(self.t("import_profiles"),"700x350")
        self.label(prompt,self.t("import_policy_hint"),18,wraplength=620,justify="left").pack(padx=25,pady=30)
        def choose(replace):
            prompt.destroy()
            self.begin_import(path,window,status,policy="replace" if replace else "keep")
        self.button(prompt,"keep_manual",lambda:choose(False)).pack(pady=8)
        self.button(prompt,"replace_manual",lambda:choose(True),True).pack(pady=8)
        prompt.keep_profiles=lambda:choose(False)
        prompt.replace_profiles=lambda:choose(True)
        self.modal(prompt)
        return prompt

    def import_save_list(self,paths,parent=None):
        window=self.popup(self.t("select_save"),"800x500")
        self.label(window,self.t("save_accounts"),wraplength=730).pack(pady=20)
        scroll=ctk.CTkScrollableFrame(window,fg_color=self.bg)
        scroll.pack(fill="both",expand=True,padx=20,pady=20)
        self.button(window,"import_all_saves",lambda:self.begin_import(paths,window,policy=None)).pack(pady=12)
        for path in paths:
            button=ctk.CTkButton(scroll,text=path.parent.name+" · "+path.name,font=self.font(),
                fg_color=self.soft,text_color=self.ink,height=42,
                command=lambda p=path:self.begin_import(p,window,policy=None))
            button.pack(fill="x",pady=6)
        return window

    def install_scroll_menu(self,option):
        if getattr(option,"_local_menu_installed",False):
            return
        option._local_menu_installed=True
        option._dropdown_menu.open=lambda *_:self.open_scroll_menu(option)

    def open_scroll_menu(self,option):
        previous=getattr(self,"scroll_menu",None)
        if previous is not None and previous.winfo_exists():
            previous.destroy()
        window=self.popup("", "300x320")
        self.scroll_menu=window
        window.overrideredirect(True)
        values=option.cget("values")
        height=min(10,max(1,len(values)))*30+8
        width=max(260,option.winfo_width())
        left,top,right,bottom=monitor_workarea(option)
        x=min(max(left,option.winfo_rootx()),right-width)
        y=option.winfo_rooty()+option.winfo_height()
        if y+height>bottom:
            y=max(top,option.winfo_rooty()-height)
        window.geometry(f"{width}x{height}{x:+d}{y:+d}")
        window.after(0,lambda:position_window(window,x,y))
        box=tk.Listbox(window,background=self.paper,foreground=self.ink,
            selectbackground=self.accent,selectforeground="#FFFFFF",
            highlightthickness=1,highlightbackground=self.soft,bd=0,
            font=(self.font_family,15 if self.data["dyslexic"] else 13),activestyle="none",exportselection=False)
        bar=ctk.CTkScrollbar(window,command=box.yview,fg_color=self.paper,button_color=self.soft)
        box.configure(yscrollcommand=bar.set)
        bar.pack(side="right",fill="y")
        box.pack(fill="both",expand=True,padx=3,pady=3)
        for value in values:
            box.insert("end",value)
        if option.get() in values:
            index=values.index(option.get())
            box.selection_set(index)
            box.see(index)
        def wheel(event):
            box.yview_scroll(-int(event.delta/120)*3,"units")
            return "break"
        def select(_=None):
            choice=box.curselection()
            if choice:
                value=values[choice[0]]
                window.destroy()
                option._dropdown_callback(value)
            return "break"
        box.bind("<MouseWheel>",wheel)
        box.bind("<ButtonRelease-1>",select)
        box.bind("<Return>",select)
        window.bind("<Escape>",lambda _:window.destroy())
        window.bind("<FocusOut>",lambda _:window.after(100,lambda:window.destroy() if window.winfo_exists() and not str(window.focus_get()).startswith(str(window)) else None))
        window.menu_list=box
        window.choose_value=select
        window.wheel=wheel
        window.after(10,box.focus_set)
        return window

    def weapon_icon(self,name,size=52):
        cache=getattr(self,"detail_icons",None)
        if cache is None:
            self.detail_icons=cache=OrderedDict()
        key=(name,size)
        if key not in cache:
            weapon=self.db.weapons[name]
            ident=self.db.raw["weapons_by_category"][weapon.category][name]["id"]
            with Image.open(resource_path(f"assets/catalogue/{ident}.webp")) as source:
                image=source.convert("RGBA")
            cache[key]=ctk.CTkImage(image,size=(size,size))
            while len(cache)>64:
                cache.popitem(last=False)
        cache.move_to_end(key)
        return cache[key]

    def checkpoint_cards(self,point):
        from .ui_v4 import display_date
        state=point["state"]
        window=self.popup(self.t("view_checkpoint"),"920x740")
        self.label(window,state["character_name"],28).pack(pady=(18,6))
        self.label(window,display_date(point["date"])+" · "+self.t(state["class_name"]),muted=True).pack(pady=6)
        body=ctk.CTkScrollableFrame(window,fg_color=self.bg)
        body.pack(fill="both",expand=True,padx=22,pady=14)
        note=self.t(point["note"]) if point["note"] in self.translator.text else point["note"]
        self.label(body,note,18,wraplength=820).pack(anchor="w",pady=8)
        summary=self.metrics(body,[(self.t("level"),str(sum(state["stats_current"].values())-79)),
                                  (self.t("runes_held"),f'{state["runes"]:,}')])
        stats=self.card(body)
        stats.pack(fill="x",pady=8)
        for index,key in enumerate(ATTRIBUTES):
            self.label(stats,self.t(key)+"   "+str(state["stats_current"][key]),16).grid(
                row=index//2,column=index%2,sticky="w",padx=20,pady=10)
        tabs=ctk.CTkSegmentedButton(body,values=[self.t("owned_weapons"),self.t("changes"),self.t("goal")],font=self.font())
        tabs.pack(fill="x",pady=14)
        content=ctk.CTkFrame(body,fg_color="transparent")
        content.pack(fill="x")
        window.weapon_cards={}
        def render(value,offset=0):
            for child in content.winfo_children():
                child.destroy()
            window.weapon_cards={}
            if value==self.t("owned_weapons"):
                items=state["inventory_weapons"][offset:offset+24]
                window.weapon_page_offset=offset
                for index,item in enumerate(items):
                    card=self.card(content)
                    card.grid(row=index//2,column=index%2,sticky="ew",padx=5,pady=5)
                    icon=self.weapon_icon(item["name"])
                    label=self.label(card,"",image=icon)
                    label.pack(side="left",padx=12,pady=12)
                    label.snapshot_icon=icon
                    self.label(card,self.translator.weapon(item["name"])+f'\n+{item["current"]}  ×{item["quantity"]}',
                               14,wraplength=290,justify="left").pack(side="left",padx=8,pady=12)
                    window.weapon_cards[(item["name"],item["current"])]=card
                content.grid_columnconfigure((0,1),weight=1)
                if len(state["inventory_weapons"])>24:
                    navigation=ctk.CTkFrame(content,fg_color="transparent")
                    navigation.grid(row=12,column=0,columnspan=2,pady=12)
                    if offset:
                        self.button(navigation,"previous_page",lambda:render(value,max(0,offset-24)),True).pack(side="left",padx=6)
                    if offset+24<len(state["inventory_weapons"]):
                        self.button(navigation,"next_page",lambda:render(value,offset+24),True).pack(side="left",padx=6)
            else:
                if value==self.t("changes"):
                    lines=[]
                    for change in point.get("changes",[]):
                        field=change["field"]
                        title=self.translator.weapon(change["name"])+f' +{change["upgrade"]}' if field=="weapon" else self.translator.stone(field) if ":" in field else self.t(field)
                        lines.append(f'{title}: {change["before"]} → {change["after"]}')
                else:
                    lines=[self.t(k)+f': {state["stats_current"][k]} → {state["stats_target"][k]}' for k in ATTRIBUTES]
                    lines.extend(self.translator.weapon(i["name"])+f'  +{i["current"]} → +{i["target"]} ×{i["quantity"]}' for i in state["selected"])
                    if state["weapon_mode"]=="manual":
                        m=state["manual"]
                        lines.append(self.t("manual_mode")+f'  +{m["current"]} → +{m["target"]} ×{m["quantity"]}')
                for line in lines:
                    self.label(content,line,15,wraplength=820,justify="left").pack(anchor="w",pady=6)
        tabs.configure(command=render)
        tabs.set(self.t("owned_weapons"))
        render(tabs.get())
        window.detail_tabs=tabs
        window.render_tab=render
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
        current=getattr(self,"compact_window",None)
        if current is not None and current.winfo_exists():
            current.lift()
            return current
        for popup in tuple(self.popups):
            popup.destroy()
        if hasattr(self,"gallery"):
            self.gallery.cache.clear()
        window=self.popup(self.t("small_mode"),"430x630")
        self.compact_window=window
        window.transient("")
        window.overrideredirect(True)
        window.resizable(False,False)
        window.attributes("-topmost",True)
        heading=self.card(window)
        heading.pack(fill="x",padx=8,pady=8)
        title=self.label(heading,self.data["character_name"],19)
        title.pack(side="left",padx=14,pady=12)
        drag={}
        def press(event):
            drag.update(x=event.x_root-window.winfo_x(),y=event.y_root-window.winfo_y())
        def move(event):
            if drag:
                position_window(window,event.x_root-drag["x"],event.y_root-drag["y"])
        def snap(_=None):
            x,y=snap_position(window.winfo_x(),window.winfo_y(),window.winfo_width(),window.winfo_height(),monitor_workarea(window))
            position_window(window,x,y)
        for widget in (heading,title):
            widget.bind("<ButtonPress-1>",press)
            widget.bind("<B1-Motion>",move)
            widget.bind("<ButtonRelease-1>",snap)
        controls=ctk.CTkFrame(window,fg_color="transparent")
        controls.pack(fill="x",padx=12,pady=6)
        mode=tk.StringVar(value=self.page if self.page in ("character","weapons","farm") else "character")
        body=ctk.CTkFrame(window,fg_color="transparent")
        body.pack(fill="both",expand=True,padx=12)
        text=self.label(body,"",wraplength=390,justify="left",size=15)
        text.pack(anchor="w",padx=6,pady=8)
        wallet=self.card(window)
        wallet.pack(fill="x",padx=12,pady=6)
        runes=self.entry(wallet,"runes_held",self.data["runes"],0,width=145)
        panes={key:ctk.CTkFrame(body,fg_color="transparent") for key in ("character","weapons","farm")}
        materials=ctk.CTkScrollableFrame(panes["weapons"],fg_color=self.bg,height=190)
        materials.pack(fill="both",expand=True)
        window.purchase_rows={}
        def paint_stones():
            rows=[r for r in self.planner.weapons()["stones"] if not r["key"].endswith("dragon")]
            for row in rows:
                key=row["key"]
                if key not in window.purchase_rows:
                    panel=self.card(materials)
                    panel.pack(fill="x",pady=3)
                    label=self.label(panel,"",13)
                    label.pack(side="left",padx=10,pady=9)
                    def buy(k=key):
                        self.planner.purchase(k)
                        self.autosave()
                        refresh()
                    button=self.button(panel,"bought",buy,True,width=90)
                    button.pack(side="right",padx=8)
                    window.purchase_rows[key]={"label":label,"button":button,"buy":buy}
                widgets=window.purchase_rows[key]
                complete=row["missing"]==0
                widgets["label"].configure(text=("✓ " if complete else "")+self.translator.stone(key)+f' ×{row["missing"]}')
                widgets["button"].configure(state="disabled" if complete else "normal",text="✓" if complete else self.t("bought"),
                    fg_color="#438B64" if complete else self.soft)
        def all_stones():
            self.acknowledge_all_stones()
            refresh()
        self.button(panes["weapons"],"all_stones",all_stones,True).pack(fill="x",pady=7)
        timer=self.label(panes["farm"],"01:00",30)
        timer.pack(pady=7)
        timer_actions=ctk.CTkFrame(panes["farm"],fg_color="transparent")
        timer_actions.pack()
        baseline=[self.data["runes"]]
        def start():
            baseline[0]=self.data["runes"]
            self.start_timer()
        for key,command in (("mini_start",start),("stop",self.stop_timer),("mini_reset",self.reset_timer)):
            self.button(timer_actions,key,command,True,width=115).pack(side="left",padx=3)
        gain_form=self.card(panes["farm"])
        gain_form.pack(fill="x",pady=8)
        gain=self.entry(gain_form,"measured_runes",0,0,width=130)
        def record():
            if self.deadline is not None:
                raise ValueError(self.t("test_finished"))
            measured=integer(gain.get(),"Measured runes",1)
            f=self.data["farm"]
            seconds=f["seconds"] if self.awaiting_result else 60
            if self.full_index is not None:
                self.farm_vars["runes"].set(str(measured))
                self.record_result()
                refresh()
                return
            self.planner.add_sample(measured,seconds,*(self.timer_buffs if self.awaiting_result else (f["talisman"],f["consumable"])))
            f.update(runes=measured,seconds=seconds)
            self.awaiting_result=False
            self.full_index=None
            self.timer_duration=60
            if hasattr(self,"farm_vars"):
                for key in ("runes","seconds"):
                    self.farm_vars[key].set(str(f[key]))
            self.autosave()
            refresh()
        self.button(panes["farm"],"record_result",record).pack(pady=10)
        def refresh():
            c=self.planner.character()
            value=mode.get()
            remaining=c["deficit"]
            detail=self.t("level_route",current=c["current"],target=c["target"],count=c["levels"])
            if value=="weapons":
                w=self.planner.weapons()
                remaining=w["deficit"]
                detail=self.t("total_cost")+": "+f'{w["total"]:,}'
                paint_stones()
            elif value=="farm":
                goal,_=self.planner.farm_goal()
                remaining=max(0,goal-self.data["runes"])
                try:
                    detail=self.t("time_needed")+": "+self.translator.duration(self.planner.farm_projection()["time"])
                except ValueError:
                    detail=self.t("new_measurement")
            text.configure(text=detail+"\n"+self.t("to_farm")+": "+f"{remaining:,}")
            for key,pane in panes.items():
                pane.pack_forget()
                if key==value:
                    pane.pack(fill="both",expand=True)
        def wallet_changed(*_):
            try:
                value=integer(runes.get())
            except ValueError:
                return
            self.data["runes"]=value
            for var in self.wallet_vars.values():
                var.set(str(value))
            if self.deadline is not None or self.awaiting_result:
                gain.set(str(max(0,value-baseline[0])))
            self.autosave()
            refresh()
        runes.trace_add("write",wallet_changed)
        for key in panes:
            self.button(controls,key,lambda k=key:(mode.set(k),refresh()),True,width=125).pack(side="left",padx=3)
        def reopen():
            self.deiconify()
            self.show(mode.get())
            window.destroy()
            self.refresh_farm_results()
        window.protocol("WM_DELETE_WINDOW",reopen)
        self.button(window,"full_window",reopen).pack(fill="x",padx=12,pady=10)
        window.rune_var=runes
        window.mode_var=mode
        window.summary_label=text
        window.refresh_summary=refresh
        window.reopen=reopen
        window.snap=snap
        window.gain_var=gain
        window.record_sample=record
        window.start_sample=start
        window.timer_label=timer
        window.all_stones=all_stones
        def pulse():
            remaining=max(0,math.ceil(self.deadline-time.monotonic())) if self.deadline else (0 if self.awaiting_result else self.timer_duration)
            timer.configure(text=f"{remaining//60:02d}:{remaining%60:02d}")
            window.after(250,pulse)
        refresh()
        self.withdraw()
        window.deiconify()
        window.lift()
        window.after(10,snap)
        pulse()
        self.release_compact_pages()
        return window
