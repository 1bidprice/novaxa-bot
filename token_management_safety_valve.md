# NOVAXA Bot Token Management Safety Valve

## Επισκόπηση

Το NOVAXA Bot περιλαμβάνει μια "δικλείδα ασφαλείας" για τη διαχείριση του token του Telegram bot. Αυτή η λειτουργία επιτρέπει στον ιδιοκτήτη του bot να ελέγχει και να αλλάζει το token όταν χρειάζεται, χωρίς να απαιτείται επανεγκατάσταση ή τροποποίηση του κώδικα.

## Λειτουργίες Διαχείρισης Token

### 1. Αυτόματη Επικύρωση Token

Κατά την εκκίνηση, το bot:
- Ελέγχει αυτόματα το format του token
- Επικυρώνει το token με το Telegram API
- Διορθώνει αυτόματα κοινά προβλήματα format
- Προτρέπει για νέο token αν το υπάρχον είναι άκυρο

### 2. Εντολές Διαχείρισης Token (Μόνο για Ιδιοκτήτη)

Ο ιδιοκτήτης του bot μπορεί να χρησιμοποιήσει τις ακόλουθες εντολές:

- `/token` - Εμφανίζει τις διαθέσιμες επιλογές διαχείρισης token
- `/token info` - Εμφανίζει πληροφορίες για το τρέχον token
- `/token change <new_token>` - Αλλάζει το token του bot

### 3. Αυτόματη Διαγραφή Webhook

Πριν την εκκίνηση σε λειτουργία polling, το bot:
- Διαγράφει αυτόματα τυχόν ενεργά webhooks
- Αποτρέπει συγκρούσεις μεταξύ polling και webhook
- Διασφαλίζει ότι το bot θα ανταποκρίνεται σωστά

## Τεχνική Υλοποίηση

### Επικύρωση Token (fix_token.py)

```python
def validate_token_format(token):
    """Validate the format of a Telegram bot token."""
    if not token:
        return False, "Token is empty"
    
    parts = token.split(':')
    if len(parts) != 2:
        return False, "Token should contain exactly one colon (:)"
    
    bot_id, bot_hash = parts
    if not bot_id.isdigit():
        return False, "Bot ID part (before colon) should contain only digits"
    
    if len(bot_hash) < 30:
        return False, "Bot hash part (after colon) seems too short"
    
    return True, "Token format is valid"

def check_token_with_telegram(token, retries=3, delay=2):
    """Check if the token is valid by making a request to the Telegram API with retries."""
    for attempt in range(retries):
        try:
            url = f"https://api.telegram.org/bot{token}/getMe"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return True, f"Token is valid! Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})", bot_info
                else:
                    return False, f"API returned ok=false: {data.get('description', 'Unknown error')}", None
            elif response.status_code == 401:
                if attempt < retries - 1:
                    logging.warning(f"Token unauthorized (attempt {attempt+1}/{retries}). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                return False, "Token is unauthorized. Please check if the token is correct or create a new one with BotFather.", None
            else:
                if attempt < retries - 1:
                    logging.warning(f"API returned status code {response.status_code} (attempt {attempt+1}/{retries}). Retrying in {delay} seconds...")
                    time.sleep(delay)
                    continue
                return False, f"API returned status code {response.status_code}: {response.text}", None
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Error checking token (attempt {attempt+1}/{retries}): {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            return False, f"Error checking token: {str(e)}", None
    
    return False, "Failed after multiple attempts to validate token", None
```

### Διαγραφή Webhook (delete_webhook.py)

```python
def delete_webhook(token=None):
    """Delete the webhook for a Telegram bot."""
    if not token:
        load_dotenv()
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        logging.error("No token found")
        print("❌ Error: No token found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{token}/deleteWebhook"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                logging.info("Webhook deleted successfully")
                print("✅ Webhook deleted successfully")
                return True
            else:
                logging.error(f"Failed to delete webhook: {data.get('description', 'Unknown error')}")
                print(f"❌ Failed to delete webhook: {data.get('description', 'Unknown error')}")
                return False
        else:
            logging.error(f"API returned status code {response.status_code}: {response.text}")
            print(f"❌ API returned status code {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error deleting webhook: {str(e)}")
        print(f"❌ Error deleting webhook: {str(e)}")
        return False
```

### Εντολές Διαχείρισης Token (simple_bot.py)

```python
@bot.message_handler(commands=['token'])
def handle_token_command(message):
    """Handle token management commands."""
    user_id = message.from_user.id
    
    # Check if user is the owner
    if user_id != OWNER_ID:
        bot.reply_to(message, "⛔ Μόνο ο ιδιοκτήτης του bot μπορεί να διαχειριστεί το token.")
        return
    
    command_text = message.text.strip()
    args = command_text.split()
    
    if len(args) == 1:
        # Just /token command
        help_text = (
            "🔐 *Διαχείριση Token (Δικλείδα Ασφαλείας)*\n\n"
            "Διαθέσιμες εντολές:\n"
            "• `/token info` - Εμφάνιση πληροφοριών για το τρέχον token\n"
            "• `/token change <new_token>` - Αλλαγή του token του bot\n\n"
            "Αυτή η λειτουργία είναι διαθέσιμη μόνο στον ιδιοκτήτη του bot."
        )
        bot.reply_to(message, help_text, parse_mode='Markdown')
    elif len(args) >= 2:
        subcommand = args[1].lower()
        
        if subcommand == 'info':
            # Get token info
            load_dotenv()
            current_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
            
            if not current_token:
                bot.reply_to(message, "❌ Δεν βρέθηκε token στο αρχείο .env")
                return
            
            # Mask the token for security
            masked_token = f"{current_token[:5]}...{current_token[-5:]}"
            
            # Check token with Telegram API
            valid, msg, bot_info = check_token_with_telegram(current_token)
            
            if valid and bot_info:
                info_text = (
                    f"✅ *Πληροφορίες Token*\n\n"
                    f"• Token: `{masked_token}`\n"
                    f"• Bot Username: @{bot_info.get('username')}\n"
                    f"• Bot Name: {bot_info.get('first_name')}\n"
                    f"• Bot ID: {bot_info.get('id')}\n"
                    f"• Κατάσταση: Έγκυρο και λειτουργικό"
                )
            else:
                info_text = (
                    f"⚠️ *Πληροφορίες Token*\n\n"
                    f"• Token: `{masked_token}`\n"
                    f"• Κατάσταση: Μη έγκυρο\n"
                    f"• Σφάλμα: {msg}"
                )
            
            bot.reply_to(message, info_text, parse_mode='Markdown')
        
        elif subcommand == 'change':
            if len(args) < 3:
                bot.reply_to(message, "❌ Παρακαλώ παρέχετε το νέο token.\nΠαράδειγμα: `/token change 123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`", parse_mode='Markdown')
                return
            
            new_token = args[2]
            
            # Validate token format
            format_valid, format_msg = validate_token_format(new_token)
            if not format_valid:
                bot.reply_to(message, f"❌ Μη έγκυρο format token: {format_msg}\n\nΠαράδειγμα: `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`", parse_mode='Markdown')
                return
            
            # Check token with Telegram API
            valid, msg, bot_info = check_token_with_telegram(new_token)
            if not valid:
                bot.reply_to(message, f"❌ Μη έγκυρο token: {msg}", parse_mode='Markdown')
                return
            
            # Update .env file with new token
            try:
                with open(".env", "r") as f:
                    env_content = f.read()
                
                # Get current token
                load_dotenv()
                current_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
                
                if current_token:
                    updated_content = env_content.replace(f"TELEGRAM_BOT_TOKEN={current_token}", f"TELEGRAM_BOT_TOKEN={new_token}")
                else:
                    if "TELEGRAM_BOT_TOKEN=" in env_content:
                        updated_content = env_content.replace("TELEGRAM_BOT_TOKEN=", f"TELEGRAM_BOT_TOKEN={new_token}")
                    else:
                        updated_content = env_content + f"\nTELEGRAM_BOT_TOKEN={new_token}\n"
                
                with open(".env", "w") as f:
                    f.write(updated_content)
                
                success_text = (
                    f"✅ *Token ενημερώθηκε επιτυχώς!*\n\n"
                    f"• Νέο Bot: @{bot_info.get('username')} ({bot_info.get('first_name')})\n"
                    f"• Bot ID: {bot_info.get('id')}\n\n"
                    f"Το bot θα χρειαστεί επανεκκίνηση για να εφαρμοστεί το νέο token.\n"
                    f"Εκτελέστε `./start_simple_bot.sh` για επανεκκίνηση."
                )
                
                bot.reply_to(message, success_text, parse_mode='Markdown')
            except Exception as e:
                bot.reply_to(message, f"❌ Σφάλμα κατά την ενημέρωση του token: {str(e)}")
        
        else:
            bot.reply_to(message, f"❌ Άγνωστη υποεντολή: {subcommand}\n\nΧρησιμοποιήστε `/token` για να δείτε τις διαθέσιμες επιλογές.", parse_mode='Markdown')
```

## Διάγραμμα Ροής Εκκίνησης Bot

1. Εκτέλεση `./start_simple_bot.sh`
2. Έλεγχος και διόρθωση format token με `fix_token.py`
3. Διαγραφή webhook με `delete_webhook.py`
4. Εκκίνηση bot σε λειτουργία polling με `simple_bot.py`
5. Αν το token είναι έγκυρο, το bot ξεκινά και ανταποκρίνεται σε εντολές
6. Αν το token είναι άκυρο, ζητείται νέο token από τον χρήστη

## Πλεονεκτήματα της "Δικλείδας Ασφαλείας"

1. **Ασφάλεια**: Μόνο ο ιδιοκτήτης μπορεί να διαχειριστεί το token
2. **Ευελιξία**: Εύκολη αλλαγή token χωρίς επανεγκατάσταση
3. **Αξιοπιστία**: Αυτόματη επικύρωση και διόρθωση προβλημάτων
4. **Διαφάνεια**: Πλήρης ενημέρωση για την κατάσταση του token
5. **Συμβατότητα με Termux**: Λειτουργεί άψογα σε περιβάλλον κινητού

## Αντιμετώπιση Προβλημάτων

Αν το bot δεν ανταποκρίνεται:
1. Ελέγξτε το token με την εντολή `/token info`
2. Αλλάξτε το token με την εντολή `/token change <new_token>`
3. Επανεκκινήστε το bot με `./start_simple_bot.sh`
