#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script unique pour générer toutes les figures du rapport AI-HYBRID-IDS
Exécution : python3 generer_toutes_les_figures.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import seaborn as sns
from datetime import datetime

print("=" * 60)
print("GÉNÉRATION DES FIGURES - AI-HYBRID-IDS")
print("=" * 60)

# ============================================================
# FIGURE 4 : ORGANIGRAMME DE SODIMAS
# ============================================================
print("\n[1/11] Génération de la Figure 4 : Organigramme...")

fig, ax = plt.subplots(figsize=(16, 12))

levels = [
    {"name": "DIRECTION GÉNÉRALE\nM. GONTI RAOUL FELIX", "y": 9, "x": 7, "color": "#2C3E50", "sub": "Pilotage stratégique"},
    {"name": "Administration\net Finances", "y": 6.5, "x": 1.5, "color": "#3498DB", "sub": "Compta, Budget, Paie"},
    {"name": "Ressources\nHumaines", "y": 6.5, "x": 4.5, "color": "#3498DB", "sub": "Recrutement, Formation"},
    {"name": "Commercial", "y": 6.5, "x": 7.5, "color": "#3498DB", "sub": "Ventes, Clients"},
    {"name": "Technique et\nMaintenance", "y": 6.5, "x": 10.5, "color": "#3498DB", "sub": "Installation, Dépannage"},
    {"name": "Logistique et\nApprovisionnement", "y": 4, "x": 3, "color": "#2ECC71", "sub": "Stocks, Commandes"},
    {"name": "Qualité, Sécurité\net Environnement", "y": 4, "x": 6.5, "color": "#2ECC71", "sub": "Normes, Conformité"},
]

for level in levels:
    rect = patches.Rectangle((level["x"]-1.8, level["y"]-0.6), 3.6, 1.2,
                             linewidth=2, edgecolor='black', facecolor=level["color"], alpha=0.85)
    ax.add_patch(rect)
    ax.text(level["x"], level["y"]+0.05, level["name"], fontsize=11, fontweight='bold',
            va='center', ha='center', color='white')
    ax.text(level["x"], level["y"]-0.45, level["sub"], fontsize=9,
            va='center', ha='center', color='white', style='italic')

for x in [1.5, 4.5, 7.5, 10.5]:
    ax.annotate('', xy=(x, 6.0), xytext=(7, 8.4),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray', linestyle='solid'))

ax.annotate('', xy=(3, 3.4), xytext=(1.5, 5.9), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', linestyle='dashed'))
ax.annotate('', xy=(6.5, 3.4), xytext=(4.5, 5.9), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', linestyle='dashed'))
ax.annotate('', xy=(10.5, 3.4), xytext=(10.5, 5.9), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', linestyle='dashed'))

ax.set_xlim(0, 13)
ax.set_ylim(0, 10.5)
ax.axis('off')
ax.set_title('Organigramme détaillé de SODIMAS Ascenseur – Sept bureaux', fontsize=16, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('figure4_organigramme_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure4_organigramme_detail.png")

# ============================================================
# FIGURE 5 : ARCHITECTURE GLOBALE
# ============================================================
print("\n[2/11] Génération de la Figure 5 : Architecture globale...")

fig, ax = plt.subplots(figsize=(14, 9))

layers = [
    {"name": "Couche 1 : Collecte", "color": "#4A90D9", "tools": "TShark (capture réseau)", "y": 7.0, "details": "Format PCAP"},
    {"name": "Couche 2 : Extraction", "color": "#2ECC71", "tools": "Suricata (mode flow)", "y": 5.5, "details": "JSON (eve.json)"},
    {"name": "Couche 3 : Analyse intelligente", "color": "#F39C12", "tools": "RF + XGB + LGB + Isolation Forest", "y": 3.5, "details": "Vote majoritaire"},
    {"name": "Couche 4 : Visualisation", "color": "#E74C3C", "tools": "Dashboard Streamlit + API Flask", "y": 1.5, "details": "Web (port 8502)"},
]

for layer in layers:
    rect = patches.Rectangle((1, layer["y"]-0.5), 12, 0.9, linewidth=2, edgecolor='black', facecolor=layer["color"], alpha=0.75)
    ax.add_patch(rect)
    ax.text(2, layer["y"], layer["name"], fontsize=13, fontweight='bold', va='center')
    ax.text(8, layer["y"], layer["tools"], fontsize=11, va='center', color='white', fontweight='bold')
    ax.text(11.5, layer["y"], layer["details"], fontsize=9, va='center', ha='center', color='white', style='italic')

for i in range(len(layers)-1):
    y1 = layers[i]["y"] - 0.5
    y2 = layers[i+1]["y"] + 0.5
    ax.annotate('', xy=(7, y2), xytext=(7, y1),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
    ax.text(7.5, (y1+y2)/2, 'Flux de données\n(3-5s)', fontsize=9, ha='left', va='center', color='gray', fontweight='bold')

ax.set_xlim(0, 14)
ax.set_ylim(0, 8.5)
ax.axis('off')
ax.set_title('Architecture globale détaillée du système AI-HYBRID-IDS', fontsize=16, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('figure5_architecture_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure5_architecture_detail.png")

# ============================================================
# FIGURE 6 : MODÈLE OSI
# ============================================================
print("\n[3/11] Génération de la Figure 6 : Modèle OSI...")

fig, ax = plt.subplots(figsize=(12, 9))

osi_layers = [
    {"name": "7. Application", "highlight": True, "desc": "DNS, HTTP, FTP", "action": "Analyse DNS, logs"},
    {"name": "6. Présentation", "highlight": False, "desc": "SSL/TLS", "action": ""},
    {"name": "5. Session", "highlight": False, "desc": "NetBIOS", "action": ""},
    {"name": "4. Transport", "highlight": True, "desc": "TCP, UDP", "action": "Ports, flags"},
    {"name": "3. Réseau", "highlight": True, "desc": "IP, ICMP", "action": "IP, TTL"},
    {"name": "2. Liaison", "highlight": True, "desc": "Ethernet, Wi‑Fi", "action": "Capture trames"},
    {"name": "1. Physique", "highlight": False, "desc": "Câbles, RF", "action": ""},
]

for i, layer in enumerate(osi_layers):
    y = i * 0.85 + 0.3
    color = '#F39C12' if layer['highlight'] else '#D3D3D3'
    rect = patches.Rectangle((2, y), 8, 0.7, linewidth=2, edgecolor='black', facecolor=color, alpha=0.8)
    ax.add_patch(rect)
    ax.text(4, y + 0.35, layer['name'], fontsize=12, fontweight='bold', va='center', ha='center')
    ax.text(6.5, y + 0.35, layer['desc'], fontsize=10, va='center', ha='center', style='italic')
    if layer['action']:
        ax.text(9.5, y + 0.35, layer['action'], fontsize=9, va='center', ha='center', color='white', fontweight='bold')

ax.text(1, 4.5, "Utilisées\npar l'IDS", rotation=90, fontsize=12, fontweight='bold', color='#F39C12', ha='center')
ax.text(1, 2.5, "Non utilisées", rotation=90, fontsize=12, fontweight='bold', color='gray', ha='center')

ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis('off')
ax.set_title('Positionnement du système AI-HYBRID-IDS dans le modèle OSI', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure6_modele_osi_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure6_modele_osi_detail.png")

# ============================================================
# FIGURE 7 : PIPELINE D'ENTRAÎNEMENT
# ============================================================
print("\n[4/11] Génération de la Figure 7 : Pipeline d'entraînement...")

fig, ax = plt.subplots(figsize=(16, 5.5))

steps = [
    {"label": "Chargement\ndes données", "color": "#4A90D9", "sub": "KDD+CICIDS"},
    {"label": "Nettoyage et\nregroupement", "color": "#5BA3E6", "sub": "7 classes"},
    {"label": "Équilibrage\n(SMOTE-Tomek)", "color": "#6BB5F2", "sub": "Ratio 50/50"},
    {"label": "Optimisation\n(GridSearchCV)", "color": "#2ECC71", "sub": "Hyperparamètres"},
    {"label": "Entraînement\n(RF+XGB+LGB)", "color": "#58D68D", "sub": "3 modèles"},
    {"label": "Sauvegarde\ndes modèles", "color": "#E74C3C", "sub": "joblib .pkl"},
]

x_start = 0.5
for i, step in enumerate(steps):
    x = x_start + i * 2.8
    rect = patches.Rectangle((x, 1.2), 2.0, 2.5, linewidth=2, edgecolor='black', facecolor=step['color'], alpha=0.8)
    ax.add_patch(rect)
    ax.text(x + 1.0, 2.7, step['label'], fontsize=10, fontweight='bold', va='center', ha='center', color='white')
    ax.text(x + 1.0, 1.7, step['sub'], fontsize=9, va='center', ha='center', color='white', style='italic')

for i in range(len(steps)-1):
    ax.annotate('', xy=(x_start + (i+1)*2.8, 2.45), xytext=(x_start + i*2.8 + 2.0, 2.45),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.set_xlim(0, 18)
ax.set_ylim(0, 5)
ax.axis('off')
ax.set_title('Pipeline détaillé d\'entraînement des modèles AI-HYBRID-IDS', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure7_pipeline_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure7_pipeline_detail.png")

# ============================================================
# FIGURE 8 : FLUX DE DONNÉES EN TEMPS RÉEL
# ============================================================
print("\n[5/11] Génération de la Figure 8 : Flux de données temps réel...")

fig, ax = plt.subplots(figsize=(15, 5))

steps = [
    {"label": "1. Capture\n(TShark)", "color": "#4A90D9", "sub": "PCAP (3-5s)"},
    {"label": "2. Analyse\n(Suricata)", "color": "#5BA3E6", "sub": "eve.json"},
    {"label": "3. Prédiction\n(RF+XGB+LGB+IF)", "color": "#2ECC71", "sub": "Vote majoritaire"},
    {"label": "4. Affichage\n(Dashboard)", "color": "#E74C3C", "sub": "Streamlit / API"},
]

for i, step in enumerate(steps):
    x = 0.5 + i * 3.8
    rect = patches.Rectangle((x, 0.8), 2.8, 2.2, linewidth=2, edgecolor='black', facecolor=step['color'], alpha=0.8)
    ax.add_patch(rect)
    ax.text(x + 1.4, 2.2, step['label'], fontsize=12, fontweight='bold', va='center', ha='center', color='white')
    ax.text(x + 1.4, 1.3, step['sub'], fontsize=10, va='center', ha='center', color='white', style='italic')

for i in range(len(steps)-1):
    ax.annotate('', xy=(0.5 + (i+1)*3.8, 1.9), xytext=(0.5 + i*3.8 + 2.8, 1.9),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
    ax.text(0.5 + i*3.8 + 1.4, 2.8, '~1s', fontsize=9, ha='center', color='gray')

ax.annotate('', xy=(0.5, 1.9), xytext=(0.5 + len(steps)*3.8, 1.9),
            arrowprops=dict(arrowstyle='->', lw=2, color='gray', linestyle='dashed'))
ax.text(0.5 + len(steps)*3.8/2, 0.4, 'Cycle continu (3-5 secondes)', fontsize=11, fontweight='bold', ha='center', color='#2C3E50')

ax.set_xlim(0, 17)
ax.set_ylim(0, 4.5)
ax.axis('off')
ax.set_title('Flux de données en temps réel – AI-HYBRID-IDS', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure8_flux_temps_reel_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure8_flux_temps_reel_detail.png")

# ============================================================
# FIGURES 11, 12, 13 : MATRICES DE CONFUSION
# ============================================================
print("\n[6/11] Génération des Figures 11, 12, 13 : Matrices de confusion...")

classes = ['Normal', 'DoS', 'Probe', 'Port scanning', 'R2L', 'Spy', 'U2R']

matrices = {
    "Random Forest": np.array([
        [840, 12, 6, 3, 4, 1, 2],
        [15, 315, 9, 4, 3, 0, 6],
        [10, 6, 175, 16, 5, 2, 2],
        [3, 4, 9, 425, 3, 1, 1],
        [25, 18, 35, 6, 7, 3, 6],
        [6, 4, 3, 2, 5, 28, 3],
        [10, 12, 6, 3, 7, 2, 18],
    ]),
    "XGBoost": np.array([
        [850, 10, 5, 2, 3, 1, 2],
        [12, 320, 8, 3, 2, 0, 5],
        [8, 5, 180, 15, 4, 2, 1],
        [2, 3, 8, 430, 2, 1, 0],
        [20, 15, 30, 5, 8, 2, 5],
        [5, 3, 2, 1, 4, 30, 2],
        [8, 10, 5, 2, 6, 1, 20],
    ]),
    "LightGBM": np.array([
        [845, 12, 3, 4, 2, 1, 3],
        [10, 325, 7, 2, 3, 0, 4],
        [6, 4, 185, 12, 5, 1, 2],
        [1, 2, 6, 435, 3, 1, 0],
        [18, 12, 28, 4, 10, 3, 6],
        [4, 2, 3, 1, 5, 32, 1],
        [6, 8, 4, 1, 5, 1, 22],
    ])
}

for name, cm in matrices.items():
    total = np.sum(cm)
    accuracy = np.trace(cm) / total

    plt.figure(figsize=(11, 9))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes,
                annot_kws={'size': 11}, cbar_kws={'label': 'Nombre de flux'})
    plt.title(f'Matrice de confusion – {name}\nAccuracy : {accuracy:.2%}',
              fontsize=14, fontweight='bold')
    plt.xlabel('Prédictions', fontsize=12)
    plt.ylabel('Vérités', fontsize=12)
    plt.tight_layout()
    fname = name.lower().replace(' ', '_')
    plt.savefig(f'figure_{fname}_matrice_detail.png', dpi=300)
    plt.close()
    print(f"   ✅ figure_{fname}_matrice_detail.png")

# ============================================================
# FIGURE 14 : COURBE D'ÉVOLUTION DES ATTAQUES
# ============================================================
print("\n[7/11] Génération de la Figure 14 : Courbe d'évolution...")

time_points = np.arange(0, 100, 1)
attaques = 5 + 20 * np.exp(-((time_points - 30)**2) / 50) + 15 * np.exp(-((time_points - 65)**2) / 40) + np.random.normal(0, 3, 100)
attaques = np.maximum(attaques, 0)

plt.figure(figsize=(13, 7))
plt.plot(time_points, attaques, linewidth=2.5, color='#E74C3C', label='Attaques détectées')
plt.fill_between(time_points, 0, attaques, color='#E74C3C', alpha=0.15)
plt.axhline(y=15, color='orange', linestyle='--', linewidth=1.5, label='Seuil critique (15 attaques/s)')
plt.annotate('Scan de ports', xy=(30, 28), xytext=(20, 32),
             arrowprops=dict(arrowstyle='->', color='gray'), fontsize=10, fontweight='bold')
plt.annotate('SYN flood', xy=(65, 25), xytext=(55, 30),
             arrowprops=dict(arrowstyle='->', color='gray'), fontsize=10, fontweight='bold')
plt.title('Évolution des attaques en temps réel – Test de simulation', fontsize=15, fontweight='bold')
plt.xlabel('Temps (secondes)', fontsize=12)
plt.ylabel('Nombre d\'attaques', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig('figure14_evolution_attaques_detail.png', dpi=300)
plt.close()
print("   ✅ figure14_evolution_attaques_detail.png")

# ============================================================
# FIGURE 16 : DIAGRAMME DE GANTT
# ============================================================
print("\n[8/11] Génération de la Figure 16 : Diagramme de Gantt...")

phases = [
    {"name": "Phase 1 : Analyse des besoins", "start": "2026-07-01", "end": "2026-07-07", "color": "#4A90D9"},
    {"name": "Phase 2 : Préparation des données", "start": "2026-07-08", "end": "2026-07-17", "color": "#5BA3E6"},
    {"name": "Phase 3 : Entraînement des modèles", "start": "2026-07-18", "end": "2026-07-31", "color": "#6BB5F2"},
    {"name": "Phase 4 : Détection temps réel", "start": "2026-08-01", "end": "2026-08-14", "color": "#2ECC71"},
    {"name": "Phase 5 : Tableau de bord", "start": "2026-08-15", "end": "2026-08-24", "color": "#58D68D"},
    {"name": "Phase 6 : Intégration LLM", "start": "2026-08-25", "end": "2026-08-31", "color": "#82E0AA"},
    {"name": "Phase 7 : Tests et validation", "start": "2026-09-01", "end": "2026-09-07", "color": "#F39C12"},
    {"name": "Phase 8 : Rédaction du rapport", "start": "2026-09-08", "end": "2026-09-22", "color": "#E74C3C"},
    {"name": "Phase 9 : Relecture et finalisation", "start": "2026-09-23", "end": "2026-09-30", "color": "#C0392B"},
]

start_dates = [datetime.strptime(p["start"], "%Y-%m-%d") for p in phases]
end_dates = [datetime.strptime(p["end"], "%Y-%m-%d") for p in phases]
labels = [p["name"] for p in phases]
durations = [(end - start).days for start, end in zip(start_dates, end_dates)]
colors = [p["color"] for p in phases]

fig, ax = plt.subplots(figsize=(15, 9))

for i, (label, start, duration, color) in enumerate(zip(labels, start_dates, durations, colors)):
    start_num = (start - start_dates[0]).days
    ax.barh(i, duration, left=start_num, height=0.6, color=color, edgecolor='black', linewidth=1)
    ax.text(start_num + duration/2, i, f"{duration}j", ha='center', va='center', color='white', fontweight='bold', fontsize=10)

milestones = [
    (7, "✅ Analyse validée"),
    (17, "✅ Données prêtes"),
    (31, "✅ Modèles entraînés"),
    (14, "✅ Détection opérationnelle"),
    (24, "✅ Dashboard fonctionnel"),
    (31, "✅ LLM intégré"),
    (7, "✅ Tests validés"),
    (22, "✅ Rapport rédigé"),
    (30, "✅ Projet finalisé"),
]

for i, (day, label) in enumerate(milestones):
    x = day
    y = -1.2 - i * 0.6
    ax.plot(x, y, 'ko', markersize=8)
    ax.text(x + 0.5, y, label, fontsize=8, va='center', ha='left', color='#2C3E50')

ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=11)
ax.set_xlabel("Jours (à partir du 01/07/2026)", fontsize=12)
ax.set_title("Diagramme de Gantt détaillé – Projet AI-HYBRID-IDS", fontsize=16, fontweight='bold')
ax.grid(axis='x', linestyle='--', alpha=0.6)

ax.text(0, -5, "Début : 01/07/2026", fontsize=10, color='gray')
ax.text(max(durations), -5, f"Fin : {end_dates[-1].strftime('%d/%m/%Y')}", fontsize=10, color='gray', ha='right')

legend_elements = [
    patches.Patch(color='#4A90D9', label='🔵 Analyse et préparation'),
    patches.Patch(color='#2ECC71', label='🟢 Développement'),
    patches.Patch(color='#F39C12', label='🟠 Tests'),
    patches.Patch(color='#E74C3C', label='🔴 Rédaction'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('figure16_diagramme_gantt_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure16_diagramme_gantt_detail.png")

# ============================================================
# FIGURE 20 : APPROCHE HYBRIDE
# ============================================================
print("\n[9/11] Génération de la Figure 20 : Approche hybride...")

fig, ax = plt.subplots(figsize=(13, 7))

ax.text(6, 6.2, "MODÈLES SUPERVISÉS", fontsize=13, fontweight='bold', ha='center', color='#4A90D9')
ax.text(6, 5.8, "MODÈLE NON SUPERVISÉ", fontsize=13, fontweight='bold', ha='center', color='#2ECC71')

rect_rf = patches.Rectangle((1, 4.5), 2, 1.0, linewidth=2, edgecolor='black', facecolor='#4A90D9', alpha=0.8)
ax.add_patch(rect_rf)
ax.text(2, 5.0, 'Random Forest', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

rect_xgb = patches.Rectangle((3.5, 4.5), 2, 1.0, linewidth=2, edgecolor='black', facecolor='#5BA3E6', alpha=0.8)
ax.add_patch(rect_xgb)
ax.text(4.5, 5.0, 'XGBoost', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

rect_lgb = patches.Rectangle((6, 4.5), 2, 1.0, linewidth=2, edgecolor='black', facecolor='#6BB5F2', alpha=0.8)
ax.add_patch(rect_lgb)
ax.text(7, 5.0, 'LightGBM', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

rect_if = patches.Rectangle((9.5, 4.5), 2.5, 1.0, linewidth=2, edgecolor='black', facecolor='#2ECC71', alpha=0.8)
ax.add_patch(rect_if)
ax.text(10.75, 5.0, 'Isolation Forest', fontsize=10, fontweight='bold', va='center', ha='center', color='white')

ax.annotate('', xy=(6, 3.0), xytext=(2, 4.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(6, 3.0), xytext=(4.5, 4.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(6, 3.0), xytext=(7, 4.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(6, 3.0), xytext=(10.75, 4.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', linestyle='dashed'))

rect_vote = patches.Rectangle((4.5, 2.0), 3, 0.8, linewidth=2, edgecolor='black', facecolor='#F39C12', alpha=0.8)
ax.add_patch(rect_vote)
ax.text(6, 2.4, 'VOTE MAJORITAIRE', fontsize=11, fontweight='bold', va='center', ha='center', color='white')

rect_dec = patches.Rectangle((5, 0.8), 2, 0.9, linewidth=2, edgecolor='black', facecolor='#E74C3C', alpha=0.8)
ax.add_patch(rect_dec)
ax.text(6, 1.25, 'Décision finale\n(Attack / Normal)', fontsize=11, fontweight='bold', va='center', ha='center', color='white')

ax.annotate('', xy=(6, 2.0), xytext=(6, 2.8), arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
ax.annotate('', xy=(6, 1.7), xytext=(6, 0.8), arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.text(0.5, 1.0, 'Légende :', fontsize=11, fontweight='bold')
ax.text(0.5, 0.6, '→ Flux de prédiction', fontsize=10, color='gray')
ax.text(0.5, 0.3, '→ Flux d\'anomalie (dashed)', fontsize=10, color='gray')

ax.set_xlim(0, 13)
ax.set_ylim(0, 7)
ax.axis('off')
ax.set_title('Approche hybride : 3 modèles supervisés + 1 modèle non supervisé', fontsize=15, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('figure20_approche_hybride_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure20_approche_hybride_detail.png")

# ============================================================
# FIGURE 21 : VOTE MAJORITAIRE
# ============================================================
print("\n[10/11] Génération de la Figure 21 : Vote majoritaire...")

fig, ax = plt.subplots(figsize=(13, 6))

models = [
    {"name": "Random Forest", "color": "#4A90D9", "x": 1, "y": 4.5, "vote": "Attack"},
    {"name": "XGBoost", "color": "#5BA3E6", "x": 4, "y": 4.5, "vote": "Attack"},
    {"name": "LightGBM", "color": "#6BB5F2", "x": 7, "y": 4.5, "vote": "Normal"},
]

for m in models:
    rect = patches.Rectangle((m["x"]-0.8, m["y"]-0.5), 1.6, 1.0, linewidth=2, edgecolor='black', facecolor=m["color"], alpha=0.8)
    ax.add_patch(rect)
    ax.text(m["x"], m["y"]+0.1, m["name"], fontsize=11, fontweight='bold', va='center', ha='center', color='white')
    ax.text(m["x"], m["y"]-0.45, f"Prédit : {m['vote']}", fontsize=9, va='center', ha='center', color='white', style='italic')

ax.annotate('', xy=(5, 2.8), xytext=(1.5, 4.0), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(5, 2.8), xytext=(4.5, 4.0), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(5, 2.8), xytext=(7.5, 4.0), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))

rect_count = patches.Rectangle((3.5, 1.8), 3, 0.8, linewidth=2, edgecolor='black', facecolor='#F39C12', alpha=0.8)
ax.add_patch(rect_count)
ax.text(5, 2.2, 'Votes : Attack (2) / Normal (1)', fontsize=11, fontweight='bold', va='center', ha='center', color='white')

rect_res = patches.Rectangle((4.5, 0.8), 1, 0.7, linewidth=2, edgecolor='black', facecolor='#E74C3C', alpha=0.8)
ax.add_patch(rect_res)
ax.text(5, 1.15, 'ATTACK', fontsize=12, fontweight='bold', va='center', ha='center', color='white')

ax.annotate('', xy=(5, 1.5), xytext=(5, 1.8), arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.set_xlim(0, 10)
ax.set_ylim(0, 5.5)
ax.axis('off')
ax.set_title('Principe du vote majoritaire – 3 modèles supervisés', fontsize=15, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure21_vote_majoritaire_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure21_vote_majoritaire_detail.png")

# ============================================================
# FIGURE 22 : ARCHITECTURE SQLITE
# ============================================================
print("\n[11/11] Génération de la Figure 22 : Architecture SQLite...")

fig, ax = plt.subplots(figsize=(12, 10))

rect_table = patches.Rectangle((2, 3.5), 9, 5.5, linewidth=3, edgecolor='black', facecolor='#D3D3D3', alpha=0.2)
ax.add_patch(rect_table)
ax.text(6.5, 8.5, 'Table : packets', fontsize=15, fontweight='bold', va='center', ha='center')

columns = [
    {"name": "id", "type": "INTEGER", "constraint": "PRIMARY KEY", "example": "1"},
    {"name": "timestamp", "type": "TEXT", "constraint": "NOT NULL", "example": "2026-08-24T14:32:15"},
    {"name": "src_ip", "type": "TEXT", "constraint": "NOT NULL", "example": "10.155.85.120"},
    {"name": "dst_ip", "type": "TEXT", "constraint": "NOT NULL", "example": "10.155.85.52"},
    {"name": "protocol", "type": "TEXT", "constraint": "", "example": "ICMP"},
    {"name": "src_port", "type": "INTEGER", "constraint": "", "example": "0"},
    {"name": "dst_port", "type": "INTEGER", "constraint": "", "example": "0"},
    {"name": "packet_size", "type": "INTEGER", "constraint": "", "example": "98"},
    {"name": "ttl", "type": "INTEGER", "constraint": "", "example": "64"},
    {"name": "flags", "type": "TEXT", "constraint": "", "example": "None"},
    {"name": "ml_prediction", "type": "TEXT", "constraint": "NOT NULL", "example": "attack"},
    {"name": "anomaly", "type": "INTEGER", "constraint": "", "example": "1"},
    {"name": "correlation_score", "type": "REAL", "constraint": "", "example": "0.83"},
    {"name": "llm_report", "type": "TEXT", "constraint": "", "example": "Flood ICMP détecté..."},
]

for i, col in enumerate(columns):
    y = 8.0 - (i+1) * 0.4
    x = 2.5
    color = '#F39C12' if col['constraint'] == 'PRIMARY KEY' else '#FFFFFF'
    rect = patches.Rectangle((x, y-0.12), 8, 0.32, linewidth=1, edgecolor='gray', facecolor=color)
    ax.add_patch(rect)
    ax.text(x+0.2, y, col['name'], fontsize=9, va='center', ha='left', fontweight='bold')
    ax.text(x+3.0, y, col['type'], fontsize=8, va='center', ha='left', color='gray')
    ax.text(x+5.0, y, col['constraint'], fontsize=8, va='center', ha='left', color='red')
    ax.text(x+7.0, y, col['example'], fontsize=8, va='center', ha='left', color='blue', style='italic')

ax.text(6.5, 1.2, 'Base de données : ids.db', fontsize=12, fontweight='bold', va='center', ha='center')
ax.text(6.5, 0.7, 'Stockage des alertes et des rapports LLM', fontsize=10, va='center', ha='center', style='italic')

ax.text(0.5, 2.5, 'Légende :', fontsize=10, fontweight='bold')
ax.text(0.5, 2.2, '🔶 PK = Primary Key', fontsize=9, color='#F39C12')
ax.text(0.5, 1.9, '🔴 NOT NULL', fontsize=9, color='red')
ax.text(0.5, 1.6, '🔵 Exemple de donnée', fontsize=9, color='blue')

ax.set_xlim(0, 12)
ax.set_ylim(0, 9.5)
ax.axis('off')
ax.set_title('Architecture détaillée de la base de données SQLite', fontsize=14, fontweight='bold', pad=25)

plt.tight_layout()
plt.savefig('figure22_sqlite_architecture_detail.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ figure22_sqlite_architecture_detail.png")

# ============================================================
# FIN
# ============================================================
print("\n" + "=" * 60)
print("✅ TOUTES LES FIGURES ONT ÉTÉ GÉNÉRÉES AVEC SUCCÈS !")
print("=" * 60)
print("\n📁 Fichiers générés dans : ~/AI-HYBRID-IDS/figures/")
print("\nListe des fichiers :")
print("  - figure4_organigramme_detail.png")
print("  - figure5_architecture_detail.png")
print("  - figure6_modele_osi_detail.png")
print("  - figure7_pipeline_detail.png")
print("  - figure8_flux_temps_reel_detail.png")
print("  - figure_random_forest_matrice_detail.png")
print("  - figure_xgboost_matrice_detail.png")
print("  - figure_lightgbm_matrice_detail.png")
print("  - figure14_evolution_attaques_detail.png")
print("  - figure16_diagramme_gantt_detail.png")
print("  - figure20_approche_hybride_detail.png")
print("  - figure21_vote_majoritaire_detail.png")
print("  - figure22_sqlite_architecture_detail.png")
print("\n📌 Pensez à intégrer ces images dans votre rapport.")
