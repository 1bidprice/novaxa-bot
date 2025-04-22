
"""
Monitoring Module for NOVAXA Bot
------------------------------
This module provides system resource monitoring, performance tracking,
and user activity logging for the NOVAXA Telegram bot.
"""

import os
import sys
import logging
import json
import time
import threading
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from collections import deque

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class SystemMonitor:
    """Class for monitoring system resources and bot activities."""
    
    def __init__(self, log_file: str = "logs/system.log", max_logs: int = 1000):
        """Initialize the system monitor."""
        self.start_time = datetime.now()
        self.log_file = log_file
        self.max_logs = max_logs
        self.logs = deque(maxlen=max_logs)
        self.user_activity = {}
        self.error_count = 0
        self.warning_count = 0
        self.settings = {
            "maintenance_mode": False,
            "log_level": os.environ.get("LOG_LEVEL", "INFO"),
            "debug": os.environ.get("DEBUG", "false").lower() == "true",
        }
        
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("System monitor initialized")
    
    def _monitor_resources(self):
        """Monitor system resources in background thread."""
        while self.monitoring_active:
            try:
                stats = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage("/").percent,
                }
                
                self.log_info(f"System stats: CPU={stats['cpu_percent']}%, "
                             f"Memory={stats['memory_percent']}%, "
                             f"Disk={stats['disk_percent']}%")
                
                time.sleep(60)
            except Exception as e:
                logger.error(f"Error monitoring resources: {e}")
                time.sleep(60)
    
    def log_activity(self, user_id: int, activity: str, details: Dict = None):
        """Log user activity."""
        timestamp = datetime.now()
        
        activity_record = {
            "timestamp": timestamp.isoformat(),
            "activity": activity,
            "details": details or {},
        }
        
        if user_id not in self.user_activity:
            self.user_activity[user_id] = []
        
        self.user_activity[user_id].append(activity_record)
        
        self.log_info(f"User {user_id} performed {activity}", user_id=user_id)
    
    def log_info(self, message: str, user_id: int = None):
        """Log an info message."""
        self._log("INFO", message, user_id)
    
    def log_warning(self, message: str, user_id: int = None):
        """Log a warning message."""
        self.warning_count += 1
        self._log("WARNING", message, user_id)
    
    def log_error(self, message: str, user_id: int = None):
        """Log an error message."""
        self.error_count += 1
        self._log("ERROR", message, user_id)
    
    def _log(self, level: str, message: str, user_id: int = None):
        """Add log entry to logs."""
        timestamp = datetime.now()
        
        log_record = {
            "timestamp": timestamp.isoformat(),
            "level": level,
            "message": message,
            "user_id": user_id,
        }
        
        self.logs.append(log_record)
        
        if level == "INFO":
            logger.info(message)
        elif level == "WARNING":
            logger.warning(message)
        elif level == "ERROR":
            logger.error(message)
    
    def get_recent_logs(self, count: int = 10, level: str = None, user_id: int = None) -> List[Dict]:
        """Get recent logs."""
        filtered_logs = list(self.logs)
        
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        
        if user_id:
            filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
        
        filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return filtered_logs[:count]
    
    def get_system_status(self) -> Dict:
        """Get current system status."""
        uptime = datetime.now() - self.start_time
        uptime_str = str(uptime).split(".")[0]  # Remove microseconds
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage("/").percent
        
        status = "normal"
        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            status = "critical"
        elif cpu_percent > 70 or memory_percent > 70 or disk_percent > 70:
            status = "warning"
        
        if self.settings["maintenance_mode"]:
            status = "maintenance"
        
        return {
            "status": status,
            "uptime": uptime_str,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "active_users": len(self.user_activity),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "maintenance_mode": self.settings["maintenance_mode"],
        }
    
    def get_user_statistics(self) -> Dict:
        """Get user statistics."""
        user_activities = {}
        for user_id, activities in self.user_activity.items():
            user_activities[user_id] = len(activities)
        
        most_active = sorted(user_activities.items(), key=lambda x: x[1], reverse=True)[:10]
        
        daily_activities = {}
        for user_id, activities in self.user_activity.items():
            for activity in activities:
                date = activity["timestamp"].split("T")[0]
                if date not in daily_activities:
                    daily_activities[date] = 0
                daily_activities[date] += 1
        
        return {
            "total_users": len(self.user_activity),
            "most_active_users": most_active,
            "daily_activities": daily_activities,
        }
    
    def toggle_maintenance_mode(self) -> bool:
        """Toggle maintenance mode."""
        self.settings["maintenance_mode"] = not self.settings["maintenance_mode"]
        
        if self.settings["maintenance_mode"]:
            self.log_info("Maintenance mode enabled")
        else:
            self.log_info("Maintenance mode disabled")
            
        return self.settings["maintenance_mode"]
    
    def stop(self):
        """Stop the monitoring thread."""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        logger.info("System monitor stopped")


class PerformanceTracker:
    """Class for tracking performance metrics."""
    
    def __init__(self, max_metrics: int = 1000):
        """Initialize the performance tracker."""
        self.start_time = datetime.now()
        self.max_metrics = max_metrics
        self.metrics = {
            "response_time": deque(maxlen=max_metrics),
            "api_calls": deque(maxlen=max_metrics),
        }
        logger.info("Performance tracker initialized")
    
    def track_response_time(self, start_time: float):
        """Track response time for a request."""
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        self.metrics["response_time"].append({
            "timestamp": datetime.now().isoformat(),
            "value": response_time,
        })
    
    def track_api_call(self, api_name: str, success: bool, response_time: float):
        """Track API call performance."""
        self.metrics["api_calls"].append({
            "timestamp": datetime.now().isoformat(),
            "api_name": api_name,
            "success": success,
            "response_time": response_time,
        })
    
    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        response_times = [m["value"] for m in self.metrics["response_time"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        api_calls = list(self.metrics["api_calls"])
        successful_calls = sum(1 for call in api_calls if call["success"])
        api_success_rate = (successful_calls / len(api_calls) * 100) if api_calls else 100
        
        api_response_times = [call["response_time"] for call in api_calls]
        avg_api_response_time = sum(api_response_times) / len(api_response_times) if api_response_times else 0
        
        return {
            "response_time": round(avg_response_time, 2),
            "api_success_rate": round(api_success_rate, 2),
            "api_response_time": round(avg_api_response_time, 2),
            "uptime": str(datetime.now() - self.start_time).split(".")[0],
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "memory_usage": psutil.virtual_memory().percent,
        }
