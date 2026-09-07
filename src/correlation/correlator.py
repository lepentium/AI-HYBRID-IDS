#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from collections import defaultdict
from datetime import datetime, timedelta
import sqlite3
import threading

# ---------- CONFIG ----------
CORRELATION_WINDOW = 60          # secondes
MIN_ALERTS_TO_TRIGGER = 3        # nombre minimum d'alertes pour déclencher une corrélation
MIN_CONFIDENCE_FOR_CORRELATION = 0.75  # confiance minimale moyenne

DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"

class Correlator:
    """Gère la corrélation des alertes par IP source."""
    
    def __init__(self):
        self.alert_cache = defaultdict(list)  # IP source -> liste de (timestamp, confiance, proto, dst_ip)
        self.correlation_counter = 0
        self._lock = threading.Lock()
        
    def add_alert(self, src_ip, dst_ip, proto, confidence, attack_type="unknown"):
        """
        Ajoute une alerte au cache et vérifie si une corrélation est déclenchée.
        Retourne : (correlation_id, is_correlated) ou (None, False)
        """
        now = time.time()
        with self._lock:
            # Ajouter l'alerte au cache
            self.alert_cache[src_ip].append({
                'timestamp': now,
                'confidence': confidence,
                'proto': proto,
                'dst_ip': dst_ip,
                'attack_type': attack_type
            })
            
            # Nettoyer les entrées trop anciennes
            self.alert_cache[src_ip] = [
                a for a in self.alert_cache[src_ip]
                if now - a['timestamp'] <= CORRELATION_WINDOW
            ]
            
            # Vérifier si on a assez d'alertes pour déclencher une corrélation
            if len(self.alert_cache[src_ip]) >= MIN_ALERTS_TO_TRIGGER:
                # Calculer la confiance moyenne
                avg_conf = sum(a['confidence'] for a in self.alert_cache[src_ip]) / len(self.alert_cache[src_ip])
                if avg_conf >= MIN_CONFIDENCE_FOR_CORRELATION:
                    # Corrélation déclenchée !
                    self.correlation_counter += 1
                    corr_id = self.correlation_counter
                    # Mettre à jour le cache avec le correlation_id
                    for alert in self.alert_cache[src_ip]:
                        alert['correlation_id'] = corr_id
                    self._save_correlation_to_db(src_ip, corr_id)
                    return corr_id, True
        
        return None, False
    
    def _save_correlation_to_db(self, src_ip, correlation_id):
        """Enregistre une corrélation dans une table dédiée."""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            # Créer la table si elle n'existe pas
            c.execute('''
                CREATE TABLE IF NOT EXISTS correlations (
                    id INTEGER PRIMARY KEY,
                    src_ip TEXT,
                    timestamp TEXT,
                    avg_confidence REAL,
                    alert_count INTEGER,
                    protocols TEXT,
                    dst_ips TEXT
                )
            ''')
            alerts = self.alert_cache[src_ip]
            avg_conf = sum(a['confidence'] for a in alerts) / len(alerts)
            protocols = ','.join(set(a['proto'] for a in alerts))
            dst_ips = ','.join(set(a['dst_ip'] for a in alerts))
            timestamp = datetime.now().isoformat()
            c.execute('''
                INSERT INTO correlations (
                    id, src_ip, timestamp, avg_confidence, alert_count, protocols, dst_ips
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (correlation_id, src_ip, timestamp, avg_conf, len(alerts), protocols, dst_ips))
            conn.commit()
            conn.close()
            print(f"[CORRELATION] ✅ Corrélation {correlation_id} enregistrée pour {src_ip} "
                  f"({len(alerts)} alertes, conf moyenne {avg_conf:.2%})")
        except Exception as e:
            print(f"[CORRELATION] Erreur sauvegarde : {e}")
    
    def get_summary(self, src_ip):
        """Retourne un résumé des alertes pour une IP."""
        now = time.time()
        alerts = self.alert_cache.get(src_ip, [])
        alerts = [a for a in alerts if now - a['timestamp'] <= CORRELATION_WINDOW]
        if not alerts:
            return None
        avg_conf = sum(a['confidence'] for a in alerts) / len(alerts)
        return {
            'count': len(alerts),
            'avg_confidence': avg_conf,
            'protocols': set(a['proto'] for a in alerts),
            'dst_ips': set(a['dst_ip'] for a in alerts)
        }
