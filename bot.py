from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

TOKEN = os.getenv("TOKEN")

async def clean_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ""

    if update.message.text:
        text = update.message.text
    elif update.message.caption:
        text = update.message.caption

    links = [line.strip() for line in text.splitlines() if line.strip().startswith("http")]

    if not links:
        return

    message = "FULL VIDEO 👀🌸\n\n" + "\n\n".join(
        [f"VIDEO {i+1} ⤵️\n{link}" for i, link in enumerate(links)]
    )

    # if photo exists
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        await update.message.reply_photo(photo=photo, caption=message)
    else:
        await update.message.reply_text(message)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, clean_links))

app.run_polling()
