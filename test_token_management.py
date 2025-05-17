#!/usr/bin/env python3
"""
Test Token Management Functionality
----------------------------------
This script tests the token management functionality of the NOVAXA bot.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_token")

def test_token_validation():
    """Test token format validation."""
    logger.info("Testing token format validation...")
    
    # Valid token
    valid_token = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    logger.info(f"Valid token: {valid_token}")
    logger.info(f"Contains colon: {':' in valid_token}")
    
    # Invalid token
    invalid_token = "1234567890AAEabcdefghijklmnopqrstuvwxyz"
    logger.info(f"Invalid token: {invalid_token}")
    logger.info(f"Contains colon: {':' in invalid_token}")
    
    # Fix invalid token
    if ':' not in invalid_token and 'AAE' in invalid_token:
        fixed_token = invalid_token.replace('AAE', ':AAE', 1)
        logger.info(f"Fixed token: {fixed_token}")
        logger.info(f"Contains colon: {':' in fixed_token}")

def test_token_management():
    """Test token management functionality."""
    logger.info("Testing token management functionality...")
    
    # Create a test environment file
    with open('.env.test', 'w') as f:
        f.write('TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ\n')
        f.write('OWNER_ID=123456789\n')
        f.write('NOVAXA_MASTER_KEY=test_master_key\n')
    
    # Load the test environment
    load_dotenv('.env.test')
    
    # Get token from environment
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    logger.info(f"Token from environment: {token}")
    
    # Test token changing
    new_token = "9876543210:ZYXWVUTSRQPONMLKJIHGFEDCBA"
    logger.info(f"New token: {new_token}")
    
    # Simulate changing token in .env file
    with open('.env.test', 'r') as f:
        env_content = f.read()
    
    env_content = env_content.replace(f"TELEGRAM_BOT_TOKEN={token}", f"TELEGRAM_BOT_TOKEN={new_token}")
    
    with open('.env.test', 'w') as f:
        f.write(env_content)
    
    # Reload environment
    load_dotenv('.env.test', override=True)
    
    # Get updated token
    updated_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    logger.info(f"Updated token: {updated_token}")
    logger.info(f"Token changed successfully: {updated_token == new_token}")

def main():
    """Main function."""
    logger.info("=== NOVAXA Bot Token Management Test ===")
    
    test_token_validation()
    print()
    
    test_token_management()
    print()
    
    logger.info("=== Test Complete ===")

if __name__ == "__main__":
    main()
