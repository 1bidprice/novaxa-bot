"""
NOVAXA Bot Token Management Script
---------------------------------
This script allows managing Telegram bot tokens for the NOVAXA bot.
It provides a command-line interface for managing tokens from Termux.
"""

import os
import sys
import json
import argparse
from datetime import datetime
import getpass

from security import TokenManager

def setup_parser():
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(description="NOVAXA Bot Token Management")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    list_parser = subparsers.add_parser("list", help="List all tokens")
    
    add_parser = subparsers.add_parser("add", help="Add a new token")
    add_parser.add_argument("token", help="Telegram bot token")
    add_parser.add_argument("--name", "-n", help="Name for the token", default="Default")
    add_parser.add_argument("--owner", "-o", help="Owner ID", type=int, default=None)
    
    activate_parser = subparsers.add_parser("activate", help="Activate a token")
    activate_parser.add_argument("token_id", help="Token ID to activate")
    
    deactivate_parser = subparsers.add_parser("deactivate", help="Deactivate a token")
    deactivate_parser.add_argument("token_id", help="Token ID to deactivate")
    
    delete_parser = subparsers.add_parser("delete", help="Delete a token")
    delete_parser.add_argument("token_id", help="Token ID to delete")
    
    rotate_parser = subparsers.add_parser("rotate", help="Rotate to a new token")
    rotate_parser.add_argument("token_id", help="Token ID to rotate")
    rotate_parser.add_argument("new_token", help="New token value")
    
    active_parser = subparsers.add_parser("active", help="Show active token")
    
    return parser

def get_master_key():
    """Get master key from environment or prompt."""
    master_key = os.environ.get("NOVAXA_MASTER_KEY")
    
    if not master_key:
        print("NOVAXA_MASTER_KEY not set in environment.")
        master_key = getpass.getpass("Enter master key: ")
        
    return master_key

def format_output(title, data, is_error=False):
    """Format output with colors for Termux."""
    RESET = "\033[0m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    BOLD = "\033[1m"
    
    color = RED if is_error else GREEN
    
    print(f"\n{BOLD}{color}=== {title} ==={RESET}\n")
    
    if isinstance(data, str):
        print(data)
    elif isinstance(data, list):
        for item in data:
            print(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            print(f"{YELLOW}{key}{RESET}: {value}")
    
    print()

def main():
    """Main function."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        master_key = get_master_key()
        token_manager = TokenManager(master_key=master_key)
        
        if args.command == "list":
            tokens = token_manager.get_tokens()
            
            if not tokens:
                format_output("Tokens", "No tokens found.")
                return
            
            header = f"{'ID':<10} {'Name':<20} {'Status':<10} {'Created':<12}"
            separator = "-" * 55
            rows = [header, separator]
            
            for token in tokens:
                status = "ACTIVE" if token["active"] else token["status"].upper()
                created = token["created"][:10]
                rows.append(f"{token['id']:<10} {token['name']:<20} {status:<10} {created:<12}")
            
            format_output("Tokens", rows)
        
        elif args.command == "add":
            token_id = token_manager.add_token(args.token, args.name, args.owner)
            format_output("Token Added", f"Token added with ID: {token_id}")
            print(f"Use './manage_tokens.py activate {token_id}' to activate this token.")
        
        elif args.command == "activate":
            if token_manager.activate_token(args.token_id):
                format_output("Token Activated", f"Token {args.token_id} activated.")
                print("Please restart the bot to apply the new token.")
            else:
                format_output("Error", f"Failed to activate token {args.token_id}.", True)
        
        elif args.command == "deactivate":
            if token_manager.deactivate_token(args.token_id):
                format_output("Token Deactivated", f"Token {args.token_id} deactivated.")
            else: 
                format_output("Error", f"Failed to deactivate token {args.token_id}.", True)
        
        elif args.command == "delete":
            confirm = input(f"Are you sure you want to delete token {args.token_id}? (y/n): ")
            if confirm.lower() == "y":
                if token_manager.delete_token(args.token_id):
                    format_output("Token Deleted", f"Token {args.token_id} deleted.")
                else:
                    format_output("Error", f"Failed to delete token {args.token_id}.", True)
            else:
                format_output("Cancelled", "Deletion cancelled.")
        
        elif args.command == "rotate":
            if token_manager.rotate_token(args.token_id, args.new_token):
                format_output("Token Rotated", f"Token {args.token_id} rotated to new value.")
                print("Please restart the bot to apply the new token.")
            else:
                format_output("Error", f"Failed to rotate token {args.token_id}.", True)
        
        elif args.command == "active":
            token_id = token_manager.active_token_id
            
            if not token_id:
                format_output("Active Token", "No active token.")
                return
            
            tokens = token_manager.get_tokens()
            active_token = next((t for t in tokens if t["id"] == token_id), None)
            
            if active_token:
                format_output("Active Token", {
                    "ID": active_token["id"],
                    "Name": active_token["name"],
                    "Created": active_token["created"][:10],
                    "Status": "ACTIVE"
                })
            else:
                format_output("Error", "No active token information available.", True)
    
    except Exception as e:
        format_output("Error", f"An error occurred: {str(e)}", True)
        sys.exit(1)

if __name__ == "__main__":
    main()
