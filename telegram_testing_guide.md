# NOVAXA Bot Telegram Testing Guide

## Εγκατάσταση και Δοκιμή του Bot στο Telegram

Αυτός ο οδηγός θα σας βοηθήσει να εγκαταστήσετε και να δοκιμάσετε το NOVAXA Bot στο Telegram, επιβεβαιώνοντας ότι ανταποκρίνεται σωστά.

### 1. Εγκατάσταση με Μία Εντολή

Αντιγράψτε και εκτελέστε την παρακάτω εντολή στο Termux:

```bash
curl -s -o novaxa_setup.sh https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/simple_bot_installer.sh && chmod +x novaxa_setup.sh && ./novaxa_setup.sh
```

### 2. Επιβεβαίωση Διαγραφής Webhook

Το πρόβλημα μη ανταπόκρισης του bot οφειλόταν σε ενεργό webhook. Η νέα έκδοση διαγράφει αυτόματα τυχόν webhooks πριν την εκκίνηση του bot σε λειτουργία polling.

Για χειροκίνητη διαγραφή του webhook:

```bash
python delete_webhook.py
```

### 3. Δοκιμή Εντολών στο Telegram

Αφού εκκινήσετε το bot, ανοίξτε το Telegram και δοκιμάστε τις παρακάτω εντολές:

- `/start` - Ξεκινήστε το bot
- `/help` - Εμφανίστε το μήνυμα βοήθειας
- `/status` - Ελέγξτε την κατάσταση του bot
- `/getid` - Δείτε το Telegram ID σας

### 4. Διαχείριση Token (Δικλείδα Ασφαλείας)

Ως ιδιοκτήτης του bot, μπορείτε να διαχειριστείτε το token με τις παρακάτω εντολές:

- `/token` - Εμφανίζει τις διαθέσιμες επιλογές διαχείρισης token
- `/token info` - Εμφανίζει πληροφορίες για το τρέχον token
- `/token change <new_token>` - Αλλάζει το token του bot

### 5. Αντιμετώπιση Προβλημάτων

Αν το bot εξακολουθεί να μην ανταποκρίνεται:

1. Βεβαιωθείτε ότι το token είναι έγκυρο: `python fix_token.py`
2. Επιβεβαιώστε ότι το webhook έχει διαγραφεί: `python delete_webhook.py`
3. Ελέγξτε τα logs για σφάλματα: `cat logs/bot.log`
4. Επανεκκινήστε το bot: `./start_simple_bot.sh`

### 6. Επιβεβαίωση Λειτουργίας Polling

Το bot τώρα λειτουργεί σε mode polling, το οποίο είναι πιο αξιόπιστο για χρήση σε Termux. Αυτό σημαίνει ότι:

- Δεν απαιτείται δημόσιο URL για webhook
- Το bot ελέγχει συνεχώς για νέα μηνύματα
- Η λειτουργία είναι πιο σταθερή σε περιβάλλον κινητού

## Σημειώσεις

- Το bot πρέπει να τρέχει συνεχώς για να λαμβάνει μηνύματα
- Αν κλείσετε το Termux, το bot θα σταματήσει
- Χρησιμοποιήστε την εντολή `/token` μόνο ως ιδιοκτήτης του bot
