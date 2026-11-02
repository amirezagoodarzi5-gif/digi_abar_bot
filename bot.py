import re
import time

from collections import defaultdict

from telegram import Update
from telegram.constants import ChatMemberStatus

from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters
)

from config import TOKEN, OWNER_ID, WARN_LIMIT
from database import *


init_db()

flood = defaultdict(list)


async def is_admin(update, context):

    user = update.effective_user
    chat = update.effective_chat

    if user.id == OWNER_ID:
        return True

    role = get_role(chat.id, user.id)

    if role in ["owner", "admin", "moderator"]:
        return True

    member = await context.bot.get_chat_member(
        chat.id, user.id
    )

    return member.status in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ]


async def get_target(update):

    message = update.effective_message

    if message.reply_to_message:
        return message.reply_to_message.from_user

    return None


async def welcome(update, context):

    for member in update.effective_message.new_chat_members:

        if member.is_bot:
            continue

        await update.effective_message.reply_text(
            f"سلام {member.first_name} عزیز! 🌹\n"
            "به گروه ما خوش اومدی."
        )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not user or chat.type == "private":
        return

    if message.new_chat_members:
        await welcome(update, context)
        return

    text = (message.text or "").strip()

    if not text:
        return

    add_message(chat.id, user.id)

    # دستورات فقط در گروه

    parts = text.split(maxsplit=1)
    command = parts[0]
    argument = parts[1] if len(parts) > 1 else ""

    admin = await is_admin(update, context)

    # راهنما

    if command in ["دستورات", "راهنما"]:

        await message.reply_text("""
🤖 دستورات ربات مدیریت گروه

👮 مدیریت کاربران:
بن
آنبن
سکوت
آزاد
اخطار
حذف اخطار
اخطارها
اخراج

👑 مدیریت لقب:
لقب مدیر
حذف لقب
لقب من
لیست القاب

🔒 مدیریت گروه:
قفل لینک
بازکردن لینک
قفل عکس
بازکردن عکس
قفل فیلم
بازکردن فیلم
قفل فوروارد
بازکردن فوروارد

⚙️ امکانات:
آمار
تنظیمات
قوانین
تنظیم قوانین
خوشامد روشن
خوشامد خاموش
پنل مدیریت
        """)

        return

    # دستورات مخصوص مدیران

    if command in [
        "بن", "آنبن", "سکوت", "آزاد",
        "اخطار", "حذف", "حذف_اخطار",
        "اخراج", "پاکسازی", "لقب",
        "تنظیم", "قفل", "بازکردن"
    ] or command in [
        "لقب_مدیر", "حذف_لقب",
        "ارتقا_مدیر", "عزل_مدیر"
    ]:

        if not admin:
            await message.reply_text(
                "⛔ فقط مدیران اجازه استفاده دارند."
            )
            return

    target = await get_target(update)

    # بن

    if command == "بن":

        if not target:
            await message.reply_text(
                "ابتدا روی پیام کاربر ریپلای کن."
            )
            return

        await context.bot.ban_chat_member(
            chat.id, target.id
        )

        await message.reply_text("🔨 کاربر مسدود شد.")

    # آنبن

    elif command == "آنبن":

        if not target:
            return

        await context.bot.unban_chat_member(
            chat.id, target.id
        )

        await message.reply_text("✅ کاربر آزاد شد.")

    # سکوت

    elif command == "سکوت":

        if not target:
            return

        await context.bot.restrict_chat_member(
            chat.id,
            target.id,
            permissions=__import__(
                "telegram"
            ).ChatPermissions(can_send_messages=False)
        )

        await message.reply_text("🔇 کاربر ساکت شد.")

    # آزاد کردن

    elif command == "آزاد":

        if not target:
            return

        from telegram import ChatPermissions

        await context.bot.restrict_chat_member(
            chat.id,
            target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True
            )
        )

        await message.reply_text("🔊 محدودیت کاربر برداشته شد.")

    # اخطار

    elif command == "اخطار":

        if not target:
            return

        add_warning(chat.id, target.id)

        count = get_warnings(chat.id, target.id)

        if count >= WARN_LIMIT:

            await context.bot.ban_chat_member(
                chat.id, target.id
            )

            await message.reply_text(
                "⛔ اخطارها به حد مجاز رسید؛ کاربر مسدود شد."
            )

        else:

            await message.reply_text(
                f"⚠️ اخطار شماره {count} ثبت شد."
            )

    # حذف اخطار

    elif command in ["حذف", "حذف_اخطار"]:

        if not target:
            return

        execute("""
        UPDATE users
        SET warnings=0
        WHERE chat_id=? AND user_id=?
        """, (chat.id, target.id))

        await message.reply_text("✅ اخطارهای کاربر پاک شد.")

    # نمایش اخطار

    elif command == "اخطارها":

        if not target:
            return

        count = get_warnings(chat.id, target.id)

        await message.reply_text(
            f"⚠️ تعداد اخطارها: {count}"
        )

    # لقب مدیر

    elif command in ["لقب", "لقب_مدیر"]:

        if not target or not argument:
            await message.reply_text(
                "روی پیام کاربر ریپلای کن و بنویس:\n"
                "لقب مدیر پادشاه گروه"
            )
            return

        if len(argument) > 40:
            await message.reply_text("لقب نباید بیشتر از ۴۰ حرف باشد.")
            return

        set_title(chat.id, target.id, argument)

        await message.reply_text(
            f"👑 لقب جدید ثبت شد:\n{argument}"
        )

    # حذف لقب

    elif command == "حذف_لقب":

        if not target:
            return

        set_title(chat.id, target.id, "")

        await message.reply_text("لقب حذف شد.")

    # لقب من

    elif command == "لقب_من":

        title = get_title(chat.id, user.id)

        await message.reply_text(
            f"👑 لقب شما: {title or 'بدون لقب'}"
        )

    # ارتقای مدیر داخلی ربات

    elif command == "ارتقا_مدیر":

        if user.id != OWNER_ID:
            await message.reply_text("فقط مالک ربات مجاز است.")
            return

        if not target:
            return

        set_role(chat.id, target.id, "admin")

        await message.reply_text("👑 کاربر به مدیر ربات ارتقا یافت.")

    # عزل مدیر داخلی

    elif command == "عزل_مدیر":

        if user.id != OWNER_ID:
            return

        if not target:
            return

        set_role(chat.id, target.id, "member")

        await message.reply_text("مدیر داخلی عزل شد.")

    # قفل لینک

    elif command == "قفل" and argument == "لینک":

        set_setting(chat.id, "links", "on")

        await message.reply_text("🔒 لینک‌ها قفل شدند.")

    elif command == "بازکردن" and argument == "لینک":

        set_setting(chat.id, "links", "off")

        await message.reply_text("🔓 لینک‌ها آزاد شدند.")

    # قفل عکس

    elif command == "قفل" and argument == "عکس":

        set_setting(chat.id, "photos", "on")

        await message.reply_text("عکس‌ها قفل شدند.")

    elif command == "بازکردن" and argument == "عکس":

        set_setting(chat.id, "photos", "off")

        await message.reply_text("عکس‌ها آزاد شدند.")

    # قفل فیلم

    elif command == "قفل" and argument == "فیلم":

        set_setting(chat.id, "videos", "on")

        await message.reply_text("فیلم‌ها قفل شدند.")

    elif command == "بازکردن" and argument == "فیلم":

        set_setting(chat.id, "videos", "off")

        await message.reply_text("فیلم‌ها آزاد شدند.")

    # قفل فوروارد

    elif command == "قفل" and argument == "فوروارد":

        set_setting(chat.id, "forwards", "on")

        await message.reply_text("فوروارد قفل شد.")

    elif command == "بازکردن" and argument == "فوروارد":

        set_setting(chat.id, "forwards", "off")

        await message.reply_text("فوروارد آزاد شد.")

    # قوانین

    elif command == "قوانین":

        await message.reply_text(get_rules(chat.id))

    elif command == "تنظیم_قوانین":

        if admin and argument:
            set_rules(chat.id, argument)
            await message.reply_text("قوانین ثبت شد.")

    # خوشامدگویی

    elif command == "خوشامد" and argument == "روشن":

        set_setting(chat.id, "welcome", "on")
        await message.reply_text("خوشامدگویی روشن شد.")

    elif command == "خوشامد" and argument == "خاموش":

        set_setting(chat.id, "welcome", "off")
        await message.reply_text("خوشامدگویی خاموش شد.")

    # آمار

    elif command == "آمار":

        users, messages = get_stats(chat.id)

        await message.reply_text(
            f"📊 آمار گروه\n\n"
            f"👥 کاربران فعال: {users}\n"
            f"💬 تعداد پیام‌ها: {messages}"
        )

    # پاکسازی

    elif command == "پاکسازی":

        if message.reply_to_message:
            await message.reply_text(
                "برای پاکسازی، تعداد پیام‌ها را مشخص کن."
            )

    # پنل مدیریت

    elif command == "پنل":

        if not admin:
            return

        await message.reply_text("""
⚙️ پنل مدیریت

🔒 قفل لینک: قفل لینک
🔓 آزادسازی لینک: بازکردن لینک
👋 خوشامدگویی: خوشامد روشن
📊 آمار گروه: آمار
📜 قوانین: قوانین
📚 راهنما: دستورات
        """)

    # سیستم ضد لینک

    if (
        get_setting(chat.id, "links") == "on"
        and not admin
        and re.search(
            r"(https?://|www\.|t\.me/)",
            text,
            re.IGNORECASE
        )
    ):

        await message.delete()
        return

    # سیستم ضد اسپم

    now = time.time()

    flood[user.id] = [
        t for t in flood[user.id]
        if now - t < 5
    ]

    flood[user.id].append(now)

    if len(flood[user.id]) > 5 and not admin:

        await message.delete()

        await message.reply_text(
            "🚫 ارسال پیام بیش از حد مجاز است."
        )

    # قفل عکس

    if (
        get_setting(chat.id, "photos") == "on"
        and message.photo
        and not admin
    ):

        await message.delete()

    # قفل فیلم

    if (
        get_setting(chat.id, "videos") == "on"
        and message.video
        and not admin
    ):

        await message.delete()


def main():

    if not TOKEN:
        raise ValueError("BOT_TOKEN تنظیم نشده است.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(
            filters.ALL,
            handle
        )
    )

    print("Bot Started Successfully!")

    app.run_polling()


if __name__ == "__main__":
    main()
