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

from security import TokenManager, SecurityMonitor, IPProtection

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

token_manager = TokenManager()
security_monitor = SecurityMonitor()
ip_protection = IPProtection(
    owner_id=int(os.environ.get("OWNER_ID", "0"))
)

# Load environment
TOKEN = token_manager.get_token() or os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", "8443"))
WEBHOOK_ENABLED = os.environ.get("WEBHOOK_ENABLED", "true").lower() == "true"
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

if not TOKEN:
    logger.error("No Telegram token provided")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Rate limiting
rate_limits = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
RATE_LIMIT_INTERVAL = 60
RATE_LIMIT_MAX = 30

def check_rate_limit(user_id: int) -> bool:
    current = time.time()
    rl = rate_limits[user_id]
    if current - rl["last_reset"] > RATE_LIMIT_INTERVAL:
        rl["count"] = 0
        rl["last_reset"] = current
    rl["count"] += 1
    return rl["count"] > RATE_LIMIT_MAX

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def is_owner(user_id: int) -> bool:
    """Check if a user is the owner."""
    return user_id == OWNER_ID and ip_protection.verify_owner(user_id)

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

# Command handlers
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

@bot.message_handler(commands=["addtoken"])
def handle_add_token(message):
    """Add a new token."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to manage tokens."
        )
        security_monitor.log_event(
            "unauthorized_token_access",
            {"command": "addtoken"},
            user_id
        )
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(
            message, 
            "❌ Please provide a token.\n\nUsage: /addtoken [TOKEN] [NAME]"
        )
        return
        
    token = parts[1]
    name = " ".join(parts[2:]) if len(parts) > 2 else "Default"
    
    token_id = token_manager.add_token(token, name, user_id)
    
    bot.reply_to(
        message, 
        f"✅ Token added with ID: `{token_id}`\n\n"
        f"Use /activatetoken {token_id} to activate this token.",
        parse_mode="Markdown"
    )
    
    security_monitor.log_event(
        "token_added",
        {"token_id": token_id, "name": name},
        user_id
    )

@bot.message_handler(commands=["activatetoken"])
def handle_activate_token(message):
    """Activate a token."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to manage tokens."
        )
        security_monitor.log_event(
            "unauthorized_token_access",
            {"command": "activatetoken"},
            user_id
        )
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(
            message, 
            "❌ Please provide a token ID.\n\nUsage: /activatetoken [TOKEN_ID]"
        )
        return
        
    token_id = parts[1]
    
    if token_manager.activate_token(token_id):
        bot.reply_to(
            message, 
            f"✅ Token {token_id} activated.\n\n"
            f"⚠️ Please restart the bot to apply the new token."
        )
        
        security_monitor.log_event(
            "token_activated",
            {"token_id": token_id},
            user_id
        )
    else:
        bot.reply_to(
            message, 
            f"❌ Failed to activate token {token_id}."
        )

@bot.message_handler(commands=["tokens"])
def handle_list_tokens(message):
    """List all tokens."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to view tokens."
        )
        security_monitor.log_event(
            "unauthorized_token_access",
            {"command": "tokens"},
            user_id
        )
        return
    
    tokens = token_manager.get_tokens()
    
    if not tokens: 
        bot.reply_to(
            message, 
            "No tokens found."
        )
        return
    
    tokens_text = "🔑 *Tokens*\n\n"
    for token in tokens:
        status = "✅ Active" if token["active"] else ("⚪ Inactive" if token["status"] == "inactive" else "⚪ Standby")
        tokens_text += f"*ID:* `{token['id']}`\n"
        tokens_text += f"*Name:* {token['name']}\n"
        tokens_text += f"*Status:* {status}\n"
        tokens_text += f"*Created:* {token['created'][:10]}\n\n"
    
    bot.reply_to(
        message, 
        tokens_text,
        parse_mode="Markdown"
    )

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
