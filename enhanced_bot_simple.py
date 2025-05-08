"""
NOVAXA Telegram Bot (Simplified Version)
----------------------------------------
Main module for the NOVAXA Telegram bot.
This version uses polling mode only for better compatibility with Termux.
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
import telebot
from telebot import types

from security import TokenManager, SecurityMonitor, IPProtection

load_dotenv()

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

TOKEN = token_manager.get_token() or os.environ.get("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

if not TOKEN:
    logger.error("No Telegram token provided")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

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

@bot.message_handler(commands=["emergencyreset"])
def handle_emergency_reset(message):
    """Emergency reset of tokens."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to perform emergency reset."
        )
        security_monitor.log_event(
            "unauthorized_emergency_reset",
            {"command": "emergencyreset"},
            user_id
        )
        return
    
    parts = message.text.split()
    if len(parts) < 2 or parts[1].lower() != "confirm":
        bot.reply_to(
            message, 
            "⚠️ This will reset all tokens to their backup state or deactivate them if no backup exists.\n\n"
            "To confirm, use: /emergencyreset confirm"
        )
        return
    
    if token_manager.emergency_reset(user_id):
        bot.reply_to(
            message, 
            "✅ Emergency reset completed successfully.\n\n"
            "Please restart the bot to apply changes."
        )
        
        security_monitor.log_event(
            "emergency_reset_performed",
            {},
            user_id
        )
    else:
        bot.reply_to(
            message, 
            "❌ Failed to perform emergency reset."
        )

@bot.message_handler(commands=["exporttokens"])
def handle_export_tokens(message):
    """Export tokens."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to export tokens."
        )
        security_monitor.log_event(
            "unauthorized_token_access",
            {"command": "exporttokens"},
            user_id
        )
        return
    
    parts = message.text.split()
    include_values = len(parts) > 1 and parts[1].lower() == "full"
    
    if include_values:
        bot.reply_to(
            message, 
            "⚠️ You are exporting tokens with their values. This is a security risk."
        )
    
    export_data = token_manager.export_tokens(include_values)
    
    export_file = f"config/tokens_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(export_file, "w") as f:
            f.write(export_data)
            
        bot.reply_to(
            message, 
            f"✅ Tokens exported to `{export_file}`\n\n"
            f"Use the file to backup or transfer tokens.",
            parse_mode="Markdown"
        )
        
        security_monitor.log_event(
            "tokens_exported",
            {"file": export_file, "include_values": include_values},
            user_id
        )
    except Exception as e:
        bot.reply_to(
            message, 
            f"❌ Failed to export tokens: {str(e)}"
        )

@bot.message_handler(commands=["rotatetoken"])
def handle_rotate_token(message):
    """Rotate a token to a new value."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to rotate tokens."
        )
        security_monitor.log_event(
            "unauthorized_token_access",
            {"command": "rotatetoken"},
            user_id
        )
        return
    
    parts = message.text.split()
    if len(parts) < 3:
        bot.reply_to(
            message, 
            "❌ Please provide a token ID and new token value.\n\n"
            "Usage: /rotatetoken [TOKEN_ID] [NEW_TOKEN]"
        )
        return
        
    token_id = parts[1]
    new_token = parts[2]
    
    if token_manager.rotate_token(token_id, new_token):
        bot.reply_to(
            message, 
            f"✅ Token {token_id} rotated to new value.\n\n"
            f"⚠️ Please restart the bot to apply the new token."
        )
        
        security_monitor.log_event(
            "token_rotated",
            {"token_id": token_id},
            user_id
        )
    else:
        bot.reply_to(
            message, 
            f"❌ Failed to rotate token {token_id}."
        )

@bot.message_handler(commands=["importtokens"])
def handle_import_tokens(message):
    """Import tokens from a file."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_owner(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to import tokens."
        )
        security_monitor.log_event(
            "unauthorized_token_access",
            {"command": "importtokens"},
            user_id
        )
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(
            message, 
            "❌ Please provide a file path.\n\n"
            "Usage: /importtokens [FILE_PATH]"
        )
        return
        
    file_path = parts[1]
    
    try:
        with open(file_path, "r") as f:
            json_data = f.read()
            
        if token_manager.import_tokens(json_data, user_id):
            bot.reply_to(
                message, 
                "✅ Tokens imported successfully.\n\n"
                "Please restart the bot to apply changes."
            )
            
            security_monitor.log_event(
                "tokens_imported",
                {"file": file_path},
                user_id
            )
        else:
            bot.reply_to(
                message, 
                "❌ Failed to import tokens."
            )
    except Exception as e:
        bot.reply_to(
            message, 
            f"❌ Failed to import tokens: {str(e)}"
        )

@bot.message_handler(commands=["help"])
def handle_help(message):
    """Show help message."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    help_text = "🤖 *NOVAXA Bot Commands*\n\n"
    
    help_text += "*Basic Commands:*\n"
    help_text += "/start - Start the bot\n"
    help_text += "/status - Check bot status\n"
    help_text += "/help - Show this help message\n\n"
    
    if is_owner(user_id):
        help_text += "*Token Management (Owner Only):*\n"
        help_text += "/tokens - List all tokens\n"
        help_text += "/addtoken [TOKEN] [NAME] - Add a new token\n"
        help_text += "/activatetoken [TOKEN_ID] - Activate a token\n"
        help_text += "/rotatetoken [TOKEN_ID] [NEW_TOKEN] - Rotate a token\n"
        help_text += "/exporttokens - Export tokens\n"
        help_text += "/importtokens [FILE_PATH] - Import tokens\n"
        help_text += "/emergencyreset confirm - Emergency reset of tokens\n"
    
    bot.reply_to(
        message,
        help_text,
        parse_mode="Markdown"
    )

@bot.message_handler(commands=["getid"])
def handle_get_id(message):
    """Get user ID."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    bot.reply_to(
        message,
        f"Your Telegram ID is: `{user_id}`",
        parse_mode="Markdown"
    )

def start_bot():
    def shutdown(sig, frame):
        logger.info("Shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Starting bot in polling mode...")
    bot.remove_webhook()
    bot.infinity_polling()

if __name__ == "__main__":
    start_bot()
