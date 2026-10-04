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
