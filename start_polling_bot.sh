cd "$(dirname "$0")"

echo "=== NOVAXA Bot Εκκίνηση ==="
echo "Έλεγχος και διόρθωση format token..."
python fix_token.py

echo "Εκκίνηση bot σε polling mode..."
python novaxa_bot_polling.py
