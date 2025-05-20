#!/bin/bash

set -e

ENV_FILE=".env"
VENV_DIR=".venv"
REQ_FILE="requirements.txt"
PROJECT_ROOT="$(pwd)"
SOCIAL_DIR="$PROJECT_ROOT/social_collector"

# Recreate venv if pip is broken or missing
if [ ! -x "$VENV_DIR/bin/pip" ]; then
    echo "Fixing or creating virtual environment..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    python -m ensurepip --upgrade
    pip install --upgrade pip
else
    source "$VENV_DIR/bin/activate"
fi

# Install dependencies
if [ -f "$REQ_FILE" ]; then
    echo "Installing/updating dependencies from $REQ_FILE"
    pip install -r "$REQ_FILE"
fi

# .env S_SERVER updater
modify_server() {
    local new_value=$1
    if grep -q "^S_SERVER=" "$ENV_FILE"; then
        sed -i "s|^S_SERVER=.*|S_SERVER=$new_value|" "$ENV_FILE"
    else
        echo "S_SERVER=$new_value" >> "$ENV_FILE"
    fi
}

# Fail if .env is missing
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found!"
    deactivate
    exit 1
fi

# Update S_SERVER based on PRODUCTION flag
PROD_VALUE=$(grep "^PRODUCTION=" "$ENV_FILE" | cut -d '=' -f2 | tr -d "'\"")
if [ "$PROD_VALUE" == "1" ]; then
    modify_server "https://orion.genesistechnologies.org:443"
else
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    modify_server "http://$LOCAL_IP:8080"
fi

# Run setup.py and main.py if build -social is requested
if [ "$1" == "build" ] && [ "$2" == "-social" ]; then
    export PYTHONPATH="$PROJECT_ROOT"
    nohup python "$SOCIAL_DIR/setup.py" > /dev/null 2>&1 &
    nohup python "$SOCIAL_DIR/main.py" > /dev/null 2>&1 &
fi

deactivate
