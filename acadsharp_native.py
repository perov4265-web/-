# -*- coding: utf-8 -*-
"""Подключение библиотеки ACadSharp (.NET) через внешнюю утилиту AcadReplace.exe.

ACadSharp — библиотека на C#/.NET, поэтому она вызывается не напрямую из
Python, а как отдельный процесс (по аналогии с LibreDWG). Утилита AcadReplace
читает DWG/DXF, заменяет текст в сущностях TEXT/MTEXT и записывает результат.

Библиотека НЕОБЯЗАТЕЛЬНА. Если AcadReplace.exe не собрана/не найдена — функции
сообщают о недоступности, и приложение использует другие пути (ezdxf, libdxfrw).
Это самый последний (третий) запасной вариант для чертежей.

Сборка утилиты — см. prodact/acadsharp/BUILD.md
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


def _exe_name() -> str:
    return "AcadReplace.exe" if os.name == "nt" else "AcadReplace"


def _search_dirs():
    """Папки поиска: рядом с программой, в libredwg/ и в acadsharp/."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return [
        base,
        base / "libredwg",
        base / "acadsharp",
        base.parent / "acadsharp",
    ]


def _find_exe() -> Optional[Path]:
    name = _exe_name()
    for d in _search_dirs():
        p = d / name
        if p.exists():
            return p
    return None


def is_available() -> bool:
    return _find_exe() is not None


def replace_text(in_path: str, out_path: str, find: str, replace: str) -> int:
    """Заменяет текст в DWG/DXF через утилиту ACadSharp.

    Возвращает число замен (>=0) или поднимает RuntimeError при ошибке/
    отсутствии утилиты.
    """
    exe = _find_exe()
    if exe is None:
        raise RuntimeError("ACadSharp: утилита AcadReplace не найдена (не собрана)")

    creationflags = 0
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        result = subprocess.run(
            [str(exe), str(in_path), str(out_path), find, replace],
            capture_output=True, timeout=120, creationflags=creationflags,
        )
    except Exception as e:
        raise RuntimeError(f"ACadSharp: запуск не удался: {e}")

    if result.returncode == 1:
        err = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"ACadSharp: ошибка чтения. {err}")
    if result.returncode == 2:
        err = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"ACadSharp: ошибка записи. {err}")
    if result.returncode == 3:
        raise RuntimeError("ACadSharp: неверные аргументы")

    # stdout: "REPLACED <N>"
    out = result.stdout.decode("utf-8", "replace").strip()
    n = 0
    for line in out.splitlines():
        if line.startswith("REPLACED"):
            try:
                n = int(line.split()[1])
            except (IndexError, ValueError):
                n = 0
    return n
