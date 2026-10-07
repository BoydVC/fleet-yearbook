#!/usr/bin/env bash
# Usage: ./screenshot.sh NAME W H [query] [url]
cd "$(dirname "$0")"
NAME=$1; W=${2:-1920}; HH=${3:-1080}; Q=${4:-}; URL=${5:-"http://127.0.0.1:4251/?$Q"}
D=/tmp/fy-chrome-$$
nice google-chrome --headless=new --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=$W,$HH --virtual-time-budget=${BUDGET:-3000} --user-data-dir=$D --screenshot="screenshots/$NAME.png" "$URL" >/dev/null 2>&1
rm -rf $D; ls -la "screenshots/$NAME.png" | awk '{print $5, $9}'
