#!/bin/bash

if [ "$(uname)" == "Darwin" ]; then
    echo "Running on MacOS"
else
    echo "This script is for MacOS only"
    exit 1
fi

# Check for Python
if command -v python3 &>/dev/null; then
    echo "Python is installed"
else
    echo "Python is not installed"
    exit 1
fi

# Check for MySQL
if command -v mysql &>/dev/null; then
    echo "MySQL is installed"
else
    # Additional check for Homebrew MySQL path
    if [ -x "/usr/local/mysql/bin/mysql" ] || [ -x "/opt/homebrew/bin/mysql" ]; then
        echo "MySQL is installed but not in PATH"
    else
        echo "MySQL is not installed"
        exit 1
    fi
fi

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r source/requirements.txt --no-cache
python3 setup/reset_db.py