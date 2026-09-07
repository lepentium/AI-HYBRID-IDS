#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API REST pour AI-HYBRID-IDS
Expose les alertes, statistiques et données en JSON
"""

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"

# ---------- FONCTIONS ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------- ROUTES ----------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "AI-HYBRID-IDS API",
        "version": "1.0",
        "endpoints": {
            "/alerts": "Dernières alertes (GET, limit=20)",
            "/stats": "Statistiques globales (GET)",
            "/attackers": "Top 10 IPs attaquantes (GET)",
            "/anomalies": "Dernières anomalies (GET, limit=20)",
            "/packets": "Derniers paquets (GET, limit=50)"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route("/alerts", methods=["GET"])
def get_alerts():
    limit = request.args.get("limit", default=20, type=int)
    if limit > 100:
        limit = 100
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
               ml_prediction, anomaly, correlation_score, llm_report
        FROM packets
        WHERE ml_prediction = 'attack'
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify({
        "count": len(rows),
        "data": [dict(row) for row in rows]
    })

@app.route("/stats", methods=["GET"])
def get_stats():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM packets").fetchone()[0]
    attacks = conn.execute("SELECT COUNT(*) FROM packets WHERE ml_prediction='attack'").fetchone()[0]
    anomalies = conn.execute("SELECT COUNT(*) FROM packets WHERE anomaly=1").fetchone()[0]
    normal = total - attacks
    conn.close()
    return jsonify({
        "total_packets": total,
        "total_attacks": attacks,
        "total_normal": normal,
        "total_anomalies": anomalies,
        "attack_rate": f"{attacks/total*100:.1f}%" if total > 0 else "0%",
        "anomaly_rate": f"{anomalies/total*100:.1f}%" if total > 0 else "0%"
    })

@app.route("/attackers", methods=["GET"])
def get_attackers():
    limit = request.args.get("limit", default=10, type=int)
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT src_ip, COUNT(*) as count, 
               MIN(timestamp) as first_seen,
               MAX(timestamp) as last_seen
        FROM packets
        WHERE ml_prediction = 'attack'
        GROUP BY src_ip
        ORDER BY count DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify({
        "count": len(rows),
        "data": [dict(row) for row in rows]
    })

@app.route("/anomalies", methods=["GET"])
def get_anomalies():
    limit = request.args.get("limit", default=20, type=int)
    if limit > 100:
        limit = 100
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
               ml_prediction, anomaly, correlation_score, llm_report
        FROM packets
        WHERE anomaly = 1
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify({
        "count": len(rows),
        "data": [dict(row) for row in rows]
    })

@app.route("/packets", methods=["GET"])
def get_packets():
    limit = request.args.get("limit", default=50, type=int)
    if limit > 200:
        limit = 200
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, timestamp, src_ip, dst_ip, protocol, src_port, dst_port,
               packet_size, ttl, ml_prediction, anomaly, correlation_score
        FROM packets
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify({
        "count": len(rows),
        "data": [dict(row) for row in rows]
    })

@app.route("/search", methods=["GET"])
def search():
    ip = request.args.get("ip", "")
    if not ip:
        return jsonify({"error": "Paramètre 'ip' requis"}), 400
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, timestamp, src_ip, dst_ip, protocol, ml_prediction, anomaly, llm_report
        FROM packets
        WHERE src_ip LIKE ? OR dst_ip LIKE ?
        ORDER BY id DESC
        LIMIT 50
    """, (f"%{ip}%", f"%{ip}%")).fetchall()
    conn.close()
    return jsonify({
        "query": ip,
        "count": len(rows),
        "data": [dict(row) for row in rows]
    })

# ---------- MAIN ----------
if __name__ == "__main__":
    print("=" * 60)
    print("📡 AI-HYBRID-IDS API REST")
    print("=" * 60)
    print("Démarrage du serveur Flask sur 0.0.0.0:5000")
    print("Endpoints disponibles :")
    print("  GET /           - Information générale")
    print("  GET /alerts     - Dernières alertes")
    print("  GET /stats      - Statistiques")
    print("  GET /attackers  - Top IPs attaquantes")
    print("  GET /anomalies  - Dernières anomalies")
    print("  GET /packets    - Derniers paquets")
    print("  GET /search?ip=X - Recherche par IP")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=False)
