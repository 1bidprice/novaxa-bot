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

# Load environment variables
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

# Environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", "8443"))
WEBHOOK_ENABLED = os.environ.get("WEBHOOK_ENABLED", "true").lower() == "true"
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

if not TOKEN:
    logger.error("Missing TELEGRAM_BOT_TOKEN")
    sys.exit(1)

# Telegram bot instance
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Rate limit setup
rate_limits = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
RATE_LIMIT_INTERVAL = 60  # seconds
RATE_LIMIT_MAX = 30       # max commands per interval

# Flask routes
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ok", "message": "NOVAXA bot is running"})

@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    success = bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook set: {success}")
    return jsonify({"status": "success" if success else "failure"})

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "error", "message": "Invalid content type"})


# Utility functions
def is_admin(user_id):
    return user_id in ADMIN_IDS

def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    data = rate_limits[user_id]
    if now - data["last_reset"] > RATE_LIMIT_INTERVAL:
        data["count"] = 0
        data["last_reset"] = now
    data["count"] += 1
    return data["count"] > RATE_LIMIT_MAX

# Bot command handlers
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
def handle_callback(call):
    if call.data == "status":
        bot.answer_callback_query(call.id, "✅ NOVAXA is healthy.")

# Entry point
def start_bot():
    def shutdown(sig, frame):
        logger.info("Shutting down gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if WEBHOOK_ENABLED:
        logger.info("Webhook mode enabled. Setting webhook...")
        bot.remove_webhook()
        time.sleep(0.5)
        if not bot.set_webhook(url=WEBHOOK_URL):
            logger.error("Failed to set webhook.")
            sys.exit(1)
        app.run(host="0.0.0.0", port=PORT)
    else:
        logger.info("Polling mode enabled. Starting polling...")
        bot.remove_webhook()
        bot.infinity_polling()

if __name__ == "__main__":
    start_bot()