# -*- coding: utf-8 -*-
"""Заменитель текста — автономное приложение.

Массовая замена текста в документах Word (.docx), Excel (.xlsx), PDF (.pdf),
AutoCAD (.dxf/.dwg), а также переименование файлов и папок.

Автор: Трусов И.П.  (i@sb-p.ru)

Запуск:  python main.py
"""
import sys
import tkinter as tk
from tkinter import ttk

from ui.theme import apply_theme
from ui.text_replace_tab import TextReplaceTab
from ui.icons import get_icon
from ui.about import show_help, show_about, APP_VERSION, AUTHOR, AUTHOR_EMAIL


APP_TITLE = f"Заменитель текста {APP_VERSION}"


class MainWindow:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.geometry("1040x760")
        root.minsize(860, 600)

        apply_theme(root)
        self._set_window_icon(root)
        self._build_menu(root)

        # Шапка
        header = ttk.Frame(root, padding=(16, 14, 16, 6))
        header.pack(side=tk.TOP, fill=tk.X)
        logo = get_icon("app", 34)
        if logo is not None:
            ttk.Label(header, image=logo).pack(side=tk.LEFT, padx=(0, 10))
            self._logo_ref = logo  # держим ссылку
        title_box = ttk.Frame(header)
        title_box.pack(side=tk.LEFT)
        ttk.Label(title_box, text="Заменитель текста",
                  style="H1.TLabel").pack(anchor="w")
        ttk.Label(title_box, style="Muted.TLabel",
                  text="Массовая замена в Word, Excel, PDF, AutoCAD и в именах файлов"
                  ).pack(anchor="w")

        # Основная вкладка-инструмент
        body = ttk.Frame(root)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.tab = TextReplaceTab(body, self)
        self.tab.pack(fill=tk.BOTH, expand=True)

        # Статусная строка
        self.status_var = tk.StringVar(value="Готов")
        status = ttk.Label(root, textvariable=self.status_var, anchor="w",
                           padding=(12, 6))
        status.pack(side=tk.BOTTOM, fill=tk.X)

    def _set_window_icon(self, root):
        try:
            from PIL import ImageTk, Image
            import os
            from ui.icons import _icons_dir
            p = os.path.join(_icons_dir(), "app.png")
            if os.path.exists(p):
                self._app_icon = ImageTk.PhotoImage(Image.open(p))
                root.iconphoto(True, self._app_icon)
        except Exception:
            pass

    def _build_menu(self, root):
        menubar = tk.Menu(root)

        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        # Помощь
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Справка",
                              command=lambda: show_help(root))
        help_menu.add_separator()
        help_menu.add_command(label="О программе",
                              command=lambda: show_about(root))
        menubar.add_cascade(label="Помощь", menu=help_menu)

        # Отдельный пункт «О программе» в строке меню (по просьбе)
        menubar.add_command(label="О программе",
                            command=lambda: show_about(root))

        root.config(menu=menubar)

    def set_status(self, text):
        self.status_var.set(text)
        try:
            self.root.update_idletasks()
        except tk.TclError:
            pass


def main():
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
