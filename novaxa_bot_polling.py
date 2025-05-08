"""
NOVAXA Bot - Simplified Polling Version
--------------------------------------
A simplified Telegram bot that uses polling mode only.
Includes token management "safety valve" for the owner.
"""

import os
import sys
import time
import logging
from datetime import datetime
import telebot
from dotenv import load_dotenv

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("novaxa_bot")

load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
    sys.exit(1)

if ":" not in TOKEN:
    logger.error("Invalid token format. Telegram bot tokens must contain a colon (:)")
    logger.error("Example of valid token format: 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ")
    sys.exit(1)

OWNER_ID = os.environ.get("OWNER_ID")
if OWNER_ID:
    try:
        OWNER_ID = int(OWNER_ID)
        logger.info(f"Owner ID set to: {OWNER_ID}")
    except ValueError:
        logger.warning(f"Invalid OWNER_ID format: {OWNER_ID}. Should be an integer.")
        OWNER_ID = None
else:
    logger.warning("OWNER_ID not found in environment variables.")
    OWNER_ID = None

ADMIN_IDS = []
admin_ids_str = os.environ.get("ADMIN_IDS", "")
if admin_ids_str:
    try:
        ADMIN_IDS = [int(admin_id.strip()) for admin_id in admin_ids_str.split(",") if admin_id.strip()]
        logger.info(f"Admin IDs: {ADMIN_IDS}")
    except ValueError:
        logger.warning(f"Invalid ADMIN_IDS format: {admin_ids_str}. Should be comma-separated integers.")

if OWNER_ID and OWNER_ID not in ADMIN_IDS:
    ADMIN_IDS.append(OWNER_ID)

START_TIME = datetime.now()
USERS = set()
MESSAGE_COUNT = 0

try:
    bot = telebot.TeleBot(TOKEN)
    logger.info("Bot initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing bot: {str(e)}")
    sys.exit(1)

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle the /start command."""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    logger.info(f"User {username} (ID: {user_id}) started the bot.")
    USERS.add(user_id)
    
    bot.reply_to(
        message,
        f"👋 Γεια σου, {message.from_user.first_name}!\n\n"
        f"Είμαι το NOVAXA Bot, ένας βοηθός για διάφορες εργασίες.\n\n"
        f"Χρησιμοποίησε /help για να δεις τις διαθέσιμες εντολές."
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handle the /help command."""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    logger.info(f"User {username} (ID: {user_id}) requested help.")
    
    help_text = (
        "📋 *Διαθέσιμες Εντολές:*\n\n"
        "/start - Ξεκίνησε το bot\n"
        "/help - Εμφάνισε αυτό το μήνυμα βοήθειας\n"
        "/status - Έλεγξε την κατάσταση του bot\n"
        "/getid - Δες το Telegram ID σου\n\n"
    )
    
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        help_text += (
            "🔐 *Εντολές Διαχειριστή:*\n\n"
            "/notify <μήνυμα> - Στείλε ειδοποίηση στον ιδιοκτήτη\n"
            "/broadcast <μήνυμα> - Στείλε μήνυμα σε όλους τους χρήστες\n"
            "/log - Δες τα πρόσφατα logs\n"
        )
        
    if user_id == OWNER_ID:
        help_text += (
            "\n🛡️ *Δικλείδα Ασφαλείας (Μόνο για τον ιδιοκτήτη):*\n\n"
            "/token - Διαχείριση token\n"
            "/token info - Δες πληροφορίες για το τρέχον token\n"
            "/token change <new_token> - Άλλαξε το token\n"
        )
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['token'])
def handle_token(message):
    """Handle the /token command (owner only)."""
    user_id = message.from_user.id
    
    if user_id != OWNER_ID:
        bot.reply_to(message, "⛔ Αυτή η εντολή είναι διαθέσιμη μόνο για τον ιδιοκτήτη του bot.")
        return
    
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        token_info = (
            "🔑 *Διαχείριση Token (Δικλείδα Ασφαλείας):*\n\n"
            f"Τρέχον token: `{TOKEN[:5]}...{TOKEN[-5:]}`\n\n"
            "*Διαθέσιμες επιλογές:*\n"
            "/token info - Δες πληροφορίες για το τρέχον token\n"
            "/token change <new_token> - Άλλαξε το token\n"
        )
        bot.reply_to(message, token_info, parse_mode="Markdown")
    elif args[0] == "info":
        try:
            bot_info = bot.get_me()
            token_info = (
                "🔑 *Πληροφορίες Token:*\n\n"
                f"Token: `{TOKEN[:5]}...{TOKEN[-5:]}`\n"
                f"Bot ID: `{bot_info.id}`\n"
                f"Bot Username: @{bot_info.username}\n"
                f"Bot Name: {bot_info.first_name}\n"
            )
            bot.reply_to(message, token_info, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ Σφάλμα: {str(e)}")
    elif args[0] == "change" and len(args) > 1:
        new_token = args[1]
        
        if ":" not in new_token:
            bot.reply_to(
                message,
                "❌ Μη έγκυρο format token. Τα Telegram bot tokens πρέπει να περιέχουν άνω-κάτω τελεία (:)\n"
                "Παράδειγμα: 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
            )
            return
        
        try:
            with open(".env", "r") as f:
                env_content = f.read()
            
            env_content = env_content.replace(f"TELEGRAM_BOT_TOKEN={TOKEN}", f"TELEGRAM_BOT_TOKEN={new_token}")
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            bot.reply_to(
                message,
                "✅ Το token άλλαξε με επιτυχία!\n\n"
                "Παρακαλώ επανεκκινήστε το bot για να εφαρμοστούν οι αλλαγές."
            )
            
            logger.info(f"Token changed by owner (ID: {user_id})")
        except Exception as e:
            bot.reply_to(message, f"❌ Σφάλμα κατά την αλλαγή του token: {str(e)}")
    else:
        bot.reply_to(
            message,
            "❌ Μη έγκυρη εντολή. Χρησιμοποιήστε:\n"
            "/token - Δες τις διαθέσιμες επιλογές\n"
            "/token info - Δες πληροφορίες για το τρέχον token\n"
            "/token change <new_token> - Άλλαξε το token"
        )

@bot.message_handler(commands=['status'])
def handle_status(message):
    """Handle the /status command."""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    logger.info(f"User {username} (ID: {user_id}) requested status.")
    
    uptime = datetime.now() - START_TIME
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    status_text = (
        "📊 *NOVAXA Bot Status:*\n\n"
        f"⏱ *Uptime:* {uptime.days}d {hours}h {minutes}m {seconds}s\n"
        f"👥 *Users:* {len(USERS)}\n"
        f"💬 *Messages:* {MESSAGE_COUNT}\n"
        f"🔄 *Version:* 3.0 (Termux)\n"
    )
    
    bot.reply_to(message, status_text, parse_mode="Markdown")

@bot.message_handler(commands=['getid'])
def handle_getid(message):
    """Handle the /getid command."""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    logger.info(f"User {username} (ID: {user_id}) requested their ID.")
    
    bot.reply_to(
        message,
        f"🆔 *Το Telegram ID σου είναι:* `{user_id}`\n\n"
        f"👤 *Username:* @{username}\n"
        f"👋 *First Name:* {message.from_user.first_name}\n"
        f"👋 *Last Name:* {message.from_user.last_name or 'N/A'}\n",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all other messages."""
    global MESSAGE_COUNT
    MESSAGE_COUNT += 1
    
    user_id = message.from_user.id
    USERS.add(user_id)
    
    if message.text and not message.text.startswith('/'):
        bot.reply_to(
            message,
            "Έλαβα το μήνυμά σου. Χρησιμοποίησε /help για να δεις τις διαθέσιμες εντολές."
        )

if __name__ == "__main__":
    logger.info("Starting NOVAXA Bot (Polling Mode)...")
    
    try:
        bot_info = bot.get_me()
        logger.info(f"Bot started: @{bot_info.username} (ID: {bot_info.id})")
        
        logger.info("Starting polling...")
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        sys.exit(1)
