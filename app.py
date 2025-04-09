import os
import logging
from flask import Flask, request
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

# Tokens and admin
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8443))
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# Initialize Telegram application
application = Application.builder().token(TOKEN).build()

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA Bot! Πληκτρολόγησε /help για οδηγίες.")

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Διαθέσιμες εντολές:\n/start\n/help\n/status\n/log\n/getid\n/broadcast\n/notify")

# Command: /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Projects:\n• BidPrice OK\n• Amesis OK\n• Project6225 OK")

# Command: /log
async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as f:
            lines = f.readlines()[-10:]
        await update.message.reply_text("".join(lines))
    except Exception:
        await update.message.reply_text("Δεν υπάρχουν logs.")

# Command: /getid
async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ID σου: {update.message.from_user.id}")

# Command: /broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις άδεια.")
        return
    message = " ".join(context.args)
    await update.message.reply_text(f"Broadcast: {message}")

# Command: /notify
async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Υπενθύμιση ρυθμίστηκε!")

# Register commands
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("status", status))
application.add_handler(CommandHandler("log", log))
application.add_handler(CommandHandler("getid", getid))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("notify", notify))

# Route για να ελέγξεις αν είναι live
@app.route("/", methods=["GET"])
def home():
    return "NOVAXA Bot is live!", 200

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "ok"