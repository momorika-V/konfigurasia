#!/bin/bash
python3 src/main.py
set -e
cd "$(dirname "$0")"
python3 src/main.py "$@"