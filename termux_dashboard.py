"""
NOVAXA Bot Termux Dashboard
--------------------------
This script provides a simple text-based dashboard for managing
the NOVAXA bot from Termux.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

security_available = False
try:
    from security import TokenManager, SecurityMonitor
    security_available = True
except ImportError:
    pass

monitor_available = False
try:
    from monitor import SystemMonitor
    monitor_available = True
except ImportError:
    pass

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')

def print_header():
    """Print dashboard header."""
    clear_screen()
    print("=" * 50)
    print("🤖 NOVAXA Bot Termux Dashboard 🤖")
    print("=" * 50)
    print()

def print_menu():
    """Print main menu."""
    print("Main Menu:")
    print("1. System Status")
    print("2. Token Management")
    print("3. Webhook Configuration")
    print("4. Security Logs")
    print("5. Start/Stop Bot")
    print("0. Exit")
    print()

def system_status():
    """Show system status."""
    print_header()
    print("📊 System Status")
    print("-" * 50)
    
    if monitor_available:
        monitor = SystemMonitor()
        status = monitor.get_system_status()
        
        print(f"Status: {status['status']}")
        print(f"Uptime: {status['uptime']}")
        print(f"CPU: {status['cpu_percent']}%")
        print(f"Memory: {status['memory_percent']}%")
        print(f"Disk: {status['disk_percent']}%")
        print(f"Active Users: {status['active_users']}")
        print(f"Errors: {status['error_count']}")
        print(f"Warnings: {status['warning_count']}")
        print(f"Maintenance Mode: {'Enabled' if status['maintenance_mode'] else 'Disabled'}")
    else:
        print("System monitor not available.")
    
    print()
    input("Press Enter to return to main menu...")

def token_management():
    """Token management menu."""
    while True:
        print_header()
        print("🔑 Token Management")
        print("-" * 50)
        
        if not security_available:
            print("Security module not available.")
            print()
            input("Press Enter to return to main menu...")
            return
        
        print("1. List Tokens")
        print("2. Add Token")
        print("3. Activate Token")
        print("4. Rotate Token")
        print("5. Deactivate Token")
        print("6. Delete Token")
        print("0. Back to Main Menu")
        print()
        
        choice = input("Enter your choice: ")
        
        if choice == "0":
            return
        elif choice == "1":
            subprocess.run(["python", "manage_tokens.py", "list"])
        elif choice == "2":
            token = input("Enter token: ")
            name = input("Enter name (optional): ")
            owner = input("Enter owner ID (optional): ")
            
            cmd = ["python", "manage_tokens.py", "add", token]
            if name:
                cmd.extend(["--name", name])
            if owner:
                cmd.extend(["--owner", owner])
                
            subprocess.run(cmd)
        elif choice == "3":
            token_id = input("Enter token ID: ")
            subprocess.run(["python", "manage_tokens.py", "activate", token_id])
        elif choice == "4":
            token_id = input("Enter token ID: ")
            new_token = input("Enter new token: ")
            subprocess.run(["python", "manage_tokens.py", "rotate", token_id, new_token])
        elif choice == "5":
            token_id = input("Enter token ID: ")
            subprocess.run(["python", "manage_tokens.py", "deactivate", token_id])
        elif choice == "6":
            token_id = input("Enter token ID: ")
            subprocess.run(["python", "manage_tokens.py", "delete", token_id])
        
        print()
        input("Press Enter to continue...")

def webhook_configuration():
    """Configure webhook."""
    print_header()
    print("🌐 Webhook Configuration")
    print("-" * 50)
    
    token = input("Enter token or token ID (leave empty for active token): ")
    url = input("Enter Render URL (e.g., https://novaxa-bot.onrender.com): ")
    chat_id = input("Enter chat ID for test message (optional): ")
    use_manager = input("Use token manager? (y/n): ").lower() == "y"
    
    cmd = ["python", "configure_webhook.py"]
    
    if token:
        cmd.extend(["--token", token])
    if url:
        cmd.extend(["--url", url])
    if chat_id:
        cmd.extend(["--chat-id", chat_id])
    if use_manager:
        cmd.append("--use-manager")
        
    subprocess.run(cmd)
    
    print()
    input("Press Enter to return to main menu...")

def security_logs():
    """Show security logs."""
    print_header()
    print("🔒 Security Logs")
    print("-" * 50)
    
    if not security_available:
        print("Security module not available.")
        print()
        input("Press Enter to return to main menu...")
        return
    
    try:
        with open("logs/security.log", "r") as f:
            logs = f.readlines()
            
        if not logs:
            print("No security logs found.")
        else:
            print(f"Last {min(20, len(logs))} security events:")
            print()
            
            for log in logs[-20:]:
                print(log.strip())
    except Exception as e:
        print(f"Error reading security logs: {e}")
    
    print()
    input("Press Enter to return to main menu...")

def start_stop_bot():
    """Start or stop the bot."""
    while True:
        print_header()
        print("🚀 Start/Stop Bot")
        print("-" * 50)
        
        print("1. Start Bot (Polling Mode)")
        print("2. Start Bot (Webhook Mode)")
        print("3. Stop Bot")
        print("0. Back to Main Menu")
        print()
        
        choice = input("Enter your choice: ")
        
        if choice == "0":
            return
        elif choice == "1":
            print("Starting bot in polling mode...")
            subprocess.Popen(["python", "enhanced_bot.py"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            print("Bot started in polling mode.")
        elif choice == "2":
            port = input("Enter port (default: 8443): ") or "8443"
            print(f"Starting bot in webhook mode on port {port}...")
            subprocess.Popen(["gunicorn", "-b", f"0.0.0.0:{port}", "enhanced_bot:app"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
            print(f"Bot started in webhook mode on port {port}.")
        elif choice == "3":
            print("Stopping bot...")
            subprocess.run(["pkill", "-f", "enhanced_bot.py"])
            subprocess.run(["pkill", "-f", "gunicorn"])
            print("Bot stopped.")
        
        print()
        input("Press Enter to continue...")

def main():
    """Main function."""
    while True:
        print_header()
        print_menu()
        
        choice = input("Enter your choice: ")
        
        if choice == "0":
            print("Exiting...")
            break
        elif choice == "1":
            system_status()
        elif choice == "2":
            token_management()
        elif choice == "3":
            webhook_configuration()
        elif choice == "4":
            security_logs()
        elif choice == "5":
            start_stop_bot()

if __name__ == "__main__":
    main()
