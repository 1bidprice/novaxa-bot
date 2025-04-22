
"""
Telegram Bot Monitoring Dashboard
--------------------------------
A simple Flask-based dashboard for monitoring the Telegram bot.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
import psutil
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from monitor import SystemMonitor, PerformanceTracker
except ImportError as e:
    print(f"Error importing bot modules: {e}")
    print("Make sure the bot modules are in the parent directory.")
    sys.exit(1)

load_dotenv()

app = Flask(__name__)

system_monitor = SystemMonitor()
performance_tracker = PerformanceTracker()

@app.route('/')
def index():
    """Render the dashboard index page."""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Get system status."""
    return jsonify(system_monitor.get_system_status())

@app.route('/api/performance')
def performance():
    """Get performance metrics."""
    return jsonify(performance_tracker.get_metrics())

@app.route('/api/users')
def users():
    """Get user statistics."""
    return jsonify(system_monitor.get_user_statistics())

@app.route('/api/logs')
def logs():
    """Get recent logs."""
    count = request.args.get('count', default=20, type=int)
    level = request.args.get('level', default=None, type=str)
    user_id = request.args.get('user_id', default=None, type=int)
    
    return jsonify(system_monitor.get_recent_logs(count=count, level=level, user_id=user_id))

@app.route('/api/toggle_maintenance', methods=['POST'])
def toggle_maintenance():
    """Toggle maintenance mode."""
    maintenance_mode = system_monitor.toggle_maintenance_mode()
    return jsonify({"maintenance_mode": maintenance_mode})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
