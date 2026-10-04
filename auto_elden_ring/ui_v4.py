"""Profile-first journal, save import, semantic themes and a compact companion."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
import colorsys
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
import time
import customtkinter as ctk
from PIL import Image, ImageOps, ImageTk
from classes_data import CLASS_DATA, ATTRIBUTES
from .core import integer, resource_path
from .profiles import timestamp
from .save_reader import read_save, read_saves, discover
from .history import import_characters,differences
from .windows import suspend_redraw,cancel_widget_jobs
from .ui_v5 import JourneyFeatures


def display_date(value):
    return datetime.fromisoformat(value).astimezone().strftime("%d/%m/%Y %H:%M")


class Features(JourneyFeatures):
    def apply_appearance(self):
        with suspend_redraw(self):
            self._legacy_apply_appearance()
            self.refresh_goal_spots()
            self.normalize_surfaces()
            if "journal" in self.views:
                self.draw_timeline()
            self.update_idletasks()
            self.paint_background()
        self.start_rgb()

    def normalize_surfaces(self,root=None):
        """Use semantic roles, never compare the previous palette's hex values."""
        self.rgb_targets=None
        def parent_color(widget):
            parent=widget.master
            while parent is not None:
                try:
                    color=parent.cget("fg_color")
                    if isinstance(color,str) and color!="transparent":
                        return color
                except (ValueError,tk.TclError,AttributeError):
                    pass
                parent=getattr(parent,"master",None)
            return self.bg
        def configure(widget,**values):
            changed={}
            for key,value in values.items():
                try:
                    current=widget.cget(key)
                except ValueError:
                    current=None
                if current!=value:
                    changed[key]=value
            if changed:
                widget.configure(**changed)
        def visit(widget):
            color=parent_color(widget)
            if isinstance(widget,ctk.CTkScrollableFrame):
                configure(widget,fg_color=self.bg,bg_color=color,
                                 scrollbar_button_color=self.soft,scrollbar_button_hover_color=self.accent)
                widget._parent_canvas.configure(bg=self.bg)
                # Its inner Tk frame is a separate surface from CTk's fg_color.
                # Retained controls can leave this native background in an old palette.
                tk.Frame.configure(widget,bg=self.bg)
                widget._scrollbar.configure(fg_color=self.bg,bg_color=self.bg)
            elif isinstance(widget,ctk.CTkBaseClass):
                try:
                    configure(widget,bg_color=color)
                except ValueError:
                    pass
                if isinstance(widget,ctk.CTkFrame) and not isinstance(widget,ctk.CTkSegmentedButton):
                    role=getattr(widget,"_surface_role",None)
                    if role:
                        configure(widget,fg_color=getattr(self,role))
                    elif widget.cget("fg_color")!="transparent":
                        configure(widget,fg_color=self.bg)
                elif isinstance(widget,ctk.CTkOptionMenu):
                    self.install_scroll_menu(widget)
                    configure(widget,fg_color=self.soft,button_color=self.accent,button_hover_color=self.accent,
                                     text_color=self.ink,dropdown_fg_color=self.paper,dropdown_text_color=self.ink,
                                     dropdown_hover_color=self.soft)
                elif isinstance(widget,ctk.CTkSegmentedButton):
                    configure(widget,fg_color=self.soft,selected_color=self.accent,selected_hover_color=self.accent,
                                     unselected_color=self.soft,unselected_hover_color=self.paper,text_color=self.ink)
                elif isinstance(widget,ctk.CTkButton):
                    secondary=getattr(widget,"_secondary",False)
                    if isinstance(widget.master,ctk.CTkSegmentedButton):
                        secondary=widget.master.get()!=widget.cget("text")
                    configure(widget,fg_color=self.soft if secondary else self.accent,
                                     text_color=self.ink if secondary else "#FFFFFF",hover_color=self.accent)
                elif isinstance(widget,ctk.CTkEntry):
                    configure(widget,fg_color=self.paper,text_color=self.ink,border_color=self.soft)
                elif isinstance(widget,ctk.CTkTextbox):
                    configure(widget,fg_color=self.bg,text_color=self.ink,
                                     scrollbar_button_color=self.soft,scrollbar_button_hover_color=self.accent)
                elif isinstance(widget,ctk.CTkCheckBox):
                    configure(widget,fg_color=self.accent,border_color=self.muted,text_color=self.ink)
                elif isinstance(widget,ctk.CTkLabel):
                    configure(widget,fg_color="transparent",text_color=self.muted if getattr(widget,"_text_role","ink")=="muted" else self.ink)
            for child in widget.winfo_children():
                visit(child)
        if root:
            visit(root)
        else:
            for child in self.winfo_children():
                visit(child)
        self.refresh_nav()
        self.profile_button.configure(text=self.data["character_name"] if self.data["profile_created"] else self.t("switch_character"))
        self.refresh_art()

    def refresh_art(self):
        # The artwork is part of the window background, never a thumbnail/banner.
        for record in self.views.values():
            record["art"].pack_forget()
        if hasattr(self,"side_art"):
            self.side_art.pack_forget()
        if not hasattr(self,"background_layers"):
            self.background_layers=[]
            self.background_job=None
            self.bind("<Configure>",self.queue_background,add="+")
        self.queue_background()

    def queue_background(self,event=None):
        if event and event.widget is not self:
            return
        if self.background_job:
            self.after_cancel(self.background_job)
        self.background_job=self.after(120,self.paint_background)

    def paint_background(self):
        self.background_job=None
        if self.data["style"]!="elden" or self.data["dyslexic"] or self._closing or not self.winfo_viewable():
            for widget,_ in getattr(self,"background_text",[]):
                if widget.winfo_exists():
                    widget._label.configure(image="")
            self.background_text=[]
            for layer in self.background_layers:
                if layer.winfo_exists():
                    layer.destroy()
            self.background_layers=[]
            self.background_key=None
            return
        width,height=max(1,self.winfo_width()),max(1,self.winfo_height())
        if width<100:
            return
        record=self.views[self.page]
        surfaces=[]
        base_widgets=(self,self.host,record["frame"],record["body"])
        allowed=base_widgets+(record["body"]._parent_frame,)
        art_widgets=list(base_widgets)
        text_widgets=[]
        def collect(widget,blocked=False):
            if isinstance(widget,ctk.CTkFrame) and widget not in allowed:
                if widget.cget("fg_color")=="transparent" and not blocked and widget.winfo_ismapped():
                    art_widgets.append(widget)
                elif widget.cget("fg_color")!="transparent":
                    blocked=True
            if isinstance(widget,ctk.CTkLabel) and not blocked and widget._image is None and widget.winfo_ismapped():
                art_widgets.append(widget)
                text_widgets.append(widget)
            for child in widget.winfo_children():
                collect(child,blocked)
        collect(record["frame"])
        for widget in art_widgets:
            viewport=widget._parent_canvas if isinstance(widget,ctk.CTkScrollableFrame) else widget
            w,h=max(1,viewport.winfo_width()),min(height,max(1,viewport.winfo_height()))
            x,y=viewport.winfo_rootx()-self.winfo_rootx(),viewport.winfo_rooty()-self.winfo_rooty()
            surfaces.append((widget,viewport,w,h,x,y))
        key=(width,height,self.page,self.data["theme"],tuple((widget._w,w,h,x,y) for widget,_,w,h,x,y in surfaces))
        if key==getattr(self,"background_key",None) and len(self.background_layers)==len(surfaces) and all(layer.winfo_exists() for layer in self.background_layers):
            return  # Moving the window does not change relative artwork geometry.
        path={"moon":"elden-moon.webp","ember":"elden-ember.webp","elden":"elden-night.webp"}[self.data["theme"]]
        with Image.open(resource_path("assets/"+path)) as source:
            picture=ImageOps.fit(source.convert("RGB"),(width,height))
        picture=Image.blend(picture,Image.new("RGB",(width,height),self.bg),.48)
        old_layers=self.background_layers
        self.background_layers=[]
        for widget,_ in getattr(self,"background_text",[]):
            if widget.winfo_exists():
                widget._label.configure(image="")
        self.background_text=[]
        for widget,viewport,w,h,x,y in surfaces:
            # Out-of-window gutters must use the palette, not Pillow's black pad.
            crop=Image.new("RGB",(w,h),self.bg)
            left,top,right,bottom=max(0,x),max(0,y),min(width,x+w),min(height,y+h)
            if right>left and bottom>top:
                crop.paste(picture.crop((left,top,right,bottom)),(left-x,top-y))
            photo=ImageTk.PhotoImage(crop,master=self)
            layer=tk.Label(widget,image=photo,bd=0,highlightthickness=0)
            layer.photo=photo
            scroll=int(viewport.canvasy(0)) if viewport is not widget else 0
            layer.place(x=0,y=scroll,width=w,height=h)
            layer.lower()
            # CTk frames draw a full-size canvas: place art above that canvas
            # while leaving interactive child controls above the background.
            canvas=getattr(widget,"_canvas",None)
            if canvas is not None and canvas.master is widget:
                layer.tk.call("raise",layer._w,canvas._w)
            self.background_layers.append(layer)
            if widget in text_widgets:
                native=widget._label
                nx,ny=native.winfo_rootx()-self.winfo_rootx(),native.winfo_rooty()-self.winfo_rooty()
                nw,nh=max(1,native.winfo_width()),max(1,native.winfo_height())
                patch=Image.new("RGB",(nw,nh),self.bg)
                l,t,r,b=max(0,nx),max(0,ny),min(width,nx+nw),min(height,ny+nh)
                if r>l and b>t:
                    patch.paste(picture.crop((l,t,r,b)),(l-nx,t-ny))
                text_photo=ImageTk.PhotoImage(patch,master=self)
                native.configure(image=text_photo,compound="center")
                self.background_text.append((widget,text_photo))
            if isinstance(widget,ctk.CTkScrollableFrame):
                widget._background_layer=layer
                if not getattr(widget,"_background_scroll_bound",False):
                    def scroll_art(first,last,body=widget):
                        body._scrollbar.set(first,last)
                        art=getattr(body,"_background_layer",None)
                        if art is not None and art.winfo_exists():
                            art.place_configure(y=int(body._parent_canvas.canvasy(0)))
                        self.queue_background()
                    viewport.configure(yscrollcommand=scroll_art)
                    widget._background_scroll_bound=True
        # Construct replacement images first, so resize never exposes an empty
        # background while an old native image window is being removed.
        for layer in old_layers:
            if layer.winfo_exists():
                layer.destroy()
        self.background_key=key

    def start_rgb(self):
        if getattr(self,"rgb_job",None):
            self.after_cancel(self.rgb_job)
            self.rgb_job=None
        if self.data["style"]!="rainbow" or self.data["dyslexic"]:
            return
        self.rgb_started=time.monotonic()
        self.rgb_tick()

    def rgb_tick(self):
        self.rgb_job=None
        if self._closing or self.data["style"]!="rainbow" or self.data["dyslexic"]:
            return
        if self.winfo_viewable():
            hue=((time.monotonic()-self.rgb_started)/3)%1
            def color(offset,value=.85):
                rgb=colorsys.hsv_to_rgb((hue+offset)%1,.75,value)
                return "#"+"".join(f"{int(c*255):02x}" for c in rgb)
            targets=getattr(self,"rgb_targets",None)
            if targets is None:
                targets=[]
                def collect(widget):
                    # Native text color changes do not redraw rounded CTk surfaces.
                    for attribute in ("_text_label","_label","_entry","_textbox"):
                        native=getattr(widget,attribute,None)
                        if isinstance(native,(tk.Label,tk.Entry,tk.Text)) and native not in targets:
                            targets.append(native)
                    for child in widget.winfo_children():
                        collect(child)
                collect(self.sidebar)
                collect(self.views[self.page]["frame"])
                for popup in tuple(self.popups):
                    if popup.winfo_exists():
                        collect(popup)
                self.rgb_targets=targets
            light=self.data["theme"] in ("pastel","prism")
            for index,native in enumerate(targets):
                if native.winfo_exists():
                    native.configure(fg=color(index*.07,.48 if light else .95))
            canvases=[]
            if getattr(self,"timeline",None) is not None and self.timeline.winfo_exists():
                canvases.append(self.timeline)
            if getattr(self,"gallery_window",None) is not None and self.gallery_window.winfo_exists():
                canvases.append(self.gallery.canvas)
            for canvas in canvases:
                for index,item in enumerate(canvas.find_all()):
                    if canvas.type(item)=="text":
                        canvas.itemconfigure(item,fill=color(index*.07))
        self.rgb_job=self.after(66,self.rgb_tick)

    def build_journal(self):
        actions=ctk.CTkFrame(self.body,fg_color="transparent")
        actions.pack(anchor="w",pady=(0,18))
        for key,command in (("new_character",self.new_profile),("import_save",self.import_dialog)):
            self.button(actions,key,command).pack(side="left",padx=(0,12))
        self.profiles.sync(self.data)
        people=[(ident,p) for ident,p in self.profiles.data["profiles"].items() if p["state"]["profile_created"]]
        if not people:
            self.label(self.body,self.t("empty_profiles"),muted=True,wraplength=800).pack(pady=40)
            self.timeline=None
            return
        profiles=ctk.CTkFrame(self.body,fg_color="transparent")
        profiles.pack(fill="x",pady=12)
        for index,(ident,profile) in enumerate(people):
            state=profile["state"]
            text=state["character_name"]+"\n"+self.t(state["class_name"])+" · "+self.t("level")+" "+str(sum(state["stats_current"].values())-79)
            button=ctk.CTkButton(profiles,text=text,font=self.font(14),height=88,width=230,corner_radius=12,
                fg_color=self.accent if ident==self.profiles.data["active"] else self.soft,text_color=self.ink,
                command=lambda i=ident:self.action(lambda:self.open_timeline(i)))
            button.grid(row=index//3,column=index%3,padx=(0,12),pady=6,sticky="ew")
        if not self.data["profile_created"]:
            self.timeline=None
            return
        self.label(self.body,self.data["character_name"],24).pack(anchor="w",pady=16)
        actions=ctk.CTkFrame(self.body,fg_color="transparent")
        actions.pack(anchor="w",pady=(0,16))
        self.button(actions,"add_event",self.event_dialog).pack(side="left",padx=(0,12))
        if self.data["save_link"]:
            self.button(actions,"refresh_save",self.refresh_import,True).pack(side="left")
            unknown=self.data["save_link"].get("unknown_items",0)
            if unknown:
                self.label(self.body,self.t("unknown_items",count=unknown),muted=True,wraplength=850).pack(anchor="w",pady=8)
        self.timeline_offset=getattr(self,"timeline_offset",0)
        self.timeline_controls=ctk.CTkFrame(self.body,fg_color="transparent")
        self.older_button=self.button(self.timeline_controls,"older_events",self.show_older_events,True)
        self.older_button.pack(side="left",padx=(0,10))
        self.newer_button=self.button(self.timeline_controls,"newer_events",self.show_newer_events,True)
        self.newer_button.pack(side="left")
        self.timeline=tk.Canvas(self.body,bg=self.bg,highlightthickness=0,height=240)
        self.timeline.pack(fill="x")
        self.timeline.bind("<Configure>",lambda _:self.draw_timeline())
        self.draw_timeline()

    def open_timeline(self,ident):
        if ident!=self.profiles.data["active"]:
            self.timeline_offset=0
            self.switch_profile(ident)
        self.show("journal",refresh=True)

    def show_older_events(self):
        limit=max(0,((len(self.profiles.active["checkpoints"])-1)//100)*100)
        self.timeline_offset=min(limit,self.timeline_offset+100)
        self.draw_timeline()

    def show_newer_events(self):
        self.timeline_offset=max(0,self.timeline_offset-100)
        self.draw_timeline()

    def refresh_timeline(self):
        if "journal" in self.views:
            self.draw_timeline()

    def draw_timeline(self):
        canvas=getattr(self,"timeline",None)
        if canvas is None or not canvas.winfo_exists():
            return
        canvas.delete("all")
        canvas.configure(bg=self.bg)
        points=self.profiles.active["checkpoints"]
        if len(points)>100:
            self.timeline_controls.pack(anchor="w",pady=8,before=canvas)
            self.older_button.configure(state="normal" if len(points)>self.timeline_offset+100 else "disabled")
            self.newer_button.configure(state="normal" if self.timeline_offset else "disabled")
        else:
            self.timeline_controls.pack_forget()
        if not points:
            canvas.configure(height=100)
            canvas.create_line(24,50,max(60,canvas.winfo_width()-24),50,fill=self.soft,width=3)
            return
        # A bounded canvas keeps long imported histories responsive.
        end=max(0,len(points)-self.timeline_offset)
        points=points[max(0,end-100):end]
        canvas.configure(height=max(150,len(points)*130))
        canvas.create_line(30,26,30,len(points)*130-40,fill=self.accent,width=3)
        for index,point in enumerate(points):
            y=index*130+26
            canvas.create_oval(22,y-8,38,y+8,fill=self.accent,outline=self.paper,width=3)
            state=point["state"]
            canvas.create_text(58,y-4,anchor="w",text=display_date(point["date"]),fill=self.muted,font=(self.font_family,12))
            note=self.t(point["note"]) if point["note"] in self.translator.text else point["note"]
            summary=note+" · "+self.t("level")+" "+str(sum(state["stats_current"].values())-79)
            tag="event_"+point["id"]
            canvas.create_text(58,y+28,anchor="w",text=summary,width=750,fill=self.ink,font=(self.font_family,16),tags=tag)
            canvas.create_text(58,y+60,anchor="w",text=self.t("view_checkpoint")+" →",fill=self.accent,font=(self.font_family,12),tags=tag)
            canvas.tag_bind(tag,"<Button-1>",lambda _,p=point:self.checkpoint_detail(p))

    def profile_form(self,creating):
        window=self.popup(self.t("new_character" if creating else "rename_profile"),"700x350")
        self.modal(window)
        form=self.card(window)
        form.pack(fill="x",padx=20,pady=20)
        name=self.entry(form,"character_name","" if creating else self.data["character_name"],0,width=320)
        classes=self.option(form,"starting_class",tuple(CLASS_DATA),self.data["class_name"],None,1) if creating else None
        def accept():
            if not name.get().strip():
                raise ValueError(self.t("character_name"))
            self.commit_current()
            self.profiles.sync(self.data)
            if creating:
                state=self.profiles.create(name.get(),name.get(),classes._enum_current,self.data)
                window.destroy()
                self.activate_profile(state)
            else:
                self.data.update(character_name=name.get().strip(),journey_name=name.get().strip())
                window.destroy()
                self.profiles.sync(self.data)
                self.show("journal",refresh=True)
                self.layout_style()
                self.autosave()
        self.button(window,"done",accept).pack(pady=12)
        return window

    def event_dialog(self):
        window=self.popup(self.t("add_event"),"720x390")
        form=self.card(window)
        form.pack(fill="x",padx=20,pady=20)
        date=self.entry(form,"date_simple",datetime.now().strftime("%d/%m/%Y %H:%M"),0,width=280)
        note=self.entry(form,"checkpoint_note","",1,width=340)
        def current():
            point=self.profiles.checkpoint(self.data,note.get(),date.get())
            self.autosave()
            window.destroy()
            self.draw_timeline()
            self.animate_event(point["id"])
        self.button(window,"current_event",current).pack(pady=8)
        self.button(window,"custom_event",lambda:self.custom_event(window,note.get(),date.get()),True).pack(pady=8)
        window.event_date=date
        window.event_note=note
        window.save_current=current
        return window

    def custom_event(self,parent,note,date):
        timestamp(date)
        parent.destroy()
        snapshot=deepcopy(self.data)
        window=self.popup(self.t("custom_event"),"870x790")
        scroll=ctk.CTkScrollableFrame(window,fg_color=self.bg)
        scroll.pack(fill="both",expand=True,padx=20,pady=15)
        self.label(scroll,self.data["character_name"]+" · "+self.t(self.data["class_name"]),22).pack(anchor="w",pady=12)
        form=self.card(scroll)
        form.pack(fill="x")
        level=self.label(form,"")
        level.grid(row=0,column=0,columnspan=2,pady=14)
        variables={}
        def update(*_):
            try:
                values={key:integer(v.get(),key,CLASS_DATA[snapshot["class_name"]]["stats"][key],99) for key,v in variables.items()}
                if len(values)==8:
                    level.configure(text=self.t("level")+": "+str(sum(values.values())-79))
            except ValueError:
                pass
        for row,key in enumerate(ATTRIBUTES,1):
            variables[key]=self.entry(form,key,snapshot["stats_current"][key],row)
            variables[key].trace_add("write",update)
        update()
        weapons=self.card(scroll)
        weapons.pack(fill="x",pady=12)
        names={self.translator.weapon(name):name for name in self.db.weapons}
        search=tk.StringVar()
        ctk.CTkEntry(weapons,textvariable=search,placeholder_text=self.t("search"),font=self.font(),width=360).pack(padx=18,pady=12)
        choice=ctk.CTkOptionMenu(weapons,values=list(names),width=360,font=self.font(),fg_color=self.soft,button_color=self.accent,text_color=self.ink)
        choice.pack(padx=18,pady=12)
        mode=ctk.CTkSegmentedButton(weapons,values=[self.t("weapon_acquired"),self.t("weapon_upgraded")],font=self.font())
        mode.set(self.t("weapon_acquired"))
        mode.pack(padx=18,pady=12)
        def filter_names(*_):
            query=search.get().casefold()
            matches=[label for label,name in names.items() if query in label.casefold() or query in name.casefold()]
            choice.configure(values=matches or [""])
            if choice.get() not in matches:
                choice.set(matches[0] if matches else "")
        search.trace_add("write",filter_names)
        edit=self.card(scroll)
        edit.pack(fill="x")
        upgrade=self.entry(edit,"current_upgrade",0,0)
        quantity=self.entry(edit,"copies",1,1)
        summary=ctk.CTkTextbox(scroll,height=145,wrap="word",font=self.font(),fg_color=self.paper,text_color=self.ink)
        summary.pack(fill="x",pady=14)
        def show_owned():
            summary.configure(state="normal")
            summary.delete("1.0","end")
            summary.insert("1.0","\n".join(self.translator.weapon(i["name"])+f' +{i["current"]} ×{i["quantity"]}' for i in snapshot["inventory_weapons"]))
            summary.configure(state="disabled")
        show_owned()
        def add():
            if choice.get() not in names:
                raise ValueError(self.t("choose_weapons"))
            name=names[choice.get()]
            value=integer(upgrade.get(),"Upgrade",0,self.db.weapons[name].maximum)
            copies=integer(quantity.get(),"Copies",1,999)
            owned=snapshot["inventory_weapons"]
            if mode.get()==self.t("weapon_upgraded"):
                remaining=copies
                for item in sorted(owned,key=lambda i:i["current"]):
                    if item["name"]==name and item["current"]<value:
                        count=min(remaining,item["quantity"])
                        item["quantity"]-=count
                        remaining-=count
                owned[:]=[i for i in owned if i["quantity"]>0]
            existing=next((i for i in owned if i["name"]==name and i["current"]==value),None)
            if existing:
                existing["quantity"]+=copies
            else:
                owned.append({"name":name,"current":value,"quantity":copies})
            show_owned()
        self.button(scroll,"add_weapon",add,True).pack(pady=8)
        def save():
            snapshot["stats_current"]={key:integer(v.get(),key,CLASS_DATA[snapshot["class_name"]]["stats"][key],99) for key,v in variables.items()}
            snapshot["stats_target"]={key:max(value,snapshot["stats_target"][key]) for key,value in snapshot["stats_current"].items()}
            old=self.profiles.active["checkpoints"][-1]["state"] if self.profiles.active["checkpoints"] else self.data
            point=self.profiles.checkpoint(snapshot,note,date)
            next(p for p in self.profiles.active["checkpoints"] if p["id"]==point["id"])["changes"]=differences(old,snapshot)
            self.autosave()
            window.destroy()
            self.draw_timeline()
            self.animate_event(point["id"])
        self.button(window,"checkpoint",save).pack(pady=14)
        window.stat_vars=variables
        window.weapon_choice=choice
        window.weapon_mode=mode
        window.weapon_upgrade=upgrade
        window.weapon_copies=quantity
        window.add_weapon=add
        window.save_event=save
        self.normalize_surfaces(window)
        return window

    def animate_event(self,ident):
        canvas=getattr(self,"timeline",None)
        if canvas is None or not canvas.winfo_exists() or self.data["style"]=="xp":
            return
        tag="event_"+ident
        def frame(step=0):
            if not canvas.winfo_exists():
                return
            mix=step/6
            start=bytes.fromhex(self.bg[1:])
            end=bytes.fromhex(self.ink[1:])
            color="#"+"".join(f"{int(a+(b-a)*mix):02x}" for a,b in zip(start,end))
            canvas.itemconfigure(tag,fill=color)
            if step<6:
                canvas.after(45,lambda:frame(step+1))
        frame()

    def save_checkpoint(self):
        # Retained as a programmatic shortcut for existing integrations.
        self.profiles.checkpoint(self.data)
        self.autosave()
        self.draw_timeline()

    def import_dialog(self):
        window=self.popup(self.t("import_save"),"800x430")
        self.label(window,self.t("save_hint"),wraplength=740,justify="left").pack(padx=24,pady=20)
        self.label(window,self.t("import_unverified"),muted=True,wraplength=740,justify="left").pack(padx=24,pady=12)
        status=self.label(window,"")
        status.pack(pady=8)
        self.modal(window)
        def choose_folder():
            folder=filedialog.askdirectory(parent=window,title=self.t("game_folder"))
            if folder:
                status.configure(text=folder)
                # Executable installation and roaming save are separate locations.
                paths=discover(folder)
                if len(paths)==1:
                    self.begin_import(paths[0],window,status,policy=None)
                elif paths:
                    self.begin_import(paths,window,status,policy=None)
                else:
                    choose_save()
        def choose_save():
            files=discover()
            path=filedialog.askopenfilename(parent=window,title=self.t("select_save"),
                 initialdir=str(files[0].parent) if files else None,filetypes=[("PC save","*.sl2 *.co2")])
            if path:
                self.begin_import(path,window,status,policy=None)
        self.button(window,"import_folder",choose_folder,True).pack(pady=8)
        self.button(window,"select_save",choose_save).pack(pady=8)

    def begin_import(self,path,window=None,status=None,policy="keep"):
        if policy is None:
            manual=any(p["state"]["profile_created"] and not p["state"]["save_link"] for p in self.profiles.data["profiles"].values())
            if manual:
                return self.ask_import_policy(path,window,status)
            policy="keep"
        if getattr(self,"import_in_progress",False):
            return
        if status:
            status.configure(text=self.t("importing"))
        if not hasattr(self,"reader_pool"):
            self.reader_pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix="save-reader")
        self.commit_current()
        self.profiles.sync(self.data)
        previous_link=deepcopy(self.data["save_link"])
        previous_page=self.page
        self.import_in_progress=True
        paths=[Path(p).resolve() for p in path] if isinstance(path,(tuple,list)) else [Path(path).resolve()]
        self.import_future=self.reader_pool.submit(read_saves,paths,self.db)
        def poll():
            if self._closing:
                return
            if window is not None and not window.winfo_exists():
                self.import_in_progress=False
                return
            if not self.import_future.done():
                self.after(80,poll)
                return
            def finish():
                characters=self.import_future.result()
                ids=import_characters(self.profiles,characters,self.data,replace_manual=policy=="replace")
                selected=next((ident for ident in ids
                    if self.profiles.data["profiles"][ident]["state"]["save_link"].get("path")==previous_link.get("path")
                    and self.profiles.data["profiles"][ident]["state"]["save_link"].get("slot")==previous_link.get("slot")),ids[0])
                state=self.profiles.select(selected)
                if window and window.winfo_exists():
                    window.destroy()
                self.page=previous_page if previous_link.get("path") in [str(p) for p in paths] else "journal"
                self.activate_profile(state)
                if not previous_link:
                    self.show_profile_picker()
            self.action(finish)
            self.import_in_progress=False
        self.after(80,poll)

    def refresh_import(self):
        link=self.data["save_link"]
        if link:
            self.begin_import(link["path"])

    def save_farm_spot(self):
        self.read_farm()
        window=self.popup(self.t("save_spot"),"650x270")
        form=self.card(window)
        form.pack(fill="x",padx=20,pady=20)
        name=self.entry(form,"spot_name","",0,width=300)
        def accept():
            if not name.get().strip():
                raise ValueError(self.t("spot_name"))
            spot={"name":name.get().strip(),"farm":deepcopy(self.data["farm"])}
            self.data["farm_spots"]=[s for s in self.data["farm_spots"] if s["name"]!=spot["name"]]+[spot]
            window.destroy()
            self.spot_option.configure(values=[self.t("new_measurement")]+[s["name"] for s in self.data["farm_spots"]])
            self.spot_option.set(spot["name"])
            self.autosave()
        self.button(window,"done",accept).pack(pady=12)
        window.spot_name=name
        window.save_spot=accept
        return window

    def goal_farm_summary(self,parent,goal):
        """Reuse a recorded farm rate without rebuilding another calculator."""
        frame=ctk.CTkFrame(parent,fg_color="transparent")
        frame.pack(fill="x",pady=12)
        option=ctk.CTkOptionMenu(frame,values=[self.t("new_measurement")]+[s["name"] for s in self.data["farm_spots"]],
            font=self.font(),fg_color=self.soft,button_color=self.accent,text_color=self.ink,width=230)
        option.pack(side="left",padx=(0,16))
        label=self.label(frame,"",muted=True,wraplength=650)
        label.pack(side="left")
        if not hasattr(self,"goal_spot_options"):
            self.goal_spot_options={}
        self.goal_spot_options[goal]=option
        def update(name=None):
            if not label.winfo_exists():
                return
            spot=next((s for s in self.data["farm_spots"] if s["name"]==name),None)
            if spot:
                self.data["farm"]=deepcopy(spot["farm"])
                # Only the farm page needs refreshed input fields on its next visit.
                self.farm_spot_dirty=True
                self.autosave()
            cost=self.planner.weapons()["deficit"] if goal=="weapons" else max(0,self.planner.character()["cost"]-self.data["runes"])
            rate=self.planner.farm_rates()["measured"]*self.data["farm"]["efficiency"]/100
            duration=int(-(-(cost*60)//rate)) if rate>0 else None
            label.configure(text=self.t("time_needed")+": "+(self.translator.duration(duration) if duration is not None else self.t("new_measurement")))
        option.configure(command=lambda name:self.action(lambda:update(name)))
        update()
        return update

    def refresh_goal_spots(self):
        values=[self.t("new_measurement")]+[s["name"] for s in self.data["farm_spots"]]
        options=list(getattr(self,"goal_spot_options",{}).values())
        if "farm" in self.views and hasattr(self,"spot_option"):
            options.append(self.spot_option)
        for option in options:
            if option.winfo_exists():
                option.configure(values=values)
                match=next((s["name"] for s in self.data["farm_spots"] if s["farm"]==self.data["farm"]),None)
                option.set(match or self.t("new_measurement"))

    def select_farm_spot(self,name):
        spot=next((s for s in self.data["farm_spots"] if s["name"]==name),None)
        if spot:
            self.data["farm"]=deepcopy(spot["farm"])
            self.show("farm",refresh=True)
            self.spot_option.set(name)

    def compact_mode(self):
        return self.compact_dashboard()

    def release_compact_pages(self):
        # Keep the active timer page; release other cached native drawing resources.
        for page,record in tuple(self.views.items()):
            if page!=self.page:
                cancel_widget_jobs(record["frame"])
                record["frame"].destroy()
                del self.views[page]
                self.wallet_vars.pop(page,None)
        if getattr(self,"background_job",None):
            self.after_cancel(self.background_job)
            self.background_job=None
        for layer in getattr(self,"background_layers",[]):
            if layer.winfo_exists():
                layer.destroy()
        self.background_layers=[]
        for widget,_ in getattr(self,"background_text",[]):
            if widget.winfo_exists():
                widget._label.configure(image="")
        self.background_text=[]

