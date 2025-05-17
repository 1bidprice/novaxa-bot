
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot Εγκατάσταση με Ένα Κλικ ===${RESET}\n"

TEMP_DIR="$HOME/novaxa_temp"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση βασικών πακέτων ===${RESET}"
if [ -d "/data/data/com.termux" ]; then
    echo -e "${BLUE}Εκτέλεση σε περιβάλλον Termux${RESET}"
    pkg update -y
    pkg install -y python git curl
else
    echo -e "${YELLOW}Δεν εκτελείται σε Termux. Κάποιες λειτουργίες ίσως δεν δουλέψουν σωστά.${RESET}"
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip git curl
fi

echo -e "\n${BOLD}${GREEN}=== Κατέβασμα απαραίτητων αρχείων ===${RESET}"

mkdir -p novaxa-bot
cd novaxa-bot
mkdir -p logs
mkdir -p config
mkdir -p dashboard/logs

echo -e "✓ Κατέβασμα του security.py"
curl -s -o security.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/security_simple.py

echo -e "✓ Κατέβασμα του manage_tokens.py"
curl -s -o manage_tokens.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/manage_tokens.py

echo -e "✓ Κατέβασμα του enhanced_bot.py"
curl -s -o enhanced_bot.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/enhanced_bot_simple.py

echo -e "✓ Κατέβασμα του termux_dashboard.py"
curl -s -o termux_dashboard.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/termux_dashboard.py

echo -e "\n${BOLD}${GREEN}=== Δημιουργία minimal requirements.txt ===${RESET}"
cat > requirements.txt << REQEOF
python-telegram-bot==13.15
python-dotenv==0.21.0
requests==2.28.2
pyTelegramBotAPI==4.10.0
REQEOF

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση Python dependencies ===${RESET}"
pip install -r requirements.txt

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
EOL
echo -e "${GREEN}Αρχείο περιβάλλοντος δημιουργήθηκε${RESET}"

echo -e "\n${BOLD}${GREEN}=== Ορισμός δικαιωμάτων εκτέλεσης ===${RESET}"
chmod +x *.py

echo -e "\n${BOLD}${GREEN}=== Ρύθμιση διαχείρισης token ===${RESET}"
export NOVAXA_MASTER_KEY=$MASTER_KEY

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
