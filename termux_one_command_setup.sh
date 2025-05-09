

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot Απλή Εγκατάσταση για Termux ===${RESET}\n"

TEMP_DIR="$HOME/novaxa_temp"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση βασικών πακέτων ===${RESET}"
pkg update -y
pkg install -y python git curl

echo -e "\n${BOLD}${GREEN}=== Κατέβασμα του NOVAXA Bot ===${RESET}"
git clone https://github.com/1bidprice/novaxa-bot.git
cd novaxa-bot
git checkout devin/1746721919-automated-setup

echo -e "\n${BOLD}${GREEN}=== Δημιουργία minimal requirements.txt ===${RESET}"
cat > requirements.txt << REQEOF
python-telegram-bot==13.15
python-dotenv==0.21.0
requests==2.28.2
flask==2.2.3
pyTelegramBotAPI==4.10.0
REQEOF

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση Python dependencies ===${RESET}"
pip install -r requirements.txt

echo -e "\n${BOLD}${GREEN}=== Δημιουργία φακέλων ===${RESET}"
mkdir -p logs
mkdir -p config
mkdir -p dashboard/logs

echo -e "\n${BOLD}${GREEN}=== Ρύθμιση περιβάλλοντος ===${RESET}"

if [ ! -f .env ] || ! grep -q "NOVAXA_MASTER_KEY" .env; then
    TIMESTAMP=$(date +%s)
    MASTER_KEY="novaxa_secure_master_key_$TIMESTAMP"
    echo -e "${GREEN}Δημιουργήθηκε νέο master key${RESET}"
else
    MASTER_KEY=$(grep "NOVAXA_MASTER_KEY" .env | cut -d'=' -f2)
    echo -e "${GREEN}Χρήση υπάρχοντος master key${RESET}"
fi

if [ ! -f .env ] || ! grep -q "OWNER_ID" .env || [ "$(grep "OWNER_ID" .env | cut -d'=' -f2)" = "your_telegram_id_here" ]; then
    echo -e "\n${YELLOW}Παρακαλώ εισάγετε το Telegram user ID σας (θα οριστεί ως ιδιοκτήτης):${RESET}"
    read OWNER_ID
    echo -e "${GREEN}Owner ID ορίστηκε σε: $OWNER_ID${RESET}"
else
    OWNER_ID=$(grep "OWNER_ID" .env | cut -d'=' -f2)
    echo -e "${GREEN}Χρήση υπάρχοντος owner ID: $OWNER_ID${RESET}"
fi

if [ ! -f .env ]; then
    echo -e "\n${BOLD}${GREEN}=== Δημιουργία .env αρχείου ===${RESET}"
    cat > .env << EOL
TELEGRAM_BOT_TOKEN=

NOVAXA_MASTER_KEY=$MASTER_KEY
OWNER_ID=$OWNER_ID

DEBUG=true
LOG_LEVEL=INFO

WEBHOOK_ENABLED=false
WEBHOOK_URL=
PORT=8443

ADMIN_IDS=$OWNER_ID
EOL
    echo -e "${GREEN}Αρχείο περιβάλλοντος δημιουργήθηκε${RESET}"
else
    echo -e "\n${BOLD}${GREEN}=== Ενημέρωση .env αρχείου ===${RESET}"
    if ! grep -q "NOVAXA_MASTER_KEY" .env; then
        echo "NOVAXA_MASTER_KEY=$MASTER_KEY" >> .env
        echo -e "${GREEN}Προστέθηκε master key στο .env${RESET}"
    fi
    
    if ! grep -q "OWNER_ID" .env; then
        echo "OWNER_ID=$OWNER_ID" >> .env
        echo -e "${GREEN}Προστέθηκε owner ID στο .env${RESET}"
    elif [ "$(grep "OWNER_ID" .env | cut -d'=' -f2)" = "your_telegram_id_here" ]; then
        sed -i "s/OWNER_ID=.*/OWNER_ID=$OWNER_ID/" .env
        echo -e "${GREEN}Ενημερώθηκε το owner ID στο .env${RESET}"
    fi
    
    if ! grep -q "ADMIN_IDS" .env; then
        echo "ADMIN_IDS=$OWNER_ID" >> .env
        echo -e "${GREEN}Προστέθηκαν admin IDs στο .env${RESET}"
    fi
fi

echo -e "\n${BOLD}${GREEN}=== Ορισμός δικαιωμάτων εκτέλεσης ===${RESET}"
chmod +x *.py
chmod +x *.sh

echo -e "\n${BOLD}${GREEN}=== Ρύθμιση διαχείρισης token ===${RESET}"
export NOVAXA_MASTER_KEY=$MASTER_KEY

TOKEN_EXISTS=false
if [ -f "config/tokens.json" ]; then
    TOKEN_EXISTS=true
    echo -e "${GREEN}Βρέθηκε διαμόρφωση token${RESET}"
fi

if [ "$TOKEN_EXISTS" = false ]; then
    echo -e "\n${YELLOW}Παρακαλώ εισάγετε το Telegram bot token σας:${RESET}"
    read BOT_TOKEN

    echo -e "\n${YELLOW}Παρακαλώ εισάγετε ένα όνομα για αυτό το token:${RESET}"
    read TOKEN_NAME

    python manage_tokens.py add "$BOT_TOKEN" --name "$TOKEN_NAME" --owner "$OWNER_ID"

    TOKEN_ID=$(python manage_tokens.py list | grep -A 1 "$TOKEN_NAME" | tail -n 1 | awk '{print $1}')
    if [ -n "$TOKEN_ID" ]; then
        python manage_tokens.py activate "$TOKEN_ID"
        echo -e "${GREEN}Το token ενεργοποιήθηκε επιτυχώς${RESET}"
    else
        echo -e "${RED}Αποτυχία λήψης ID token. Παρακαλώ ενεργοποιήστε το token χειροκίνητα.${RESET}"
    fi
else
    echo -e "${GREEN}Χρήση υπάρχουσας διαμόρφωσης token${RESET}"
    python manage_tokens.py list
fi

echo -e "\n${BOLD}${GREEN}=== Δημιουργία scripts εκκίνησης ===${RESET}"
cat > start_bot.sh << 'EOL'
python enhanced_bot.py
EOL

chmod +x start_bot.sh

cat > start_dashboard.sh << 'EOL'
python termux_dashboard.py
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
