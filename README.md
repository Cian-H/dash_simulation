# Overview

A simulation of a dashboard in a live printing environment. Intended as a testbed/demonstrator
for developing in-situ data visualization tools. Intended to iron out any issues in the
event loop before pushing changes upstream to MTPy and then testing the new dashboard
friendly implementation here.

# Requirements
- Python >=3.11,<3.13
- Poetry >=1.0
- Nushell >=0.100.0
- GNU Parallel >2024 (on unix systems)

These requirements are automatically provided by the nix devenv, where that is an option.

# Quickstart

- Linux/MacOS:
```bash
./run.sh
```

- Windows:
```cmd
./run.ps1
```

- Nix:
```bash
devenv tasks run simulation:start
```
