from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import os
import re

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send photo or text with links 👀")

async def clean_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""

    if update.message.text:
        text = update.message.text
    elif update.message.caption:
        text = update.message.caption

    if not text:
        return

    # find links
    links = re.findall(r'https?://\S+', text)

    # remove links from text
    normal_text = re.sub(r'https?://\S+', '', text).strip()

    message = ""

    if normal_text:
        message += normal_text + "\n\n"

    if links:
        message += "FULL VIDEO 👀🌸\n\n"

        for i, link in enumerate(links, 1):
            message += f"VIDEO {i} ⤵️\n{link}\n\n"

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await update.message.reply_photo(photo=photo, caption=message)

    else:
        await update.message.reply_text(message)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, clean_links))

app.run_polling()
