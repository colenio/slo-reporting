#!/bin/sh
set -e

if [ $# -eq 0 ]; then
    python main.py
fi

exec "$@"
