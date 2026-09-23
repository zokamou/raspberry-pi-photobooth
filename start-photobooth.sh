#!/bin/bash

cd "$(dirname "$0")"

python3 app.py >> "$HOME/photobooth.log" 2>&1