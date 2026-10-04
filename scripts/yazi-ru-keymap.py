#!/usr/bin/env python3
# yazi-ru-keymap.py — русские подсказки для yazi.
#
# Что делает: читает keymap по умолчанию (из поставки yazi) и создаёт
# ~/.config/yazi/keymap.toml, где через prepend_keymap подкладываются ТЕ ЖЕ
# клавиши и ТЕ ЖЕ действия, но с русскими описаниями. Поведение не меняется —
# меняется только текст подсказок (то, что всплывает при нажатии c / g / m / , / t).
#
# Использование:
#   ./yazi-ru-keymap.py                  # взять keymap у установленного yazi, если удастся
#   ./yazi-ru-keymap.py /путь/keymap-default.toml
#
# Если новая версия yazi добавит подсказки — скрипт скажет, каких переводов не хватает,
# и оставит их на английском (файл не сломается).
import io, os, re, shutil, subprocess, sys

HOME = os.path.expanduser("~")
OUT_DIR = os.path.join(HOME, ".config", "yazi")
OUT = os.path.join(OUT_DIR, "keymap.toml")

RU = {
    "Exit visual mode, clear selection, or cancel search": "Выйти из выделения, снять выделение или отменить поиск",
    "Quit the process": "Выйти из программы",
    "Quit without outputting cwd-file": "Выйти, не записывая файл каталога",
    "Close the current tab, or quit if it's last": "Закрыть вкладку (если последняя — выйти)",
    "Suspend the process": "Приостановить и уйти в фон",
    "Previous file": "Предыдущий файл",
    "Next file": "Следующий файл",
    "Go to top": "В начало списка",
    "Go to bottom": "В конец списка",
    "Move cursor up half page": "Вверх на пол-экрана",
    "Move cursor down half page": "Вниз на пол-экрана",
    "Move cursor up one page": "Вверх на экран",
    "Move cursor down one page": "Вниз на экран",
    "Back to the parent directory": "В родительский каталог",
    "Enter the child directory": "Войти в каталог",
    "Back to previous directory": "Назад в прошлый каталог",
    "Forward to next directory": "Вперёд в следующий каталог",
    "Toggle the current selection state": "Выделить или снять выделение",
    "Select all files": "Выделить все файлы",
    "Invert selection of all files": "Инвертировать выделение",
    "Enter visual mode (selection mode)": "Режим выделения (выделять)",
    "Enter visual mode (unset mode)": "Режим выделения (снимать)",
    "Seek up 5 units in the preview": "Прокрутить превью вверх",
    "Seek down 5 units in the preview": "Прокрутить превью вниз",
    "Spot hovered file": "Информация о файле",
    "Open selected files": "Открыть выбранные файлы",
    "Open selected files interactively": "Открыть (выбор программы)",
    "Yank selected files (copy)": "Копировать (в буфер yazi)",
    "Yank selected files (cut)": "Вырезать (перенос)",
    "Paste yanked files": "Вставить",
    "Paste yanked files (overwrite if the destination exists)": "Вставить с перезаписью",
    "Symlink the absolute path of yanked files": "Символическая ссылка (абсолютный путь)",
    "Symlink the relative path of yanked files": "Символическая ссылка (относительный путь)",
    "Hardlink yanked files": "Жёсткая ссылка",
    "Cancel the yank status": "Снять пометку копирования",
    "Trash selected files": "Удалить в корзину",
    "Permanently delete selected files": "Удалить навсегда",
    "Create a file (ends with / for directories)": "Создать файл (с / на конце — каталог)",
    "Bulk create files": "Создать несколько файлов",
    "Rename selected file(s)": "Переименовать",
    "Run a shell command": "Выполнить команду оболочки",
    "Run a shell command (block until finishes)": "Выполнить команду и дождаться",
    "Toggle the visibility of hidden files": "Показать или скрыть скрытые файлы",
    "Search files by name via fd": "Поиск по имени (fd)",
    "Search files by content via ripgrep": "Поиск по содержимому (ripgrep)",
    "Cancel the ongoing search": "Отменить поиск",
    "Jump to a file/directory via fzf": "Перейти к файлу (fzf)",
    "Jump to a directory via zoxide": "Перейти в каталог (zoxide)",
    "Linemode: size": "Строка: размер",
    "Linemode: permissions": "Строка: права",
    "Linemode: btime": "Строка: время создания",
    "Linemode: mtime": "Строка: время изменения",
    "Linemode: owner": "Строка: владелец",
    "Linemode: none": "Строка: без доп. столбца",
    "Copy file path": "Копировать путь файла",
    "Copy file URL": "Копировать URL файла",
    "Copy directory path": "Копировать путь каталога",
    "Copy directory URL": "Копировать URL каталога",
    "Copy filename": "Копировать имя файла",
    "Copy filename without extension": "Копировать имя без расширения",
    "Filter files": "Фильтр файлов",
    "Find next file": "Искать следующий",
    "Find previous file": "Искать предыдущий",
    "Next found": "Следующее совпадение",
    "Previous found": "Предыдущее совпадение",
    "Sort by modified time": "Сортировка: время изменения",
    "Sort by modified time (reverse)": "Время изменения (обратно)",
    "Sort by birth time": "Сортировка: время создания",
    "Sort by birth time (reverse)": "Время создания (обратно)",
    "Sort by extension": "Сортировка: расширение",
    "Sort by extension (reverse)": "Расширение (обратно)",
    "Sort alphabetically": "Сортировка: по алфавиту",
    "Sort alphabetically (reverse)": "По алфавиту (обратно)",
    "Sort naturally": "Сортировка: естественная",
    "Sort naturally (reverse)": "Естественная (обратно)",
    "Sort by size": "Сортировка: размер",
    "Sort by size (reverse)": "Размер (обратно)",
    "Sort randomly": "Сортировка: случайная",
    "Go home": "Домой",
    "Go to ~/.config": "В ~/.config",
    "Go to ~/Downloads": "В ~/Downloads",
    "Go to trash bin": "В корзину",
    "Jump interactively": "Перейти (ввести путь)",
    "Follow hovered symlink": "Перейти по символической ссылке",
    "Create a new tab in CWD": "Новая вкладка в этом каталоге",
    "Rename current tab": "Переименовать вкладку",
    "Switch to previous tab": "Предыдущая вкладка",
    "Switch to next tab": "Следующая вкладка",
    "Swap current tab with previous tab": "Поменять местами с предыдущей",
    "Swap current tab with next tab": "Поменять местами со следующей",
    "Show task manager": "Список задач",
    "Open help": "Справка",
    "Close task manager": "Закрыть список задач",
    "Previous task": "Предыдущая задача",
    "Next task": "Следующая задача",
    "Inspect the task": "Подробнее о задаче",
    "Cancel the task": "Отменить задачу",
    "Close the spot": "Закрыть информацию",
    "Previous line": "Строка вверх",
    "Next line": "Строка вниз",
    "Swipe to previous file": "Пролистать к прошлому файлу",
    "Swipe to next file": "Пролистать к следующему файлу",
    "Copy selected cell": "Копировать выделенную ячейку",
    "Cancel pick": "Отменить выбор",
    "Submit the pick": "Подтвердить выбор",
    "Previous option": "Предыдущий вариант",
    "Next option": "Следующий вариант",
    "Cancel input": "Отменить ввод",
    "Submit input": "Подтвердить ввод",
    "Back to normal mode, or cancel input": "Обычный режим или отменить ввод",
    "Enter insert mode": "Режим вставки",
    "Move to the BOL, and enter insert mode": "В начало строки и режим вставки",
    "Enter append mode": "Режим добавления",
    "Move to the EOL, and enter append mode": "В конец строки и режим добавления",
    "Enter visual mode": "Режим выделения",
    "Replace a single character": "Заменить символ",
    "Select from BOL to EOL": "Выделить строку",
    "Select from EOL to BOL": "Выделить строку в обратную сторону",
    "Move back a character": "Символ влево",
    "Move forward a character": "Символ вправо",
    "Move back to the start of the current or previous word": "Слово назад",
    "Move back to the start of the current or previous WORD": "СЛОВО назад",
    "Move forward to the start of the next word": "Слово вперёд",
    "Move forward to the start of the next WORD": "СЛОВО вперёд",
    "Move forward to the end of the current or next word": "К концу слова",
    "Move forward to the end of the current or next WORD": "К концу СЛОВА",
    "Move to the BOL": "В начало строки",
    "Move to the EOL": "В конец строки",
    "Move to the first non-whitespace character": "К первому непробельному символу",
    "Delete the character before the cursor": "Удалить символ перед курсором",
    "Delete the character under the cursor": "Удалить символ под курсором",
    "Kill backwards to the BOL": "Удалить до начала строки",
    "Kill forwards to the EOL": "Удалить до конца строки",
    "Kill backwards to the start of the current word": "Удалить до начала слова",
    "Kill forwards to the end of the current word": "Удалить до конца слова",
    "Cut selected characters": "Вырезать выделенное",
    "Cut until EOL": "Вырезать до конца строки",
    "Cut selected characters, and enter insert mode": "Вырезать выделенное и в режим вставки",
    "Cut until EOL, and enter insert mode": "Вырезать до конца строки и в режим вставки",
    "Cut current character, and enter insert mode": "Вырезать символ и в режим вставки",
    "Cut from BOL until EOL, and enter insert mode": "Вырезать строку и в режим вставки",
    "Cut current character": "Вырезать символ",
    "Copy selected characters": "Копировать выделенное",
    "Paste copied characters after the cursor": "Вставить после курсора",
    "Paste copied characters before the cursor": "Вставить перед курсором",
    "Undo, or lowercase if in visual mode": "Отменить или в нижний регистр",
    "Uppercase": "В верхний регистр",
    "Redo the last operation": "Повторить отменённое",
    "Recall previous input": "Прошлый ввод",
    "Recall next input": "Следующий ввод",
    "Cancel the confirm": "Отменить",
    "Submit the confirm": "Подтвердить",
    "Cancel completion": "Отменить автодополнение",
    "Submit the completion": "Подтвердить автодополнение",
    "Complete and submit the input": "Дополнить и подтвердить",
    "Previous item": "Предыдущий пункт",
    "Next item": "Следующий пункт",
    "Enter normal mode, or hide help menu": "Обычный режим или скрыть справку",
    "Close help menu": "Закрыть справку",
    "Close help menu and run selected action(s)": "Закрыть справку и выполнить действие",
}
# вкладки tab 1..9 нумеруем программно
for _n, _w in enumerate(["первую", "вторую", "третью", "четвёртую", "пятую",
                         "шестую", "седьмую", "восьмую", "девятую"], 1):
    RU[f"Switch to {['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth'][_n-1]} tab"] = f"На {_n}-ю вкладку"


# Короткие варианты: длинные подписи обрезаются в узких колонках всплывающего меню,
# поэтому самые длинные подсказки сокращаем (смысл сохраняется).
SHORT = {
    "Выйти из выделения, снять выделение или отменить поиск": "Снять выделение / отменить поиск",
    "Символическая ссылка (относительный путь)": "Симлинк (относительный путь)",
    "Символическая ссылка (абсолютный путь)": "Симлинк (абсолютный путь)",
    "Закрыть вкладку (если последняя — выйти)": "Закрыть вкладку или выйти",
    "Создать файл (с / на конце — каталог)": "Создать файл (/ — каталог)",
    "Выйти, не записывая файл каталога": "Выйти без записи каталога",
    "Показать или скрыть скрытые файлы": "Показать скрытые файлы",
    "Перейти по символической ссылке": "Перейти по симлинку",
    "Поиск по содержимому (ripgrep)": "Поиск по тексту (rg)",
    "Поменять местами с предыдущей": "Поменять с предыдущей",
    "Поменять местами со следующей": "Поменять со следующей",
    "Выполнить команду и дождаться": "Команда с ожиданием",
    "Новая вкладка в этом каталоге": "Новая вкладка здесь",
    "Копировать имя без расширения": "Имя без расширения",
    "Инвертировать выделение": "Инвертировать выделение",
}
RU = {en: SHORT.get(ru, ru) for en, ru in RU.items()}


def default_keymap_source():
    """Где взять keymap по умолчанию: аргумент → кэш в домашнем каталоге."""
    if len(sys.argv) > 1:
        return sys.argv[1]
    for p in (os.path.join(HOME, "keymap-default.toml"), "/tmp/keymap.toml"):
        if os.path.exists(p):
            return p
    sys.exit("укажите путь к keymap-default.toml (из исходников yazi)")


def main():
    src_path = default_keymap_source()
    src = io.open(src_path, encoding="utf-8").read()

    layers, layer = {}, None
    for ln in src.splitlines():
        m = re.match(r"\s*\[([a-z]+)\]\s*$", ln)
        if m:
            layer = m.group(1); layers.setdefault(layer, []); continue
        m = re.search(r'\{\s*on = (.+?),\s*run = (.+?),\s*desc = "(.*?)"\s*\}', ln)
        if m and layer:
            layers[layer].append((m.group(1).strip(), m.group(2).strip(), m.group(3)))

    missing, out = [], []
    out.append("# Русские подсказки yazi. Сгенерировано yazi-ru-keymap.py\n")
    out.append("# Клавиши и действия скопированы из keymap по умолчанию без изменений —\n")
    out.append("# переведены только описания, которые всплывают в подсказках.\n")
    out.append("# Убрать русификацию: удалить этот файл, вернуть английский — вернуть из бэкапа.\n")
    for lay, rows in layers.items():
        out.append(f"\n[{lay}]\nprepend_keymap = [\n")
        for on, run, desc in rows:
            ru = RU.get(desc)
            if ru is None:
                missing.append(desc)
                continue
            out.append(f'  {{ on = {on}, run = {run}, desc = "{ru}" }},\n')
        out.append("]\n")

    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(OUT):
        shutil.copy2(OUT, OUT + ".bak-before-ru")
    io.open(OUT, "w", encoding="utf-8").write("".join(out))
    print(f"   записано: {OUT}")
    print(f"   слоёв: {len(layers)}, переведено описаний: {sum(1 for l in layers.values() for r in l if r[2] in RU)}")
    if missing:
        print("   без перевода (остались английскими):")
        for d in dict.fromkeys(missing):
            print("      -", d)

    v = subprocess.run(["yazi", "--version"], capture_output=True, text=True).stdout
    print("   версия yazi:", " | ".join(l.strip() for l in v.splitlines() if l.strip())[:80])


if __name__ == "__main__":
    main()
