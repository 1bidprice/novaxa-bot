#!/usr/bin/env python3
"""
Fix Telegram Bot Token Format
"""
import os
import sys
from dotenv import load_dotenv

def fix_token_format():
    """Fix the token format in the .env file."""
    # Load current .env file
    load_dotenv()
    
    # Get current token
    current_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not current_token:
        print("Error: No token found in .env file")
        return False
    
    # Check if token already has a colon
    if ":" in current_token:
        print(f"Token format appears valid: {current_token[:5]}...{current_token[-5:]}")
        return True
    
    print(f"Current token format is invalid: {current_token[:5]}...{current_token[-5:]}")
    print("Telegram bot tokens must contain a colon (:)")
    print("Example: 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ")
    
    # Ask for a new token
    new_token = input("Please enter a valid Telegram bot token: ")
    if not new_token or ":" not in new_token:
        print("Error: Invalid token format. Must contain a colon (:)")
        return False
    
    # Update .env file
    with open(".env", "r") as f:
        env_content = f.read()
    
    updated_content = env_content.replace(f"TELEGRAM_BOT_TOKEN={current_token}", f"TELEGRAM_BOT_TOKEN={new_token}")
    
    with open(".env", "w") as f:
        f.write(updated_content)
    
    print(f"Token updated successfully: {new_token[:5]}...{new_token[-5:]}")
    return True

if __name__ == "__main__":
    fix_token_format()
