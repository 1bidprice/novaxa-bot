
cd "$(dirname "$0")"

echo "=== NOVAXA Bot Εκκίνηση (Έτοιμο προς χρήση) ==="

echo "Έλεγχος και εγκατάσταση απαραίτητων πακέτων..."
pip install python-telegram-bot==13.15 python-dotenv==0.21.0 requests==2.28.2 pyTelegramBotAPI==4.10.0

mkdir -p logs

if [ ! -f ".env" ]; then
    echo "Δημιουργία .env αρχείου..."
    
    echo "Παρακαλώ εισάγετε το Telegram user ID σας (θα οριστεί ως ιδιοκτήτης):"
    read OWNER_ID
    
    echo "Παρακαλώ εισάγετε το Telegram bot token σας:"
    read BOT_TOKEN
    
    cat > .env << EOL
TELEGRAM_BOT_TOKEN=$BOT_TOKEN
OWNER_ID=$OWNER_ID
DEBUG=true
LOG_LEVEL=INFO
ADMIN_IDS=$OWNER_ID
EOL
    echo "Αρχείο περιβάλλοντος δημιουργήθηκε"
fi

echo "Εκκίνηση του NOVAXA Bot..."
python ready_to_use_bot.py
