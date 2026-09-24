#!/bin/bash

cd "$(dirname "$0")"

python3 main.py >> "$HOME/photobooth.log" 2>&1