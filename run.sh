#!/usr/bin/env bash
# Rebuild data and (re)start the Fleet Yearbook on :4251 in the background (nohup).
cd "$(dirname "$0")"
PORT=${PORT:-4251}
nice python3 build.py >/dev/null || { echo "build failed"; exit 1; }
if [ -f data/server.pid ] && kill -0 "$(cat data/server.pid)" 2>/dev/null; then kill "$(cat data/server.pid)"; sleep 1; fi
PORT=$PORT nohup nice python3 server.py > data/server.log 2>&1 &
echo $! > data/server.pid
sleep 1
curl -fsS "http://127.0.0.1:$PORT/healthz" >/dev/null && echo "Fleet Yearbook up: http://127.0.0.1:$PORT/"
