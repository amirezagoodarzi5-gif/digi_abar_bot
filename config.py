import os
from motor.motor_asyncio import AsyncIOMotorClient

# توکن و اطلاعات اتصال
BOT_TOKEN = os.getenv("BOT_TOKEN", "TOKEN_HERE")
MONGO_URI = os.getenv("MONGO_URI", "MONGODB_URI_HERE")

# اتصال به MongoDB
db_client = AsyncIOMotorClient(MONGO_URI)
db = db_client["digi_abar_bot"]

# شناسه‌های گروه‌های مجاز (اصلی و تست)
MAIN_GROUP_ID = int(os.getenv("MAIN_GROUP_ID", "-100XXXXXXXXXX"))
TEST_GROUP_ID = int(os.getenv("TEST_GROUP_ID", "-100XXXXXXXXXX"))
ALLOWED_CHATS = [MAIN_GROUP_ID, TEST_GROUP_ID]
