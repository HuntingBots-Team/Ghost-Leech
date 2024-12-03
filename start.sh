#!/bin/bash

# Activate virtual environment if needed
# source venv/bin/activate

# Update the bot
python3 update.py

# Check if update was successful
if [ $? -eq 0 ]; then
    echo "Update successful, starting bot..."
    # Start the bot
    python3 -m tghbot
else
    echo "Update failed, exiting..."
    exit 1
fi
