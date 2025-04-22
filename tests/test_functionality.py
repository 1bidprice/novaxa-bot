
"""
Test Suite for NOVAXA Telegram Bot
---------------------------------
This module contains unit tests for the NOVAXA Telegram bot.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
import time
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api import TelegramAPI, DataProcessor
    from monitor import SystemMonitor, PerformanceTracker
    from integration import ServiceIntegration, NotificationSystem
    from enhanced_bot import EnhancedBot
except ImportError as e:
    print(f"Error importing bot modules: {e}")
    print("Make sure the bot modules are in the parent directory.")
    sys.exit(1)


class TestTelegramAPI(unittest.TestCase):
    """Test cases for the TelegramAPI class."""
    
    def setUp(self):
        """Set up test environment."""
        self.token = "test_token"
        self.api = TelegramAPI(self.token)
    
    @patch('api.requests.post')
    def test_send_message(self, mock_post):
        """Test sending a message."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 123}}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.send_message(chat_id=123456789, text="Test message")
        
        self.assertTrue(result["ok"])
        self.assertEqual(result["result"]["message_id"], 123)
        mock_post.assert_called_once()
    
    @patch('api.requests.post')
    def test_send_message_error(self, mock_post):
        """Test sending a message with error."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": False, "description": "Error"}
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = self.api.send_message(chat_id=123456789, text="Test message")
        
        self.assertFalse(result["ok"])
        self.assertEqual(result["description"], "Error")
        mock_post.assert_called_once()
    
    @patch('api.requests.post')
    def test_set_webhook(self, mock_post):
        """Test setting a webhook."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.set_webhook(url="https://example.com/webhook")
        
        self.assertTrue(result["ok"])
        self.assertTrue(result["result"])
        mock_post.assert_called_once()
    
    @patch('api.requests.post')
    def test_remove_webhook(self, mock_post):
        """Test removing a webhook."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.api.remove_webhook()
        
        self.assertTrue(result["ok"])
        self.assertTrue(result["result"])
        mock_post.assert_called_once()


class TestDataProcessor(unittest.TestCase):
    """Test cases for the DataProcessor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = DataProcessor()
    
    def test_process_message(self):
        """Test processing a message."""
        result = self.processor.process_message("Hello, world!")
        
        self.assertIsInstance(result, dict)
        self.assertIn("text", result)
        self.assertEqual(result["text"], "Hello, world!")
    
    def test_analyze_sentiment(self):
        """Test analyzing sentiment."""
        result = self.processor.analyze_sentiment("I love this bot!")
        
        self.assertIsInstance(result, dict)
        self.assertIn("sentiment", result)
        self.assertIn("score", result)
    
    def test_extract_keywords(self):
        """Test extracting keywords."""
        result = self.processor.extract_keywords("This is a test message about Telegram bots.")
        
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)


class TestSystemMonitor(unittest.TestCase):
    """Test cases for the SystemMonitor class."""
    
    def setUp(self):
        """Set up test environment."""
        self.monitor = SystemMonitor(log_file="tests/test_system.log")
    
    def tearDown(self):
        """Clean up after tests."""
        self.monitor.stop()
        if os.path.exists("tests/test_system.log"):
            os.remove("tests/test_system.log")
    
    def test_log_activity(self):
        """Test logging user activity."""
        self.monitor.log_activity(user_id=123456789, activity="test", details={"test": "value"})
        
        self.assertIn(123456789, self.monitor.user_activity)
        self.assertEqual(len(self.monitor.user_activity[123456789]), 1)
        self.assertEqual(self.monitor.user_activity[123456789][0]["activity"], "test")
        self.assertEqual(self.monitor.user_activity[123456789][0]["details"]["test"], "value")
    
    def test_log_info(self):
        """Test logging info message."""
        self.monitor.log_info("Test info message")
        
        self.assertEqual(len(self.monitor.logs), 1)
        self.assertEqual(self.monitor.logs[0]["level"], "INFO")
        self.assertEqual(self.monitor.logs[0]["message"], "Test info message")
    
    def test_log_warning(self):
        """Test logging warning message."""
        self.monitor.log_warning("Test warning message")
        
        self.assertEqual(len(self.monitor.logs), 1)
        self.assertEqual(self.monitor.logs[0]["level"], "WARNING")
        self.assertEqual(self.monitor.logs[0]["message"], "Test warning message")
        self.assertEqual(self.monitor.warning_count, 1)
    
    def test_log_error(self):
        """Test logging error message."""
        self.monitor.log_error("Test error message")
        
        self.assertEqual(len(self.monitor.logs), 1)
        self.assertEqual(self.monitor.logs[0]["level"], "ERROR")
        self.assertEqual(self.monitor.logs[0]["message"], "Test error message")
        self.assertEqual(self.monitor.error_count, 1)
    
    def test_get_recent_logs(self):
        """Test getting recent logs."""
        self.monitor.log_info("Test info message")
        self.monitor.log_warning("Test warning message")
        self.monitor.log_error("Test error message")
        
        logs = self.monitor.get_recent_logs(count=2)
        
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0]["level"], "ERROR")
        self.assertEqual(logs[1]["level"], "WARNING")
    
    def test_get_system_status(self):
        """Test getting system status."""
        status = self.monitor.get_system_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("status", status)
        self.assertIn("uptime", status)
        self.assertIn("cpu_percent", status)
        self.assertIn("memory_percent", status)
        self.assertIn("disk_percent", status)
        self.assertIn("active_users", status)
        self.assertIn("error_count", status)
        self.assertIn("warning_count", status)
        self.assertIn("maintenance_mode", status)
    
    def test_toggle_maintenance_mode(self):
        """Test toggling maintenance mode."""
        initial_mode = self.monitor.settings["maintenance_mode"]
        
        new_mode = self.monitor.toggle_maintenance_mode()
        
        self.assertNotEqual(initial_mode, new_mode)
        self.assertEqual(new_mode, self.monitor.settings["maintenance_mode"])


class TestPerformanceTracker(unittest.TestCase):
    """Test cases for the PerformanceTracker class."""
    
    def setUp(self):
        """Set up test environment."""
        self.tracker = PerformanceTracker()
    
    def test_track_response_time(self):
        """Test tracking response time."""
        start_time = time.time() - 0.5  # 500ms ago
        self.tracker.track_response_time(start_time)
        
        self.assertEqual(len(self.tracker.metrics["response_time"]), 1)
        self.assertGreaterEqual(self.tracker.metrics["response_time"][0]["value"], 500)  # At least 500ms
    
    def test_track_api_call(self):
        """Test tracking API call."""
        self.tracker.track_api_call(api_name="test_api", success=True, response_time=200)
        
        self.assertEqual(len(self.tracker.metrics["api_calls"]), 1)
        self.assertEqual(self.tracker.metrics["api_calls"][0]["api_name"], "test_api")
        self.assertTrue(self.tracker.metrics["api_calls"][0]["success"])
        self.assertEqual(self.tracker.metrics["api_calls"][0]["response_time"], 200)
    
    def test_get_metrics(self):
        """Test getting metrics."""
        start_time = time.time() - 0.5  # 500ms ago
        self.tracker.track_response_time(start_time)
        self.tracker.track_api_call(api_name="test_api", success=True, response_time=200)
        
        metrics = self.tracker.get_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("response_time", metrics)
        self.assertIn("api_success_rate", metrics)
        self.assertIn("api_response_time", metrics)
        self.assertIn("uptime", metrics)
        self.assertIn("cpu_usage", metrics)
        self.assertIn("memory_usage", metrics)


class TestServiceIntegration(unittest.TestCase):
    """Test cases for the ServiceIntegration class."""
    
    def setUp(self):
        """Set up test environment."""
        self.integration = ServiceIntegration()
    
    def test_register_service(self):
        """Test registering a service."""
        result = self.integration.register_service(
            name="test_service",
            service_type="http",
            config={"url": "https://example.com/api"}
        )
        
        self.assertTrue(result)
        self.assertIn("test_service", self.integration.services)
        self.assertEqual(self.integration.services["test_service"]["type"], "http")
        self.assertEqual(self.integration.services["test_service"]["config"]["url"], "https://example.com/api")
    
    def test_enable_service(self):
        """Test enabling a service."""
        self.integration.register_service(
            name="test_service",
            service_type="http",
            config={"url": "https://example.com/api"}
        )
        
        result = self.integration.enable_service("test_service")
        
        self.assertTrue(result)
        self.assertTrue(self.integration.services["test_service"]["enabled"])
    
    def test_disable_service(self):
        """Test disabling a service."""
        self.integration.register_service(
            name="test_service",
            service_type="http",
            config={"url": "https://example.com/api"}
        )
        self.integration.enable_service("test_service")
        
        result = self.integration.disable_service("test_service")
        
        self.assertTrue(result)
        self.assertFalse(self.integration.services["test_service"]["enabled"])
    
    def test_check_service(self):
        """Test checking a service."""
        self.integration.register_service(
            name="test_service",
            service_type="http",
            config={"url": "https://example.com/api"}
        )
        
        with patch('integration.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = self.integration.check_service("test_service")
            
            self.assertTrue(result)
            mock_get.assert_called_once()


class TestNotificationSystem(unittest.TestCase):
    """Test cases for the NotificationSystem class."""
    
    def setUp(self):
        """Set up test environment."""
        self.integration = ServiceIntegration()
        self.notification = NotificationSystem(self.integration)
    
    @patch('integration.smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        """Test sending an email."""
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        result = self.notification.send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        self.assertTrue(result)
        mock_smtp_instance.sendmail.assert_called_once()
    
    @patch('integration.requests.post')
    def test_send_webhook(self, mock_post):
        """Test sending a webhook."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.notification.send_webhook(
            url="https://example.com/webhook",
            data={"message": "Test Message"}
        )
        
        self.assertTrue(result)
        mock_post.assert_called_once()


class TestEnhancedBot(unittest.TestCase):
    """Test cases for the EnhancedBot class."""
    
    def setUp(self):
        """Set up test environment."""
        self.env_patcher = patch.dict('os.environ', {
            'TELEGRAM_BOT_TOKEN': 'test_token',
            'DEBUG': 'true',
            'LOG_LEVEL': 'INFO',
            'WEBHOOK_ENABLED': 'false',
            'ADMIN_IDS': '123456789'
        })
        self.env_patcher.start()
        
        self.telebot_patcher = patch('enhanced_bot.telebot.TeleBot')
        self.mock_telebot = self.telebot_patcher.start()
        
        self.bot = EnhancedBot()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
        self.telebot_patcher.stop()
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.bot.token, "test_token")
        self.assertTrue(self.bot.debug)
        self.assertFalse(self.bot.webhook_enabled)
        self.assertEqual(self.bot.admin_ids, [123456789])
        self.mock_telebot.assert_called_once()
    
    def test_is_admin(self):
        """Test admin check."""
        self.assertTrue(self.bot._is_admin(123456789))
        self.assertFalse(self.bot._is_admin(987654321))
    
    def test_get_user_data(self):
        """Test getting user data."""
        user_data = self.bot._get_user_data(123456789)
        
        self.assertIsInstance(user_data, dict)
        self.assertEqual(user_data["id"], 123456789)
        self.assertIn("first_seen", user_data)
        self.assertIn("last_seen", user_data)
        self.assertEqual(user_data["command_count"], 0)
        self.assertIn("settings", user_data)
    
    def test_update_user_command_count(self):
        """Test updating user command count."""
        user_data = self.bot._get_user_data(123456789)
        initial_count = user_data["command_count"]
        
        self.bot._update_user_command_count(123456789)
        
        self.assertEqual(user_data["command_count"], initial_count + 1)
    
    def test_check_rate_limit(self):
        """Test rate limit check."""
        initial_result = self.bot._check_rate_limit(123456789)
        
        self.assertFalse(initial_result)
        
        for _ in range(self.bot.rate_limit_max):
            self.bot._check_rate_limit(123456789)
        
        exceeded_result = self.bot._check_rate_limit(123456789)
        
        self.assertTrue(exceeded_result)


def run_tests():
    """Run all tests."""
    test_suite = unittest.TestSuite()
    
    test_suite.addTest(unittest.makeSuite(TestTelegramAPI))
    test_suite.addTest(unittest.makeSuite(TestDataProcessor))
    test_suite.addTest(unittest.makeSuite(TestSystemMonitor))
    test_suite.addTest(unittest.makeSuite(TestPerformanceTracker))
    test_suite.addTest(unittest.makeSuite(TestServiceIntegration))
    test_suite.addTest(unittest.makeSuite(TestNotificationSystem))
    test_suite.addTest(unittest.makeSuite(TestEnhancedBot))
    
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_result = test_runner.run(test_suite)
    
    return test_result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    
    sys.exit(0 if success else 1)
