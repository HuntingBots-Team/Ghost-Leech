import os
import sys
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

# Add directories to system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tghbot'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'sabnzbdapi'))

# Example imports from directories
# from tghbot import some_module
# from plugins import another_module
# from sabnzbdapi import sabnzbd_module

# Load environment variables
load_dotenv('config.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

if not BOT_TOKEN or not DATABASE_URL:
    raise ValueError("Missing BOT_TOKEN or DATABASE_URL in environment variables")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup MongoDB Client
try:
    client = MongoClient(DATABASE_URL)
    db = client.get_database()
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {e}")
    raise

def run_bot():
    logger.info("Bot is starting...")
    # Placeholder for bot's main code
    # some_module.run()
    # another_module.execute()
    # sabnzbd_module.start()

if __name__ == "__main__":
    run_bot()
