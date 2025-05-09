
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot Εγκατάσταση με Ένα Κλικ (Polling Mode) ===${RESET}\n"

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

echo -e "✓ Κατέβασμα του validate_token.py"
curl -s -o validate_token.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/validate_token.py

echo -e "✓ Κατέβασμα του novaxa_bot_polling_fixed.py"
curl -s -o novaxa_bot_polling.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/novaxa_bot_polling_fixed.py

echo -e "✓ Κατέβασμα του token_guide.md"
curl -s -o token_guide.md https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/token_guide.md

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

echo -e "\n${YELLOW}Παρακαλώ εισάγετε το Telegram user ID σας (θα οριστεί ως ιδιοκτήτης):${RESET}"
read OWNER_ID
echo -e "${GREEN}Owner ID ορίστηκε σε: $OWNER_ID${RESET}"

echo -e "\n${YELLOW}Παρακαλώ εισάγετε το Telegram bot token σας:${RESET}"
read BOT_TOKEN

echo -e "\n${BOLD}${GREEN}=== Επικύρωση token ===${RESET}"
python validate_token.py "$BOT_TOKEN"

if [ $? -ne 0 ]; then
    echo -e "\n${RED}Το token δεν είναι έγκυρο. Παρακαλώ δείτε το αρχείο token_guide.md για οδηγίες.${RESET}"
    echo -e "\n${YELLOW}Θέλετε να συνεχίσετε με αυτό το token παρόλα αυτά; (y/n)${RESET}"
    read CONTINUE_WITH_INVALID
    
    if [[ "$CONTINUE_WITH_INVALID" != "y" && "$CONTINUE_WITH_INVALID" != "Y" ]]; then
        echo -e "\n${YELLOW}Παρακαλώ εισάγετε ένα νέο token:${RESET}"
        read BOT_TOKEN
    fi
fi

echo -e "\n${BOLD}${GREEN}=== Δημιουργία .env αρχείου ===${RESET}"
cat > .env << EOL
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
OWNER_ID=$OWNER_ID
DEBUG=true
LOG_LEVEL=INFO
ADMIN_IDS=$OWNER_ID
EOL
echo -e "${GREEN}Αρχείο περιβάλλοντος δημιουργήθηκε${RESET}"

echo -e "\n${BOLD}${GREEN}=== Ορισμός δικαιωμάτων εκτέλεσης ===${RESET}"
chmod +x *.py

echo -e "\n${BOLD}${GREEN}=== Δημιουργία script εκκίνησης ===${RESET}"
cat > start_bot.sh << 'STARTEOF'
cd "$(dirname "$0")"

echo "=== NOVAXA Bot Εκκίνηση ==="
echo "Επικύρωση token..."
python validate_token.py

if [ $? -eq 0 ]; then
    echo "Εκκίνηση bot σε polling mode..."
    python novaxa_bot_polling.py
else
    echo "Το token δεν είναι έγκυρο. Παρακαλώ διορθώστε το πριν την εκκίνηση του bot."
    echo "Δείτε το αρχείο token_guide.md για οδηγίες."
fi
STARTEOF

chmod +x start_bot.sh

echo -e "\n${BOLD}${GREEN}=== Η εγκατάσταση ολοκληρώθηκε! ===${RESET}"
echo -e "\n${BOLD}${BLUE}Το NOVAXA Bot έχει ρυθμιστεί σε polling mode.${RESET}"

echo -e "\n${YELLOW}Θέλετε να ξεκινήσετε το bot τώρα; (y/n)${RESET}"
read START_NOW

if [[ "$START_NOW" == "y" || "$START_NOW" == "Y" ]]; then
    echo -e "\n${GREEN}Εκκίνηση του bot...${RESET}"
    ./start_bot.sh
else
    echo -e "\n${GREEN}Μπορείτε να ξεκινήσετε το bot αργότερα με:${RESET}"
    echo -e "  ./start_bot.sh"
    echo -e "\n${YELLOW}Σημείωση: Αν αντιμετωπίζετε προβλήματα με το token, δείτε το αρχείο token_guide.md${RESET}"
fi

echo -e "\n${BOLD}${GREEN}Απολαύστε το NOVAXA Bot σας!${RESET}"
