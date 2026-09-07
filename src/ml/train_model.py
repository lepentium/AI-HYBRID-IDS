#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

CSV_PATH = "/home/lepentium/AI-HYBRID-IDS/data/features_labeled.csv"
MODEL_PATH = "/home/lepentium/AI-HYBRID-IDS/models/rf_model.pkl"
ENCODER_PATH = "/home/lepentium/AI-HYBRID-IDS/models/encoders.pkl"

def train():
    df = pd.read_csv(CSV_PATH)
    
    le_ip = LabelEncoder()
    le_proto = LabelEncoder()
    le_flags = LabelEncoder()
    
    df['src_ip_enc'] = le_ip.fit_transform(df['src_ip'])
    df['dst_ip_enc'] = le_ip.fit_transform(df['dst_ip'])
    df['proto_enc'] = le_proto.fit_transform(df['protocol'])
    df['flags_enc'] = le_flags.fit_transform(df['flags'].fillna('None'))
    
    features = ['src_ip_enc', 'dst_ip_enc', 'proto_enc', 
                'src_port', 'dst_port', 'packet_size', 'ttl', 'flags_enc']
    X = df[features]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"✅ Précision du modèle : {accuracy:.2%}")
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump({
        'ip_encoder': le_ip,
        'proto_encoder': le_proto,
        'flags_encoder': le_flags
    }, ENCODER_PATH)
    
    print(f"✅ Modèle sauvegardé dans {MODEL_PATH}")
    print(f"✅ Encodeurs sauvegardés dans {ENCODER_PATH}")

if __name__ == "__main__":
    train()
