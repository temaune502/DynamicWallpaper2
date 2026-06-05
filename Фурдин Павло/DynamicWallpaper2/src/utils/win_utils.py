import ctypes
from ctypes import wintypes
from typing import Optional

user32 = ctypes.windll.user32
dwmapi = ctypes.windll.dwmapi

DWMWA_EXTENDED_FRAME_BOUNDS = 9
DWMWA_CLOAKED = 14


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


def is_window_cloaked(hwnd: int) -> bool:
    cloaked = wintypes.DWORD()
    res = dwmapi.DwmGetWindowAttribute(
        ctypes.c_void_p(hwnd), DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked)
    )
    return (res == 0) and bool(cloaked.value)


def get_window_bounds(hwnd: int) -> wintypes.RECT:
    rect = wintypes.RECT()
    # Try DWM extended bounds for more accurate window frame
    res = dwmapi.DwmGetWindowAttribute(
        ctypes.c_void_p(hwnd), DWMWA_EXTENDED_FRAME_BOUNDS, ctypes.byref(rect), ctypes.sizeof(rect)
    )
    if res != 0:
        user32.GetWindowRect(ctypes.c_void_p(hwnd), ctypes.byref(rect))
    return rect


def get_monitor_rects(hwnd: int) -> tuple[wintypes.RECT, wintypes.RECT]:
    hmon = user32.MonitorFromWindow(ctypes.c_void_p(hwnd), 2)  # MONITOR_DEFAULTTONEAREST
    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(MONITORINFO)
    user32.GetMonitorInfoW(ctypes.c_void_p(hmon), ctypes.byref(mi))
    return mi.rcMonitor, mi.rcWork


def _spawn_workerw() -> None:
    progman = user32.FindWindowW("Progman", None)
    if progman:
        result = ctypes.c_ulong()
        user32.SendMessageTimeoutW(progman, 0x052C, 0, 0, 0, 1000, ctypes.byref(result))


def _get_workerw() -> Optional[int]:
    _spawn_workerw()
    workerw_holder = ctypes.c_void_p(None)

    EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def _enum_windows(hwnd, lparam):  # type: ignore[override]
        shell = user32.FindWindowExW(hwnd, 0, "SHELLDLL_DefView", 0)
        if shell:
            h_workerw = user32.FindWindowExW(0, hwnd, "WorkerW", 0)
            if h_workerw:
                workerw_holder.value = h_workerw
                return False
        return True

    user32.EnumWindows(EnumProc(_enum_windows), 0)

    if workerw_holder.value:
        return int(workerw_holder.value)

    fallback = user32.FindWindowExW(0, 0, "WorkerW", 0)
    return int(fallback) if fallback else None


def attach_to_workerw(qt_hwnd: int) -> bool:
    workerw = _get_workerw()
    if not workerw:
        return False
    res = user32.SetParent(ctypes.c_void_p(qt_hwnd), ctypes.c_void_p(workerw))
    return bool(res)


def is_occluded(my_hwnd: int, use_work_area: bool = True, tolerance: int = 4) -> bool:
    occluded = False
    rc_mon, rc_work = get_monitor_rects(my_hwnd)
    target_rect = rc_work if use_work_area else rc_mon

    def covers(r1: wintypes.RECT, r2: wintypes.RECT, t: int = tolerance) -> bool:
        return (
            abs(r1.left - r2.left) <= t
            and abs(r1.top - r2.top) <= t
            and abs(r1.right - r2.right) <= t
            and abs(r1.bottom - r2.bottom) <= t
        )

    def enum_proc(hwnd, lparam):
        nonlocal occluded

        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(ctypes.c_void_p(hwnd), cls_buf, 256)
        cls = cls_buf.value
        if cls in ("Progman", "WorkerW"):
            return True

        if (
            not user32.IsWindowVisible(ctypes.c_void_p(hwnd))
            or user32.IsIconic(ctypes.c_void_p(hwnd))
            or is_window_cloaked(hwnd)
        ):
            return True

        rc_wmon, _ = get_monitor_rects(hwnd)
        if not covers(rc_wmon, rc_mon, 100):
            return True

        wb = get_window_bounds(hwnd)
        if covers(wb, target_rect) or bool(user32.IsZoomed(ctypes.c_void_p(hwnd))):
            occluded = True
            return False

        return True

    EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(EnumProc(enum_proc), 0)
    return occluded