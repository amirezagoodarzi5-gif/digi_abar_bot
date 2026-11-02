import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

DATABASE = "bot.db"

WARN_LIMIT = 3
FLOOD_LIMIT = 5
FLOOD_SECONDS = 5
