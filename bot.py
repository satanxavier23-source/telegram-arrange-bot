import os
import re
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("Token ഇല്ല ❌")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

# ===== STORAGE =====
replace_photo = None
waiting_photo = False

thumb_mode = False
link_mode = True
forward_mode = False

selected_channels = set()

# ===== CHANNEL IDS =====
CHANNELS = {
    "Channel 1": -1002674664027,
    "Channel 2": -1002514181198,
    "Channel 3": -1002427180742
}

# ===== FUNCTIONS =====
def extract_links(text):
    if not text:
        return []
    return re.findall(r'https?://\S+', text)

def arrange_links(text):
    links = extract_links(text)
    if not links:
        return None

    result = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(links, 1):
        result += f"VIDEO {i} ⤵️\n{link}\n\n"

    return result.strip()

# ===== KEYBOARDS =====
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Set Photo")
    markup.row("Thumb ON", "Thumb OFF")
    markup.row("Link ON", "Link OFF")
    markup.row("Forward ON", "Forward OFF")
    markup.row("Select Channels")
    markup.row("Status")
    return markup

def channel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Channel 1", "Channel 2")
    markup.row("Channel 3")
    markup.row("Clear Channels")
    markup.row("Back")
    return markup

def get_status():
    return (
        f"📊 Status\n\n"
        f"Thumb: {'ON ✅' if thumb_mode else 'OFF ❌'}\n"
        f"Link: {'ON ✅' if link_mode else 'OFF ❌'}\n"
        f"Forward: {'ON ✅' if forward_mode else 'OFF ❌'}\n"
        f"Photo: {'Saved ✅' if replace_photo else 'Not Saved ❌'}\n"
        f"Channels: {len(selected_channels)}"
    )

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, "🔥 Bot Ready 🔥", reply_markup=main_keyboard())

# ===== BUTTON HANDLERS =====
@bot.message_handler(func=lambda m: m.text == "Set Photo")
def set_photo(msg):
    global waiting_photo
    waiting_photo = True
    bot.reply_to(msg, "Photo അയക്കൂ 📸")

@bot.message_handler(func=lambda m: m.text == "Thumb ON")
def thumb_on(msg):
    global thumb_mode
    if not replace_photo:
        bot.reply_to(msg, "Photo set ചെയ്തിട്ടില്ല ❌")
        return
    thumb_mode = True
    bot.reply_to(msg, "Thumb ON 🔥")

@bot.message_handler(func=lambda m: m.text == "Thumb OFF")
def thumb_off(msg):
    global thumb_mode
    thumb_mode = False
    bot.reply_to(msg, "Thumb OFF ❌")

@bot.message_handler(func=lambda m: m.text == "Link ON")
def link_on(msg):
    global link_mode
    link_mode = True
    bot.reply_to(msg, "Link ON ✅")

@bot.message_handler(func=lambda m: m.text == "Link OFF")
def link_off(msg):
    global link_mode
    link_mode = False
    bot.reply_to(msg, "Link OFF ❌")

@bot.message_handler(func=lambda m: m.text == "Forward ON")
def forward_on(msg):
    global forward_mode
    forward_mode = True
    bot.reply_to(msg, "Forward ON 🚀")

@bot.message_handler(func=lambda m: m.text == "Forward OFF")
def forward_off(msg):
    global forward_mode
    forward_mode = False
    bot.reply_to(msg, "Forward OFF ❌")

@bot.message_handler(func=lambda m: m.text == "Select Channels")
def select_channels(msg):
    bot.send_message(msg.chat.id, "Channels select ചെയ്യൂ", reply_markup=channel_keyboard())

@bot.message_handler(func=lambda m: m.text in ["Channel 1", "Channel 2", "Channel 3"])
def add_channel(msg):
    selected_channels.add(CHANNELS[msg.text])
    bot.reply_to(msg, f"{msg.text} added ✅")

@bot.message_handler(func=lambda m: m.text == "Clear Channels")
def clear_channels(msg):
    selected_channels.clear()
    bot.reply_to(msg, "Channels cleared ❌")

@bot.message_handler(func=lambda m: m.text == "Back")
def back(msg):
    bot.send_message(msg.chat.id, "Main Menu 🔥", reply_markup=main_keyboard())

@bot.message_handler(func=lambda m: m.text == "Status")
def status(msg):
    bot.reply_to(msg, get_status())
