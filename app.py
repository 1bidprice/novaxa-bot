import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Ρύθμιση logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Περιβαλλοντικές μεταβλητές
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8443))
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# Πρόχειρη μνήμη υπενθυμίσεων
notifications = {}

# --- Εντολές Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"User {user.id} started the bot.")
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA Bot! Πληκτρολόγησε /help για οδηγίες.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Διαθέσιμες εντολές:\n"
        "/start - Ξεκινά το bot\n"
        "/help - Οδηγίες χρήσης\n"
        "/status - Κατάσταση projects\n"
        "/log - Δείχνει πρόσφατα logs\n"
        "/getid - Δείχνει το Telegram ID σου\n"
        "/broadcast <μήνυμα> - Μαζικό μήνυμα (admin)\n"
        "/notify <ώρα> <μήνυμα> - Ρύθμιση υπενθύμισης"
    )
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = (
        "📊 *Κατάσταση Projects:*\n"
        "• BidPrice: OK\n"
        "• Amesis: OK\n"
        "• Project6225: OK"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as f:
            last_lines = f.readlines()[-10:]
        await update.message.reply_text("".join(last_lines))
    except Exception as e:
        logger.error(f"Log read error: {e}")
        await update.message.reply_text("Σφάλμα κατά την ανάγνωση log.")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Το Telegram ID σου είναι: {user_id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις δικαιώματα για αυτή την εντολή.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast <μήνυμα>")
        return
    message = " ".join(context.args)
    logger.info(f"Broadcast από {user_id}: {message}")
    await update.message.reply_text(f"Μήνυμα στάλθηκε: {message}")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Χρήση: /notify 15:00 Υπενθύμιση")
        return
    time = context.args[0]
    text = " ".join(context.args[1:])
    user_id = update.message.from_user.id
    notifications[user_id] = {"time": time, "text": text}
    await update.message.reply_text(f"✅ Υπενθύμιση ρυθμίστηκε: {time} - {text}")

# Health check
@app.route('/')
def index():
    return 'NOVAXA Bot is running!', 200

# Webhook εκκίνηση
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("log", log))
    application.add_handler(CommandHandler("getid", getid))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("notify", notify))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://novaxa-bot.onrender.com/{TOKEN}"
    )

# Flask + Bot ταυτόχρονα
if __name__ == "__main__":
    from threading import Thread
    Thread(target=main).start()
    app.run(host="0.0.0.0", port=PORT)