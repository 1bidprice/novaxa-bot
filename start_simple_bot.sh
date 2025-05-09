cd "$(dirname "$0")"

echo "=== NOVAXA Bot Εκκίνηση (Απλή Έκδοση) ==="
echo "Έλεγχος και διόρθωση format token..."
python fix_token.py

echo "Διαγραφή webhook (αν υπάρχει)..."
python delete_webhook.py

echo "Εκκίνηση bot..."
python simple_bot.py

echo "Απολαύστε το NOVAXA Bot σας!"
