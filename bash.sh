# echo "starting Bot ~@save_restricted";
# python3 -m main

=======================
# new changes

#!/bin/bash

# Start dummy web server so Render doesn't timeout
python3 server.py &

# Start your Telegram bot
python3 main/__main__.py
