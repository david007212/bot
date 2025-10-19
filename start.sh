#!/usr/bin/env bash
set -e
echo "🚀 Starting Python bot..."

# Aktiviraj virtualno okruženje koje Railpack napravi
source /app/.venv/bin/activate

# Instaliraj pakete u to okruženje
pip install --upgrade pip
pip install -r requirements.txt

# Pokreni bota
python bot.py