# Установка yazi на Orange Pi Zero 3W

Пошагово, копипастой. Понадобится `sudo` (на этой плате он без пароля: `sudo -n`).

## Шаг 1. Что нужно

- Orange Pi Zero 3W, arm64, Debian 13 «Trixie», рабочий стол MATE/X11, экран 1024×600;
- терминал: **xterm** (для пиксельных превью) — на этой плате уже установлен, проверьте `xterm -version`;
- `sudo` и выход в интернет. Если наружу пускает только прокси, добавляйте `PROXY=…` в команды ниже
  (прокси нужен **только** для https; если направить через него http-зеркало Debian, оно ответит 502).

Проверка:

```bash
dpkg --print-architecture          # arm64
xterm -version                     # XTerm(398)
command -v sudo gpg curl           # всё должно быть найдено
```

## Шаг 2. yazi из официального репозитория (готовые сборки arm64)

```bash
install -m755 scripts/install-yazi.sh ~/.local/bin/
PROXY=http://127.0.0.1:9697 ~/.local/bin/install-yazi.sh    # без прокси — просто без PROXY
```

Скрипт кладёт ключ в `/usr/share/keyrings/yazi-keyring.gpg`, добавляет
`/etc/apt/sources.list.d/yazi.list`, ставит `yazi`, `chafa`, `fzf`, `zoxide`, `xclip`.
В репозиториях Debian самого yazi нет — только в этом источнике.

Ожидаемый результат: `yazi --version` → `Version: 26.9.1` (или новее), в списке есть `/usr/bin/ya`.

## Шаг 3. Проверка: каким способом будут показываться картинки

```bash
install -m755 scripts/yazi-verify.sh ~/.local/bin/
~/.local/bin/yazi-verify.sh
```

Смотрите строку `Drivers.matches`:

- `Sixel` — родной sixel терминала: пиксельные картинки (наш путь через xterm);
- `X11` — потребуется Überzug++ (`ueberzugpp`), которого в Debian нет;
- `Chafa` — ASCII-графика через chafa ≥ 1.16.

Важно: проверять **внутри того терминала**, где нужны превью — выбор драйвера зависит от `TERM` и `DISPLAY`.

## Шаг 4. Пиксельные превью: xterm + sixel (рекомендуется)

```bash
install -m755 scripts/yazi-sixel ~/.local/bin/
yazi-sixel ~                 # откроется xterm с yazi
```

Внутри выделите картинку — она покажется пиксельно. Проверка драйвера: в этом окне наберите
`ya env | grep -E 'sixel|Drivers'` → должно быть `sixel: true` и `Drivers.matches: Sixel`.

Почему так: `xterm -ti vt340` поддерживает sixel, и yazi видит это сам. `DISPLAY` сохраняется,
поэтому открытие файлов внешними программами и буфер обмена внутри yazi работают.

## Шаг 5. Запасной путь: картинки символами в любом терминале

Нужен, если xterm не подходит (например, вы хотите остаться в терминале MATE).

```bash
install -m755 scripts/build-chafa.sh ~/.local/bin/
PROXY=http://127.0.0.1:9697 ~/.local/bin/build-chafa.sh     # соберёт chafa 1.18.3 в /usr/local
install -m755 scripts/yazi-img ~/.local/bin/
yazi-img                     # yazi с превью картинок символами
```

Почему нужна сборка: в Debian 13 chafa 1.14.5, а yazi требует ≥ 1.16. Если в архиве нет `configure`,
скрипт сгенерирует его через `autogen.sh` — для этого нужен пакет **libtool** (`sudo apt install libtool
libtool-bin`), иначе сборка падает на `LT_INIT`.

Ограничение этого режима: `DISPLAY` убирается намеренно, поэтому внутри yazi не работают внешние
открыватели файлов и системный буфер обмена.

## Шаг 6. Русские подсказки

```bash
install -m755 scripts/yazi-ru-keymap.py ~/.local/bin/
curl -fLs --proxy http://127.0.0.1:9697 \
  https://raw.githubusercontent.com/sxyazi/yazi/v26.9.1/yazi-config/preset/keymap-default.toml \
  -o ~/keymap-default.toml
~/.local/bin/yazi-ru-keymap.py ~/keymap-default.toml
```

Скрипт создаёт `~/.config/yazi/keymap.toml`: клавиши и действия копируются из штатного keymap
**без изменений**, подменяются только описания (в 26.9.1 — 254 штуки в 8 слоях). Если yazi обновится,
запустите скрипт с новым `keymap-default.toml` — он скажет, каких переводов не хватает.

Откат: удалить `~/.config/yazi/keymap.toml` (рядом останется `keymap.toml.bak-before-ru`).

## Шаг 7. Справочник клавиш (по-русски)

```bash
install -m755 scripts/yazi-keys-ru.py ~/.local/bin/
~/.local/bin/yazi-keys-ru.py         # соберёт ~/yazi-keys-ru.md из ваших настроек
```

## Шаг 8. Ярлык в карусели приложений (необязательно)

Если на рабочем столе есть карусель приложений (`~/.local/bin/app-carousel-v.py`, виджет MATE),
добавьте пункт в список `APPS`:

```python
("Yazi", "/usr/share/icons/Papirus/48x48/apps/system-file-manager.svg",
 HOME_DIR + "/.local/bin/yazi-sixel " + HOME_DIR),
```

Применить: закрыть текущий экземпляр виджета (`kill <pid>`) и запустить его снова
(`setsid nohup ~/.local/bin/app-carousel-v.py >/dev/null 2>&1 &`), затем проверить кадром экрана.
Команду в списке указывайте **абсолютным путём** — PATH сессии может не содержать `~/.local/bin`.

## Шаг 9. Автопроверка файловых операций (необязательно)

```bash
install -m755 scripts/yazi-ops-test.py ~/.local/bin/
python3 ~/.local/bin/yazi-ops-test.py
```

Скрипт прогоняет yazi в псевдотерминале и проверяет на диске: копирование в подкаталог, перенос,
удаление, переименование, копирование пути/имени/каталога в буфер.

## Важно

- **Буфер обмена.** yazi копирует путь через `xclip`, ему нужен `DISPLAY`. Работает в `yazi-sixel`
  и в обычном yazi; в `yazi-img` — нет. Содержимое буфера проверяйте, **пока yazi жив**.
- **Корзина.** `g t` — вход; выделить (`Space`, `Ctrl+a`) и **`D`** — удалить навсегда.
  Корзина стандартная: `~/.local/share/Trash/{files,info}`; снаружи чистится `gio trash --empty`.
- **Диалоги останутся английскими** (`Rename:`, `Trash 1 file?`) — локализации интерфейса у yazi нет.
- **`xterm -ti vt340`** нужен именно для sixel; без него картинок в xterm не будет.

## Откат

```bash
# настройки yazi
rm -f ~/.config/yazi/keymap.toml
# обёртки и скрипты
rm -f ~/.local/bin/{yazi-sixel,yazi-img,yazi-ru-keymap.py,yazi-keys-ru.py,yazi-verify.sh,yazi-ops-test.py}
# собранный chafa (системный из apt останется)
sudo -n rm -f /usr/local/bin/chafa
# сам yazi и его репозиторий
sudo -n apt-get remove -y yazi
sudo -n rm -f /etc/apt/sources.list.d/yazi.list /usr/share/keyrings/yazi-keyring.gpg
```

---

## Полный код файлов (установка без git)

Ниже — те же файлы целиком, если удобнее создавать их руками (например, без git).
Копируйте блоки по порядку; делимитер `'FILE_EOF'` в кавычках обязателен.

### 1. Обёртка xterm + sixel: пиксельные превью картинок

```bash
mkdir -p $(dirname $HOME/.local/bin/yazi-sixel)
cat > $HOME/.local/bin/yazi-sixel << 'FILE_EOF'
#!/bin/bash
# yazi-sixel — запуск yazi в xterm с настоящими пиксельными превью картинок (sixel).
#
# Почему так. Терминал MATE (VTE) не умеет ни sixel, ни kitty-протокол, и yazi при
# заданном DISPLAY всегда уходит на драйвер «X11», который требует Überzug++.
# xterm же умеет sixel (в Debian собран с его поддержкой), и yazi это видит:
#   Emulator.probe: ... sixel: true, version: XTerm(398)
#   Adapter: Drivers.matches: Sixel
# Важное отличие от обёртки yazi-img (chafa без DISPLAY): здесь DISPLAY сохраняется,
# поэтому внутри yazi работают внешние открыватели файлов и буфер обмена (xclip).
#
# Требуется режим VT340 у xterm (xterm -ti vt340) — иначе sixel-запросы не поддерживаются
# и yazi покажет картинки блоками (chafa) либо ничего.
#
# Использование: yazi-sixel [каталог]
set -u
DIR="${1:-$PWD}"
exec xterm -ti vt340 -fa Monospace -fs 11 -geometry 110x32 -title "yazi (sixel)" \
     -e /usr/bin/yazi "$DIR"
FILE_EOF
chmod +x $HOME/.local/bin/yazi-sixel 2>/dev/null || true
```

### 2. Обёртка chafa без DISPLAY: превью символами в любом терминале

```bash
mkdir -p $(dirname $HOME/.local/bin/yazi-img)
cat > $HOME/.local/bin/yazi-img << 'FILE_EOF'
#!/bin/bash
# yazi-img — запуск yazi с работающим превью картинок в терминале MATE (VTE) на Zero 3W.
#
# Зачем обёртка. Терминал MATE — это VTE: ни sixel, ни kitty-протокола у него нет.
# yazi выбирает способ показа картинок так (yazi-adapter/src/drivers/drivers.rs):
#   1) встроенный протокол терминала — у VTE отсутствует;
#   2) если задан DISPLAY (X11) → драйвер «X11 / Window system», а он требует
#      установленный Überzug++ (ueberzugpp); без него панель превью просто пустая;
#   3) ASCII-графика через chafa — только если DISPLAY НЕ задан (и нет WAYLAND_DISPLAY).
# Поэтому здесь мы убираем DISPLAY у самого yazi: он уходит на chafa (>= 1.16, у нас 1.18.3).
#
# Что теряется: открытие файлов внешними программами и системный буфер обмена (xclip)
# внутри yazi без DISPLAY не работают. Нужны они — запускайте обычный `yazi`
# либо ставьте Überzug++ (тогда картинки будут настоящие, пиксельные).
#
# Использование: yazi-img [каталог]
exec env -u DISPLAY -u WAYLAND_DISPLAY -u XDG_SESSION_TYPE /usr/bin/yazi "$@"
FILE_EOF
chmod +x $HOME/.local/bin/yazi-img 2>/dev/null || true
```

### 3. Проверка: версии, драйвер превью, chafa, обёртки

```bash
mkdir -p $(dirname $HOME/.local/bin/yazi-verify.sh)
cat > $HOME/.local/bin/yazi-verify.sh << 'FILE_EOF'
#!/bin/bash
# yazi-verify.sh — что установлено и каким способом yazi будет показывать картинки.
# Запускать ВНУТРИ того терминала, где нужны превью: выбор драйвера зависит от $TERM и $DISPLAY.
set -u

echo "=== версии ==="
for c in yazi ya chafa fzf zoxide xclip; do
    v=$(command -v "$c" 2>/dev/null)
    printf '   %-7s %s\n' "$c" "${v:-НЕ УСТАНОВЛЕН}"
done
yazi --version 2>/dev/null | sed -n '2p' | sed 's/^/          /'
echo "   xterm: $(xterm -version 2>&1 | head -1)  (нужен для sixel-превью: xterm -ti vt340)"
echo "   chafa: $(chafa --version 2>&1 | head -1)  (yazi требует >= 1.16)"

echo
echo "=== как yazi видит этот терминал ==="
ENVINFO="$(ya env 2>/dev/null | grep -aE 'TERM |TERM_PROGRAM|Brand|Emulator.probe|Drivers.matches|dimension|DISPLAY|SESSION_TYPE')"
if [ -n "$ENVINFO" ]; then
    echo "$ENVINFO" | sed 's/^/   /' | cut -c1-200
else
    echo "   (данных нет — запустите этот скрипт В ТЕРМИНАЛЕ, а не из скрипта/крона:"
    echo "    выбор драйвера превью зависит от переменных TERM и DISPLAY конкретного окна)"
fi
cat <<'TXT'
   расшифровка строки Drivers.matches:
      Sixel  — родной sixel терминала (xterm -ti vt340): пиксельные картинки, DISPLAY цел   ← лучший случай
      X11    — нужен Überzug++ (ueberzugpp); если его нет, панель превью будет пустой
      Chafa  — ASCII-графика (нужен chafa >= 1.16); yazi выбирает её, только если DISPLAY не задан
      Kgp/Iip/Sixel (по бренду) — терминал с картинками из коробки (kitty, WezTerm, foot…)
TXT

echo
echo "=== обёртки (если установлены) ==="
for w in yazi-sixel yazi-img; do
    p="$(command -v "$w" 2>/dev/null)"
    printf '   %-11s %s\n' "$w" "${p:-нет}"
done

echo
echo "=== превью картинок: быстрый тест ==="
T="$(mktemp -d)"; printf 'файл\n' > "$T/1-текст.txt"
if command -v chafa >/dev/null && [ -n "${DISPLAY:-}" ]; then
    if chafa -f symbols --relative off --view-size 20x10 "$T/1-текст.txt" >/dev/null 2>&1; then
        echo "   chafa работает (флаги, которые использует yazi, приняты)"
    else
        echo "   chafa есть, но флаги не приняты — вероятно версия < 1.16 (соберите из исходников)"
    fi
fi
echo "   живую проверку смотрите так: запустите yazi, выделите картинку и посмотрите панель превью"
rm -rf "$T"
FILE_EOF
chmod +x $HOME/.local/bin/yazi-verify.sh 2>/dev/null || true
```

### 4. Установка yazi из официального репозитория (arm64)

```bash
mkdir -p $(dirname $HOME/.local/bin/install-yazi.sh)
cat > $HOME/.local/bin/install-yazi.sh << 'FILE_EOF'
#!/bin/bash
# install-yazi.sh — установка yazi на Debian 13 (arm64) с официального репозитория проекта.
#
# Что делает:
#   1) кладёт ключ репозитория yazi в /usr/share/keyrings
#   2) добавляет источник в /etc/apt/sources.list.d/yazi.list
#   3) ставит yazi (TUI + CLI ya) и полезные зависимости
#
# ВАЖНО про прокси. Если наружу пускает только прокси (обычный случай на плате без VPN),
# прокси нужен ТОЛЬКО для https (сайт репозитория yazi). Если направить через прокси ещё и
# http-зеркало Debian, оно ответит 502 Bad Gateway.
#
# Использование:
#   ./install-yazi.sh                                # без прокси
#   PROXY=http://127.0.0.1:9697 ./install-yazi.sh    # через прокси для https
set -u

PROXY="${PROXY:-}"
CURL_PROXY=(); APT_PROXY=()
if [ -n "$PROXY" ]; then
    CURL_PROXY=(--proxy "$PROXY")
    APT_PROXY=(-o "Acquire::https::Proxy=$PROXY" -o "Acquire::http::Proxy=false")
fi

KEY="$(mktemp /tmp/yazi-keyring.XXXXXX.gpg)"
echo "=== 1) ключ репозитория ==="
curl -fsSL "${CURL_PROXY[@]}" https://yazi-rs.github.io/builds/yazi-keyring.gpg -o "$KEY" \
  && echo "   ключ получен" || { echo "   не удалось получить ключ"; exit 1; }
gpg --show-keys --with-colons "$KEY" 2>/dev/null | awk -F: '/^pub/{print "   ключ: "$5}' | head -1
sudo -n install -m 0644 "$KEY" /usr/share/keyrings/yazi-keyring.gpg \
  && echo "   установлен в /usr/share/keyrings/yazi-keyring.gpg"

echo "=== 2) источник apt ==="
echo 'deb [signed-by=/usr/share/keyrings/yazi-keyring.gpg] https://yazi-rs.github.io/builds/ stable main' \
  | sudo -n tee /etc/apt/sources.list.d/yazi.list >/dev/null && echo "   /etc/apt/sources.list.d/yazi.list"

echo "=== 3) обновление индексов и установка ==="
sudo -n apt-get "${APT_PROXY[@]}" update 2>&1 | tail -2 | sed 's/^/   /'
sudo -n apt-get "${APT_PROXY[@]}" install -y yazi chafa fzf zoxide xclip 2>&1 | tail -4 | sed 's/^/   /'

echo "=== 4) результат ==="
for c in yazi ya chafa fzf zoxide xclip; do
    v=$(command -v "$c" 2>/dev/null)
    printf '   %-7s %s\n' "$c" "${v:-НЕ УСТАНОВЛЕН}"
done
yazi --version 2>/dev/null | sed -n '2p' | sed 's/^/          /'
echo "   дальше: scripts/yazi-verify.sh — покажет, каким способом будут показываться картинки"
FILE_EOF
chmod +x $HOME/.local/bin/install-yazi.sh 2>/dev/null || true
```

### 5. Сборка chafa >= 1.16 из исходников в /usr/local

```bash
mkdir -p $(dirname $HOME/.local/bin/build-chafa.sh)
cat > $HOME/.local/bin/build-chafa.sh << 'FILE_EOF'
#!/bin/bash
# build-chafa.sh — сборка chafa >= 1.16 из исходников в /usr/local.
#
# Зачем: yazi использует chafa как запасной способ показа картинок (ASCII-графика) и требует
# версию НЕ НИЖЕ 1.16. В Debian 13 (trixie) в репозитории только 1.14.5 — с ней запасной путь
# не работает, и панель превью остаётся пустой.
# Сборка ставится в /usr/local, системный /usr/bin/chafa не трогается (откат — удалить файл).
#
# Зависимости: gcc, make, pkg-config, autoconf, automake, libtool + libtool-bin,
# libglib2.0-dev, libfreetype-dev, libjpeg-dev, libwebp-dev, libtiff-dev.
# В архиве chafa нет готового ./configure — он генерируется через autogen.sh, а для этого
# нужен пакет libtool (без него падает на LT_INIT).
#
# Использование:
#   ./build-chafa.sh                                 # версия по умолчанию
#   VER=1.18.3 PROXY=http://127.0.0.1:9697 ./build-chafa.sh
set -u

VER="${VER:-1.18.3}"
PROXY="${PROXY:-}"
CURL_PROXY=(); [ -n "$PROXY" ] && CURL_PROXY=(--proxy "$PROXY")

echo "=== 1) инструменты сборки ==="
need=0
for c in gcc make pkg-config libtoolize; do
    if command -v "$c" >/dev/null; then printf '   %-11s %s\n' "$c" "$(command -v "$c")"
    else printf '   %-11s НЕТ (доставьте: sudo apt install libtool libtool-bin build-essential pkg-config)\n' "$c"; need=1; fi
done
[ "$need" = 1 ] && echo "   ВНИМАНИЕ: без отсутствующих инструментов сборка не пойдёт"

echo "=== 2) скачивание исходника chafa $VER ==="
SRC="$HOME/chafa-build"
mkdir -p "$SRC"; cd "$SRC"
curl -fLs --retry 2 "${CURL_PROXY[@]}" \
  "https://github.com/hpjansson/chafa/archive/refs/tags/$VER.tar.gz" -o "chafa-$VER.tar.gz" \
  && ls -la "chafa-$VER.tar.gz" | awk '{printf "   скачано: %.1f МБ\n", $5/1048576}'
rm -rf "chafa-$VER" && tar xzf "chafa-$VER.tar.gz" && cd "chafa-$VER"

echo "=== 3) подготовка (в архиве нет готового configure) ==="
if [ ! -x ./configure ]; then
    NOCONFIGURE=1 ./autogen.sh >/dev/null 2>&1 || autoreconf -i >/dev/null 2>&1
    [ -x ./configure ] || { echo "   ОШИБКА: configure не создан (обычно не хватает libtool)"; exit 1; }
fi
echo "   configure готов"

echo "=== 4) configure + сборка (4 потока) ==="
./configure --prefix=/usr/local --disable-static 2>&1 | tail -3 | sed 's/^/   /'
start=$(date +%s)
make -j4 2>&1 | tail -3 | sed 's/^/   /'
echo "   сборка заняла $(( $(date +%s) - start )) с"

echo "=== 5) установка ==="
sudo -n make install 2>&1 | tail -2 | sed 's/^/   /'
sudo -n ldconfig 2>/dev/null
hash -r 2>/dev/null

echo "=== 6) результат ==="
echo "   в PATH:    $(command -v chafa) — $(chafa --version 2>&1 | head -1)"
echo "   системный: /usr/bin/chafa — $(/usr/bin/chafa --version 2>&1 | head -1)"
echo "   флаги --probe/--passthrough (нужны yazi): $(chafa --help 2>&1 | grep -cE -- '--probe|--passthrough')"
FILE_EOF
chmod +x $HOME/.local/bin/build-chafa.sh 2>/dev/null || true
```

### 6. Русские подсказки: генератор ~/.config/yazi/keymap.toml

```bash
mkdir -p $(dirname $HOME/.local/bin/yazi-ru-keymap.py)
cat > $HOME/.local/bin/yazi-ru-keymap.py << 'FILE_EOF'
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
FILE_EOF
chmod +x $HOME/.local/bin/yazi-ru-keymap.py 2>/dev/null || true
```

### 7. Справочник клавиш по-русски из ваших настроек

```bash
mkdir -p $(dirname $HOME/.local/bin/yazi-keys-ru.py)
cat > $HOME/.local/bin/yazi-keys-ru.py << 'FILE_EOF'
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
FILE_EOF
chmod +x $HOME/.local/bin/yazi-keys-ru.py 2>/dev/null || true
```

### 8. Автопроверка файловых операций через псевдотерминал

```bash
mkdir -p $(dirname $HOME/.local/bin/yazi-ops-test.py)
cat > $HOME/.local/bin/yazi-ops-test.py << 'FILE_EOF'
#!/usr/bin/env python3
# yazi_ops_final.py — проверка всех файловых операций yazi (копирование, перенос, удаление,
# переименование, копирование пути) в псевдотерминале, с проверкой результата на диске.
import fcntl, os, pty, re, select, shutil, struct, subprocess, termios, time

D = os.path.join(os.path.expanduser("~"), "yazi-ops-test")
ERRLOG = "/tmp/yazi-pty-err.txt"
ENV = {**os.environ, "DISPLAY": ":0", "XAUTHORITY": os.path.expanduser("~/.Xauthority"),
       "TERM": "xterm-256color"}
COLS, ROWS = 120, 34

def start():
    pid, fd = pty.fork()
    if pid == 0:
        os.makedirs(D, exist_ok=True); os.chdir(D)
        os.execvpe("bash", ["bash", "-c", f'exec yazi "{D}" 2>{ERRLOG}'], ENV)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
    return pid, fd

def drain(fd, seconds):
    buf, end = b"", time.time() + seconds
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try: buf += os.read(fd, 65536)
            except OSError: break
    return buf.decode(errors="replace")

def clipboard():
    return subprocess.run(["xclip", "-o", "-selection", "clipboard"], env=ENV,
                          capture_output=True, text=True).stdout.strip()

def run(keys, clipboard_after=False):
    pid, fd = start()
    time.sleep(3.5); drain(fd, 1.0)
    for k in keys:
        os.write(fd, k); time.sleep(0.9)
    cl = clipboard() if clipboard_after else None
    drain(fd, 0.8)
    os.write(fd, b"q"); time.sleep(0.7)
    try: os.kill(pid, 9); os.waitpid(pid, 0)
    except Exception: pass
    return cl

def prepare():
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D + "/dst")
    open(D + "/a-note.txt", "w").write("файл A\n")
    open(D + "/b-note.txt", "w").write("файл B\n")
    open(D + "/c-del.txt", "w").write("файл C\n")

J, K, L, ENTER = b"j", b"k", b"l", b"\r"

print("=== КОПИРОВАНИЕ ФАЙЛА В ПОДКАТАЛОГ: j (файл) → y → k (папка) → l → p ===")
prepare()
run([J, b"y", K, L, b"p"])
print("   dst:", sorted(os.listdir(D + "/dst")), "| рядом с папкой:", sorted(os.listdir(D)))

print("=== ПЕРЕНОС (вырезать/вставить): j j → x → k k → l → p ===")
prepare()
run([J, J, b"x", K, K, L, b"p"])
print("   dst:", sorted(os.listdir(D + "/dst")), "| рядом с папкой:", sorted(os.listdir(D)))

print("=== УДАЛЕНИЕ В КОРЗИНУ: j j j → d ===")
prepare()
run([J, J, J, b"d"])
print("   рядом с папкой:", sorted(os.listdir(D)))

print("=== ПЕРЕИМЕНОВАНИЕ: j → r → добавить «-2» → Enter ===")
prepare()
run([J, b"r", b"-2", ENTER])
print("   рядом с папкой:", sorted(os.listdir(D)))

print("=== КОПИРОВАНИЕ ПУТИ В БУФЕР: j → c → c ===")
prepare()
cl = run([J, b"c", b"c"], clipboard_after=True)
print("   буфер обмена:", repr(cl))

print("=== КОПИРОВАНИЕ ИМЕНИ ФАЙЛА: j → c → f ===")
print("   буфер обмена:", repr(run([J, b"c", b"f"], clipboard_after=True)))

print("=== ПУТЬ КАТАЛОГА: j j (папка) → c → d ===")
# порядок: dst, a-note.txt, b-note.txt, c-del.txt → j j = a-note? проверим оба варианта
print("   буфер обмена:", repr(run([K, b"c", b"d"], clipboard_after=True)))
FILE_EOF
chmod +x $HOME/.local/bin/yazi-ops-test.py 2>/dev/null || true
```

