# -*- coding: utf-8 -*-
"""Генератор цветных PNG-иконок интерфейса «Заменитель текста».

Рисует набор плоских цветных иконок в едином стиле средствами Pillow
(без внешних SVG-движков) и сохраняет их в resources/icons/<name>.png.

Иконки рисуются с 4-кратным запасом разрешения (supersampling) и затем
уменьшаются с сглаживанием — так получаются ровные края.

Запуск:
    python tools/make_icons.py
"""
import os
import math
from PIL import Image, ImageDraw

# ── Палитра иконок (сочные, но не кричащие цвета) ──────────────────────────
PAL = {
    "blue":    "#2f6fed",
    "blue_d":  "#1b4fc0",
    "green":   "#1faa59",
    "green_d": "#15833f",
    "red":     "#e1503e",
    "red_d":   "#b8392b",
    "orange":  "#f29230",
    "orange_d":"#d2761a",
    "violet":  "#7b54d6",
    "violet_d":"#5d39b0",
    "teal":    "#1aa6b7",
    "teal_d":  "#127f8d",
    "amber":   "#f2c037",
    "slate":   "#5b6b7d",
    "slate_d": "#3d4a59",
    "white":   "#ffffff",
    "paper":   "#f4f7fc",
    "ink":     "#2a3442",
}

SS = 4                 # supersampling factor
BASE = 64              # итоговый размер иконки (px)
CANVAS = BASE * SS     # размер рабочего холста


def _new():
    """Новый прозрачный холст увеличенного размера + ImageDraw."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def _save(img, name):
    out_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "resources", "icons")
    os.makedirs(out_dir, exist_ok=True)
    small = img.resize((BASE, BASE), Image.LANCZOS)
    small.save(os.path.join(out_dir, name + ".png"))
    print("  ✓", name + ".png")


def _rr(d, box, r, fill=None, outline=None, width=1):
    """Скруглённый прямоугольник (координаты в системе увеличенного холста)."""
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def s(v):
    """Масштабирует «логическую» координату (0..64) в координаты холста."""
    return int(round(v * SS))


# ── Отдельные иконки ───────────────────────────────────────────────────────
def icon_add():
    img, d = _new()
    _rr(d, [s(8), s(8), s(56), s(56)], s(16), fill=PAL["green"])
    _rr(d, [s(8), s(8), s(56), s(20)], s(16), fill=PAL["green"])  # лёгкий блик сверху
    d.rounded_rectangle([s(8), s(8), s(56), s(56)], radius=s(16),
                        outline=PAL["green_d"], width=s(1.2))
    # плюс
    cx, cy, ln, th = s(32), s(32), s(13), s(4.5)
    d.rounded_rectangle([cx - th, cy - ln, cx + th, cy + ln], radius=th, fill=PAL["white"])
    d.rounded_rectangle([cx - ln, cy - th, cx + ln, cy + th], radius=th, fill=PAL["white"])
    return img


def icon_edit():
    img, d = _new()
    # Карандаш по диагонали: корпус + наконечник + ластик
    # Корпус (амбер) — толстая линия
    d.line([s(20), s(46), s(44), s(22)], fill=PAL["amber"], width=s(9))
    # Деревянный кончик (светлый)
    d.line([s(16), s(50), s(21), s(45)], fill=PAL["paper"], width=s(9))
    # Грифель (тёмный треугольник)
    d.polygon([(s(13), s(53)), (s(19), s(51)), (s(17), s(45))], fill=PAL["slate_d"])
    # Ластик (красный) у верхнего конца
    d.line([s(43), s(23), s(48), s(18)], fill=PAL["red"], width=s(9))
    # Тонкая окантовка корпуса
    d.line([s(20), s(46), s(44), s(22)], fill=PAL["orange_d"], width=s(1))
    return img


def icon_delete():
    img, d = _new()
    # корзина
    body = [s(18), s(22), s(46), s(54)]
    _rr(d, body, s(5), fill=PAL["red"])
    d.rounded_rectangle(body, radius=s(5), outline=PAL["red_d"], width=s(1.3))
    # крышка
    _rr(d, [s(14), s(15), s(50), s(22)], s(3), fill=PAL["red_d"])
    # ручка
    _rr(d, [s(26), s(10), s(38), s(16)], s(3), fill=PAL["red_d"])
    # рёбра
    for x in (s(26), s(32), s(38)):
        d.line([x, s(28), x, s(48)], fill=PAL["white"], width=s(2.2))
    return img


def icon_clear():
    """Метла/очистка."""
    img, d = _new()
    d.line([s(46), s(14), s(28), s(34)], fill=PAL["slate"], width=s(5))   # ручка
    # веник
    d.polygon([(s(18), s(50), ), (s(34), s(50)), (s(30), s(32)), (s(22), s(32))],
              fill=PAL["amber"])
    d.polygon([(s(18), s(50)), (s(34), s(50)), (s(30), s(32)), (s(22), s(32))],
              outline=PAL["orange_d"], width=s(1.2))
    for x in (s(22), s(26), s(30)):
        d.line([x, s(40), x, s(50)], fill=PAL["orange_d"], width=s(1.4))
    return img


def icon_replace():
    """Две круговые стрелки (замена/обмен) — верхняя и нижняя дуги."""
    img, d = _new()
    bbox = [s(15), s(15), s(49), s(49)]
    # Верхняя дуга со стрелкой вправо
    d.arc(bbox, start=200, end=350, fill=PAL["blue"], width=s(5))
    d.polygon([(s(46), s(16)), (s(52), s(24)), (s(42), s(26))], fill=PAL["blue_d"])
    # Нижняя дуга со стрелкой влево
    d.arc(bbox, start=20, end=170, fill=PAL["teal"], width=s(5))
    d.polygon([(s(18), s(48)), (s(12), s(40)), (s(22), s(38))], fill=PAL["teal_d"])
    return img


def icon_rollback():
    """Стрелка отката влево-назад."""
    img, d = _new()
    bbox = [s(16), s(16), s(48), s(48)]
    d.arc(bbox, start=120, end=400, fill=PAL["violet"], width=s(6))
    d.polygon([(s(18), s(12)), (s(30), s(16)), (s(20), s(24))], fill=PAL["violet_d"])
    return img


def icon_folder():
    img, d = _new()
    _rr(d, [s(10), s(20), s(54), s(50)], s(5), fill=PAL["amber"])
    d.polygon([(s(10), s(24)), (s(24), s(24)), (s(30), s(18)), (s(12), s(18))],
              fill=PAL["orange"])
    _rr(d, [s(10), s(26), s(54), s(50)], s(5), fill=PAL["amber"])
    d.rounded_rectangle([s(10), s(26), s(54), s(50)], radius=s(5),
                        outline=PAL["orange_d"], width=s(1.2))
    return img


def icon_word():
    img, d = _new()
    _rr(d, [s(14), s(8), s(50), s(56)], s(5), fill=PAL["white"],
        outline=PAL["blue_d"], width=s(1.4))
    _rr(d, [s(14), s(8), s(50), s(56)], s(5), outline=PAL["blue_d"], width=s(1.4))
    # синяя плашка с буквой W
    _rr(d, [s(8), s(28), s(40), s(48)], s(4), fill=PAL["blue"])
    d.line([s(13), s(33), s(17), s(43)], fill=PAL["white"], width=s(2.4))
    d.line([s(17), s(43), s(21), s(35)], fill=PAL["white"], width=s(2.4))
    d.line([s(21), s(35), s(25), s(43)], fill=PAL["white"], width=s(2.4))
    d.line([s(25), s(43), s(29), s(33)], fill=PAL["white"], width=s(2.4))
    return img


def icon_excel():
    img, d = _new()
    _rr(d, [s(14), s(8), s(50), s(56)], s(5), fill=PAL["white"],
        outline=PAL["green_d"], width=s(1.4))
    _rr(d, [s(8), s(28), s(40), s(48)], s(4), fill=PAL["green"])
    # буква X
    d.line([s(13), s(33), s(23), s(43)], fill=PAL["white"], width=s(2.6))
    d.line([s(23), s(33), s(13), s(43)], fill=PAL["white"], width=s(2.6))
    return img


def icon_autocad():
    """Чертёж/циркуль."""
    img, d = _new()
    _rr(d, [s(12), s(10), s(52), s(54)], s(4), fill=PAL["paper"],
        outline=PAL["teal_d"], width=s(1.3))
    # линии чертежа
    d.line([s(18), s(44), s(34), s(20)], fill=PAL["teal"], width=s(2.4))
    d.line([s(34), s(20), s(46), s(44)], fill=PAL["teal"], width=s(2.4))
    d.line([s(18), s(44), s(46), s(44)], fill=PAL["teal"], width=s(2.4))
    d.ellipse([s(31), s(17), s(37), s(23)], fill=PAL["orange"])
    return img


def icon_pdf():
    img, d = _new()
    _rr(d, [s(14), s(8), s(50), s(56)], s(5), fill=PAL["white"],
        outline=PAL["red_d"], width=s(1.4))
    # загнутый уголок
    d.polygon([(s(40), s(8)), (s(50), s(18)), (s(40), s(18))], fill=PAL["red"])
    # плашка PDF
    _rr(d, [s(8), s(30), s(44), s(46)], s(4), fill=PAL["red"])
    return img


def icon_filename():
    """Файл с ярлычком (тег)."""
    img, d = _new()
    _rr(d, [s(16), s(10), s(46), s(54)], s(5), fill=PAL["white"],
        outline=PAL["slate_d"], width=s(1.4))
    d.polygon([(s(36), s(10)), (s(46), s(20)), (s(36), s(20))], fill=PAL["slate"])
    # тег
    _rr(d, [s(8), s(34), s(30), s(50)], s(4), fill=PAL["violet"])
    d.ellipse([s(11), s(40), s(16), s(45)], fill=PAL["white"])
    return img


def icon_help():
    img, d = _new()
    d.ellipse([s(8), s(8), s(56), s(56)], fill=PAL["blue"])
    d.ellipse([s(8), s(8), s(56), s(56)], outline=PAL["blue_d"], width=s(1.4))
    # знак вопроса
    d.arc([s(22), s(18), s(42), s(36)], start=160, end=20, fill=PAL["white"], width=s(4))
    d.line([s(32), s(34), s(32), s(40)], fill=PAL["white"], width=s(4))
    d.ellipse([s(29), s(44), s(35), s(50)], fill=PAL["white"])
    return img


def icon_info():
    img, d = _new()
    d.ellipse([s(8), s(8), s(56), s(56)], fill=PAL["teal"])
    d.ellipse([s(8), s(8), s(56), s(56)], outline=PAL["teal_d"], width=s(1.4))
    d.ellipse([s(29), s(18), s(35), s(24)], fill=PAL["white"])
    d.rounded_rectangle([s(29), s(28), s(35), s(46)], radius=s(3), fill=PAL["white"])
    return img


def icon_app():
    """Логотип приложения — буква с лупой замены."""
    img, d = _new()
    _rr(d, [s(6), s(6), s(58), s(58)], s(14), fill=PAL["blue"])
    _rr(d, [s(6), s(6), s(58), s(58)], s(14), outline=PAL["blue_d"], width=s(1.4))
    # буква A (Abc)
    d.line([s(18), s(44), s(26), s(20)], fill=PAL["white"], width=s(3))
    d.line([s(26), s(20), s(34), s(44)], fill=PAL["white"], width=s(3))
    d.line([s(21), s(36), s(31), s(36)], fill=PAL["white"], width=s(2.4))
    # стрелка замены
    d.arc([s(34), s(30), s(52), s(48)], start=10, end=300, fill=PAL["amber"], width=s(3.2))
    d.polygon([(s(50), s(28)), (s(56), s(34)), (s(48), s(36))], fill=PAL["amber"])
    return img


def icon_run():
    """Запуск замены — стрелка-play в круге."""
    img, d = _new()
    d.ellipse([s(8), s(8), s(56), s(56)], fill=PAL["green"])
    d.ellipse([s(8), s(8), s(56), s(56)], outline=PAL["green_d"], width=s(1.4))
    d.polygon([(s(26), s(22)), (s(26), s(42)), (s(44), s(32))], fill=PAL["white"])
    return img


def icon_save():
    img, d = _new()
    _rr(d, [s(12), s(12), s(52), s(52)], s(5), fill=PAL["blue"])
    _rr(d, [s(20), s(12), s(44), s(24)], s(2), fill=PAL["blue_d"])
    _rr(d, [s(18), s(34), s(46), s(50)], s(2), fill=PAL["white"])
    _rr(d, [s(34), s(14), s(40), s(22)], s(1), fill=PAL["paper"])
    return img


ICONS = {
    "add": icon_add,
    "edit": icon_edit,
    "delete": icon_delete,
    "clear": icon_clear,
    "replace": icon_replace,
    "rollback": icon_rollback,
    "folder": icon_folder,
    "word": icon_word,
    "excel": icon_excel,
    "autocad": icon_autocad,
    "pdf": icon_pdf,
    "filename": icon_filename,
    "help": icon_help,
    "info": icon_info,
    "app": icon_app,
    "run": icon_run,
    "save": icon_save,
}


def main():
    print("Генерация цветных иконок:")
    for name, fn in ICONS.items():
        _save(fn(), name)
    print("Готово.")


if __name__ == "__main__":
    main()
