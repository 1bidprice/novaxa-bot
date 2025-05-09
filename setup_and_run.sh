
BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
RED="\033[31m"
RESET="\033[0m"

echo -e "${BOLD}${GREEN}=== NOVAXA Bot One-Click Setup and Run ===${RESET}\n"

if [ -d "/data/data/com.termux" ]; then
    echo -e "${BLUE}Running in Termux environment${RESET}"
    TERMUX=true
else
    echo -e "${YELLOW}Not running in Termux. Some features may not work correctly.${RESET}"
    TERMUX=false
fi

echo -e "\n${BOLD}${GREEN}=== Creating directories ===${RESET}"
mkdir -p logs
mkdir -p config
mkdir -p dashboard/logs

echo -e "\n${BOLD}${GREEN}=== Installing required packages ===${RESET}"
if [ "$TERMUX" = true ]; then
    pkg update -y
    pkg install -y python git
    pip install --upgrade pip
else
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip git
    pip3 install --upgrade pip
fi

echo -e "\n${BOLD}${GREEN}=== Installing Python dependencies ===${RESET}"
pip install -r requirements.txt

echo -e "\n${BOLD}${GREEN}=== Setting up environment variables ===${RESET}"

if [ ! -f .env ] || ! grep -q "NOVAXA_MASTER_KEY" .env; then
    TIMESTAMP=$(date +%s)
    MASTER_KEY="novaxa_secure_master_key_$TIMESTAMP"
    echo -e "${GREEN}Generated new master key${RESET}"
else
    MASTER_KEY=$(grep "NOVAXA_MASTER_KEY" .env | cut -d'=' -f2)
    echo -e "${GREEN}Using existing master key${RESET}"
fi

if [ ! -f .env ] || ! grep -q "OWNER_ID" .env || [ "$(grep "OWNER_ID" .env | cut -d'=' -f2)" = "your_telegram_id_here" ]; then
    echo -e "\n${YELLOW}Please enter your Telegram user ID (this will be set as the owner):${RESET}"
    read OWNER_ID
    echo -e "${GREEN}Owner ID set to: $OWNER_ID${RESET}"
else
    OWNER_ID=$(grep "OWNER_ID" .env | cut -d'=' -f2)
    echo -e "${GREEN}Using existing owner ID: $OWNER_ID${RESET}"
fi

if [ ! -f .env ]; then
    echo -e "\n${BOLD}${GREEN}=== Creating .env file ===${RESET}"
    cat > .env << EOL

NOVAXA_MASTER_KEY=$MASTER_KEY
OWNER_ID=$OWNER_ID

DEBUG=true
LOG_LEVEL=INFO

WEBHOOK_ENABLED=false
WEBHOOK_URL=
PORT=8443

ADMIN_IDS=$OWNER_ID
EOL
    echo -e "${GREEN}Environment file created${RESET}"
else
    echo -e "\n${BOLD}${GREEN}=== Updating .env file ===${RESET}"
    if ! grep -q "NOVAXA_MASTER_KEY" .env; then
        echo "NOVAXA_MASTER_KEY=$MASTER_KEY" >> .env
        echo -e "${GREEN}Added master key to .env${RESET}"
    fi
    
    if ! grep -q "OWNER_ID" .env; then
        echo "OWNER_ID=$OWNER_ID" >> .env
        echo -e "${GREEN}Added owner ID to .env${RESET}"
    elif [ "$(grep "OWNER_ID" .env | cut -d'=' -f2)" = "your_telegram_id_here" ]; then
        sed -i "s/OWNER_ID=.*/OWNER_ID=$OWNER_ID/" .env
        echo -e "${GREEN}Updated owner ID in .env${RESET}"
    fi
    
    if ! grep -q "ADMIN_IDS" .env; then
        echo "ADMIN_IDS=$OWNER_ID" >> .env
        echo -e "${GREEN}Added admin IDs to .env${RESET}"
    fi
fi

echo -e "\n${BOLD}${GREEN}=== Making scripts executable ===${RESET}"
chmod +x *.py
chmod +x *.sh

echo -e "\n${BOLD}${GREEN}=== Setting up token management ===${RESET}"
export NOVAXA_MASTER_KEY=$MASTER_KEY

TOKEN_EXISTS=false
if [ -f "config/tokens.json" ]; then
    TOKEN_EXISTS=true
    echo -e "${GREEN}Token configuration found${RESET}"
fi

if [ "$TOKEN_EXISTS" = false ]; then
    echo -e "\n${YELLOW}Please enter your Telegram bot token:${RESET}"
    read BOT_TOKEN

    echo -e "\n${YELLOW}Please enter a name for this token:${RESET}"
    read TOKEN_NAME

    python manage_tokens.py add "$BOT_TOKEN" --name "$TOKEN_NAME" --owner "$OWNER_ID"

    TOKEN_ID=$(python manage_tokens.py list | grep -A 1 "$TOKEN_NAME" | tail -n 1 | awk '{print $1}')
    if [ -n "$TOKEN_ID" ]; then
        python manage_tokens.py activate "$TOKEN_ID"
        echo -e "${GREEN}Token activated successfully${RESET}"
    else
        echo -e "${RED}Failed to get token ID. Please activate the token manually.${RESET}"
    fi
else
    echo -e "${GREEN}Using existing token configuration${RESET}"
    python manage_tokens.py list
fi

echo -e "\n${BOLD}${GREEN}=== Creating start scripts ===${RESET}"
cat > start_bot.sh << EOL

python enhanced_bot.py
EOL

chmod +x start_bot.sh

cat > start_dashboard.sh << EOL

python termux_dashboard_enhanced.py
EOL

chmod +x start_dashboard.sh

echo -e "\n${BOLD}${GREEN}=== Setup Complete! ===${RESET}"
echo -e "\n${BOLD}${BLUE}NOVAXA Bot is now set up with token management capabilities.${RESET}"

echo -e "\n${YELLOW}What would you like to do now?${RESET}"
echo -e "1. Start the bot"
echo -e "2. Start the dashboard"
echo -e "3. Exit"
read -p "Enter your choice (1-3): " CHOICE

case $CHOICE in
    1)
        echo -e "\n${GREEN}Starting the bot...${RESET}"
        ./start_bot.sh
        ;;
    2)
        echo -e "\n${GREEN}Starting the dashboard...${RESET}"
        ./start_dashboard.sh
        ;;
    3)
        echo -e "\n${GREEN}Setup completed. You can start the bot later with:${RESET}"
        echo -e "  ./start_bot.sh"
        echo -e "\n${GREEN}Or start the dashboard with:${RESET}"
        echo -e "  ./start_dashboard.sh"
        ;;
    *)
        echo -e "\n${RED}Invalid choice. Exiting.${RESET}"
        ;;
esac

echo -e "\n${BOLD}${GREEN}Enjoy your NOVAXA Bot!${RESET}"
