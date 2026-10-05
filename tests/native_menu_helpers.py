"""Drive only the test process's native popup; never another application's UI."""

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import sys
import time


def interact_native_menu(app, option, index=None):
    """Use a separate driver: Windows menu tracking blocks the calling Tk thread."""
    user = ctypes.windll.user32
    user.GetParent.argtypes = [wintypes.HWND]
    user.GetParent.restype = wintypes.HWND
    user.GetForegroundWindow.restype = wintypes.HWND
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.SetForegroundWindow.argtypes = [wintypes.HWND]
    hwnd = user.GetParent(app.winfo_id())
    user.SetCursorPos(app.winfo_rootx() + 15, app.winfo_rooty() + 20)
    foreground_thread = user.GetWindowThreadProcessId(user.GetForegroundWindow(), None)
    thread = ctypes.windll.kernel32.GetCurrentThreadId()
    attached = user.AttachThreadInput(thread, foreground_thread, True)
    try:
        user.SetForegroundWindow(hwnd)
    finally:
        if attached:
            user.AttachThreadInput(thread, foreground_thread, False)
    driver = subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            str(os.getpid()),
            str(hwnd),
            "escape" if index is None else str(index),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    menu = app.open_native_menu(option)
    output, errors = driver.communicate(timeout=10)
    if driver.returncode:
        raise AssertionError(output + errors)
    app.dismiss_menu()
    app.update()
    return menu


def drive(pid, root, index):
    user = ctypes.windll.user32
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.GetForegroundWindow.restype = wintypes.HWND
    user.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user.SendMessageW.restype = ctypes.c_ssize_t
    user.GetMenuItemRect.argtypes = [
        wintypes.HWND,
        wintypes.HMENU,
        wintypes.UINT,
        ctypes.POINTER(wintypes.RECT),
    ]
    user.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    found = []

    def visit(hwnd, _):
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        name = ctypes.create_unicode_buffer(64)
        user.GetClassNameW(hwnd, name, 64)
        if owner.value == pid and name.value == "#32768":
            found.append(hwnd)
        return True

    end = time.monotonic() + 5
    while not found and time.monotonic() < end:
        user.EnumWindows(callback_type(visit), 0)
        time.sleep(0.03)
    owner = wintypes.DWORD()
    user.GetWindowThreadProcessId(user.GetForegroundWindow(), ctypes.byref(owner))
    if not found or owner.value != pid:
        user.GetWindowThreadProcessId(root, ctypes.byref(owner))
        if owner.value == pid:
            user.PostMessageW(root, 0x0010, 0, 0)
        raise AssertionError("The test does not own a foreground native menu.")
    if index == "escape":
        user.keybd_event(0x1B, 0, 0, 0)
        user.keybd_event(0x1B, 0, 2, 0)
    elif index.startswith("keyboard:"):
        keys = [0x28] * (int(index.split(":")[1]) + 1) + [0x0D]
        for key in keys:
            user.keybd_event(key, 0, 0, 0)
            user.keybd_event(key, 0, 2, 0)
            time.sleep(0.025)
    elif index == "wheel":
        hwnd = found[0]
        rect = wintypes.RECT()
        user.GetWindowRect(hwnd, ctypes.byref(rect))
        user.SetCursorPos((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
        user.mouse_event(0x0800, 0, 0, ctypes.c_ulong(-120).value, 0)
        user.keybd_event(0x1B, 0, 0, 0)
        user.keybd_event(0x1B, 0, 2, 0)
    else:
        hwnd = found[0]
        handle = user.SendMessageW(hwnd, 0x01E1, 0, 0)  # MN_GETHMENU
        rect = wintypes.RECT()
        if not user.GetMenuItemRect(hwnd, handle, int(index), ctypes.byref(rect)):
            raise ctypes.WinError()
        user.SetCursorPos((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
        user.mouse_event(0x0002, 0, 0, 0, 0)
        user.mouse_event(0x0004, 0, 0, 0, 0)


if __name__ == "__main__":
    drive(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
