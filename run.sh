#!/usr/bin/env bash

parallel --line-buffer ::: "python -m dash_simulation" "./simulate_printer.nu"
