#!/usr/bin/env bash

MODULE_NAME=app.main

export PYTHONPATH=$PYTHONPATH:/app

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
LOG_LEVEL=${LOG_LEVEL:-info}

case "$1" in
  "start")
    echo "Running migrations..."
    alembic upgrade head

    echo "Starting web server with uvicorn..."
    python -m ${MODULE_NAME} --host ${HOST} --port ${PORT} --log-level ${LOG_LEVEL} --proxy-headers
    ;;
  "migrate")
    echo "Running migrations..."
    alembic upgrade head
    ;;
  *)
    exec ${@}
    ;;
esac
