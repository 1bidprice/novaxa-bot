"""
Delete Telegram Bot Webhook
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
        logging.FileHandler('logs/webhook.log')
    ]
)

def delete_webhook(token=None):
    """Delete the webhook for a Telegram bot."""
    if not token:
        load_dotenv()
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logging.error("No token found")
        print("❌ Error: No token found")
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

if __name__ == "__main__":
    delete_webhook()
