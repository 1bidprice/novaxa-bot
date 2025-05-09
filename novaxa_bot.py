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
from typing import Dict, List, Optional, Any
from collections import defaultdict

from dotenv import load_dotenv
import telebot
from telebot import types

from security import TokenManager, SecurityMonitor, IPProtection

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("NOVAXA")
file_handler = logging.FileHandler("logs/bot.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

if os.path.exists(".env"):
    load_dotenv()

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

bot = telebot.TeleBot(TOKEN)

rate_limits = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
RATE_LIMIT_INTERVAL = 60
RATE_LIMIT_MAX = 30

def check_rate_limit(user_id: int) -> bool:
    """Check if a user has exceeded the rate limit."""
    current = time.time()
    rl = rate_limits[user_id]
    if current - rl["last_reset"] > RATE_LIMIT_INTERVAL:
        rl["count"] = 0
        rl["last_reset"] = current
    rl["count"] += 1
    return rl["count"] > RATE_LIMIT_MAX

def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    return user_id in ADMIN_IDS

def is_owner(user_id: int) -> bool:
    """Check if a user is the owner."""
    return user_id == OWNER_ID

@bot.message_handler(commands=["start"])
def handle_start(message):
    """Handle the /start command."""
    user_id = message.from_user.id
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Status", callback_data="status"))
    markup.add(types.InlineKeyboardButton("ℹ️ Help", callback_data="help"))
    
    bot.send_message(
        message.chat.id, 
        f"👋 Welcome to NOVAXA Bot!\n\n"
        f"Your user ID is: `{user_id}`\n\n"
        f"Use /help to see available commands.",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    logger.info(f"User {user_id} started the bot")
    security_monitor.log_event("bot_start", {"user_id": user_id}, user_id)

@bot.message_handler(commands=["help"])
def handle_help(message):
    """Handle the /help command."""
    user_id = message.from_user.id
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    help_text = (
        "🤖 *NOVAXA Bot Commands*\n\n"
        "Basic Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - Check bot status\n"
        "/getid - Get your Telegram ID\n\n"
    )
    
    if is_owner(user_id):
        help_text += (
            "Owner Commands:\n"
            "/addtoken [TOKEN] [NAME] - Add a new token\n"
            "/activatetoken [TOKEN_ID] - Activate a token\n"
            "/listtokens - List all tokens\n"
            "/deletetoken [TOKEN_ID] - Delete a token\n"
            "/rotatetoken [TOKEN_ID] [NEW_TOKEN] - Rotate a token\n"
            "/emergency - Emergency reset\n\n"
        )
    
    if is_admin(user_id):
        help_text += (
            "Admin Commands:\n"
            "/broadcast [MESSAGE] - Send message to all users\n"
            "/log - View recent logs\n\n"
        )
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=["status"])
def handle_status(message):
    """Handle the /status command."""
    user_id = message.from_user.id
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    uptime = datetime.now() - datetime.fromtimestamp(os.path.getmtime(__file__))
    uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m"
    
    status_text = (
        "✅ *NOVAXA Bot Status*\n\n"
        f"Status: 🟢 Online\n"
        f"Uptime: {uptime_str}\n"
        f"Mode: Polling\n"
        f"Version: 3.0\n"
    )
    
    if is_owner(user_id):
        active_token = token_manager.active_token_id
        status_text += f"Active Token: {active_token or 'None'}\n"
    
    bot.send_message(message.chat.id, status_text, parse_mode="Markdown")

@bot.message_handler(commands=["getid"])
def handle_getid(message):
    """Handle the /getid command."""
    user_id = message.from_user.id
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    bot.reply_to(
        message, 
        f"Your Telegram ID is: `{user_id}`\n\n"
        f"Chat ID: `{message.chat.id}`",
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Handle callback queries from inline buttons."""
    if call.data == "status":
        bot.answer_callback_query(call.id, "✅ NOVAXA is healthy.")
        handle_status(call.message)
    elif call.data == "help":
        bot.answer_callback_query(call.id, "Showing help...")
        handle_help(call.message)

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
            f"✅ Token `{token_id}` activated.\n\n"
            f"Please restart the bot to apply the new token.",
            parse_mode="Markdown"
        )
        
        security_monitor.log_event(
            "token_activated",
            {"token_id": token_id},
            user_id
        )
    else:
        bot.reply_to(
            message, 
            f"❌ Failed to activate token `{token_id}`.\n\n"
            f"Please check if the token ID is correct.",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=["listtokens"])
def handle_list_tokens(message):
    """List all tokens."""
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
            {"command": "listtokens"},
            user_id
        )
        return
    
    tokens = token_manager.get_tokens()
    
    if not tokens:
        bot.reply_to(message, "No tokens found.")
        return
    
    active_token_id = token_manager.active_token_id
    
    tokens_text = "🔑 *Tokens*\n\n"
    
    for token in tokens:
        status = "✅ ACTIVE" if token["id"] == active_token_id else "❌ INACTIVE"
        tokens_text += (
            f"ID: `{token['id']}`\n"
            f"Name: {token['name']}\n"
            f"Status: {status}\n"
            f"Created: {token['created'][:10]}\n\n"
        )
    
    bot.reply_to(message, tokens_text, parse_mode="Markdown")
    
    security_monitor.log_event(
        "tokens_listed",
        {"count": len(tokens)},
        user_id
    )

@bot.message_handler(commands=["deletetoken"])
def handle_delete_token(message):
    """Delete a token."""
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
            {"command": "deletetoken"},
            user_id
        )
        return
    
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(
            message, 
            "❌ Please provide a token ID.\n\nUsage: /deletetoken [TOKEN_ID]"
        )
        return
        
    token_id = parts[1]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Yes", callback_data=f"delete_token_yes_{token_id}"),
        types.InlineKeyboardButton("❌ No", callback_data="delete_token_no")
    )
    
    bot.reply_to(
        message, 
        f"⚠️ Are you sure you want to delete token `{token_id}`?",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_token_"))
def callback_delete_token(call):
    """Handle token deletion confirmation."""
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(
            call.id, 
            "⛔ You don't have permission to manage tokens."
        )
        return
    
    if call.data == "delete_token_no":
        bot.answer_callback_query(call.id, "Deletion cancelled.")
        bot.edit_message_text(
            "Token deletion cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        return
    
    if call.data.startswith("delete_token_yes_"):
        token_id = call.data.replace("delete_token_yes_", "")
        
        if token_manager.delete_token(token_id):
            bot.answer_callback_query(call.id, "Token deleted.")
            bot.edit_message_text(
                f"✅ Token `{token_id}` deleted.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
            
            security_monitor.log_event(
                "token_deleted",
                {"token_id": token_id},
                user_id
            )
        else:
            bot.answer_callback_query(call.id, "Failed to delete token.")
            bot.edit_message_text(
                f"❌ Failed to delete token `{token_id}`.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
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
            "⛔ You don't have permission to manage tokens."
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
            "❌ Please provide a token ID and a new token value.\n\n"
            "Usage: /rotatetoken [TOKEN_ID] [NEW_TOKEN]"
        )
        return
        
    token_id = parts[1]
    new_token = parts[2]
    
    if token_manager.rotate_token(token_id, new_token):
        bot.reply_to(
            message, 
            f"✅ Token `{token_id}` rotated to new value.\n\n"
            f"Please restart the bot to apply the new token.",
            parse_mode="Markdown"
        )
        
        security_monitor.log_event(
            "token_rotated",
            {"token_id": token_id},
            user_id
        )
    else:
        bot.reply_to(
            message, 
            f"❌ Failed to rotate token `{token_id}`.\n\n"
            f"Please check if the token ID is correct.",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=["emergency"])
def handle_emergency(message):
    """Emergency reset of tokens."""
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
            {"command": "emergency"},
            user_id
        )
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Yes", callback_data="emergency_yes"),
        types.InlineKeyboardButton("❌ No", callback_data="emergency_no")
    )
    
    bot.reply_to(
        message, 
        "⚠️ *EMERGENCY RESET*\n\n"
        "This will reset all tokens to their last known good state.\n\n"
        "Are you sure you want to proceed?",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("emergency_"))
def callback_emergency(call):
    """Handle emergency reset confirmation."""
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(
            call.id, 
            "⛔ You don't have permission to manage tokens."
        )
        return
    
    if call.data == "emergency_no":
        bot.answer_callback_query(call.id, "Emergency reset cancelled.")
        bot.edit_message_text(
            "Emergency reset cancelled.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
        return
    
    if call.data == "emergency_yes":
        if token_manager.emergency_reset(user_id):
            bot.answer_callback_query(call.id, "Emergency reset completed.")
            bot.edit_message_text(
                "✅ Emergency reset completed.\n\n"
                "All tokens have been reset to their last known good state.\n\n"
                "Please restart the bot to apply the changes.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            
            security_monitor.log_event(
                "emergency_reset",
                {"success": True},
                user_id
            )
        else:
            bot.answer_callback_query(call.id, "Failed to perform emergency reset.")
            bot.edit_message_text(
                "❌ Failed to perform emergency reset.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            
            security_monitor.log_event(
                "emergency_reset",
                {"success": False},
                user_id
            )

@bot.message_handler(commands=["broadcast"])
def handle_broadcast(message):
    """Broadcast a message to all users."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_admin(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to broadcast messages."
        )
        security_monitor.log_event(
            "unauthorized_broadcast",
            {"command": "broadcast"},
            user_id
        )
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(
            message, 
            "❌ Please provide a message to broadcast.\n\n"
            "Usage: /broadcast [MESSAGE]"
        )
        return
        
    broadcast_message = parts[1]
    
    bot.reply_to(
        message, 
        f"✅ Broadcast message sent:\n\n{broadcast_message}"
    )
    
    security_monitor.log_event(
        "broadcast_sent",
        {"message": broadcast_message},
        user_id
    )

@bot.message_handler(commands=["log"])
def handle_log(message):
    """View recent logs."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
        
    if not is_admin(user_id):
        bot.reply_to(
            message, 
            "⛔ You don't have permission to view logs."
        )
        security_monitor.log_event(
            "unauthorized_log_access",
            {"command": "log"},
            user_id
        )
        return
    
    try:
        with open("logs/bot.log", "r") as f:
            logs = f.readlines()
            
        last_logs = logs[-10:]
        
        log_text = "📋 *Recent Logs*\n\n"
        for log in last_logs:
            log_text += f"`{log.strip()}`\n\n"
            
        bot.reply_to(message, log_text, parse_mode="Markdown")
        
        security_monitor.log_event(
            "logs_viewed",
            {"count": len(last_logs)},
            user_id
        )
    except Exception as e:
        bot.reply_to(
            message, 
            f"❌ Failed to read logs: {str(e)}"
        )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle all other messages."""
    user_id = message.from_user.id
    
    if check_rate_limit(user_id):
        bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    
    bot.reply_to(
        message, 
        "I don't understand that command. Use /help to see available commands."
    )

def signal_handler(sig, frame):
    """Handle signals to gracefully shut down the bot."""
    logger.info("Shutting down...")
    bot.stop_polling()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info("Starting NOVAXA Bot...")
    
    try:
        bot_info = bot.get_me()
        logger.info(f"Bot started: @{bot_info.username} ({bot_info.id})")
        print(f"Bot started: @{bot_info.username}")
        print(f"Press Ctrl+C to stop the bot")
    except Exception as e:
        logger.error(f"Failed to get bot info: {str(e)}")
        sys.exit(1)
    
    bot.infinity_polling()
