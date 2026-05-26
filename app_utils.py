# -*- coding: utf-8 -*-
"""
Вспомогательные функции для определения каталогов приложения.
Вынесены в отдельный модуль, чтобы избежать циклических импортов.
"""

import os
import sys
from pathlib import Path

APP_DATA_FOLDER = "ASU NEPT"


def get_app_data_dir() -> Path:
    """Возвращает общий каталог данных приложения: %ProgramData%\\ASU NEPT
    на Windows (общий для всех пользователей), либо аналог на других ОС.
    Здесь хранится локальная база данных клиента.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("PROGRAMDATA") or os.environ.get("ALLUSERSPROFILE") \
            or r"C:\ProgramData"
        path = Path(base) / APP_DATA_FOLDER
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        path = Path(base) / APP_DATA_FOLDER
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = get_exe_dir() / "data"
        path.mkdir(parents=True, exist_ok=True)
    return path


def get_exe_dir() -> Path:
    """Папка, где лежит .exe (frozen) или main.py (исходники)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    # When called from a submodule, resolve relative to this file's parent
    return Path(__file__).parent


def get_user_data_dir() -> Path:
    """Совместимость: для output/templates — папка рядом с программой."""
    return get_exe_dir()
