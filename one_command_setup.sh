

echo "Κατέβασμα και εγκατάσταση του NOVAXA Bot..."

mkdir -p ~/novaxa_temp
cd ~/novaxa_temp

git clone https://github.com/1bidprice/novaxa-bot.git
cd novaxa-bot

git checkout devin/1746721919-automated-setup

chmod +x setup_and_run.sh
./setup_and_run.sh

echo "Η εγκατάσταση ολοκληρώθηκε!"
