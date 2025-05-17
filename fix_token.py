#!/usr/bin/env python3
"""
Fix Telegram Bot Token Format and Validate with API
"""
import os
import sys
import logging
import requests
import time
from dotenv import load_dotenv

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/token_fix.log')
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

def check_token_with_telegram(token, retries=3, delay=2):
    """Check if the token is valid by making a request to the Telegram API with retries."""
    for attempt in range(retries):
        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return True, f"Token is valid! Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})", bot_info
                else:
                    return False, f"API returned ok=false: {data.get('description', 'Unknown error')}", None
            elif response.status_code == 401:
                if attempt < retries - 1:
                    logging.warning(f"Token unauthorized (attempt {attempt+1}/{retries}). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                return False, "Token is unauthorized. Please check if the token is correct or create a new one with BotFather.", None
            else:
                if attempt < retries - 1:
                    logging.warning(f"API returned status code {response.status_code} (attempt {attempt+1}/{retries}). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                return False, f"API returned status code {response.status_code}: {response.text}", None
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Error checking token (attempt {attempt+1}/{retries}): {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            return False, f"Error checking token: {str(e)}", None
    
    return False, "Failed after multiple attempts to validate token", None

def fix_token_format():
    """Fix the token format in the .env file and validate with Telegram API."""
    # Load current .env file
    load_dotenv()
    
    # Get current token
    current_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not current_token:
        logging.error("No token found in .env file")
        print("❌ Error: No token found in .env file")
        return False
    
    format_valid, format_message = validate_token_format(current_token)
    if format_valid:
        logging.info(f"Token format is valid: {current_token[:5]}...{current_token[-5:]}")
        print(f"✅ Token format is valid: {current_token[:5]}...{current_token[-5:]}")
        
        api_valid, api_message, bot_info = check_token_with_telegram(current_token)
        if api_valid:
            logging.info(api_message)
            print(f"✅ {api_message}")
            return True
        else:
            logging.error(f"Token format is valid but API check failed: {api_message}")
            print(f"❌ Token format is valid but API check failed: {api_message}")
    else:
        logging.error(f"Token format is invalid: {format_message}")
        print(f"❌ Token format is invalid: {format_message}")
    
    fixed_token = current_token.strip()
    
    if (fixed_token.startswith('"') and fixed_token.endswith('"')) or \
       (fixed_token.startswith("'") and fixed_token.endswith("'")):
        fixed_token = fixed_token[1:-1]
        logging.info(f"Removed quotes from token: {fixed_token[:5]}...{fixed_token[-5:]}")
        print(f"✅ Removed quotes from token: {fixed_token[:5]}...{fixed_token[-5:]}")
    
    # Check if fixed token is valid
    format_valid, format_message = validate_token_format(fixed_token)
    if format_valid and fixed_token != current_token:
        # Update .env file with fixed token
        try:
            with open(".env", "r") as f:
                env_content = f.read()
            
            updated_content = env_content.replace(f"TELEGRAM_BOT_TOKEN={current_token}", f"TELEGRAM_BOT_TOKEN={fixed_token}")
            
            with open(".env", "w") as f:
                f.write(updated_content)
            
            logging.info(f"Token format fixed: {fixed_token[:5]}...{fixed_token[-5:]}")
            print(f"✅ Token format fixed: {fixed_token[:5]}...{fixed_token[-5:]}")
            
            api_valid, api_message, bot_info = check_token_with_telegram(fixed_token)
            if api_valid:
                logging.info(api_message)
                print(f"✅ {api_message}")
                return True
            else:
                logging.error(f"Fixed token format is valid but API check failed: {api_message}")
                print(f"❌ Fixed token format is valid but API check failed: {api_message}")
        except Exception as e:
            logging.error(f"Error updating token in .env file: {str(e)}")
            print(f"❌ Error updating token in .env file: {str(e)}")
    
    # If we get here, we need to ask for a new token
    print("\n📢 Telegram bot tokens must contain a colon (:)")
    print("📝 Example: 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ")
    print("\n🔄 Για να λάβετε ένα νέο token:")
    print("1. Ανοίξτε το Telegram και αναζητήστε @BotFather")
    print("2. Στείλτε την εντολή /start")
    print("3. Στείλτε την εντολή /newbot ή /mybots και επιλέξτε το bot σας")
    print("4. Αντιγράψτε το token που θα σας δώσει ο BotFather")
    
    # Ask for a new token
    new_token = input("\n📥 Παρακαλώ εισάγετε ένα έγκυρο Telegram bot token: ")
    
    format_valid, format_message = validate_token_format(new_token)
    if not format_valid:
        logging.error(f"New token format is invalid: {format_message}")
        print(f"❌ Μη έγκυρο format token: {format_message}")
        return False
    
    api_valid, api_message, bot_info = check_token_with_telegram(new_token)
    if not api_valid:
        logging.error(f"New token API check failed: {api_message}")
        print(f"❌ Μη έγκυρο token: {api_message}")
        return False
    
    # Update .env file with new token
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        updated_content = env_content.replace(f"TELEGRAM_BOT_TOKEN={current_token}", f"TELEGRAM_BOT_TOKEN={new_token}")
        
        with open(".env", "w") as f:
            f.write(updated_content)
        
        logging.info(f"Token updated successfully: {new_token[:5]}...{new_token[-5:]}")
        print(f"✅ Token ενημερώθηκε επιτυχώς: {new_token[:5]}...{new_token[-5:]}")
        print(f"✅ Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})")
        return True
    except Exception as e:
        logging.error(f"Error updating token in .env file: {str(e)}")
        print(f"❌ Σφάλμα κατά την ενημέρωση του token: {str(e)}")
        return False

if __name__ == "__main__":
    fix_token_format()
