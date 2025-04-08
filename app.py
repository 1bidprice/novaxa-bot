import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BASE_URL = "https://novaxa-bot.onrender.com"

bot = Bot(token=TOKEN)
app = Flask(__name__)

application = ApplicationBuilder().token(TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA bot!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start /help /status /getid /broadcast /notify")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Το NOVAXA bot είναι ενεργό!")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Telegram ID σου: {update.message.from_user.id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις άδεια.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast μήνυμα")
        return
    msg = " ".join(context.args)
    for user_id in [ADMIN_ID]:  # Μπορείς να προσθέσεις λίστα χρηστών
        try:
            await bot.send_message(chat_id=user_id, text=f"📢 {msg}")
        except:
            pass
    await update.message.reply_text("Το μήνυμα στάλθηκε.")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Χρήση: /notify ώρα μήνυμα")
        return
    time, *message = context.args
    await update.message.reply_text(f"📅 Υπενθύμιση για {time}: {' '.join(message)}")

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("status", status))
application.add_handler(CommandHandler("getid", getid))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("notify", notify))

# Webhook setup
@app.route("/")
def home():
    return "NOVAXA Bot is live!"

@app.route("/setwebhook")
async def setwebhook():
    url = f"{BASE_URL}/webhook"
    await application.bot.set_webhook(url)
    return f"Webhook set to {url}"

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return "OK"

if __name__ == "__main__":
    import asyncio
    asyncio.run(application.initialize())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))