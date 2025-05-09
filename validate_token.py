import os
import sys
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/token_validation.log')
    ]
)

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

def get_token_from_env():
    """Get the token from the .env file."""
    load_dotenv()
    return os.getenv('TELEGRAM_BOT_TOKEN')

def get_new_token_from_botfather():
    """Instructions for getting a new token from BotFather."""
    print("\n=== Οδηγίες για δημιουργία νέου token από το BotFather ===")
    print("1. Ανοίξτε το Telegram και αναζητήστε @BotFather")
    print("2. Στείλτε την εντολή /start")
    print("3. Στείλτε την εντολή /newbot για να δημιουργήσετε νέο bot")
    print("4. Ακολουθήστε τις οδηγίες για να δώσετε όνομα στο bot")
    print("5. Αντιγράψτε το token που θα σας δώσει ο BotFather")
    print("6. Επιστρέψτε εδώ και εισάγετε το νέο token")
    print("=== ή ===")
    print("1. Αν έχετε ήδη bot, στείλτε /mybots στον @BotFather")
    print("2. Επιλέξτε το bot σας")
    print("3. Επιλέξτε API Token")
    print("4. Αντιγράψτε το token")
    print("=== ή ===")
    print("1. Στείλτε /revoke στον @BotFather για να ανανεώσετε το token ενός υπάρχοντος bot")
    print("2. Επιλέξτε το bot σας")
    print("3. Αντιγράψτε το νέο token\n")

def update_token_in_env(token):
    """Update the token in the .env file."""
    try:
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        with open('.env', 'w') as f:
            for line in lines:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    f.write(f'TELEGRAM_BOT_TOKEN={token}\n')
                else:
                    f.write(line)
        return True, "Token updated in .env file"
    except Exception as e:
        return False, f"Error updating token in .env file: {str(e)}"

def main():
    """Main function to validate and test a Telegram bot token."""
    os.makedirs('logs', exist_ok=True)
    
    token = get_token_from_env()
    if len(sys.argv) > 1:
        token = sys.argv[1]
    
    if not token:
        logging.error("No token found in .env file or command line arguments")
        print("Παρακαλώ εισάγετε το Telegram bot token σας:")
        token = input().strip()
    
    format_valid, format_message = validate_token_format(token)
    if format_valid:
        logging.info(format_message)
        print(f"✓ {format_message}")
    else:
        logging.error(format_message)
        print(f"✗ {format_message}")
        print("Παρακαλώ εισάγετε ένα έγκυρο token:")
        token = input().strip()
        format_valid, format_message = validate_token_format(token)
        if not format_valid:
            logging.error("Token format still invalid after retry")
            print("Το format του token εξακολουθεί να μην είναι έγκυρο.")
            get_new_token_from_botfather()
            return
    
    valid, message = check_token_with_telegram(token)
    if valid:
        logging.info(message)
        print(f"✓ {message}")
        
        current_token = get_token_from_env()
        if current_token != token:
            update_success, update_message = update_token_in_env(token)
            if update_success:
                logging.info(update_message)
                print(f"✓ {update_message}")
            else:
                logging.error(update_message)
                print(f"✗ {update_message}")
    else:
        logging.error(message)
        print(f"✗ {message}")
        get_new_token_from_botfather()
        
        print("\nΘέλετε να εισάγετε ένα νέο token τώρα; (y/n)")
        choice = input().strip().lower()
        if choice == 'y':
            print("Παρακαλώ εισάγετε το νέο token:")
            new_token = input().strip()
            format_valid, format_message = validate_token_format(new_token)
            if format_valid:
                valid, message = check_token_with_telegram(new_token)
                if valid:
                    update_success, update_message = update_token_in_env(new_token)
                    if update_success:
                        logging.info(f"New token validated and updated: {message}")
                        print(f"✓ Το νέο token επικυρώθηκε και ενημερώθηκε: {message}")
                    else:
                        logging.error(update_message)
                        print(f"✗ {update_message}")
                else:
                    logging.error(f"New token validation failed: {message}")
                    print(f"✗ Η επικύρωση του νέου token απέτυχε: {message}")
            else:
                logging.error(f"New token format invalid: {format_message}")
                print(f"✗ Το format του νέου token δεν είναι έγκυρο: {format_message}")

if __name__ == "__main__":
    main()
