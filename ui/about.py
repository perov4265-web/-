# -*- coding: utf-8 -*-
"""Окна «Справка» и «О программе»."""
import tkinter as tk
from tkinter import ttk

from ui.icons import get_icon

APP_VERSION = "1.1"
AUTHOR = "Трусов И.П."
AUTHOR_EMAIL = "i@sb-p.ru"

HELP_TEXT = """\
КРАТКОЕ РУКОВОДСТВО

1. Выберите папку
   Нажмите «Выбрать…» и укажите папку. Обработка идёт рекурсивно — \
включая вложенные папки.

2. Добавьте задачи замены
   Нажмите «Добавить». Откроется окно задачи, в котором нужно:
     • ввести текст «Найти» и «Заменить на»;
     • отметить, ЧТО делать (раздел «Что делать»):
         – Word (.docx), Excel (.xlsx), AutoCAD (.dxf/.dwg), PDF (.pdf)
           — замена текста ВНУТРИ файлов;
         – Имена файлов — переименование самих файлов;
         – Имена папок — переименование папок;
     • если выбрано «Имена файлов», указать расширения
       (Word, Excel, dwg, pdf) — переименование затронет только их.
   Каждая задача имеет собственную конфигурацию. Их можно добавить сколько угодно.

3. Конфигурация в таблице
   В таблице задач видно, что именно делает каждая строка
   (колонка «Конфигурация задачи»). Двойной клик по строке — редактирование.

4. Выполните замену
   Нажмите «Выполнить замену». Перед изменением автоматически создаётся
   резервная копия. Все задачи выполняются как одна операция.

5. Откат
   Кнопка «Вернуть прежнее» отменяет последнюю операцию целиком:
   восстанавливает и содержимое файлов, и прежние имена файлов/папок.

ЖУРНАЛ
   Внизу отображается иерархический журнал: операция → файлы → конкретные замены.

ПОДДЕРЖИВАЕМЫЕ ФОРМАТЫ
   Word .docx (текст, таблицы, колонтитулы), Excel .xlsx (ячейки всех листов),
   PDF .pdf (PyMuPDF → pikepdf → pypdf), AutoCAD .dxf и .dwg (TEXT/MTEXT/ATTRIB).

СОВЕТЫ
   • Замены применяются по порядку задач — учитывайте это при цепочках замен.
   • Если файл уже содержит целевое имя, переименование такого файла \
пропускается с пометкой в журнале.
"""


def _center(win, parent):
    win.update_idletasks()
    try:
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = win.winfo_width(), win.winfo_height()
        win.geometry(f"+{max(px + (pw - w)//2, 0)}+{max(py + (ph - h)//3, 0)}")
    except Exception:
        pass


def show_help(parent):
    win = tk.Toplevel(parent)
    win.title("Справка")
    win.transient(parent)
    win.geometry("680x600")
    win.minsize(560, 460)

    head = ttk.Frame(win, padding=(16, 14, 16, 8))
    head.pack(fill=tk.X)
    icon = get_icon("help", 28)
    if icon:
        lbl = ttk.Label(head, image=icon)
        lbl.image = icon
        lbl.pack(side=tk.LEFT, padx=(0, 10))
    ttk.Label(head, text="Справка по программе", style="H2.TLabel").pack(side=tk.LEFT)

    body = ttk.Frame(win, padding=(16, 0, 16, 12))
    body.pack(fill=tk.BOTH, expand=True)
    txt = tk.Text(body, wrap="word", font=("Segoe UI", 10), relief="flat",
                  padx=10, pady=10, borderwidth=1)
    vsb = ttk.Scrollbar(body, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=vsb.set)
    txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    txt.insert("1.0", HELP_TEXT)
    txt.configure(state="disabled")

    btns = ttk.Frame(win, padding=(16, 0, 16, 14))
    btns.pack(fill=tk.X)
    ttk.Button(btns, text="Закрыть", command=win.destroy).pack(side=tk.RIGHT)

    _center(win, parent)
    win.grab_set()


def show_about(parent):
    win = tk.Toplevel(parent)
    win.title("О программе")
    win.transient(parent)
    win.resizable(False, False)

    wrap = ttk.Frame(win, padding=22)
    wrap.pack(fill=tk.BOTH, expand=True)

    icon = get_icon("app", 56)
    if icon:
        lbl = ttk.Label(wrap, image=icon)
        lbl.image = icon
        lbl.pack(pady=(0, 8))

    ttk.Label(wrap, text="Заменитель текста", style="H1.TLabel").pack()
    ttk.Label(wrap, text=f"Версия {APP_VERSION}", style="Muted.TLabel").pack(pady=(2, 14))

    info = ttk.Frame(wrap)
    info.pack()
    ttk.Label(info, text="Массовая замена текста в документах Word, Excel,\n"
                         "PDF, AutoCAD и в именах файлов и папок.",
              justify="center").pack(pady=(0, 14))

    ttk.Separator(wrap).pack(fill=tk.X, pady=6)

    author = ttk.Frame(wrap)
    author.pack(pady=(8, 0))
    ttk.Label(author, text="Автор:", style="Muted.TLabel").grid(
        row=0, column=0, sticky="e", padx=(0, 8), pady=2)
    ttk.Label(author, text=AUTHOR, font=("Segoe UI", 10, "bold")).grid(
        row=0, column=1, sticky="w", pady=2)
    ttk.Label(author, text="E-mail:", style="Muted.TLabel").grid(
        row=1, column=0, sticky="e", padx=(0, 8), pady=2)
    ttk.Label(author, text=AUTHOR_EMAIL, foreground="#2f6fed").grid(
        row=1, column=1, sticky="w", pady=2)

    ttk.Button(wrap, text="Закрыть", style="Accent.TButton",
               command=win.destroy).pack(pady=(20, 0))

    _center(win, parent)
    win.grab_set()
