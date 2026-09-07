#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyseur DNS en temps réel pour AI-HYBRID-IDS
Détection de tunnels DNS et exfiltration de données
"""

import time
import sqlite3
from collections import defaultdict
from datetime import datetime
from scapy.all import sniff, IP, UDP, DNS, DNSQR
import math
import os

# ---------- CONFIG ----------
DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"
INTERFACE = "wlan0"
SUSPICIOUS_LENGTH = 30
ENTROPY_THRESHOLD = 4.5
RATE_THRESHOLD = 10  # requêtes par seconde

# Cache pour éviter les doublons (IP + domaine + timestamp)
alert_cache = {}
CACHE_DURATION = 10  # secondes

# Cache pour le taux de requêtes
dns_cache = defaultdict(list)

# ---------- FONCTIONS ----------
def entropy(s):
    if not s:
        return 0
    prob = [float(s.count(c)) / len(s) for c in set(s)]
    return -sum(p * math.log(p, 2) for p in prob)

def insert_alert(src_ip, message, priority=0.8):
    # Vérifier le cache
    key = f"{src_ip}_{message[:50]}"
    if key in alert_cache and (time.time() - alert_cache[key]) < CACHE_DURATION:
        return
    alert_cache[key] = time.time()
    # Nettoyer le cache (supprimer les entrées trop anciennes)
    for k in list(alert_cache.keys()):
        if time.time() - alert_cache[k] > CACHE_DURATION * 2:
            del alert_cache[k]

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        timestamp = datetime.now().isoformat()
        c.execute('''
            INSERT INTO packets (
                timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
                packet_size, ttl, flags, ml_prediction, ml_confidence,
                anomaly, correlation_score, llm_report
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            src_ip,
            "DNS",
            "UDP",
            53, 0, 0, 0, "N/A",
            "attack",
            priority,  # confiance = 0.8
            1,
            0.5,
            f"[DNS] {message}"
        ))
        conn.commit()
        conn.close()
        print(f"[DNS-ALERT] {src_ip} : {message}")
    except Exception as e:
        print(f"[DNS-ERR] {e}")

def analyze_dns(packet):
    if UDP in packet and packet[UDP].dport == 53 and DNS in packet:
        dns = packet[DNS]
        if dns.qr == 0:
            src_ip = packet[IP].src
            for i in range(dns.qdcount):
                qname = dns.qd[i].qname.decode('utf-8').rstrip('.')
                if not qname:
                    continue
                # Longueur excessive
                if len(qname) > SUSPICIOUS_LENGTH:
                    insert_alert(src_ip, f"Nom long ({len(qname)}): {qname}", 0.9)
                # Entropie élevée
                if entropy(qname) > ENTROPY_THRESHOLD:
                    insert_alert(src_ip, f"Entropie {entropy(qname):.2f}: {qname}", 0.85)
                # Taux de requêtes
                now = time.time()
                dns_cache[src_ip].append((now, qname))
                dns_cache[src_ip] = [(t, d) for t, d in dns_cache[src_ip] if now - t <= 2]
                if len(dns_cache[src_ip]) >= RATE_THRESHOLD:
                    insert_alert(src_ip, f"Taux DNS anormal ({len(dns_cache[src_ip])} en 2s)", 0.9)
                    dns_cache[src_ip].clear()

def packet_callback(packet):
    analyze_dns(packet)

def main():
    print("=" * 60)
    print("📡 ANALYSEUR DNS - AI-HYBRID-IDS (version corrigée)")
    print("=" * 60)
    print(f"Interface : {INTERFACE}")
    print("Capture illimitée. Ctrl+C pour arrêter.")
    print("=" * 60)
    try:
        sniff(iface=INTERFACE, prn=packet_callback, store=False)
    except KeyboardInterrupt:
        print("\n[DNS] Arrêt demandé.")

if __name__ == "__main__":
    main()
