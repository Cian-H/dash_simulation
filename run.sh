#!/usr/bin/env bash

trap "/usr/bin/env rm -r ./layers/* && /usr/bin/env rm -r ./cache/live/*" EXIT
parallel --line-buffer ::: "python -m dash_simulation" "./simulate_printer.nu"
