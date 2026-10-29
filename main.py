import os
from hydrogram import Client, filters
from config import BOT_TOKEN, ALLOWED_CHATS
from helpers import check_group_access

# راه‌اندازی کلاینت ربات با Hydrogram
app = Client(
    "digi_abar_bot",
    api_id=int(os.getenv("API_ID", "123456")),
    api_hash=os.getenv("API_HASH", "your_api_hash"),
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    if message.chat.type == "private":
        await message.reply(
            "من ربات مدیریت گروه دیجی ابر بات هستم 🌟\n"
            "من رو به گروهت اضافه کن و مدیریت کامل داشته باش."
        )
    else:
        if not await check_group_access(client, message):
            return
        await message.reply("✨ دیجی ابر بات با موفقیت در این گروه فعال است و آماده مدیریت می‌باشد.")

# رویداد ورود به گروه جدید برای بررسی اجازه فعالیت
@app.on_message(filters.new_chat_members)
async def new_chat_member(client, message):
    if message.chat.id not in ALLOWED_CHATS:
        await message.reply("❌ اجازه فعالیت در این گروه صادر نشده است. خداحافظ!")
        await client.leave_chat(message.chat.id)

if __name__ == "__main__":
    print("🤖 Digi Abar Bot is starting...")
    app.run()
  
