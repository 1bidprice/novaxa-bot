"""
NOVAXA Bot Termux Dashboard (Enhanced)
------------------------------------
This script provides a simple text-based dashboard for managing
the NOVAXA bot from Termux with enhanced owner-only token management.
"""

import os
import sys
import json
import time
import getpass
import subprocess
from datetime import datetime

security_available = False
try:
    from security import TokenManager, SecurityMonitor, IPProtection
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

def print_menu(is_owner=False):
    """Print main menu."""
    print("Main Menu:")
    print("1. System Status")
    print("2. Token Management")
    print("3. Webhook Configuration")
    print("4. Security Logs")
    print("5. Start/Stop Bot")
    if is_owner:
        print("6. Owner Controls")
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

def owner_controls():
    """Owner-only controls."""
    print_header()
    print("👑 Owner Controls")
    print("-" * 50)
    
    if not security_available:
        print("Security module not available.")
        print()
        input("Press Enter to return to main menu...")
        return
    
    try:
        ip_protection = IPProtection()
        owner_id = ip_protection.owner_id
        
        if not owner_id:
            print("No owner ID set in environment.")
            print("Please set the OWNER_ID environment variable.")
            print()
            input("Press Enter to return to main menu...")
            return
        
        user_id = input("Enter your Telegram user ID: ")
        
        try:
            user_id = int(user_id)
        except ValueError:
            print("Invalid user ID. Please enter a numeric ID.")
            print()
            input("Press Enter to return to main menu...")
            return
        
        if not ip_protection.verify_owner(user_id):
            print("Access denied. You are not the owner.")
            print()
            input("Press Enter to return to main menu...")
            return
        
        while True:
            print_header()
            print("👑 Owner Controls")
            print("-" * 50)
            print("1. Emergency Token Reset")
            print("2. Export All Tokens")
            print("3. Import Tokens")
            print("4. Change Owner ID")
            print("5. Generate New Master Key")
            print("0. Back to Main Menu")
            print()
            
            choice = input("Enter your choice: ")
            
            if choice == "0":
                return
            elif choice == "1":
                emergency_token_reset()
            elif choice == "2":
                export_all_tokens()
            elif choice == "3":
                import_tokens()
            elif choice == "4":
                change_owner_id()
            elif choice == "5":
                generate_new_master_key()
            
            print()
            input("Press Enter to continue...")
    
    except Exception as e:
        print(f"Error in owner controls: {e}")
        print()
        input("Press Enter to return to main menu...")

def emergency_token_reset():
    """Emergency token reset function."""
    print_header()
    print("🚨 Emergency Token Reset")
    print("-" * 50)
    
    confirm = input("This will reset all tokens. Are you sure? (y/n): ")
    
    if confirm.lower() != "y":
        print("Operation cancelled.")
        return
    
    token = input("Enter new token: ")
    
    if not token:
        print("No token provided. Operation cancelled.")
        return
    
    try:
        master_key = os.environ.get("NOVAXA_MASTER_KEY")
        if not master_key:
            print("NOVAXA_MASTER_KEY not set in environment.")
            master_key = getpass.getpass("Enter master key: ")
        
        token_manager = TokenManager(master_key=master_key)
        
        tokens = token_manager.get_tokens()
        for token_info in tokens:
            token_manager.delete_token(token_info["id"])
        
        owner_id = os.environ.get("OWNER_ID")
        token_id = token_manager.add_token(token, "Emergency Reset", owner_id)
        token_manager.activate_token(token_id)
        
        print(f"✅ All tokens reset. New token added with ID: {token_id}")
        print("Please restart the bot to apply the new token.")
    
    except Exception as e:
        print(f"Error resetting tokens: {e}")

def export_all_tokens():
    """Export all tokens to a file."""
    print_header()
    print("📤 Export All Tokens")
    print("-" * 50)
    
    try:
        master_key = os.environ.get("NOVAXA_MASTER_KEY")
        if not master_key:
            print("NOVAXA_MASTER_KEY not set in environment.")
            master_key = getpass.getpass("Enter master key: ")
        
        token_manager = TokenManager(master_key=master_key)
        
        tokens = []
        for token_info in token_manager.get_tokens():
            token_value = token_manager.get_token(token_info["id"])
            if token_value:
                tokens.append({
                    "id": token_info["id"],
                    "token": token_value,
                    "name": token_info["name"],
                    "owner_id": token_info["owner_id"],
                    "active": token_info["active"],
                })
        
        if not tokens:
            print("No tokens to export.")
            return
        
        export_file = input("Enter export filename (default: tokens_export.json): ") or "tokens_export.json"
        
        with open(export_file, "w") as f:
            json.dump({"tokens": tokens, "exported_at": datetime.now().isoformat()}, f, indent=2)
        
        print(f"✅ Exported {len(tokens)} tokens to {export_file}")
    
    except Exception as e:
        print(f"Error exporting tokens: {e}")

def import_tokens():
    """Import tokens from a file."""
    print_header()
    print("📥 Import Tokens")
    print("-" * 50)
    
    import_file = input("Enter import filename: ")
    
    if not import_file or not os.path.exists(import_file):
        print("File not found.")
        return
    
    try:
        with open(import_file, "r") as f:
            data = json.load(f)
        
        if "tokens" not in data or not isinstance(data["tokens"], list):
            print("Invalid import file format.")
            return
        
        master_key = os.environ.get("NOVAXA_MASTER_KEY")
        if not master_key:
            print("NOVAXA_MASTER_KEY not set in environment.")
            master_key = getpass.getpass("Enter master key: ")
        
        token_manager = TokenManager(master_key=master_key)
        
        imported = 0
        for token_data in data["tokens"]:
            if "token" in token_data and "name" in token_data:
                token_id = token_manager.add_token(
                    token_data["token"],
                    token_data.get("name", "Imported"),
                    token_data.get("owner_id")
                )
                
                if token_data.get("active"):
                    token_manager.activate_token(token_id)
                
                imported += 1
        
        print(f"✅ Imported {imported} tokens")
        print("Please restart the bot to apply any changes.")
    
    except Exception as e:
        print(f"Error importing tokens: {e}")

def change_owner_id():
    """Change the owner ID."""
    print_header()
    print("👤 Change Owner ID")
    print("-" * 50)
    
    current_owner_id = os.environ.get("OWNER_ID")
    print(f"Current owner ID: {current_owner_id}")
    
    new_owner_id = input("Enter new owner ID: ")
    
    try:
        new_owner_id = int(new_owner_id)
    except ValueError:
        print("Invalid owner ID. Please enter a numeric ID.")
        return
    
    confirm = input(f"Change owner ID to {new_owner_id}? (y/n): ")
    
    if confirm.lower() != "y":
        print("Operation cancelled.")
        return
    
    try:
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                lines = f.readlines()
            
            with open(env_file, "w") as f:
                for line in lines:
                    if line.startswith("OWNER_ID="):
                        f.write(f"OWNER_ID={new_owner_id}\n")
                    else:
                        f.write(line)
        
        os.environ["OWNER_ID"] = str(new_owner_id)
        
        print(f"✅ Owner ID changed to {new_owner_id}")
        print("Please restart the bot to apply the change.")
    
    except Exception as e:
        print(f"Error changing owner ID: {e}")

def generate_new_master_key():
    """Generate a new master key."""
    print_header()
    print("🔐 Generate New Master Key")
    print("-" * 50)
    
    confirm = input("This will generate a new master key. All existing tokens will need to be re-added. Continue? (y/n): ")
    
    if confirm.lower() != "y":
        print("Operation cancelled.")
        return
    
    try:
        timestamp = int(time.time())
        new_master_key = f"novaxa_secure_master_key_{timestamp}"
        
        env_file = ".env"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                lines = f.readlines()
            
            with open(env_file, "w") as f:
                for line in lines:
                    if line.startswith("NOVAXA_MASTER_KEY="):
                        f.write(f"NOVAXA_MASTER_KEY={new_master_key}\n")
                    else:
                        f.write(line)
        
        os.environ["NOVAXA_MASTER_KEY"] = new_master_key
        
        print(f"✅ New master key generated: {new_master_key}")
        print("Please restart the bot and re-add your tokens.")
        
        export_all_tokens()
    
    except Exception as e:
        print(f"Error generating new master key: {e}")

def main():
    """Main function."""
    is_owner = False
    if security_available:
        try:
            ip_protection = IPProtection()
            owner_id = ip_protection.owner_id
            
            if owner_id:
                print(f"Enter your Telegram user ID to verify owner status (or press Enter to skip): ")
                user_id = input()
                
                if user_id:
                    try:
                        user_id = int(user_id)
                        is_owner = ip_protection.verify_owner(user_id)
                        
                        if is_owner:
                            print("✅ Owner verified!")
                        else:
                            print("You are not the owner. Some features will be restricted.")
                    except ValueError:
                        print("Invalid user ID. Some features will be restricted.")
        except Exception:
            pass
    
    while True:
        print_header()
        print_menu(is_owner)
        
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
        elif choice == "6" and is_owner:
            owner_controls()

if __name__ == "__main__":
    main()
    try:
        if not os.path.exists(".env"):
            print(f"{RED}.env file not found.{RESET}")
            input(f"{BOLD}Press Enter to continue...{RESET}")
            return
        
        print(f"{YELLOW}Current .env file contents:{RESET}")
        print()
        
        with open(".env", "r") as f:
            for line in f:
                print(line.strip())
        
        print()
        print(f"{YELLOW}Options:{RESET}")
        print(f"1. Edit OWNER_ID")
        print(f"2. Edit ADMIN_IDS")
        print(f"3. Edit WEBHOOK settings")
        print(f"4. Edit DEBUG settings")
        print(f"0. Cancel")
        print()
        
        choice = input(f"{BOLD}Enter your choice (0-4): {RESET}")
        
        if choice == "0":
            return
        elif choice == "1":
            owner_id = input(f"{BOLD}Enter your Telegram ID (OWNER_ID): {RESET}")
            
            if not owner_id:
                print(f"{RED}OWNER_ID cannot be empty.{RESET}")
                input(f"{BOLD}Press Enter to continue...{RESET}")
                return
            
            # Update .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("OWNER_ID="):
                        f.write(f"OWNER_ID={owner_id}\n")
                    else:
                        f.write(line)
            
            print(f"{GREEN}OWNER_ID updated.{RESET}")
        elif choice == "2":
            admin_ids = input(f"{BOLD}Enter admin Telegram IDs (comma-separated): {RESET}")
            
            # Update .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("ADMIN_IDS="):
                        f.write(f"ADMIN_IDS={admin_ids}\n")
                    else:
                        f.write(line)
            
            print(f"{GREEN}ADMIN_IDS updated.{RESET}")
        elif choice == "3":
            webhook_enabled = input(f"{BOLD}Enable webhook? (true/false): {RESET}")
            
            if webhook_enabled.lower() == "true":
                webhook_url = input(f"{BOLD}Enter webhook URL: {RESET}")
                port = input(f"{BOLD}Enter port (default: 8443): {RESET}")
                
                if not port:
                    port = "8443"
            else:
                webhook_url = ""
                port = "8443"
            
            # Update .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("WEBHOOK_ENABLED="):
                        f.write(f"WEBHOOK_ENABLED={webhook_enabled.lower()}\n")
                    elif line.startswith("WEBHOOK_URL="):
                        f.write(f"WEBHOOK_URL={webhook_url}\n")
                    elif line.startswith("PORT="):
                        f.write(f"PORT={port}\n")
                    else:
                        f.write(line)
            
            print(f"{GREEN}Webhook settings updated.{RESET}")
        elif choice == "4":
            debug = input(f"{BOLD}Enable debug? (true/false): {RESET}")
            log_level = input(f"{BOLD}Enter log level (DEBUG/INFO/WARNING/ERROR): {RESET}")
            
            if not log_level:
                log_level = "INFO"
            
            # Update .env file
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("DEBUG="):
                        f.write(f"DEBUG={debug.lower()}\n")
                    elif line.startswith("LOG_LEVEL="):
                        f.write(f"LOG_LEVEL={log_level.upper()}\n")
                    else:
                        f.write(line)
            
            print(f"{GREEN}Debug settings updated.{RESET}")
    except Exception as e:
        print(f"{RED}Error editing .env file: {str(e)}{RESET}")
    
    print()
    input(f"{BOLD}Press Enter to continue...{RESET}")

def configure_webhook():
    """Configure webhook."""
    print_header()
    print(f"{BOLD}{BLUE}Configure Webhook{RESET}")
    print()
    
    try:
        # Check if webhook is enabled
        webhook_enabled = False
        webhook_url = ""
        port = "8443"
        
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                for line in f:
                    if line.startswith("WEBHOOK_ENABLED="):
                        webhook_enabled = line.strip().split("=")[1].lower() == "true"
                    elif line.startswith("WEBHOOK_URL="):
                        webhook_url = line.strip().split("=")[1]
                    elif line.startswith("PORT="):
                        port = line.strip().split("=")[1]
        
        print(f"{YELLOW}Current webhook settings:{RESET}")
        print(f"Enabled: {webhook_enabled}")
        print(f"URL: {webhook_url}")
        print(f"Port: {port}")
        print()
        
        enable = input(f"{BOLD}Enable webhook? (y/n): {RESET}")
        
        if enable.lower() == "y":
            url = input(f"{BOLD}Enter webhook URL: {RESET}")
            new_port = input(f"{BOLD}Enter port (default: 8443): {RESET}")
            
            if not new_port:
                new_port = "8443"
            
            # Update .env file
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    lines = f.readlines()
                
                with open(".env", "w") as f:
                    for line in lines:
                        if line.startswith("WEBHOOK_ENABLED="):
                            f.write("WEBHOOK_ENABLED=true\n")
                        elif line.startswith("WEBHOOK_URL="):
                            f.write(f"WEBHOOK_URL={url}\n")
                        elif line.startswith("PORT="):
                            f.write(f"PORT={new_port}\n")
                        else:
                            f.write(line)
            
            print(f"{GREEN}Webhook enabled with URL: {url} and port: {new_port}{RESET}")
            print(f"{YELLOW}Please restart the bot to apply the new settings.{RESET}")
        else:
            # Update .env file
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    lines = f.readlines()
                
                with open(".env", "w") as f:
                    for line in lines:
                        if line.startswith("WEBHOOK_ENABLED="):
                            f.write("WEBHOOK_ENABLED=false\n")
                        else:
                            f.write(line)
            
            print(f"{GREEN}Webhook disabled.{RESET}")
            print(f"{YELLOW}Please restart the bot to apply the new settings.{RESET}")
    except Exception as e:
        print(f"{RED}Error configuring webhook: {str(e)}{RESET}")
    
    print()
    input(f"{BOLD}Press Enter to continue...{RESET}")

def view_bot_configuration():
    """View bot configuration."""
    print_header()
    print(f"{BOLD}{BLUE}Bot Configuration{RESET}")
    print()
    
    try:
        if not os.path.exists(".env"):
            print(f"{RED}.env file not found.{RESET}")
            input(f"{BOLD}Press Enter to continue...{RESET}")
            return
        
        print(f"{YELLOW}.env file contents:{RESET}")
        print()
        
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    
                    if key in ["TELEGRAM_BOT_TOKEN", "NOVAXA_MASTER_KEY"]:
                        value = value[:5] + "..." + value[-5:] if len(value) > 10 else "..."
                    
                    print(f"{key}: {value}")
    except Exception as e:
        print(f"{RED}Error viewing bot configuration: {str(e)}{RESET}")
    
    print()
    input(f"{BOLD}Press Enter to continue...{RESET}")

def main():
    """Main function."""
    show_main_menu()

if __name__ == "__main__":
    main()
DASHEOF
    echo -e "${GREEN}Termux dashboard created${RESET}"
fi

echo -e "\n${BOLD}${GREEN}=== Creating test script ===${RESET}"
if [ ! -f test_token_management.py ]; then
    cat > test_token_management.py << TESTEOF
"""
NOVAXA Bot Token Management Test Script
--------------------------------------
This script tests the token management system.
"""

import os
import sys
from security import TokenManager, SecurityMonitor

def main():
    """Main test function."""
    print("=" * 50)
    print("🔑 NOVAXA Bot Token Management Test")
    print("=" * 50)
    print()
    
    os.environ["NOVAXA_MASTER_KEY"] = "test_master_key"
    print("✅ Master key set for testing")
    
    token_manager = TokenManager()
    print("✅ Token manager initialized")
    
    token_id = token_manager.add_token("test_token_123456789", "Test Token", 123456789)
    print(f"✅ Test token added with ID: {token_id}")
    
    tokens = token_manager.get_tokens()
    print("\n📋 Token List:")
    for token in tokens:
        status = "ACTIVE" if token["active"] else token["status"].upper()
        print(f"  - ID: {token['id']}")
        print(f"    Name: {token['name']}")
        print(f"    Status: {status}")
        print(f"    Created: {token['created'][:10]}")
        print()
    
    if token_manager.activate_token(token_id):
        print(f"✅ Token {token_id} activated")
    else:
        print(f"❌ Failed to activate token {token_id}")
    
    active_token = token_manager.get_token()
    print(f"✅ Active token: {active_token[:5]}...{active_token[-5:]}")
    
    security_monitor = SecurityMonitor()
    security_monitor.log_event("token_test", {"token_id": token_id}, 123456789)
    print("✅ Security event logged")
    
    print("\n✅ Token management test completed successfully")

if __name__ == "__main__":
    main()
TESTEOF
    echo -e "${GREEN}Test script created${RESET}"
fi

echo -e "\n${BOLD}${GREEN}=== Making scripts executable ===${RESET}"
chmod +x setup_and_run.sh
chmod +x start_bot.sh
chmod +x start_dashboard.sh
chmod +x *.py

echo -e "\n${BOLD}${GREEN}=== Setup Complete! ===${RESET}"
echo -e "\n${BOLD}${BLUE}What would you like to do now?${RESET}"
echo -e "1. Start the bot"
echo -e "2. Start the dashboard"
echo -e "3. Exit"
read -p "Enter your choice (1-3): " CHOICE

case $CHOICE in
    1)
        echo -e "\n${GREEN}Starting the bot...${RESET}"
        ./start_bot.sh
        ;;
    2)
        echo -e "\n${GREEN}Starting the dashboard...${RESET}"
        ./start_dashboard.sh
        ;;
    3)
        echo -e "\n${GREEN}Setup completed. You can start the bot later with:${RESET}"
        echo -e "  ./start_bot.sh"
        echo -e "\n${GREEN}Or start the dashboard with:${RESET}"
        echo -e "  ./start_dashboard.sh"
        ;;
    *)
        echo -e "\n${RED}Invalid choice. Exiting.${RESET}"
        ;;
esac

echo -e "\n${BOLD}${GREEN}Enjoy your NOVAXA Bot!${RESET}"
