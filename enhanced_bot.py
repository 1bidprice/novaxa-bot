import os import sys import logging import json import time import signal from datetime import datetime from typing import Dict from collections import defaultdict import telebot from telebot import types from dotenv import load_dotenv from flask import Flask, request, jsonify

app = Flask(name) load_dotenv()

try: from api import TelegramAPI, DataProcessor from monitor import SystemMonitor, PerformanceTracker from integration import ServiceIntegration, NotificationSystem except ImportError as e: print(f"Error importing custom modules: {e}") sys.exit(1)

logging.basicConfig( format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO, ) logger = logging.getLogger("NOVAXA")

log_level = os.environ.get("LOG_LEVEL", "INFO").upper() logger.setLevel(getattr(logging, log_level))

os.makedirs("logs", exist_ok=True) file_handler = logging.FileHandler("logs/bot.log") file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")) logger.addHandler(file_handler)

class EnhancedBot: def init(self): self.token = os.environ.get("TELEGRAM_BOT_TOKEN") if not self.token: logger.error("No Telegram token provided") raise ValueError("Telegram token is required")

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
    self.rate_limit_interval = 60
    self.rate_limit_max = 30

    self._register_handlers()
    logger.info("Bot initialized")

def _register_handlers(self):
    self.bot.message_handler(commands=["start"])(self.handle_start)
    self.bot.message_handler(commands=["help"])(self.handle_help)
    self.bot.message_handler(commands=["status"])(self.handle_status)
    self.bot.message_handler(commands=["getid"])(self.handle_getid)
    self.bot.callback_query_handler(func=lambda call: True)(self.handle_callback_query)
    self.bot.message_handler(func=lambda message: True)(self.handle_message)
    logger.info("Handlers registered")

def start(self):
    logger.info("Starting bot...")
    signal.signal(signal.SIGINT, self._signal_handler)
    signal.signal(signal.SIGTERM, self._signal_handler)

    if self.webhook_enabled and self.webhook_url:
        self._start_webhook()
    else:
        self._start_polling()

def _start_webhook(self):
    logger.info(f"Starting webhook mode at {self.webhook_url}")
    self.bot.remove_webhook()
    time.sleep(0.5)
    self.bot.set_webhook(url=self.webhook_url)

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({"status": "ok", "message": "NOVAXA Bot is running"})

    @app.route("/webhook", methods=["POST"])
    def webhook():
        if request.headers.get("content-type") == "application/json":
            update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
            self.bot.process_new_updates([update])
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "Invalid content type"})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify(self.monitor.get_system_status())

    @app.route("/setwebhook", methods=["GET"])
    def set_webhook():
        success = self.bot.set_webhook(url=self.webhook_url)
        return jsonify({"status": "ok" if success else "fail"})

    @app.route("/unsetwebhook", methods=["GET"])
    def unset_webhook():
        success = self.bot.remove_webhook()
        return jsonify({"status": "ok" if success else "fail"})

    app.run(host="0.0.0.0", port=self.port)

def _start_polling(self):
    logger.info("Polling mode")
    self.bot.remove_webhook()
    self.bot.infinity_polling()

def _signal_handler(self, sig, frame):
    logger.info(f"Received signal {sig}, shutting down...")
    self.monitor.stop()
    self.bot.stop_polling()
    sys.exit(0)

def _check_rate_limit(self, user_id: int) -> bool:
    now = time.time()
    user = self.rate_limits[user_id]
    if now - user["last_reset"] > self.rate_limit_interval:
        user["count"] = 0
        user["last_reset"] = now
    user["count"] += 1
    return user["count"] > self.rate_limit_max

def _is_admin(self, user_id: int) -> bool:
    return user_id in self.admin_ids

def _get_user_data(self, user_id: int) -> Dict:
    if user_id not in self.user_data:
        self.user_data[user_id] = {
            "id": user_id,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "command_count": 0,
            "settings": {"language": "en", "notifications": True},
        }
    else:
        self.user_data[user_id]["last_seen"] = datetime.now().isoformat()
    return self.user_data[user_id]

def _update_user_command_count(self, user_id: int):
    self.user_data[user_id]["command_count"] += 1

def handle_start(self, message):
    if self._check_rate_limit(message.from_user.id):
        self.bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    user = self._get_user_data(message.from_user.id)
    self._update_user_command_count(user["id"])
    self.monitor.log_activity(user["id"], "start", {"chat_id": message.chat.id})
    welcome = "👋 Welcome to <b>NOVAXA</b>! Use /help to begin."
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📚 Help", callback_data="help"))
    self.bot.send_message(message.chat.id, welcome, reply_markup=markup)
    self.performance_tracker.track_response_time(time.time())

def handle_help(self, message):
    if self._check_rate_limit(message.from_user.id):
        self.bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    help_text = """🤖 <b>NOVAXA Commands</b>

/start - Start the bot /help - Help /status - System status /getid - Show your ID""" self.bot.send_message(message.chat.id, help_text)

def handle_status(self, message):
    if self._check_rate_limit(message.from_user.id):
        self.bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    status = self.monitor.get_system_status()
    self.bot.send_message(message.chat.id, json.dumps(status, indent=2))

def handle_getid(self, message):
    if self._check_rate_limit(message.from_user.id):
        self.bot.reply_to(message, "⚠️ Rate limit exceeded.")
        return
    self.bot.send_message(
        message.chat.id,
        f"User ID: <code>{message.from_user.id}</code>\nChat ID: <code>{message.chat.id}</code>",
        parse_mode="HTML",
    )

def handle_callback_query(self, call):
    self.bot.answer_callback_query(call.id, "Callback received")

def handle_message(self, message):
    if self._check_rate_limit(message.from_user.id):
        return
    self.bot.reply_to(message, "Message received. Use /help for commands.")

if name == "main": try: bot = EnhancedBot() bot.start() except Exception as e: logger.error(f"Bot failed: {e}") sys.exit(1)

