#!/bin/bash
# ============================================================
# AI-HYBRID-IDS - Lancement complet de tous les services
# ============================================================

echo "🔄 Lancement de AI-HYBRID-IDS..."

# Réinitialiser la base
rm -f ~/AI-HYBRID-IDS/data/ids.db
echo "✅ Base réinitialisée."

# Lancer les services
cd ~/AI-HYBRID-IDS
nohup sudo ~/AI-HYBRID-IDS/.venv/bin/python ~/AI-HYBRID-IDS/src/capture/sniffer_ensemble.py > ~/logs_sniffer.log 2>&1 &
nohup sudo ~/AI-HYBRID-IDS/.venv/bin/python ~/AI-HYBRID-IDS/src/log_monitor.py > ~/logs_logmonitor.log 2>&1 &
nohup ~/AI-HYBRID-IDS/.venv/bin/python ~/AI-HYBRID-IDS/src/api/auth_api.py > ~/logs_api.log 2>&1 &
nohup sudo ~/AI-HYBRID-IDS/.venv/bin/python ~/AI-HYBRID-IDS/src/capture/dns_analyzer.py > ~/logs_dns.log 2>&1 &
source ~/AI-HYBRID-IDS/.venv/bin/activate
nohup streamlit run ~/AI-HYBRID-IDS/src/dashboard/app.py --server.port 8502 --server.address 0.0.0.0 > ~/logs_dashboard.log 2>&1 &

echo "✅ Services lancés !"
echo "📊 Dashboard : http://localhost:8502"
echo "📡 API : http://localhost:5001"
echo 'alias ids="sudo ~/AI-HYBRID-IDS/start_all.sh"' >> ~/.bashrc
source ~/.bashrc
