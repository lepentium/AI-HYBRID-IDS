#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mode apprentissage pour AI-HYBRID-IDS
Extrait les features d'un fichier PCAP et les ajoute au dataset
Permet d'enrichir le modèle avec de nouvelles attaques
"""

import sys
import os
import pandas as pd
from scapy.all import rdpcap, IP, TCP, UDP, ICMP, Raw
from datetime import datetime
import subprocess

# ---------- CONFIG ----------
CSV_PATH = "/home/lepentium/AI-HYBRID-IDS/data/features_labeled.csv"
MODEL_DIR = "/home/lepentium/AI-HYBRID-IDS/models"

def extract_features_from_pcap(pcap_file, label="attack"):
    """
    Extrait les features d'un fichier PCAP.
    label : 'attack' ou 'normal'
    """
    print(f"[INFO] Lecture de {pcap_file}...")
    try:
        packets = rdpcap(pcap_file)
    except Exception as e:
        print(f"[ERREUR] Impossible de lire {pcap_file} : {e}")
        return pd.DataFrame()

    rows = []
    for pkt in packets:
        if IP not in pkt:
            continue
        ip = pkt[IP]
        src_ip = ip.src
        dst_ip = ip.dst
        size = len(pkt)
        ttl = ip.ttl

        if TCP in pkt:
            proto = "TCP"
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
            flags = pkt[TCP].flags
        elif UDP in pkt:
            proto = "UDP"
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
            flags = None
        elif ICMP in pkt:
            proto = "ICMP"
            sport = 0
            dport = 0
            flags = None
        else:
            continue

        rows.append({
            "timestamp": datetime.now().isoformat(),
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "protocol": proto,
            "src_port": sport,
            "dst_port": dport,
            "packet_size": size,
            "ttl": ttl,
            "flags": str(flags) if flags is not None else None,
            "label": label
        })

    return pd.DataFrame(rows)

def add_to_dataset(df):
    """Ajoute les nouvelles données au dataset existant."""
    if os.path.exists(CSV_PATH):
        existing = pd.read_csv(CSV_PATH)
        # Concaténer et dédoublonner (sur base des mêmes features)
        combined = pd.concat([existing, df], ignore_index=True)
        # Supprimer les doublons exacts
        combined = combined.drop_duplicates(subset=['src_ip', 'dst_ip', 'protocol', 'src_port', 'dst_port', 'packet_size', 'ttl'])
        combined.to_csv(CSV_PATH, index=False)
        print(f"[INFO] Dataset enrichi : {len(combined)} lignes (ajout de {len(df) - (len(combined) - len(existing))} nouvelles)")
    else:
        df.to_csv(CSV_PATH, index=False)
        print(f"[INFO] Dataset créé : {len(df)} lignes")

def retrain_models():
    """Relance l'entraînement des modèles."""
    print("[INFO] Ré-entraînement des modèles...")
    script_path = "/home/lepentium/AI-HYBRID-IDS/src/ml/train_ensemble.py"
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("[ERREUR]", result.stderr)

# ---------- MAIN ----------
def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("📚 MODE APPRENTISSAGE - AI-HYBRID-IDS")
        print("=" * 60)
        print("Usage :")
        print("  python learn_from_pcap.py <fichier.pcap> [label]")
        print("  label : 'attack' (défaut) ou 'normal'")
        print("")
        print("Exemple :")
        print("  python learn_from_pcap.py ~/capture_attaque.pcap attack")
        print("  python learn_from_pcap.py ~/trafic_normal.pcap normal")
        sys.exit(1)

    pcap_file = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) > 2 else "attack"

    if not os.path.exists(pcap_file):
        print(f"[ERREUR] Fichier introuvable : {pcap_file}")
        sys.exit(1)

    print("=" * 60)
    print("📚 MODE APPRENTISSAGE - AI-HYBRID-IDS")
    print("=" * 60)
    print(f"Fichier PCAP : {pcap_file}")
    print(f"Label : {label}")
    print("-" * 60)

    # Extraction
    df = extract_features_from_pcap(pcap_file, label)
    if df.empty:
        print("[ERREUR] Aucun paquet IP extrait.")
        sys.exit(1)
    print(f"[INFO] {len(df)} paquets extraits.")

    # Ajout au dataset
    add_to_dataset(df)

    # Ré-entraînement (optionnel)
    reponse = input("Voulez-vous ré-entraîner les modèles maintenant ? (o/n) : ")
    if reponse.lower() == "o":
        retrain_models()
    else:
        print("[INFO] Ré-entraînement reporté. Lancez manuellement :")
        print("  ~/AI-HYBRID-IDS/.venv/bin/python ~/AI-HYBRID-IDS/src/ml/train_ensemble.py")

    print("=" * 60)
    print("✅ Apprentissage terminé.")
    print("=" * 60)

if __name__ == "__main__":
    main()
