cd "$(dirname "$0")"

echo "=== NOVAXA Bot Εκκίνηση (Απλή Έκδοση) ==="
echo "Έλεγχος και διόρθωση format token..."
python fix_token.py

echo "Εκκίνηση bot..."
python simple_bot.py
