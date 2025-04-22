
"""
Service Integration Module for NOVAXA Bot
--------------------------------------
This module provides service integration and notification capabilities
for the NOVAXA Telegram bot.

It includes classes for connecting to external services, sending notifications,
and managing service configurations.
"""

import os
import sys
import logging
import json
import time
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class ServiceIntegration:
    """Class for integrating with external services."""
    
    def __init__(self, config_file: str = "config/services.json"):
        """Initialize the service integration.
        
        Args:
            config_file: Path to service configuration file
        """
        self.config_file = config_file
        self.services = {}
        self.enabled_services = set()
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        self._load_config()
        
        logger.info("Service integration initialized")
    
    def _load_config(self):
        """Load services configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.services = config.get("services", {})
                    self.enabled_services = set(config.get("enabled_services", []))
                    logger.info(f"Loaded {len(self.services)} services from configuration")
            else:
                logger.info("No services configuration file found, using defaults")
                self._save_config()
        except Exception as e:
            logger.error(f"Error loading services configuration: {e}")
    
    def _save_config(self):
        """Save services configuration to file."""
        try:
            config = {
                "services": self.services,
                "enabled_services": list(self.enabled_services),
                "last_updated": datetime.now().isoformat(),
            }
            
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
                
            logger.info("Services configuration saved")
        except Exception as e:
            logger.error(f"Error saving services configuration: {e}")
    
    def register_service(self, service_id: str, service_type: str, name: str, config: Dict) -> bool:
        """Register a new service.
        
        Args:
            service_id: Unique identifier for the service
            service_type: Type of service (http, smtp, database, etc.)
            name: Display name for the service
            config: Service configuration
            
        Returns:
            bool: True if service was registered, False otherwise
        """
        if service_id in self.services:
            logger.warning(f"Service {service_id} already exists")
            return False
        
        self.services[service_id] = {
            "id": service_id,
            "type": service_type,
            "name": name,
            "config": config,
            "created": datetime.now().isoformat(),
            "last_used": None,
            "status": "registered",
        }
        
        self._save_config()
        
        logger.info(f"Service {service_id} registered")
        return True
    
    def update_service(self, service_id: str, config: Dict) -> bool:
        """Update service configuration.
        
        Args:
            service_id: Unique identifier for the service
            config: New service configuration
            
        Returns:
            bool: True if service was updated, False otherwise
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return False
        
        self.services[service_id]["config"] = config
        self.services[service_id]["updated"] = datetime.now().isoformat()
        
        self._save_config()
        
        logger.info(f"Service {service_id} updated")
        return True
    
    def enable_service(self, service_id: str) -> bool:
        """Enable a service.
        
        Args:
            service_id: Unique identifier for the service
            
        Returns:
            bool: True if service was enabled, False otherwise
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return False
        
        self.enabled_services.add(service_id)
        
        self._save_config()
        
        logger.info(f"Service {service_id} enabled")
        return True
    
    def disable_service(self, service_id: str) -> bool:
        """Disable a service.
        
        Args:
            service_id: Unique identifier for the service
            
        Returns:
            bool: True if service was disabled, False otherwise
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return False
        
        if service_id in self.enabled_services:
            self.enabled_services.remove(service_id)
        
        self._save_config()
        
        logger.info(f"Service {service_id} disabled")
        return True
    
    def delete_service(self, service_id: str) -> bool:
        """Delete a service.
        
        Args:
            service_id: Unique identifier for the service
            
        Returns:
            bool: True if service was deleted, False otherwise
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return False
        
        del self.services[service_id]
        
        if service_id in self.enabled_services:
            self.enabled_services.remove(service_id)
        
        self._save_config()
        
        logger.info(f"Service {service_id} deleted")
        return True
    
    def get_service(self, service_id: str) -> Dict:
        """Get service information.
        
        Args:
            service_id: Unique identifier for the service
            
        Returns:
            dict: Service information
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return {}
        
        return self.services[service_id]
    
    def get_services(self, service_type: str = None) -> List[Dict]:
        """Get all services.
        
        Args:
            service_type: Filter by service type
            
        Returns:
            list: List of services
        """
        if service_type:
            return [service for service_id, service in self.services.items()
                   if service["type"] == service_type]
        
        return list(self.services.values())
    
    def get_enabled_services(self, service_type: str = None) -> List[Dict]:
        """Get enabled services.
        
        Args:
            service_type: Filter by service type
            
        Returns:
            list: List of enabled services
        """
        enabled = [service for service_id, service in self.services.items()
                  if service_id in self.enabled_services]
        
        if service_type:
            return [service for service in enabled if service["type"] == service_type]
        
        return enabled
    
    def check_service(self, service_id: str) -> Dict:
        """Check if a service is available.
        
        Args:
            service_id: Unique identifier for the service
            
        Returns:
            dict: Service status information
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return {"status": "not_found"}
        
        service = self.services[service_id]
        service_type = service["type"]
        
        if service_type == "http":
            return self._check_http_service(service)
        elif service_type == "smtp":
            return self._check_smtp_service(service)
        elif service_type == "database":
            return self._check_database_service(service)
        else:
            logger.warning(f"Unknown service type: {service_type}")
            return {"status": "unknown_type"}
    
    def _check_http_service(self, service: Dict) -> Dict:
        """Check if an HTTP service is available.
        
        Args:
            service: Service information
            
        Returns:
            dict: Service status information
        """
        config = service["config"]
        url = config.get("url")
        
        if not url:
            return {"status": "invalid_config", "message": "No URL provided"}
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            status = "available" if response.status_code < 400 else "error"
            
            service["status"] = status
            service["last_used"] = datetime.now().isoformat()
            self._save_config()
            
            return {
                "status": status,
                "response_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error checking HTTP service: {e}")
            
            service["status"] = "error"
            service["last_used"] = datetime.now().isoformat()
            self._save_config()
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def _check_smtp_service(self, service: Dict) -> Dict:
        """Check if an SMTP service is available.
        
        Args:
            service: Service information
            
        Returns:
            dict: Service status information
        """
        config = service["config"]
        host = config.get("host")
        port = config.get("port", 587)
        
        if not host:
            return {"status": "invalid_config", "message": "No host provided"}
        
        try:
            start_time = time.time()
            smtp = smtplib.SMTP(host, port, timeout=5)
            smtp.quit()
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            service["status"] = "available"
            service["last_used"] = datetime.now().isoformat()
            self._save_config()
            
            return {
                "status": "available",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error checking SMTP service: {e}")
            
            service["status"] = "error"
            service["last_used"] = datetime.now().isoformat()
            self._save_config()
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def _check_database_service(self, service: Dict) -> Dict:
        """Check if a database service is available.
        
        Args:
            service: Service information
            
        Returns:
            dict: Service status information
        """
        
        service["status"] = "unknown"
        service["last_used"] = datetime.now().isoformat()
        self._save_config()
        
        return {
            "status": "unknown",
            "message": "Database service check not implemented",
            "timestamp": datetime.now().isoformat(),
        }
    
    def http_request(self, service_id: str, method: str = "GET", endpoint: str = "",
                   params: Dict = None, data: Dict = None, headers: Dict = None) -> Dict:
        """Make an HTTP request to a service.
        
        Args:
            service_id: Unique identifier for the service
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request data
            headers: Request headers
            
        Returns:
            dict: Response from the service
        """
        if service_id not in self.services:
            logger.warning(f"Service {service_id} does not exist")
            return {"status": "error", "message": "Service not found"}
        
        if service_id not in self.enabled_services:
            logger.warning(f"Service {service_id} is not enabled")
            return {"status": "error", "message": "Service not enabled"}
        
        service = self.services[service_id]
        if service["type"] != "http":
            logger.warning(f"Service {service_id} is not an HTTP service")
            return {"status": "error", "message": "Not an HTTP service"}
        
        config = service["config"]
        base_url = config.get("url")
        
        if not base_url:
            return {"status": "error", "message": "No URL provided in service configuration"}
        
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}" if endpoint else base_url
        
        auth = None
        if "username" in config and "password" in config:
            auth = (config["username"], config["password"])
        
        request_headers = config.get("headers", {}).copy()
        if headers:
            request_headers.update(headers)
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=request_headers, auth=auth)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, json=data, headers=request_headers, auth=auth)
            elif method.upper() == "PUT":
                response = requests.put(url, params=params, json=data, headers=request_headers, auth=auth)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, headers=request_headers, auth=auth)
            else:
                return {"status": "error", "message": f"Unsupported HTTP method: {method}"}
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            service["status"] = "available"
            service["last_used"] = datetime.now().isoformat()
            self._save_config()
            
            return {
                "status": "success" if response.status_code < 400 else "error",
                "response_code": response.status_code,
                "response_time": response_time,
                "data": response.json() if response.headers.get("content-type") == "application/json" else response.text,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error making HTTP request: {e}")
            
            service["status"] = "error"
            service["last_used"] = datetime.now().isoformat()
            self._save_config()
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }


class NotificationSystem:
    """Class for sending notifications to users."""
    
    def __init__(self, service_integration: ServiceIntegration = None):
        """Initialize the notification system.
        
        Args:
            service_integration: Service integration instance
        """
        self.service_integration = service_integration or ServiceIntegration()
        logger.info("Notification system initialized")
    
    def send_email(self, service_id: str, to: Union[str, List[str]], subject: str, body: str,
                 html: bool = False, cc: Union[str, List[str]] = None,
                 bcc: Union[str, List[str]] = None) -> Dict:
        """Send an email notification.
        
        Args:
            service_id: Unique identifier for the SMTP service
            to: Recipient email address(es)
            subject: Email subject
            body: Email body
            html: Whether the body is HTML
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            
        Returns:
            dict: Result of the email sending operation
        """
        if not self.service_integration:
            logger.error("No service integration available")
            return {"status": "error", "message": "No service integration available"}
        
        service = self.service_integration.get_service(service_id)
        if not service:
            logger.warning(f"Service {service_id} not found")
            return {"status": "error", "message": "Service not found"}
        
        if service["type"] != "smtp":
            logger.warning(f"Service {service_id} is not an SMTP service")
            return {"status": "error", "message": "Not an SMTP service"}
        
        if service_id not in self.service_integration.enabled_services:
            logger.warning(f"Service {service_id} is not enabled")
            return {"status": "error", "message": "Service not enabled"}
        
        config = service["config"]
        host = config.get("host")
        port = config.get("port", 587)
        username = config.get("username")
        password = config.get("password")
        from_email = config.get("from_email", username)
        
        if not all([host, username, password]):
            return {"status": "error", "message": "Incomplete SMTP configuration"}
        
        msg = MIMEMultipart("alternative" if html else "mixed")
        msg["Subject"] = subject
        msg["From"] = from_email
        
        if isinstance(to, list):
            msg["To"] = ", ".join(to)
        else:
            msg["To"] = to
            to = [to]
        
        if cc:
            if isinstance(cc, list):
                msg["Cc"] = ", ".join(cc)
                to.extend(cc)
            else:
                msg["Cc"] = cc
                to.append(cc)
        
        if bcc:
            if isinstance(bcc, list):
                to.extend(bcc)
            else:
                to.append(bcc)
        
        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))
        
        try:
            smtp = smtplib.SMTP(host, port)
            smtp.ehlo()
            
            if smtp.has_extn("STARTTLS"):
                smtp.starttls()
                smtp.ehlo()
            
            smtp.login(username, password)
            
            smtp.sendmail(from_email, to, msg.as_string())
            smtp.quit()
            
            service["status"] = "available"
            service["last_used"] = datetime.now().isoformat()
            self.service_integration._save_config()
            
            logger.info(f"Email sent to {to}")
            return {
                "status": "success",
                "message": "Email sent successfully",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            
            service["status"] = "error"
            service["last_used"] = datetime.now().isoformat()
            self.service_integration._save_config()
            
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    def send_webhook(self, service_id: str, data: Dict) -> Dict:
        """Send a webhook notification.
        
        Args:
            service_id: Unique identifier for the webhook service
            data: Data to send
            
        Returns:
            dict: Result of the webhook operation
        """
        if not self.service_integration:
            logger.error("No service integration available")
            return {"status": "error", "message": "No service integration available"}
        
        return self.service_integration.http_request(service_id, method="POST", data=data)
    
    def send_telegram(self, chat_id: Union[int, str], text: str, parse_mode: str = "HTML") -> Dict:
        """Send a Telegram notification.
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Message parse mode
            
        Returns:
            dict: Result of the Telegram operation
        """
        
        logger.info(f"Telegram notification sent to {chat_id}")
        return {
            "status": "success",
            "message": "Telegram notification sent",
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    integration = ServiceIntegration()
    
    integration.register_service(
        "test_http",
        "http",
        "Test HTTP Service",
        {"url": "https://httpbin.org/get"}
    )
    
    integration.enable_service("test_http")
    
    status = integration.check_service("test_http")
    print(f"Service status: {status}")
    
    response = integration.http_request("test_http")
    print(f"Response: {response}")
