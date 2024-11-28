#!/usr/bin/env bash

trap "/usr/bin/env rm -r ./layers/* && /usr/bin/env rm -r ./cache/live/*" EXIT
parallel --line-buffer ::: "panel serve dash_simulation/app.py --port 4242 --allow-websocket-origin=127.0.0.1:4242" "./simulate_printer.nu" "sleep 10 && electron http://127.0.0.1:4242/app"
