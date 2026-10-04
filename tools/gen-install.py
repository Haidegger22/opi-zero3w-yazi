#!/usr/bin/env python3
# gen-install.py — дописывает в INSTALL.md раздел «Полный код файлов (установка без git)».
# Запускать из корня репозитория. Текстовые шаги в INSTALL.md пишутся ДО запуска:
# генератор дописывает раздел в конец файла (маркер «## Полный код файлов»).
import io, os, sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # корень репозитория
INSTALL = os.path.join(D, "INSTALL.md")
MARKER = "## Полный код файлов (установка без git)"

# (путь в репо, куда ставить у читателя, подпись)
FILES = [
    ("scripts/yazi-sixel",        "$HOME/.local/bin/yazi-sixel",        "Обёртка xterm + sixel: пиксельные превью картинок"),
    ("scripts/yazi-img",          "$HOME/.local/bin/yazi-img",          "Обёртка chafa без DISPLAY: превью символами в любом терминале"),
    ("scripts/yazi-verify.sh",    "$HOME/.local/bin/yazi-verify.sh",    "Проверка: версии, драйвер превью, chafa, обёртки"),
    ("scripts/install-yazi.sh",   "$HOME/.local/bin/install-yazi.sh",   "Установка yazi из официального репозитория (arm64)"),
    ("scripts/build-chafa.sh",    "$HOME/.local/bin/build-chafa.sh",    "Сборка chafa >= 1.16 из исходников в /usr/local"),
    ("scripts/yazi-ru-keymap.py", "$HOME/.local/bin/yazi-ru-keymap.py", "Русские подсказки: генератор ~/.config/yazi/keymap.toml"),
    ("scripts/yazi-keys-ru.py",   "$HOME/.local/bin/yazi-keys-ru.py",   "Справочник клавиш по-русски из ваших настроек"),
    ("scripts/yazi-ops-test.py",  "$HOME/.local/bin/yazi-ops-test.py",  "Автопроверка файловых операций через псевдотерминал"),
]


def rd(p):
    with io.open(p, encoding="utf-8") as fh:
        return fh.read()


def main():
    h = rd(INSTALL)
    if MARKER not in h:
        sys.exit("в INSTALL.md нет маркера: " + MARKER)
    h = h.split(MARKER)[0].rstrip() + "\n\n" + MARKER + "\n\n"
    h += ("Ниже — те же файлы целиком, если удобнее создавать их руками (например, без git).\n"
          "Копируйте блоки по порядку; делимитер `'FILE_EOF'` в кавычках обязателен.\n\n")
    for i, (src, dst, title) in enumerate(FILES, 1):
        h += "### %d. %s\n\n" % (i, title)
        h += ("```bash\nmkdir -p $(dirname %s)\ncat > %s << 'FILE_EOF'\n%sFILE_EOF\n"
              "chmod +x %s 2>/dev/null || true\n```\n\n" % (dst, dst, rd(os.path.join(D, src)), dst))
    with io.open(INSTALL, "w", encoding="utf-8") as fh:
        fh.write(h)
    print("INSTALL.md: строк=%d, блоков FILE_EOF=%d (ожидалось %d)" % (
        h.count("\n"), h.count("FILE_EOF"), len(FILES) * 2))


if __name__ == "__main__":
    main()
