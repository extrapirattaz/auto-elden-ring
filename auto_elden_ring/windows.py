"""Small Windows helpers; never remove caption styles or synthesize move loops."""

import ctypes
import os
from contextlib import contextmanager
from .core import resource_path

_fonts_loaded = False


@contextmanager
def presentation_transaction(window):
    """Apply retained-widget changes in one Tk transaction, then flush layout.

    Do not send WM_SETREDRAW to the top-level HWND: Windows removes WS_VISIBLE
    during that call, which makes appearance changes look like a window restart.
    No native visibility, mapping, identity or window-manager state is changed.
    """
    depth = getattr(window, "_presentation_depth", 0)
    window._presentation_depth = depth + 1
    try:
        yield
    finally:
        window._presentation_depth = depth
        if not depth and window.winfo_exists():
            window.update_idletasks()


def load_reading_font():
    global _fonts_loaded
    if os.name == "nt" and not _fonts_loaded:
        api = ctypes.windll.gdi32.AddFontResourceExW
        api.argtypes = [ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
        for name in ("OpenDyslexic-Regular.otf", "OpenDyslexic-Bold.otf"):
            api(str(resource_path("assets/fonts/" + name)), 0x10, None)
        _fonts_loaded = True


def caption_color(window, bg, ink):
    if os.name != "nt":
        return
    user32 = ctypes.windll.user32
    user32.GetParent.argtypes = [ctypes.c_void_p]
    user32.GetParent.restype = ctypes.c_void_p
    hwnd = user32.GetParent(window.winfo_id())
    dwm = ctypes.windll.dwmapi
    dwm.DwmSetWindowAttribute.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_uint,
    ]
    for attribute, value in ((35, bg), (36, ink), (34, bg)):
        r, g, b = bytes.fromhex(value[1:])
        packed = ctypes.c_uint(r | (g << 8) | (b << 16))
        dwm.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(packed), 4)


def cancel_widget_jobs(widget):
    """Cancel callbacks owned by a widget subtree, preserving other windows."""
    commands = set()

    def visit(current):
        commands.update(getattr(current, "_tclCommands", None) or ())
        for child in current.winfo_children():
            visit(child)

    visit(widget)
    for job in widget.tk.splitlist(widget.tk.call("after", "info")):
        info = widget.tk.call("after", "info", job)
        script = widget.tk.splitlist(info[0])
        if script and script[0] in commands:
            # Cancel scheduling only; the owning widget deletes its Tcl command.
            # Calling another widget's after_cancel deletes the command twice.
            widget.tk.call("after", "cancel", job)


def set_text(widget, text):
    """Configure a label or button only when its text actually changes."""
    if widget.cget("text") != text:
        widget.configure(text=text)


def monitor_workarea(widget):
    """Return the current monitor's usable rectangle, including negative origins."""
    if os.name != "nt":
        return (0, 0, widget.winfo_screenwidth(), widget.winfo_screenheight())
    from ctypes import wintypes

    class MonitorInfo(ctypes.Structure):
        _fields_ = [
            ("size", wintypes.DWORD),
            ("monitor", wintypes.RECT),
            ("work", wintypes.RECT),
            ("flags", wintypes.DWORD),
        ]

    user = ctypes.windll.user32
    user.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
    user.MonitorFromWindow.restype = wintypes.HANDLE
    info = MonitorInfo()
    info.size = ctypes.sizeof(info)
    user.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MonitorInfo)]
    if not user.GetMonitorInfoW(user.MonitorFromWindow(widget.winfo_id(), 2), ctypes.byref(info)):
        return (0, 0, widget.winfo_screenwidth(), widget.winfo_screenheight())
    return (info.work.left, info.work.top, info.work.right, info.work.bottom)


def snap_position(x, y, width, height, area, threshold=28):
    left, top, right, bottom = area
    x = min(max(left, x), max(left, right - width))
    y = min(max(top, y), max(top, bottom - height))
    for edge in (left, right - width):
        if abs(x - edge) <= threshold:
            x = edge
    for edge in (top, bottom - height):
        if abs(y - edge) <= threshold:
            y = edge
    return x, y


def position_window(window, x, y):
    if os.name == "nt":
        user = ctypes.windll.user32
        user.GetParent.argtypes = [ctypes.c_void_p]
        user.GetParent.restype = ctypes.c_void_p
        user.SetWindowPos.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint,
        ]
        user.SetWindowPos(user.GetParent(window.winfo_id()), None, x, y, 0, 0, 0x15)
    else:
        window.geometry(f"{x:+d}{y:+d}")
