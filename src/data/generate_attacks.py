#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import random
import time
from datetime import datetime
from scapy.all import IP, TCP, UDP, ICMP, DNS, DNSQR, sr1, RandIP, RandShort

# ----- Configuration -----
ATTACK_CSV = "/home/lepentium/AI-HYBRID-IDS/data/features_labeled.csv"
NORMAL_COUNT = 50   # nombre de paquets normaux
ATTACK_COUNT = 50   # nombre de paquets par type d'attaque

# Adresses de ton réseau
KALI_IP = "10.155.85.52"
TEL_IP = "10.155.85.120"
EXTERNAL_IPS = ["155.102.195.194", "57.144.39.32", "8.8.8.8"]

# ----- Utilitaires -----
def now():
    return datetime.now().isoformat()

def write_features(features, label):
    """Écrit une ligne de features avec label."""
    return [
        now(),
        features[0], features[1], features[2],   # src_ip, dst_ip, protocol
        features[3], features[4],                # src_port, dst_port
        features[5], features[6],                # packet_size, ttl
        features[7],                             # flags
        label                                    # label
    ]

# ----- 1. Scan de ports (TCP SYN) -----
def generate_port_scan(n=ATTACK_COUNT):
    features = []
    for _ in range(n):
        dst_ip = random.choice(EXTERNAL_IPS + [KALI_IP])
        dst_port = random.choice([22, 80, 443, 3389, 8080])
        src_port = random.randint(1024, 65535)
        pkt = IP(src=KALI_IP, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags="S")
        features.append([
            KALI_IP, dst_ip, "TCP",
            src_port, dst_port,
            len(pkt), 64,
            "S"          # flag SYN
        ])
        time.sleep(0.02)
    return [write_features(f, "attack") for f in features]

# ----- 2. Force brute (simulée SSH) -----
def generate_bruteforce(n=ATTACK_COUNT):
    features = []
    for _ in range(n):
        dst_ip = TEL_IP
        dst_port = 22
        src_port = random.randint(1024, 65535)
        pkt = IP(src=KALI_IP, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags="A")
        features.append([
            KALI_IP, dst_ip, "TCP",
            src_port, dst_port,
            len(pkt), 64,
            "A"          # flag ACK
        ])
        time.sleep(0.01)
    return [write_features(f, "attack") for f in features]

# ----- 3. SYN flood -----
def generate_syn_flood(n=ATTACK_COUNT):
    features = []
    for _ in range(n):
        dst_ip = KALI_IP
        dst_port = random.choice([80, 443, 22])
        src_ip = str(RandIP())
        src_port = random.randint(1024, 65535)
        pkt = IP(src=src_ip, dst=dst_ip)/TCP(sport=src_port, dport=dst_port, flags="S")
        features.append([
            src_ip, dst_ip, "TCP",
            src_port, dst_port,
            len(pkt), random.randint(64, 128),
            "S"
        ])
        time.sleep(0.001)
    return [write_features(f, "attack") for f in features]

# ----- 4. UDP flood -----
def generate_udp_flood(n=ATTACK_COUNT):
    features = []
    for _ in range(n):
        dst_ip = KALI_IP
        dst_port = random.choice([53, 67, 123, 161])
        src_ip = str(RandIP())
        src_port = random.randint(1024, 65535)
        pkt = IP(src=src_ip, dst=dst_ip)/UDP(sport=src_port, dport=dst_port)/b"PAYLOAD"
        features.append([
            src_ip, dst_ip, "UDP",
            src_port, dst_port,
            len(pkt), random.randint(64, 128),
            None
        ])
        time.sleep(0.001)
    return [write_features(f, "attack") for f in features]

# ----- 5. Reconnaissance ICMP (ping sweep) -----
def generate_ping_sweep(n=ATTACK_COUNT):
    features = []
    for _ in range(n):
        dst_ip = str(RandIP())
        pkt = IP(src=KALI_IP, dst=dst_ip)/ICMP()
        features.append([
            KALI_IP, dst_ip, "ICMP",
            0, 0,
            len(pkt), 64,
            None
        ])
        time.sleep(0.01)
    return [write_features(f, "attack") for f in features]

# ----- 6. Tunneling DNS (requêtes anormales) -----
def generate_dns_tunnel(n=ATTACK_COUNT):
    features = []
    for _ in range(n):
        dst_ip = random.choice(["8.8.8.8", "1.1.1.1"])
        src_port = random.randint(1024, 65535)
        dst_port = 53
        # Nom de domaine long et aléatoire (tunneling)
        subdomain = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=20))
        query = f"{subdomain}.exfil.com"
        pkt = IP(src=KALI_IP, dst=dst_ip)/UDP(sport=src_port, dport=53)/DNS(rd=1, qd=DNSQR(qname=query))
        features.append([
            KALI_IP, dst_ip, "UDP",
            src_port, dst_port,
            len(pkt), 64,
            None
        ])
        time.sleep(0.02)
    return [write_features(f, "attack") for f in features]

# ----- 7. Trafic normal -----
def generate_normal_traffic(n=NORMAL_COUNT):
    features = []
    ips = [KALI_IP, TEL_IP] + EXTERNAL_IPS
    protocols = ["TCP", "UDP", "ICMP"]
    for _ in range(n):
        src = random.choice(ips)
        dst = random.choice([ip for ip in ips if ip != src])
        proto = random.choice(protocols)
        if proto == "TCP":
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([80, 443, 53, 22])
            flags = random.choice(["A", "PA", "F"])
        elif proto == "UDP":
            src_port = random.randint(1024, 65535)
            dst_port = random.choice([53, 67, 68, 123])
            flags = None
        else:
            src_port = 0
            dst_port = 0
            flags = None
        features.append([
            src, dst, proto,
            src_port, dst_port,
            random.randint(60, 1500),
            random.randint(64, 128),
            flags
        ])
        time.sleep(0.1)
    return [write_features(f, "normal") for f in features]

# ----- Main -----
def main():
    print("=" * 60)
    print("GÉNÉRATION DE DONNÉES D'ATTAQUES VARIÉES")
    print("=" * 60)

    all_features = []

    # Générer chaque type d'attaque
    print("  [1/7] Scan de ports...")
    all_features.extend(generate_port_scan())
    print("  [2/7] Force brute SSH...")
    all_features.extend(generate_bruteforce())
    print("  [3/7] SYN flood...")
    all_features.extend(generate_syn_flood())
    print("  [4/7] UDP flood...")
    all_features.extend(generate_udp_flood())
    print("  [5/7] Ping sweep ICMP...")
    all_features.extend(generate_ping_sweep())
    print("  [6/7] Tunneling DNS...")
    all_features.extend(generate_dns_tunnel())
    print("  [7/7] Trafic normal...")
    all_features.extend(generate_normal_traffic())

    # Mélanger
    random.shuffle(all_features)

    # Écrire dans le CSV
    with open(ATTACK_CSV, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp", "src_ip", "dst_ip", "protocol",
            "src_port", "dst_port", "packet_size", "ttl", "flags", "label"
        ])
        writer.writerows(all_features)

    print("=" * 60)
    print(f"✅ {len(all_features)} lignes générées dans {ATTACK_CSV}")
    print("=" * 60)

if __name__ == "__main__":
    main()
