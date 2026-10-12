# /dev/uinput button + key injection. Works on KMS, sway, weston, Xwayland.

import ctypes
import fcntl
import os
import struct
import time

UINPUT_PATH = "/dev/uinput"

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502

EV_SYN = 0x00
EV_KEY = 0x01
SYN_REPORT = 0x00

BUS_USB = 0x03

# Subset of linux/input-event-codes.h used by SDL gamepads.
KEY_CODES = {
    # gamepad
    "south": 0x130, "east": 0x131, "north": 0x133, "west": 0x134,
    "tl": 0x136, "tr": 0x137, "tl2": 0x138, "tr2": 0x139,
    "select": 0x13a, "start": 0x13b, "mode": 0x13c,
    "thumbl": 0x13d, "thumbr": 0x13e,
    "dpad_up": 0x220, "dpad_down": 0x221, "dpad_left": 0x222, "dpad_right": 0x223,
    # keyboard (subset)
    "esc": 1, "enter": 28, "space": 57,
    "up": 103, "down": 108, "left": 105, "right": 106,
    "f1": 59, "f2": 60, "f3": 61, "f4": 62,
}


class UinputError(Exception):
    pass


class _UinputUserDev(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char * 80),
        ("id_bustype", ctypes.c_uint16),
        ("id_vendor", ctypes.c_uint16),
        ("id_product", ctypes.c_uint16),
        ("id_version", ctypes.c_uint16),
        ("ff_effects_max", ctypes.c_uint32),
        ("absmax", ctypes.c_int32 * 64),
        ("absmin", ctypes.c_int32 * 64),
        ("absfuzz", ctypes.c_int32 * 64),
        ("absflat", ctypes.c_int32 * 64),
    ]


def _open_device(name: str = "reglinux-test-uinput"):
    try:
        fd = os.open(UINPUT_PATH, os.O_WRONLY | os.O_NONBLOCK)
    except OSError as e:
        raise UinputError(f"open {UINPUT_PATH}: {e}") from e

    fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
    fcntl.ioctl(fd, UI_SET_EVBIT, EV_SYN)
    for code in set(KEY_CODES.values()):
        fcntl.ioctl(fd, UI_SET_KEYBIT, code)

    dev = _UinputUserDev()
    dev.name = name.encode("ascii")[:79]
    dev.id_bustype = BUS_USB
    dev.id_vendor = 0x1234
    dev.id_product = 0x5678
    dev.id_version = 1
    os.write(fd, bytes(dev))
    fcntl.ioctl(fd, UI_DEV_CREATE)
    time.sleep(0.2)  # let userspace bind
    return fd


def _emit(fd, type_, code, value):
    # struct input_event: timeval{sec,usec} u16 type, u16 code, s32 value
    pkt = struct.pack("llHHi", 0, 0, type_, code, value)
    os.write(fd, pkt)


def _close(fd):
    try:
        fcntl.ioctl(fd, UI_DEV_DESTROY)
    finally:
        os.close(fd)


def press(name: str, hold_ms: int = 60):
    code = KEY_CODES.get(name)
    if code is None:
        raise UinputError(f"unknown key: {name}")
    fd = _open_device()
    try:
        _emit(fd, EV_KEY, code, 1)
        _emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(hold_ms / 1000.0)
        _emit(fd, EV_KEY, code, 0)
        _emit(fd, EV_SYN, SYN_REPORT, 0)
    finally:
        time.sleep(0.05)
        _close(fd)


def chord(names: list[str], hold_ms: int = 60):
    fd = _open_device()
    try:
        codes = []
        for n in names:
            c = KEY_CODES.get(n)
            if c is None:
                raise UinputError(f"unknown key: {n}")
            codes.append(c)
        for c in codes:
            _emit(fd, EV_KEY, c, 1)
        _emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(hold_ms / 1000.0)
        for c in reversed(codes):
            _emit(fd, EV_KEY, c, 0)
        _emit(fd, EV_SYN, SYN_REPORT, 0)
    finally:
        time.sleep(0.05)
        _close(fd)
