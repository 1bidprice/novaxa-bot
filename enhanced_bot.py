"""
NOVAXA Telegram Bot

Main module for the NOVAXA Telegram bot.
Supports both webhook and polling mode.
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from typing import Dict
from collections import defaultdict

from dotenv import load_dotenv
from flask import Flask, request, jsonify
import telebot
from telebot import types

load_dotenv()

# Flask app
app = Flask(__name__)

# Logging setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("NOVAXA")
file_handler = logging.FileHandler("logs/bot.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

# Token and webhook
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", "8443"))
WEBHOOK_ENABLED = os.environ.get("WEBHOOK_ENABLED", "true").lower() == "true"
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

if not TOKEN:
    logger.error("Missing TELEGRAM_BOT_TOKEN")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Rate limit
rate_limits = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
RATE_LIMIT_INTERVAL = 60
RATE_LIMIT_MAX = 30

# Routes
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "NOVAXA bot is running"})

@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    success = bot.set_webhook(url=WEBHOOK_URL)
    return jsonify({"status": "success" if success else "failure"})

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "Invalid content type"})

# Helpers
def is_admin(user_id):
    return user_id in ADMIN_IDS

def check_rate_limit(user_id: int) -> bool:
    current = time.time()
    rl = rate_limits[user_id]
    if current - rl["last_reset"] > RATE_LIMIT_INTERVAL:
        rl["count"] = 0
        rl["last_reset"] = current
    rl["count"] += 1
    return rl["count"] > RATE_LIMIT_MAX

# Handlers
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Status", callback_data="status"))
    bot.send_message(message.chat.id, "👋 Welcome to NOVAXA!", reply_markup=markup)

@bot.message_handler(commands=["status"])
def handle_status(message):
    user_id = message.from_user.id
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    bot.send_message(message.chat.id, "✅ NOVAXA is running fine.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "status":
        bot.answer_callback_query(call.id, "✅ NOVAXA is healthy.")

# Entry point
def start_bot():
    def shutdown(sig, frame):
        logger.info("Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if WEBHOOK_ENABLED:
        logger.info("Starting bot in webhook mode...")
        bot.remove_webhook()
        time.sleep(1)
        bot.set_webhook(url=WEBHOOK_URL)
        app.run(host="0.0.0.0", port=PORT)
    else:
        logger.info("Starting bot in polling mode...")
        bot.remove_webhook()
        bot.infinity_polling()

if __name__ == "__main__":
    start_bot()