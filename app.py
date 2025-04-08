import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Περιβαλλοντικές μεταβλητές
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 8443))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Προσωρινή μνήμη υπενθυμίσεων
notifications = {}

# Εντολές bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA Bot! Πληκτρολόγησε /help για οδηγίες.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Ξεκινά το bot\n"
        "/help - Οδηγίες\n"
        "/status - Κατάσταση συστημάτων\n"
        "/log - Δείχνει logs\n"
        "/getid - Το Telegram ID σου\n"
        "/broadcast - Μαζικό μήνυμα (admin)\n"
        "/notify - Υπενθύμιση\n"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BidPrice: OK\nAmesis: OK\nProject6225: OK")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as file:
            lines = file.readlines()[-5:]
            await update.message.reply_text("".join(lines))
    except Exception as e:
        await update.message.reply_text("Σφάλμα ανάγνωσης log.")
        logger.error(e)

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Telegram ID σου: {update.message.from_user.id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις άδεια.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast Μήνυμα")
        return
    msg = " ".join(context.args)
    await update.message.reply_text(f"Μήνυμα στάλθηκε: {msg}")
    # Εδώ μπορείς να προσθέσεις αποστολή σε χρήστες

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Χρήση: /notify 15:00 Μήνυμα")
        return
    time, *message = context.args
    notifications[update.message.from_user.id] = {"time": time, "message": " ".join(message)}
    await update.message.reply_text(f"Υπενθύμιση ορίστηκε: {time} - {' '.join(message)}")

# Flask route για έλεγχο
@app.route('/')
def home():
    return 'NOVAXA bot is live!'

# Webhook endpoint (πρέπει να είναι /TOKEN)
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
    return 'OK'

# Εκκίνηση bot
def main():
    global application
    application = Application.builder().token(TOKEN).build()

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
        webhook_url=f"https://novaxa.onrender.com/{TOKEN}"
    )

if __name__ == "__main__":
    main()