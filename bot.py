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


def is_admin(uid):
    return uid in ADMIN_IDS


def init_user(uid):
    if uid not in user_data:
        user_data[uid] = {
            "thumb_mode": False,
            "arrange_mode": False,
            "text_edit_mode": False,
            "auto_forward": False,
            "selected_channels": [],
            "selected_thumb": None,
            "waiting_thumb": None,
            "thumb_action": None,
            "thumbs": {s: None for s in THUMB_SLOTS}
        }


def extract_links(text):
    return re.findall(r'https?://\S+', text or "")


def build_links(links):
    txt = "FULL VIDEO 👀🌸\n\n"
    for i, l in enumerate(links, 1):
        txt += f"VIDEO {i} ⤵️\n{l}\n\n"
    return txt.strip()


def extract_malayalam(text):
    lines = text.splitlines()
    result = []

    for l in lines:
        l = l.strip()
        if not l:
            continue

        if re.search(r'https?://', l):
            continue

        if re.search(r'[\u0D00-\u0D7F]', l):
            result.append(l)

    # footer remove
    if len(result) > 2:
        result = result[:-2]
    elif len(result) > 1:
        result = result[:-1]

    return result


def text_edit(text):
    mal = extract_malayalam(text)
    links = extract_links(text)

    final = ""

    if mal:
        final += "\n".join(mal) + "\n\n"

    if links:
        final += build_links(links)

    return final[:1024]


def arrange(text):
    links = extract_links(text)
    if not links:
        return (text or "")[:1024]
    return build_links(links)[:1024]


def get_thumb(uid):
    slot = user_data[uid]["selected_thumb"]
    if not slot:
        return None
    return user_data[uid]["thumbs"][slot]


def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("📸 Set Thumb", "✅ Use Thumb")
    kb.row("🖼 Thumb ON", "❌ Thumb OFF")
    kb.row("🔗 Arrange ON", "🚫 Arrange OFF")
    kb.row("📝 Text Edit ON", "❎ Text Edit OFF")
    kb.row("📢 Select Channel")
    kb.row("🟢 Auto Forward ON", "🔴 Auto Forward OFF")
    kb.row("📊 Current Settings")
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
def start(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    bot.send_message(m.chat.id, "🔥 FINAL BOT READY", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "📸 Set Thumb")
def set_thumb(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_action"] = "set"
    bot.send_message(m.chat.id, "Select slot", reply_markup=slot_kb())


@bot.message_handler(func=lambda m: m.text == "✅ Use Thumb")
def use_thumb(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_action"] = "use"
    bot.send_message(m.chat.id, "Select slot", reply_markup=slot_kb())


@bot.message_handler(func=lambda m: m.text in THUMB_SLOTS)
def thumb_slot(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)

    if user_data[uid]["thumb_action"] == "set":
        user_data[uid]["waiting_thumb"] = m.text
        bot.send_message(m.chat.id, "Send photo now 📸", reply_markup=slot_kb())

    elif user_data[uid]["thumb_action"] == "use":
        if user_data[uid]["thumbs"][m.text]:
            user_data[uid]["selected_thumb"] = m.text
            bot.send_message(m.chat.id, f"{m.text} selected ✅", reply_markup=main_kb())
        else:
            bot.send_message(m.chat.id, f"{m.text} il thumb ഇല്ല ❌", reply_markup=slot_kb())


@bot.message_handler(func=lambda m: m.text == "🖼 Thumb ON")
def t_on(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_mode"] = True
    bot.reply_to(m, "Thumb ON ✅")


@bot.message_handler(func=lambda m: m.text == "❌ Thumb OFF")
def t_off(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["thumb_mode"] = False
    bot.reply_to(m, "Thumb OFF ❌")


@bot.message_handler(func=lambda m: m.text == "🔗 Arrange ON")
def a_on(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["arrange_mode"] = True
    bot.reply_to(m, "Arrange ON")


@bot.message_handler(func=lambda m: m.text == "🚫 Arrange OFF")
def a_off(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["arrange_mode"] = False
    bot.reply_to(m, "Arrange OFF")


@bot.message_handler(func=lambda m: m.text == "📝 Text Edit ON")
def te_on(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["text_edit_mode"] = True
    bot.reply_to(m, "Text Edit ON 🔥")


@bot.message_handler(func=lambda m: m.text == "❎ Text Edit OFF")
def te_off(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["text_edit_mode"] = False
    bot.reply_to(m, "Text Edit OFF")


@bot.message_handler(func=lambda m: m.text == "📢 Select Channel")
def select_channel(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    bot.send_message(m.chat.id, "Select channels", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text in CHANNELS.keys())
def toggle_channel(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)

    cid = CHANNELS[m.text]
    if cid in user_data[uid]["selected_channels"]:
        user_data[uid]["selected_channels"].remove(cid)
        bot.send_message(m.chat.id, f"{m.text} removed ❌", reply_markup=channel_kb())
    else:
        user_data[uid]["selected_channels"].append(cid)
        bot.send_message(m.chat.id, f"{m.text} added ✅", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text == "✅ Done")
def done(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    bot.send_message(m.chat.id, "Channels saved ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🗑 Clear Channels")
def clear_channels(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["selected_channels"] = []
    bot.send_message(m.chat.id, "Channels cleared ✅", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text == "⬅️ Back")
def back(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    bot.send_message(m.chat.id, "Main menu ✅", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Auto Forward ON")
def af_on(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["auto_forward"] = True
    bot.reply_to(m, "Auto Forward ON")


@bot.message_handler(func=lambda m: m.text == "🔴 Auto Forward OFF")
def af_off(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)
    user_data[uid]["auto_forward"] = False
    bot.reply_to(m, "Auto Forward OFF")


@bot.message_handler(func=lambda m: m.text == "📊 Current Settings")
def current_settings(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return
    init_user(uid)

    text = (
        f"Thumb Mode: {'ON ✅' if user_data[uid]['thumb_mode'] else 'OFF ❌'}\n"
        f"Arrange Mode: {'ON ✅' if user_data[uid]['arrange_mode'] else 'OFF ❌'}\n"
        f"Text Edit Mode: {'ON ✅' if user_data[uid]['text_edit_mode'] else 'OFF ❌'}\n"
        f"Auto Forward: {'ON ✅' if user_data[uid]['auto_forward'] else 'OFF ❌'}\n"
        f"Selected Thumb: {user_data[uid]['selected_thumb'] or 'None ❌'}\n"
        f"Selected Channels: {len(user_data[uid]['selected_channels'])}"
    )
    bot.send_message(m.chat.id, text, reply_markup=main_kb())


@bot.message_handler(content_types=["photo"])
def photo(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    photo_id = m.photo[-1].file_id
    cap = m.caption or ""

    if user_data[uid]["waiting_thumb"]:
        slot = user_data[uid]["waiting_thumb"]
        user_data[uid]["thumbs"][slot] = photo_id
        user_data[uid]["waiting_thumb"] = None
        bot.send_message(m.chat.id, f"{slot} saved ✅", reply_markup=main_kb())
        return

    send_photo = photo_id
    if user_data[uid]["thumb_mode"]:
        t = get_thumb(uid)
        if t:
            send_photo = t

    final = cap
    if user_data[uid]["text_edit_mode"]:
        final = text_edit(cap)
    elif user_data[uid]["arrange_mode"]:
        final = arrange(cap)

    bot.send_photo(m.chat.id, send_photo, caption=final, reply_markup=main_kb())

    if user_data[uid]["auto_forward"]:
        for ch in user_data[uid]["selected_channels"]:
            try:
                bot.send_photo(ch, send_photo, caption=final)
            except Exception as e:
                print("Forward photo error:", e)


@bot.message_handler(content_types=["text"])
def text(m):
    uid = m.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    ignore = {
        "📸 Set Thumb", "✅ Use Thumb",
        "🖼 Thumb ON", "❌ Thumb OFF",
        "🔗 Arrange ON", "🚫 Arrange OFF",
        "📝 Text Edit ON", "❎ Text Edit OFF",
        "📢 Select Channel",
        "🟢 Auto Forward ON", "🔴 Auto Forward OFF",
        "📊 Current Settings",
        "Channel 1", "Channel 2", "Channel 3", "Channel 4",
        "✅ Done", "🗑 Clear Channels", "⬅️ Back",
        "Photo 1", "Photo 2", "Photo 3", "Photo 4"
    }

    if m.text in ignore:
        return

    txt = m.text

    if user_data[uid]["text_edit_mode"]:
        txt = text_edit(txt)
    elif user_data[uid]["arrange_mode"]:
        txt = arrange(txt)

    if user_data[uid]["thumb_mode"]:
        t = get_thumb(uid)
        if t:
            bot.send_photo(m.chat.id, t, caption=txt, reply_markup=main_kb())

            if user_data[uid]["auto_forward"]:
                for ch in user_data[uid]["selected_channels"]:
                    try:
                        bot.send_photo(ch, t, caption=txt)
                    except Exception as e:
                        print("Forward text-photo error:", e)
            return

    bot.send_message(m.chat.id, txt, reply_markup=main_kb())

    if user_data[uid]["auto_forward"]:
        for ch in user_data[uid]["selected_channels"]:
            try:
                bot.send_message(ch, txt)
            except Exception as e:
                print("Forward text error:", e)


print("Bot running...")
bot.remove_webhook()
bot.infinity_polling(skip_pending=True)
