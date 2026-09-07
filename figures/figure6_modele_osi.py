#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 8))

osi_layers = [
    {"name": "7. Application", "highlight": True, "desc": "Analyse DNS, logs"},
    {"name": "6. Présentation", "highlight": False, "desc": ""},
    {"name": "5. Session", "highlight": False, "desc": ""},
    {"name": "4. Transport", "highlight": True, "desc": "Ports, flags TCP/UDP"},
    {"name": "3. Réseau", "highlight": True, "desc": "IP, TTL, ICMP"},
    {"name": "2. Liaison", "highlight": True, "desc": "Capture trames"},
    {"name": "1. Physique", "highlight": False, "desc": ""},
]

for i, layer in enumerate(osi_layers):
    y = i * 0.9 + 0.3
    color = '#F39C12' if layer['highlight'] else '#D3D3D3'
    rect = patches.Rectangle((2, y), 8, 0.7, linewidth=2, edgecolor='black', facecolor=color, alpha=0.7)
    ax.add_patch(rect)
    ax.text(4.5, y + 0.35, layer['name'], fontsize=12, fontweight='bold', va='center', ha='center')
    if layer['desc']:
        ax.text(8.5, y + 0.35, layer['desc'], fontsize=9, va='center', ha='center', style='italic')

ax.text(1, 4.5, "Utilisées", rotation=90, fontsize=12, fontweight='bold', color='#F39C12')
ax.text(1, 2.5, "Non utilisées", rotation=90, fontsize=12, fontweight='bold', color='gray')

ax.set_xlim(0, 11)
ax.set_ylim(0, 7)
ax.axis('off')
ax.set_title('Positionnement du système AI-HYBRID-IDS dans le modèle OSI', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure6_modele_osi.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 6 générée : figure6_modele_osi.png")
