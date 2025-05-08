"""
Security Module for NOVAXA Bot
-----------------------------
This module provides token management, authentication, and 
intellectual property protection for the NOVAXA Telegram bot.
"""

import os
import sys
import logging
import json
import time
import hashlib
import base64
import hmac
import secrets
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TokenManager:
    """Class for managing Telegram bot tokens and security."""
    
    def __init__(self, token_file: str = "config/tokens.json", master_key: str = None):
        """Initialize the token manager.
        
        Args:
            token_file: Path to token configuration file
            master_key: Master key for token encryption
        """
        self.token_file = token_file
        self.master_key = master_key or os.environ.get("NOVAXA_MASTER_KEY")
        self.tokens = {}
        self.active_token_id = None
        
        os.makedirs(os.path.dirname(token_file), exist_ok=True)
        
        self._load_tokens()
        
        logger.info("Token manager initialized")
    
    def _load_tokens(self):
        """Load tokens from file."""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, "r") as f:
                    data = json.load(f)
                    self.tokens = data.get("tokens", {})
                    self.active_token_id = data.get("active_token_id")
                    logger.info(f"Loaded {len(self.tokens)} tokens from configuration")
            else:
                logger.info("No tokens configuration file found, using defaults")
                self._save_tokens()
        except Exception as e:
            logger.error(f"Error loading tokens: {e}")
    
    def _save_tokens(self):
        """Save tokens to file."""
        try:
            data = {
                "tokens": self.tokens,
                "active_token_id": self.active_token_id,
                "last_updated": datetime.now().isoformat(),
            }
            
            with open(self.token_file, "w") as f:
                json.dump(data, f, indent=2)
                
            logger.info("Tokens configuration saved")
        except Exception as e:
            logger.error(f"Error saving tokens: {e}")
    
    def _encrypt(self, text: str) -> str:
        """Encrypt text using the master key."""
        if not self.master_key:
            logger.warning("No master key set, using plaintext")
            return text
            
        try:
            key = hashlib.sha256(self.master_key.encode()).digest()
            return base64.b64encode(
                hmac.new(key, text.encode(), hashlib.sha256).digest() +
                text.encode()
            ).decode()
        except Exception as e:
            logger.error(f"Error encrypting text: {e}")
            return text
    
    def _decrypt(self, encrypted_text: str) -> str:
        """Decrypt text using the master key."""
        if not self.master_key:
            logger.warning("No master key set, using plaintext")
            return encrypted_text
            
        try:
            data = base64.b64decode(encrypted_text.encode())
            text = data[32:].decode()
            return text
        except Exception as e:
            logger.error(f"Error decrypting text: {e}")
            return encrypted_text
    
    def add_token(self, token: str, name: str = "Default", owner_id: int = None) -> str:
        """Add a new token.
        
        Args:
            token: Telegram Bot API token
            name: Name for this token
            owner_id: Telegram user ID of the token owner
            
        Returns:
            str: Token ID
        """
        token_id = secrets.token_hex(8)
        
        self.tokens[token_id] = {
            "id": token_id,
            "token": self._encrypt(token),
            "name": name,
            "owner_id": owner_id,
            "created": datetime.now().isoformat(),
            "last_used": None,
            "status": "active",
        }
        
        if not self.active_token_id:
            self.active_token_id = token_id
        
        self._save_tokens()
        
        logger.info(f"Token {token_id} added")
        return token_id
    
    def update_token(self, token_id: str, token: str) -> bool:
        """Update an existing token.
        
        Args:
            token_id: Token ID to update
            token: New Telegram Bot API token
            
        Returns:
            bool: True if token was updated, False otherwise
        """
        if token_id not in self.tokens:
            logger.warning(f"Token {token_id} does not exist")
            return False
        
        self.tokens[token_id]["token"] = self._encrypt(token)
        self.tokens[token_id]["updated"] = datetime.now().isoformat()
        
        self._save_tokens()
        
        logger.info(f"Token {token_id} updated")
        return True
    
    def rotate_token(self, token_id: str, new_token: str) -> bool:
        """Rotate to a new token.
        
        Args:
            token_id: Token ID to rotate
            new_token: New Telegram Bot API token
            
        Returns:
            bool: True if token was rotated, False otherwise
        """
        return self.update_token(token_id, new_token)
    
    def activate_token(self, token_id: str) -> bool:
        """Set a token as active.
        
        Args:
            token_id: Token ID to activate
            
        Returns:
            bool: True if token was activated, False otherwise
        """
        if token_id not in self.tokens:
            logger.warning(f"Token {token_id} does not exist")
            return False
        
        self.active_token_id = token_id
        
        self._save_tokens()
        
        logger.info(f"Token {token_id} activated")
        return True
    
    def deactivate_token(self, token_id: str) -> bool:
        """Deactivate a token.
        
        Args:
            token_id: Token ID to deactivate
            
        Returns:
            bool: True if token was deactivated, False otherwise
        """
        if token_id not in self.tokens:
            logger.warning(f"Token {token_id} does not exist")
            return False
        
        self.tokens[token_id]["status"] = "inactive"
        
        if self.active_token_id == token_id:
            active_tokens = [tid for tid, t in self.tokens.items() 
                            if t["status"] == "active"]
            if active_tokens:
                self.active_token_id = active_tokens[0]
            else:
                self.active_token_id = None
        
        self._save_tokens()
        
        logger.info(f"Token {token_id} deactivated")
        return True
    
    def delete_token(self, token_id: str) -> bool:
        """Delete a token.
        
        Args:
            token_id: Token ID to delete
            
        Returns:
            bool: True if token was deleted, False otherwise
        """
        if token_id not in self.tokens:
            logger.warning(f"Token {token_id} does not exist")
            return False
        
        del self.tokens[token_id]
        
        if self.active_token_id == token_id:
            if self.tokens:
                self.active_token_id = list(self.tokens.keys())[0]
            else:
                self.active_token_id = None
        
        self._save_tokens()
        
        logger.info(f"Token {token_id} deleted")
        return True
    
    def get_token(self, token_id: str = None) -> str:
        """Get a token.
        
        Args:
            token_id: Token ID to get, or None for active token
            
        Returns:
            str: Token value
        """
        token_id = token_id or self.active_token_id
        
        if not token_id or token_id not in self.tokens:
            logger.warning("No active token found")
            return None
        
        token_data = self.tokens[token_id]
        
        if token_data["status"] == "inactive":
            logger.warning(f"Token {token_id} is inactive")
            return None
        
        token_data["last_used"] = datetime.now().isoformat()
        self._save_tokens()
        
        return self._decrypt(token_data["token"])
    
    def get_tokens(self) -> List[Dict]:
        """Get all tokens.
        
        Returns:
            list: List of token information (without actual token values)
        """
        return [{
            "id": token_id,
            "name": token["name"],
            "owner_id": token["owner_id"],
            "created": token["created"],
            "updated": token.get("updated"),
            "last_used": token.get("last_used"),
            "status": token["status"],
            "active": token_id == self.active_token_id,
        } for token_id, token in self.tokens.items()]


class SecurityMonitor:
    """Class for monitoring security-related events."""
    
    def __init__(self, log_file: str = "logs/security.log", max_logs: int = 1000):
        """Initialize the security monitor."""
        self.log_file = log_file
        self.max_logs = max_logs
        self.logs = []
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
        
        logger.info("Security monitor initialized")
    
    def log_event(self, event_type: str, details: Dict = None, user_id: int = None):
        """Log a security event."""
        timestamp = datetime.now()
        
        event = {
            "timestamp": timestamp.isoformat(),
            "type": event_type,
            "details": details or {},
            "user_id": user_id,
        }
        
        self.logs.append(event)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        log_message = f"Security event: {event_type}"
        if user_id:
            log_message += f" (User: {user_id})"
        
        logger.info(log_message)
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Error writing to security log file: {e}")
    
    def get_recent_events(self, count: int = 10, event_type: str = None, user_id: int = None) -> List[Dict]:
        """Get recent security events."""
        filtered_events = self.logs
        
        if event_type:
            filtered_events = [event for event in filtered_events if event["type"] == event_type]
        
        if user_id:
            filtered_events = [event for event in filtered_events if event["user_id"] == user_id]
        
        filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return filtered_events[:count]


class IPProtection:
    """Class for intellectual property protection."""
    
    def __init__(self, owner_id: int = None):
        """Initialize IP protection."""
        self.owner_id = owner_id or int(os.environ.get("OWNER_ID", "0"))
        self.security_monitor = SecurityMonitor()
        logger.info("IP protection initialized")
    
    def verify_owner(self, user_id: int) -> bool:
        """Verify if a user is the owner.
        
        Args:
            user_id: User ID to check
            
        Returns:
            bool: True if user is the owner, False otherwise
        """
        if not self.owner_id:
            logger.warning("No owner ID set")
            return False
            
        is_owner = user_id == self.owner_id
        
        if not is_owner:
            self.security_monitor.log_event(
                "owner_verification_failed",
                {"attempted_user_id": user_id},
                user_id
            )
            
        return is_owner
    
    def log_usage(self, feature: str, user_id: int = None):
        """Log feature usage for licensing purposes."""
        self.security_monitor.log_event(
            "feature_usage",
            {"feature": feature},
            user_id
        )
