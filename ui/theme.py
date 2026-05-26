# -*- coding: utf-8 -*-
"""Оформление приложения «Заменитель текста».

Основная тема — Sun Valley (sv-ttk), современный стиль в духе Windows 11.
Если пакет sv-ttk недоступен, используется запасная светлая тема на основе
clam, чтобы приложение всё равно выглядело опрятно.

Точка входа — apply_theme(root). Дополнительно настраиваются именованные
стили (Accent.TButton, H1.TLabel и т.п.), общие для обеих тем.
"""
import tkinter as tk
from tkinter import ttk


# Палитра акцентов (используется для тегов таблиц и подсветок)
COLORS = {
    "bg":            "#f4f6f9",
    "surface":       "#ffffff",
    "surface_alt":   "#eef2f7",
    "border":        "#d6deea",
    "accent":        "#2f6fed",
    "accent_hover":  "#1b4fc0",
    "accent_press":  "#164bb0",
    "accent_soft":   "#e7f0ff",
    "text":          "#1b2733",
    "text_muted":    "#6b7785",
    "text_on_accent":"#ffffff",
    "header_bg":     "#0d2840",
    "header_text":   "#eaf2fb",
    "success":       "#1faa59",
    "warning":       "#f2c037",
    "danger":        "#e1503e",
    "row_warn":      "#fff3e6",
    "row_repl":      "#eef4ff",
    "row_err":       "#fdecea",
}

FONT_FAMILY = "Segoe UI"
FONT_BASE  = (FONT_FAMILY, 10)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_BOLD  = (FONT_FAMILY, 10, "bold")
FONT_H1    = (FONT_FAMILY, 16, "bold")
FONT_H2    = (FONT_FAMILY, 12, "bold")

_SV_ACTIVE = False  # включена ли тема Sun Valley


def is_sun_valley() -> bool:
    return _SV_ACTIVE


def apply_theme(root: tk.Tk) -> ttk.Style:
    """Применяет тему к окну. Возвращает объект Style."""
    global _SV_ACTIVE
    style = ttk.Style(root)

    # Пытаемся включить Sun Valley
    try:
        import sv_ttk
        sv_ttk.set_theme("light")
        _SV_ACTIVE = True
    except Exception:
        _SV_ACTIVE = False
        try:
            style.theme_use("clam")
        except tk.TclError:
            style.theme_use("default")
        _apply_fallback(style, root)

    # Именованные стили поверх любой темы
    _apply_named_styles(style, root)
    return style


def _apply_named_styles(style: ttk.Style, root: tk.Tk):
    """Стили, общие и для Sun Valley, и для запасной темы."""
    c = COLORS
    style.configure("H1.TLabel", font=FONT_H1, foreground=c["accent"])
    style.configure("H2.TLabel", font=FONT_H2, foreground=c["accent"])
    style.configure("Muted.TLabel", font=FONT_SMALL, foreground=c["text_muted"])
    style.configure("Hint.TLabel", font=FONT_SMALL, foreground=c["text_muted"])
    try:
        style.configure("Accent.TButton", font=FONT_BOLD)
    except tk.TclError:
        pass
    style.configure("Card.TFrame", background=c["surface"])


def _apply_fallback(style: ttk.Style, root: tk.Tk):
    """Запасная светлая тема (если sv-ttk не установлен)."""
    c = COLORS
    root.configure(background=c["bg"])
    style.configure(".", background=c["bg"], foreground=c["text"],
                    font=FONT_BASE, borderwidth=0)
    style.configure("TFrame", background=c["bg"])
    style.configure("TLabel", background=c["bg"], foreground=c["text"])
    style.configure("TButton", background=c["surface"], foreground=c["text"],
                    font=FONT_BASE, padding=(12, 7), borderwidth=1, relief="flat",
                    bordercolor=c["border"])
    style.map("TButton",
              background=[("pressed", c["surface_alt"]), ("active", c["accent_soft"])],
              bordercolor=[("active", c["accent"])])
    style.configure("Accent.TButton", background=c["accent"],
                    foreground=c["text_on_accent"], font=FONT_BOLD,
                    padding=(14, 8), borderwidth=0, relief="flat")
    style.map("Accent.TButton",
              background=[("pressed", c["accent_press"]), ("active", c["accent_hover"])])
    style.configure("TEntry", fieldbackground=c["surface"], borderwidth=1,
                    relief="flat", padding=5, bordercolor=c["border"])
    style.map("TEntry", bordercolor=[("focus", c["accent"])])
    style.configure("Treeview", background=c["surface"], fieldbackground=c["surface"],
                    foreground=c["text"], rowheight=30, borderwidth=0)
    style.map("Treeview", background=[("selected", c["accent_soft"])],
              foreground=[("selected", c["text"])])
    style.configure("Treeview.Heading", background=c["header_bg"],
                    foreground=c["header_text"], font=FONT_BOLD, padding=(8, 8),
                    relief="flat")
    style.configure("TLabelframe", background=c["bg"], bordercolor=c["border"],
                    borderwidth=1, relief="flat")
    style.configure("TLabelframe.Label", background=c["bg"], foreground=c["accent"],
                    font=FONT_BOLD)
    style.configure("TCheckbutton", background=c["bg"], foreground=c["text"])
    style.configure("TNotebook", background=c["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 9))


def configure_tree_tags(tree: ttk.Treeview):
    """Настраивает теги строк: чередование и подсветки."""
    c = COLORS
    tree.tag_configure("odd", background=c["surface"])
    tree.tag_configure("even", background=c["surface_alt"])
    tree.tag_configure("warn", background=c["row_warn"])
    tree.tag_configure("repl", background=c["row_repl"])
    tree.tag_configure("err", background=c["row_err"])
