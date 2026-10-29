from hydrogram import Client
from config import ALLOWED_CHATS

async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    """بررسی اینکه آیا کاربر ادمین گروه است یا خیر"""
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

async def check_group_access(client: Client, message) -> bool:
    """بررسی اینکه ربات فقط در گروه‌های مجاز فعالیت کند و در غیر این صورت لفت دهد"""
    if message.chat.type in ["group", "supergroup"]:
        if message.chat.id not in ALLOWED_CHATS:
            await message.reply("❌ این ربات تنها در گروه‌های مجاز اجازه فعالیت دارد.")
            await client.leave_chat(message.chat.id)
            return False
    return True
  
