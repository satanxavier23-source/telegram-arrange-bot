import os
import re
import telebot
from telebot import types

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set")

bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_IDS = [6630347046, 7194569468]

CHANNELS = {
    "Channel 1": "-1002674664027",
    "Channel 2": "-1002514181198",
    "Channel 3": "-1002427180742",
    "Channel 4": "-1003590340901",
}

THUMB_SLOTS = ["Photo 1", "Photo 2", "Photo 3", "Photo 4"]

user_data = {}


def is_admin(user_id):
    return user_id in ADMIN_IDS


def init_user(uid):
    if uid not in user_data:
        user_data[uid] = {
            "waiting_thumb_slot": None,
            "thumb_mode": False,
            "selected_thumb_slot": None,
            "saved_thumbs": {
                "Photo 1": None,
                "Photo 2": None,
                "Photo 3": None,
                "Photo 4": None,
            },
            "arrange_mode": False,
            "auto_forward": False,
            "selected_channels": [],
            "thumb_action": None
        }


def extract_links(text):
    if not text:
        return []
    matches = re.findall(r'https?://[^\s]+', text)
    cleaned = []
    for link in matches:
        link = link.strip().rstrip("),.?!;:'\"")
        if link not in cleaned:
            cleaned.append(link)
    return cleaned


def build_arranged_caption(text):
    if not text:
        return ""

    links = extract_links(text)
    if not links:
        return text[:1024]

    final_text = "FULL VIDEO 👀🌸\n\n"
    for i, link in enumerate(links, start=1):
        final_text += f"VIDEO {i} ⤵️\n{link}\n\n"

    return final_text[:1024]


def selected_channel_names(uid):
    names = []
    for name, cid in CHANNELS.items():
        if cid in user_data[uid]["selected_channels"]:
            names.append(name)
    return names


def get_selected_thumb(uid):
    slot = user_data[uid]["selected_thumb_slot"]
    if not slot:
        return None
    return user_data[uid]["saved_thumbs"].get(slot)


def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📸 Set Thumb", "✅ Use Thumb")
    kb.row("🖼 Thumb ON", "❌ Thumb OFF")
    kb.row("🔗 Arrange ON", "🚫 Arrange OFF")
    kb.row("📢 Select Channel")
    kb.row("🟢 Auto Forward ON", "🔴 Auto Forward OFF")
    kb.row("👁 Current Thumb", "📊 Current Settings")
    return kb


def slot_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Photo 1", "Photo 2")
    kb.row("Photo 3", "Photo 4")
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
        "🔥 Multi Thumb Bot Ready ✅\n\n"
        "Photo 1 / Photo 2 / Photo 3 / Photo 4 save ചെയ്യാം.\n"
        "Thumb Change, Link Arrange, Auto Forward support ഉണ്ട്.",
        reply_markup=main_kb()
    )


@bot.message_handler(func=lambda m: m.text == "📸 Set Thumb")
def set_thumb_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_action"] = "set"
    bot.send_message(message.chat.id, "Save ചെയ്യാൻ slot select ചെയ്യൂ", reply_markup=slot_kb())


@bot.message_handler(func=lambda m: m.text == "✅ Use Thumb")
def use_thumb_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_action"] = "use"
    bot.send_message(message.chat.id, "Use ചെയ്യാൻ slot select ചെയ്യൂ", reply_markup=slot_kb())


@bot.message_handler(func=lambda m: m.text in THUMB_SLOTS)
def thumb_slot_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    slot = message.text
    action = user_data[uid]["thumb_action"]

    if action == "set":
        user_data[uid]["waiting_thumb_slot"] = slot
        bot.send_message(message.chat.id, f"{slot} ലേക്ക് save ചെയ്യാൻ ഇപ്പോൾ photo അയക്കൂ 📸", reply_markup=slot_kb())
        return

    if action == "use":
        thumb = user_data[uid]["saved_thumbs"].get(slot)
        if not thumb:
            bot.send_message(message.chat.id, f"{slot} il thumb ഇല്ല ❌", reply_markup=slot_kb())
            return

        user_data[uid]["selected_thumb_slot"] = slot
        bot.send_photo(
            message.chat.id,
            thumb,
            caption=f"{slot} selected ✅",
            reply_markup=main_kb()
        )
        return


@bot.message_handler(func=lambda m: m.text == "🖼 Thumb ON")
def thumb_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)

    if not user_data[uid]["selected_thumb_slot"]:
        bot.send_message(message.chat.id, "ആദ്യം ✅ Use Thumb ചെയ്ത് ഒരു slot select ചെയ്യൂ ❌", reply_markup=main_kb())
        return

    user_data[uid]["thumb_mode"] = True
    bot.send_message(message.chat.id, "Thumb Change ON ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "❌ Thumb OFF")
def thumb_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_mode"] = False
    bot.send_message(message.chat.id, "Thumb Change OFF ❌", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🔗 Arrange ON")
def arrange_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["arrange_mode"] = True
    bot.send_message(message.chat.id, "Arrange Link ON ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🚫 Arrange OFF")
def arrange_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["arrange_mode"] = False
    bot.send_message(message.chat.id, "Arrange Link OFF ❌", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "📢 Select Channel")
def select_channel(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    bot.send_message(message.chat.id, "Forward ചെയ്യേണ്ട channels select ചെയ്യൂ 👇", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text in CHANNELS.keys())
def channel_toggle(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    name = message.text
    cid = CHANNELS[name]

    if cid in user_data[uid]["selected_channels"]:
        user_data[uid]["selected_channels"].remove(cid)
        bot.send_message(message.chat.id, f"{name} removed ❌", reply_markup=channel_kb())
    else:
        user_data[uid]["selected_channels"].append(cid)
        bot.send_message(message.chat.id, f"{name} added ✅", reply_markup=channel_kb())


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
    user_data[uid]["selected_channels"] = []
    bot.send_message(message.chat.id, "Channels cleared ✅", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Auto Forward ON")
def auto_forward_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["auto_forward"] = True
    bot.send_message(message.chat.id, "Auto Forward ON ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🔴 Auto Forward OFF")
def auto_forward_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["auto_forward"] = False
    bot.send_message(message.chat.id, "Auto Forward OFF ❌", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "👁 Current Thumb")
def current_thumb(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)

    thumb = get_selected_thumb(uid)
    slot = user_data[uid]["selected_thumb_slot"]

    if not thumb:
        bot.send_message(message.chat.id, "Current thumb ഇല്ല ❌", reply_markup=main_kb())
        return

    bot.send_photo(message.chat.id, thumb, caption=f"Current Thumb: {slot} ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "📊 Current Settings")
def current_settings(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)

    thumb_mode = "ON ✅" if user_data[uid]["thumb_mode"] else "OFF ❌"
    arrange_mode = "ON ✅" if user_data[uid]["arrange_mode"] else "OFF ❌"
    auto_forward = "ON ✅" if user_data[uid]["auto_forward"] else "OFF ❌"
    selected_thumb = user_data[uid]["selected_thumb_slot"] or "None ❌"

    channels = selected_channel_names(uid)
    channels_text = "\n".join(channels) if channels else "None ❌"

    text = (
        f"Selected Thumb: {selected_thumb}\n"
        f"Thumb Mode: {thumb_mode}\n"
        f"Arrange Mode: {arrange_mode}\n"
        f"Auto Forward: {auto_forward}\n\n"
        f"Selected Channels:\n{channels_text}"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "⬅️ Back")
def back_btn(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return
    bot.send_message(message.chat.id, "Main menu ✅", reply_markup=main_kb())


@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    incoming_photo = message.photo[-1].file_id
    caption = message.caption or ""

    waiting_slot = user_data[uid]["waiting_thumb_slot"]
    if waiting_slot:
        user_data[uid]["saved_thumbs"][waiting_slot] = incoming_photo
        user_data[uid]["waiting_thumb_slot"] = None
        user_data[uid]["thumb_action"] = None
        bot.send_photo(
            message.chat.id,
            incoming_photo,
            caption=f"{waiting_slot} saved ✅",
            reply_markup=main_kb()
        )
        return

    send_photo = incoming_photo
    if user_data[uid]["thumb_mode"]:
        selected_thumb = get_selected_thumb(uid)
        if selected_thumb:
            send_photo = selected_thumb

    final_caption = caption[:1024] if caption else ""
    if user_data[uid]["arrange_mode"]:
        final_caption = build_arranged_caption(caption)

    bot.send_photo(
        message.chat.id,
        send_photo,
        caption=final_caption,
        reply_markup=main_kb()
    )

    if user_data[uid]["auto_forward"]:
        for ch in user_data[uid]["selected_channels"]:
            try:
                bot.send_photo(ch, send_photo, caption=final_caption)
            except Exception as e:
                print("Forward photo error:", e)


@bot.message_handler(content_types=["text"])
def text_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    ignore = {
        "📸 Set Thumb", "✅ Use Thumb",
        "🖼 Thumb ON", "❌ Thumb OFF",
        "🔗 Arrange ON", "🚫 Arrange OFF",
        "📢 Select Channel",
        "🟢 Auto Forward ON", "🔴 Auto Forward OFF",
        "👁 Current Thumb", "📊 Current Settings",
        "Channel 1", "Channel 2", "Channel 3", "Channel 4",
        "✅ Done", "🗑 Clear Channels", "⬅️ Back",
        "Photo 1", "Photo 2", "Photo 3", "Photo 4"
    }

    if message.text in ignore:
        return

    final_text = message.text
    if user_data[uid]["arrange_mode"]:
        final_text = build_arranged_caption(message.text)

    if user_data[uid]["thumb_mode"]:
        selected_thumb = get_selected_thumb(uid)
        if selected_thumb:
            bot.send_photo(
                message.chat.id,
                selected_thumb,
                caption=final_text[:1024],
                reply_markup=main_kb()
            )

            if user_data[uid]["auto_forward"]:
                for ch in user_data[uid]["selected_channels"]:
                    try:
                        bot.send_photo(ch, selected_thumb, caption=final_text[:1024])
                    except Exception as e:
                        print("Forward text-photo error:", e)
            return

    bot.send_message(message.chat.id, final_text[:4096], reply_markup=main_kb())

    if user_data[uid]["auto_forward"]:
        for ch in user_data[uid]["selected_channels"]:
            try:
                bot.send_message(ch, final_text[:4096])
            except Exception as e:
                print("Forward text error:", e)


print("Bot running...")
bot.remove_webhook()
bot.infinity_polling(skip_pending=True, none_stop=True)
