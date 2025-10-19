#!/bin/bash
set -e
echo "🚀 Starting Python bot..."
pip install --upgrade pip
pip install -r requirements.txt
python bot.py