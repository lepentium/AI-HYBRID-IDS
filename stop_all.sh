#!/bin/bash
echo "🛑 Arrêt des services AI-HYBRID-IDS..."
sudo pkill -f sniffer_ensemble
sudo pkill -f log_monitor
pkill -f auth_api.py
sudo pkill -f dns_analyzer
pkill -f streamlit
echo "✅ Services arrêtés."
