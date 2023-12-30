#!/bin/sh
set -e

if [ $# -eq 0 ]; then
    uvicorn --host 0.0.0.0 --port 8000 main:app
fi

exec "$@"
