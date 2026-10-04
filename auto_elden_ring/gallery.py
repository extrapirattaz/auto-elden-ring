"""Virtualized catalogue: one canvas, visible cards only, bounded image cache."""
from collections import OrderedDict
import math
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from .core import resource_path


class Gallery(tk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent,bg=app.bg)
        self.app=app
        self.query=""
        self.layout=[]
        self.hitboxes=[]
        self.cache=OrderedDict()
        self.max_cache=64
        self.job=None
        self.canvas=tk.Canvas(self,bg=app.bg,highlightthickness=0,bd=0)
        self.scrollbar=ctk.CTkScrollbar(self,orientation="vertical",command=self.scroll,
            fg_color=app.bg,bg_color=app.bg,button_color=app.soft,button_hover_color=app.accent,
            corner_radius=app.style_spec["button_radius"],width=12)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right",fill="y")
        self.canvas.pack(fill="both",expand=True)
        self.canvas.bind("<Configure>",lambda _:self.reflow())
        self.canvas.bind("<MouseWheel>",self.wheel)
        self.canvas.bind("<Button-1>",self.click)
        self.reflow()

    def filter(self,query):
        self.query=query.casefold()
        self.canvas.yview_moveto(0)
        self.reflow()

    def reflow(self):
        self.configure(bg=self.app.bg)
        self.canvas.configure(bg=self.app.bg)
        self.scrollbar.configure(fg_color=self.app.bg,bg_color=self.app.bg,
            button_color=self.app.soft,button_hover_color=self.app.accent,
            corner_radius=self.app.style_spec["button_radius"],width=18 if self.app.data["style"]=="xp" else 12)
        width=max(340,self.canvas.winfo_width())
        columns=max(1,width//190)
        card_width=width/columns
        y=12
        self.layout=[]
        grouped={}
        for name,w in self.app.db.weapons.items():
            if self.query in name.casefold() or self.query in self.app.translator.weapon(name).casefold():
                grouped.setdefault(w.category,[]).append(name)
        for category,names in grouped.items():
            self.layout.append(("heading",category,12,y,width,36))
            y+=46
            for index,name in enumerate(names):
                self.layout.append(("card",name,(index%columns)*card_width+6,y+(index//columns)*225,card_width-12,215))
            y+=math.ceil(len(names)/columns)*225+14
        self.canvas.configure(scrollregion=(0,0,width,max(y,self.canvas.winfo_height())))
        self.schedule()

    def schedule(self):
        if self.job is None:
            self.job=self.after_idle(self.draw)

    def scroll(self,*args):
        self.canvas.yview(*args)
        self.schedule()

    def wheel(self,event):
        self.canvas.yview_scroll(-int(event.delta/120)*3,"units")
        self.schedule()
        return "break"

    def thumbnail(self,name):
        if name in self.cache:
            self.cache.move_to_end(name)
            return self.cache[name]
        weapon=self.app.db.weapons[name]
        entry=self.app.db.raw["weapons_by_category"][weapon.category][name]
        path=resource_path(f'assets/catalogue/{entry["id"]}.webp')
        if not path.exists():
            path=resource_path(f'assets/catalogue/{entry["id"]}.png')
        with Image.open(path) as source:
            image=source.convert("RGBA")
            image.thumbnail((100,100),Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(image,master=self.canvas)
        self.cache[name]=photo
        while len(self.cache)>self.max_cache:
            self.cache.popitem(last=False)
        return photo

    def draw(self):
        self.job=None
        if not self.winfo_exists():
            return
        canvas=self.canvas
        top=canvas.canvasy(0)-210
        bottom=top+canvas.winfo_height()+420
        canvas.delete("all")
        self.hitboxes=[]
        self.ownership_badges={}
        selected={i["name"] for i in self.app.data["selected"]}
        self.visible_photos=[]
        family=self.app.font_family
        for kind,name,x,y,w,h in self.layout:
            if y+h<top or y>bottom:
                continue
            if kind=="heading":
                canvas.create_text(x,y,anchor="nw",text=self.app.t(name),fill=self.app.ink,font=(family,20))
                continue
            weapon=self.app.db.weapons[name]
            on=name in selected
            radius=self.app.style_spec["radius"]
            if radius:
                points=(x+radius,y,x+w-radius,y,x+w,y,x+w,y+radius,x+w,y+h-radius,x+w,y+h,x+w-radius,y+h,x+radius,y+h,x,y+h,x,y+h-radius,x,y+radius,x,y)
                canvas.create_polygon(points,smooth=True,fill=self.app.soft if on else self.app.paper,outline=self.app.accent if on else self.app.paper,width=2)
            else:
                canvas.create_rectangle(x,y,x+w,y+h,fill=self.app.soft if on else self.app.paper,outline=self.app.accent if on else self.app.muted,width=2 if on else 1)
            canvas.create_text(x+10,y+14,anchor="w",text=self.app.t(weapon.kind),fill=self.app.muted,font=(family,10))
            canvas.create_text(x+w-10,y+14,anchor="e",text=f"+{weapon.maximum}",fill=self.app.muted,font=(family,10))
            photo=self.thumbnail(name)
            self.visible_photos.append(photo)
            canvas.create_image(x+w/2,y+78,image=photo)
            canvas.create_text(x+w/2,y+145,text=self.app.translator.weapon(name),fill=self.app.ink,width=w-16,font=(family,12))
            canvas.create_text(x+w/2,y+174,text=self.app.t("dlc")+": "+self.app.t("yes" if weapon.dlc else "no"),fill=self.app.muted,font=(family,10))
            owned=[i for i in self.app.data["inventory_weapons"] if i["name"]==name]
            status=("✓ "+self.app.t("owned")+"  "+"/".join(f'+{i["current"]} ×{i["quantity"]}' for i in owned)) if owned else self.app.t("not_owned")
            badge=canvas.create_text(x+w/2,y+199,text=status,width=w-16,
                fill="#428DDF" if owned else self.app.muted,font=(family,10,"bold" if owned else "normal"))
            self.ownership_badges[name]=badge
            if on:
                canvas.create_text(x+w-14,y+116,text="✓",fill=self.app.accent,font=(family,18,"bold"))
            self.hitboxes.append((name,x,y,x+w,y+h))

    def click(self,event):
        x,y=self.canvas.canvasx(event.x),self.canvas.canvasy(event.y)
        for name,left,top,right,bottom in self.hitboxes:
            if left<=x<=right and top<=y<=bottom:
                self.app.planner.toggle_weapon(name)
                self.app.autosave()
                self.schedule()
                break

    def destroy(self):
        if self.job:
            self.after_cancel(self.job)
        self.cache.clear()
        self.visible_photos=[]
        super().destroy()
