#!/bin/bash

# NOVAXA Bot Direct Setup Script
# This script sets up everything needed for NOVAXA bot in one step

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot Άμεση Εγκατάσταση ===${RESET}\n"

# Check if running in Termux
if [ -d "/data/data/com.termux" ]; then
    echo -e "${BLUE}Εκτέλεση σε περιβάλλον Termux${RESET}"
    TERMUX=true
else
    echo -e "${YELLOW}Δεν εκτελείται σε Termux. Κάποιες λειτουργίες ίσως δεν δουλέψουν σωστά.${RESET}"
    TERMUX=false
fi

# Create directories
echo -e "\n${BOLD}${GREEN}=== Δημιουργία φακέλων ===${RESET}"
mkdir -p logs
mkdir -p config
mkdir -p dashboard/logs

# Install required packages
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

# Create requirements.txt if it doesn't exist
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

# Install Python dependencies
echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση Python dependencies ===${RESET}"
pip install -r requirements.txt

# Download necessary files
echo -e "\n${BOLD}${GREEN}=== Κατέβασμα απαραίτητων αρχείων ===${RESET}"

# Security module
if [ ! -f security.py ]; then
    curl -s -o security.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/security.py
    chmod +x security.py
    echo -e "${GREEN}✓ Κατέβηκε το security.py${RESET}"
fi

# Token management
if [ ! -f manage_tokens.py ]; then
    curl -s -o manage_tokens.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/manage_tokens.py
    chmod +x manage_tokens.py
    echo -e "${GREEN}✓ Κατέβηκε το manage_tokens.py${RESET}"
fi

# Enhanced bot
if [ ! -f enhanced_bot.py ]; then
    curl -s -o enhanced_bot.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/enhanced_bot.py
    chmod +x enhanced_bot.py
    echo -e "${GREEN}✓ Κατέβηκε το enhanced_bot.py${RESET}"
fi

# Dashboard
if [ ! -f termux_dashboard.py ]; then
    curl -s -o termux_dashboard.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/termux_dashboard.py
    chmod +x termux_dashboard.py
    echo -e "${GREEN}✓ Κατέβηκε το termux_dashboard.py${RESET}"
fi

# Set up environment
echo -e "\n${BOLD}${GREEN}=== Ρύθμιση περιβάλλοντος ===${RESET}"
if [ ! -f .env ]; then
    # Auto-generate owner ID (will need to be updated later)
    echo -e "${YELLOW}Παρακαλώ εισάγετε το Telegram ID σας (θα οριστεί ως ιδιοκτήτης):${RESET}"
    read OWNER_ID
    
    if [ -z "$OWNER_ID" ]; then
        OWNER_ID="123456789"
        echo -e "${YELLOW}Χρησιμοποιείται προεπιλεγμένο ID. Θα πρέπει να το ενημερώσετε αργότερα.${RESET}"
    fi
    
    TIMESTAMP=$(date +%s)
    MASTER_KEY="novaxa_secure_master_key_$TIMESTAMP"
    
    cat > .env << ENVEOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=

# Security Configuration
NOVAXA_MASTER_KEY=$MASTER_KEY
OWNER_ID=$OWNER_ID

# Debug Settings
DEBUG=true
LOG_LEVEL=INFO

# Webhook Configuration
WEBHOOK_ENABLED=false
WEBHOOK_URL=
PORT=8443

# Admin User IDs (comma-separated)
ADMIN_IDS=$OWNER_ID
ENVEOF
    
    echo -e "${GREEN}Το αρχείο περιβάλλοντος δημιουργήθηκε${RESET}"
fi

# Make scripts executable
echo -e "\n${BOLD}${GREEN}=== Ορισμός δικαιωμάτων εκτέλεσης ===${RESET}"
chmod +x *.py
chmod +x *.sh 2>/dev/null || true

# Set up token management
echo -e "\n${BOLD}${GREEN}=== Ρύθμιση διαχείρισης token ===${RESET}"
export NOVAXA_MASTER_KEY=$(grep "NOVAXA_MASTER_KEY" .env | cut -d'=' -f2)

TOKEN_EXISTS=false
if [ -f "config/tokens.json" ]; then
    TOKEN_EXISTS=true
    echo -e "${GREEN}Βρέθηκε διαμόρφωση token${RESET}"
fi

if [ "$TOKEN_EXISTS" = false ]; then
    echo -e "\n${YELLOW}Παρακαλώ εισάγετε το Telegram bot token σας:${RESET}"
    read BOT_TOKEN

    if [ -z "$BOT_TOKEN" ]; then
        echo -e "${RED}Δεν δόθηκε token. Θα πρέπει να προσθέσετε ένα token αργότερα.${RESET}"
    else
        echo -e "\n${YELLOW}Παρακαλώ εισάγετε ένα όνομα για αυτό το token:${RESET}"
        read TOKEN_NAME
        
        if [ -z "$TOKEN_NAME" ]; then
            TOKEN_NAME="Default"
        fi

        python manage_tokens.py add "$BOT_TOKEN" --name "$TOKEN_NAME" --owner "$OWNER_ID"

        TOKEN_ID=$(python manage_tokens.py list | grep -A 1 "$TOKEN_NAME" | tail -n 1 | awk '{print $1}')
        if [ -n "$TOKEN_ID" ]; then
            python manage_tokens.py activate "$TOKEN_ID"
            echo -e "${GREEN}Το token ενεργοποιήθηκε επιτυχώς${RESET}"
        else
            echo -e "${RED}Αποτυχία λήψης ID token. Παρακαλώ ενεργοποιήστε το token χειροκίνητα.${RESET}"
        fi
    fi
else
    echo -e "${GREEN}Χρήση υπάρχουσας διαμόρφωσης token${RESET}"
    python manage_tokens.py list
fi

# Create start scripts
echo -e "\n${BOLD}${GREEN}=== Δημιουργία scripts εκκίνησης ===${RESET}"
cat > start_bot.sh << 'EOL'
#!/bin/bash
python enhanced_bot.py
EOL
EOL

chmod +x start_bot.sh

cat > start_dashboard.sh << 'EOL'
#!/bin/bash
python termux_dashboard.py
EOL
EOL

chmod +x start_dashboard.sh

echo -e "\n${BOLD}${GREEN}=== Η εγκατάσταση ολοκληρώθηκε! ===${RESET}"
echo -e "\n${BOLD}${BLUE}Το NOVAXA Bot έχει ρυθμιστεί με δυνατότητες διαχείρισης token.${RESET}"

echo -e "\n${YELLOW}Τι θα θέλατε να κάνετε τώρα;${RESET}"
echo -e "1. Εκκίνηση του bot"
echo -e "2. Εκκίνηση του dashboard"
echo -e "3. Έξοδος"
read -p "Εισάγετε την επιλογή σας (1-3): " CHOICE

case $CHOICE in
    1)
        echo -e "\n${GREEN}Εκκίνηση του bot...${RESET}"
        ./start_bot.sh
        ;;
    2)
        echo -e "\n${GREEN}Εκκίνηση του dashboard...${RESET}"
        ./start_dashboard.sh
        ;;
    3)
        echo -e "\n${GREEN}Η εγκατάσταση ολοκληρώθηκε. Μπορείτε να ξεκινήσετε το bot αργότερα με:${RESET}"
        echo -e "  ./start_bot.sh"
        echo -e "\n${GREEN}Ή να ξεκινήσετε το dashboard με:${RESET}"
        echo -e "  ./start_dashboard.sh"
        ;;
    *)
        echo -e "\n${RED}Μη έγκυρη επιλογή. Έξοδος.${RESET}"
        ;;
esac

echo -e "\n${BOLD}${GREEN}Απολαύστε το NOVAXA Bot σας!${RESET}"
