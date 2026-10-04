"""Small Windows helpers; never remove caption styles or synthesize move loops."""
import ctypes
import os
from contextlib import contextmanager
from .core import resource_path

_fonts_loaded=False


@contextmanager
def suspend_redraw(window):
    """Batch presentation changes without hiding or recreating the window."""
    if os.name!="nt" or not window.winfo_viewable():
        yield
        return
    user=ctypes.windll.user32
    user.GetParent.argtypes=[ctypes.c_void_p]
    user.GetParent.restype=ctypes.c_void_p
    hwnd=user.GetParent(window.winfo_id())
    user.SendMessageW.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_size_t,ctypes.c_ssize_t]
    user.SendMessageW(hwnd,0xB,0,0)
    try:
        yield
        window.update_idletasks()
    finally:
        user.SendMessageW(hwnd,0xB,1,0)
        user.RedrawWindow.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint]
        user.RedrawWindow(hwnd,None,None,0x185)


def load_reading_font():
    global _fonts_loaded
    if os.name=="nt" and not _fonts_loaded:
        api=ctypes.windll.gdi32.AddFontResourceExW
        api.argtypes=[ctypes.c_wchar_p,ctypes.c_uint,ctypes.c_void_p]
        for name in ("OpenDyslexic-Regular.otf","OpenDyslexic-Bold.otf"):
            api(str(resource_path("assets/fonts/"+name)),0x10,None)
        _fonts_loaded=True


def caption_color(window,bg,ink):
    if os.name!="nt":
        return
    user32=ctypes.windll.user32
    user32.GetParent.argtypes=[ctypes.c_void_p]
    user32.GetParent.restype=ctypes.c_void_p
    hwnd=user32.GetParent(window.winfo_id())
    dwm=ctypes.windll.dwmapi
    dwm.DwmSetWindowAttribute.argtypes=[ctypes.c_void_p,ctypes.c_uint,ctypes.c_void_p,ctypes.c_uint]
    for attribute,value in ((35,bg),(36,ink),(34,bg)):
        r,g,b=bytes.fromhex(value[1:])
        packed=ctypes.c_uint(r|(g<<8)|(b<<16))
        dwm.DwmSetWindowAttribute(hwnd,attribute,ctypes.byref(packed),4)


def cancel_widget_jobs(widget):
    """Cancel callbacks owned by a widget subtree, preserving other windows."""
    commands=set()
    def visit(current):
        commands.update(getattr(current,"_tclCommands",None) or ())
        for child in current.winfo_children():
            visit(child)
    visit(widget)
    for job in widget.tk.splitlist(widget.tk.call("after","info")):
        info=widget.tk.call("after","info",job)
        script=widget.tk.splitlist(info[0])
        if script and script[0] in commands:
            # Cancel scheduling only; the owning widget deletes its Tcl command.
            # Calling another widget's after_cancel deletes the command twice.
            widget.tk.call("after","cancel",job)
