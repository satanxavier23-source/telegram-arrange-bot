import telebot
import re
import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def extract_links(text):
    if not text:
        return []
    return re.findall(r'https?://\S+', text)

@bot.message_handler(commands=['start'])
def start_handler(message):
    print(f"/start from {message.from_user.id}")
    bot.reply_to(message, "Bot active ✅\nPhoto അയക്കൂ 📸")

@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    user_id = message.from_user.id
    caption = message.caption or ""

    print(f"PHOTO received from {user_id}")
    print(f"Caption: {caption}")

    user_data[user_id] = {
        "photo": message.photo[-1].file_id,
        "links": []
    }

    links = extract_links(caption)

    if links:
        user_data[user_id]["links"].extend(links)
        send_result(message.chat.id, user_id)
    else:
        bot.reply_to(message, "Links അയക്കൂ 🔗")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    user_id = message.from_user.id
    text = message.text or ""

    print(f"TEXT received from {user_id}: {text}")

    if text.startswith("/start"):
        return

    if user_id not in user_data:
        bot.reply_to(message, "ആദ്യം photo അയക്കൂ 📸")
        return

    links = extract_links(text)

    if not links:
        bot.reply_to(message, "Valid link അയക്കൂ 🔗")
        return

    user_data[user_id]["links"].extend(links)
    send_result(message.chat.id, user_id)

def send_result(chat_id, user_id):
    data = user_data.get(user_id)

    print(f"send_result called for {user_id}")
    print(f"data = {data}")

    if not data or not data["links"]:
        print("No data or no links")
        return

    new_links = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(data["links"], start=1):
        new_links += f"VIDEO {i} ⤵️\n{link}\n\n"

    try:
        bot.send_photo(chat_id, data["photo"])
        bot.send_message(chat_id, new_links)
        print("Message sent successfully")
    except Exception as e:
        print("SEND ERROR:", e)

    user_data.pop(user_id, None)

print("Bot running...")
bot.infinity_polling(skip_pending=True, none_stop=True)
