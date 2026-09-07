#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 8))

layers = [
    {"name": "Couche 1 : Collecte", "color": "#4A90D9", "tools": "TShark (capture réseau)", "y": 6.5},
    {"name": "Couche 2 : Extraction", "color": "#2ECC71", "tools": "Suricata (mode flow)", "y": 5},
    {"name": "Couche 3 : Analyse intelligente", "color": "#F39C12", "tools": "RF + XGB + LGB + Isolation Forest", "y": 3.5},
    {"name": "Couche 4 : Visualisation", "color": "#E74C3C", "tools": "Dashboard Streamlit + API Flask", "y": 2},
]

for layer in layers:
    rect = patches.Rectangle((1, layer["y"]-0.5), 10, 0.9, linewidth=2, edgecolor='black', facecolor=layer["color"], alpha=0.7)
    ax.add_patch(rect)
    ax.text(2, layer["y"], layer["name"], fontsize=13, fontweight='bold', va='center')
    ax.text(7, layer["y"], layer["tools"], fontsize=11, va='center', color='white', fontweight='bold')

for i in range(3):
    ax.annotate('', xy=(6, 5.5-i*1.5), xytext=(6, 5.5-i*1.5-0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='gray'))

ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis('off')
ax.set_title('Architecture globale du système AI-HYBRID-IDS', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure5_architecture.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 5 générée : figure5_architecture.png")
