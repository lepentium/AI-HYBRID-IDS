#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
autonomous_ids.py - Système de détection en temps réel AI-HYBRID-IDS
Avec nettoyage automatique de la base de données au démarrage
"""

import os
import sys
import sqlite3
import shutil
import subprocess
import json
import time
from datetime import datetime
import pandas as pd
import joblib

# ================================================================
# CONFIGURATION
# ================================================================

# Chemins des fichiers
BASE_DIR = "/home/lepentium/AI-HYBRID-IDS"
DB_PATH = os.path.join(BASE_DIR, "data", "ids.db")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Fichiers de logs
FLOW_LOG = os.path.join(LOG_DIR, "live_flows.csv")
ALERT_LOG = os.path.join(LOG_DIR, "alerts_{}.csv")

# Paramètres de capture
INTERFACE = "wlan0"          # Interface réseau à écouter
CAPTURE_INTERVAL = 3         # Secondes entre chaque capture
CONFIDENCE_THRESHOLD = 0.80  # Seuil pour déclencher le LLM

# ================================================================
# FONCTIONS DE GESTION DE LA BASE DE DONNÉES
# ================================================================

def get_db_connection():
    """Établit une connexion à la base de données SQLite"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Crée les tables si elles n'existent pas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            src_ip TEXT,
            src_port INTEGER,
            dst_ip TEXT,
            dst_port INTEGER,
            protocol TEXT,
            attack_type TEXT,
            probability REAL,
            anomaly_score REAL,
            llm_report TEXT,
            status TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            src_ip TEXT,
            dst_ip TEXT,
            src_port INTEGER,
            dst_port INTEGER,
            protocol TEXT,
            duration REAL,
            bytes INTEGER,
            packets INTEGER,
            status TEXT,
            attack_type TEXT,
            probability REAL,
            anomaly_score REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ips (
            ip TEXT PRIMARY KEY,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            attack_count INTEGER DEFAULT 0,
            last_seen TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            message TEXT,
            source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[INFO] ✅ Base de données initialisée.")

def backup_database():
    """Crée une sauvegarde de la base de données avec horodatage"""
    if not os.path.exists(DB_PATH):
        print("[INFO] Aucune base à sauvegarder.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BASE_DIR, "data", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_path = os.path.join(backup_dir, f"ids_backup_{timestamp}.db")
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"[INFO] ✅ Sauvegarde créée : {backup_path}")
    except Exception as e:
        print(f"[ERREUR] Échec de la sauvegarde : {e}")

def clear_database(keep_backup=True):
    """
    Vide complètement la base de données.
    Si keep_backup=True, une sauvegarde est créée avant le nettoyage.
    """
    if not os.path.exists(DB_PATH):
        print("[INFO] Base de données inexistante. Création automatique...")
        init_database()
        return
    
    # Sauvegarde avant nettoyage
    if keep_backup:
        backup_database()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Désactiver les contraintes pour un nettoyage plus rapide
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Liste des tables à vider
        tables = ['alerts', 'flows', 'ips', 'logs']
        for table in tables:
            cursor.execute(f"DELETE FROM {table};")
            print(f"[INFO] Table {table} vidée.")
        
        # Réinitialiser les compteurs d'auto-incrémentation
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('alerts', 'flows', 'ips', 'logs');")
        
        # Réactiver les contraintes
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Compactage de la base pour récupérer l'espace
        cursor.execute("VACUUM;")
        
        conn.commit()
        conn.close()
        print("[INFO] ✅ Base de données entièrement vidée et optimisée.")
        
    except sqlite3.Error as e:
        print(f"[ERREUR] Échec du nettoyage de la base : {e}")
        sys.exit(1)

# ================================================================
# FONCTIONS DE DÉTECTION EN TEMPS RÉEL (À COMPLÉTER)
# ================================================================

def load_models():
    """Charge les modèles entraînés"""
    try:
        rf_model = joblib.load(os.path.join(MODELS_DIR, "rf_model.pkl"))
        xgb_model = joblib.load(os.path.join(MODELS_DIR, "xgb_model.pkl"))
        lgb_model = joblib.load(os.path.join(MODELS_DIR, "lgb_model.pkl"))
        iso_forest = joblib.load(os.path.join(MODELS_DIR, "iso_forest.pkl"))
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        feature_list = joblib.load(os.path.join(MODELS_DIR, "feature_list.pkl"))
        label_encoder = joblib.load(os.path.join(MODELS_DIR, "encoders.pkl"))
        print("[INFO] ✅ Modèles chargés avec succès.")
        return rf_model, xgb_model, lgb_model, iso_forest, scaler, feature_list, label_encoder
    except Exception as e:
        print(f"[ERREUR] Échec du chargement des modèles : {e}")
        sys.exit(1)

def capture_traffic():
    """Capture le trafic réseau avec TShark"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pcap_file = os.path.join(LOG_DIR, f"capture_{timestamp}.pcap")
    
    cmd = [
        "tshark",
        "-i", INTERFACE,
        "-a", f"duration:{CAPTURE_INTERVAL}",
        "-w", pcap_file,
        "-q"
    ]
    
    try:
        subprocess.run(cmd, check=True, timeout=CAPTURE_INTERVAL + 2)
        return pcap_file
    except subprocess.TimeoutExpired:
        print(f"[INFO] Capture terminée après {CAPTURE_INTERVAL}s.")
        return pcap_file
    except Exception as e:
        print(f"[ERREUR] Échec de la capture : {e}")
        return None

def analyze_with_suricata(pcap_file):
    """Analyse le fichier PCAP avec Suricata en mode flow"""
    if not pcap_file or not os.path.exists(pcap_file):
        return None
    
    cmd = [
        "suricata",
        "-r", pcap_file,
        "-c", "/etc/suricata/suricata.yaml",
        "-l", LOG_DIR,
        "--set", "engine-mode=flow"
    ]
    
    try:
        subprocess.run(cmd, check=True, timeout=30)
        # Lire le fichier eve.json
        eve_file = os.path.join(LOG_DIR, "eve.json")
        if os.path.exists(eve_file):
            return parse_eve_file(eve_file)
        return None
    except Exception as e:
        print(f"[ERREUR] Échec de l'analyse Suricata : {e}")
        return None

def parse_eve_file(eve_file):
    """Parse le fichier eve.json et extrait les flux"""
    flows = []
    try:
        with open(eve_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get('event_type') == 'flow':
                        flow = extract_flow_features(data)
                        if flow:
                            flows.append(flow)
                except json.JSONDecodeError:
                    continue
        return flows
    except Exception as e:
        print(f"[ERREUR] Parse de eve.json : {e}")
        return None

def extract_flow_features(data):
    """Extrait les caractéristiques d'un flux"""
    try:
        flow = data.get('flow', {})
        return {
            'timestamp': datetime.now().isoformat(),
            'src_ip': flow.get('src_ip'),
            'dst_ip': flow.get('dest_ip'),
            'src_port': flow.get('src_port'),
            'dst_port': flow.get('dest_port'),
            'protocol': flow.get('proto'),
            'duration': flow.get('dur'),
            'bytes': flow.get('bytes_toserver') + flow.get('bytes_toclient', 0),
            'packets': flow.get('pkts_toserver') + flow.get('pkts_toclient', 0),
            'tcp_flags': flow.get('tcp_flags', '0')
        }
    except Exception:
        return None

def predict(flow_data, models):
    """Effectue la prédiction avec les modèles"""
    rf_model, xgb_model, lgb_model, iso_forest, scaler, feature_list, label_encoder = models
    
    # Construire le vecteur de caractéristiques (à adapter selon votre dataset)
    # Cette partie doit être complétée avec votre extraction réelle
    features = [0] * len(feature_list)
    
    # Normalisation
    features_scaled = scaler.transform([features])
    
    # Prédictions supervisées
    rf_pred = rf_model.predict(features_scaled)[0]
    xgb_pred = xgb_model.predict(features_scaled)[0]
    lgb_pred = lgb_model.predict(features_scaled)[0]
    
    rf_proba = rf_model.predict_proba(features_scaled)[0].max()
    xgb_proba = xgb_model.predict_proba(features_scaled)[0].max()
    lgb_proba = lgb_model.predict_proba(features_scaled)[0].max()
    
    # Vote majoritaire
    votes = [rf_pred, xgb_pred, lgb_pred]
    final_class = max(set(votes), key=votes.count)
    avg_probability = (rf_proba + xgb_proba + lgb_proba) / 3
    
    # Anomalie
    anomaly_score = iso_forest.decision_function(features_scaled)[0]
    is_anomaly = anomaly_score < 0  # Seuil par défaut
    
    # Déterminer le statut
    if avg_probability >= CONFIDENCE_THRESHOLD and is_anomaly:
        status = "critical"
    elif avg_probability >= CONFIDENCE_THRESHOLD or is_anomaly:
        status = "attack"
    else:
        status = "normal"
    
    attack_type = label_encoder.inverse_transform([final_class])[0]
    
    return {
        'status': status,
        'attack_type': attack_type,
        'probability': avg_probability,
        'anomaly_score': anomaly_score,
        'is_anomaly': is_anomaly
    }

def generate_llm_report(alert_data):
    """Génère un rapport LLM pour une alerte critique"""
    # Implémentation de l'appel à Ollama
    prompt = f"""Génère un rapport en français pour cette alerte :
- IP source : {alert_data.get('src_ip')}
- IP destination : {alert_data.get('dst_ip')}
- Type d'attaque : {alert_data.get('attack_type')}
- Probabilité : {alert_data.get('probability'):.2%}
- Score d'anomalie : {alert_data.get('anomaly_score')}

Format de réponse :
1. Nature probable de l'attaque : ...
2. Explication technique : ...
3. Niveau de criticité : ...
4. Recommandation d'action : ..."""
    
    try:
        result = subprocess.run(
            ["ollama", "run", "qwen2:1.5b", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"[ERREUR] Génération du rapport LLM : {e}")
        return "Rapport non disponible."

def save_alert(alert_data, llm_report=None):
    """Sauvegarde une alerte dans la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alerts (
            timestamp, src_ip, src_port, dst_ip, dst_port,
            protocol, attack_type, probability, anomaly_score,
            llm_report, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        alert_data['timestamp'],
        alert_data['src_ip'],
        alert_data.get('src_port'),
        alert_data['dst_ip'],
        alert_data.get('dst_port'),
        alert_data.get('protocol'),
        alert_data['attack_type'],
        alert_data['probability'],
        alert_data['anomaly_score'],
        llm_report,
        alert_data['status']
    ))
    
    conn.commit()
    conn.close()

def main():
    """Fonction principale du sniffer en temps réel"""
    print("=" * 60)
    print("🛡️  AI-HYBRID-IDS - Détection en temps réel")
    print("=" * 60)
    
    # 1. Initialisation de la base
    init_database()
    
    # 2. Nettoyage automatique au démarrage
    print("\n🧹 Nettoyage automatique de la base de données...")
    clear_database(keep_backup=True)
    
    # 3. Chargement des modèles
    print("\n📦 Chargement des modèles...")
    models = load_models()
    
    print(f"\n✅ Système prêt. Surveillance sur {INTERFACE}...")
    print(f"📋 Intervalle de capture : {CAPTURE_INTERVAL}s")
    print("🔄 Appuyez sur Ctrl+C pour arrêter.")
    print("=" * 60)
    
    try:
        while True:
            # Capture du trafic
            pcap_file = capture_traffic()
            if not pcap_file:
                continue
            
            # Analyse Suricata
            flows = analyze_with_suricata(pcap_file)
            if not flows:
                continue
            
            # Traitement de chaque flux
            for flow_data in flows:
                # Prédiction
                prediction = predict(flow_data, models)
                
                # Combinaison des données
                alert_data = {**flow_data, **prediction}
                
                # Si alerte critique, générer rapport LLM
                llm_report = None
                if prediction['status'] == 'critical':
                    print(f"⚠️ ALERTE CRITIQUE ! {alert_data['src_ip']} → {alert_data['dst_ip']}")
                    llm_report = generate_llm_report(alert_data)
                    print(f"📄 Rapport LLM :\n{llm_report}\n")
                
                # Sauvegarde dans la base
                save_alert(alert_data, llm_report)
                
                # Ajout au CSV des flux
                df = pd.DataFrame([alert_data])
                if os.path.exists(FLOW_LOG):
                    df.to_csv(FLOW_LOG, mode='a', header=False, index=False)
                else:
                    df.to_csv(FLOW_LOG, index=False)
            
            # Nettoyer les fichiers temporaires
            if pcap_file and os.path.exists(pcap_file):
                os.remove(pcap_file)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt demandé par l'utilisateur.")
        print("👋 Au revoir !")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERREUR] {e}")
        sys.exit(1)

# ================================================================
# POINT D'ENTRÉE DU SCRIPT
# ================================================================

if __name__ == "__main__":
    # Gestion des arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--clear":
            clear_database(keep_backup=True)
            print("✅ Base vidée. Démarrage de l'IDS...")
        elif sys.argv[1] == "--backup":
            backup_database()
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print("""
Utilisation : python3 autonomous_ids.py [OPTIONS]

Options :
  --clear    Vider automatiquement la base au démarrage
  --backup   Créer une sauvegarde de la base
  --help     Afficher cette aide
            """)
            sys.exit(0)
    
    # Lancer l'IDS
    main()
