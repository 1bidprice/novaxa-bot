import os
import sys
import time
import logging
import telebot
from dotenv import load_dotenv
import requests

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/bot.log')
    ]
)

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER_ID = os.getenv('OWNER_ID')
ADMIN_IDS = os.getenv('ADMIN_IDS', OWNER_ID)

if ADMIN_IDS and isinstance(ADMIN_IDS, str):
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS.split(',') if id.strip().isdigit()]
else:
    ADMIN_IDS = []

if OWNER_ID and OWNER_ID.isdigit():
    OWNER_ID = int(OWNER_ID)
    if OWNER_ID not in ADMIN_IDS:
        ADMIN_IDS.append(OWNER_ID)
else:
    OWNER_ID = None

logging.info(f"Owner ID set to: {OWNER_ID}")
logging.info(f"Admin IDs: {ADMIN_IDS}")

def validate_token(token):
    if not token:
        logging.error("No token provided. Please set TELEGRAM_BOT_TOKEN in .env file.")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                logging.info(f"Token validated successfully. Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})")
                return True
            else:
                logging.error(f"API returned ok=false: {data.get('description', 'Unknown error')}")
                return False
        elif response.status_code == 401:
            logging.error("Token is unauthorized. Please check if the token is correct or create a new one with BotFather.")
            return False
        else:
            logging.error(f"API returned status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error validating token: {str(e)}")
        return False

if not validate_token(TOKEN):
    logging.error("Token validation failed. Please fix the token and restart the bot.")
    print("\n=== Οδηγίες για διόρθωση του token ===")
    print("1. Ελέγξτε ότι το token στο αρχείο .env είναι σωστό")
    print("2. Αν χρειάζεται, δημιουργήστε νέο token από τον @BotFather στο Telegram")
    print("3. Τρέξτε το script validate_token.py για να ελέγξετε και να ενημερώσετε το token")
    print("4. Επανεκκινήστε το bot με ./start_polling_bot.sh")
    sys.exit(1)

try:
    bot = telebot.TeleBot(TOKEN)
    logging.info("Bot initialized successfully.")
except Exception as e:
    logging.error(f"Error initializing bot: {str(e)}")
    sys.exit(1)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Καλώς ήρθατε στο NOVAXA Bot! Χρησιμοποιήστε /help για να δείτε τις διαθέσιμες εντολές.")
    logging.info(f"User {message.from_user.id} started the bot")

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = """
Διαθέσιμες εντολές:
/start - Ξεκινήστε το bot
/help - Εμφανίστε αυτό το μήνυμα βοήθειας
/status - Ελέγξτε την κατάσταση του bot
/getid - Δείτε το Telegram ID σας

Εντολές διαχειριστή:
/notify <μήνυμα> - Στείλτε ειδοποίηση στον ιδιοκτήτη
/broadcast <μήνυμα> - Στείλτε μήνυμα σε όλους τους χρήστες
/log - Δείτε τα πρόσφατα logs

Εντολές ιδιοκτήτη:
/token - Διαχείριση token
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def handle_status(message):
    status_text = "✅ NOVAXA Bot λειτουργεί κανονικά!"
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['getid'])
def handle_getid(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    id_text = f"👤 Το Telegram ID σας είναι: {user_id}\n💬 Το Chat ID είναι: {chat_id}"
    bot.reply_to(message, id_text)

@bot.message_handler(commands=['notify'])
def handle_notify(message):
    if not OWNER_ID:
        bot.reply_to(message, "❌ Δεν έχει οριστεί ιδιοκτήτης για το bot.")
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Παρακαλώ δώστε ένα μήνυμα μετά την εντολή /notify")
        return
    
    notify_text = message.text.split(' ', 1)[1]
    user_info = f"Από: {message.from_user.first_name} (ID: {message.from_user.id})"
    full_message = f"📢 Ειδοποίηση!\n\n{notify_text}\n\n{user_info}"
    
    try:
        bot.send_message(OWNER_ID, full_message)
        bot.reply_to(message, "✅ Η ειδοποίηση στάλθηκε στον ιδιοκτήτη!")
    except Exception as e:
        logging.error(f"Error sending notification: {str(e)}")
        bot.reply_to(message, "❌ Σφάλμα κατά την αποστολή της ειδοποίησης.")

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Δεν έχετε δικαίωμα για αυτή την ενέργεια.")
        return
    
    if len(message.text.split()) < 2:
        bot.reply_to(message, "❌ Παρακαλώ δώστε ένα μήνυμα μετά την εντολή /broadcast")
        return
    
    broadcast_text = message.text.split(' ', 1)[1]
    full_message = f"📣 Broadcast Message\n\n{broadcast_text}"
    
    try:
        bot.send_message(message.chat.id, full_message)
        if OWNER_ID and OWNER_ID != message.from_user.id:
            bot.send_message(OWNER_ID, full_message)
        bot.reply_to(message, "✅ Το μήνυμα broadcast στάλθηκε!")
    except Exception as e:
        logging.error(f"Error sending broadcast: {str(e)}")
        bot.reply_to(message, "❌ Σφάλμα κατά την αποστολή του broadcast.")

@bot.message_handler(commands=['log'])
def handle_log(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Δεν έχετε δικαίωμα για αυτή την ενέργεια.")
        return
    
    try:
        with open('logs/bot.log', 'r') as f:
            logs = f.readlines()
        
        last_logs = logs[-10:]
        log_text = "📋 Τελευταίες καταγραφές:\n\n" + "".join(last_logs)
        
        if len(log_text) > 4000:
            log_text = log_text[:3997] + "..."
        
        bot.reply_to(message, log_text)
    except Exception as e:
        logging.error(f"Error reading logs: {str(e)}")
        bot.reply_to(message, "❌ Σφάλμα κατά την ανάγνωση των logs.")

@bot.message_handler(commands=['token'])
def handle_token(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Μόνο ο ιδιοκτήτης μπορεί να διαχειριστεί το token.")
        return
    
    command_parts = message.text.split()
    
    if len(command_parts) == 1:
        help_text = """
💼 Διαχείριση Token

Διαθέσιμες εντολές:
/token info - Δείτε πληροφορίες για το τρέχον token
/token change <new_token> - Αλλάξτε το token του bot

Σημείωση: Αυτές οι εντολές είναι διαθέσιμες μόνο για τον ιδιοκτήτη του bot.
"""
        bot.reply_to(message, help_text)
    
    elif len(command_parts) >= 2:
        subcommand = command_parts[1].lower()
        
        if subcommand == 'info':
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getMe"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        info_text = f"""
ℹ️ Πληροφορίες Token

🤖 Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})
🆔 Bot ID: {bot_info.get('id')}
🔑 Token: {TOKEN[:4]}...{TOKEN[-4:]}
✅ Κατάσταση: Έγκυρο
"""
                        bot.reply_to(message, info_text)
                    else:
                        bot.reply_to(message, f"❌ Σφάλμα: {data.get('description', 'Άγνωστο σφάλμα')}")
                else:
                    bot.reply_to(message, f"❌ Σφάλμα API: {response.status_code}")
            except Exception as e:
                logging.error(f"Error getting token info: {str(e)}")
                bot.reply_to(message, f"❌ Σφάλμα: {str(e)}")
        
        elif subcommand == 'change' and len(command_parts) >= 3:
            new_token = command_parts[2]
            
            format_valid, format_message = validate_token_format(new_token)
            if not format_valid:
                bot.reply_to(message, f"❌ Μη έγκυρο format token: {format_message}")
                return
            
            valid, api_message = check_token_with_telegram(new_token)
            if not valid:
                bot.reply_to(message, f"❌ Μη έγκυρο token: {api_message}")
                return
            
            try:
                with open('.env', 'r') as f:
                    lines = f.readlines()
                
                with open('.env', 'w') as f:
                    for line in lines:
                        if line.startswith('TELEGRAM_BOT_TOKEN='):
                            f.write(f'TELEGRAM_BOT_TOKEN={new_token}\n')
                        else:
                            f.write(line)
                
                bot.reply_to(message, "✅ Το token ενημερώθηκε επιτυχώς! Επανεκκινήστε το bot για να εφαρμοστούν οι αλλαγές.")
                logging.info(f"Token changed by owner (ID: {message.from_user.id})")
            except Exception as e:
                logging.error(f"Error updating token: {str(e)}")
                bot.reply_to(message, f"❌ Σφάλμα κατά την ενημέρωση του token: {str(e)}")
        
        else:
            bot.reply_to(message, "❌ Μη έγκυρη υποεντολή. Χρησιμοποιήστε /token για να δείτε τις διαθέσιμες εντολές.")

def validate_token_format(token):
    """Validate the format of a Telegram bot token."""
    if not token:
        return False, "Token is empty"
    
    parts = token.split(':')
    if len(parts) != 2:
        return False, "Token should contain exactly one colon (:)"
    
    bot_id, bot_hash = parts
    if not bot_id.isdigit():
        return False, "Bot ID part (before colon) should contain only digits"
    
    if len(bot_hash) < 30:
        return False, "Bot hash part (after colon) seems too short"
    
    return True, "Token format is valid"

def check_token_with_telegram(token):
    """Check if the token is valid by making a request to the Telegram API."""
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                return True, f"Token is valid! Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})"
            else:
                return False, f"API returned ok=false: {data.get('description', 'Unknown error')}"
        elif response.status_code == 401:
            return False, "Token is unauthorized. Please check if the token is correct or create a new one with BotFather."
        else:
            return False, f"API returned status code {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Error checking token: {str(e)}"

def main():
    logging.info("Starting NOVAXA Bot (Polling Mode)...")
    try:
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
        logging.error(f"Error starting bot: {str(e)}")
        print(f"❌ Σφάλμα εκκίνησης bot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
