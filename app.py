import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Περιβάλλον
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    return "NOVAXA Bot is live!"

@app.route("/setwebhook")
def set_webhook():
    url = f"https://novaxa-bot.onrender.com/webhook"
    application.bot.set_webhook(url)
    return f"Webhook set to {url}"

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put(update)
        return "ok"

# Εντολές Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA bot!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start /help /status /getid /notify /broadcast /alert /log")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Το bot είναι ενεργό και λειτουργεί σωστά.")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Telegram ID σου: {update.message.from_user.id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις άδεια να χρησιμοποιήσεις αυτή την εντολή.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast <μήνυμα>")
        return
    msg = " ".join(context.args)
    await update.message.reply_text(f"Μήνυμα προς αποστολή: {msg}")
    # Εδώ μπορείς να προσθέσεις αποστολή προς λίστα χρηστών

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Χρήση: /notify <ώρα> <μήνυμα>")
        return
    time, *message = context.args
    await update.message.reply_text(f"Ειδοποίηση για {time}: {' '.join(message)}")

async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Alert! Κάτι σημαντικό συνέβη!")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("log.txt"):
        with open("log.txt", "r") as f:
            lines = f.readlines()[-10:]
        await update.message.reply_text("".join(lines))
    else:
        await update.message.reply_text("Δεν υπάρχουν logs.")

# Δημιουργία εφαρμογής Telegram
application = ApplicationBuilder().token(TOKEN).build()

# Καταχωρήσεις εντολών
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("status", status))
application.add_handler(CommandHandler("getid", getid))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("notify", notify))
application.add_handler(CommandHandler("alert", alert))
application.add_handler(CommandHandler("log", log))