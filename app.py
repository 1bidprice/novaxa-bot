import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, Dispatcher

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

TOKEN = "7658672268:AAHbvuM4fxYr2kiA-Aiynjgm5VPVTiYXe8U"
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

notifications = {}

# --- Telegram Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    await update.message.reply_text("📊 *Κατάσταση Projects:*\n• BidPrice: OK\n• Amesis: OK\n• Project6225: OK", parse_mode="Markdown")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as f:
            last_lines = f.readlines()[-10:]
        await update.message.reply_text("".join(last_lines))
    except:
        await update.message.reply_text("Σφάλμα κατά την ανάγνωση log.")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Το Telegram ID σου είναι: {update.message.from_user.id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις δικαιώματα για αυτή την εντολή.")
        return
    message = " ".join(context.args)
    await update.message.reply_text(f"Broadcast μήνυμα: {message}")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Χρήση: /notify 15:00 Υπενθύμιση")
        return
    time = context.args[0]
    text = " ".join(context.args[1:])
    notifications[update.message.from_user.id] = {"time": time, "text": text}
    await update.message.reply_text(f"✅ Υπενθύμιση: {time} - {text}")

# --- Register Handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("status", status))
application.add_handler(CommandHandler("log", log))
application.add_handler(CommandHandler("getid", getid))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("notify", notify))

# --- Routes ---
@app.route("/")
def home():
    return "NOVAXA is alive!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# --- Start ---
if __name__ == "__main__":
    bot.delete_webhook()
    bot.set_webhook(url=f"https://novaxa-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=PORT)