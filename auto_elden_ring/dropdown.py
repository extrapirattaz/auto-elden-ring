"""Native Tk menus with CTk styling and deferred application callbacks.

The operating system owns selection, keyboard navigation and cancellation.
No imitation list, image, polling timer or extra application window is needed.
"""

import customtkinter as ctk


class NativeOptionMenu(ctk.CTkOptionMenu):
    """Retain the CTk control API while using its original native Tk menu."""

    def _open_dropdown_menu(self):
        if self.cget("state") == "disabled" or not self.cget("values"):
            return
        app = self.winfo_toplevel()
        app.dismiss_menu()
        menu = self._dropdown_menu
        app.scroll_menu = menu
        app.menu_geometry = (app.winfo_x(), app.winfo_y(), app.winfo_width(), app.winfo_height())
        try:
            # Tk performs platform-native tracking, including Escape/outside click.
            menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())
        finally:
            # On Windows the native tracking loop may return before the app's
            # deferred appearance callback. On X11 Tk owns the menu grab.
            if app.grab_current() is menu:
                menu.grab_release()

    def _dropdown_callback(self, value):
        """Close the native menu before changing fonts, language or geometry."""
        app = self.winfo_toplevel()
        app.dismiss_menu()
        command = self._command
        # CTk's setter updates both the visible label and an optional variable.
        self.set(value)
        if command is not None:
            app.after(0, lambda: command(value) if self.winfo_exists() else None)
