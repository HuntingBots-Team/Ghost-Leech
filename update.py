import os
import logging
from dotenv import load_dotenv
import pymongo

# Load environment variables from config.env file
load_dotenv('config.env')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
TELEGRAM_API = os.getenv('TELEGRAM_API')
TELEGRAM_HASH = os.getenv('TELEGRAM_HASH')
DATABASE_URL = os.getenv('DATABASE_URL')

if not BOT_TOKEN or not DATABASE_URL:
    logger.error("BOT_TOKEN or DATABASE_URL is not set in the environment variables.")
    exit(1)

# MongoDB client setup
try:
    client = pymongo.MongoClient(DATABASE_URL)
    db = client.get_database()
    logger.info("Connected to MongoDB successfully.")
except pymongo.errors.ConnectionError as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    exit(1)

# Example function to demonstrate the use of environment variables
def run_bot():
    # Your bot's main code would go here
    logger.info("Bot is running...")

    # Check for log files and handle them
    log_file_path = 'bot.log'
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        logger.info(f"Removed existing log file: {log_file_path}")

# Run the bot
if __name__ == "__main__":
    run_bot()
