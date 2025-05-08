
echo "Setting up environment for Telegram bot on Render platform..."

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

if [ ! -f "enhanced_bot.py" ]; then
    echo "Error: enhanced_bot.py not found."
    exit 1
fi

if [ ! -f "api.py" ]; then
    echo "Error: api.py not found."
    exit 1
fi

if [ ! -f "integration.py" ]; then
    echo "Error: integration.py not found."
    exit 1
fi

if [ ! -f "monitor.py" ]; then
    echo "Error: monitor.py not found."
    exit 1
fi

if [ ! -f "security.py" ]; then
    echo "Error: security.py not found."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    cat > .env << ENVEOF
DEBUG=true
LOG_LEVEL=INFO
WEBHOOK_ENABLED=true
WEBHOOK_URL=
PORT=8443
ADMIN_IDS=
ENVEOF
    echo ".env file created."
fi

mkdir -p logs

if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Installing default dependencies..."
    pip install python-telegram-bot==13.12 requests>=2.27.1 psutil>=5.9.0 python-dotenv>=0.19.2 flask>=2.0.1 gunicorn>=20.1.0
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ] && [ -z "$NOVAXA_MASTER_KEY" ]; then
    echo "Warning: Neither TELEGRAM_BOT_TOKEN nor NOVAXA_MASTER_KEY environment variables are set."
    echo "Please set at least one of these variables in the Render dashboard."
    echo "For testing purposes, a placeholder token will be used."
    export TELEGRAM_BOT_TOKEN="placeholder_token"
fi

echo "Starting Telegram bot..."
if [ "$WEBHOOK_ENABLED" = "true" ]; then
    echo "Starting bot in webhook mode..."
    gunicorn -b 0.0.0.0:$PORT enhanced_bot:app
else
    echo "Starting bot in polling mode..."
    python3 enhanced_bot.py
fi

exit $?
