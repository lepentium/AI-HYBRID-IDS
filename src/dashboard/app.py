#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# ============================================================
# AUTHENTIFICATION
# ============================================================
try:
    PASSWORD = st.secrets.get("DASHBOARD_PASSWORD")
    if PASSWORD is None:
        raise Exception("Secret manquant")
except Exception:
    PASSWORD = " "
    print("[INFO] Mot de passe par défaut.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Connexion au Dashboard")
    password_input = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    st.stop()

# ============================================================
# CONFIGURATION
# ============================================================
DB_PATH = "/home/lepentium/AI-HYBRID-IDS/data/ids.db"
PAGE_REFRESH = 3

st.set_page_config(page_title="AI HYBRID IDS - Dashboard", layout="wide")
st.title("🛡️ Tableau de bord - IDS Hybride")
st.markdown("Détection d'intrusions avec ensemble de modèles (RF+XGB+LGB+ISO) + LLM")

# ============================================================
# FONCTIONS
# ============================================================
def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("""
            SELECT id, timestamp, src_ip, dst_ip, protocol,
                   src_port, dst_port, packet_size, ttl, flags,
                   ml_prediction, ml_confidence, anomaly, correlation_score, llm_report
            FROM packets ORDER BY id DESC LIMIT 500
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur : {e}")
        return pd.DataFrame()

def get_stats(df):
    total = len(df)
    attacks = len(df[df['ml_prediction'] == 'attack']) if total > 0 else 0
    anomalies = df['anomaly'].sum() if total > 0 else 0
    normal = total - attacks
    return total, attacks, normal, anomalies

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2942/2942792.png", width=80)
    st.title("🛡️ AI HYBRID IDS")
    st.markdown("---")
    if st.button("🔄 Rafraîchir maintenant"):
        st.session_state.refresh_counter = st.session_state.get('refresh_counter', 0) + 1
        st.rerun()
    st.markdown("---")
    st.markdown("**Filtres**")
    protocol_filter = st.multiselect(
        "Protocole",
        options=["TCP", "UDP", "ICMP", "OTHER"],
        default=["TCP", "UDP", "ICMP", "OTHER"],
        key="protocol_filter"
    )
    pred_filter = st.multiselect(
        "Prédiction",
        options=["attack", "normal"],
        default=["attack", "normal"],
        key="pred_filter"
    )
    st.markdown("---")
    st.caption(f"🔄 Auto-refresh toutes les {PAGE_REFRESH}s")

# ============================================================
# PAGE PRINCIPALE
# ============================================================
df = load_data()
if df.empty:
    st.warning("Aucune donnée. Lancez le sniffer.")
    st.stop()

df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')

filtered_df = df.copy()
if protocol_filter:
    filtered_df = filtered_df[filtered_df['protocol'].isin(protocol_filter)]
if pred_filter:
    filtered_df = filtered_df[filtered_df['ml_prediction'].isin(pred_filter)]

total, attacks, normal, anomalies = get_stats(filtered_df)
cols = st.columns(5)
cols[0].metric("📦 Total paquets", total)
cols[1].metric("🚨 Alertes", attacks, delta=f"{attacks/total*100:.1f}%" if total > 0 else "0%")
cols[2].metric("✅ Normaux", normal)
cols[3].metric("⚠️ Anomalies", anomalies)
cols[4].metric("🔒 Confiance moyenne",
              f"{filtered_df['ml_confidence'].mean():.2%}" if total > 0 else "0%")

st.markdown("---")

# ---------- ALERTES ----------
st.subheader("🚨 Dernières alertes")
alerts_df = filtered_df[filtered_df['ml_prediction'] == 'attack'].head(20).copy()
if not alerts_df.empty:
    now = datetime.now()
    alerts_df['datetime'] = pd.to_datetime(alerts_df['timestamp'])
    alerts_df['age_secondes'] = (now - alerts_df['datetime']).dt.total_seconds()
    alerts_df['nouveau'] = alerts_df['age_secondes'] < 30
    alerts_df['icone'] = alerts_df['nouveau'].map({True: '🆕', False: '✅'})
    display_alerts = alerts_df.head(10)[['icone', 'timestamp', 'src_ip', 'dst_ip', 'protocol', 'ml_confidence', 'llm_report']]
    display_alerts['timestamp'] = display_alerts['timestamp'].dt.strftime('%H:%M:%S')
    display_alerts = display_alerts.rename(columns={
        'icone': '', 'timestamp': 'Heure', 'src_ip': 'Source', 'dst_ip': 'Destination',
        'protocol': 'Proto', 'ml_confidence': 'Confiance', 'llm_report': 'Rapport LLM'
    })
    st.dataframe(display_alerts, use_container_width=True, height=300,
                 column_config={"Rapport LLM": st.column_config.TextColumn(width="large")})
    new_count = alerts_df['nouveau'].sum()
    if new_count > 0:
        st.success(f"🆕 {new_count} nouvelle(s) alerte(s) dans les 30 dernières secondes.")
    else:
        st.info("✅ Aucune nouvelle alerte.")
else:
    st.info("Aucune alerte.")

st.markdown("---")

# ---------- FLUX NORMAUX AVEC CONFIANCE ----------
st.subheader("📊 Flux normaux (avec confiance)")
normal_df = filtered_df[filtered_df['ml_prediction'] == 'normal'].head(20).copy()
if not normal_df.empty:
    display_normal = normal_df[['timestamp', 'src_ip', 'dst_ip', 'protocol', 'ml_confidence']]
    display_normal['timestamp'] = display_normal['timestamp'].dt.strftime('%H:%M:%S')
    display_normal = display_normal.rename(columns={
        'timestamp': 'Heure', 'src_ip': 'Source', 'dst_ip': 'Destination',
        'protocol': 'Proto', 'ml_confidence': 'Confiance'
    })
    st.dataframe(display_normal, use_container_width=True, height=250)
else:
    st.info("Aucun flux normal pour le moment.")

st.markdown("---")

# ---------- GRAPHIQUES ----------
counter = st.session_state.get('refresh_counter', 0)

c1, c2 = st.columns(2)
with c1:
    attacks_df = filtered_df[filtered_df['ml_prediction'] == 'attack']
    if not attacks_df.empty:
        ip_counts = attacks_df['src_ip'].value_counts().head(10).reset_index()
        ip_counts.columns = ['IP Source', 'Alertes']
        fig = px.bar(ip_counts, x='IP Source', y='Alertes',
                   title='Top 10 IP sources d\'alertes',
                   color='Alertes', color_continuous_scale='Reds')
        st.plotly_chart(fig, width='stretch', key=f"bar_alertes_{counter}")
    else:
        st.info("Aucune alerte.")

with c2:
    if not filtered_df.empty:
        proto_counts = filtered_df['protocol'].value_counts().reset_index()
        proto_counts.columns = ['Protocole', 'Nombre']
        fig = px.pie(proto_counts, values='Nombre', names='Protocole',
                   title='Répartition par protocole',
                   color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, width='stretch', key=f"pie_protocole_{counter}")

c3, c4 = st.columns(2)
with c3:
    if not filtered_df.empty and len(filtered_df) > 1:
        df_time = filtered_df.set_index('timestamp')
        attacks_time = df_time[df_time['ml_prediction'] == 'attack']
        if not attacks_time.empty:
            attacks_min = attacks_time.resample('1min').size().reset_index()
            attacks_min.columns = ['timestamp', 'nb_alertes']
            fig = px.line(attacks_min, x='timestamp', y='nb_alertes',
                        title='Évolution des alertes (min)',
                        markers=True)
            st.plotly_chart(fig, width='stretch', key=f"line_evolution_{counter}")

with c4:
    anomaly_df = filtered_df[filtered_df['anomaly'] == 1]
    if not anomaly_df.empty:
        ip_anomaly = anomaly_df['src_ip'].value_counts().head(10).reset_index()
        ip_anomaly.columns = ['IP Source', 'Anomalies']
        fig = px.bar(ip_anomaly, x='IP Source', y='Anomalies',
                   title='Top 10 IP avec anomalies',
                   color='Anomalies', color_continuous_scale='Oranges')
        st.plotly_chart(fig, width='stretch', key=f"bar_anomalies_{counter}")

st.caption(f"🔄 Mise à jour dans {PAGE_REFRESH}s")
time.sleep(PAGE_REFRESH)
st.rerun()
