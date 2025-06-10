import os
import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, ChatAdminRequiredError, UserPrivacyRestrictedError, MessageIdInvalidError, ChatWriteForbiddenError

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
OWNER_ID = int(os.environ.get("OWNER_ID"))
SESSION_STRING = os.environ.get("SESSION_STRING")

bot = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
pending_users = {}
link_pattern = re.compile(r'(https?://t\.me/c/\d+/\d+)')

@bot.on(events.NewMessage)
async def handler(event):
    sender = await event.get_sender()
    if not sender or not sender.id:
        return

    user_id = sender.id
    msg = event.raw_text.strip()

    if msg.startswith('/start'):
        if user_id == OWNER_ID:
            await event.reply("✅ أهلاً بالمالك! أرسل الرابط لتحميل الوسائط فورًا.")
        else:
            await event.reply("👋 أرسل رقم جوالك مع رمز الدولة للتسجيل مثل: `+966XXXXXXXXX`", parse_mode='markdown')
        return

    if user_id != OWNER_ID and msg.startswith('+') and len(msg) > 10:
        await event.reply("❌ تم تعطيل التسجيل الذاتي في هذه النسخة.")
        return

    match = re.search(link_pattern, msg)
    if match:
        link = match.group(1)
        try:
            parts = link.split('/')
            chat_id = int("-100" + parts[4])
            msg_id = int(parts[5])

            message = await bot.get_messages(chat_id, ids=msg_id)
            if message and message.media:
                await event.reply("📥 جارٍ تحميل الوسائط...")
                await bot.send_file(user_id, message.media)
            else:
                await event.reply("⚠️ الرسالة لا تحتوي على صورة أو فيديو.")
        except MessageIdInvalidError:
            await event.reply("❌ خطأ: معرف الرسالة غير صالح.")
        except ChatAdminRequiredError:
            await event.reply("❌ خطأ: تحتاج أن تكون مشرفًا في القناة لتحميل هذه الرسالة.")
        except UserPrivacyRestrictedError:
            await event.reply("❌ لا يمكن تحميل المحتوى بسبب إعدادات الخصوصية.")
        except Exception as e:
            if 'protected content' in str(e).lower():
                await event.reply("❌ الرسالة محمية ولا يمكن تحميلها (Protected Content).")
            else:
                await event.reply(f"❌ خطأ أثناء التحميل:\n`{str(e)}`", parse_mode='markdown')

bot.start()
bot.run_until_disconnected()
