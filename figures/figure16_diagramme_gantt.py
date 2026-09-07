#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

phases = [
    ("Phase 1 : Analyse des besoins", "2026-07-01", "2026-07-07"),
    ("Phase 2 : Préparation des données", "2026-07-08", "2026-07-17"),
    ("Phase 3 : Entraînement des modèles", "2026-07-18", "2026-07-31"),
    ("Phase 4 : Détection temps réel", "2026-08-01", "2026-08-14"),
    ("Phase 5 : Tableau de bord", "2026-08-15", "2026-08-24"),
    ("Phase 6 : Intégration LLM", "2026-08-25", "2026-08-31"),
    ("Phase 7 : Tests et validation", "2026-09-01", "2026-09-07"),
    ("Phase 8 : Rédaction du rapport", "2026-09-08", "2026-09-22"),
    ("Phase 9 : Relecture et finalisation", "2026-09-23", "2026-09-30"),
]

start_dates = [datetime.strptime(d, "%Y-%m-%d") for _, d, _ in phases]
end_dates = [datetime.strptime(d, "%Y-%m-%d") for _, _, d in phases]
labels = [p[0] for p in phases]
durations = [(end - start).days for start, end in zip(start_dates, end_dates)]

fig, ax = plt.subplots(figsize=(14, 8))

colors = ['#4A90D9', '#5BA3E6', '#6BB5F2', '#2ECC71', '#58D68D', '#82E0AA', '#F39C12', '#E74C3C', '#C0392B']

for i, (label, start, duration, color) in enumerate(zip(labels, start_dates, durations, colors)):
    start_num = (start - start_dates[0]).days
    ax.barh(i, duration, left=start_num, height=0.6, color=color, edgecolor='black', linewidth=1)
    ax.text(start_num + duration/2, i, f"{duration}j", ha='center', va='center', color='white', fontweight='bold', fontsize=10)

ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("Jours (à partir du 01/07/2026)", fontsize=12)
ax.set_title("Diagramme de Gantt – Projet AI-HYBRID-IDS", fontsize=16, fontweight='bold')
ax.grid(axis='x', linestyle='--', alpha=0.7)

ax.text(0, -1, "Début : 01/07/2026", fontsize=10, color='gray')
ax.text(max(durations), -1, f"Fin : {end_dates[-1].strftime('%d/%m/%Y')}", fontsize=10, color='gray', ha='right')

legend_elements = [
    mpatches.Patch(color='#4A90D9', label='Analyse et préparation'),
    mpatches.Patch(color='#2ECC71', label='Développement'),
    mpatches.Patch(color='#F39C12', label='Tests'),
    mpatches.Patch(color='#E74C3C', label='Rédaction'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('figure16_diagramme_gantt.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 16 générée : figure16_diagramme_gantt.png")
