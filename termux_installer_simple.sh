#!/bin/bash

# NOVAXA Bot Termux Installer (Simplified)
# This script installs and runs NOVAXA Bot with token management capabilities
# Designed for Termux on Android

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot Εγκατάσταση για Termux ===${RESET}\n"

# Create working directory
INSTALL_DIR="$HOME/novaxa_bot"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση βασικών πακέτων ===${RESET}"
pkg update -y
pkg install -y python git curl

# Create directory structure
mkdir -p logs
mkdir -p config
touch logs/bot.log

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση Python πακέτων ===${RESET}"
pip install pyTelegramBotAPI==4.10.0 python-dotenv==0.21.0

# Download files from GitHub
echo -e "\n${BOLD}${GREEN}=== Κατέβασμα αρχείων από GitHub ===${RESET}"
curl -s -o security.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/security_simple.py
curl -s -o manage_tokens.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/manage_tokens.py
curl -s -o novaxa_bot.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/novaxa_bot.py

echo -e "\n${BOLD}${GREEN}=== Ρύθμιση περιβάλλοντος ===${RESET}"

TIMESTAMP=$(date +%s)
MASTER_KEY="novaxa_secure_master_key_$TIMESTAMP"
echo -e "${GREEN}Δημιουργήθηκε νέο master key${RESET}"

echo -e "\n${YELLOW}Παρακαλώ εισάγετε το Telegram user ID σας (θα οριστεί ως ιδιοκτήτης):${RESET}"
read OWNER_ID
echo -e "${GREEN}Owner ID ορίστηκε σε: $OWNER_ID${RESET}"

echo -e "\n${BOLD}${GREEN}=== Δημιουργία .env αρχείου ===${RESET}"
cat > .env << EOL
TELEGRAM_BOT_TOKEN=

NOVAXA_MASTER_KEY=$MASTER_KEY
OWNER_ID=$OWNER_ID

DEBUG=true
LOG_LEVEL=INFO

ADMIN_IDS=$OWNER_ID
