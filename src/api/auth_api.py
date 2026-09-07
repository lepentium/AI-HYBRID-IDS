#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, abort
from flask_cors import CORS  # <-- Nouvel import
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # <-- Activer CORS pour toutes les routes

DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"

VALID_TOKENS = {
    "mon_token_secret": "admin",
    "token_public": "lecture"
}

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token not in VALID_TOKENS:
            abort(401, description="Token invalide ou manquant")
        return f(*args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET"])
@token_required
def home():
    return jsonify({"message": "API sécurisée AI-HYBRID-IDS", "timestamp": datetime.now().isoformat()})

@app.route("/alerts", methods=["GET"])
@token_required
def get_alerts():
    limit = request.args.get("limit", default=20, type=int)
    conn = get_db()
    rows = conn.execute("""
        SELECT id, timestamp, src_ip, dst_ip, protocol, ml_prediction, llm_report
        FROM packets
        WHERE ml_prediction='attack'
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/stats", methods=["GET"])
@token_required
def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM packets").fetchone()[0]
    attacks = conn.execute("SELECT COUNT(*) FROM packets WHERE ml_prediction='attack'").fetchone()[0]
    conn.close()
    return jsonify({"total": total, "attacks": attacks, "attack_rate": f"{attacks/total*100:.1f}%" if total else "0%"})

# ---- ROUTE PUBLIQUE (sans token) pour la carte ----
@app.route("/attackers_ips", methods=["GET"])
def get_attackers_ips():
    conn = get_db()
    rows = conn.execute("""
        SELECT src_ip, COUNT(*) as count
        FROM packets
        WHERE ml_prediction='attack'
        GROUP BY src_ip
        ORDER BY count DESC
        LIMIT 20
    """).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
