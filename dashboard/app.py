#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import sqlite3
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# ---------- CONFIG ----------
DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"
PAGE_TITLE = "AI HYBRID IDS - DASHBOARD"
PAGE_ICON = "🛡️"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
st.title(f"{PAGE_ICON} AI HYBRID IDS - Dashboard en temps réel")

# ---------- FONCTIONS ----------
@st.cache_data(ttl=3)
def load_data():
    """Charge les dernières alertes depuis SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT 
                id,
                timestamp,
                src_ip,
                dst_ip,
                protocol,
                src_port,
                dst_port,
                packet_size,
                ml_prediction,
                anomaly,
                llm_report
            FROM packets
            WHERE ml_prediction = 'attack'
            ORDER BY id DESC
            LIMIT 500
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=10)
def load_stats():
    """Charge les statistiques globales."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Nombre total d'alertes
        total = pd.read_sql_query("SELECT COUNT(*) FROM packets WHERE ml_prediction = 'attack'", conn).iloc[0, 0]
        # Nombre d'alertes des dernières 24h
        last_24h = pd.read_sql_query(
            "SELECT COUNT(*) FROM packets WHERE ml_prediction = 'attack' AND datetime(timestamp) > datetime('now', '-1 day')",
            conn
        ).iloc[0, 0]
        # Top 5 IPs attaquantes
        top_ips = pd.read_sql_query(
            "SELECT src_ip, COUNT(*) as count FROM packets WHERE ml_prediction = 'attack' GROUP BY src_ip ORDER BY count DESC LIMIT 5",
            conn
        )
        # Répartition des protocoles
        protocols = pd.read_sql_query(
            "SELECT protocol, COUNT(*) as count FROM packets WHERE ml_prediction = 'attack' GROUP BY protocol ORDER BY count DESC",
            conn
        )
        conn.close()
        return total, last_24h, top_ips, protocols
    except:
        return 0, 0, pd.DataFrame(), pd.DataFrame()

# ---------- SIDEBAR ----------
st.sidebar.title("📊 Filtres")
refresh_rate = st.sidebar.selectbox("🔄 Taux de rafraîchissement", ["1s", "3s", "5s", "10s"], index=1)
refresh_seconds = int(refresh_rate.replace("s", ""))

st.sidebar.markdown("---")
st.sidebar.info("💡 **Conseil** : Laissez le dashboard ouvert pour surveiller les attaques en temps réel.")

# ---------- MAIN ----------
# Statistiques
total, last_24h, top_ips, protocols = load_stats()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🚨 Alertes totales", total)
with col2:
    st.metric("🕒 Alertes (24h)", last_24h)
with col3:
    st.metric("📦 Protocoles", len(protocols) if not protocols.empty else 0)
with col4:
    # Dernière alerte
    df = load_data()
    if not df.empty:
        last_time = df.iloc[0]['timestamp'][:19]
        st.metric("⏱️ Dernière alerte", last_time)
    else:
        st.metric("⏱️ Dernière alerte", "Aucune")

# Graphiques
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌐 Top 5 IPs attaquantes")
    if not top_ips.empty:
        fig = px.bar(top_ips, x='src_ip', y='count', title="", color='count', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée")

with col2:
    st.subheader("📊 Protocoles des attaques")
    if not protocols.empty:
        fig = px.pie(protocols, values='count', names='protocol', title="", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée")

# Table des dernières alertes
st.subheader("📋 Dernières alertes (en direct)")

# Auto-refresh avec st.empty()
placeholder = st.empty()

try:
    while True:
        df = load_data()
        if not df.empty:
            # Nettoyer l'affichage
            display_df = df.copy()
            # Tronquer les rapports LLM trop longs
            if 'llm_report' in display_df.columns:
                display_df['llm_report'] = display_df['llm_report'].apply(lambda x: x[:50] + "..." if len(str(x)) > 50 else x)
            # Renommer les colonnes pour l'affichage
            display_df.columns = ['ID', 'Timestamp', 'Source IP', 'Destination IP', 'Protocole', 
                                  'Port src', 'Port dst', 'Taille', 'Prédiction', 'Anomalie', 'Rapport LLM']
            # Afficher les 10 dernières
            with placeholder.container():
                st.dataframe(display_df.head(20), use_container_width=True)
        else:
            with placeholder.container():
                st.info("🔍 Aucune alerte détectée pour le moment.")

        time.sleep(refresh_seconds)
except KeyboardInterrupt:
    st.stop()
