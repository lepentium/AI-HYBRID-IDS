#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 5))

models = [
    {"name": "Random Forest", "color": "#4A90D9", "x": 1, "y": 3},
    {"name": "XGBoost", "color": "#5BA3E6", "x": 4, "y": 3},
    {"name": "LightGBM", "color": "#6BB5F2", "x": 7, "y": 3},
]

for m in models:
    rect = patches.Rectangle((m["x"]-0.8, m["y"]-0.5), 1.6, 1, linewidth=2, edgecolor='black', facecolor=m["color"], alpha=0.7)
    ax.add_patch(rect)
    ax.text(m["x"], m["y"], m["name"], fontsize=10, fontweight='bold', va='center', ha='center', color='white')
    ax.text(m["x"], m["y"]-1, "Prédiction", fontsize=9, va='center', ha='center', style='italic')

ax.annotate('', xy=(4.5, 1.5), xytext=(1.5, 2.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(4.5, 1.5), xytext=(4.5, 2.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
ax.annotate('', xy=(4.5, 1.5), xytext=(7.5, 2.5), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))

rect_vote = patches.Rectangle((3.5, 0.7), 2, 0.8, linewidth=2, edgecolor='black', facecolor='#F39C12', alpha=0.7)
ax.add_patch(rect_vote)
ax.text(4.5, 1.1, 'VOTE', fontsize=12, fontweight='bold', va='center', ha='center', color='white')

rect_res = patches.Rectangle((4, 0), 1, 0.6, linewidth=2, edgecolor='black', facecolor='#E74C3C', alpha=0.7)
ax.add_patch(rect_res)
ax.text(4.5, 0.3, 'Attack / Normal', fontsize=9, fontweight='bold', va='center', ha='center', color='white')

ax.annotate('', xy=(4.5, 0.7), xytext=(4.5, 0.6), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))

ax.set_xlim(0, 9)
ax.set_ylim(0, 4.5)
ax.axis('off')
ax.set_title('Principe du vote majoritaire entre les 3 modèles supervisés', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure21_vote_majoritaire.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 21 générée : figure21_vote_majoritaire.png")
