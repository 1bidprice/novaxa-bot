# NOVAXA Bot - Polling Mode Implementation

## Πρόβλημα και Λύση

### Το Πρόβλημα
Το αρχικό bot αντιμετώπιζε δύο βασικά προβλήματα στο Termux:

1. **Ασυμβατότητα Flask/Werkzeug**: Το σφάλμα `ImportError: cannot import name 'url_quote' from 'werkzeug.urls'` δείχνει ότι υπάρχει πρόβλημα με τις εκδόσεις των βιβλιοθηκών στο Termux.

2. **Σφάλμα Webhook**: Το σφάλμα `ApiTelegramException: Error code: 404. Description: Not Found` εμφανίζεται κατά την προσπάθεια αφαίρεσης του webhook, υποδεικνύοντας πρόβλημα με τη διαμόρφωση του webhook.

### Η Λύση
Δημιουργήθηκε μια νέα έκδοση του bot που:

1. **Χρησιμοποιεί μόνο Polling Mode**: Αποφεύγει εντελώς τη χρήση webhooks, επομένως δεν χρειάζεται να τα αφαιρέσει κατά την εκκίνηση.

2. **Δεν εξαρτάται από το Flask**: Αποφεύγει τα προβλήματα συμβατότητας με το Werkzeug/Flask στο Termux.

3. **Διορθώνει αυτόματα προβλήματα με τη μορφή του token**: Περιλαμβάνει ένα script που ελέγχει και διορθώνει αυτόματα τη μορφή του token.

4. **Περιλαμβάνει τη "δικλείδα ασφαλείας"**: Επιτρέπει στον ιδιοκτήτη να αλλάξει το token μέσω της εντολής `/token change`.

## Πώς Λειτουργεί

### Polling Mode vs Webhook Mode

- **Webhook Mode**: Το Telegram στέλνει ενημερώσεις στον server σας όταν συμβαίνουν (απαιτεί δημόσιο URL).
- **Polling Mode**: Το bot ρωτάει συνεχώς το Telegram αν υπάρχουν νέες ενημερώσεις (δεν απαιτεί δημόσιο URL).

Το polling mode είναι πιο απλό και λειτουργεί παντού, ακόμα και πίσω από firewalls ή σε συσκευές χωρίς δημόσια IP.

### Αρχεία της Λύσης

1. **novaxa_bot_polling.py**: Το κύριο αρχείο του bot που χρησιμοποιεί polling mode.
2. **fix_token.py**: Script που διορθώνει αυτόματα προβλήματα με τη μορφή του token.
3. **start_polling_bot.sh**: Script εκκίνησης που τρέχει το fix_token.py και μετά το bot.
4. **one_command_download_polling.sh**: Script εγκατάστασης με ένα κλικ.

## Πώς να Χρησιμοποιήσετε το Bot

### Εγκατάσταση

```bash
curl -s -o novaxa_setup.sh https://raw.githubusercontent.com/1bidprice/novaxa-bot/devin/1746721919-automated-setup/one_command_download_polling.sh && chmod +x novaxa_setup.sh && ./novaxa_setup.sh
```

### Διαθέσιμες Εντολές

- `/start` - Ξεκινήστε το bot
- `/help` - Εμφανίστε το μήνυμα βοήθειας
- `/status` - Ελέγξτε την κατάσταση του bot
- `/getid` - Δείτε το Telegram ID σας

### Εντολές Διαχειριστή

- `/notify <μήνυμα>` - Στείλτε ειδοποίηση στον ιδιοκτήτη
- `/broadcast <μήνυμα>` - Στείλτε μήνυμα σε όλους τους χρήστες
- `/log` - Δείτε τα πρόσφατα logs

### Δικλείδα Ασφαλείας (Μόνο για τον ιδιοκτήτη)

- `/token` - Δείτε πληροφορίες για το token
- `/token info` - Δείτε λεπτομερείς πληροφορίες για το token
- `/token change <new_token>` - Αλλάξτε το token

## Αντιμετώπιση Προβλημάτων

### Αν το Bot Δεν Ανταποκρίνεται

1. Ελέγξτε ότι το token είναι σωστό: `/token info`
2. Επανεκκινήστε το bot: `./start_polling_bot.sh`
3. Ελέγξτε τα logs για σφάλματα: `cat logs/bot.log`

### Αν το Token Έχει Λάθος Μορφή

Το script `fix_token.py` θα προσπαθήσει να διορθώσει αυτόματα τη μορφή του token κατά την εκκίνηση. Αν αυτό αποτύχει, μπορείτε να αλλάξετε χειροκίνητα το token στο αρχείο `.env`.
