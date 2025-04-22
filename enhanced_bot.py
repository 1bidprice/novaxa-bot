
"""
NOVAXA Telegram Bot
----------------
This is the main module for the NOVAXA Telegram bot.

It provides command handling, user management, and system monitoring.
The bot can operate in either webhook or polling mode.
"""

import os
import sys
import logging
import json
import time
import threading
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from collections import defaultdict, deque
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from dotenv import load_dotenv

load_dotenv()

try:
    from api import TelegramAPI, DataProcessor
    from monitor import SystemMonitor, PerformanceTracker
    from integration import ServiceIntegration, NotificationSystem
except ImportError as e:
    print(f"Error importing custom modules: {e}")
    print("Make sure all required modules are in the same directory.")
    sys.exit(1)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level))

os.makedirs("logs", exist_ok=True)

file_handler = logging.FileHandler("logs/bot.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)


class EnhancedBot:
    """Main class for the NOVAXA Telegram bot."""
    
    def __init__(self):
        """Initialize the bot."""
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.token:
            logger.error("No Telegram token provided")
            raise ValueError("Telegram token is required")
        
        self.debug = os.environ.get("DEBUG", "false").lower() == "true"
        self.webhook_enabled = os.environ.get("WEBHOOK_ENABLED", "false").lower() == "true"
        self.webhook_url = os.environ.get("WEBHOOK_URL", "")
        self.port = int(os.environ.get("PORT", "8443"))
        
        admin_ids_str = os.environ.get("ADMIN_IDS", "")
        self.admin_ids = [int(admin_id.strip()) for admin_id in admin_ids_str.split(",") if admin_id.strip()]
        
        self.bot = telebot.TeleBot(self.token, parse_mode="HTML")
        
        self.api = TelegramAPI(self.token)
        self.data_processor = DataProcessor()
        self.monitor = SystemMonitor()
        self.performance_tracker = PerformanceTracker()
        self.service_integration = ServiceIntegration()
        self.notification_system = NotificationSystem(self.service_integration)
        
        self.user_data = {}
        self.rate_limits = defaultdict(lambda: {"count": 0, "last_reset": time.time()})
        self.rate_limit_interval = 60  # seconds
        self.rate_limit_max = 30  # commands per interval
        
        self._register_handlers()
        
        logger.info("Bot initialized")
    
    def _register_handlers(self):
        """Register command and message handlers."""
        self.bot.message_handler(commands=["start"])(self.handle_start)
        self.bot.message_handler(commands=["help"])(self.handle_help)
        self.bot.message_handler(commands=["status"])(self.handle_status)
        self.bot.message_handler(commands=["getid"])(self.handle_getid)
        self.bot.message_handler(commands=["notify"])(self.handle_notify)
        self.bot.message_handler(commands=["broadcast"])(self.handle_broadcast)
        self.bot.message_handler(commands=["alert"])(self.handle_alert)
        self.bot.message_handler(commands=["log"])(self.handle_log)
        
        self.bot.message_handler(commands=["maintenance"])(self.handle_maintenance)
        self.bot.message_handler(commands=["users"])(self.handle_users)
        
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback_query)
        
        self.bot.message_handler(func=lambda message: True)(self.handle_message)
        
        logger.info("Command handlers registered")
    
    def start(self):
        """Start the bot."""
        logger.info("Starting bot...")
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if self.webhook_enabled and self.webhook_url:
            self._start_webhook()
        else:
            self._start_polling()
    
    def _start_webhook(self):
        """Start the bot in webhook mode."""
        logger.info(f"Starting bot in webhook mode at {self.webhook_url}")
        
        self.bot.remove_webhook()
        time.sleep(0.5)
        
        self.bot.set_webhook(url=self.webhook_url)
        
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route("/", methods=["GET"])
        def index():
            return jsonify({"status": "ok", "message": "NOVAXA Bot is running"})
        
        @app.route("/webhook", methods=["POST"])
        def webhook():
            if request.headers.get("content-type") == "application/json":
                update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
                self.bot.process_new_updates([update])
                return jsonify({"status": "ok"})
            else:
                return jsonify({"status": "error", "message": "Invalid content type"})
        
        @app.route("/health", methods=["GET"])
        def health():
            status = self.monitor.get_system_status()
            return jsonify(status)
        
        app.run(host="0.0.0.0", port=self.port)
    
    def _start_polling(self):
        """Start the bot in polling mode."""
        logger.info("Starting bot in polling mode")
        
        self.bot.remove_webhook()
        
        self.bot.infinity_polling()
    
    def _signal_handler(self, sig, frame):
        """Handle signals for graceful shutdown."""
        logger.info(f"Received signal {sig}, shutting down...")
        
        self.monitor.stop()
        
        self.bot.stop_polling()
        
        sys.exit(0)
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Check if a user has exceeded the rate limit."""
        current_time = time.time()
        user_rate = self.rate_limits[user_id]
        
        if current_time - user_rate["last_reset"] > self.rate_limit_interval:
            user_rate["count"] = 0
            user_rate["last_reset"] = current_time
        
        user_rate["count"] += 1
        
        return user_rate["count"] > self.rate_limit_max
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if a user is an admin."""
        return user_id in self.admin_ids
    
    def _get_user_data(self, user_id: int) -> Dict:
        """Get user data, creating it if it doesn't exist."""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "id": user_id,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "command_count": 0,
                "settings": {
                    "language": "en",
                    "notifications": True,
                },
            }
        else:
            self.user_data[user_id]["last_seen"] = datetime.now().isoformat()
            
        return self.user_data[user_id]
    
    def _update_user_command_count(self, user_id: int):
        """Update user command count."""
        user_data = self._get_user_data(user_id)
        user_data["command_count"] += 1
    
    def handle_start(self, message):
        """Handle /start command."""
        start_time = time.time()
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if self._check_rate_limit(user_id):
            self.bot.reply_to(message, "⚠️ Rate limit exceeded. Please try again later.")
            return
        
        user_data = self._get_user_data(user_id)
        self._update_user_command_count(user_id)
        
        self.monitor.log_activity(user_id, "start", {
            "chat_id": chat_id,
            "username": message.from_user.username,
        })
        
        welcome_text = (
            f"👋 Welcome to <b>NOVAXA</b> Bot!\n\n"
            f"I'm your advanced Telegram assistant with professional capabilities and automations.\n\n"
            f"Use /help to see available commands."
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        help_button = types.InlineKeyboardButton("📚 Help", callback_data="help")
        status_button = types.InlineKeyboardButton("📊 Status", callback_data="status")
        markup.add(help_button, status_button)
        
        self.bot.send_message(chat_id, welcome_text, reply_markup=markup)
        
        self.performance_tracker.track_response_time(start_time)
    
    def handle_help(self, message):
        """Handle /help command."""
        start_time = time.time()
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if self._check_rate_limit(user_id):
            self.bot.reply_to(message, "⚠️ Rate limit exceeded. Please try again later.")
            return
        
        user_data = self._get_user_data(user_id)
        self._update_user_command_count(user_id)
        
        self.monitor.log_activity(user_id, "help", {
            "chat_id": chat_id,
            "username": message.from_user.username,
        })
        
        help_text = (
            f"🤖 <b>NOVAXA Bot Commands</b>\n\n"
            f"<b>Basic Commands:</b>\n"
            f"/start - Start the bot\n"
            f"/help - Show this help message\n"
            f"/status - Show bot status\n"
            f"/getid - Get your Telegram ID\n\n"
        )
        
        if self._is_admin(user_id):
            help_text += (
                f"<b>Admin Commands:</b>\n"
                f"/notify [user_id] [message] - Send notification to a user\n"
                f"/broadcast [message] - Send message to all users\n"
                f"/alert [message] - Send alert to all admins\n"
                f"/log [count] - Show recent logs\n"
                f"/maintenance - Toggle maintenance mode\n"
                f"/users - Show user statistics\n\n"
            )
        
        self.bot.send_message(chat_id, help_text)
        
        self.performance_tracker.track_response_time(start_time)
    

    def handle_status(self, message):
        """Handle /status command."""
        start_time = time.time()
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if self._check_rate_limit(user_id):
            self.bot.reply_to(message, "⚠️ Rate limit exceeded. Please try again later.")
            return
        
        self._update_user_command_count(user_id)
        self.monitor.log_activity(user_id, "status", {"chat_id": chat_id})
        
        status = self.monitor.get_system_status()
        status_emoji = "✅"
        if status["status"] == "warning": status_emoji = "⚠️"
        elif status["status"] == "critical": status_emoji = "🔴"
        elif status["status"] == "maintenance": status_emoji = "🔧"
        
        status_text = (
            f"{status_emoji} <b>NOVAXA Bot Status</b>\n\n"
            f"Status: <b>{status['status'].upper()}</b>\n"
            f"Uptime: {status['uptime']}\n"
            f"CPU: {status['cpu_percent']}%\n"
            f"Memory: {status['memory_percent']}%\n"
            f"Disk: {status['disk_percent']}%\n"
            f"Active Users: {status['active_users']}\n"
            f"Errors: {status['error_count']}\n"
            f"Warnings: {status['warning_count']}\n"
        )
        
        if self._is_admin(user_id):
            status_text += f"Maintenance Mode: {'Enabled' if status['maintenance_mode'] else 'Disabled'}\n"
        
        self.bot.send_message(chat_id, status_text)
        self.performance_tracker.track_response_time(start_time)
    
    def handle_callback_query(self, call):
        """Handle callback queries from inline keyboards."""
        start_time = time.time()
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        
        if self._check_rate_limit(user_id):
            self.bot.answer_callback_query(call.id, "⚠️ Rate limit exceeded. Please try again later.")
            return
        
        self.monitor.log_activity(user_id, "callback_query", {
            "data": call.data,
        })
        
        if call.data == "help":
            self.bot.answer_callback_query(call.id, "Help information displayed")
            
        elif call.data == "status":
            self.bot.answer_callback_query(call.id, "Status information displayed")
            
        elif call.data.startswith("broadcast_confirm:"):
            if not self._is_admin(user_id):
                self.bot.answer_callback_query(call.id, "⛔ You don't have permission")
                return
                
            self.bot.answer_callback_query(call.id, "Broadcast sent")
            
        elif call.data == "broadcast_cancel":
            if not self._is_admin(user_id):
                self.bot.answer_callback_query(call.id, "⛔ You don't have permission")
                return
                
            self.bot.answer_callback_query(call.id, "Broadcast cancelled")
        
        else:
            self.bot.answer_callback_query(call.id, "Unknown command")
        
        self.performance_tracker.track_response_time(start_time)
    
    def handle_message(self, message):
        """Handle regular messages."""
        start_time = time.time()
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        if self._check_rate_limit(user_id):
            return
        
        user_data = self._get_user_data(user_id)
        
        self.monitor.log_activity(user_id, "message", {
            "chat_id": chat_id,
            "username": message.from_user.username,
        })
        
        if self.monitor.settings["maintenance_mode"] and not self._is_admin(user_id):
            maintenance_text = (
                f"🔧 <b>Maintenance Mode</b>\n\n"
                f"The bot is currently in maintenance mode and is not processing regular messages.\n"
                f"Please try again later."
            )
            
            self.bot.reply_to(message, maintenance_text)
            return
        
        processed = self.data_processor.process_message(message.text)
        
        self.bot.reply_to(message, "I received your message. Use /help to see available commands.")
        
        self.performance_tracker.track_response_time(start_time)


if __name__ == "__main__":
    try:
        bot = EnhancedBot()
        bot.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)
