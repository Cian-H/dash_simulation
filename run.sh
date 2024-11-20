#!/usr/bin/env bash

trap "/usr/bin/env rm -r ./layers/* && /usr/bin/env rm -r ./cache/live/*" EXIT
parallel --line-buffer ::: "panel serve --show ./dash_simulation/app.py" "./simulate_printer.nu"
