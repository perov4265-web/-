# -*- coding: utf-8 -*-
"""Подключение C/C++ библиотеки libdxfrw через её C-обёртку (DLL/SO).

Это «мост» к нативной библиотеке: загружает скомпилированную
dxfrw_replace.dll (Windows) / .so (Linux) через ctypes и предоставляет
простую функцию замены текста в DXF.

Библиотека НЕОБЯЗАТЕЛЬНА. Если DLL не собрана/не найдена — функции просто
сообщают, что библиотека недоступна, и приложение продолжает использовать
основной путь (ezdxf). См. как она используется в text_replacer.py
(replace_in_dxf / replace_in_dwg — как запасной вариант).

Сборка DLL — см. prodact/libdxfrw/wrapper/BUILD.md
"""
import os
import sys
import ctypes
from pathlib import Path
from typing import Optional


_LIB = None          # загруженный ctypes-объект (или None)
_LOAD_ATTEMPTED = False
_LOAD_ERROR = None   # текст ошибки загрузки, если была


def _candidate_names():
    """Возможные имена файла библиотеки по платформам."""
    if os.name == "nt":
        return ["dxfrw_replace.dll", "libdxfrw_replace.dll"]
    if sys.platform == "darwin":
        return ["libdxfrw_replace.dylib", "dxfrw_replace.dylib"]
    return ["libdxfrw_replace.so", "dxfrw_replace.so"]


def _search_dirs():
    """Папки, где ищем библиотеку: рядом с программой и в подпапке libdxfrw/."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent
    return [
        base,
        base / "libdxfrw",
        base.parent / "libdxfrw",
    ]


def _find_library() -> Optional[Path]:
    for d in _search_dirs():
        for name in _candidate_names():
            p = d / name
            if p.exists():
                return p
    return None


def load() -> bool:
    """Пытается загрузить библиотеку. Возвращает True при успехе.
    Повторные вызовы кэшируются."""
    global _LIB, _LOAD_ATTEMPTED, _LOAD_ERROR
    if _LOAD_ATTEMPTED:
        return _LIB is not None
    _LOAD_ATTEMPTED = True

    path = _find_library()
    if path is None:
        _LOAD_ERROR = "DLL libdxfrw не найдена (не собрана)."
        return False
    try:
        lib = ctypes.CDLL(str(path))
        lib.dxf_replace_text.restype = ctypes.c_int
        lib.dxf_replace_text.argtypes = [ctypes.c_char_p] * 4
        lib.dxf_replace_version.restype = ctypes.c_char_p
        _LIB = lib
        return True
    except Exception as e:
        _LOAD_ERROR = f"Не удалось загрузить libdxfrw: {e}"
        _LIB = None
        return False


def is_available() -> bool:
    return load()


def version() -> Optional[str]:
    if not load():
        return None
    try:
        return _LIB.dxf_replace_version().decode("utf-8", "replace")
    except Exception:
        return None


def replace_text_in_dxf(in_path: str, out_path: str,
                        find: str, replace: str) -> int:
    """Заменяет текст в DXF через нативную libdxfrw.

    Возвращает число замен (>=0) или поднимает RuntimeError при ошибке
    библиотеки / её отсутствии.
    """
    if not load():
        raise RuntimeError(_LOAD_ERROR or "libdxfrw недоступна")
    n = _LIB.dxf_replace_text(
        str(in_path).encode("utf-8"),
        str(out_path).encode("utf-8"),
        find.encode("utf-8"),
        replace.encode("utf-8"),
    )
    if n == -1:
        raise RuntimeError("libdxfrw: не удалось прочитать входной DXF")
    if n == -2:
        raise RuntimeError("libdxfrw: не удалось записать выходной DXF")
    return int(n)
