#!/bin/bash

set -e  # Exit on error
export RUNTIME_ENV="${RUNTIME_ENV:-DEV}"

export PYTHONPATH=./src
python src/task_01/main.py
