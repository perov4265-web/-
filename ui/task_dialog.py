# -*- coding: utf-8 -*-
"""Модальное окно «Задача замены».

Используется для создания новой задачи и редактирования существующей.
Задача описывается словарём:
    {
      "find": str,
      "replace": str,
      "targets": {"word","excel","autocad","pdf","filename","foldername": bool},
      "filename_exts": set[str],   # группы расширений для имён файлов
    }

Окно возвращает результат в self.result (dict) либо None при отмене.
"""
import tkinter as tk
from tkinter import ttk

import text_replacer
from ui.icons import get_icon


# Метки целей (что делать)
TARGET_LABELS = [
    ("word",       "word",     "Word (.docx) — текст в документах"),
    ("excel",      "excel",    "Excel (.xlsx) — текст в ячейках"),
    ("autocad",    "autocad",  "AutoCAD (.dxf / .dwg) — текстовые объекты"),
    ("pdf",        "pdf",      "PDF (.pdf) — текст в документах"),
    ("filename",   "filename", "Имена файлов — переименование"),
    ("foldername", "folder",   "Имена папок — переименование"),
]

# Группы расширений для имён файлов
EXT_LABELS = [
    ("word",  "Word"),
    ("excel", "Excel"),
    ("dwg",   "dwg"),
    ("pdf",   "pdf"),
]


class TaskDialog(tk.Toplevel):
    """Диалог настройки одной задачи замены."""

    def __init__(self, parent, task=None, title="Новая задача замены"):
        super().__init__(parent)
        self.result = None
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(padx=0, pady=0)

        # Значения по умолчанию
        task = task or {}
        targets = task.get("targets", {"word": True, "excel": True})
        exts = task.get("filename_exts_groups",
                        task.get("_groups", {"word", "excel", "dwg", "pdf"}))

        self.find_var = tk.StringVar(value=task.get("find", ""))
        self.replace_var = tk.StringVar(value=task.get("replace", ""))
        self.target_vars = {
            key: tk.BooleanVar(value=bool(targets.get(key, False)))
            for key, _, _ in TARGET_LABELS
        }
        self.ext_vars = {
            key: tk.BooleanVar(value=(key in exts))
            for key, _ in EXT_LABELS
        }

        self._build()
        self._sync_ext_state()

        # Центрируем относительно родителя
        self.update_idletasks()
        self._center(parent)

        self.grab_set()
        self.find_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda e: self._cancel())

    # ── Построение интерфейса ──────────────────────────────────────────
    def _build(self):
        wrap = ttk.Frame(self, padding=18)
        wrap.pack(fill=tk.BOTH, expand=True)

        ttk.Label(wrap, text="Замена текста", style="H2.TLabel").pack(
            anchor="w", pady=(0, 2))
        ttk.Label(wrap, style="Hint.TLabel",
                  text="Укажите, что искать и на что заменить."
                  ).pack(anchor="w", pady=(0, 10))

        # Поля поиска/замены
        f = ttk.Frame(wrap)
        f.pack(fill=tk.X)
        f.columnconfigure(1, weight=1)
        ttk.Label(f, text="Найти:").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 8))
        self.find_entry = ttk.Entry(f, textvariable=self.find_var, width=42)
        self.find_entry.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(f, text="Заменить на:").grid(row=1, column=0, sticky="w", pady=5, padx=(0, 8))
        ttk.Entry(f, textvariable=self.replace_var, width=42).grid(
            row=1, column=1, sticky="ew", pady=5)

        ttk.Separator(wrap).pack(fill=tk.X, pady=12)

        # Панель «Замена текста для:» (цели)
        ttk.Label(wrap, text="Что делать", style="H2.TLabel").pack(anchor="w")
        ttk.Label(wrap, style="Hint.TLabel",
                  text="Отметьте, где выполнять замену для этой задачи."
                  ).pack(anchor="w", pady=(0, 8))

        tgt = ttk.Frame(wrap)
        tgt.pack(fill=tk.X)
        for i, (key, icon_name, label) in enumerate(TARGET_LABELS):
            cb = ttk.Checkbutton(tgt, text="  " + label,
                                 variable=self.target_vars[key],
                                 image=get_icon(icon_name, 18), compound="left")
            cb.grid(row=i, column=0, sticky="w", pady=3)
            if key == "filename":
                self.target_vars[key].trace_add("write", self._sync_ext_state)

        # Список расширений для имён файлов
        self.ext_frame = ttk.LabelFrame(
            wrap, text="Расширения для имён файлов", padding=10)
        self.ext_frame.pack(fill=tk.X, pady=(10, 0))
        row = ttk.Frame(self.ext_frame)
        row.pack(fill=tk.X)
        for key, label in EXT_LABELS:
            ttk.Checkbutton(row, text=label, variable=self.ext_vars[key]).pack(
                side=tk.LEFT, padx=10)

        # Кнопки
        btns = ttk.Frame(wrap)
        btns.pack(fill=tk.X, pady=(18, 0))
        ttk.Button(btns, text="Отмена", command=self._cancel).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(btns, text="Сохранить", style="Accent.TButton",
                   command=self._ok).pack(side=tk.RIGHT)

    def _center(self, parent):
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = px + (pw - w) // 2
            y = py + (ph - h) // 3
            self.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

    def _sync_ext_state(self, *args):
        state = tk.NORMAL if self.target_vars["filename"].get() else tk.DISABLED
        for child in self.ext_frame.winfo_children():
            for sub in child.winfo_children():
                try:
                    sub.configure(state=state)
                except tk.TclError:
                    pass

    # ── Завершение ─────────────────────────────────────────────────────
    def _ok(self):
        from tkinter import messagebox
        find = self.find_var.get()
        if not find:
            messagebox.showwarning("Внимание", "Введите текст для поиска.", parent=self)
            return
        targets = {k: v.get() for k, v in self.target_vars.items()}
        if not any(targets.values()):
            messagebox.showwarning(
                "Внимание", "Отметьте хотя бы одну цель (что делать).", parent=self)
            return
        groups = {k for k, v in self.ext_vars.items() if v.get()}
        if targets.get("filename") and not groups:
            messagebox.showwarning(
                "Внимание",
                "Для замены имён файлов выберите хотя бы одно расширение.",
                parent=self)
            return
        # Собираем множество расширений из выбранных групп
        exts = set()
        for g in groups:
            exts |= text_replacer.FILENAME_EXT_GROUPS.get(g, set())

        self.result = {
            "find": find,
            "replace": self.replace_var.get(),
            "targets": targets,
            "filename_exts": exts,
            "filename_exts_groups": groups,  # для повторного редактирования
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()
