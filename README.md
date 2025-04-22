# NOVAXA Telegram Bot

NOVAXA is an advanced Telegram bot with professional capabilities and automation features.

## Features

- Command handling (/start, /help, /status, /getid)
- Broadcast mechanisms (/notify, /broadcast, /alert)
- Logging system with file-based storage
- Webhook support for reliable operation
- Rate limiting to control command frequency
- System monitoring and performance tracking
- Dashboard for real-time monitoring and management

## Requirements

- Python 3.8 or newer
- pip (Python Package Manager)
- Telegram Bot Token from BotFather

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/novaxa-bot.git
cd novaxa-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:

```
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_token_here

# Debug Settings
DEBUG=true
LOG_LEVEL=INFO

# Webhook Configuration
WEBHOOK_ENABLED=false
WEBHOOK_URL=https://your-render-app.onrender.com/webhook
PORT=8443

# Admin User IDs (comma-separated)
ADMIN_IDS=123456789,987654321
```

## Usage

### Running the Bot

```bash
python enhanced_bot.py
```

Or using the start script:

```bash
chmod +x render_start.sh
./render_start.sh
```

### Running the Dashboard

```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

Access the dashboard at `http://localhost:5000`.

### Available Commands

#### Basic Commands
- `/start` - Start the bot
- `/help` - Show help message
- `/status` - Show bot status
- `/getid` - Get your Telegram ID

#### Admin Commands
- `/notify [user_id] [message]` - Send notification to a user
- `/broadcast [message]` - Send message to all users
- `/alert [message]` - Send alert to all admins
- `/log [count]` - Show recent logs
- `/maintenance` - Toggle maintenance mode
- `/users` - Show user statistics

## Deployment

### Deploying to Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set the start command to `./render_start.sh`
4. Add environment variables (TELEGRAM_BOT_TOKEN, etc.)
5. Deploy the service

For more detailed instructions, see the [Render Deployment Guide](render_deployment_guide.md).

## Dashboard

The NOVAXA bot includes a monitoring dashboard that provides:

- Real-time system status
- Performance metrics
- User statistics
- Log viewer
- Maintenance mode toggle

To access the dashboard, run the `start_dashboard.sh` script and navigate to `http://localhost:5000` in your browser.

## Testing

Run the tests with:

```bash
python -m tests.test_functionality
```

The test suite includes tests for:
- Bot commands
- API integration
- Monitoring functionality
- Performance tracking
- Service integration
- Notification system

## Project Structure

```
novaxa-bot/
├── api.py                # Telegram API integration
├── enhanced_bot.py       # Main bot implementation
├── integration.py        # Service integration module
├── monitor.py            # System monitoring module
├── render_start.sh       # Script for Render deployment
├── start_dashboard.sh    # Script to start the dashboard
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment configuration
├── dashboard/            # Dashboard implementation
│   ├── app.py            # Flask dashboard application
│   ├── templates/        # HTML templates
│   └── static/           # Static assets
├── logs/                 # Log files directory
└── tests/                # Test suite
    └── test_functionality.py  # Unit tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
