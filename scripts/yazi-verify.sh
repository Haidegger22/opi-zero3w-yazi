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
