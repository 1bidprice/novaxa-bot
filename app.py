import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Token & Port από περιβαλλοντικές μεταβλητές
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8443))

# Bot notifications (προσωρινή μνήμη)
notifications = {}

# Telegram bot commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA Bot! Πληκτρολόγησε /help για οδηγίες.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "/start - Ξεκινά το bot\n"
        "/help - Οδηγίες\n"
        "/status - Κατάσταση συστημάτων\n"
        "/log - Δείχνει logs\n"
        "/getid - Το Telegram ID σου\n"
        "/broadcast - Μαζικό μήνυμα (admin)\n"
        "/notify - Υπενθύμιση\n"
    )
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "BidPrice: OK\nAmesis: OK\nProject6225: OK"
    )

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as file:
            lines = file.readlines()[-5:]
            await update.message.reply_text("".join(lines))
    except Exception as e:
        await update.message.reply_text("Σφάλμα ανάγνωσης log.")
        logger.error(e)

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Telegram ID σου: {user_id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = 123456789  # <-- άλλαξε το με το δικό σου
    if update.message.from_user.id != admin_id:
        await update.message.reply_text("Δεν έχεις άδεια.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast Μήνυμα")
        return
    message = " ".join(context.args)
    await update.message.reply_text(f"Μήνυμα στάλθηκε: {message}")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Χρήση: /notify 15:00 Μήνυμα")
        return
    time = context.args[0]
    message = " ".join(context.args[1:])
    notifications[update.message.from_user.id] = {"time": time, "message": message}
    await update.message.reply_text(f"Υπενθύμιση ορίστηκε: {time} - {message}")

@app.route('/')
def home():
    return "NOVAXA Bot is live!"

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
        webhook_url=f"https://novaxa.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
