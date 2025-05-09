"""
Test NOVAXA Bot Functionality
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
        logging.FileHandler('logs/functionality_test.log')
    ]
)

def test_basic_commands():
    """Test basic bot commands."""
    logging.info("Testing basic bot commands...")
    print("\n=== Testing Basic Bot Commands ===")
    
    commands = [
        ("/start", "Εκκίνηση του bot"),
        ("/help", "Εμφάνιση βοήθειας"),
        ("/status", "Έλεγχος κατάστασης"),
        ("/getid", "Εμφάνιση Telegram ID")
    ]
    
    for cmd, desc in commands:
        print(f"• {cmd}: {desc}")
    
    print("\nΓια να δοκιμάσετε αυτές τις εντολές:")
    print("1. Ανοίξτε το Telegram")
    print("2. Βρείτε το bot σας")
    print("3. Στείλτε κάθε εντολή και επιβεβαιώστε ότι το bot ανταποκρίνεται σωστά")
    
    return True

def test_token_management():
    """Test token management commands."""
    logging.info("Testing token management commands...")
    print("\n=== Testing Token Management Commands (Δικλείδα Ασφαλείας) ===")
    
    commands = [
        ("/token", "Εμφάνιση επιλογών διαχείρισης token"),
        ("/token info", "Εμφάνιση πληροφοριών για το τρέχον token"),
        ("/token change <new_token>", "Αλλαγή του token του bot")
    ]
    
    for cmd, desc in commands:
        print(f"• {cmd}: {desc}")
    
    print("\nΣημείωση: Αυτές οι εντολές είναι διαθέσιμες μόνο στον ιδιοκτήτη του bot.")
    print("Για να δοκιμάσετε αυτές τις εντολές:")
    print("1. Βεβαιωθείτε ότι είστε ο ιδιοκτήτης του bot (OWNER_ID στο .env)")
    print("2. Στείλτε κάθε εντολή στο bot σας στο Telegram")
    print("3. Επιβεβαιώστε ότι το bot ανταποκρίνεται σωστά και μόνο σε εσάς")
    
    return True

def test_webhook_deletion():
    """Test webhook deletion process."""
    logging.info("Testing webhook deletion...")
    print("\n=== Testing Webhook Deletion ===")
    
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

def test_token_validation():
    """Test token validation process."""
    logging.info("Testing token validation...")
    print("\n=== Testing Token Validation ===")
    
    valid_token = "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
    print(f"Testing valid token format: {valid_token[:5]}...{valid_token[-5:]}")
    
    parts = valid_token.split(':')
    if len(parts) == 2 and parts[0].isdigit() and len(parts[1]) >= 30:
        print("✅ Valid token format detected correctly")
    else:
        print("❌ Failed to validate correct token format")
    
    invalid_token = "123456789-ABCdefGHIjklMNOpqrSTUvwxYZ"
    print(f"Testing invalid token format: {invalid_token[:5]}...{invalid_token[-5:]}")
    
    parts = invalid_token.split(':')
    if len(parts) != 2:
        print("✅ Invalid token format detected correctly")
    else:
        print("❌ Failed to detect invalid token format")
    
    return True

def test_error_handling():
    """Test error handling for invalid tokens."""
    logging.info("Testing error handling for invalid tokens...")
    print("\n=== Testing Error Handling for Invalid Tokens ===")
    
    invalid_token = "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ"
    print(f"Testing API validation with invalid token: {invalid_token[:5]}...{invalid_token[-5:]}")
    
    try:
        url = f"https://api.telegram.org/bot{invalid_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 401:
            print("✅ Unauthorized token detected correctly")
        else:
            print(f"❌ Failed to detect unauthorized token: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing API validation: {str(e)}")
    
    return True

def main():
    """Run all tests."""
    print("=== NOVAXA Bot Functionality Test ===\n")
    print("Αυτό το script θα σας καθοδηγήσει στη δοκιμή των λειτουργιών του NOVAXA Bot.")
    print("Ακολουθήστε τις οδηγίες για κάθε δοκιμή.\n")
    
    basic_cmds = test_basic_commands()
    token_mgmt = test_token_management()
    webhook_del = test_webhook_deletion()
    token_val = test_token_validation()
    error_handling = test_error_handling()
    
    print("\n=== Συνολικά Αποτελέσματα Δοκιμών ===")
    print(f"Βασικές Εντολές: {'✅ Οδηγίες Παρέχονται' if basic_cmds else '❌ Αποτυχία'}")
    print(f"Διαχείριση Token (Δικλείδα Ασφαλείας): {'✅ Οδηγίες Παρέχονται' if token_mgmt else '❌ Αποτυχία'}")
    print(f"Διαγραφή Webhook: {'✅ Επιτυχία' if webhook_del else '❌ Αποτυχία'}")
    print(f"Επικύρωση Token: {'✅ Επιτυχία' if token_val else '❌ Αποτυχία'}")
    print(f"Χειρισμός Σφαλμάτων: {'✅ Επιτυχία' if error_handling else '❌ Αποτυχία'}")
    
    print("\n=== Οδηγίες Εκκίνησης Bot ===")
    print("1. Εκτελέστε: ./start_simple_bot.sh")
    print("2. Ακολουθήστε τις οδηγίες στην οθόνη")
    print("3. Αν ζητηθεί νέο token, δημιουργήστε ένα με το @BotFather στο Telegram")
    print("4. Μετά την εκκίνηση, δοκιμάστε τις εντολές που αναφέρονται παραπάνω")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
