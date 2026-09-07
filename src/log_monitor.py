#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyseur de logs système pour AI-HYBRID-IDS
Surveille /var/log/auth.log et /var/log/syslog
Détecte les tentatives d'intrusion locales et les injecte dans SQLite
"""

import time
import re
import sqlite3
from datetime import datetime
import os

# ---------- CONFIG ----------
DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"
LOG_FILES = [
    "/var/log/auth.log",
    "/var/log/syslog"
]

# Patterns de détection : (regex, label, priorité)
PATTERNS = [
    (r"Failed password for .* from (\d+\.\d+\.\d+\.\d+)", "Tentative SSH échouée", 1),
    (r"Invalid user .* from (\d+\.\d+\.\d+\.\d+)", "Utilisateur invalide SSH", 1),
    (r"authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)", "Échec d'authentification", 1),
    (r"sudo.*COMMAND.*FAILED", "Échec sudo (local)", 0.5),
    (r"session opened for user root", "Session root ouverte", 0.3),
    (r"Connection closed by authenticating user .* (\d+\.\d+\.\d+\.\d+)", "Connexion SSH fermée", 0.5),
    (r"pam_unix\(sshd:auth\): authentication failure.*rhost=(\d+\.\d+\.\d+\.\d+)", "Échec PAM SSH", 1),
]

# Cache pour éviter les doublons
seen_entries = set()

# ---------- FONCTIONS ----------
def init_db():
    """S'assurer que la colonne llm_report existe dans la table packets."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("PRAGMA table_info(packets)")
        columns = [col[1] for col in c.fetchall()]
        if 'llm_report' not in columns:
            c.execute("ALTER TABLE packets ADD COLUMN llm_report TEXT")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERREUR] Init DB : {e}")

def insert_alert(src_ip, message, priority=1.0):
    """Injecte une alerte dans la base SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        # Vérifier si l'alerte existe déjà (éviter les doublons)
        entry_key = f"{src_ip}_{message[:50]}"
        if entry_key in seen_entries:
            return
        seen_entries.add(entry_key)
        # Limiter la taille du cache
        if len(seen_entries) > 10000:
            seen_entries.clear()
        c.execute('''
            INSERT INTO packets (
                timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                packet_size, ttl, flags, ml_prediction, anomaly, correlation_score, llm_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            src_ip,
            "localhost",
            "LOG",
            0, 0, 0, 0, "N/A",
            "attack",
            1,
            priority,
            f"[LOG] {message}"
        ))
        conn.commit()
        conn.close()
        print(f"[LOG-ALERT] {src_ip} : {message[:80]}...")
    except Exception as e:
        print(f"[ERREUR] Insertion log : {e}")

def follow_logs():
    """Surveille les fichiers de logs en temps réel."""
    print("[LOG-MONITOR] Démarrage de la surveillance des logs système...")
    print(f"[LOG-MONITOR] Fichiers surveillés : {', '.join(LOG_FILES)}")
    print("[LOG-MONITOR] Appuyez sur Ctrl+C pour arrêter.")
    print("-" * 60)

    positions = {}
    # Initialiser les positions
    for log_file in LOG_FILES:
        try:
            with open(log_file, "r") as f:
                f.seek(0, 2)  # Aller à la fin
                positions[log_file] = f.tell()
        except FileNotFoundError:
            positions[log_file] = 0
            print(f"[LOG-MONITOR] Fichier non trouvé : {log_file}")

    while True:
        for log_file in LOG_FILES:
            try:
                with open(log_file, "r") as f:
                    f.seek(positions[log_file])
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        # Vérifier les patterns
                        for pattern, label, priority in PATTERNS:
                            match = re.search(pattern, line)
                            if match:
                                ip = match.group(1) if len(match.groups()) > 0 else "0.0.0.0"
                                # Filtrer les IP locales (ignorer les bruits)
                                if ip.startswith("127.") or ip == "0.0.0.0":
                                    continue
                                message = f"{label} - {line[:200]}"
                                insert_alert(ip, message, priority)
                                break  # Éviter les doublons de pattern pour la même ligne
                    positions[log_file] = f.tell()
            except FileNotFoundError:
                pass
            except Exception as e:
                print(f"[ERREUR] Lecture {log_file} : {e}")
        time.sleep(2)

# ---------- MAIN ----------
if __name__ == "__main__":
    if os.geteuid() != 0:
        print("❌ Ce script doit être exécuté avec sudo (lecture de /var/log).")
        print("   Utilisez : sudo ~/AI-HYBRID-IDS/.venv/bin/python ~/AI-HYBRID-IDS/src/log_monitor.py")
        exit(1)
    init_db()
    try:
        follow_logs()
    except KeyboardInterrupt:
        print("\n[LOG-MONITOR] Arrêt demandé.")
