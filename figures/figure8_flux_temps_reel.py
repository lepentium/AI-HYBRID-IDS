#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 4))

steps = [
    {"label": "1. Capture\n(TShark)", "color": "#4A90D9"},
    {"label": "2. Analyse\n(Suricata)", "color": "#5BA3E6"},
    {"label": "3. Prédiction\n(RF+XGB+LGB+IF)", "color": "#2ECC71"},
    {"label": "4. Affichage\n(Dashboard Streamlit)", "color": "#E74C3C"},
]

for i, step in enumerate(steps):
    x = 0.5 + i * 3.5
    rect = patches.Rectangle((x, 0.8), 2.5, 2, linewidth=2, edgecolor='black', facecolor=step['color'], alpha=0.7)
    ax.add_patch(rect)
    ax.text(x + 1.25, 1.8, step['label'], fontsize=11, fontweight='bold', va='center', ha='center', color='white')

for i in range(len(steps)-1):
    ax.annotate('', xy=(0.5 + (i+1)*3.5, 1.8), xytext=(0.5 + i*3.5 + 2.5, 1.8),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.annotate('', xy=(0.5, 1.8), xytext=(0.5 + len(steps)*3.5, 1.8),
            arrowprops=dict(arrowstyle='->', lw=2, color='gray', linestyle='dashed'))
ax.text(14, 1.8, 'Cycle continu\n(3-5 secondes)', fontsize=10, fontweight='bold', ha='center', color='gray')

ax.set_xlim(0, 16)
ax.set_ylim(0, 4)
ax.axis('off')
ax.set_title('Flux de données en temps réel – AI-HYBRID-IDS', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure8_flux_temps_reel.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 8 générée : figure8_flux_temps_reel.png")
