import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# Logging setup
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Περιβάλλον: TOKEN και ADMIN_ID
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PORT = int(os.getenv("PORT", 10000))

# Δημιουργία bot
application = Application.builder().token(TOKEN).build()

# Προσωρινή μνήμη για /notify
notifications = {}

# --- Εντολές Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA Bot! Πληκτρολόγησε /help για οδηγίες.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Ξεκινά το bot\n"
        "/help - Οδηγίες\n"
        "/status - Κατάσταση συστημάτων\n"
        "/log - Τελευταία logs\n"
        "/getid - Το Telegram ID σου\n"
        "/broadcast - Μαζικό μήνυμα (admin)\n"
        "/notify - Υπενθύμιση με ώρα\n"
    )
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BidPrice: OK\nAmesis: OK\nProject6225: OK")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as f:
            lines = f.readlines()[-5:]
        await update.message.reply_text("".join(lines))
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Σφάλμα ανάγνωσης log.")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Telegram ID σου: {user_id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις άδεια για αυτή την εντολή.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast Μήνυμα")
        return
    message = " ".join(context.args)
    await update.message.reply_text(f"Μήνυμα στάλθηκε: {message}")
    # Εδώ μπορείς να προσθέσεις αποστολή σε όλους τους χρήστες

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Χρήση: /notify 15:00 Μήνυμα")
        return
    time = context.args[0]
    message = " ".join(context.args[1:])
    notifications[update.message.from_user.id] = {"time": time, "message": message}
    await update.message.reply_text(f"Υπενθύμιση ορίστηκε: {time} - {message}")

# --- Flask Route ---
@app.route('/')
def home():
    return "NOVAXA Bot is live!"

@app.route(f'/{TOKEN}', methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# --- Main ---
def main():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("getid", getid))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("notify", notify))

    # Ρύθμιση webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://novaxa-bot.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()