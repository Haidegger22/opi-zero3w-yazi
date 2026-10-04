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
