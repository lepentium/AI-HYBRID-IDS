#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 5))

steps = [
    {"label": "Chargement\ndes données", "color": "#4A90D9"},
    {"label": "Nettoyage et\nregroupement", "color": "#5BA3E6"},
    {"label": "Équilibrage\n(SMOTE-Tomek)", "color": "#6BB5F2"},
    {"label": "Optimisation\n(GridSearchCV)", "color": "#2ECC71"},
    {"label": "Entraînement\n(RF+XGB+LGB)", "color": "#58D68D"},
    {"label": "Sauvegarde\ndes modèles", "color": "#E74C3C"},
]

x_start = 0.5
for i, step in enumerate(steps):
    x = x_start + i * 2.5
    rect = patches.Rectangle((x, 1), 1.8, 2.5, linewidth=2, edgecolor='black', facecolor=step['color'], alpha=0.7)
    ax.add_patch(rect)
    ax.text(x + 0.9, 2.25, step['label'], fontsize=10, fontweight='bold', va='center', ha='center', color='white')

for i in range(len(steps)-1):
    ax.annotate('', xy=(x_start + (i+1)*2.5, 2.25), xytext=(x_start + i*2.5 + 1.8, 2.25),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.set_xlim(0, 16)
ax.set_ylim(0, 4.5)
ax.axis('off')
ax.set_title('Pipeline d\'entraînement des modèles AI-HYBRID-IDS', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure7_pipeline.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 7 générée : figure7_pipeline.png")
