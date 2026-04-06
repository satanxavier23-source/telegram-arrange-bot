from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import re

TOKEN = os.getenv("TOKEN")

async def clean_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""

    if update.message.text:
        text = update.message.text
    elif update.message.caption:
        text = update.message.caption

    # find all links
    links = re.findall(r'https?://\S+', text)

    if not links:
        return

    message = "FULL VIDEO 👀🌸\n\n"

    for i, link in enumerate(links, 1):
        message += f"VIDEO {i} ⤵️\n{link}\n\n"

    # photo case
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await update.message.reply_photo(photo=photo, caption=message)

    else:
        await update.message.reply_text(message)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, clean_links))

app.run_polling()
