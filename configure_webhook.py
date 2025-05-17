"""
NOVAXA Bot Webhook Configuration Script

This script helps you configure the webhook for your NOVAXA Telegram bot.
It will check the current webhook status and set it to the correct URL.

Usage:
    python configure_webhook.py --token TOKEN --url URL [--chat-id CHAT_ID] [--use-manager]

Example:
    python configure_webhook.py --token 1234567890:ABCDEF-ghijklmnopqrstuvwxyz --url https://novaxa-bot.onrender.com
    python configure_webhook.py --token token_id_123 --url https://novaxa-bot.onrender.com --use-manager
"""

import sys
import requests
import json
import time
import argparse
import getpass
import os

token_manager_available = False
try:
    from security import TokenManager
    token_manager_available = True
except ImportError:
    pass

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="NOVAXA Bot Webhook Configuration")
    
    parser.add_argument("--token", help="Bot token or token ID from token manager")
    parser.add_argument("--url", help="Render URL (e.g., https://novaxa-bot.onrender.com)")
    parser.add_argument("--chat-id", help="Chat ID to send test message to")
    
    if token_manager_available:
        parser.add_argument("--use-manager", action="store_true", 
                          help="Use token manager instead of direct token")
    
    return parser.parse_args()

def get_token_from_manager(token_id):
    """Get token from token manager."""
    if not token_manager_available:
        print("❌ Token manager not available. Please install the security module.")
        return None
    
    try:
        master_key = os.environ.get("NOVAXA_MASTER_KEY")
        if not master_key:
            print("NOVAXA_MASTER_KEY not set in environment.")
            master_key = getpass.getpass("Enter master key: ")
        
        token_manager = TokenManager(master_key=master_key)
        
        if token_id == "active":
            token = token_manager.get_token()
            if not token:
                print("❌ No active token found.")
                return None
            return token
        else:
            token = token_manager.get_token(token_id)
            if not token:
                print(f"❌ Token with ID {token_id} not found.")
                return None
            return token
    
    except Exception as e:
        print(f"❌ Error getting token from manager: {e}")
        return None

def check_webhook_status(token):
    """Check the current webhook status."""
    print("\n🔍 Checking current webhook status...")
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        webhook_info = response.json()
        
        if webhook_info.get("ok") and webhook_info.get("result"):
            result = webhook_info["result"]
            if result.get("url"):
                print(f"✅ Current webhook URL: {result['url']}")
                print(f"📊 Pending updates: {result.get('pending_update_count', 0)}")
                if result.get("last_error_date"):
                    print(f"❌ Last error: {result.get('last_error_message', 'Unknown error')}")
                    print(f"⏰ Last error date: {result.get('last_error_date')}")
                return result.get("url")
            else:
                print("ℹ️ No webhook URL set. Bot is in polling mode.")
                return None
        else:
            print(f"❌ Error: {webhook_info.get('description', 'Unknown error')}")
            return None
    
    except Exception as e:
        print(f"❌ Error checking webhook status: {e}")
        return None

def set_webhook(token, webhook_url):
    """Set the webhook URL."""
    print(f"\n🔧 Setting webhook to: {webhook_url}")
    
    if not webhook_url.endswith("/webhook"):
        webhook_url = webhook_url.rstrip("/") + "/webhook"
        print(f"ℹ️ Added /webhook to URL: {webhook_url}")
    
    url = f"https://api.telegram.org/bot{token}/setWebhook"
    params = {
        "url": webhook_url,
        "drop_pending_updates": True
    }
    
    try:
        response = requests.post(url, params=params)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Webhook successfully set to: {webhook_url}")
            return True
        else:
            print(f"❌ Error setting webhook: {result.get('description', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error setting webhook: {e}")
        return False

def test_bot(token):
    """Test if the bot is accessible."""
    print("\n🤖 Testing bot connection...")
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("ok"):
            bot_info = result["result"]
            print(f"✅ Bot username: @{bot_info.get('username')}")
            print(f"✅ Bot name: {bot_info.get('first_name')}")
            print(f"✅ Bot ID: {bot_info.get('id')}")
            return True
        else:
            print(f"❌ Error: {result.get('description', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        return False

def send_test_message(token, chat_id=None):
    """Send a test message to verify the bot is working."""
    if not chat_id:
        print("\n⚠️ No chat ID provided. Skipping test message.")
        return False
    
    print(f"\n📤 Sending test message to chat ID: {chat_id}")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": "🎉 NOVAXA Bot webhook has been configured successfully! 🎉\n\nThis is a test message to verify the bot is working.",
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, params=params)
        result = response.json()
        
        if result.get("ok"):
            print(f"✅ Test message sent successfully to chat ID: {chat_id}")
            return True
        else:
            print(f"❌ Error sending message: {result.get('description', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def update_render_env_vars(render_url, webhook_url):
    """Provide instructions to update Render environment variables."""
    print("\n📝 To complete the setup, update these environment variables in Render:")
    print("1. Go to your Render dashboard")
    print("2. Select the NOVAXA bot service")
    print("3. Click on 'Environment' tab")
    print("4. Add or update these variables:")
    print("\n```")
    print("WEBHOOK_ENABLED=true")
    print(f"WEBHOOK_URL={webhook_url}")
    print("RENDER=true")
    print("```")
    print("\n5. Click 'Save Changes'")
    print("6. Go to the 'Manual Deploy' tab")
    print("7. Click 'Deploy latest commit'")

def format_output(title, message="", is_error=False):
    """Format output with colors for Termux."""
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    BOLD = "\033[1m"
    
    color = RED if is_error else GREEN
    
    print(f"\n{BOLD}{color}=== {title} ==={RESET}")
    if message:
        print(message)

def main():
    """Main function to configure the webhook."""
    args = parse_arguments()
    
    if not args.token or not args.url:
        print(__doc__)
        sys.exit(1)
    
    format_output("NOVAXA Bot Webhook Configuration Tool")
    
    token = args.token
    if hasattr(args, 'use_manager') and args.use_manager:
        if not token_manager_available:
            format_output("Error", "Token manager not available. Please install the security module.", True)
            sys.exit(1)
        
        token = get_token_from_manager(args.token)
        if not token:
            format_output("Error", f"Failed to get token {args.token} from token manager.", True)
            sys.exit(1)
    
    if not test_bot(token):
        format_output("Error", "Bot connection failed. Please check your token and try again.", True)
        sys.exit(1)
    
    current_webhook = check_webhook_status(token)
    
    webhook_url = args.url.rstrip("/") + "/webhook"
    
    if current_webhook != webhook_url:
        if set_webhook(token, webhook_url):
            format_output("Waiting", "Waiting for webhook to activate...")
            time.sleep(2)
            check_webhook_status(token)
        else:
            format_output("Error", "Failed to set webhook. Please check your Render URL and try again.", True)
            sys.exit(1)
    else:
        format_output("Success", "Webhook is already correctly configured.")
    
    if args.chat_id:
        send_test_message(token, args.chat_id)
    
    update_render_env_vars(args.url, webhook_url)
    
    format_output("Webhook Configuration Complete")
    print("\n🔍 To test your bot, send a message to it on Telegram.")
    print("If it doesn't respond, check the Render logs for errors.")

if __name__ == "__main__":
    main()
