
echo "====================================="
echo "NOVAXA Bot Termux Setup"
echo "====================================="
echo

if [ -z "$TERMUX_VERSION" ]; then
    echo "⚠️ This script is designed to run in Termux."
    echo "If you're not running in Termux, some features may not work correctly."
    echo
fi

echo "📦 Installing required packages..."
pkg update -y
pkg install -y python git

echo "📁 Creating directory structure..."
mkdir -p ~/novaxa-bot
cd ~/novaxa-bot

if [ ! -d ".git" ]; then
    echo "🔄 Cloning NOVAXA bot repository..."
    git clone https://github.com/1bidprice/novaxa-bot.git .
else
    echo "🔄 Updating NOVAXA bot repository..."
    git pull
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << ENVEOF
TELEGRAM_BOT_TOKEN=
NOVAXA_MASTER_KEY=

DEBUG=true
LOG_LEVEL=INFO

WEBHOOK_ENABLED=false
WEBHOOK_URL=
PORT=8443

ADMIN_IDS=
OWNER_ID=
ENVEOF
    echo "✅ .env file created."
fi

echo "🔧 Making scripts executable..."
chmod +x configure_webhook.py
chmod +x manage_tokens.py
chmod +x render_start.sh
chmod +x termux_dashboard.py

echo "📁 Creating logs directory..."
mkdir -p logs

echo
echo "====================================="
echo "✅ NOVAXA Bot setup complete!"
echo "====================================="
echo
echo "Next steps:"
echo "1. Edit the .env file to set your Telegram bot token:"
echo "   nano .env"
echo
echo "2. Set up your master key for token management:"
echo "   export NOVAXA_MASTER_KEY=your_secret_key"
echo
echo "3. Add your Telegram user ID as the owner:"
echo "   Edit the .env file and set OWNER_ID=your_telegram_id"
echo
echo "4. Run the bot in polling mode for local testing:"
echo "   python enhanced_bot.py"
echo
echo "5. Configure webhook for deployment:"
echo "   python configure_webhook.py --token YOUR_TOKEN --url YOUR_RENDER_URL"
echo
echo "6. Manage tokens:"
echo "   python manage_tokens.py list"
echo
echo "7. Start the Termux dashboard:"
echo "   python termux_dashboard.py"
echo
echo "For more information, see the README.md file."
echo
