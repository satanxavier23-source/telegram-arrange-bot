import os
import re
import time
import threading
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# =========================
# STORAGE
# =========================
user_data = {}
user_settings = {}

CHANNELS = {
    "Channel 1": "-1002674664027",
    "Channel 2": "-1002514181198",
    "Channel 3": "-1002427180742",
    "Channel 4": "-1003590340901",
}

PHOTO_SLOTS = ["Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5"]

# =========================
# INIT
# =========================
def init_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "photo": None,
            "text_parts": [],
            "links": [],
            "timer_id": 0,
        }

    if user_id not in user_settings:
        user_settings[user_id] = {
            "saved_photos": {
                "Photo 1": None,
                "Photo 2": None,
                "Photo 3": None,
                "Photo 4": None,
                "Photo 5": None,
            },
            "selected_photo_slot": None,
            "selected_photo_file_id": None,
            "selected_channels": [],
            "auto_forward": False,
            "waiting_set_photo_slot": None,
        }

# =========================
# KEYBOARDS
# =========================
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔗 Link Arrangement")
    markup.row("📸 Set Photo", "✅ Use Photo")
    markup.row("📢 Auto Forward Channel", "📋 Current Channels")
    markup.row("🖼 Current Photo", "🔘 Auto Forward On/Off")
    return markup

def set_photo_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Photo 1", "Photo 2")
    markup.row("Photo 3", "Photo 4")
    markup.row("Photo 5")
    markup.row("⬅️ Back")
    return markup

def use_photo_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Photo 1", "Photo 2")
    markup.row("Photo 3", "Photo 4")
    markup.row("Photo 5")
    markup.row("❌ Disable Photo", "⬅️ Back")
    return markup

def channel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Channel 1", "Channel 2")
    markup.row("Channel 3", "Channel 4")
    markup.row("✅ Done", "🗑 Clear Channels")
    markup.row("⬅️ Back")
    return markup

def forward_toggle_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🟢 ON", "🔴 OFF")
    markup.row("⬅️ Back")
    return markup

# =========================
# HELPERS
# =========================
def extract_links(text):
    return re.findall(r'https?://\S+', text)

def clean_links_from_text(text):
    links = extract_links(text)
    clean_text = text
    for link in links:
        clean_text = clean_text.replace(link, "")
    return clean_text.strip()

def selected_channels_text(user_id):
    channels = user_settings[user_id]["selected_channels"]
    if not channels:
        return "Channel onnum select cheythittilla."
    out = "Selected Channels:\n\n"
    for i, ch in enumerate(channels, start=1):
        out += f"{i}. {ch}\n"
    return out

# =========================
# START
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    init_user(user_id)
    bot.send_message(
        message.chat.id,
        "Bot ready ✅",
        reply_markup=main_keyboard()
    )

# =========================
# BACK BUTTON
# =========================
@bot.message_handler(func=lambda m: m.text == "⬅️ Back")
def back_btn(message):
    bot.send_message(
        message.chat.id,
        "Main menu ✅",
        reply_markup=main_keyboard()
    )

# =========================
# MAIN BUTTONS
# =========================
@bot.message_handler(func=lambda m: m.text == "🔗 Link Arrangement")
def link_arrangement(message):
    user_id = message.from_user.id
    init_user(user_id)
    bot.send_message(
        message.chat.id,
        "Photo + text + links അയക്കൂ. Bot arrange ചെയ്ത് തിരിച്ച് അയക്കും ✅",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📸 Set Photo")
def set_photo_menu(message):
    user_id = message.from_user.id
    init_user(user_id)
    bot.send_message(
        message.chat.id,
        "ഏത് photo slot set ചെയ്യണം?",
        reply_markup=set_photo_keyboard()
    )

@bot.message_handler(func=lambda m: m.text in PHOTO_SLOTS)
def photo_slot_handler(message):
    user_id = message.from_user.id
    init_user(user_id)

    # If user came from set photo flow
    user_settings[user_id]["waiting_set_photo_slot"] = message.text

    bot.send_message(
        message.chat.id,
        f"{message.text} നായി ഇപ്പോൾ photo അയക്കൂ 📸",
        reply_markup=set_photo_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "✅ Use Photo")
def use_photo_menu(message):
    user_id = message.from_user.id
    init_user(user_id)
    bot.send_message(
        message.chat.id,
        "ഏത് saved photo use ചെയ്യണം?",
        reply_markup=use_photo_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "❌ Disable Photo")
def disable_photo(message):
    user_id = message.from_user.id
    init_user(user_id)

    user_settings[user_id]["selected_photo_slot"] = None
    user_settings[user_id]["selected_photo_file_id"] = None

    bot.send_message(
        message.chat.id,
        "Use Photo OFF ✅",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text in ["Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5"])
def use_saved_photo_handler(message):
    user_id = message.from_user.id
    init_user(user_id)

    slot = message.text
    saved_photo = user_settings[user_id]["saved_photos"].get(slot)

    if not saved_photo:
        bot.send_message(
            message.chat.id,
            f"{slot} ഇൽ photo save ചെയ്തിട്ടില്ല.",
            reply_markup=use_photo_keyboard()
        )
        return

    user_settings[user_id]["selected_photo_slot"] = slot
    user_settings[user_id]["selected_photo_file_id"] = saved_photo

    bot.send_photo(
        message.chat.id,
        saved_photo,
        caption=f"✅ {slot} selected",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📢 Auto Forward Channel")
def auto_forward_channel_menu(message):
    user_id = message.from_user.id
    init_user(user_id)

    bot.send_message(
        message.chat.id,
        "Forward ചെയ്യാനുള്ള channels select ചെയ്യൂ.",
        reply_markup=channel_keyboard()
    )

@bot.message_handler(func=lambda m: m.text in ["Channel 1", "Channel 2", "Channel 3", "Channel 4"])
def select_channel_handler(message):
    user_id = message.from_user.id
    init_user(user_id)

    channel_name = message.text
    channel_id = CHANNELS[channel_name]

    if channel_id in user_settings[user_id]["selected_channels"]:
        user_settings[user_id]["selected_channels"].remove(channel_id)
        bot.send_message(
            message.chat.id,
            f"{channel_name} remove ചെയ്തു ❌",
            reply_markup=channel_keyboard()
        )
    else:
        user_settings[user_id]["selected_channels"].append(channel_id)
        bot.send_message(
            message.chat.id,
            f"{channel_name} add ചെയ്തു ✅",
            reply_markup=channel_keyboard()
        )

@bot.message_handler(func=lambda m: m.text == "✅ Done")
def done_channels(message):
    user_id = message.from_user.id
    init_user(user_id)

    bot.send_message(
        message.chat.id,
        selected_channels_text(user_id),
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🗑 Clear Channels")
def clear_channels(message):
    user_id = message.from_user.id
    init_user(user_id)

    user_settings[user_id]["selected_channels"] = []

    bot.send_message(
        message.chat.id,
        "Channels clear ചെയ്തു ✅",
        reply_markup=channel_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "📋 Current Channels")
def current_channels(message):
    user_id = message.from_user.id
    init_user(user_id)

    bot.send_message(
        message.chat.id,
        selected_channels_text(user_id),
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🖼 Current Photo")
def current_photo(message):
    user_id = message.from_user.id
    init_user(user_id)

    selected_slot = user_settings[user_id]["selected_photo_slot"]
    selected_file = user_settings[user_id]["selected_photo_file_id"]

    if not selected_file:
        bot.send_message(
            message.chat.id,
            "Current photo ഇല്ല.",
            reply_markup=main_keyboard()
        )
        return

    bot.send_photo(
        message.chat.id,
        selected_file,
        caption=f"🖼 Current Photo: {selected_slot}",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🔘 Auto Forward On/Off")
def auto_forward_toggle_menu(message):
    user_id = message.from_user.id
    init_user(user_id)

    bot.send_message(
        message.chat.id,
        "Auto forward ON/OFF select ചെയ്യൂ.",
        reply_markup=forward_toggle_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🟢 ON")
def forward_on(message):
    user_id = message.from_user.id
    init_user(user_id)

    user_settings[user_id]["auto_forward"] = True

    bot.send_message(
        message.chat.id,
        "Auto Forward ON ✅❤️🔥",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda m: m.text == "🔴 OFF")
def forward_off(message):
    user_id = message.from_user.id
    init_user(user_id)

    user_settings[user_id]["auto_forward"] = False

    bot.send_message(
        message.chat.id,
        "Auto Forward OFF ❌",
        reply_markup=main_keyboard()
    )

# =========================
# PHOTO HANDLER
# =========================
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    user_id = message.from_user.id
    init_user(user_id)

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""

    # Set Photo flow
    waiting_slot = user_settings[user_id]["waiting_set_photo_slot"]
    if waiting_slot:
        user_settings[user_id]["saved_photos"][waiting_slot] = photo_id
        user_settings[user_id]["waiting_set_photo_slot"] = None

        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=f"{waiting_slot} save ചെയ്തു ✅",
            reply_markup=main_keyboard()
        )
        return

    # Normal link arrangement flow
    user_data[user_id]["photo"] = photo_id
    user_data[user_id]["text_parts"] = []
    user_data[user_id]["links"] = []
    user_data[user_id]["timer_id"] += 1

    clean_text = clean_links_from_text(caption)
    links = extract_links(caption)

    if clean_text:
        user_data[user_id]["text_parts"].append(clean_text)

    if links:
        user_data[user_id]["links"].extend(links)

    current_timer = user_data[user_id]["timer_id"]

    bot.send_message(
        message.chat.id,
        "Photo received ✅ Links/text അയക്കാം.",
        reply_markup=main_keyboard()
    )

    threading.Thread(
        target=auto_send_after_delay,
        args=(user_id, message.chat.id, current_timer),
        daemon=True
    ).start()

# =========================
# TEXT HANDLER
# =========================
@bot.message_handler(content_types=['text'])
def text_handler(message):
    user_id = message.from_user.id
    init_user(user_id)

    text = message.text.strip()

    ignore_buttons = [
        "🔗 Link Arrangement",
        "📸 Set Photo",
        "✅ Use Photo",
        "📢 Auto Forward Channel",
        "📋 Current Channels",
        "🖼 Current Photo",
        "🔘 Auto Forward On/Off",
        "🟢 ON",
        "🔴 OFF",
        "✅ Done",
        "🗑 Clear Channels",
        "⬅️ Back",
        "❌ Disable Photo",
        "Photo 1",
        "Photo 2",
        "Photo 3",
        "Photo 4",
        "Photo 5",
        "Channel 1",
        "Channel 2",
        "Channel 3",
        "Channel 4",
    ]

    if text in ignore_buttons:
        return

    links = extract_links(text)
    clean_text = clean_links_from_text(text)

    if clean_text:
        user_data[user_id]["text_parts"].append(clean_text)

    if links:
        user_data[user_id]["links"].extend(links)
        user_data[user_id]["timer_id"] += 1
        current_timer = user_data[user_id]["timer_id"]

        threading.Thread(
            target=auto_send_after_delay,
            args=(user_id, message.chat.id, current_timer),
            daemon=True
        ).start()

# =========================
# AUTO SEND
# =========================
def auto_send_after_delay(user_id, chat_id, timer_id):
    time.sleep(10)

    if user_id not in user_data:
        return

    if timer_id != user_data[user_id]["timer_id"]:
        return

    send_arranged_message(user_id, chat_id)

def send_arranged_message(user_id, chat_id):
    init_user(user_id)

    data = user_data[user_id]
    settings = user_settings[user_id]

    if not data["links"]:
        return

    unique_links = []
    for link in data["links"]:
        if link not in unique_links:
            unique_links.append(link)

    arranged_text = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(unique_links, start=1):
        arranged_text += f"VIDEO {i} ⤵️\n{link}\n\n"

    original_text = "\n\n".join(part for part in data["text_parts"] if part).strip()
    final_text = arranged_text if not original_text else original_text + "\n\n" + arranged_text

    photo_to_use = None
    if settings["selected_photo_file_id"]:
        photo_to_use = settings["selected_photo_file_id"]
    elif data["photo"]:
        photo_to_use = data["photo"]

    try:
        if photo_to_use:
            if len(final_text) <= 1024:
                bot.send_photo(
                    chat_id,
                    photo_to_use,
                    caption=final_text,
                    reply_markup=main_keyboard()
                )
            else:
                bot.send_photo(
                    chat_id,
                    photo_to_use,
                    caption="FULL VIDEO 👀🌸",
                    reply_markup=main_keyboard()
                )
                bot.send_message(chat_id, final_text, reply_markup=main_keyboard())
        else:
            bot.send_message(chat_id, final_text, reply_markup=main_keyboard())
    except Exception as e:
        print("Send error:", e)

    if settings["auto_forward"] and settings["selected_channels"]:
        for ch in settings["selected_channels"]:
            try:
                if photo_to_use:
                    if len(final_text) <= 1024:
                        bot.send_photo(ch, photo_to_use, caption=final_text)
                    else:
                        bot.send_photo(ch, photo_to_use, caption="FULL VIDEO 👀🌸")
                        bot.send_message(ch, final_text)
                else:
                    bot.send_message(ch, final_text)
            except Exception as e:
                print(f"Forward error to {ch}: {e}")

    user_data[user_id] = {
        "photo": None,
        "text_parts": [],
        "links": [],
        "timer_id": 0,
    }

print("Bot running...")
bot.infinity_polling(skip_pending=True)
