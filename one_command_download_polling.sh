
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

echo -e "✓ Κατέβασμα του fix_token.py"
curl -s -o fix_token.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/fix_token.py

echo -e "✓ Κατέβασμα του novaxa_bot_polling.py"
curl -s -o novaxa_bot_polling.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/novaxa_bot_polling.py

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
echo "Έλεγχος και διόρθωση format token..."
python fix_token.py

echo "Εκκίνηση bot σε polling mode..."
python novaxa_bot_polling.py
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
fi

echo -e "\n${BOLD}${GREEN}Απολαύστε το NOVAXA Bot σας!${RESET}"
