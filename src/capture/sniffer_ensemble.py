#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sqlite3
import joblib
import pandas as pd
import subprocess
import os
import numpy as np
import re
from datetime import datetime
from collections import defaultdict, Counter
from scapy.all import sniff, IP, TCP, UDP, ICMP

# ============================================================
# PATHS ET PARAMÈTRES
# ============================================================
DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"
MODEL_DIR = "/home/lepentium/AI-HYBRID-IDS/models"
ENCODER_PATH = os.path.join(MODEL_DIR, "encoders.pkl")
FEATURE_LIST_PATH = os.path.join(MODEL_DIR, "feature_list.pkl")

MIN_CONFIDENCE_FOR_LLM = 0.40
LLM_COOLDOWN_SECONDS = 5
CORRELATION_WINDOW = 60
ALERT_THRESHOLD = 2

# ============================================================
# CHARGEMENT DES MODÈLES ET ENCODEURS
# ============================================================
print("[INFO] Chargement des encodeurs...")
encoders = joblib.load(ENCODER_PATH)
le_ip = encoders['ip_encoder']
le_proto = encoders['proto_encoder']
le_flags = encoders['flags_encoder']
le_label = encoders['label_encoder']
print("[INFO] Encodeurs chargés.")

print("[INFO] Chargement de la liste des features...")
feature_info = joblib.load(FEATURE_LIST_PATH)
USE_ENHANCED_FEATURES = feature_info.get('use_enhanced', False)
print(f"[INFO] Features améliorées : {USE_ENHANCED_FEATURES}")

print("[INFO] Chargement des modèles...")
rf_model = joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl"))
xgb_model = joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl"))
lgb_model = joblib.load(os.path.join(MODEL_DIR, "lgb_model.pkl"))
iso_forest = joblib.load(os.path.join(MODEL_DIR, "iso_forest.pkl"))
print("[INFO] Modèles chargés.")

# ============================================================
# CACHES ET ÉTATS
# ============================================================
flow_cache = defaultdict(lambda: {
    'packets': [],
    'syn_count': 0,
    'ack_count': 0,
    'timestamps': [],
    'sizes': [],
    'start_time': time.time(),
    'first_seen': time.time()
})
alert_cache = defaultdict(list)
last_llm_call = {}

# ============================================================
# FONCTION LLM OPTIMISÉE AVEC NETTOYAGE
# ============================================================
def clean_llm_response(text):
    """Nettoie la réponse du LLM : supprime guillemets, retours à la ligne, répétitions."""
    if not text:
        return text
    # Supprimer les guillemets simples et doubles superflus
    text = re.sub(r'["\']', '', text)
    # Supprimer les retours à la ligne et les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    # Si la réponse contient le mot "confiance", on le retire (redondant)
    text = re.sub(r'confiance\s+\d+%', '', text, flags=re.IGNORECASE)
    # Limiter à 150 caractères
    if len(text) > 150:
        text = text[:150] + "..."
    return text

def ask_llm(src_ip, dst_ip, proto, proba, correlation_score):
    prompt = (
        f"1 phrase : Attaque {proto} depuis {src_ip}. Action (ex: bloquer IP)."
    )
    try:
        result = subprocess.run(
            ["ollama", "run", "qwen2:1.5b", prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        response = result.stdout.strip()
        if not response:
            return f"{proto} détecté. Bloquer {src_ip}."
        return response
    except Exception:
        return f"{proto} détecté. Bloquer {src_ip}."

# ============================================================
# PRÉDICTION ENSEMBLE
# ============================================================
def predict_ensemble(features):
    preds = [
        rf_model.predict([features])[0],
        xgb_model.predict([features])[0],
        lgb_model.predict([features])[0]
    ]
    counter = Counter(preds)
    majority = counter.most_common(1)[0][0]
    confidence = counter[majority] / len(preds)
    pred_label = le_label.inverse_transform([majority])[0]
    iso_pred = iso_forest.predict([features])[0]
    is_anomaly = (iso_pred == -1)
    return pred_label, confidence, is_anomaly

# ============================================================
# CORRÉLATION
# ============================================================
def check_correlation(src_ip, confidence):
    now = time.time()
    alert_cache[src_ip] = [(t, c) for t, c in alert_cache[src_ip] if now - t <= CORRELATION_WINDOW]
    alert_cache[src_ip].append((now, confidence))
    count = len(alert_cache[src_ip])
    avg_confidence = np.mean([c for _, c in alert_cache[src_ip]]) if count > 0 else 0
    correlation_score = min(1.0, (count / ALERT_THRESHOLD) * (avg_confidence / MIN_CONFIDENCE_FOR_LLM))
    should_alert = count >= ALERT_THRESHOLD or avg_confidence >= MIN_CONFIDENCE_FOR_LLM
    return correlation_score, should_alert

# ============================================================
# FEATURES COMPORTEMENTALES
# ============================================================
def get_behavioral_features(flow_key, now):
    flow = flow_cache[flow_key]
    if len(flow['sizes']) > 50:
        flow['sizes'] = flow['sizes'][-50:]
        flow['timestamps'] = flow['timestamps'][-50:]
    syn = flow['syn_count']
    ack = flow['ack_count']
    ratio_syn_ack = syn / (ack + 1)
    variance_size = np.var(flow['sizes']) if len(flow['sizes']) > 1 else 0
    recent = [t for t in flow['timestamps'] if now - t <= 5]
    packets_per_sec = len(recent) / 5.0 if recent else 0
    return ratio_syn_ack, variance_size, packets_per_sec

# ============================================================
# BASE DE DONNÉES SQLITE
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            src_ip TEXT,
            dst_ip TEXT,
            protocol TEXT,
            src_port INTEGER,
            dst_port INTEGER,
            packet_size INTEGER,
            ttl INTEGER,
            flags TEXT,
            ml_prediction TEXT,
            ml_confidence REAL,
            anomaly INTEGER,
            correlation_score REAL,
            llm_report TEXT
        )
    ''')
    c.execute("PRAGMA table_info(packets)")
    columns = [col[1] for col in c.fetchall()]
    if 'ml_confidence' not in columns:
        c.execute("ALTER TABLE packets ADD COLUMN ml_confidence REAL")
    if 'anomaly' not in columns:
        c.execute("ALTER TABLE packets ADD COLUMN anomaly INTEGER")
    if 'correlation_score' not in columns:
        c.execute("ALTER TABLE packets ADD COLUMN correlation_score REAL")
    if 'llm_report' not in columns:
        c.execute("ALTER TABLE packets ADD COLUMN llm_report TEXT")
    conn.commit()
    conn.close()
    print("[INFO] Base SQLite initialisée.")

def insert_packet(timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                  packet_size, ttl, flags, ml_prediction, ml_confidence,
                  anomaly, correlation_score=0.0, llm_report=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO packets (
            timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
            packet_size, ttl, flags, ml_prediction, ml_confidence,
            anomaly, correlation_score, llm_report
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
          packet_size, ttl, flags, ml_prediction, ml_confidence,
          anomaly, correlation_score, llm_report))
    conn.commit()
    conn.close()

# ============================================================
# CALLBACK
# ============================================================
def packet_callback(packet):
    if IP not in packet:
        return
    ip = packet[IP]
    src_ip = ip.src
    dst_ip = ip.dst
    size = len(packet)
    ttl = ip.ttl
    timestamp = datetime.now().isoformat()
    now = time.time()

    # Extraction des features
    if TCP in packet:
        proto_name = "TCP"
        src_port = packet[TCP].sport
        dst_port = packet[TCP].dport
        flags = packet[TCP].flags
        if flags & 0x02:
            flow_cache[(src_ip, dst_ip, proto_name, src_port, dst_port)]['syn_count'] += 1
        if flags & 0x10:
            flow_cache[(src_ip, dst_ip, proto_name, src_port, dst_port)]['ack_count'] += 1
    elif UDP in packet:
        proto_name = "UDP"
        src_port = packet[UDP].sport
        dst_port = packet[UDP].dport
        flags = None
    elif ICMP in packet:
        proto_name = "ICMP"
        src_port = 0
        dst_port = 0
        flags = None
    else:
        proto_name = "OTHER"
        src_port = 0
        dst_port = 0
        flags = None

    flow_key = (src_ip, dst_ip, proto_name, src_port, dst_port)
    flow_cache[flow_key]['packets'].append(packet)
    flow_cache[flow_key]['timestamps'].append(now)
    flow_cache[flow_key]['sizes'].append(size)

    if USE_ENHANCED_FEATURES:
        ratio_syn_ack, variance_size, packets_per_sec = get_behavioral_features(flow_key, now)
    else:
        ratio_syn_ack, variance_size, packets_per_sec = 0, 0, 0

    try:
        src_ip_enc = le_ip.transform([src_ip])[0]
        dst_ip_enc = le_ip.transform([dst_ip])[0]
        proto_enc = le_proto.transform([proto_name])[0]
        flags_enc = le_flags.transform([str(flags)])[0]
    except ValueError:
        src_ip_enc = 0
        dst_ip_enc = 0
        proto_enc = 0
        flags_enc = 0

    if USE_ENHANCED_FEATURES:
        features = [src_ip_enc, dst_ip_enc, proto_enc, src_port, dst_port,
                    size, ttl, flags_enc, ratio_syn_ack, variance_size, packets_per_sec]
    else:
        features = [src_ip_enc, dst_ip_enc, proto_enc, src_port, dst_port,
                    size, ttl, flags_enc]

    pred_label, confidence, is_anomaly = predict_ensemble(features)
    correlation_score, should_alert = check_correlation(src_ip, confidence)

    final_is_attack = False
    if pred_label == "attack":
        if is_anomaly or confidence >= MIN_CONFIDENCE_FOR_LLM or should_alert or confidence >= 0.99:
            final_is_attack = True

    print(f"[FEATURES] {src_ip} -> {dst_ip} | PROTO={proto_name} | "
          f"SPORT={src_port} | DPORT={dst_port} | SIZE={size} | TTL={ttl} | "
          f"FLAGS={flags} | ML={pred_label} ({confidence:.2%}) | "
          f"Anomalie={is_anomaly} | Corrélation={correlation_score:.2f}")

    llm_report = ""

    if final_is_attack:
        print(f"🚨 ALERTE CRITIQUE : Attaque depuis {src_ip} vers {dst_ip} "
              f"(confiance={confidence:.2%}, anomalie={is_anomaly}, corrélation={correlation_score:.2f})")
        if src_ip not in last_llm_call or (now - last_llm_call[src_ip]) >= LLM_COOLDOWN_SECONDS:
            print("[LLM] Analyse en cours...")
            llm_report = ask_llm(src_ip, dst_ip, proto_name, confidence, correlation_score)
            print(f"📝 RAPPORT LLM : {llm_report}")
            print("-" * 60)
            last_llm_call[src_ip] = now
        else:
            print(f"[SKIP LLM] Cooldown {LLM_COOLDOWN_SECONDS}s pour {src_ip}")
    else:
        print(f"[INFO] Trafic normal ou confiance faible ({confidence:.2%})")

    insert_packet(
        timestamp, src_ip, dst_ip, proto_name,
        src_port, dst_port, size, ttl, str(flags),
        pred_label, confidence,
        int(is_anomaly), correlation_score, llm_report
    )

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("🛡️ AI-HYBRID-IDS - VERSION CORRIGÉE")
    print("=" * 60)
    print(f"Base SQLite : {DB_PATH}")
    print(f"Interface : wlan0")
    print("Capture illimitée. Ctrl+C pour arrêter.")
    print("=" * 60)

    init_db()

    try:
        sniff(iface="wlan0", prn=packet_callback, store=False)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("Capture interrompue.")
        print("=" * 60)
    except Exception as e:
        print(f"[ERREUR] {e}")

if __name__ == "__main__":
    main()
