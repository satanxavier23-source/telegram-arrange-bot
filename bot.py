import os
import re
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_IDS = [6630347046, 7194569468]

CHANNELS = {
    "Channel 1": "-1002674664027",
    "Channel 2": "-1002514181198",
    "Channel 3": "-1002427180742",
    "Channel 4": "-1003590340901",
}

user_settings = {}


def is_admin(user_id):
    return user_id in ADMIN_IDS


def init_user(uid):
    if uid not in user_settings:
        user_settings[uid] = {
            "arrange_mode": False,
            "auto_forward": False,
            "selected_channels": [],
        }


def extract_links(text):
    if not text:
        return []
    return re.findall(r'https?://\S+', text)


def build_arranged_text(links):
    unique_links = []
    for link in links:
        if link not in unique_links:
            unique_links.append(link)

    final_text = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(unique_links, start=1):
        final_text += f"VIDEO {i} ⤵️\n{link}\n\n"
    return final_text.strip()


def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔗 Arrange Link")
    kb.row("📢 Select Channel")
    kb.row("🟢 Auto Forward ON", "🔴 Auto Forward OFF")
    kb.row("📢 Current Forward Channels", "📊 Current Settings")
    kb.row("❓ Help")
    return kb


def arrange_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟢 Arrange ON", "🔴 Arrange OFF")
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
    if not is_admin(uid):
        bot.reply_to(message, "❌ Admin only bot")
        return

    init_user(uid)
    bot.send_message(
        message.chat.id,
        "🔥 Welcome\n\n"
        "Links only arrange + auto forward bot ✅\n\n"
        "Use buttons below 👇",
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda m: not is_admin(m.from_user.id), content_types=[
    "text", "photo", "video", "document", "audio", "voice", "sticker"
])
def block_non_admin(message):
    bot.reply_to(message, "❌ Admin only bot")


@bot.message_handler(func=lambda m: m.text == "❓ Help")
def help_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    bot.send_message(
        message.chat.id,
        "HOW TO USE\n\n"
        "1. Open 🔗 Arrange Link\n"
        "2. Turn ON arrange mode\n"
        "3. Open 📢 Select Channel and choose channels\n"
        "4. Turn ON auto forward\n"
        "5. Send photo + links or text + links\n\n"
        "Bot removes all extra text and keeps links only.",
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda m: m.text == "📊 Current Settings")
def current_settings(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    settings = user_settings[uid]

    arrange_mode = "ON ✅" if settings["arrange_mode"] else "OFF ❌"
    auto_forward = "ON ✅" if settings["auto_forward"] else "OFF ❌"

    if settings["selected_channels"]:
        channel_names = []
        for name, cid in CHANNELS.items():
            if cid in settings["selected_channels"]:
                channel_names.append(name)
        channels_text = "\n".join(channel_names) if channel_names else "None ❌"
    else:
        channels_text = "None ❌"

    text = (
        "📊 CURRENT SETTINGS\n\n"
        f"🔗 Arrange Mode: {arrange_mode}\n"
        f"📈 Auto Forward: {auto_forward}\n\n"
        f"📢 Selected Channels:\n{channels_text}"
    )

    bot.send_message(message.chat.id, text, reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "📢 Current Forward Channels")
def current_forward_channels(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    selected = user_settings[uid]["selected_channels"]

    if not selected:
        bot.send_message(
            message.chat.id,
            "No forward channels selected ❌",
            reply_markup=main_kb()
        )
        return

    channel_names = []
    for name, cid in CHANNELS.items():
        if cid in selected:
            channel_names.append(f"✅ {name}")

    text = "📢 Current Forward Channels\n\n" + "\n".join(channel_names)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda m: m.text == "⬅️ Back")
def back_btn(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    bot.send_message(message.chat.id, "Main menu ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🔗 Arrange Link")
def arrange_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(
        message.chat.id,
        "Arrange Link settings",
        reply_markup=arrange_kb()
    )


@bot.message_handler(func=lambda m: m.text == "🟢 Arrange ON")
def arrange_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["arrange_mode"] = True
    bot.send_message(
        message.chat.id,
        "Arrange Link ON ✅",
        reply_markup=arrange_kb()
    )


@bot.message_handler(func=lambda m: m.text == "🔴 Arrange OFF")
def arrange_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["arrange_mode"] = False
    bot.send_message(
        message.chat.id,
        "Arrange Link OFF ❌",
        reply_markup=arrange_kb()
    )


@bot.message_handler(func=lambda m: m.text == "📢 Select Channel")
def select_channel_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(message.chat.id, "Select channels", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text in CHANNELS.keys())
def channel_select(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    channel_id = CHANNELS[message.text]
    selected = user_settings[uid]["selected_channels"]

    if channel_id in selected:
        selected.remove(channel_id)
        bot.send_message(
            message.chat.id,
            f"{message.text} removed ❌",
            reply_markup=channel_kb()
        )
    else:
        selected.append(channel_id)
        bot.send_message(
            message.chat.id,
            f"{message.text} added ✅",
            reply_markup=channel_kb()
        )


@bot.message_handler(func=lambda m: m.text == "✅ Done")
def done_channels(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    bot.send_message(message.chat.id, "Channels saved ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🗑 Clear Channels")
def clear_channels(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["selected_channels"] = []
    bot.send_message(message.chat.id, "Channels cleared ✅", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Auto Forward ON")
def auto_forward_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["auto_forward"] = True
    bot.send_message(message.chat.id, "Auto Forward ON ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🔴 Auto Forward OFF")
def auto_forward_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["auto_forward"] = False
    bot.send_message(message.chat.id, "Auto Forward OFF ❌", reply_markup=main_kb())


@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    if not user_settings[uid]["arrange_mode"]:
        return

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""
    links = extract_links(caption)

    if not links:
        return

    final_caption = build_arranged_text(links)

    try:
        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=final_caption[:1024],
            reply_markup=main_kb()
        )
    except Exception as e:
        print("Photo send error:", e)

    if user_settings[uid]["auto_forward"]:
        for ch in user_settings[uid]["selected_channels"]:
            try:
                bot.send_photo(ch, photo_id, caption=final_caption[:1024])
            except Exception as e:
                print("Forward photo error:", e)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    ignore = {
        "🔗 Arrange Link",
        "🟢 Arrange ON",
        "🔴 Arrange OFF",
        "📢 Select Channel",
        "🟢 Auto Forward ON",
        "🔴 Auto Forward OFF",
        "📢 Current Forward Channels",
        "📊 Current Settings",
        "❓ Help",
        "✅ Done",
        "🗑 Clear Channels",
        "⬅️ Back",
        "Channel 1", "Channel 2", "Channel 3", "Channel 4"
    }

    if message.text in ignore:
        return

    if not user_settings[uid]["arrange_mode"]:
        return

    links = extract_links(message.text)

    if not links:
        return

    final_text = build_arranged_text(links)

    try:
        bot.send_message(
            message.chat.id,
            final_text,
            reply_markup=main_kb()
        )
    except Exception as e:
        print("Text send error:", e)

    if user_settings[uid]["auto_forward"]:
        for ch in user_settings[uid]["selected_channels"]:
            try:
                bot.send_message(ch, final_text)
            except Exception as e:
                print("Forward text error:", e)


print("Bot running...")
bot.infinity_polling(skip_pending=True)
