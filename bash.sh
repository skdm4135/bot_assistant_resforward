#!/bin/bash

# ===========================
# OLD CODE (commented)
# ===========================
# echo "starting Bot ~@save_restricted";
# python3 -m main

# ===========================
# NEW WORKING CODE (Render compatible)
# ===========================

# Start dummy server for Render
python3 server.py &

# Start Telegram bot properly using package mode
python3 -m main
