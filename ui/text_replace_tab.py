# -*- coding: utf-8 -*-
"""Раздел «Заменитель текста».

Задачи замены задаются списком: каждая строка — отдельная задача со своим
текстом «найти/заменить» и собственной конфигурацией (что менять: содержимое
файлов Word/Excel/AutoCAD/PDF, имена файлов, имена папок). Конфигурация
видна прямо в таблице. Добавление и редактирование — через всплывающее окно.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from pathlib import Path

import text_replacer
import app_utils as app_main
from ui.icons import get_icon
from ui.task_dialog import TaskDialog
from ui import theme


# Короткие подписи целей для колонки конфигурации
TARGET_SHORT = {
    "word": "Word",
    "excel": "Excel",
    "autocad": "AutoCAD",
    "pdf": "PDF",
    "filename": "имена файлов",
    "foldername": "имена папок",
}


def task_config_text(task: dict) -> str:
    """Человекочитаемое описание конфигурации задачи для таблицы."""
    targets = task.get("targets", {})
    content = [TARGET_SHORT[k] for k in ("word", "excel", "autocad", "pdf")
               if targets.get(k)]
    parts = []
    if content:
        parts.append("файлы: " + ", ".join(content))
    if targets.get("filename"):
        groups = task.get("filename_exts_groups") or set()
        gtxt = ", ".join(sorted(groups)) if groups else "все"
        parts.append(f"имена файлов ({gtxt})")
    if targets.get("foldername"):
        parts.append("имена папок")
    return "  •  ".join(parts) if parts else "—"


class TextReplaceTab(ttk.Frame):
    """Вкладка замены текста: список задач, журнал, откат."""

    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main = main_window
        self._last_tx = None
        self._tasks = []  # список словарей-задач
        self._build_ui()

    # ── Построение интерфейса ──────────────────────────────────────────
    def _build_ui(self):
        outer = ttk.Frame(self, padding=(14, 10))
        outer.pack(fill=tk.BOTH, expand=True)

        # Выбор папки
        folder_frame = ttk.Frame(outer)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(folder_frame, text="Папка для обработки:",
                  style="H2.TLabel").pack(anchor="w", pady=(0, 4))
        row = ttk.Frame(folder_frame)
        row.pack(fill=tk.X)
        self.folder_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.folder_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text=" Выбрать…", image=get_icon("folder", 18),
                   compound="left", command=self._choose_folder).pack(
                   side=tk.LEFT, padx=(8, 0))

        # Список задач
        tasks_box = ttk.LabelFrame(outer, text="Задачи замены", padding=10)
        tasks_box.pack(fill=tk.BOTH, expand=True)

        bar = ttk.Frame(tasks_box)
        bar.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(bar, text=" Добавить", image=get_icon("add", 18),
                   compound="left", style="Accent.TButton",
                   command=self._add_task).pack(side=tk.LEFT)
        ttk.Button(bar, text=" Изменить", image=get_icon("edit", 18),
                   compound="left", command=self._edit_task).pack(side=tk.LEFT, padx=6)
        ttk.Button(bar, text=" Удалить", image=get_icon("delete", 18),
                   compound="left", command=self._delete_task).pack(side=tk.LEFT)
        ttk.Button(bar, text=" Очистить все", image=get_icon("clear", 18),
                   compound="left", command=self._clear_tasks).pack(side=tk.LEFT, padx=6)

        tbl_wrap = ttk.Frame(tasks_box)
        tbl_wrap.pack(fill=tk.BOTH, expand=True)
        self.tasks_tree = ttk.Treeview(
            tbl_wrap, columns=("find", "replace", "config"),
            show="headings", selectmode="browse", height=7)
        self.tasks_tree.heading("find", text="Найти")
        self.tasks_tree.heading("replace", text="Заменить на")
        self.tasks_tree.heading("config", text="Конфигурация задачи")
        self.tasks_tree.column("find", width=200, anchor=tk.W)
        self.tasks_tree.column("replace", width=200, anchor=tk.W)
        self.tasks_tree.column("config", width=420, anchor=tk.W)
        vsb = ttk.Scrollbar(tbl_wrap, orient="vertical",
                            command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=vsb.set)
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_tree.bind("<Double-1>", lambda e: self._edit_task())
        theme.configure_tree_tags(self.tasks_tree)

        # Кнопки операции
        ops = ttk.Frame(outer)
        ops.pack(fill=tk.X, pady=(10, 8))
        self.replace_btn = ttk.Button(
            ops, text=" Выполнить замену", image=get_icon("run", 18),
            compound="left", style="Accent.TButton", command=self._do_replace)
        self.replace_btn.pack(side=tk.LEFT)
        self.rollback_btn = ttk.Button(
            ops, text=" Вернуть прежнее", image=get_icon("rollback", 18),
            compound="left", command=self._do_rollback, state=tk.DISABLED)
        self.rollback_btn.pack(side=tk.LEFT, padx=6)
        ttk.Button(ops, text=" Очистить журнал", image=get_icon("clear", 18),
                   compound="left", command=self._clear_log).pack(side=tk.LEFT)

        # Журнал
        log_frame = ttk.LabelFrame(outer, text="Журнал замены", padding=8)
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_tree = ttk.Treeview(log_frame, columns=("info",),
                                     show="tree headings", selectmode="browse")
        self.log_tree.heading("#0", text="Файл / Папка / Замена")
        self.log_tree.column("#0", width=560, anchor=tk.W)
        self.log_tree.heading("info", text="Сведения")
        self.log_tree.column("info", width=320, anchor=tk.W)
        lvsb = ttk.Scrollbar(log_frame, orient="vertical",
                             command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=lvsb.set)
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lvsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_tree.tag_configure("file", font=("Segoe UI", 9, "bold"),
                                    foreground="#1a4d80")
        self.log_tree.tag_configure("change", font=("Segoe UI", 9))
        self.log_tree.tag_configure("error", foreground="#c00")
        self.log_tree.tag_configure("op", font=("Segoe UI", 10, "bold"),
                                    foreground="#0a3060")
        self._kind_icon = {
            "word": "📄", "excel": "📊", "autocad": "📐",
            "pdf": "📕", "filename": "🏷", "foldername": "📁",
        }

    # ── Папка ──────────────────────────────────────────────────────────
    def _choose_folder(self):
        d = filedialog.askdirectory(title="Выберите папку для замены")
        if d:
            self.folder_var.set(d)

    def _backup_root(self) -> Path:
        try:
            base = app_main.get_app_data_dir() / "text_replace_backups"
        except Exception:
            base = Path.home() / ".asu_nept_backups"
        base.mkdir(parents=True, exist_ok=True)
        return base

    # ── Управление задачами ────────────────────────────────────────────
    def _refresh_tasks_table(self):
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        for i, t in enumerate(self._tasks):
            tag = "even" if i % 2 else "odd"
            self.tasks_tree.insert(
                "", tk.END, iid=str(i),
                values=(t.get("find", ""), t.get("replace", ""),
                        task_config_text(t)),
                tags=(tag,))

    def _add_task(self):
        dlg = TaskDialog(self.winfo_toplevel(), title="Новая задача замены")
        self.wait_window(dlg)
        if dlg.result:
            self._tasks.append(dlg.result)
            self._refresh_tasks_table()

    def _selected_index(self):
        sel = self.tasks_tree.selection()
        if not sel:
            return None
        try:
            return int(sel[0])
        except ValueError:
            return None

    def _edit_task(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Изменение", "Выберите задачу в таблице.")
            return
        dlg = TaskDialog(self.winfo_toplevel(), task=self._tasks[idx],
                         title="Изменить задачу замены")
        self.wait_window(dlg)
        if dlg.result:
            self._tasks[idx] = dlg.result
            self._refresh_tasks_table()

    def _delete_task(self):
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Удаление", "Выберите задачу для удаления.")
            return
        del self._tasks[idx]
        self._refresh_tasks_table()

    def _clear_tasks(self):
        if self._tasks and messagebox.askyesno(
                "Очистить", "Удалить все задачи из списка?"):
            self._tasks.clear()
            self._refresh_tasks_table()

    # ── Выполнение замены ──────────────────────────────────────────────
    def _do_replace(self):
        folder = self.folder_var.get().strip()
        if not folder or not Path(folder).is_dir():
            messagebox.showwarning("Внимание", "Выберите существующую папку.")
            return
        if not self._tasks:
            messagebox.showwarning(
                "Внимание", "Добавьте хотя бы одну задачу замены.")
            return

        lines = "\n".join(
            f"  • «{t['find']}» → «{t.get('replace','')}»   [{task_config_text(t)}]"
            for t in self._tasks)
        if not messagebox.askyesno(
                "Подтверждение замены",
                f"Будут выполнены задачи:\n{lines}\n\nв папке:\n{folder}\n\n"
                f"Перед изменением создаётся резервная копия. Продолжить?"):
            return

        self.replace_btn.configure(state=tk.DISABLED)
        self.main.set_status("Замена текста…")
        tasks = list(self._tasks)

        def worker():
            try:
                tx = text_replacer.run_replace_tasks(
                    folder, tasks, backup_root=self._backup_root(),
                    progress=lambda m: None)
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._replace_failed(msg))
                return
            self.after(0, lambda: self._replace_done(tx))

        threading.Thread(target=worker, daemon=True).start()

    def _replace_failed(self, err):
        self.replace_btn.configure(state=tk.NORMAL)
        messagebox.showerror("Ошибка замены", err)
        self.main.set_status("Ошибка замены")

    def _replace_done(self, tx):
        self.replace_btn.configure(state=tk.NORMAL)
        self._last_tx = tx
        self._append_transaction_to_log(tx)
        total_files = len(tx.results)
        total_changes = sum(r.count for r in tx.results)
        if tx.actions:
            self.rollback_btn.configure(state=tk.NORMAL)
        self.main.set_status(
            f"Замена завершена: затронуто {total_files}, замен {total_changes}")
        messagebox.showinfo(
            "Готово",
            f"Замена завершена.\n\nЗатронуто файлов/папок: {total_files}\n"
            f"Всего замен: {total_changes}\n\n"
            f"Чтобы отменить — нажмите «Вернуть прежнее».")

    def _append_transaction_to_log(self, tx):
        op_iid = f"op::{id(tx)}"
        op_label = f"🕒 Операция {tx.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        pairs = getattr(tx, "pairs", [])
        pairs_info = "; ".join(f"«{f}» → «{r}»" for f, r in pairs) if pairs else ""
        self.log_tree.insert("", 0, iid=op_iid, text=op_label,
                             values=(pairs_info,), tags=("op",), open=True)
        if not tx.results:
            self.log_tree.insert(op_iid, tk.END, text="(совпадений не найдено)",
                                 values=("",), tags=("change",))
            return
        for i, r in enumerate(tx.results):
            icon = self._kind_icon.get(r.kind, "•")
            name = Path(r.path).name
            file_iid = f"{op_iid}::f{i}"
            if r.error:
                info, tag = f"ОШИБКА: {r.error}", "error"
            elif r.new_path:
                info, tag = f"→ {Path(r.new_path).name}  ({r.count} замен)", "file"
            else:
                info, tag = f"{r.count} замен", "file"
            self.log_tree.insert(op_iid, tk.END, iid=file_iid,
                                 text=f"{icon} {name}", values=(info,),
                                 tags=(tag,), open=False)
            for ch in r.changes:
                self.log_tree.insert(file_iid, tk.END, text=f"   ↳ {ch}",
                                     values=("",), tags=("change",))

    # ── Откат ──────────────────────────────────────────────────────────
    def _do_rollback(self):
        if not self._last_tx or not self._last_tx.actions:
            messagebox.showinfo("Откат", "Нет операции для отката.")
            return
        if not messagebox.askyesno(
                "Вернуть прежнее",
                "Отменить последнюю операцию замены?\n\n"
                "Будут восстановлены прежнее содержимое файлов и прежние имена."):
            return
        self.rollback_btn.configure(state=tk.DISABLED)
        self.main.set_status("Откат замены…")

        def worker():
            try:
                stats = text_replacer.rollback(self._last_tx, progress=lambda m: None)
            except Exception as e:
                msg = str(e)
                self.after(0, lambda: self._rollback_failed(msg))
                return
            self.after(0, lambda: self._rollback_done(stats))

        threading.Thread(target=worker, daemon=True).start()

    def _rollback_failed(self, err):
        self.rollback_btn.configure(state=tk.NORMAL)
        messagebox.showerror("Ошибка отката", err)
        self.main.set_status("Ошибка отката")

    def _rollback_done(self, stats):
        self._last_tx = None
        self.log_tree.insert("", 0, text="↩ ОТКАТ выполнен",
                             values=(f"содержимого: {stats['content']}, "
                                     f"имён: {stats['renames']}, "
                                     f"ошибок: {stats['errors']}",),
                             tags=("op",))
        self.main.set_status(
            f"Откат завершён: содержимого {stats['content']}, "
            f"имён {stats['renames']}, ошибок {stats['errors']}")
        messagebox.showinfo(
            "Откат завершён",
            f"Восстановлено содержимого файлов: {stats['content']}\n"
            f"Возвращено имён файлов/папок: {stats['renames']}\n"
            f"Ошибок: {stats['errors']}")

    def _clear_log(self):
        self.log_tree.delete(*self.log_tree.get_children())

    def on_data_changed(self, kind: str):
        pass
