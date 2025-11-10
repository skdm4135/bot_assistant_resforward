#!/bin/bash

# ===========================
# OLD CODE (commented)
# ===========================
# echo "starting Bot ~@save_restricted";
# python3 -m main

# ===========================
# NEW WORKING CODE (Render compatible)
# ===========================

# Start dummy web server so Render doesn't timeout
python3 server.py &

# Start your Telegram bot
python3 main/__main__.py
