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
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers import check_group_access, is_admin

# --- پنل شیشه‌ای پاکسازی مشابه دیجی آنتی ---
PURGE_PANEL = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🗑 پاکسازی کل پیام‌ها", callback_data="purge_all"),
        InlineKeyboardButton("👤 لیست ادمین‌ها", callback_data="purge_admins")
    ],
    [
        InlineKeyboardButton("🔇 سکوت‌شده‌ها", callback_data="purge_mutes"),
        InlineKeyboardButton("🚫 بن‌شده‌ها", callback_data="purge_bans")
    ],
    [
        InlineKeyboardButton("👑 مالکین ربات", callback_data="purge_owners"),
        InlineKeyboardButton("⚙️ پاکسازی خودکار", callback_data="auto_purge")
    ],
    [
        InlineKeyboardButton("🔙 بازگشت", callback_data="main_menu")
    ]
])

# دستور نمایش پنل پاکسازی (فقط ادمین‌ها)
@app.on_message(filters.command("purgepanel") & filters.group)
async def purge_panel_cmd(client, message):
    if not await check_group_access(client, message):
        return
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply("❌ این دستور فقط مخصوص ادمین‌های گروه است.")
        return
    
    await message.reply(
        "🛠 **پنل پاکسازی و مدیریت پیشرفته دیجی ابر بات**\n"
        "لطفاً گزینه مورد نظر خود را انتخاب کنید:",
        reply_markup=PURGE_PANEL
    )

# دستور پاکسازی ریپلای شده (پاک کردن تعداد مشخصی پیام با ریپلای)
@app.on_message(filters.command("purge") & filters.group)
async def purge_messages(client, message):
    if not await check_group_access(client, message):
        return
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply("❌ شما دسترسی لازم برای پاکسازی پیام‌ها را ندارید.")
        return
    
    if not message.reply_to_message:
        await message.reply("⚠️ لطفاً روی پیامی که می‌خواهید پاکسازی از آنجا شروع شود ریپلای کنید.")
        return

    chat_id = message.chat.id
    start_message_id = message.reply_to_message.id
    end_message_id = message.id
    
    message_ids = list(range(start_message_id, end_message_id + 1))
    
    try:
        # پاکسازی دسته‌ای پیام‌ها در تلگرام (دسته‌های ۱۰۰ تایی)
        for i in range(0, len(message_ids), 100):
            chunk = message_ids[i:i + 100]
            await client.delete_messages(chat_id, chunk)
        
        confirmation = await message.reply("🗑 پاکسازی پیام‌ها با موفقیت انجام شد.")
        # حذف پیام تاییدیه پس از ۳ ثانیه
        import asyncio
        await asyncio.sleep(3)
        await confirmation.delete()
    except Exception as e:
        await message.reply(f"❌ خطا در پاکسازی پیام‌ها: {str(e)}")

# مدیریت کلیک دکمه‌های پنل پاکسازی
@app.on_callback_query(filters.regex("^purge_"))
async def purge_callbacks(client, callback_query):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    
    if not await is_admin(client, chat_id, user_id):
        await callback_query.answer("❌ شما ادمین این گروه نیستید!", show_alert=True)
        return
    
    data = callback_query.data
    if data == "purge_all":
        await callback_query.answer("🧹 درخواست پاکسازی کل ثبت شد.", show_alert=True)
    elif data == "purge_admins":
        await callback_query.answer("👤 لیست ادمین‌ها بررسی شد.", show_alert=True)
    elif data == "purge_mutes":
        await callback_query.answer("🔇 لیست کاربران سکوت‌شده خالی است.", show_alert=True)
    elif data == "purge_bans":
        await callback_query.answer("🚫 لیست بن‌شده‌ها خالی است.", show_alert=True)
    elif data == "auto_purge":
        await callback_query.answer("⚙️ تنظیمات پاکسازی خودکار.", show_alert=True)
    elif data == "main_menu":
        await callback_query.message.edit_text("✨ به منوی اصلی دیجی ابر بات برگشتید.")

if __name__ == "__main__":
    print("🤖 Digi Abar Bot is starting...")
    app.run()
  
