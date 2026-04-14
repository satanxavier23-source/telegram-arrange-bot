import os
import re
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_IDS = [6630347046, 7194569468]

user_settings = {}

def is_admin(user_id):
    return user_id in ADMIN_IDS

def init_user(uid):
    if uid not in user_settings:
        user_settings[uid] = {
            "arrange_mode": True,
            "thumb_mode": True,
            "saved_photo": None
        }

def extract_links(text):
    if not text:
        return []
    return re.findall(r'https?://[^\s]+', text)

def build_text(links):
    text = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(links, start=1):
        text += f"VIDEO {i} ⤵️\n{link}\n\n"
    return text[:1024]

def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Set Thumb")
    kb.row("Thumb ON", "Thumb OFF")
    kb.row("Arrange ON", "Arrange OFF")
    kb.row("Status")
    return kb

@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    if not is_admin(uid):
        bot.reply_to(message, "❌ Admin only")
        return

    init_user(uid)
    bot.reply_to(message, "Bot started ✅", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == "Set Thumb")
def set_thumb(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_settings[uid]["waiting_thumb"] = True
    bot.reply_to(message, "Photo അയക്കൂ thumb save ചെയ്യാൻ 📸")

@bot.message_handler(func=lambda m: m.text == "Thumb ON")
def thumb_on(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["thumb_mode"] = True
    bot.reply_to(message, "Thumb ON ✅")

@bot.message_handler(func=lambda m: m.text == "Thumb OFF")
def thumb_off(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["thumb_mode"] = False
    bot.reply_to(message, "Thumb OFF ❌")

@bot.message_handler(func=lambda m: m.text == "Arrange ON")
def arrange_on(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["arrange_mode"] = True
    bot.reply_to(message, "Arrange ON ✅")

@bot.message_handler(func=lambda m: m.text == "Arrange OFF")
def arrange_off(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["arrange_mode"] = False
    bot.reply_to(message, "Arrange OFF ❌")

@bot.message_handler(func=lambda m: m.text == "Status")
def status(message):
    uid = message.from_user.id
    init_user(uid)
    s = user_settings[uid]
    bot.reply_to(
        message,
        f"Arrange: {s['arrange_mode']}\nThumb: {s['thumb_mode']}\nThumb saved: {bool(s['saved_photo'])}"
    )

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    # DEBUG
    bot.send_message(message.chat.id, "DEBUG: photo handler reached ✅")

    if user_settings[uid].get("waiting_thumb"):
        user_settings[uid]["saved_photo"] = message.photo[-1].file_id
        user_settings[uid]["waiting_thumb"] = False
        bot.reply_to(message, "Thumb saved ✅")
        return

    if not user_settings[uid]["arrange_mode"]:
        bot.reply_to(message, "Arrange OFF ആണ്")
        return

    caption = message.caption or ""
    links = extract_links(caption)

    if not links:
        bot.reply_to(message, "Caption-il links കണ്ടില്ല ❌")
        return

    final_text = build_text(links)

    send_photo = message.photo[-1].file_id
    if user_settings[uid]["thumb_mode"] and user_settings[uid]["saved_photo"]:
        send_photo = user_settings[uid]["saved_photo"]

    bot.send_photo(
        message.chat.id,
        send_photo,
        caption=final_text
    )

@bot.message_handler(content_types=['text'])
def text_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    if message.text in ["Set Thumb", "Thumb ON", "Thumb OFF", "Arrange ON", "Arrange OFF", "Status"]:
        return

    init_user(uid)

    if not user_settings[uid]["arrange_mode"]:
        return

    links = extract_links(message.text)
    if not links:
        return

    final_text = build_text(links)

    if user_settings[uid]["thumb_mode"] and user_settings[uid]["saved_photo"]:
        bot.send_photo(message.chat.id, user_settings[uid]["saved_photo"], caption=final_text)
    else:
        bot.send_message(message.chat.id, final_text)

print("Bot running...")
bot.infinity_polling(skip_pending=True, none_stop=True)
