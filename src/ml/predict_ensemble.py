#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import joblib
import pandas as pd
import numpy as np
import os

MODEL_DIR = "/home/lepentium/AI-HYBRID-IDS/models"

# Chargement des modèles et des encodeurs
def load_ensemble():
    print("[INFO] Chargement des modèles d'ensemble...")
    models = {
        'rf': joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl")),
        'xgb': joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl")),
        'lgb': joblib.load(os.path.join(MODEL_DIR, "lgb_model.pkl")),
        'iso_forest': joblib.load(os.path.join(MODEL_DIR, "isolation_forest.pkl"))
    }
    encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
    weights = joblib.load(os.path.join(MODEL_DIR, "ensemble_weights.pkl"))
    print("[INFO] Modèles chargés.")
    return models, encoders, weights

def weighted_vote(predictions, weights):
    score = 0
    total_weight = sum(weights.values())
    for model, pred in predictions.items():
        if pred == 'attack':
            score += weights[model]
    if score / total_weight > 0.5:
        return 'attack', score / total_weight
    else:
        return 'normal', 1 - (score / total_weight)

def predict_ensemble(features, models, encoders, weights):
    """
    features : dict avec les champs bruts (src_ip, dst_ip, protocol, src_port, dst_port, packet_size, ttl, flags)
    Retourne : (prediction_finale, confiance, details)
    """
    # Encodage des features
    try:
        src_ip_enc = encoders['ip_encoder'].transform([features['src_ip']])[0]
        dst_ip_enc = encoders['ip_encoder'].transform([features['dst_ip']])[0]
        proto_enc = encoders['proto_encoder'].transform([features['protocol']])[0]
        flags_enc = encoders['flags_encoder'].transform([str(features['flags'])])[0]
    except ValueError:
        # Si une valeur est inconnue, on utilise 0
        src_ip_enc = 0
        dst_ip_enc = 0
        proto_enc = 0
        flags_enc = 0

    # Construction du vecteur de features
    X = [[src_ip_enc, dst_ip_enc, proto_enc,
          features['src_port'], features['dst_port'],
          features['packet_size'], features['ttl'], flags_enc]]

    # Prédictions supervisées
    preds = {}
    preds['rf'] = models['rf'].predict(X)[0]
    preds['xgb'] = models['xgb'].predict(X)[0]
    preds['lgb'] = models['lgb'].predict(X)[0]

    # Prédiction non supervisée (Isolation Forest)
    iso_pred = models['iso_forest'].predict(X)[0]
    # Isolation Forest retourne 1 pour normal, -1 pour anomalie
    iso_attack = (iso_pred == -1)  # True si anomalie

    # Vote pondéré supervisé
    final_pred, confidence = weighted_vote(preds, weights)

    # Intégration de l'Isolation Forest : si l'anomalie est détectée ET que le vote supervisé est normal,
    # on passe en attack avec une confiance modérée.
    if iso_attack and final_pred == 'normal':
        final_pred = 'attack'
        confidence = confidence * 0.7  # on réduit la confiance car c'est une détection non supervisée

    details = {
        'rf': preds['rf'],
        'xgb': preds['xgb'],
        'lgb': preds['lgb'],
        'iso_anomaly': iso_attack,
        'supervised_vote': final_pred,
        'confidence': confidence,
        'weighted_vote': weighted_vote(preds, weights)
    }

    return final_pred, confidence, details
