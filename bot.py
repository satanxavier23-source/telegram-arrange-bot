import os
import re
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("ERROR: BOT_TOKEN not found")
    raise SystemExit(1)

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def extract_links(text: str):
    if not text:
        return []
    return re.findall(r'https?://\S+', text)

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "Bot working ✅\nആദ്യം photo അയക്കൂ 📸")

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    user_id = message.from_user.id

    user_data[user_id] = {
        "photo": message.photo[-1].file_id,
        "links": []
    }

    bot.reply_to(message, "ഇപ്പോൾ links അയക്കൂ 🔗")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    user_id = message.from_user.id
    text = message.text or ""

    if text.startswith("/start"):
        return

    if user_id not in user_data:
        bot.reply_to(message, "ആദ്യം photo അയക്കൂ 📸")
        return

    links = extract_links(text)

    if not links:
        bot.reply_to(message, "Valid links അയക്കൂ 🔗")
        return

    user_data[user_id]["links"].extend(links)
    send_result(message.chat.id, user_id)

def send_result(chat_id, user_id):
    data = user_data.get(user_id)

    if not data or not data["links"]:
        return

    result = "FULL VIDEO 👀🌸\n\n"

    for i, link in enumerate(data["links"], start=1):
        result += f"VIDEO {i} ⤵️\n{link}\n\n"

    try:
        bot.send_photo(chat_id, data["photo"])
        bot.send_message(chat_id, result)
    except Exception as e:
        print("SEND ERROR:", e)

    user_data.pop(user_id, None)

print("Bot running...")
bot.infinity_polling(skip_pending=True, none_stop=True)
