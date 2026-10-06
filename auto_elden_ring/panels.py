"""Owned in-window navigation panels; only the compact companion is native."""

import customtkinter as ctk
from .windows import cancel_widget_jobs


class Panel(ctk.CTkFrame):
    def __init__(self, app, title):
        self.app = app
        self.shell = ctk.CTkFrame(app.host, fg_color=app.bg, corner_radius=0)
        self.shell._surface_role = "bg"
        heading = ctk.CTkFrame(self.shell, fg_color="transparent")
        self.heading = heading
        heading.pack(fill="x", pady=(0, 12))
        self.back = app.button(heading, "back", self.leave, True)
        self.back.pack(side="left", padx=12, pady=10)
        app.label(heading, title, 23).pack(side="left", padx=18)
        super().__init__(self.shell, fg_color=app.bg, corner_radius=0)
        self._surface_role = "bg"
        self.pack(fill="both", expand=True)
        self.close_command = self.destroy

    def present(self):
        # Construct off screen, then reveal the completed panel in one step.
        self.shell.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.shell.lift()

    def leave(self):
        self.close_command()

    def protocol(self, name, command):
        if name == "WM_DELETE_WINDOW":
            self.close_command = command

    def lift(self, aboveThis=None):
        self.present()

    def destroy(self):
        if not self.winfo_exists():
            return
        cancel_widget_jobs(self.shell)
        self.app.popups.discard(self)
        super().destroy()
        self.shell.destroy()

    def grab_set(self):
        # No native grab: navigation panels share the main application window.
        pass

    def grab_release(self):
        pass
