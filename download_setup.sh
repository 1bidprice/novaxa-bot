#!/bin/bash


BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot One-Click Setup ===${RESET}\n"

if [ -d "/data/data/com.termux" ]; then
    echo -e "${BLUE}Εκτέλεση σε περιβάλλον Termux${RESET}"
    TERMUX=true
else
    echo -e "${YELLOW}Δεν εκτελείται σε Termux. Κάποιες λειτουργίες ίσως δεν δουλέψουν σωστά.${RESET}"
    TERMUX=false
fi

echo -e "\n${BOLD}${GREEN}=== Δημιουργία φακέλων ===${RESET}"
mkdir -p logs
mkdir -p config
mkdir -p dashboard/logs

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση απαραίτητων πακέτων ===${RESET}"
if [ "$TERMUX" = true ]; then
    pkg update -y
    pkg install -y python git curl
    pip install --upgrade pip
else
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip git curl
    pip3 install --upgrade pip
fi

if [ ! -f requirements.txt ]; then
    echo -e "\n${BOLD}${GREEN}=== Δημιουργία requirements.txt ===${RESET}"
    cat > requirements.txt << REQEOF
python-telegram-bot==13.15
python-dotenv==0.21.0
requests==2.28.2
flask==2.2.3
gunicorn==20.1.0
pyTelegramBotAPI==4.10.0
psutil==5.9.4
cryptography==39.0.1
REQEOF
fi

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση Python dependencies ===${RESET}"
pip install -r requirements.txt

# Download setup_and_run.sh
echo -e "\n${BOLD}${GREEN}=== Κατέβασμα του κύριου script εγκατάστασης ===${RESET}"
curl -s -o setup_and_run.sh https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/setup_and_run.sh
chmod +x setup_and_run.sh

# Run setup_and_run.sh
echo -e "\n${BOLD}${GREEN}=== Εκτέλεση του script εγκατάστασης ===${RESET}"
./setup_and_run.sh

echo -e "\n${BOLD}${GREEN}=== Η εγκατάσταση ολοκληρώθηκε! ===${RESET}"
