#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Génération du diagramme de Gantt pour le projet AI-HYBRID-IDS
Utilisation : python3 gantt.py
Sortie : diagramme_gantt.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
import numpy as np

# ============================================================
# 1. DONNÉES DU PROJET
# ============================================================

# Liste des phases du projet avec leurs dates de début et de fin
phases = [
    ("Phase 1 : Analyse des besoins et étude de l'existant", "2026-07-01", "2026-07-07"),
    ("Phase 2 : Préparation des données (nettoyage, équilibrage)", "2026-07-08", "2026-07-17"),
    ("Phase 3 : Entraînement et optimisation des modèles", "2026-07-18", "2026-07-31"),
    ("Phase 4 : Développement du système de détection temps réel", "2026-08-01", "2026-08-14"),
    ("Phase 5 : Conception et mise en place du tableau de bord", "2026-08-15", "2026-08-24"),
    ("Phase 6 : Intégration du LLM local (Ollama + Qwen 0.5B)", "2026-08-25", "2026-08-31"),
    ("Phase 7 : Tests, simulations et validation", "2026-09-01", "2026-09-07"),
    ("Phase 8 : Rédaction du rapport de stage", "2026-09-08", "2026-09-22"),
    ("Phase 9 : Relecture, corrections et finalisation", "2026-09-23", "2026-09-30"),
]

# ============================================================
# 2. CONVERSION DES DATES
# ============================================================

# Convertir les chaînes de caractères en objets datetime
start_dates = [datetime.strptime(d, "%Y-%m-%d") for _, d, _ in phases]
end_dates = [datetime.strptime(d, "%Y-%m-%d") for _, _, d in phases]
labels = [p[0] for p in phases]

# Calculer la durée en jours pour chaque phase
durations = [(end - start).days for start, end in zip(start_dates, end_dates)]

# Définir la date de référence (premier jour du projet)
reference_date = start_dates[0]

# Calculer le nombre de jours depuis la date de référence pour chaque phase
start_days = [(start - reference_date).days for start in start_dates]

# ============================================================
# 3. CRÉATION DU DIAGRAMME
# ============================================================

# Créer une figure avec une taille adaptée
fig, ax = plt.subplots(figsize=(14, 8))

# Définir les couleurs pour chaque phase (par catégorie)
colors = {
    'analyse': '#4A90D9',      # Bleu
    'preparation': '#5BA3E6',  # Bleu clair
    'entrainement': '#6BB5F2', # Bleu moyen
    'developpement': '#2ECC71',# Vert
    'dashboard': '#58D68D',    # Vert clair
    'llm': '#82E0AA',          # Vert très clair
    'tests': '#F39C12',        # Orange
    'redaction': '#E74C3C',    # Rouge
    'finalisation': '#C0392B', # Rouge foncé
}

# Associer chaque phase à une couleur
phase_colors = [
    colors['analyse'],
    colors['preparation'],
    colors['entrainement'],
    colors['developpement'],
    colors['dashboard'],
    colors['llm'],
    colors['tests'],
    colors['redaction'],
    colors['finalisation'],
]

# ============================================================
# 4. TRACÉ DES BARRES
# ============================================================

# Tracer chaque barre horizontale
for i, (label, start_day, duration, color) in enumerate(zip(labels, start_days, durations, phase_colors)):
    # Barre horizontale : left = jour de début, width = durée
    bar = ax.barh(i, duration, left=start_day, height=0.6, 
                  color=color, edgecolor='black', linewidth=1)
    
    # Ajouter le nombre de jours au centre de la barre
    ax.text(start_day + duration/2, i, f"{duration} j", 
            ha='center', va='center', color='white', 
            fontweight='bold', fontsize=11)

# ============================================================
# 5. CONFIGURATION DES AXES
# ============================================================

# Définir les étiquettes de l'axe Y (noms des phases)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=10)

# Définir l'étiquette de l'axe X
ax.set_xlabel("Jours (à partir du 01/07/2026)", fontsize=12, fontweight='bold')

# Définir le titre du diagramme
ax.set_title("Diagramme de Gantt – Projet AI-HYBRID-IDS", 
             fontsize=16, fontweight='bold', pad=20)

# Ajouter une grille verticale pour faciliter la lecture
ax.grid(axis='x', linestyle='--', alpha=0.6)

# ============================================================
# 6. MARQUEURS DE DATES IMPORTANTES
# ============================================================

# Ajouter des repères visuels pour les dates clés
important_dates = [
    (7, "07/07"),
    (17, "17/07"),
    (31, "31/07"),
    (14, "14/08"),
    (24, "24/08"),
    (31, "31/08"),
    (7, "07/09"),
    (22, "22/09"),
    (30, "30/09"),
]

for day, label in important_dates:
    ax.axvline(x=day, color='gray', linestyle=':', alpha=0.5)
    ax.text(day, -0.5, label, ha='center', va='top', fontsize=8, color='gray')

# ============================================================
# 7. LÉGENDE
# ============================================================

# Créer une légende par catégorie de tâches
legend_elements = [
    mpatches.Patch(color='#4A90D9', label='🔵 Analyse et préparation'),
    mpatches.Patch(color='#2ECC71', label='🟢 Développement'),
    mpatches.Patch(color='#F39C12', label='🟠 Tests et validation'),
    mpatches.Patch(color='#E74C3C', label='🔴 Rédaction et finalisation'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10, framealpha=0.9)

# ============================================================
# 8. INFORMATIONS COMPLÉMENTAIRES
# ============================================================

# Ajouter la date de début et de fin du projet
ax.text(0, -1.2, f"Début : {start_dates[0].strftime('%d/%m/%Y')}", 
        fontsize=10, color='gray')
ax.text(max(durations), -1.2, f"Fin : {end_dates[-1].strftime('%d/%m/%Y')}", 
        fontsize=10, color='gray', ha='right')

# Ajouter la durée totale du projet en bas
total_days = (end_dates[-1] - start_dates[0]).days
ax.text(max(durations)/2, -1.8, f"Durée totale : {total_days} jours (13 semaines)", 
        fontsize=11, ha='center', fontweight='bold', color='#2C3E50')

# ============================================================
# 9. AJUSTEMENTS FINAUX ET SAUVEGARDE
# ============================================================

# Ajuster automatiquement les marges
plt.tight_layout()

# Sauvegarder l'image en haute résolution
plt.savefig('diagramme_gantt.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('diagramme_gantt.pdf', bbox_inches='tight', facecolor='white')

# Afficher le diagramme à l'écran
plt.show()

# Message de confirmation
print("✅ Diagramme de Gantt généré avec succès !")
print("   📁 Fichiers créés :")
print("      - diagramme_gantt.png (image haute résolution)")
print("      - diagramme_gantt.pdf (format vectoriel pour le rapport)")
