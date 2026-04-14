import os
import re
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# ADMINS
# =========================
ADMIN_IDS = [6630347046, 7194569468]

# =========================
# CHANNELS
# =========================
CHANNELS = {
    "Channel 1": "-1002674664027",
    "Channel 2": "-1002514181198",
    "Channel 3": "-1002427180742",
    "Channel 4": "-1003590340901",
}

PHOTO_SLOTS = ["Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5"]

# =========================
# STORAGE
# =========================
user_settings = {}


# =========================
# HELPERS
# =========================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def init_user(uid: int) -> None:
    if uid not in user_settings:
        user_settings[uid] = {
            "arrange_mode": False,
            "thumb_mode": False,
            "auto_forward": False,
            "selected_channels": [],
            "saved_photos": {
                "Photo 1": None,
                "Photo 2": None,
                "Photo 3": None,
                "Photo 4": None,
                "Photo 5": None,
            },
            "selected_photo": None,
            "waiting_photo_slot": None,
        }


def extract_links(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r'https?://\S+', text)


def build_arranged_text(links: list[str]) -> str:
    unique_links = []
    for link in links:
        if link not in unique_links:
            unique_links.append(link)

    final_text = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(unique_links, start=1):
        final_text += f"VIDEO {i} ⤵️\n{link}\n\n"
    return final_text.strip()


def get_selected_channel_names(uid: int) -> list[str]:
    selected = user_settings[uid]["selected_channels"]
    names = []
    for name, cid in CHANNELS.items():
        if cid in selected:
            names.append(name)
    return names


# =========================
# KEYBOARDS
# =========================
def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🔗 Arrange Link", "🖼 Thumb Change")
    kb.row("📸 Set Photo", "✅ Use Photo")
    kb.row("👁 Current Photo", "📢 Select Channel")
    kb.row("🟢 Auto Forward ON", "🔴 Auto Forward OFF")
    kb.row("📢 Current Forward Channels", "📊 Current Settings")
    kb.row("❓ Help")
    return kb


def arrange_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟢 Arrange ON", "🔴 Arrange OFF")
    kb.row("⬅️ Back")
    return kb


def thumb_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("🟢 Thumb ON", "🔴 Thumb OFF")
    kb.row("⬅️ Back")
    return kb


def photo_slot_kb():
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


# =========================
# START / HELP
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    uid = message.from_user.id

    if not is_admin(uid):
        bot.reply_to(message, "❌ Admin only bot")
        return

    init_user(uid)

    bot.send_message(
        message.chat.id,
        "🔥 Welcome to Safe Arrange Bot\n\n"
        "✅ Link arrange\n"
        "✅ Thumb change\n"
        "✅ Auto forward\n"
        "✅ Photo 1 to Photo 5 support\n\n"
        "Buttons use ചെയ്യൂ 👇",
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda m: m.text == "❓ Help")
def help_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    bot.send_message(
        message.chat.id,
        "📌 എങ്ങനെ ഉപയോഗിക്കാം\n\n"
        "1. 🔗 Arrange Link → ON ആക്കൂ\n"
        "2. 📸 Set Photo → Photo 1 മുതൽ Photo 5 വരെ save ചെയ്യാം\n"
        "3. ✅ Use Photo → use ചെയ്യേണ്ട photo select ചെയ്യാം\n"
        "4. 🖼 Thumb Change → Thumb ON ആക്കാം\n"
        "5. 📢 Select Channel → channels select ചെയ്യൂ\n"
        "6. 🟢 Auto Forward ON ആക്കൂ\n\n"
        "ഇനി text + links അല്ലെങ്കിൽ photo + links അയച്ചാൽ:\n"
        "• links arrange ചെയ്യും\n"
        "• Thumb ON ആണെങ്കിൽ selected photo use ചെയ്യും\n"
        "• Auto Forward ON ആണെങ്കിൽ channelsലേക്ക് പോവും",
        reply_markup=main_kb()
    )


# =========================
# BLOCK NON ADMINS
# =========================
@bot.message_handler(func=lambda m: not is_admin(m.from_user.id), content_types=[
    "text", "photo", "video", "document", "audio", "voice", "sticker"
])
def block_non_admin(message):
    bot.reply_to(message, "❌ Admin only bot")


# =========================
# NAVIGATION
# =========================
@bot.message_handler(func=lambda m: m.text == "⬅️ Back")
def back_btn(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    bot.send_message(message.chat.id, "Main menu ✅", reply_markup=main_kb())


# =========================
# CURRENT SETTINGS
# =========================
@bot.message_handler(func=lambda m: m.text == "📊 Current Settings")
def current_settings(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    arrange_mode = "ON ✅" if user_settings[uid]["arrange_mode"] else "OFF ❌"
    thumb_mode = "ON ✅" if user_settings[uid]["thumb_mode"] else "OFF ❌"
    auto_forward = "ON ✅" if user_settings[uid]["auto_forward"] else "OFF ❌"
    selected_photo = user_settings[uid]["selected_photo"] or "None ❌"

    channel_names = get_selected_channel_names(uid)
    channels_text = "\n".join(channel_names) if channel_names else "None ❌"

    text = (
        "📊 CURRENT SETTINGS\n\n"
        f"🔗 Arrange Mode: {arrange_mode}\n"
        f"🖼 Thumb Mode: {thumb_mode}\n"
        f"📈 Auto Forward: {auto_forward}\n"
        f"📸 Selected Photo: {selected_photo}\n\n"
        f"📢 Selected Channels:\n{channels_text}"
    )

    bot.send_message(message.chat.id, text, reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "📢 Current Forward Channels")
def current_forward_channels(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    names = get_selected_channel_names(uid)

    if not names:
        bot.send_message(
            message.chat.id,
            "No forward channels selected ❌",
            reply_markup=main_kb()
        )
        return

    bot.send_message(
        message.chat.id,
        "📢 Current Forward Channels\n\n" + "\n".join(f"✅ {name}" for name in names),
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda m: m.text == "👁 Current Photo")
def current_photo_preview(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    selected_slot = user_settings[uid]["selected_photo"]
    if not selected_slot:
        bot.send_message(
            message.chat.id,
            "No photo selected ❌",
            reply_markup=main_kb()
        )
        return

    photo_id = user_settings[uid]["saved_photos"].get(selected_slot)
    if not photo_id:
        bot.send_message(
            message.chat.id,
            "Selected photo not found ❌",
            reply_markup=main_kb()
        )
        return

    bot.send_photo(
        message.chat.id,
        photo_id,
        caption=f"Current Photo: {selected_slot} ✅",
        reply_markup=main_kb()
    )


# =========================
# ARRANGE MODE
# =========================
@bot.message_handler(func=lambda m: m.text == "🔗 Arrange Link")
def arrange_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(message.chat.id, "Arrange Link settings", reply_markup=arrange_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Arrange ON")
def arrange_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["arrange_mode"] = True
    bot.send_message(message.chat.id, "Arrange Link ON ✅", reply_markup=arrange_kb())


@bot.message_handler(func=lambda m: m.text == "🔴 Arrange OFF")
def arrange_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["arrange_mode"] = False
    bot.send_message(message.chat.id, "Arrange Link OFF ❌", reply_markup=arrange_kb())


# =========================
# THUMB MODE
# =========================
@bot.message_handler(func=lambda m: m.text == "🖼 Thumb Change")
def thumb_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(message.chat.id, "Thumb settings", reply_markup=thumb_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Thumb ON")
def thumb_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    if not user_settings[uid]["selected_photo"]:
        bot.send_message(
            message.chat.id,
            "Aadyam ✅ Use Photo use ചെയ്ത് ഒരു photo select ചെയ്യൂ ❌",
            reply_markup=thumb_kb()
        )
        return

    user_settings[uid]["thumb_mode"] = True
    bot.send_message(message.chat.id, "Thumb ON ✅", reply_markup=thumb_kb())


@bot.message_handler(func=lambda m: m.text == "🔴 Thumb OFF")
def thumb_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["thumb_mode"] = False
    bot.send_message(message.chat.id, "Thumb OFF ❌", reply_markup=thumb_kb())


# =========================
# SET / USE PHOTO
# =========================
@bot.message_handler(func=lambda m: m.text == "📸 Set Photo")
def set_photo_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(
        message.chat.id,
        "Save ചെയ്യാൻ slot select ചെയ്യൂ",
        reply_markup=photo_slot_kb()
    )


@bot.message_handler(func=lambda m: m.text == "✅ Use Photo")
def use_photo_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(
        message.chat.id,
        "Use ചെയ്യാൻ slot select ചെയ്യൂ",
        reply_markup=photo_slot_kb()
    )


@bot.message_handler(func=lambda m: m.text in PHOTO_SLOTS)
def photo_slot_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    slot = message.text

    # if photo already exists in this slot, treat as selection when not waiting
    if user_settings[uid]["saved_photos"].get(slot) and user_settings[uid]["waiting_photo_slot"] is None:
        user_settings[uid]["selected_photo"] = slot
        bot.send_photo(
            message.chat.id,
            user_settings[uid]["saved_photos"][slot],
            caption=f"{slot} selected ✅",
            reply_markup=main_kb()
        )
        return

    user_settings[uid]["waiting_photo_slot"] = slot
    bot.send_message(
        message.chat.id,
        f"{slot} ലേക്ക് save ചെയ്യാൻ ഇപ്പോൾ photo അയക്കൂ 📸",
        reply_markup=photo_slot_kb()
    )


# =========================
# CHANNEL SELECT
# =========================
@bot.message_handler(func=lambda m: m.text == "📢 Select Channel")
def select_channel_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(
        message.chat.id,
        "Forward ചെയ്യേണ്ട channels select ചെയ്യൂ 👇",
        reply_markup=channel_kb()
    )


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
            f"{message.text} remove ചെയ്തു ❌",
            reply_markup=channel_kb()
        )
    else:
        selected.append(channel_id)
        bot.send_message(
            message.chat.id,
            f"{message.text} add ചെയ്തു ✅",
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


# =========================
# AUTO FORWARD
# =========================
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


# =========================
# TEXT HANDLER
# =========================
@bot.message_handler(content_types=["text"])
def text_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    ignore = {
        "🔗 Arrange Link",
        "🖼 Thumb Change",
        "📸 Set Photo",
        "✅ Use Photo",
        "👁 Current Photo",
        "🟢 Arrange ON",
        "🔴 Arrange OFF",
        "🟢 Thumb ON",
        "🔴 Thumb OFF",
        "📢 Select Channel",
        "🟢 Auto Forward ON",
        "🔴 Auto Forward OFF",
        "📢 Current Forward Channels",
        "📊 Current Settings",
        "❓ Help",
        "✅ Done",
        "🗑 Clear Channels",
        "⬅️ Back",
        "Channel 1", "Channel 2", "Channel 3", "Channel 4",
        "Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5"
    }

    if message.text in ignore:
        return

    if not user_settings[uid]["arrange_mode"]:
        return

    links = extract_links(message.text)
    if not links:
        return

    final_text = build_arranged_text(links)

    bot.send_message(
        message.chat.id,
        final_text,
        reply_markup=main_kb()
    )

    if user_settings[uid]["auto_forward"]:
        for ch in user_settings[uid]["selected_channels"]:
            try:
                bot.send_message(ch, final_text)
            except Exception as e:
                print("Forward text error:", e)


# =========================
# PHOTO HANDLER
# =========================
@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    photo_id = message.photo[-1].file_id
    caption = message.caption or ""

    # save selected slot photo
    if user_settings[uid]["waiting_photo_slot"]:
        slot = user_settings[uid]["waiting_photo_slot"]
        user_settings[uid]["saved_photos"][slot] = photo_id
        user_settings[uid]["waiting_photo_slot"] = None

        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=f"{slot} saved ✅",
            reply_markup=main_kb()
        )
        return

    if not user_settings[uid]["arrange_mode"]:
        return

    links = extract_links(caption)
    if not links:
        return

    final_caption = build_arranged_text(links)

    send_photo_id = photo_id
    if user_settings[uid]["thumb_mode"] and user_settings[uid]["selected_photo"]:
        saved = user_settings[uid]["saved_photos"].get(user_settings[uid]["selected_photo"])
        if saved:
            send_photo_id = saved

    bot.send_photo(
        message.chat.id,
        send_photo_id,
        caption=final_caption[:1024],
        reply_markup=main_kb()
    )

    if user_settings[uid]["auto_forward"]:
        for ch in user_settings[uid]["selected_channels"]:
            try:
                bot.send_photo(ch, send_photo_id, caption=final_caption[:1024])
            except Exception as e:
                print("Forward photo error:", e)


print("Bot running...")
bot.infinity_polling(skip_pending=True)
