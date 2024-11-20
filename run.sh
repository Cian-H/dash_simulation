#!/usr/bin/env bash

trap "/usr/bin/env rm -r ./cache/live/*" EXIT
# parallel --line-buffer ::: "panel serve ./dash_simulation/app.py --show" "./simulate_printer.nu"
parallel --line-buffer ::: "python -m dash_simulation" "./simulate_printer.nu"
