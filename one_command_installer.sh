
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot Εγκατάσταση (Έτοιμο προς χρήση) ===${RESET}\n"

mkdir -p novaxa_bot
cd novaxa_bot

mkdir -p logs

echo -e "\n${BOLD}${GREEN}=== Εγκατάσταση Python dependencies ===${RESET}"
pip install python-telegram-bot==13.15 python-dotenv==0.21.0 requests==2.28.2 pyTelegramBotAPI==4.10.0

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

echo -e "\n${BOLD}${GREEN}=== Κατέβασμα του ready_to_use_bot.py ===${RESET}"
curl -s -o ready_to_use_bot.py https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/ready_to_use_bot.py
chmod +x ready_to_use_bot.py

echo -e "\n${BOLD}${GREEN}=== Δημιουργία script εκκίνησης ===${RESET}"
cat > start_bot.sh << 'EOL'

cd "$(dirname "$0")"

echo "=== NOVAXA Bot Εκκίνηση (Έτοιμο προς χρήση) ==="
python ready_to_use_bot.py
EOL

chmod +x start_bot.sh

echo -e "\n${BOLD}${GREEN}=== Εκκίνηση του NOVAXA Bot ===${RESET}"
echo -e "${YELLOW}Το bot ξεκινάει αυτόματα...${RESET}"
./start_bot.sh
