import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# TOKEN (hardcoded για άμεση χρήση)
TOKEN = "7658672268:AAHbvuM4fxYr2kiA-Aiynjgm5VPVTiYXe8U"
PORT = int(os.environ.get("PORT", 8443))
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))  # Βάλε το Telegram ID σου εδώ αν θες

# Logging
logging.basicConfig(
    filename='log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app για Render
app = Flask(__name__)

# --- Υπενθυμίσεις (σε προσωρινή μνήμη) ---
notifications = {}

# --- Εντολές Bot ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Καλώς ήρθες στο NOVAXA Bot!\nΧρησιμοποίησε /help για οδηγίες.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "NOVAXA Bot - Εντολές:\n"
        "/start - Ξεκινάει το bot\n"
        "/help - Βοήθεια\n"
        "/status - Κατάσταση projects\n"
        "/log - Δείχνει τελευταία logs\n"
        "/getid - Εμφάνιση Telegram ID\n"
        "/broadcast <μήνυμα> - Μαζικό μήνυμα (admin)\n"
        "/notify <ώρα> <μήνυμα> - Ρύθμιση υπενθύμισης"
    )
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("BidPrice: OK\nAmesis: OK\nProject6225: OK")

async def log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open("log.txt", "r") as f:
            lines = f.readlines()[-10:]
        await update.message.reply_text("".join(lines))
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Δεν βρέθηκαν logs.")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Το Telegram ID σου είναι: {user_id}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("Δεν έχεις δικαίωμα για αυτή την εντολή.")
        return
    if not context.args:
        await update.message.reply_text("Χρήση: /broadcast <μήνυμα>")
        return
    message = " ".join(context.args)
    logger.info(f"Broadcast από {user_id}: {message}")
    await update.message.reply_text(f"📢 Το μήνυμα στάλθηκε: {message}")

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Χρήση: /notify 15:00 Υπενθύμιση")
        return
    time = context.args[0]
    msg = " ".join(context.args[1:])
    notifications[update.message.from_user.id] = {"time": time, "msg": msg}
    await update.message.reply_text(f"🔔 Υπενθύμιση ορίστηκε: {time} - {msg}")

# --- Flask route για health check ---
@app.route('/')
def index():
    return 'NOVAXA Bot is running!', 200

# --- Εκκίνηση bot με webhook ---
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

# Εκκίνηση Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)