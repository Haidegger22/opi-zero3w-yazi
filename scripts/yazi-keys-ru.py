#!/usr/bin/env python3
# yazi-keys-ru.py — собрать справочник клавиш yazi (по-русски) из ~/.config/yazi/keymap.toml.
import io, os, re

SRC = os.path.expanduser("~/.config/yazi/keymap.toml")
OUT = os.path.expanduser("~/yazi-keys-ru.md")

src = io.open(SRC, encoding="utf-8").read()


def layer_items(layer):
    """[(on, run, desc)] для указанного слоя."""
    block = re.search(rf"\[{layer}\]\s*prepend_keymap = \[(.*?)\n\]", src, re.S)
    if not block:
        return []
    items = []
    for m in re.finditer(r'\{\s*on = (.+?),\s*run = (.+?),\s*desc = "(.*?)"\s*\}', block.group(1)):
        items.append((m.group(1).strip(), m.group(2).strip(), m.group(3)))
    return items


def key_name(on):
    s = on.strip()
    if s.startswith("["):
        keys = re.findall(r'"([^"]+)"', s)
        return " → ".join(keys)
    return re.findall(r'"([^"]+)"', s)[0]


mgr = {key_name(on): desc for on, run, desc in layer_items("mgr")}

CATS = [
    ("Навигация по списку", ["j", "k", "<Down>", "<Up>", "<C-u>", "<C-d>", "<C-b>", "<C-f>",
                             "g → g", "G", "<Home>", "<End>", "<PageUp>", "<PageDown>",
                             "<S-PageUp>", "<S-PageDown>"]),
    ("Вход и выход", ["l", "<Right>", "h", "<Left>", "H", "L", "J", "K", "q", "Q", "<C-c>", "<Esc>", "<C-[>", "<C-z>"]),
    ("Открытие файлов", ["o", "O", "<Enter>", "<S-Enter>", "<Tab>"]),
    ("Копирование и перенос", ["y", "x", "p", "P", "Y", "X", "-", "_", "<C-->"]),
    ("Копировать в системный буфер", ["c → c", "c → C", "c → d", "c → D", "c → f", "c → n"]),
    ("Создать, переименовать, удалить", ["a", "A", "r", "d", "D"]),
    ("Выделение нескольких файлов", ["<Space>", "<C-a>", "<C-r>", "v", "V"]),
    ("Вид списка и сортировка", ["m → s", "m → p", "m → b", "m → m", "m → o", "m → n",
                                 ", → m", ", → M", ", → b", ", → B", ", → e", ", → E",
                                 ", → a", ", → A", ", → n", ", → N", ", → s", ", → S", ", → r"]),
    ("Переходы (g…)", ["g → h", "g → c", "g → d", "g → t", "g → <Space>", "g → f"]),
    ("Вкладки", ["t → t", "t → r", "<Tab>", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                 "[", "]", "{", "}"]),
    ("Поиск и фильтр", ["f", "/", "?", "n", "N", "s", "S", "z", "Z", "<C-s>"]),
    ("Задачи, справка, прочее", ["w", "~", "<F1>", ";", ":", "<C-q>"]),
]

lines = ["# Клавиши yazi (русский справочник)", "",
         "Собрано из рабочего файла настроек `~/.config/yazi/keymap.toml`.", ""]
unknown = set(mgr)
for title, keys in CATS:
    rows = [(k, mgr[k]) for k in keys if k in mgr]
    unknown -= set(keys)
    if not rows:
        continue
    lines.append(f"## {title}")
    lines.append("")
    for k, d in rows:
        lines.append(f"- `{k}` — {d}")
    lines.append("")

if unknown:
    lines.append("## Прочее (файловый список)")
    lines.append("")
    for k in sorted(unknown):
        lines.append(f"- `{k}` — {mgr[k]}")
    lines.append("")

# прочие слои
for layer, title in [("tasks", "Список задач (w)"), ("spot", "Информация о файле (<Tab>)"),
                     ("pick", "Выбор программы (O)"), ("input", "Ввод текста (a/r/;)"),
                     ("confirm", "Подтверждение (d)"), ("cmp", "Автодополнение"),
                     ("help", "Справка (~)")]:
    items = layer_items(layer)
    if not items:
        continue
    lines.append(f"## Слой: {title}")
    lines.append("")
    for on, run, desc in items:
        lines.append(f"- `{key_name(on)}` — {desc}")
    lines.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(lines))
print(f"   записано: {OUT} ({len(lines)} строк)")
print("   разделов:", sum(1 for l in lines if l.startswith("## ")))
