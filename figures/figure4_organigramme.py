#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 10))

levels = [
    {"name": "DIRECTION GÉNÉRALE\nM. GONTI RAOUL FELIX", "y": 8, "x": 7, "color": "#2C3E50"},
    {"name": "Administration\net Finances", "y": 6, "x": 1.5, "color": "#3498DB"},
    {"name": "Ressources\nHumaines", "y": 6, "x": 4.5, "color": "#3498DB"},
    {"name": "Commercial", "y": 6, "x": 7.5, "color": "#3498DB"},
    {"name": "Technique et\nMaintenance", "y": 6, "x": 10.5, "color": "#3498DB"},
    {"name": "Logistique et\nApprovisionnement", "y": 4, "x": 3, "color": "#2ECC71"},
    {"name": "Qualité, Sécurité\net Environnement (QSE)", "y": 4, "x": 6.5, "color": "#2ECC71"},
]

for level in levels:
    rect = patches.Rectangle((level["x"]-1.5, level["y"]-0.5), 3, 1,
                             linewidth=2, edgecolor='black', facecolor=level["color"], alpha=0.8)
    ax.add_patch(rect)
    ax.text(level["x"], level["y"], level["name"], fontsize=10, fontweight='bold',
            va='center', ha='center', color='white')

for x in [1.5, 4.5, 7.5, 10.5]:
    ax.plot([7, x], [7.5, 6.5], 'k-', linewidth=1.5)
ax.plot([7, 10.5], [7.5, 6.5], 'k-', linewidth=1.5)
ax.plot([1.5, 3], [5.5, 4.5], 'k--', linewidth=1)
ax.plot([4.5, 6.5], [5.5, 4.5], 'k--', linewidth=1)
ax.plot([10.5, 10.5], [5.5, 4.5], 'k--', linewidth=1)

ax.set_xlim(0, 13)
ax.set_ylim(0, 9.5)
ax.axis('off')
ax.set_title('Organigramme simplifié de SODIMAS Ascenseur', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('figure4_organigramme.png', dpi=300, bbox_inches='tight')
plt.close()
print("✅ Figure 4 générée : figure4_organigramme.png")
