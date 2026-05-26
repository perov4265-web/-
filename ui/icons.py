# -*- coding: utf-8 -*-
"""Загрузка PNG-иконок интерфейса с кэшированием.

Иконки лежат в resources/icons/<name>.png (генерируются tools/make_icons.py).
Используется Pillow для масштабирования под нужный размер. PhotoImage
кэшируются по (имя, размер), чтобы Tk не терял ссылки (иначе картинки
исчезают из-за сборки мусора).

Использование:
    from ui.icons import get_icon
    btn = ttk.Button(parent, text="Добавить", image=get_icon("add"),
                     compound="left")
"""
import os
import sys
import tkinter as tk

try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except Exception:
    _PIL_OK = False

# Кэш: (name, size) -> PhotoImage. Хранит ссылки, чтобы не терялись.
_CACHE = {}


def _icons_dir():
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "resources", "icons")


def get_icon(name, size=18):
    """Возвращает PhotoImage иконки name нужного размера или None, если
    иконка/Pillow недоступны (тогда кнопка останется только с текстом)."""
    key = (name, size)
    if key in _CACHE:
        return _CACHE[key]
    if not _PIL_OK:
        return None
    path = os.path.join(_icons_dir(), name + ".png")
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        img = img.resize((size, size), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        _CACHE[key] = photo
        return photo
    except Exception:
        return None
