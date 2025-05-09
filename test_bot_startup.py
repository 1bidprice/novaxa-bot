"""
Test NOVAXA Bot Startup Process
"""
import os
import sys
import logging
import requests
from dotenv import load_dotenv

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/startup_test.log')
    ]
)

def test_token_validation():
    """Test token validation process."""
    logging.info("Testing token validation...")
    
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logging.error("No token found in .env file")
        print("❌ No token found in .env file")
        return False
    
    parts = token.split(':')
    if len(parts) != 2:
        logging.error("Token format is invalid: should contain exactly one colon (:)")
        print("❌ Token format is invalid: should contain exactly one colon (:)")
        return False
    
    bot_id, bot_hash = parts
    if not bot_id.isdigit():
        logging.error("Token format is invalid: Bot ID part (before colon) should contain only digits")
        print("❌ Token format is invalid: Bot ID part (before colon) should contain only digits")
        return False
    
    logging.info(f"Token format is valid: {token[:5]}...{token[-5:]}")
    print(f"✅ Token format is valid: {token[:5]}...{token[-5:]}")
    return True

def test_webhook_deletion():
    """Test webhook deletion process."""
    logging.info("Testing webhook deletion...")
    
    load_dotenv()
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logging.error("No token found in .env file")
        print("❌ No token found in .env file")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logging.info("Webhook deleted successfully")
                print("✅ Webhook deleted successfully")
                return True
            else:
                logging.error(f"Failed to delete webhook: {data.get('description', 'Unknown error')}")
                print(f"❌ Failed to delete webhook: {data.get('description', 'Unknown error')}")
                return False
        else:
            logging.error(f"API returned status code {response.status_code}: {response.text}")
            print(f"❌ API returned status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error deleting webhook: {str(e)}")
        print(f"❌ Error deleting webhook: {str(e)}")
        return False

def test_bot_initialization():
    """Test bot initialization process."""
    logging.info("Testing bot initialization...")
    
    try:
        import telebot
        logging.info("Telebot imported successfully")
        print("✅ Telebot imported successfully")
        
        if not os.path.exists('simple_bot.py'):
            logging.error("simple_bot.py not found")
            print("❌ simple_bot.py not found")
            return False
        
        logging.info("Bot initialization test passed")
        print("✅ Bot initialization test passed")
        return True
    except ImportError:
        logging.error("Failed to import telebot. Make sure it's installed: pip install pyTelegramBotAPI")
        print("❌ Failed to import telebot. Make sure it's installed: pip install pyTelegramBotAPI")
        return False
    except Exception as e:
        logging.error(f"Error testing bot initialization: {str(e)}")
        print(f"❌ Error testing bot initialization: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("=== NOVAXA Bot Startup Test ===\n")
    
    token_valid = test_token_validation()
    webhook_deleted = test_webhook_deletion()
    bot_init = test_bot_initialization()
    
    print("\n=== Test Results ===")
    print(f"Token Validation: {'✅ Passed' if token_valid else '❌ Failed'}")
    print(f"Webhook Deletion: {'✅ Passed' if webhook_deleted else '❌ Failed'}")
    print(f"Bot Initialization: {'✅ Passed' if bot_init else '❌ Failed'}")
    
    if token_valid and webhook_deleted and bot_init:
        print("\n✅ All tests passed! The bot should start without errors.")
        print("Run ./start_simple_bot.sh to start the bot.")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix the issues before starting the bot.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
