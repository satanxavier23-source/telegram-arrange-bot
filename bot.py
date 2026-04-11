import os
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

user_settings = {}

CHANNELS = {
    "Channel 1": "-1002674664027",
    "Channel 2": "-1002514181198",
    "Channel 3": "-1002427180742",
    "Channel 4": "-1003590340901",
}

PHOTO_SLOTS = ["Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5"]

def init_user(uid):
    if uid not in user_settings:
        user_settings[uid] = {
            "saved_photos": {
                "Photo 1": None,
                "Photo 2": None,
                "Photo 3": None,
                "Photo 4": None,
                "Photo 5": None,
            },
            "selected_photo": None,
            "link_mode": False,
            "thumb_forward_mode": False,
            "selected_channels": [],
            "waiting_photo_slot": None,
            "menu": "main"
        }

def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔗 Link Arrangement")
    kb.row("🚀 Thumb & Auto Forward")
    return kb

def link_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟢 Link Arrange ON", "🔴 Link Arrange OFF")
    kb.row("⬅️ Back")
    return kb

def thumb_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📸 Set Photo", "✅ Use Photo")
    kb.row("📢 Select Channel")
    kb.row("🟢 Thumb ON", "🔴 Thumb OFF")
    kb.row("⬅️ Back")
    return kb

def set_photo_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Photo 1", "Photo 2")
    kb.row("Photo 3", "Photo 4")
    kb.row("Photo 5")
    kb.row("⬅️ Back")
    return kb

def use_photo_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Photo 1", "Photo 2")
    kb.row("Photo 3", "Photo 4")
    kb.row("Photo 5")
    kb.row("⬅️ Back")
    return kb

def channel_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Channel 1", "Channel 2")
    kb.row("Channel 3", "Channel 4")
    kb.row("✅ Done", "🗑 Clear Channels")
    kb.row("⬅️ Back")
    return kb

@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "main"
    bot.send_message(message.chat.id, "Bot ready ✅", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == "⬅️ Back")
def back_btn(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "main"
    bot.send_message(message.chat.id, "Main menu ✅", reply_markup=main_kb())

@bot.message_handler(func=lambda m: m.text == "🔗 Link Arrangement")
def link_menu(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "link"
    bot.send_message(message.chat.id, "Link Arrangement settings", reply_markup=link_kb())

@bot.message_handler(func=lambda m: m.text == "🟢 Link Arrange ON")
def link_on(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["link_mode"] = True
    bot.send_message(message.chat.id, "Link Arrangement ON ✅", reply_markup=link_kb())

@bot.message_handler(func=lambda m: m.text == "🔴 Link Arrange OFF")
def link_off(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["link_mode"] = False
    bot.send_message(message.chat.id, "Link Arrangement OFF ❌", reply_markup=link_kb())

@bot.message_handler(func=lambda m: m.text == "🚀 Thumb & Auto Forward")
def thumb_menu(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "thumb"
    bot.send_message(message.chat.id, "Thumb & Auto Forward settings", reply_markup=thumb_kb())

@bot.message_handler(func=lambda m: m.text == "📸 Set Photo")
def set_photo_menu(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "set_photo"
    bot.send_message(message.chat.id, "Save ചെയ്യേണ്ട photo slot select ചെയ്യൂ", reply_markup=set_photo_kb())

@bot.message_handler(func=lambda m: m.text == "✅ Use Photo")
def use_photo_menu(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "use_photo"
    bot.send_message(message.chat.id, "Use ചെയ്യേണ്ട saved photo select ചെയ്യൂ", reply_markup=use_photo_kb())

@bot.message_handler(func=lambda m: m.text in PHOTO_SLOTS)
def photo_slot_handler(message):
    uid = message.from_user.id
    init_user(uid)

    current_menu = user_settings[uid]["menu"]

    if current_menu == "set_photo":
        user_settings[uid]["waiting_photo_slot"] = message.text
        bot.send_message(
            message.chat.id,
            f"{message.text} ലേക്ക് save ചെയ്യാൻ ഇപ്പോൾ ഒരു photo അയക്കൂ 📸",
            reply_markup=set_photo_kb()
        )
        return

    if current_menu == "use_photo":
        slot = message.text
        photo_id = user_settings[uid]["saved_photos"].get(slot)

        if not photo_id:
            bot.send_message(
                message.chat.id,
                f"{slot} ഇൽ photo save ചെയ്തിട്ടില്ല ❌",
                reply_markup=use_photo_kb()
            )
            return

        user_settings[uid]["selected_photo"] = slot
        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=f"{slot} selected ✅",
            reply_markup=thumb_kb()
        )
        user_settings[uid]["menu"] = "thumb"
        return

@bot.message_handler(func=lambda m: m.text == "📢 Select Channel")
def select_channel_menu(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "channel"
    bot.send_message(message.chat.id, "Channels select ചെയ്യൂ", reply_markup=channel_kb())

@bot.message_handler(func=lambda m: m.text in CHANNELS.keys())
def channel_select(message):
    uid = message.from_user.id
    init_user(uid)

    channel_id = CHANNELS[message.text]
    selected = user_settings[uid]["selected_channels"]

    if channel_id in selected:
        selected.remove(channel_id)
        bot.send_message(message.chat.id, f"{message.text} removed ❌", reply_markup=channel_kb())
    else:
        selected.append(channel_id)
        bot.send_message(message.chat.id, f"{message.text} added ✅", reply_markup=channel_kb())

@bot.message_handler(func=lambda m: m.text == "✅ Done")
def done_channels(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["menu"] = "thumb"
    bot.send_message(message.chat.id, "Channels saved ✅", reply_markup=thumb_kb())

@bot.message_handler(func=lambda m: m.text == "🗑 Clear Channels")
def clear_channels(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["selected_channels"] = []
    bot.send_message(message.chat.id, "Channels cleared ✅", reply_markup=channel_kb())

@bot.message_handler(func=lambda m: m.text == "🟢 Thumb ON")
def thumb_on(message):
    uid = message.from_user.id
    init_user(uid)

    if not user_settings[uid]["selected_photo"]:
        bot.send_message(
            message.chat.id,
            "Aadyam ✅ Use Photo il poi Photo 1 / Photo 2 select ചെയ്യൂ ❌",
            reply_markup=thumb_kb()
        )
        return

    user_settings[uid]["thumb_forward_mode"] = True
    bot.send_message(message.chat.id, "Thumb & Auto Forward ON ✅🔥", reply_markup=thumb_kb())

@bot.message_handler(func=lambda m: m.text == "🔴 Thumb OFF")
def thumb_off(message):
    uid = message.from_user.id
    init_user(uid)
    user_settings[uid]["thumb_forward_mode"] = False
    bot.send_message(message.chat.id, "Thumb & Auto Forward OFF ❌", reply_markup=thumb_kb())

@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    uid = message.from_user.id
    init_user(uid)

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""

    waiting_slot = user_settings[uid]["waiting_photo_slot"]

    # Set Photo flow
    if waiting_slot:
        user_settings[uid]["saved_photos"][waiting_slot] = photo_id
        user_settings[uid]["waiting_photo_slot"] = None
        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=f"{waiting_slot} save ചെയ്തു ✅",
            reply_markup=thumb_kb()
        )
        user_settings[uid]["menu"] = "thumb"
        return

    # Thumb & Auto Forward ON
    if user_settings[uid]["thumb_forward_mode"]:
        selected_slot = user_settings[uid]["selected_photo"]
        selected_photo_id = user_settings[uid]["saved_photos"].get(selected_slot) if selected_slot else None

        if not selected_photo_id:
            bot.send_message(
                message.chat.id,
                "Selected photo ഇല്ല. ആദ്യം ✅ Use Photo വഴി ഒരു photo select ചെയ്യൂ ❌",
                reply_markup=thumb_kb()
            )
            return

        # userക്ക് selected photo + original caption
        try:
            bot.send_photo(message.chat.id, selected_photo_id, caption=caption)
        except Exception as e:
            print("Send error:", e)

        # selected channelsലേക്ക് same message forward
        for ch in user_settings[uid]["selected_channels"]:
            try:
                bot.send_photo(ch, selected_photo_id, caption=caption)
            except Exception as e:
                print("Forward error:", e)
        return

    # Link arrangement OFF ആയാൽ ഒന്നും ചെയ്യണ്ട
    if not user_settings[uid]["link_mode"]:
        return

    # Link arrangement ON
    bot.send_photo(message.chat.id, photo_id, caption=caption)

@bot.message_handler(content_types=["text"])
def text_handler(message):
    uid = message.from_user.id
    init_user(uid)

    ignore = [
        "🔗 Link Arrangement",
        "🚀 Thumb & Auto Forward",
        "🟢 Link Arrange ON",
        "🔴 Link Arrange OFF",
        "📸 Set Photo",
        "✅ Use Photo",
        "📢 Select Channel",
        "🟢 Thumb ON",
        "🔴 Thumb OFF",
        "✅ Done",
        "🗑 Clear Channels",
        "⬅️ Back",
        "Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5",
        "Channel 1", "Channel 2", "Channel 3", "Channel 4"
    ]

    if message.text in ignore:
        return

    # Thumb & Auto Forward ON + text only
    if user_settings[uid]["thumb_forward_mode"]:
        try:
            bot.send_message(message.chat.id, message.text)
        except Exception as e:
            print("Send text error:", e)

        for ch in user_settings[uid]["selected_channels"]:
            try:
                bot.send_message(ch, message.text)
            except Exception as e:
                print("Forward text error:", e)
        return

    # Link arrangement ON
    if user_settings[uid]["link_mode"]:
        bot.send_message(message.chat.id, message.text)

print("Bot running...")
bot.infinity_polling(skip_pending=True)
