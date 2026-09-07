#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import xgboost as xgb
import lightgbm as lgb

# ---------- PATHS ----------
CSV_PATH = "/home/lepentium/AI-HYBRID-IDS/data/features_labeled.csv"
MODEL_DIR = "/home/lepentium/AI-HYBRID-IDS/models"

# ---------- CONFIG ----------
USE_ENHANCED_FEATURES = True   # Activer les nouvelles features

# ---------- CHARGEMENT ----------
print("[INFO] Chargement des données...")
df = pd.read_csv(CSV_PATH)

# Encoder les variables catégorielles
le_ip = LabelEncoder()
le_proto = LabelEncoder()
le_flags = LabelEncoder()
le_label = LabelEncoder()

df['src_ip_enc'] = le_ip.fit_transform(df['src_ip'])
df['dst_ip_enc'] = le_ip.fit_transform(df['dst_ip'])
df['proto_enc'] = le_proto.fit_transform(df['protocol'])
df['flags_enc'] = le_flags.fit_transform(df['flags'].fillna('None'))
df['label_enc'] = le_label.fit_transform(df['label'])  # attack=1, normal=0

# Sauvegarde des encodeurs
encoders = {
    'ip_encoder': le_ip,
    'proto_encoder': le_proto,
    'flags_encoder': le_flags,
    'label_encoder': le_label
}
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(encoders, os.path.join(MODEL_DIR, "encoders.pkl"))
print("[INFO] Encodeurs sauvegardés.")

# ---------- FEATURES DE BASE ----------
base_features = ['src_ip_enc', 'dst_ip_enc', 'proto_enc',
                 'src_port', 'dst_port', 'packet_size', 'ttl', 'flags_enc']

# ---------- AJOUT DE FEATURES COMPORTEMENTALES (simulées pour l'entraînement) ----------
if USE_ENHANCED_FEATURES:
    print("[INFO] Génération de features comportementales (simulées)...")
    # On crée des features synthétiques basées sur les données existantes
    # Pour chaque ligne, on génère des valeurs cohérentes
    np.random.seed(42)
    n = len(df)
    # Ratio SYN/ACK (simulé : plus élevé pour les attaques)
    df['ratio_syn_ack'] = np.random.uniform(0.1, 0.9, n)
    # Variance de taille (simulée)
    df['variance_size'] = np.random.uniform(10, 200, n)
    # Paquets par seconde (simulé)
    df['packets_per_sec'] = np.random.uniform(1, 100, n)
    # Pour les attaques, on augmente artificiellement certaines valeurs
    attack_mask = df['label'] == 'attack'
    df.loc[attack_mask, 'ratio_syn_ack'] += np.random.uniform(0.2, 0.5, attack_mask.sum())
    df.loc[attack_mask, 'packets_per_sec'] += np.random.uniform(10, 50, attack_mask.sum())

    enhanced_features = base_features + ['ratio_syn_ack', 'variance_size', 'packets_per_sec']
else:
    enhanced_features = base_features

print(f"[INFO] Nombre de features : {len(enhanced_features)}")
print(f"[INFO] Features utilisées : {enhanced_features}")

X = df[enhanced_features]
y = df['label_enc']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---------- MODÈLES SUPERVISÉS ----------
print("[INFO] Entraînement des modèles supervisés...")

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
print(f"✅ Random Forest accuracy: {accuracy_score(y_test, rf.predict(X_test)):.2%}")

xgb_model = xgb.XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='logloss')
xgb_model.fit(X_train, y_train)
print(f"✅ XGBoost accuracy: {accuracy_score(y_test, xgb_model.predict(X_test)):.2%}")

lgb_model = lgb.LGBMClassifier(n_estimators=100, random_state=42)
lgb_model.fit(X_train, y_train)
print(f"✅ LightGBM accuracy: {accuracy_score(y_test, lgb_model.predict(X_test)):.2%}")

# ---------- MODÈLE NON SUPERVISÉ (Isolation Forest) ----------
print("[INFO] Entraînement d'Isolation Forest...")
iso_forest = IsolationForest(contamination=0.1, random_state=42)
iso_forest.fit(X)  # sur toutes les données

# ---------- SAUVEGARDE ----------
joblib.dump(rf, os.path.join(MODEL_DIR, "rf_model.pkl"))
joblib.dump(xgb_model, os.path.join(MODEL_DIR, "xgb_model.pkl"))
joblib.dump(lgb_model, os.path.join(MODEL_DIR, "lgb_model.pkl"))
joblib.dump(iso_forest, os.path.join(MODEL_DIR, "iso_forest.pkl"))

# Sauvegarde de la liste des features pour le sniffer
feature_list = {
    'features': enhanced_features,
    'use_enhanced': USE_ENHANCED_FEATURES
}
joblib.dump(feature_list, os.path.join(MODEL_DIR, "feature_list.pkl"))

print(f"\n✅ Modèles sauvegardés dans {MODEL_DIR}")
print("   - rf_model.pkl (Random Forest)")
print("   - xgb_model.pkl (XGBoost)")
print("   - lgb_model.pkl (LightGBM)")
print("   - iso_forest.pkl (Isolation Forest)")
print("   - feature_list.pkl (liste des features)")
