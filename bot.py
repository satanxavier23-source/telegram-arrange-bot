if current_menu == "use_photo":
        slot = message.text
        photo_id = user_settings[uid]["saved_photos"].get(slot)

        if not photo_id:
            bot.send_message(
                message.chat.id,
                f"{slot} il photo save ചെയ്തിട്ടില്ല ❌",
                reply_markup=use_photo_kb()
            )
            return

        user_settings[uid]["selected_photo"] = slot
        user_settings[uid]["menu"] = "thumb"

        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=f"{slot} selected ✅",
            reply_markup=thumb_kb()
        )
        return


@bot.message_handler(func=lambda m: m.text == "📢 Select Channel")
def select_channel_menu(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["menu"] = "channel"
    bot.send_message(message.chat.id, "Channels select ചെയ്യൂ", reply_markup=channel_kb())


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

    init_user(uid)
    user_settings[uid]["menu"] = "thumb"
    bot.send_message(message.chat.id, "Channels saved ✅", reply_markup=thumb_kb())


@bot.message_handler(func=lambda m: m.text == "🗑 Clear Channels")
def clear_channels(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["selected_channels"] = []
    bot.send_message(message.chat.id, "Channels cleared ✅", reply_markup=channel_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Thumb ON")
def thumb_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    if not user_settings[uid]["selected_photo"]:
        bot.send_message(
            message.chat.id,
            "Aadyam ✅ Use Photo il poi Photo 1 / Photo 2 select ചെയ്യൂ ❌",
            reply_markup=thumb_kb()
        )
        return

    user_settings[uid]["thumb_mode"] = True
    bot.send_message(message.chat.id, "Thumb ON ✅🔥", reply_markup=thumb_kb())


@bot.message_handler(func=lambda m: m.text == "🔴 Thumb OFF")
def thumb_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["thumb_mode"] = False
    bot.send_message(message.chat.id, "Thumb OFF ❌", reply_markup=thumb_kb())


@bot.message_handler(func=lambda m: m.text == "🟢 Auto Forward ON")
def auto_forward_on(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["auto_forward"] = True
    bot.send_message(message.chat.id, "Auto Forward ON 📈❤️", reply_markup=thumb_kb())


@bot.message_handler(func=lambda m: m.text == "🔴 Auto Forward OFF")
def auto_forward_off(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)
    user_settings[uid]["auto_forward"] = False
    bot.send_message(message.chat.id, "Auto Forward OFF ❌", reply_markup=thumb_kb())


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
    waiting_slot = user_settings[uid]["waiting_photo_slot"]

    # Save Photo mode
    if waiting_slot:
        user_settings[uid]["saved_photos"][waiting_slot] = photo_id
        user_settings[uid]["waiting_photo_slot"] = None
        user_settings[uid]["menu"] = "thumb"

        bot.send_photo(
            message.chat.id,
            photo_id,
            caption=f"{waiting_slot} save ചെയ്തു ✅",
            reply_markup=thumb_kb()
        )
        return

    # Link Arrange mode
    if user_settings[uid]["link_mode"]:
        links = extract_links(caption)

        if not links:
            return

        final_text = build_arranged_text(links)

        try:
            bot.send_photo(
                message.chat.id,
                photo_id,
                caption=final_text,
                reply_markup=main_kb()
            )
        except Exception as e:
            print("Link arrange photo error:", e)
        return

    # Thumb mode
    if user_settings[uid]["thumb_mode"]:
        selected_slot = user_settings[uid]["selected_photo"]
        selected_photo_id = user_settings[uid]["saved_photos"].get(selected_slot) if selected_slot else None

        if not selected_photo_id:
            bot.send_message(
                message.chat.id,
                "Selected photo ഇല്ല ❌",
                reply_markup=thumb_kb()
            )
            return

        try:
            bot.send_photo(
                message.chat.id,
                selected_photo_id,
                caption=caption,
                reply_markup=thumb_kb()
            )
        except Exception as e:
            print("Send error:", e)

        if user_settings[uid]["auto_forward"]:
            for ch in user_settings[uid]["selected_channels"]:
                try:
                    bot.send_photo(ch, selected_photo_id, caption=caption)
                except Exception as e:
                    print("Forward error:", e)
        return


# =========================
# TEXT HANDLER
# =========================
@bot.message_handler(content_types=["text"])
def text_handler(message):
    uid = message.from_user.id
    if not is_admin(uid):
        return

    init_user(uid)

    ignore = [
        "🔗 Link Arrangement",
        "🚀 Thumb & Auto Forward",
        "❓ Help",
        "🟢 Link Arrange ON",
        "🔴 Link Arrange OFF",
        "📸 Set Photo",
        "✅ Use Photo",
        "📢 Select Channel",
        "🟢 Thumb ON",
        "🔴 Thumb OFF",
        "🟢 Auto Forward ON",
        "🔴 Auto Forward OFF",
        "✅ Done",
        "🗑 Clear Channels",
        "⬅️ Back",
        "Photo 1", "Photo 2", "Photo 3", "Photo 4", "Photo 5",
        "Channel 1", "Channel 2", "Channel 3", "Channel 4"
    ]

    if message.text in ignore:
        return

    # Link Arrange mode
    if user_settings[uid]["link_mode"]:
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
            print("Link arrange text error:", e)
        return

    # Thumb mode text
    if user_settings[uid]["thumb_mode"]:
        try:
            bot.send_message(
                message.chat.id,
                message.text,
                reply_markup=thumb_kb()
            )
        except Exception as e:
            print("Send text error:", e)

        if user_settings[uid]["auto_forward"]:
            for ch in user_settings[uid]["selected_channels"]:
                try:
                    bot.send_message(ch, message.text)
                except Exception as e:
                    print("Forward text error:", e)
        return


print("Bot running...")
bot.infinity_polling(skip_pending=True)
